# Information Composer 项目概览

## 🎯 项目简介

Information Composer 是一个综合性的信息收集、处理和过滤工具包，专为学术研究、文档管理和信息处理而设计。它集成了多种强大的功能，帮助用户高效地处理各种格式的文档和数据。

## ✨ 核心特性

### 📄 PDF 处理
- **格式验证**: 验证 PDF 文件格式和完整性
- **批量处理**: 支持批量验证多个 PDF 文件
- **错误报告**: 提供详细的错误信息和统计
- **递归搜索**: 支持目录递归搜索

### 📝 Markdown 处理
- **格式转换**: Markdown 与 JSON 之间的转换
- **内容提取**: 提取标题、链接、图片、表格等元素
- **格式清理**: 清理和标准化 Markdown 格式
- **元数据提取**: 提取文档元数据信息

### 🔬 学术文献处理
- **PubMed 集成**: 查询和处理 PubMed 文献数据
- **DOI 管理**: 下载和管理 DOI 引用
- **关键词过滤**: 基于关键词的文献过滤
- **批量处理**: 支持批量文献处理

### 🤖 AI 驱动过滤
- **LLM 集成**: 使用大语言模型进行智能过滤
- **内容分析**: 智能分析文档内容
- **自动分类**: 自动分类和标记文档
- **质量评估**: 评估文档质量和相关性

## 🏗️ 项目架构

```
information-composer/
├── src/information_composer/    # 主源代码
│   ├── pdf/                    # PDF 处理模块
│   │   ├── validator.py        # PDF 验证器
│   │   └── cli/                # PDF CLI 工具
│   ├── markdown/               # Markdown 处理模块
│   │   ├── markdown.py         # 核心处理功能
│   │   └── vendor/             # 第三方库
│   ├── pubmed/                 # PubMed 集成模块
│   │   ├── pubmed.py           # 查询功能
│   │   └── baseline.py         # 基线数据
│   ├── core/                   # 核心功能模块
│   │   ├── doi_downloader.py   # DOI 下载器
│   │   └── downloader.py       # 通用下载器
│   ├── llm_filter/             # LLM 过滤模块
│   │   ├── core/               # 核心过滤逻辑
│   │   ├── llm/                # LLM 接口
│   │   ├── config/             # 配置管理
│   │   └── cli/                # CLI 工具
│   └── sites/                  # 网站解析模块
├── examples/                   # 使用示例
├── scripts/                    # 工具脚本
├── docs/                       # 项目文档
└── tests/                      # 测试文件
```

## 🚀 快速开始

### 安装
```bash
# 克隆项目
git clone https://github.com/yourusername/information-composer.git
cd information-composer

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装项目
pip install -e .
```

### 基本使用
```bash
# 验证 PDF 文件
pdf-validator document.pdf

# 过滤 Markdown 文档
md-llm-filter input.md output.md

# 运行代码质量检查
python scripts/check_code.py --fix
```

## 🛠️ 技术栈

### 核心依赖
- **Python 3.10+**: 主要编程语言
- **pypdfium2**: PDF 处理库
- **dashscope**: 阿里云大语言模型 API
- **llama-index**: 大语言模型集成框架
- **beautifulsoup4**: HTML/XML 解析
- **requests**: HTTP 请求库

### 开发工具
- **Ruff**: 代码质量检查
- **Black**: 代码格式化
- **pytest**: 测试框架
- **GitHub Actions**: CI/CD

### 支持格式
- **PDF**: 文档验证和处理
- **Markdown**: 文档格式转换
- **JSON**: 数据交换格式
- **XML**: PubMed 数据格式
- **TXT**: 纯文本处理

## 📊 功能模块

### 1. PDF 验证器
- 文件格式验证
- 完整性检查
- 页面统计
- 错误报告
- 批量处理

### 2. Markdown 处理器
- 格式转换
- 内容提取
- 格式清理
- 元数据提取
- 链接验证

### 3. PubMed 集成
- 文献查询
- 数据解析
- 关键词过滤
- 批量处理
- 缓存管理

### 4. DOI 管理器
- DOI 下载
- 元数据提取
- 批量处理
- 格式转换
- 错误处理

### 5. LLM 过滤器
- 智能过滤
- 内容分析
- 自动分类
- 质量评估
- 批量处理

## 🔧 配置选项

### 环境变量
```bash
# 必需配置
export DASHSCOPE_API_KEY="your-api-key"

# 可选配置
export MAX_CONCURRENT_REQUESTS=5
export REQUEST_TIMEOUT=30
export ENABLE_CACHE=true
```

### 配置文件
```yaml
# config.yaml
llm:
  api_key: "your-api-key"
  model: "qwen-plus"
  max_concurrent_requests: 5

processing:
  max_file_size_mb: 10
  supported_formats: ["pdf", "md", "txt"]
```

## 🧪 质量保证

### 代码质量
- Ruff 代码检查
- Black 代码格式化
- 类型注解
- 文档字符串
- 单元测试

### CI/CD
- GitHub Actions 集成
- 多 Python 版本测试
- 自动化代码检查
- 自动发布

### 测试覆盖
- 单元测试
- 集成测试
- 端到端测试
- 性能测试

## 📈 性能特性

### 并发处理
- 多线程支持
- 异步处理
- 批量操作
- 资源管理

### 缓存机制
- 智能缓存
- 过期管理
- 存储优化
- 性能提升

### 错误处理
- 优雅降级
- 重试机制
- 错误恢复
- 日志记录

## 🌟 使用场景

### 学术研究
- 文献收集和整理
- 文档质量检查
- 内容过滤和分析
- 数据标准化

### 文档管理
- 批量文档处理
- 格式转换
- 内容提取
- 质量评估

### 信息处理
- 数据清洗
- 格式标准化
- 内容过滤
- 智能分析

## 🤝 贡献指南

### 开发环境
1. Fork 项目
2. 创建功能分支
3. 安装开发依赖
4. 运行代码检查
5. 提交 Pull Request

### 代码规范
- 遵循 PEP 8 标准
- 使用类型注解
- 编写文档字符串
- 添加单元测试

### 测试要求
- 所有新功能必须有测试
- 测试覆盖率 > 80%
- 通过所有代码检查
- 通过 CI/CD 检查

## 📚 文档结构

```
docs/
├── README.md              # 文档导航
├── overview.md            # 项目概览
├── installation.md        # 安装指南
├── quickstart.md          # 快速开始
├── configuration.md       # 配置说明
├── guides/                # 功能指南
│   ├── pdf-validator.md   # PDF 验证器
│   ├── markdown-processor.md # Markdown 处理器
│   ├── pubmed-integration.md # PubMed 集成
│   ├── doi-manager.md     # DOI 管理器
│   └── llm-filter.md      # LLM 过滤器
├── api/                   # API 参考
├── examples/              # 示例代码
└── development/           # 开发指南
    ├── code-quality.md    # 代码质量
    ├── testing.md         # 测试指南
    └── contributing.md    # 贡献指南
```

## 🆘 支持与帮助

### 获取帮助
1. 查看 [文档](README.md)
2. 搜索 [Issues](https://github.com/yourusername/information-composer/issues)
3. 创建新的 Issue
4. 参与讨论

### 常见问题
- 查看 [FAQ](faq.md)
- 搜索现有问题
- 查看错误日志
- 检查配置设置

---

**Information Composer** - 让信息处理更简单、更智能、更高效！
