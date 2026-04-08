#!/usr/bin/env python3
"""数字足迹与社交记录解析器

用于扫描和归档逝者生前在朋友圈、微博、备忘录等平台留下的数字足迹截图或文本导出文件。
图片类截图后续将交由大模型的视觉工具进行读取，本工具主要负责梳理目录结构与提取纯文本数据。

Usage:
    python3 social_parser.py --dir <screenshot_dir> --output <output_path>
"""

import argparse
import os
import sys
from pathlib import Path


def scan_directory(dir_path: str) -> dict:
    """扫描归档目录，按数据类型分类文件"""
    files = {'images': [], 'texts': [], 'other': []}
    
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    text_exts = {'.txt', '.md', '.json', '.csv'}
    
    for root, dirs, filenames in os.walk(dir_path):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            ext = Path(fname).suffix.lower()
            if ext in image_exts:
                files['images'].append(fpath)
            elif ext in text_exts:
                files['texts'].append(fpath)
            else:
                files['other'].append(fpath)
    
    return files


def main():
    parser = argparse.ArgumentParser(description='生前数字足迹与社交记录解析器')
    parser.add_argument('--dir', required=True, help='截图或原始文件所在的目录')
    parser.add_argument('--output', required=True, help='扫描结果输出文件路径')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"目录读取错误：找不到指定的文件夹 {args.dir}", file=sys.stderr)
        sys.exit(1)
    
    files = scan_directory(args.dir)
    
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("# 生前数字足迹归档扫描结果\n\n")
        f.write(f"扫描目录：{args.dir}\n\n")
        
        f.write(f"## 数据资产统计\n")
        f.write(f"- 图像文件：{len(files['images'])} 个\n")
        f.write(f"- 文本文件：{len(files['texts'])} 个\n")
        f.write(f"- 其他格式：{len(files['other'])} 个\n\n")
        
        if files['images']:
            f.write("## 图像档案列表（需交由视觉工具逐一解析）\n")
            for img in sorted(files['images']):
                f.write(f"- {img}\n")
            f.write("\n")
        
        if files['texts']:
            f.write("## 纯文本内容提取\n")
            for txt in sorted(files['texts']):
                f.write(f"\n### {os.path.basename(txt)}\n")
                try:
                    with open(txt, 'r', encoding='utf-8', errors='ignore') as tf:
                        content = tf.read(5000)
                    f.write(f"```\n{content}\n```\n")
                except Exception as e:
                    f.write(f"文件读取失败：{e}\n")
    
    print(f"目录扫描完成，资产归档清单已写入 {args.output}")
    print(f"系统提示：图片类的截图需配置视觉工具辅助查看，本扫描器仅列出物理路径。")


if __name__ == '__main__':
    main()