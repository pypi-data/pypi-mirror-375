"""
配置管理模块

管理项目的所有配置，包括DashScope API配置、模型参数等。
"""

import contextlib
from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class DashScopeConfig:
    """DashScope配置"""

    # API配置
    api_key: str = field(default_factory=lambda: os.getenv("DASHSCOPE_API_KEY", ""))
    model: str = field(
        default_factory=lambda: os.getenv("DASHSCOPE_MODEL", "qwen-plus-latest")
    )

    # 模型参数
    temperature: float = 0.1
    max_tokens: int = 4096
    top_p: float = 0.8
    enable_search: bool = False
    result_format: str = "message"

    # 流式配置
    stream: bool = False

    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0

    # 超时配置
    timeout: int = 30

    def validate(self) -> bool:
        """验证配置有效性"""
        if not self.api_key:
            logger.error("DashScope API密钥未配置")
            return False

        if not self.model:
            logger.error("DashScope模型未配置")
            return False

        return True


@dataclass
class LLMConfig:
    """LLM通用配置"""

    # 提供商选择
    provider: str = "dashscope"

    # 模型配置
    model: str = "qwen-plus-latest"

    # 性能配置
    max_concurrent_requests: int = 5
    request_timeout: int = 30

    # 缓存配置
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    cache_dir: str = "./cache"

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ProcessingConfig:
    """文档处理配置"""

    # 文件配置
    max_file_size_mb: int = 50
    supported_formats: List[str] = field(default_factory=lambda: ["md", "markdown"])
    output_format: str = "markdown"

    # 处理配置
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # 内容提取配置
    extraction_targets: List[str] = field(
        default_factory=lambda: [
            "title",
            "abstract",
            "methods",
            "results",
            "discussion",
        ]
    )

    # 内容过滤配置
    filter_targets: List[str] = field(
        default_factory=lambda: [
            "references",
            "affiliations",
            "acknowledgments",
            "appendices",
            "footnotes",
            "page_numbers",
        ]
    )


@dataclass
class AppConfig:
    """应用主配置"""

    # 环境配置
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )

    # 路径配置
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    cache_dir: Path = field(default_factory=lambda: Path("./cache"))
    output_dir: Path = field(default_factory=lambda: Path("./output"))

    # 子配置
    dashscope: DashScopeConfig = field(default_factory=DashScopeConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    def __post_init__(self):
        """初始化后处理"""
        # 确保目录存在
        self.cache_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # 设置日志级别
        logging.basicConfig(
            level=getattr(logging, self.llm.log_level.upper()),
            format=self.llm.log_format,
        )

    def validate(self) -> bool:
        """验证所有配置"""
        validations = [
            self.dashscope.validate(),
            # 可以添加其他配置验证
        ]
        return all(validations)

    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置字典"""
        return {
            "provider": self.llm.provider,
            "model": self.dashscope.model,
            "api_key": self.dashscope.api_key,
            "temperature": self.dashscope.temperature,
            "max_tokens": self.dashscope.max_tokens,
            "top_p": self.dashscope.top_p,
            "enable_search": self.dashscope.enable_search,
            "result_format": self.dashscope.result_format,
            "stream": self.dashscope.stream,
            "max_retries": self.dashscope.max_retries,
            "retry_delay": self.dashscope.retry_delay,
            "timeout": self.dashscope.timeout,
        }

    def get_processing_config(self) -> Dict[str, Any]:
        """获取处理配置字典"""
        return {
            "max_file_size_mb": self.processing.max_file_size_mb,
            "supported_formats": self.processing.supported_formats,
            "output_format": self.processing.output_format,
            "chunk_size": self.processing.chunk_size,
            "chunk_overlap": self.processing.chunk_overlap,
            "extraction_targets": self.processing.extraction_targets,
            "filter_targets": self.processing.filter_targets,
        }


class ConfigManager:
    """配置管理器"""

    _instance: Optional["ConfigManager"] = None
    _config: Optional[AppConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._config = self._load_config()

    def _load_config(self) -> AppConfig:
        """加载配置"""
        try:
            config = AppConfig()

            # 从环境变量加载配置
            self._load_from_env(config)

            # 验证配置
            if not config.validate():
                logger.warning("配置验证失败，使用默认配置")

            logger.info("配置加载成功")
            return config

        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            # 返回默认配置
            return AppConfig()

    def _load_from_env(self, config: AppConfig):
        """从环境变量加载配置"""
        # DashScope配置
        if os.getenv("DASHSCOPE_API_KEY"):
            config.dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

        if os.getenv("DASHSCOPE_MODEL"):
            config.dashscope.model = os.getenv("DASHSCOPE_MODEL")

        # 应用配置
        if os.getenv("APP_ENV"):
            config.app_env = os.getenv("APP_ENV")

        if os.getenv("DEBUG"):
            config.debug = os.getenv("DEBUG").lower() == "true"

        # 性能配置
        if os.getenv("MAX_CONCURRENT_REQUESTS"):
            with contextlib.suppress(ValueError):
                config.llm.max_concurrent_requests = int(
                    os.getenv("MAX_CONCURRENT_REQUESTS")
                )

        if os.getenv("REQUEST_TIMEOUT"):
            with contextlib.suppress(ValueError):
                config.llm.request_timeout = int(os.getenv("REQUEST_TIMEOUT"))

        # 缓存配置
        if os.getenv("ENABLE_CACHE"):
            config.llm.enable_cache = os.getenv("ENABLE_CACHE").lower() == "true"

        if os.getenv("CACHE_TTL_HOURS"):
            with contextlib.suppress(ValueError):
                config.llm.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS"))

        if os.getenv("CACHE_DIR"):
            config.llm.cache_dir = os.getenv("CACHE_DIR")

        # 文件处理配置
        if os.getenv("MAX_FILE_SIZE_MB"):
            with contextlib.suppress(ValueError):
                config.processing.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB"))

        if os.getenv("SUPPORTED_FORMATS"):
            formats = os.getenv("SUPPORTED_FORMATS").split(",")
            config.processing.supported_formats = [f.strip() for f in formats]

        if os.getenv("OUTPUT_FORMAT"):
            config.processing.output_format = os.getenv("OUTPUT_FORMAT")

    def get_config(self) -> AppConfig:
        """获取配置实例"""
        return self._config

    def reload_config(self):
        """重新加载配置"""
        self._config = self._load_config()

    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                logger.warning(f"未知配置项: {key}")


# 全局配置实例
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """获取配置实例的便捷函数"""
    return config_manager.get_config()


def get_llm_config() -> Dict[str, Any]:
    """获取LLM配置的便捷函数"""
    return config_manager.get_config().get_llm_config()


def get_processing_config() -> Dict[str, Any]:
    """获取处理配置的便捷函数"""
    return config_manager.get_config().get_processing_config()
