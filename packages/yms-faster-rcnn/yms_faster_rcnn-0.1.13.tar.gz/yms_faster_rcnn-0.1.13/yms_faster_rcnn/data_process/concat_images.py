import os
import argparse
from PIL import Image
from typing import Set, List

# 支持的图片文件扩展名
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}


def get_image_filenames(folder: str) -> Set[str]:
    """获取文件夹中所有图片的文件名（含扩展名，去重）"""
    if not os.path.exists(folder):
        raise ValueError(f"文件夹不存在：{folder}")

    image_names = set()
    for filename in os.listdir(folder):
        # 过滤非图片文件
        ext = os.path.splitext(filename)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            image_names.add(filename)
    return image_names


def concat_images(img1_path: str, img2_path: str, mode: str = "horizontal") -> Image.Image:
    """
    拼接两张图片
    mode: "horizontal"（横向拼接）或 "vertical"（纵向拼接）
    """
    try:
        with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
            # 统一图片模式为RGB（避免透明通道等问题）
            img1 = img1.convert("RGB")
            img2 = img2.convert("RGB")

            # 计算拼接后图片的尺寸
            if mode == "horizontal":
                width = img1.width + img2.width
                height = max(img1.height, img2.height)
            else:  # vertical
                width = max(img1.width, img2.width)
                height = img1.height + img2.height

            # 创建空白画布并拼接
            combined = Image.new("RGB", (width, height))
            combined.paste(img1, (0, 0))  # 第一张图放在左侧/上方

            if mode == "horizontal":
                combined.paste(img2, (img1.width, 0))  # 第二张图放在右侧
            else:
                combined.paste(img2, (0, img1.height))  # 第二张图放在下方

            return combined
    except Exception as e:
        raise RuntimeError(f"拼接图片失败（{img1_path} 和 {img2_path}）：{str(e)}")


def process_folders(folder1: str, folder2: str, folder3: str, output_folder: str, concat_mode: str = "horizontal"):
    """
    处理三个文件夹的图片拼接逻辑
    """
    # 创建输出文件夹（若不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 1. 获取三个文件夹中的图片文件名
    s1 = get_image_filenames(folder1)  # 文件夹1的图片名集合
    s2 = get_image_filenames(folder2)  # 文件夹2的图片名集合
    s3 = get_image_filenames(folder3)  # 文件夹3的图片名集合

    # 2. 处理需求1：拼接文件夹1与文件夹2/3中同名图片（优先文件夹2）
    print("=== 开始处理需求1：文件夹1与文件夹2/3同名图片拼接 ===")
    for name in s1:
        # 优先检查文件夹2是否有同名图片
        if name in s2:
            img1_path = os.path.join(folder1, name)
            img2_path = os.path.join(folder2, name)
            try:
                combined_img = concat_images(img1_path, img2_path, mode=concat_mode)
                # 保存拼接结果（添加后缀区分来源）
                base_name = os.path.splitext(name)[0]
                save_path = os.path.join(output_folder, f"{base_name}_1+2.{os.path.splitext(name)[1][1:]}")
                combined_img.save(save_path)
                print(f"成功拼接：{name}（文件夹1 + 文件夹2）→ 保存至 {save_path}")
            except Exception as e:
                print(f"跳过 {name}：{str(e)}")

        # 若文件夹2无，则检查文件夹3
        elif name in s3:
            img1_path = os.path.join(folder1, name)
            img3_path = os.path.join(folder3, name)
            try:
                combined_img = concat_images(img1_path, img3_path, mode=concat_mode)
                base_name = os.path.splitext(name)[0]
                save_path = os.path.join(output_folder, f"{base_name}_1+3.{os.path.splitext(name)[1][1:]}")
                combined_img.save(save_path)
                print(f"成功拼接：{name}（文件夹1 + 文件夹3）→ 保存至 {save_path}")
            except Exception as e:
                print(f"跳过 {name}：{str(e)}")

    # 3. 处理需求2：文件夹1无但文件夹2有，且文件夹3有同名的图片拼接
    print("\n=== 开始处理需求2：文件夹2（文件夹1无）与文件夹3同名图片拼接 ===")
    # 筛选：文件夹2有但文件夹1无的图片名
    s2_unique = s2 - s1
    for name in s2_unique:
        # 检查文件夹3是否有同名图片
        if name in s3:
            img2_path = os.path.join(folder2, name)
            img3_path = os.path.join(folder3, name)
            try:
                combined_img = concat_images(img2_path, img3_path, mode=concat_mode)
                base_name = os.path.splitext(name)[0]
                save_path = os.path.join(output_folder, f"{base_name}_2+3.{os.path.splitext(name)[1][1:]}")
                combined_img.save(save_path)
                print(f"成功拼接：{name}（文件夹2 + 文件夹3）→ 保存至 {save_path}")
            except Exception as e:
                print(f"跳过 {name}：{str(e)}")

    print(f"\n所有处理完成，结果保存在：{output_folder}")


def main():
    parser = argparse.ArgumentParser(description="处理三个图片文件夹的拼接逻辑")
    parser.add_argument("--folder1", default=r'F:\代码\结果\第2次\预测图片',
                        help="第一个文件夹路径")
    parser.add_argument("--folder2", default=r'F:\代码\dataset\标注',
                        help="第二个文件夹路径")
    parser.add_argument("--folder3", default=r'F:\代码\dataset\VOCdevkit\VOC2012\JPEGImages',
                        help="第三个文件夹路径")
    parser.add_argument("--output", default=r"F:\代码\结果\第2次\combined_images",
                        help="拼接后图片的输出文件夹（默认：combined_images）")
    parser.add_argument("--mode", default="horizontal", choices=["horizontal", "vertical"],
                        help="拼接模式（horizontal：横向，vertical：纵向，默认：horizontal）")
    args = parser.parse_args()

    process_folders(
        folder1=args.folder1,
        folder2=args.folder2,
        folder3=args.folder3,
        output_folder=args.output,
        concat_mode=args.mode
    )


if __name__ == "__main__":
    main()