import os
import time
import json

import torch
from PIL import Image
import matplotlib.pyplot as plt

from torchvision import transforms
from torchvision.models import EfficientNet_B0_Weights

from yms_faster_rcnn.backbone import LastLevelMaxPool, BackboneWithFPN
from yms_faster_rcnn.backbone.resnet50_fpn_model import resnet152_fpn_backbone, resnet50_fpn_backbone
from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor, AnchorsGenerator
from yms_faster_rcnn.train.draw_box_utils import draw_objs

from torchvision.models import EfficientNet_B0_Weights
from yms_faster_rcnn.backbone import BackboneWithFPN, LastLevelMaxPool
from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor, AnchorsGenerator


def create_model(num_classes):
    import torchvision
    from torchvision.models.feature_extraction import create_feature_extractor
    from torchvision.ops import MultiScaleRoIAlign
    from torchvision.models import ConvNeXt_Tiny_Weights

    from yms_faster_rcnn.backbone import BackboneWithFPN, LastLevelMaxPool
    from yms_faster_rcnn.network_files import FasterRCNN, AnchorsGenerator


    # 1. 加载ConvNeXt-Tiny（高精度，浅层特征细节丰富）
    # 预训练权重：weights=torchvision.models.ConvNeXt_Tiny_Weights.DEFAULT
    backbone = torchvision.models.convnext_tiny(weights=ConvNeXt_Tiny_Weights.DEFAULT)
    # print(backbone)

    # 2. 选择特征层（保留stride=4的浅层）
    # ConvNeXt-Tiny的特征层结构：
    # - features.0: stride=4（下采样4倍，极浅层，小目标核心信息）
    # - features.1: stride=8（下采样8倍）
    # - features.2: stride=16（下采样16倍）
    # - features.3: stride=32（下采样32倍）
    return_layers = {
        "features.0": "0",  # 深层：768通道（stride=32，语义强）
        "features.2": "1",  # 次深层：384通道（stride=16）
        "features.4": "2",  # 次浅层：192通道（stride=8）
        "features.6": "3",   # 浅层：96通道（stride=4，小目标细节核心）
    }

    # 3. 对应特征层的输入通道数（ConvNeXt-Tiny各层输出通道固定）
    in_channels_list = [96, 192, 384, 768]  # "0"→768, "1"→384, "2"→192, "3"→96

    # 4. 构建带FPN的Backbone
    new_backbone = create_feature_extractor(backbone, return_layers)
    img = torch.randn(1, 3, 224, 224)
    outputs = new_backbone(img)
    [print(f"{k} shape: {v.shape}") for k, v in outputs.items()]

    backbone_with_fpn = BackboneWithFPN(
        new_backbone,
        return_layers=return_layers,
        in_channels_list=in_channels_list,
        out_channels=256,
        extra_blocks=LastLevelMaxPool(),
        re_getter=False
    )

    # 5. 小Anchor配置（同方案1，覆盖8×8~128×8）
    anchor_sizes = ((14,), (7,), (32,), (48,), (21,))
    aspect_ratios = ((0.4010903, 0.7580582, 1.4109948),) * len(anchor_sizes)
    anchor_generator = AnchorsGenerator(sizes=anchor_sizes, aspect_ratios=aspect_ratios)

    # 6. 大尺寸RoI Align（同方案1，14×14输出）
    roi_pooler = MultiScaleRoIAlign(
        featmap_names=['0', '1', '2', '3'],
        output_size=[14, 14],
        sampling_ratio=2
    )

    # 7. 初始化Faster R-CNN（同方案1，调整输入尺寸）
    model = FasterRCNN(
        backbone=backbone_with_fpn,
        num_classes=num_classes,
        rpn_anchor_generator=anchor_generator,
        box_roi_pool=roi_pooler,
        min_size=1000,
        max_size=1000,
        box_score_thresh=0.01,
        box_detections_per_img=200
    )

    return model



def time_synchronized():
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    return time.time()


def main():
    # get devices
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # create model
    model = create_model(num_classes=2)

    # load train weights
    weights_path = r"D:\Code\0-data\0-故障诊断结果输出\results\save_weights\best_model.pth"
    assert os.path.exists(weights_path), "{} file dose not exist.".format(weights_path)
    weights_dict = torch.load(weights_path, map_location='cpu')
    weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
    model.load_state_dict(weights_dict)
    model.to(device)

    # read class_indict
    label_json_path = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\classes.json'
    assert os.path.exists(label_json_path), "json file {} dose not exist.".format(label_json_path)
    with open(label_json_path, 'r') as f:
        class_dict = json.load(f)

    category_index = {str(v): str(k) for k, v in class_dict.items()}

    # load image
    original_img = Image.open(
        r"F:\IDM_Downloads\VOCdevkit\VOC2012\JPEGImages\1__H2_817171_IO-NIO198M_210119A0184-1-1.jpg")

    # from pil image to tensor, do not normalize image
    data_transform = transforms.Compose([transforms.ToTensor()])
    img = data_transform(original_img)
    # expand batch dimension
    img = torch.unsqueeze(img, dim=0)

    model.eval()  # 进入验证模式
    with torch.no_grad():
        # init
        img_height, img_width = img.shape[-2:]
        init_img = torch.zeros((1, 3, img_height, img_width), device=device)
        model(init_img)

        t_start = time_synchronized()
        predictions = model(img.to(device))[0]
        t_end = time_synchronized()
        print("inference+NMS time: {}".format(t_end - t_start))

        predict_boxes = predictions["boxes"].to("cpu").numpy()
        predict_classes = predictions["labels"].to("cpu").numpy()
        predict_scores = predictions["scores"].to("cpu").numpy()

        if len(predict_boxes) == 0:
            print("没有检测到任何目标!")

        plot_img = draw_objs(original_img,
                             predict_boxes,
                             predict_classes,
                             predict_scores,
                             category_index=category_index,
                             box_thresh=0.5,
                             line_thickness=3,
                             font='arial.ttf',
                             font_size=20)
        plt.imshow(plot_img)
        plt.show()
        # 保存预测的图片结果
        plot_img.save("test_result.jpg")


if __name__ == '__main__':
    # main()
    model = create_model(2)
    print(model)