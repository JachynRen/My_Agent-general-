# 🤖 桌面 Agent Demo

一个基于 **Python + tkinter** 的简单桌面 Agent 演示程序。当前为**规则式**版本（尚未接入大模型），支持聊天、执行本机命令和文件管理。

## ✨ 功能

- **聊天**：规则式回复（问候、自我介绍、报时间、帮助等）
- **执行命令**：`/shell 命令`，10 秒超时保护
- **文件操作**：`/ls`、`/cat`、`/open`、`/mkdir`
- **系统信息**：`/sysinfo` 查看 CPU / 内存 / 磁盘
- **桌面窗口**：多行聊天记录 + 输入框，回车快捷发送

## 📁 项目结构

```
Agent/
├── main.py            # 程序入口
├── requirements.txt   # 依赖（psutil）
└── agent/
    ├── __init__.py
    ├── core.py        # Agent 核心：意图识别 + 规则回复
    ├── tools.py       # 工具集：命令、文件、系统信息
    └── ui.py          # 桌面 GUI（tkinter 聊天窗口）
```

## 🚀 快速开始

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

## 💬 使用示例

| 输入 | 效果 |
|------|------|
| `你好` | 打招呼 |
| `现在几点了` | 报当前时间 |
| `/ls` | 列出当前目录 |
| `/cat 文件名` | 读取文本文件 |
| `/shell pwd` | 执行 shell 命令 |
| `/sysinfo` | 查看系统信息 |
| `/help` | 查看所有指令 |

## 📦 打包为可执行程序（PyInstaller）

将桌面应用打包成独立可执行程序，无需 Python 环境即可运行。

```bash
source .venv/bin/activate

# 安装 PyInstaller
pip install pyinstaller

# 打包（macOS 下会生成 .app 应用包）
pyinstaller --noconfirm --clean --windowed --name DesktopAgent main.py
```

产物位于 `dist/` 目录：
- `dist/DesktopAgent.app` — macOS 应用包（双击即可运行）
- `dist/DesktopAgent/` — 目录版可执行文件

> 提示：PyInstaller 打包只能在**当前操作系统**上运行，Windows 需在 Windows 上打包，macOS 需在 macOS 上打包。

## ⚠️ 安全说明

- `/shell` 会在你的账户权限下执行命令，**请勿输入破坏性命令**。
- 命令带 **10 秒超时**保护，避免卡死。
- 当前为演示版，建议仅在本机测试使用。
