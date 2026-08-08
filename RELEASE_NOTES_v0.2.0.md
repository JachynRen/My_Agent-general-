# v0.2.0 版本说明

## 🆕 本次更新
- **UI 全面优化**
  - 改用 `Label` 模拟发送按钮，解决 macOS 上原生按钮文字不显示的问题（黑色底 + 白色加粗文字 + 悬停变色）
  - 添加暗色主题滚动条（灰色滑块 + 暗色轨道），与整体深色界面协调

## ✨ 核心功能（桌面 Agent Demo）
- **智能聊天**：规则式回复，支持问候、自我介绍、报时间、感谢、告别等
- **本机命令执行**：`/shell 命令`，带 10 秒超时保护
- **文件管理**：
  - `/ls` 列出目录
  - `/cat` 读取文本文件
  - `/open` 用默认程序打开路径
  - `/mkdir` 创建目录
- **系统信息**：`/sysinfo` 查看 CPU、内存、磁盘占用、开机时间
- **辅助指令**：`/echo`、`/help`

## 🎨 技术栈
- Python 3.11 + tkinter（标准库）
- psutil（系统信息采集）
- 暗色主题桌面聊天窗口

## 🚀 运行
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

