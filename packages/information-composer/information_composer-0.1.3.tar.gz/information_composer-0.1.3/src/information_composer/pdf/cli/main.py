#!/usr/bin/env python3
"""
PDF文件格式验证CLI工具
"""

import argparse
from pathlib import Path
import sys
from typing import List

from information_composer.pdf.validator import PDFValidator


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PDF文件格式验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  pdf-validator file1.pdf file2.pdf          # 验证指定文件
  pdf-validator -d /path/to/directory        # 验证目录中所有PDF
  pdf-validator -d /path/to/directory -r     # 递归验证目录
  pdf-validator -d /path/to/directory -v     # 详细输出
  pdf-validator -d /path/to/directory --json # JSON格式输出
        """,
    )

    parser.add_argument("files", nargs="*", help="要验证的PDF文件路径")

    parser.add_argument("-d", "--directory", help="要验证的目录路径")

    parser.add_argument(
        "-r", "--recursive", action="store_true", help="递归搜索子目录中的PDF文件"
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细输出信息")

    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")

    parser.add_argument(
        "--stats-only", action="store_true", help="只显示统计信息，不显示详细错误"
    )

    args = parser.parse_args()

    # 创建验证器
    validator = PDFValidator(verbose=args.verbose)

    try:
        if args.directory:
            # 验证目录
            validator.validate_directory(args.directory, args.recursive)
        elif args.files:
            # 验证指定文件
            validator.validate_files(args.files)
        else:
            # 如果没有指定参数，显示帮助信息
            parser.print_help()
            return

        # 输出结果
        if args.json:
            import json

            stats = validator.get_validation_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        elif args.stats_only:
            stats = validator.get_validation_stats()
            print(f"总文件数: {stats['total_files']}")
            print(f"有效PDF: {stats['valid_files']}")
            print(f"无效PDF: {stats['invalid_files']}")
            print(f"成功率: {stats['success_rate']:.1f}%")
        else:
            # 打印结果摘要
            validator.print_summary()

    except KeyboardInterrupt:
        print("\n\n验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
