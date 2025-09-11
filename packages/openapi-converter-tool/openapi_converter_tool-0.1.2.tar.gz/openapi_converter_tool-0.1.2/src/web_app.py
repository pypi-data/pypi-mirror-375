#!/usr/bin/env python3
"""
OpenAPI Converter Web 应用
提供可视化的转换界面
"""

import os
import tempfile
import zipfile
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import yaml
from .converter import OpenAPIConverter
from .config import ConfigManager

# 获取模板目录路径
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'openapi-converter-secret-key'

# 配置上传
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'yaml', 'yml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """上传 OpenAPI 文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # 验证 YAML 文件
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': '文件上传成功'
            })
        except yaml.YAMLError as e:
            os.remove(filepath)
            return jsonify({'error': f'YAML 文件格式错误: {str(e)}'}), 400
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'文件处理失败: {str(e)}'}), 400
    
    return jsonify({'error': '不支持的文件格式'}), 400


@app.route('/convert', methods=['POST'])
def convert_api():
    """转换 OpenAPI 文件"""
    data = request.get_json()
    filename = data.get('filename')
    config_data = data.get('config', {})
    
    if not filename:
        return jsonify({'error': '缺少文件名'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 400
    
    try:
        # 创建临时输出目录
        output_dir = tempfile.mkdtemp()
        
        # 创建配置管理器
        config_manager = ConfigManager()
        config_manager.config.update(config_data)
        
        # 执行转换
        converter = OpenAPIConverter(filepath, output_dir, config_manager.config)
        converter.convert_and_save()
        
        # 创建 ZIP 文件
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}_converted.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{os.path.basename(zip_path)}',
            'message': '转换完成'
        })
        
    except Exception as e:
        return jsonify({'error': f'转换失败: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """下载转换结果"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': '文件不存在'}), 404


@app.route('/config/template')
def get_config_template():
    """获取配置模板"""
    config_manager = ConfigManager()
    return jsonify(config_manager.get_default_config())


@app.route('/preview', methods=['POST'])
def preview_conversion():
    """预览转换结果"""
    data = request.get_json()
    filename = data.get('filename')
    config_data = data.get('config', {})
    
    if not filename:
        return jsonify({'error': '缺少文件名'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 400
    
    try:
        # 创建配置管理器
        config_manager = ConfigManager()
        config_manager.config.update(config_data)
        
        # 创建转换器
        converter = OpenAPIConverter(filepath, '/tmp', config_manager.config)
        converter.load_openapi_file()
        
        # 获取转换预览
        converted_apis = converter.convert_all_apis()
        
        # 只返回前几个 API 的预览
        preview_apis = {}
        count = 0
        for api_name, api_config in converted_apis.items():
            if count >= 3:  # 只预览前3个
                break
            preview_apis[api_name] = {
                'name': api_config['name'],
                'endpoint': api_config['endpoint'],
                'method': api_config['method'],
                'curl_preview': api_config['curl'][:200] + '...' if len(api_config['curl']) > 200 else api_config['curl']
            }
            count += 1
        
        return jsonify({
            'success': True,
            'total_apis': len(converted_apis),
            'preview_apis': preview_apis
        })
        
    except Exception as e:
        return jsonify({'error': f'预览失败: {str(e)}'}), 500


def create_app():
    """创建 Flask 应用"""
    return app


def main():
    """命令行入口点"""
    import sys
    import argparse
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='Converter Web 应用')
    parser.add_argument('port', nargs='?', type=int, default=5000,
                       help='端口号 (默认: 5000)')
    
    # 解析参数
    args = parser.parse_args()
    
    port = args.port
    
    print(f"🚀 启动 Converter Web 应用...")
    print(f"📱 访问地址: http://localhost:{port}")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
