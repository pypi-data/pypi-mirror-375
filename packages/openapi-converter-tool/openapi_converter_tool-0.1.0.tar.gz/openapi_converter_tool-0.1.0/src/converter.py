#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI 3.0.1 到目标 API 格式的转换器
将 OpenAPI 格式的 YAML 文件转换为项目所需的 API 配置文件格式
"""

import yaml
import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class OpenAPIConverter:
    """OpenAPI 格式转换器"""
    
    def __init__(self, openapi_file: str, output_dir: str = "api", template_config: dict = None):
        """
        初始化转换器
        
        Args:
            openapi_file: OpenAPI YAML 文件路径
            output_dir: 输出目录
            template_config: 模板配置，用于自定义转换行为
        """
        self.openapi_file = openapi_file
        self.output_dir = output_dir
        self.openapi_data = None
        self.schemas = {}
        self.template_config = template_config or {}
        
    def load_openapi_file(self):
        """加载 OpenAPI 文件"""
        try:
            with open(self.openapi_file, 'r', encoding='utf-8') as f:
                self.openapi_data = yaml.safe_load(f)
            self.schemas = self.openapi_data.get('components', {}).get('schemas', {})
            print(f"✅ 成功加载 OpenAPI 文件: {self.openapi_file}")
        except Exception as e:
            print(f"❌ 加载 OpenAPI 文件失败: {e}")
            raise
    
    def resolve_schema_ref(self, ref: str) -> Dict[str, Any]:
        """解析 schema 引用"""
        if ref.startswith('#/components/schemas/'):
            schema_name = ref.split('/')[-1]
            return self.schemas.get(schema_name, {})
        return {}
    
    def convert_type(self, schema: Dict[str, Any]) -> str:
        """转换 OpenAPI 类型到目标格式类型"""
        if 'type' not in schema:
            return "string"
        
        openapi_type = schema['type']
        format_type = schema.get('format', '')
        
        type_mapping = {
            'string': 'string',
            'integer': 'integer',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'array',
            'object': 'object'
        }
        
        return type_mapping.get(openapi_type, 'string')
    
    def generate_api_name(self, path: str, method: str) -> str:
        """生成 API 名称"""
        # 移除路径前缀和版本号
        clean_path = re.sub(r'^/v\d+/', '', path)
        # 取路径的最后一部分作为API名称
        path_parts = clean_path.strip('/').split('/')
        last_part = path_parts[-1] if path_parts else 'api'
        
        # 将驼峰命名转换为下划线命名
        # 例如: isShowQuestionnaire -> is_show_questionnaire
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', last_part)
        name = name.lower()
        
        return name
    
    def generate_curl_command(self, path: str, method: str, parameters: List[Dict], request_body: Dict = None) -> str:
        """生成 curl 命令"""
        # 基础 curl 命令
        curl_parts = [f'curl --location --request {method.upper()} "{{{{host}}}}{path}"']
        
        # 从配置中获取标准 headers，如果没有配置则使用默认值
        standard_headers = self.template_config.get('standard_headers', [
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
        ])
        
        for header in standard_headers:
            curl_parts.append(f'--header "{header}"')
        
        # 添加 Content-Type
        content_type = self.template_config.get('content_type', 'application/json')
        curl_parts.append(f'--header "Content-Type: {content_type}"')
        
        # 生成请求体
        if request_body:
            body_data = self.generate_request_body(request_body)
            curl_parts.append(f"--data-raw '{body_data}'")
        
        return ' \\\n'.join(curl_parts)
    
    def generate_request_body(self, request_body: Dict) -> str:
        """生成请求体 JSON"""
        if 'content' not in request_body:
            return '{}'
        
        content = request_body['content']
        if 'application/json' not in content:
            return '{}'
        
        schema = content['application/json'].get('schema', {})
        
        if '$ref' in schema:
            ref_schema = self.resolve_schema_ref(schema['$ref'])
            return self.schema_to_json_example(ref_schema)
        
        return self.schema_to_json_example(schema)
    
    def schema_to_json_example(self, schema: Dict[str, Any]) -> str:
        """将 schema 转换为 JSON 示例"""
        if 'properties' not in schema:
            return '{}'
        
        properties = {}
        for prop_name, prop_schema in schema['properties'].items():
            prop_type = self.convert_type(prop_schema)
            
            if prop_type == 'string':
                properties[prop_name] = f'{{{{{prop_name}}}}}'
            elif prop_type == 'integer':
                properties[prop_name] = f'{{{{{prop_name}}}}}'
            elif prop_type == 'number':
                properties[prop_name] = f'{{{{{prop_name}}}}}'
            elif prop_type == 'boolean':
                properties[prop_name] = True
            elif prop_type == 'array':
                if 'items' in prop_schema:
                    items_schema = prop_schema['items']
                    if '$ref' in items_schema:
                        ref_schema = self.resolve_schema_ref(items_schema['$ref'])
                        properties[prop_name] = [self.schema_to_dict_example(ref_schema)]
                    else:
                        items_type = self.convert_type(items_schema)
                        if items_type == 'string':
                            properties[prop_name] = [f'{{{{{prop_name}_item}}}}']
                        elif items_type == 'object':
                            properties[prop_name] = [self.schema_to_dict_example(items_schema)]
                        else:
                            properties[prop_name] = [f'{{{{{prop_name}_item}}}}']
                else:
                    properties[prop_name] = []
            elif prop_type == 'object':
                if 'properties' in prop_schema:
                    properties[prop_name] = self.schema_to_dict_example(prop_schema)
                else:
                    properties[prop_name] = {}
        
        return json.dumps(properties, ensure_ascii=False, separators=(',', ':'))
    
    def schema_to_dict_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """将 schema 转换为字典示例"""
        if 'properties' not in schema:
            return {}
        
        properties = {}
        for prop_name, prop_schema in schema['properties'].items():
            prop_type = self.convert_type(prop_schema)
            
            if prop_type == 'string':
                properties[prop_name] = f'{{{{{prop_name}}}}}'
            elif prop_type in ['integer', 'number']:
                properties[prop_name] = f'{{{{{prop_name}}}}}'
            elif prop_type == 'boolean':
                properties[prop_name] = True
            elif prop_type == 'array':
                properties[prop_name] = []
            elif prop_type == 'object':
                properties[prop_name] = {}
        
        return properties
    
    def extract_body_params(self, request_body: Dict) -> List[Dict[str, Any]]:
        """提取请求体参数"""
        if 'content' not in request_body:
            return []
        
        content = request_body['content']
        if 'application/json' not in content:
            return []
        
        schema = content['application/json'].get('schema', {})
        
        if '$ref' in schema:
            ref_schema = self.resolve_schema_ref(schema['$ref'])
            return self.extract_schema_properties(ref_schema)
        
        return self.extract_schema_properties(schema)
    
    def extract_schema_properties(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取 schema 属性"""
        properties = []
        required_fields = schema.get('required', [])
        
        if 'properties' not in schema:
            return properties
        
        for prop_name, prop_schema in schema['properties'].items():
            if '$ref' in prop_schema:
                ref_schema = self.resolve_schema_ref(prop_schema['$ref'])
                prop_type = self.convert_type(ref_schema)
            else:
                prop_type = self.convert_type(prop_schema)
            
            property_info = {
                'name': prop_name,
                'type': prop_type,
                'description': prop_schema.get('description', ''),
                'required': prop_name in required_fields
            }
            
            properties.append(property_info)
        
        return properties
    
    def extract_response_data(self, responses: Dict) -> Dict[str, Any]:
        """提取响应数据结构"""
        if '200' not in responses:
            return {}
        
        response = responses['200']
        if 'content' not in response:
            return {}
        
        content = response['content']
        if 'application/json' not in content:
            return {}
        
        schema = content['application/json'].get('schema', {})
        
        if '$ref' in schema:
            ref_schema = self.resolve_schema_ref(schema['$ref'])
            return self.parse_response_schema(ref_schema)
        
        return self.parse_response_schema(schema)
    
    def parse_response_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """解析响应 schema"""
        if 'allOf' in schema:
            # 处理 allOf 组合 - 寻找数据字段
            for sub_schema in schema['allOf']:
                if '$ref' in sub_schema:
                    continue  # 跳过 BasicResponse 引用
                else:
                    # 找到包含 data 字段的 schema
                    if 'properties' in sub_schema and 'data' in sub_schema['properties']:
                        data_field = sub_schema['properties']['data']
                        if '$ref' in data_field:
                            data_schema = self.resolve_schema_ref(data_field['$ref'])
                            return self.convert_data_schema(data_schema)
            return {}
        
        return self.convert_data_schema(schema)
    
    def convert_data_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """转换数据 schema"""
        if 'properties' not in schema:
            return {}
        
        result = {}
        for prop_name, prop_schema in schema['properties'].items():
            if '$ref' in prop_schema:
                ref_schema = self.resolve_schema_ref(prop_schema['$ref'])
                result[prop_name] = self.format_property_value(ref_schema, prop_schema.get('description', ''))
            else:
                result[prop_name] = self.format_property_value(prop_schema, prop_schema.get('description', ''))
        
        return result
    
    def format_property_value(self, schema: Dict[str, Any], description: str = "") -> Any:
        """格式化属性值"""
        prop_type = self.convert_type(schema)
        
        if prop_type == 'array' and 'items' in schema:
            items_schema = schema['items']
            if '$ref' in items_schema:
                ref_schema = self.resolve_schema_ref(items_schema['$ref'])
                if 'properties' in ref_schema:
                    return {
                        'type': 'array',
                        'description': description,
                        'items': {
                            'type': 'object',
                            'properties': self.convert_data_schema(ref_schema)
                        }
                    }
            return {
                'type': 'array',
                'description': description,
                'items': {
                    'type': self.convert_type(items_schema)
                }
            }
        elif prop_type == 'object' and 'properties' in schema:
            return {
                'type': 'object',
                'description': description,
                'properties': self.convert_data_schema(schema)
            }
        else:
            return f'"{prop_type}"'
    
    def convert_api(self, path: str, method: str, api_info: Dict) -> Dict[str, Any]:
        """转换单个 API"""
        api_name = self.generate_api_name(path, method)
        
        # 提取参数
        parameters = api_info.get('parameters', [])
        
        # 提取所有标准 header 参数（补全完整的header列表）
        standard_headers = [
            {'name': 'X-App-version', 'description': '应用版本号', 'required': False},
            {'name': 'X-Os-version', 'description': '操作系统版本', 'required': False},
            {'name': 'X-Country', 'description': '国家代码', 'required': False},
            {'name': 'X-Language', 'description': '语言代码', 'required': False},
            {'name': 'X-Timezone', 'description': '时区', 'required': False},
            {'name': 'X-Os', 'description': '操作系统', 'required': False},
            {'name': 'X-Client-Timestamp', 'description': '客户端时间戳', 'required': False},
            {'name': 'X-Phone-Model', 'description': '手机型号', 'required': False},
            {'name': 'User-Agent', 'description': '用户代理', 'required': False},
            {'name': 'X-Auth-Token', 'description': '用户认证token', 'required': False},
            {'name': 'X-Open-Udid', 'description': '设备唯一标识', 'required': True}
        ]
        
        header_params = []
        
        # 处理每个标准header
        for std_header in standard_headers:
            # 先查找是否在OpenAPI中定义了这个header
            found_param = None
            for param in parameters:
                if param['in'] == 'header' and param['name'] == std_header['name']:
                    found_param = param
                    break
            
            # 如果找到了OpenAPI定义，使用它；否则使用标准定义
            if found_param:
                header_params.append({
                    'name': found_param['name'],
                    'type': self.convert_type(found_param.get('schema', {})),
                    'description': found_param.get('description', std_header['description']),
                    'required': found_param.get('required', std_header['required'])
                })
            else:
                header_params.append({
                    'name': std_header['name'],
                    'type': 'string',
                    'description': std_header['description'],
                    'required': std_header['required']
                })
        
        # 提取请求体参数
        request_body = api_info.get('requestBody', {})
        body_params = []
        if request_body:
            body_params = self.extract_body_params(request_body)
        
        # 生成 curl 命令
        curl_command = self.generate_curl_command(path, method, parameters, request_body)
        
        # 提取响应数据
        response_data = self.extract_response_data(api_info.get('responses', {}))
        
        # 构建 API 配置
        api_config = {
            'name': api_info.get('summary', f'{api_name}接口'),
            'curl': curl_command,
            'endpoint': path,
            'method': method.upper(),
            'params': {
                'content_type': 'application/json',
                'query': [],
                'header': header_params,
                'body': body_params
            },
            'expected_response': {
                'success': {
                    'code': 0,
                    'msg': '',
                    'data': response_data
                }
            }
        }
        
        return api_config
    
    def save_api_file(self, api_name: str, api_config: Dict[str, Any]):
        """保存 API 文件，格式与 login_by_email.yaml 完全一致"""
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 生成文件路径
        filename = f"{api_name}.yaml"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 写入注释
                f.write(f"# API配置文件 - {api_config['name']}\n\n")
                
                # 写入版本
                f.write('version: "0.0.1"\n\n')
                
                # 写入 apis
                f.write('apis:\n')
                f.write(f'  {api_name}:\n')
                f.write(f'    name: "{api_config["name"]}"\n')
                
                # 写入 curl（使用 | 块标量）
                f.write('    curl: |\n')
                curl_lines = api_config['curl'].split('\n')
                for line in curl_lines:
                    f.write(f'      {line}\n')
                
                # 写入基本信息
                f.write(f'    endpoint: "{api_config["endpoint"]}"\n')
                f.write(f'    method: {api_config["method"]}\n')
                
                # 写入 params
                f.write('    params: \n')
                f.write(f'      content_type: "{api_config["params"]["content_type"]}"\n')
                f.write('      query:\n')
                f.write('      header:\n')
                
                # 写入 header 参数
                for header in api_config['params']['header']:
                    f.write(f'        - name: "{header["name"]}"\n')
                    f.write(f'          type: "{header["type"]}"\n')
                    f.write(f'          description: "{header["description"]}"\n')
                    f.write(f'          required: {str(header["required"]).lower()}\n')
                
                # 写入 body 参数
                f.write('      body:\n')
                for body_param in api_config['params']['body']:
                    f.write(f'        - name: "{body_param["name"]}"\n')
                    f.write(f'          type: "{body_param["type"]}"\n')
                    f.write(f'          description: "{body_param["description"]}"\n')
                    f.write(f'          required: {str(body_param["required"]).lower()}\n')
                
                # 写入 expected_response
                f.write('    expected_response:\n')
                f.write('      success:\n')
                f.write('        code: 0\n')
                f.write('        msg: ""\n')
                f.write('        data:\n')
                
                # 写入响应数据
                self.write_data_structure(f, api_config['expected_response']['success']['data'], 10)
                
            print(f"✅ 已生成 API 文件: {filepath}")
        except Exception as e:
            print(f"❌ 保存文件失败 {filepath}: {e}")
    
    def write_data_structure(self, f, data, indent_level):
        """写入数据结构，保持格式与 login_by_email.yaml 一致"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and 'type' in value:
                    # 处理复杂类型
                    if value['type'] == 'array':
                        f.write(' ' * indent_level + f'{key}:\n')
                        f.write(' ' * (indent_level + 2) + 'type: "array"\n')
                        if value.get('description'):
                            f.write(' ' * (indent_level + 2) + f'description: "{value["description"]}"\n')
                        if 'items' in value:
                            f.write(' ' * (indent_level + 2) + 'items:\n')
                            if isinstance(value['items'], dict) and value['items'].get('type') == 'object':
                                f.write(' ' * (indent_level + 4) + 'type: "object"\n')
                                if 'properties' in value['items']:
                                    f.write(' ' * (indent_level + 4) + 'properties:\n')
                                    self.write_data_structure(f, value['items']['properties'], indent_level + 6)
                            else:
                                self.write_data_structure(f, value['items'], indent_level + 4)
                    elif value['type'] == 'object':
                        f.write(' ' * indent_level + f'{key}:\n')
                        f.write(' ' * (indent_level + 2) + 'type: "object"\n')
                        if value.get('description'):
                            f.write(' ' * (indent_level + 2) + f'description: "{value["description"]}"\n')
                        if 'properties' in value:
                            f.write(' ' * (indent_level + 2) + 'properties:\n')
                            self.write_data_structure(f, value['properties'], indent_level + 4)
                    else:
                        # 简单类型
                        f.write(' ' * indent_level + f'{key}:\n')
                        f.write(' ' * (indent_level + 2) + f'type: "{value["type"]}"\n')
                        if value.get('description'):
                            f.write(' ' * (indent_level + 2) + f'description: "{value["description"]}"\n')
                elif isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                    # 处理简单类型字符串 (如 "string", "integer")
                    f.write(' ' * indent_level + f'{key}: {value}\n')
                else:
                    # 其他值类型
                    f.write(' ' * indent_level + f'{key}: "{value}"\n')
    
    def convert_all_apis(self):
        """转换所有 API"""
        if not self.openapi_data or 'paths' not in self.openapi_data:
            print("❌ OpenAPI 数据中没有找到 paths")
            return {}
        
        paths = self.openapi_data['paths']
        converted_apis = {}
        
        for path, path_info in paths.items():
            for method, method_info in path_info.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    api_name = self.generate_api_name(path, method)
                    api_config = self.convert_api(path, method, method_info)
                    converted_apis[api_name] = api_config
        
        return converted_apis
    
    def convert_and_save(self):
        """转换并保存所有 API 文件"""
        print("🚀 开始转换 OpenAPI 文件...")
        
        # 加载 OpenAPI 文件
        self.load_openapi_file()
        
        # 转换所有 API
        converted_apis = self.convert_all_apis()
        
        if not converted_apis:
            print("❌ 没有找到可转换的 API")
            return
        
        print(f"📝 找到 {len(converted_apis)} 个 API，开始生成文件...")
        
        # 保存每个 API 文件
        for api_name, api_config in converted_apis.items():
            self.save_api_file(api_name, api_config)
        
        print(f"🎉 转换完成！共生成 {len(converted_apis)} 个 API 文件")
