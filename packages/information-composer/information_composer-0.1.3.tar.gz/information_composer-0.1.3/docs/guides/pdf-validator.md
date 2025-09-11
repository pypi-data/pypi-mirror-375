# PDF 验证器指南

PDF 验证器是 Information Composer 的核心功能之一，用于验证 PDF 文件的格式和完整性。

## 🎯 功能概述

PDF 验证器提供以下功能：

- **格式验证**: 检查 PDF 文件是否符合标准格式
- **完整性检查**: 验证文件是否完整且可读
- **页面统计**: 获取 PDF 页面数量
- **错误报告**: 提供详细的错误信息
- **批量处理**: 支持批量验证多个文件

## 🚀 快速开始

### 命令行使用

```bash
# 验证单个文件
pdf-validator document.pdf

# 验证多个文件
pdf-validator file1.pdf file2.pdf file3.pdf

# 验证目录中的所有 PDF
pdf-validator -d /path/to/pdfs

# 递归验证目录
pdf-validator -d /path/to/pdfs -r

# 详细输出
pdf-validator -d /path/to/pdfs -v

# JSON 格式输出
pdf-validator -d /path/to/pdfs --json

# 只显示统计信息
pdf-validator -d /path/to/pdfs --stats-only
```

### Python API 使用

```python
from information_composer.pdf.validator import PDFValidator

# 创建验证器
validator = PDFValidator(verbose=True)

# 验证单个文件
is_valid, error_msg = validator.validate_single_pdf("document.pdf")
if is_valid:
    print("PDF 文件有效")
else:
    print(f"PDF 文件无效: {error_msg}")

# 验证目录
validator.validate_directory("/path/to/pdfs", recursive=True)

# 获取统计信息
stats = validator.get_validation_stats()
print(f"总文件数: {stats['total_files']}")
print(f"有效文件: {stats['valid_files']}")
print(f"无效文件: {stats['invalid_files']}")
print(f"成功率: {stats['success_rate']:.1f}%")
```

## 📖 详细功能

### 1. 单文件验证

```python
from information_composer.pdf.validator import PDFValidator

validator = PDFValidator()

# 基本验证
is_valid, error = validator.validate_single_pdf("document.pdf")

# 检查结果
if is_valid:
    print("✅ 文件验证通过")
else:
    print(f"❌ 文件验证失败: {error}")
```

### 2. 目录验证

```python
# 验证目录中的所有 PDF
validator.validate_directory("/path/to/pdfs")

# 递归验证子目录
validator.validate_directory("/path/to/pdfs", recursive=True)

# 获取验证结果
stats = validator.get_validation_stats()
print(f"验证了 {stats['total_files']} 个文件")
print(f"成功: {stats['valid_files']} 个")
print(f"失败: {stats['invalid_files']} 个")
```

### 3. 批量文件验证

```python
# 验证文件列表
file_list = ["file1.pdf", "file2.pdf", "file3.pdf"]
validator.validate_files(file_list)

# 获取详细结果
stats = validator.get_validation_stats()
for file_path, error_msg in stats['error_details']:
    print(f"文件: {file_path}")
    print(f"错误: {error_msg}")
```

### 4. 统计信息

```python
# 获取统计信息
stats = validator.get_validation_stats()

# 统计信息包含：
# - total_files: 总文件数
# - valid_files: 有效文件数
# - invalid_files: 无效文件数
# - success_rate: 成功率
# - error_details: 错误详情列表

print(f"验证统计:")
print(f"  总文件数: {stats['total_files']}")
print(f"  有效文件: {stats['valid_files']}")
print(f"  无效文件: {stats['invalid_files']}")
print(f"  成功率: {stats['success_rate']:.1f}%")
```

## ⚙️ 配置选项

### 验证器参数

```python
validator = PDFValidator(
    verbose=True,  # 详细输出
    strict_mode=True,  # 严格模式（默认: False）
    check_encryption=True,  # 检查加密（默认: True）
    max_pages=1000  # 最大页数限制（默认: 无限制）
)
```

### 环境变量

```bash
# PDF 验证配置
export PDF_STRICT_MODE=true
export PDF_CHECK_ENCRYPTION=true
export PDF_MAX_PAGES=1000
export PDF_VERBOSE=true
```

## 🔧 高级用法

