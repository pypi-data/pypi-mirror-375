"""
OpenAPI Converter - 独立的 OpenAPI 转换工具

将 OpenAPI 3.0.1 格式的 YAML 文件转换为项目所需的 API 配置文件格式。
"""

__version__ = "0.1.0"
__author__ = "OpenAPI Converter Team"
__email__ = "team@openapi-converter.dev"

from .converter import OpenAPIConverter

__all__ = ["OpenAPIConverter"]
