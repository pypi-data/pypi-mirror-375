import argparse
from yms_faster_rcnn.data_process.util import read_lines, natural_sort_key


def extract_and_merge_diffs(file1, file2, output_file):
    """
    提取两个文件中相同的文件名、第一个文件独有的文件名、第二个文件独有的文件名，
    合并到一个txt文件，用提示信息分割并统计数量
    """
    # 读取两个文件的内容并去重（转为集合自动去重）
    names1 = set(read_lines(file1))
    names2 = set(read_lines(file2))

    # 计算三类文件名
    common_names = names1 & names2  # 两个文件中相同的名称
    file1_unique = names1 - names2  # 第一个文件独有的名称
    file2_unique = names2 - names1  # 第二个文件独有的名称

    # 自然排序（按人类习惯排序，如数字会按大小排列）
    sorted_common = sorted(common_names, key=natural_sort_key)
    sorted_file1 = sorted(file1_unique, key=natural_sort_key)
    sorted_file2 = sorted(file2_unique, key=natural_sort_key)

    # 写入合并文件（使用utf-8编码避免中文乱码）
    with open(output_file, 'w', encoding='utf-8') as f:
        # 1. 写入两个文件中相同的名称
        f.write("===== 检出（共{}个） =====".format(len(sorted_common)) + '\n')
        for name in sorted_common:
            f.write(name + '\n')
        f.write('\n')  # 空行分隔

        # 2. 写入第一个文件独有的名称
        f.write("===== 漏检（共{}个） =====".format(len(sorted_file1)) + '\n')
        for name in sorted_file1:
            f.write(name + '\n')
        f.write('\n')  # 空行分隔

        # 3. 写入第二个文件独有的名称
        f.write("===== 误检（共{}个） =====".format(len(sorted_file2)) + '\n')
        for name in sorted_file2:
            f.write(name + '\n')

    # 打印统计结果
    print(f"处理完成！结果已保存至：{output_file}")
    print(f"检出数量：{len(sorted_common)}")
    print(f"漏检数量：{len(sorted_file1)}")
    print(f"误检数量：{len(sorted_file2)}")


def get_args():
    parser = argparse.ArgumentParser(description='提取两个txt文件中独有的文件名并合并输出')
    parser.add_argument('--file1', type=str,
                        default=r'F:\代码\dataset\VOCdevkit\VOC2012\有缺陷验证集.txt',
                        help='第一个txt文件路径')
    parser.add_argument('--file2', type=str, default=r'F:\代码\结果\第2次\检测结果.txt',
                        help='第二个txt文件路径')
    parser.add_argument('--output', type=str, default=r'F:\代码\结果\第2次\unique_names.txt',
                        help='合并输出的txt文件路径')
    return parser.parse_args()


def main():
    args = get_args()
    extract_and_merge_diffs(args.file1, args.file2, args.output)


if __name__ == "__main__":
    main()