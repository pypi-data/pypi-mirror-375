# B站视频下载器 (bili-dl2loader)

[![PyPI version](https://img.shields.io/pypi/v/bili-dl2.svg)](https://pypi.org/project/bili-dl2/)
[![Python versions](https://img.shields.io/pypi/pyversions/bili-dl2.svg)](https://pypi.org/project/bili-dl2/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个功能强大的B站视频下载工具，支持最高清晰度下载和自动合并。

## ✨ 功能特性

- 🎯 **智能清晰度选择**: 自动获取账号权限内的最高清晰度视频
- 🔐 **多种登录方式**: 支持二维码登录和Cookie登录
- 🔍 **Cookie状态检查**: 自动验证Cookie可用性，失效时提示重新登录
- 📦 **自动合并**: 支持DASH格式视频的自动音视频合并
- 🚀 **多线程下载**: 支持多线程并发下载，提高下载速度
- 📁 **智能文件管理**: 按BV号自动组织文件结构
- 📊 **元数据保存**: 自动保存视频信息和下载元数据
- ⚡ **断点续传**: 支持下载中断后继续下载
- 🏗️ **模块化架构**: 清晰的命令分离和职责划分

## 📦 安装

### 通过 pip 安装

```bash
pip install bili-dl2
```

### 从源码安装

```bash
git clone https://github.com/WavesMan/bili-dl2load.git
cd bili-dl2loader
pip install -e .
```

## 🚀 快速开始

### 基本使用

```bash
# 查看帮助信息
bili-dl --help

# 查看特定命令帮助
bili-dl download --help
bili-dl login --help
bili-dl status --help

# 下载单个视频（需要先登录）
bili-dl download BV1A6aRz4EBU

# 指定输出目录
bili-dl download BV1A6aRz4EBU --output ./my_videos

# 指定清晰度 (80=1080P, 112=1080P+, 120=4K)
bili-dl download BV1A6aRz4EBU --quality 112

# 禁用自动合并
bili-dl download BV1A6aRz4EBU --no-merge

# 登录B站账号
bili-dl login

# 检查登录状态
bili-dl status
```

### 配置说明

首次运行会自动在项目目录下的 `config/config.json` 创建配置文件。**重要安全提示：配置文件包含敏感登录信息，请勿将此文件提交到版本控制系统或分享给他人。**

配置文件模板 (`config/config.json.template`) 会在安装时提供，您需要：

1. 复制模板文件：
```bash
cp config/config.json.template config/config.json
```

2. 运行登录命令获取Cookie：
```bash
bili-dl login
```

配置文件结构：

```json
{
  "user": {
    "username": "",
    "password": "",
    "cookies": {
      "SESSDATA": "",
      "bili_jct": "",
      "DedeUserID": ""
    },
    "login_method": "qrcode"
  },
  "download": {
    "output_dir": "downloads",
    "quality": "auto",
    "format": "mp4",
    "threads": 4,
    "retry_times": 3,
    "timeout": 30
  },
  "ffmpeg": {
    "path": "auto",
    "auto_merge": true,
    "delete_temp_files": true
  },
  "network": {
    "proxy": "",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  },
  "debug": {
    "enable_logging": false,
    "log_level": "INFO",
    "save_response": false
  }
}
```

**安全警告：**
- `SESSDATA`、`bili_jct`、`DedeUserID` 是B站登录凭证，泄露可能导致账户被盗
- 配置文件已默认添加到 `.gitignore`，请勿手动取消忽略
- 建议定期检查并更新Cookie信息

## 🔧 高级用法

### 作为Python模块使用

```python
from bili_downloader.commands import handle_download_command, handle_login_command
from bili_downloader.services.login_manager import login_manager

# 初始化配置
from bili_downloader.config.config_manager import init_config
init_config()

# 登录
login_manager.init_login()

# 下载视频
success = handle_download_command("BV1A6aRz4EBU", output_dir="./videos")
if success:
    print("下载成功！")
```

### 批量下载

```python
from bili_downloader.commands import handle_download_command

video_list = [
    "BV1A6aRz4EBU",
    "BV1B6bRz5FCV", 
    "BV1C7cSx6GDW"
]

for bvid in video_list:
    handle_download_command(bvid)
```

## 📁 文件结构

下载完成后，文件会按以下结构组织：

```
downloads/
└── BV1A6aRz4EBU/
    ├── 视频标题_video.m4s      # 视频流文件
    ├── 视频标题_audio.m4s      # 音频流文件
    ├── 视频标题.mp4           # 最终合并的视频文件
    └── metadata.json          # 视频元数据信息
```

项目代码结构：

```
bili-dl2loader/
├── commands/                 # 命令处理模块
│   ├── download_command.py   # 下载命令处理
│   ├── login_command.py      # 登录命令处理
│   └── status_command.py     # 状态检查命令
├── modules/                  # 核心功能模块
│   ├── login_manager.py      # 登录管理
│   ├── video_info.py         # 视频信息获取
│   ├── stream_downloader.py  # 流下载器
│   └── ffmpeg_integration.py # FFmpeg集成
├── services/                 # 服务层
│   └── __init__.py
├── utils/                    # 工具函数
│   └── common_utils.py
├── config/                   # 配置管理
│   └── config_manager.py
└── main.py                   # 主入口点
```

## ⚙️ 依赖要求

- Python 3.7+
- requests >= 2.28.0
- qrcode >= 7.3.1
- Pillow >= 9.3.0
- ffmpeg (用于视频合并，可选但推荐)

## 🔍 常见问题

### Q: 如何安装 ffmpeg？

**Windows:**
1. 下载 ffmpeg: https://ffmpeg.org/download.html
2. 解压并添加 bin 目录到系统 PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

### Q: 登录失败怎么办？

使用 login 命令重新登录：
```bash
bili-dl login
```

### Q: Cookie失效怎么办？

程序会自动检测Cookie状态，如果失效会在下载时提示重新登录。

### Q: 下载速度慢怎么办？

可以尝试：
1. 检查网络连接
2. 使用更好的网络环境
3. 调整配置中的超时和重试参数

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本项目仅用于学习和研究目的，请勿用于商业用途。下载的视频请遵守相关法律法规和B站用户协议。
