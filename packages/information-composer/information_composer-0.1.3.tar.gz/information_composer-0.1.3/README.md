# Information Composer

[![Code Quality](https://github.com/yourusername/information-composer/actions/workflows/code-quality.yaml/badge.svg)](https://github.com/yourusername/information-composer/actions/workflows/code-quality.yaml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A comprehensive toolkit for collecting, composing, and filtering information from various web resources with AI-powered markdown processing.

## Features

- **PDF Validation**: Validate PDF file formats and integrity
- **Markdown Processing**: Advanced markdown processing with LLM filtering
- **PubMed Integration**: Query and process PubMed data
- **DOI Management**: Download and manage DOI references
- **Code Quality**: Automated code quality checks with Ruff
- **Multi-format Support**: Support for various data formats and sources

## Installation

### Prerequisites

- Python 3.10, 3.11, 3.12, or 3.13
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/information-composer.git
cd information-composer
```

2. Create and activate virtual environment:
```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Quick Start

### Activate Environment
```bash
# Linux/macOS
source activate.sh

# Windows
activate.bat
```

### Available Commands

- `md-llm-filter` - Run MD_LLM_Filter CLI
- `pdf-validator` - Run PDF validator CLI
- `python -m information_composer.core.doi_downloader` - Run DOI downloader
- `python -m information_composer.pubmed.pubmed` - Run PubMed tools

### Examples

```bash
# Validate PDF files
pdf-validator file.pdf

# Validate directory of PDFs
pdf-validator -d /path/to/directory -r

# Filter markdown with LLM
md-llm-filter input.md output.md

# Run code quality checks
python scripts/check_code.py --fix
```

## Development

### Code Quality

This project uses Ruff for code quality checks:

```bash
# Run all checks
python scripts/check_code.py

# Auto-fix issues
python scripts/check_code.py --fix

# With verbose output
python scripts/check_code.py --verbose
```

### Testing

```bash
# Run tests
python scripts/check_code.py --with-tests

# Or directly with pytest
pytest tests/ -v
```

## CI/CD

This project uses GitHub Actions for continuous integration:

- **Code Quality**: Automated Ruff checks on multiple Python versions
- **Testing**: Comprehensive test suite execution
- **Release**: Automated package building and publishing

See [.github/README.md](.github/README.md) for detailed CI/CD documentation.

## Documentation

- [📚 完整文档](docs/README.md) - 项目完整文档
- [🚀 快速开始](docs/quickstart.md) - 5分钟快速上手
- [⚙️ 配置说明](docs/configuration.md) - 详细配置选项
- [📖 功能指南](docs/guides/) - 各功能详细说明
- [🔧 开发指南](docs/development/) - 开发和贡献指南

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run code quality checks: `python scripts/check_code.py --fix`
5. Run tests: `python scripts/check_code.py --with-tests`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue on GitHub.
