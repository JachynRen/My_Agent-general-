# 🚀 DesktopAgent v0.4.0 版本发布说明

> **菜单栏升级：模型选择、作者信息、帮助文档**

---

## ✨ 版本亮点

本版本在 v0.3.0 大模型接入的基础上，**进一步完善用户体验**：
- 📋 新增顶部**菜单栏**（模型切换、帮助、关于）
- 🤖 支持从菜单栏**快速切换 Ollama 模型**，无需重启应用
- ℹ️ 新增**关于对话框**，展示版本、作者、联系方式
- 🪟 新增 **Windows 平台打包支持**（onedir / onefile / debug）

---

## 🆕 本次更新详解

### 📋 菜单栏功能
- **🤖 模型菜单**：
  - 自动加载本机 Ollama 可用模型列表
  - 支持一键切换模型，实时生效
  - 刷新模型列表（检测新下载的模型）
  - Ollama 未启动时显示提示
  
- **❓ 帮助菜单**：
  - "查看帮助"：在聊天区输出所有可用工具指令
  - "关于"：弹窗展示版本、作者、邮箱、技术栈

### 🪟 Windows 平台支持
- 新增 3 套 Windows 打包配置：
  - `DesktopAgent_win_onedir.spec` — 文件夹分发模式
  - `DesktopAgent_win_onefile.spec` — 单文件 exe 模式
  - `DesktopAgent_win_debug.spec` — 带控制台的调试版
- 新增 `start.bat` 一键启动脚本

### 🛠️ 代码优化
- `agent/ui.py`：重构菜单栏构建逻辑，异步加载模型列表
- `agent/tools.py`：优化系统信息输出格式
- `agent/config.py`：支持动态模型切换

---

## 📦 安装包

| 文件 | 说明 |
|------|------|
| `DesktopAgent-macos-v0.4.0.zip` | **macOS 正式版**：隐藏控制台 |
| `DesktopAgentDebug-macos-v0.4.0.zip` | **macOS 调试版**：保留控制台 |
| `DesktopAgent-windows-v0.4.0.zip` | **Windows 正式版**：单文件 exe |
| `DesktopAgentDebug-windows-v0.4.0.zip` | **Windows 调试版** |

---

## ⚠️ 使用前提

打包后的应用是**独立完整应用**（已内置 Python/tkinter/psutil），但**大模型能力依赖本机 Ollama 服务**：

```bash
# macOS 安装 Ollama
brew install ollama
ollama serve
ollama pull qwen2.5:0.5b
```

> 💡 若未启动 Ollama，App **不会崩溃**，会自动回退到内置规则聊天。

### macOS 首次打开提示
未做 Apple 公证，Gatekeeper 可能提示"无法验证开发者"。解决方法：
- **右键**点击 `.app` → **打开**；或
- 终端执行：`xattr -d com.apple.quarantine /路径/DesktopAgent.app`

---

## 📈 版本历史

| 版本 | 说明 |
|------|------|
| **v0.4.0** | 📋 菜单栏、模型选择、作者信息、Windows 打包（本次） |
| v0.3.0 | 🎉 接入 Ollama 大模型，分层架构，规则兜底 |
| v0.2.0 | UI 优化（Label 按钮、暗色滚动条） |
| v0.1.0 | 规则式桌面 Agent Demo |

---

感谢使用！如有问题，请在 GitHub Issues 反馈。🙏
