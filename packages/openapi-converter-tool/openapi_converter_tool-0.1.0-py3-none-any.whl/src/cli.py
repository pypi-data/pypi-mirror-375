#!/usr/bin/env python3
"""
OpenAPI Converter CLI - 命令行界面
"""

import argparse
import sys
import os
from typing import Optional

from .converter import OpenAPIConverter
from .config import ConfigManager
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='converter',
        description='OpenAPI 3.0.1 到项目 API 格式转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  converter convert openapi.yaml                    # 转换到默认目录
  converter convert openapi.yaml -o api/explore     # 转换到指定目录
  converter --version                               # 显示版本信息
  converter --help                                  # 显示帮助信息
        """
    )
    
    # 添加全局选项
    parser.add_argument('-v', '--version', action='version', version=f'converter {__version__}')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='转换 OpenAPI 文件')
    convert_parser.add_argument('input_file', help='输入的 OpenAPI YAML 文件路径')
    convert_parser.add_argument('-o', '--output', default='api', help='输出目录 (默认: api)')
    convert_parser.add_argument('-c', '--config', help='配置文件路径')
    convert_parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='配置操作')
    
    # config init 子命令
    config_init_parser = config_subparsers.add_parser('init', help='创建示例配置文件')
    config_init_parser.add_argument('-o', '--output', default='openapi-converter-config.yaml', 
                                   help='输出配置文件路径')
    
    # config show 子命令
    config_show_parser = config_subparsers.add_parser('show', help='显示当前配置')
    config_show_parser.add_argument('-c', '--config', help='配置文件路径')
    
    return parser


def handle_convert_command(args) -> int:
    """处理 convert 命令"""
    input_file = args.input_file
    output_dir = args.output
    config_file = args.config
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return 1
    
    # 检查输入文件是否为 YAML 文件
    if not input_file.lower().endswith(('.yaml', '.yml')):
        print(f"⚠️ 警告: 输入文件可能不是 YAML 格式: {input_file}")
    
    try:
        # 加载配置
        config_manager = ConfigManager(config_file)
        template_config = config_manager.config
        
        # 创建转换器并执行转换
        converter = OpenAPIConverter(input_file, output_dir, template_config)
        converter.convert_and_save()
        return 0
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def handle_config_command(args) -> int:
    """处理 config 命令"""
    if args.config_action == 'init':
        return handle_config_init(args)
    elif args.config_action == 'show':
        return handle_config_show(args)
    else:
        print("❌ 请指定配置操作: init 或 show")
        return 1


def handle_config_init(args) -> int:
    """处理 config init 命令"""
    try:
        config_manager = ConfigManager()
        config_manager.create_sample_config(args.output)
        return 0
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return 1


def handle_config_show(args) -> int:
    """处理 config show 命令"""
    try:
        config_manager = ConfigManager(args.config)
        import yaml
        print("当前配置:")
        print(yaml.dump(config_manager.config, default_flow_style=False, allow_unicode=True, indent=2))
        return 0
    except Exception as e:
        print(f"❌ 显示配置失败: {e}")
        return 1


def main() -> int:
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'convert':
            return handle_convert_command(args)
        elif args.command == 'config':
            return handle_config_command(args)
        else:
            print(f"❌ 未知命令: {args.command}")
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
        return 130
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
