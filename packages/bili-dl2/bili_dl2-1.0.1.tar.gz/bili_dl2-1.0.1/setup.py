from setuptools import setup, find_packages
import os

# 读取README文件
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="bili-dl2",
    version="1.0.1",
    author="B站视频下载器",
    author_email="",
    description="一个功能强大的B站视频下载工具，支持最高清晰度下载和自动合并",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WavesMan/bili-dl2load",
    packages=find_packages(include=['config', 'modules', 'utils', 'commands']),
    py_modules=['main'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bili-dl=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json.template"],
    },
    keywords="bilibili, video, download, b站, 视频下载",
    project_urls={
        "Bug Reports": "https://github.com/WavesMan/bili-dl2load/issues",
        "Source": "https://github.com/WavesMan/bili-dl2load",
    },
)
