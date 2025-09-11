#!/usr/bin/env python3
"""
OpenAPI Converter 配置管理
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为 None 则使用默认配置
        """
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ 加载配置文件失败: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'standard_headers': [
                "X-App-version;",
                "X-Os-version;",
                "X-Country;",
                "X-Language;",
                "X-Timezone;",
                "X-Os;",
                "X-Client-Timestamp;",
                "X-Phone-Model;",
                "User-Agent;",
                "X-Auth-Token;",
                "X-Open-Udid: 733f9d17-9bcb-4cc0-94ba-8eb5e49b609f"
            ],
            'content_type': 'application/json',
            'api_version': '0.0.1',
            'output_format': {
                'include_comments': True,
                'indent_size': 2,
                'quote_style': 'double'
            },
            'naming_convention': {
                'case': 'snake_case',  # snake_case, camelCase, kebab-case
                'prefix': '',
                'suffix': ''
            },
            'response_format': {
                'success_code': 0,
                'success_msg': '',
                'include_metadata': True
            }
        }
    
    def save_config(self, output_file: str = None):
        """保存配置到文件"""
        if output_file is None:
            output_file = self.config_file or 'openapi-converter-config.yaml'
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            print(f"✅ 配置已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update_headers(self, headers: list):
        """更新标准 headers"""
        self.set('standard_headers', headers)
    
    def add_header(self, header: str):
        """添加单个 header"""
        headers = self.get('standard_headers', [])
        if header not in headers:
            headers.append(header)
            self.set('standard_headers', headers)
    
    def remove_header(self, header: str):
        """移除单个 header"""
        headers = self.get('standard_headers', [])
        if header in headers:
            headers.remove(header)
            self.set('standard_headers', headers)
    
    def create_sample_config(self, output_file: str = 'converter-config.yaml'):
        """创建示例配置文件"""
        sample_config = {
            'standard_headers': [
                "X-App-version;",
                "X-Os-version;",
                "X-Country;",
                "X-Language;",
                "X-Timezone;",
                "X-Os;",
                "X-Client-Timestamp;",
                "X-Phone-Model;",
                "User-Agent;",
                "X-Auth-Token;",
                "X-Open-Udid: 733f9d17-9bcb-4cc0-94ba-8eb5e49b609f"
            ],
            'content_type': 'application/json',
            'api_version': '0.0.1',
            'output_format': {
                'include_comments': True,
                'indent_size': 2,
                'quote_style': 'double'
            },
            'naming_convention': {
                'case': 'snake_case',
                'prefix': '',
                'suffix': ''
            },
            'response_format': {
                'success_code': 0,
                'success_msg': '',
                'include_metadata': True
            },
            'custom_templates': {
                'curl_template': 'curl --location --request {method} "{{host}}{path}"',
                'header_template': '--header "{header}"',
                'body_template': "--data-raw '{body}'"
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True, indent=2)
            print(f"✅ 示例配置文件已创建: {output_file}")
            print("💡 您可以编辑此文件来自定义转换行为")
        except Exception as e:
            print(f"❌ 创建示例配置失败: {e}")
