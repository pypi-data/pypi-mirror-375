"""
PDF文件格式验证工具
使用pypdfium2库来检测PDF文件是否格式正确
"""

import os
from pathlib import Path
import sys
from typing import List, Optional, Tuple

import pypdfium2 as pdfium
from pypdfium2._helpers.misc import PdfiumError


class PDFValidator:
    """PDF文件验证器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.valid_count = 0
        self.invalid_count = 0
        self.error_details = []

    def validate_single_pdf(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证单个PDF文件

        Args:
            pdf_path: PDF文件路径

        Returns:
            (is_valid, error_message): 验证结果和错误信息
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(pdf_path):
                return False, f"文件不存在: {pdf_path}"

            # 检查文件大小
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                return False, "文件为空"

            # 尝试打开PDF文件
            with open(pdf_path, "rb") as file:
                pdf_doc = pdfium.PdfDocument(file)

                # 获取页面数量
                page_count = len(pdf_doc)

                if self.verbose:
                    print(f"✓ {pdf_path}: 有效PDF文件，共{page_count}页")

                return True, None

        except PdfiumError as e:
            error_msg = f"PDF格式错误: {e!s}"
            if self.verbose:
                print(f"✗ {pdf_path}: {error_msg}")
            return False, error_msg

        except Exception as e:
            error_msg = f"未知错误: {e!s}"
            if self.verbose:
                print(f"✗ {pdf_path}: {error_msg}")
            return False, error_msg

    def validate_directory(self, directory_path: str, recursive: bool = False) -> None:
        """
        验证目录中的所有PDF文件

        Args:
            directory_path: 目录路径
            recursive: 是否递归搜索子目录
        """
        directory = Path(directory_path)

        if not directory.exists():
            print(f"错误: 目录不存在 - {directory_path}")
            return

        if not directory.is_dir():
            print(f"错误: 不是有效目录 - {directory_path}")
            return

        # 搜索PDF文件
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))

        if not pdf_files:
            print(f"在目录 {directory_path} 中未找到PDF文件")
            return

        print(f"找到 {len(pdf_files)} 个PDF文件，开始验证...")
        print("-" * 60)

        for pdf_file in pdf_files:
            is_valid, error_msg = self.validate_single_pdf(str(pdf_file))

            if is_valid:
                self.valid_count += 1
            else:
                self.invalid_count += 1
                self.error_details.append((str(pdf_file), error_msg))

    def validate_files(self, file_paths: List[str]) -> None:
        """
        验证指定的PDF文件列表

        Args:
            file_paths: PDF文件路径列表
        """
        print(f"开始验证 {len(file_paths)} 个PDF文件...")
        print("-" * 60)

        for file_path in file_paths:
            is_valid, error_msg = self.validate_single_pdf(file_path)

            if is_valid:
                self.valid_count += 1
            else:
                self.invalid_count += 1
                self.error_details.append((file_path, error_msg))

    def get_validation_stats(self) -> dict:
        """
        获取验证统计信息

        Returns:
            包含统计信息的字典
        """
        total = self.valid_count + self.invalid_count
        return {
            "total_files": total,
            "valid_files": self.valid_count,
            "invalid_files": self.invalid_count,
            "success_rate": (self.valid_count / total * 100) if total > 0 else 0,
            "error_details": self.error_details,
        }

    def print_summary(self) -> None:
        """打印验证结果摘要"""
        total = self.valid_count + self.invalid_count

        print("\n" + "=" * 60)
        print("验证结果摘要")
        print("=" * 60)
        print(f"总文件数: {total}")
        print(f"有效PDF: {self.valid_count}")
        print(f"无效PDF: {self.invalid_count}")

        if self.invalid_count > 0:
            print("\n无效文件详情:")
            print("-" * 40)
            for file_path, error_msg in self.error_details:
                print(f"文件: {file_path}")
                print(f"错误: {error_msg}")
                print()

    def reset_stats(self) -> None:
        """重置统计信息"""
        self.valid_count = 0
        self.invalid_count = 0
        self.error_details = []
