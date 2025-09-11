#!/usr/bin/env python3
"""
OpenAPI Converter - 独立的 OpenAPI 转换工具
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    """读取文件内容"""
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

def read_requirements():
    """读取requirements.txt"""
    requirements = []
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    except FileNotFoundError:
        pass
    return requirements

setup(
    name="openapi-converter-tool",
    version="0.1.1",
    description="独立的 OpenAPI 3.0.1 到项目 API 格式转换工具",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="OpenAPI Converter Team",
    author_email="team@openapi-converter.dev",
    url="https://github.com/openapi-converter/openapi-converter",
    packages=['src'],
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'openapi-converter=src.cli:main',
            'openapi-converter-web=src.web_app:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="openapi swagger api conversion yaml",
    project_urls={
        "Bug Reports": "https://github.com/openapi-converter/openapi-converter/issues",
        "Source": "https://github.com/openapi-converter/openapi-converter",
        "Documentation": "https://openapi-converter.readthedocs.io",
    },
    package_data={
        'src': [
            '../templates/*',
            '../examples/*',
        ],
    },
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'isort',
            'flake8',
        ],
        'web': [
            'flask>=2.0.0',
            'werkzeug>=2.0.0',
        ],
    },
)