### 1. 自定义验证逻辑

```python
from information_composer.pdf.validator import PDFValidator

class CustomPDFValidator(PDFValidator):
    def validate_single_pdf(self, pdf_path: str):
        # 调用父类方法
        is_valid, error = super().validate_single_pdf(pdf_path)
        
        if is_valid:
            # 添加自定义检查
            if self._check_custom_requirements(pdf_path):
                return True, None
            else:
                return False, "不满足自定义要求"
        
        return is_valid, error
    
    def _check_custom_requirements(self, pdf_path: str) -> bool:
        # 实现自定义检查逻辑
        return True

# 使用自定义验证器
validator = CustomPDFValidator()
```

### 2. 结果处理

```python
def process_validation_results(validator: PDFValidator):
    stats = validator.get_validation_stats()
    
    # 处理有效文件
    print(f"✅ 有效文件 ({stats['valid_files']} 个):")
    # 这里可以添加处理有效文件的逻辑
    
    # 处理无效文件
    if stats['invalid_files'] > 0:
        print(f"❌ 无效文件 ({stats['invalid_files']} 个):")
        for file_path, error_msg in stats['error_details']:
            print(f"  - {file_path}: {error_msg}")
            # 这里可以添加处理无效文件的逻辑

# 使用
validator = PDFValidator()
validator.validate_directory("/path/to/pdfs")
process_validation_results(validator)
```

### 3. 进度监控

```python
import time
from tqdm import tqdm

def validate_with_progress(validator: PDFValidator, file_list: list):
    results = []
    
    for file_path in tqdm(file_list, desc="验证 PDF 文件"):
        is_valid, error = validator.validate_single_pdf(file_path)
        results.append((file_path, is_valid, error))
        time.sleep(0.1)  # 避免过于频繁的请求
    
    return results

# 使用
file_list = ["file1.pdf", "file2.pdf", "file3.pdf"]
results = validate_with_progress(validator, file_list)
```

## 📊 输出格式

### 标准输出

```
找到 5 个PDF文件，开始验证...
------------------------------------------------------------
✓ document1.pdf: 有效PDF文件，共10页
✓ document2.pdf: 有效PDF文件，共25页
✗ document3.pdf: PDF格式错误: Invalid PDF structure
✓ document4.pdf: 有效PDF文件，共8页
✗ document5.pdf: 文件为空

============================================================
验证结果摘要
============================================================
总文件数: 5
有效PDF: 3
无效PDF: 2

无效文件详情:
----------------------------------------
文件: document3.pdf
错误: PDF格式错误: Invalid PDF structure

文件: document5.pdf
错误: 文件为空
```

### JSON 输出

```bash
pdf-validator -d /path/to/pdfs --json
```

```json
{
  "total_files": 5,
  "valid_files": 3,
  "invalid_files": 2,
  "success_rate": 60.0,
  "error_details": [
    {
      "file": "document3.pdf",
      "error": "PDF格式错误: Invalid PDF structure"
    },
    {
      "file": "document5.pdf",
      "error": "文件为空"
    }
  ]
}
```

## 🛠️ 故障排除

### 常见问题

#### 1. 文件不存在
```
文件不存在: /path/to/file.pdf
```

**解决方案**: 检查文件路径是否正确

#### 2. 权限问题
```
Permission denied: /path/to/file.pdf
```

**解决方案**: 检查文件权限，确保有读取权限

#### 3. 文件损坏
```
PDF格式错误: Invalid PDF structure
```

**解决方案**: 文件可能已损坏，尝试重新下载或使用其他工具修复

#### 4. 内存不足
```
Memory error: File too large
```

**解决方案**: 增加系统内存或使用更小的文件

### 调试技巧

```python
# 启用详细输出
validator = PDFValidator(verbose=True)

# 检查特定文件
is_valid, error = validator.validate_single_pdf("problematic.pdf")
if not is_valid:
    print(f"详细错误信息: {error}")
```

## 📚 相关文档

- [安装指南](../installation.md) - 安装和配置
- [快速开始](../quickstart.md) - 快速上手
- [API 参考](../api/pdf.md) - PDF API 文档
- [示例代码](../examples/) - 使用示例

---

**PDF 验证器** 让您轻松验证 PDF 文件的完整性和有效性！
