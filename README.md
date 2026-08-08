# 🤖 DesktopAgent 桌面智能助手

一个基于 **Python + tkinter** 的桌面 Agent（`v0.3.0`），已接入 **Ollama 本地大模型**，支持智能聊天、多轮对话记忆、自主调用本机命令与文件管理。若 Ollama 未启动，会自动回退到内置规则聊天，**程序不会崩溃**。

---

## 📌 快速导航

- [✨ 功能特性](#-功能特性)
- [🏗️ 软件架构](#️-软件架构)
- [🔗 数据流转调用链](#-数据流转调用链)
- [📄 函数接口注释](#-函数接口注释)
- [🛠️ 工具指令](#️-工具指令)
- [⚙️ 配置说明](#️-配置说明)
- [🚀 快速开始](#-快速开始)
- [📦 打包说明](#-打包说明)
- [🔒 安全说明](#-安全说明)

---

## ✨ 功能特性

- 🧠 **智能聊天**：接入本地 Ollama 大模型（默认 `qwen2.5:0.5b`，体积小、内存要求低）
- 💬 **多轮记忆**：自动携带最近对话上下文（默认 8 条），连续对话更连贯
- 📄 **读取文件**：支持 txt / docx / xlsx / pdf 多种格式的智能解析
- 🖱️ **鼠标拖拽文件**：直接把文件拖进窗口，即可读取/总结
- ⚠️ **生成总结（实验性）**：依赖 Ollama 大模型，默认 `qwen2.5:0.5b` 小模型总结质量有限，**建议换更大的模型**（如 `qwen2.5:7b`）才能获得可用总结
- 🔧 **工具调用**：大模型可自主输出 `/` 指令并自动执行本机操作
- 💻 **执行命令**：`/shell 命令`，10 秒超时保护
- 📁 **文件操作**：`/ls`、`/cat`、`/open`、`/mkdir`
- 🖥️ **系统信息**：`/sysinfo` 查看 CPU / 内存 / 磁盘
- 🏠 **桌面窗口**：多行聊天 + 输入框，回车快捷发送；调模型时界面不卡死（后台线程 + "思考中…"占位）
- 🛡️ **规则兜底**：Ollama 未启动/出错时自动回退到内置规则回复
- 🔢 **版本查询**：`/version` 查看应用版本

---

## 🏗️ 软件架构

本项目采用**分层架构**，上层依赖下层，职责清晰、便于维护与扩展。

```
┌─────────────────────────────────────────────────────────────┐
│                    GUI 层        agent/ui.py                │
│         ChatWindow：tkinter 聊天窗口、事件与线程调度          │
└─────────────────────────────────────────────────────────────┘
                            │ 调用
┌─────────────────────────────────────────────────────────────┐
│                    核心层        agent/core.py              │
│     Agent：对话入口 / 分发器 / 大模型调用 / 工具路由 / 兜底    │
└─────────────────────────────────────────────────────────────┘
                            │            │
             ┌──────────────┘            └──────────────┐
             ▼                                          ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│     工具层  agent/tools.py│    │   配置层   agent/config.py│
│ 本机操作（命令/文件/系统） │    │ Ollama 连接 / 模型参数    │
└──────────────────────────┘    └──────────────────────────┘
```

### 各层职责说明

| 层 | 文件 | 核心类/函数 | 职责 |
|----|------|-------------|------|
| **GUI 层** | `agent/ui.py` | `ChatWindow` | 界面构建、消息回显、输入事件、后台线程调度 |
| **核心层** | `agent/core.py` | `Agent` | 对话分发、大模型调用、工具路由、规则兜底、记忆管理 |
| **工具层** | `agent/tools.py` | 多个工具函数 | 执行命令、读写文件、打开路径、创建目录、系统信息 |
| **配置层** | `agent/config.py` | 模块常量 | Ollama 地址、模型名、采样参数、系统提示词 |
| **入口** | `main.py` | `main()` | 组装 Agent + ChatWindow 并启动 |

**依赖方向**：`main.py → ui.py → core.py → tools.py / config.py`（单向、无循环依赖）。

---

## 🔗 数据流转调用链

以一条普通聊天消息（如"帮我列一下当前目录"）为例：

```
用户输入
  │
  ▼
ChatWindow.on_send()                 ui.py     捕获输入，启动后台线程
  │
  ▼
ChatWindow._process()                ui.py     线程中调用 Agent
  │
  ▼
Agent.handle(text)                   core.py   ① 记录历史 → ② 分发
  │
  ▼
Agent._dispatch(text)                core.py   判断是否 `/` 工具指令
  │                                ┌─────────── 是 → _handle_tool() 直接执行本机操作
  ▼                                └─────────── 否 → _chat_with_llm()
Agent._chat_with_llm(text)           core.py   调大模型，失败则回退 _chat()
  │
  ▼
Agent._query_ollama(text) ★          core.py   ★ 连接大模型的核心接口
  │                                            构造 messages → POST /api/chat
  ▼
Ollama 服务 (http://localhost:11434/api/chat)    返回模型回复文本
  │
  ▼
返回回复 → _chat_with_llm()           core.py   若回复含 `/指令` → 自动执行
  │
  ▼
ChatWindow._show_reply()             ui.py     （回到主线程）更新界面
```

### 工具指令数据流（直接输入 `/ls`）

```
/指令 → _dispatch() → _handle_tool() → 从 tool_map 取对应函数 → 结果返回
```

---

## 📄 函数接口注释

### `agent/core.py` — Agent 核心类

| 方法 | 签名 | 说明 |
|------|------|------|
| `handle` | `handle(user_input: str) -> str` | **主入口**：接收用户输入，返回 Agent 回复；负责记录历史与裁剪记忆 |
| `_dispatch` | `_dispatch(text: str) -> str` | **分发器**：判断是 `/` 工具指令（本地处理）还是正常聊天（走大模型） |
| `_chat_with_llm` | `_chat_with_llm(text: str) -> str` | 聊天处理：调用大模型，若回复含 `/` 指令则自动执行；失败回退规则聊天 |
| `_query_ollama` ★ | `_query_ollama(user_text: str) -> str` | **连接大模型的核心接口**：调用 Ollama `/api/chat`，返回回复文本 |
| `_handle_tool` | `_handle_tool(text: str) -> str` | 工具指令路由：解析指令名与参数，从 `tool_map` 分发到具体函数 |
| `_need_arg` | `_need_arg(arg: str, msg: str) -> str` | 参数校验：空的参数抛 `ToolError` |
| `_extract_tool` | `_extract_tool(reply: str) -> str` | 从模型回复中提取 `/` 指令行（正则匹配） |
| `_chat` | `_chat(text: str) -> str` | **规则兜底聊天**：Ollama 不可用时，用内置规则回答问候/时间等 |
| `_help` | `_help() -> str` | 生成帮助文本 |

#### ★ 连接大模型的核心接口 `_query_ollama` 详解

```python
def _query_ollama(self, user_text: str) -> str:
    """调用 Ollama /api/chat，返回模型回复文本。"""
    # 1. 构造消息列表：系统提示 + 最近历史 + 当前输入
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    for msg in self.history[-config.HISTORY_LIMIT:]:
        messages.append(msg)

    # 2. 组装请求体
    payload = {
        "model": config.MODEL,              # 模型名 qwen2.5:0.5b
        "messages": messages,               # OpenAI 兼容的对话格式
        "stream": False,                    # 非流式，一次返回
        "options": {                        # 采样参数
            "temperature": config.TEMPERATURE,
            "num_predict": config.MAX_TOKENS,
        },
    }

    # 3. 发 HTTP POST 到 Ollama（标准库 urllib，零第三方依赖）
    req = urllib.request.Request(
        f"{config.OLLAMA_HOST}/api/chat",   # http://localhost:11434/api/chat
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=config.OLLAMA_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # 4. 从响应中取模型文本
    content = data.get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError("模型返回为空")
    return content
```

> 📡 **连接方式**：通过标准库 `urllib.request` 向本机 Ollama 服务发送 HTTP POST 请求到 `/api/chat` 端点，以 OpenAI 兼容的 `messages` 格式传递对话，并从响应 `data["message"]["content"]` 中取回复文本。**无需任何第三方 SDK**，依赖极简。

---

### `agent/tools.py` — 工具层

| 函数 | 签名 | 说明 |
|------|------|------|
| `run_command` | `run_command(cmd: str, timeout: int = 10) -> str` | 执行 shell 命令（默认 10 秒超时），返回输出 |
| `list_dir` | `list_dir(path: str = ".") -> str` | 列出目录内容，目录后加 `/` 标记 |
| `read_file` | `read_file(path: str, max_bytes: int = 200_000) -> str` | 读取文本文件，超 200KB 拒绝（防刷屏） |
| `open_path` | `open_path(path: str = ".") -> str` | 用系统默认程序打开路径（跨平台） |
| `make_dir` | `make_dir(path: str) -> str` | 创建目录（含父目录） |
| `get_sysinfo` | `get_sysinfo() -> str` | 获取系统信息（CPU/内存/磁盘/开机时间） |
| `sys_platform_is_mac` | `sys_platform_is_mac() -> bool` | 判断是否 macOS |
| `sys_platform_is_win` | `sys_platform_is_win() -> bool` | 判断是否 Windows |

> 所有工具函数在出错时统一抛 `ToolError` 异常，由核心层捕获并显示 `❌` 前缀提示。

---

### `agent/ui.py` — GUI 层

| 方法 | 签名 | 说明 |
|------|------|------|
| `__init__` | `__init__(self, agent: Agent)` | 创建窗口、构建组件、显示欢迎横幅 |
| `_build_widgets` | `_build_widgets() -> None` | 构建聊天区、滚动条、输入框、发送按钮 |
| `_show_banner` | `_show_banner() -> None` | 显示欢迎横幅（含版本号） |
| `_append` | `_append(who, text, font_tag="") -> None` | 追加一条消息到聊天区（带样式 tag） |
| `on_send` | `on_send() -> None` | 发送事件：回显用户输入、显示"思考中…"、启动后台线程 |
| `_process` | `_process(text: str) -> None` | **后台线程**执行 `Agent.handle`，完成后切回主线程更新 UI |
| `_show_reply` | `_show_reply(reply: str) -> None` | 删除"思考中…"占位，替换为真实回复 |
| `run` | `run() -> None` | 启动 tkinter 主事件循环 |

> ⚡ **线程模型**：调用大模型是阻塞操作，放在 `threading.Thread` 中执行避免界面卡死；tkinter 只能在主线程更新，因此用 `root.after(0, ...)` 切回主线程刷新界面。

---

### `main.py` — 程序入口

```python
def main() -> None:
    agent = Agent(name="小助手")   # 创建核心 Agent
    app = ChatWindow(agent)       # 将 Agent 注入 GUI
    app.run()                     # 启动界面
```

---

## 🛠️ 工具指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/help` | — | 显示帮助 |
| `/ls` | `[路径]` | 列出目录内容（默认当前目录） |
| `/cat` | `文件名` | 读取纯文本文件（限制 200KB） |
| `/read` | `文件` | 读取文件内容（支持 txt/docx/xlsx/pdf） |
| `/summarize` | `文件` | 读取文件内容并生成中文总结（实验性，需较大模型） |
| `/open` | `[路径]` | 用系统默认程序打开 |
| `/mkdir` | `路径` | 创建目录（含父目录） |
| `/shell` | `命令` | 执行 shell 命令（10 秒超时） |
| `/sysinfo` | — | 查看系统信息（CPU/内存/磁盘/开机时间） |
| `/echo` | `文本` | 原样回显 |
| `/version` | — | 查看版本信息 |

---

## ⚙️ 配置说明（`agent/config.py`）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama 服务地址 |
| `MODEL` | `qwen2.5:0.5b` | 使用的本地模型 |
| `TEMPERATURE` | `0.7` | 采样温度（越高越随机） |
| `MAX_TOKENS` | `512` | 单次回复最大 token |
| `HISTORY_LIMIT` | `8` | 传给模型的最近消息条数 |
| `OLLAMA_TIMEOUT` | `60` | 调用大模型超时（秒） |
| `SYSTEM_PROMPT` | — | 系统提示词（定义角色 + 引导工具调用） |

> 💡 内存充足（≥8GB）可把 `MODEL` 改为更大的模型（如 `qwen2.5:7b`）换取更好效果。

---

## 🚀 快速开始

### 1. 安装 Ollama 并拉取模型
```bash
# macOS 用 Homebrew 安装
brew install ollama

# 启动 Ollama 服务（首次会自动后台运行）
ollama serve

# 拉取最小模型（约 0.4GB）
ollama pull qwen2.5:0.5b

# 可选：确认模型就绪
ollama list
```

### 2. 创建并激活虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt    # 主要依赖 psutil（可选，./shell 用）
```

### 4. 运行
```bash
python main.py
```

### 使用示例

| 输入 | 效果 |
|------|------|
| `你好` | 大模型打招呼 |
| `帮我列一下当前目录` | 大模型回复并可能输出 `/ls` 自动执行 |
| `现在几点了` | 大模型回答（或规则兜底报时间） |
| `/ls` | 手动列出当前目录 |
| `/cat 文件名` | 读取文本文件 |
| `/read 文件.docx` | 读取 Word/Excel/PDF 等文件内容 |
| `/summarize 文件.xlsx` | 读取文件并生成总结（实验性） |
| 把文件拖进窗口 | 自动读取并总结该文件 |
| `/shell pwd` | 执行 shell 命令 |
| `/sysinfo` | 查看系统信息 |
| `/version` | 查看版本 |
| `/help` | 查看所有指令 |

---

## 📦 打包说明

使用 **PyInstaller** 打包成独立 macOS App（`DesktopAgent.spec` / `DesktopAgentDebug.spec`）。

### 打包步骤
```bash
# 安装打包依赖
pip install pyinstaller

# Release 版（隐藏控制台）
pyinstaller DesktopAgent.spec

# Debug 版（保留控制台查看日志）
pyinstaller DesktopAgentDebug.spec
```

### 生产物
- `dist/DesktopAgent.app` — Release 正式版
- `dist-debug/DesktopAgentDebug.app` — Debug 调试版

> ⚠️ **注意**：打包后的 App 是**完整独立应用**（已内置 Python / tkinter / psutil），但**大模型能力依赖本机 Ollama 服务**——App 只是 Ollama 的 HTTP 客户端，模型与 Ollama 服务不随 App 打包。目标机器需先安装并启动 Ollama、拉取模型。

### macOS 首次打开提示
未做 Apple 公证时，Gatekeeper 可能提示"无法验证开发者"。解决方法：
- **右键**点击 `.app` → **打开**；或
- 终端执行：`xattr -d com.apple.quarantine /路径/DesktopAgent.app`

---

## 🔒 安全说明

- `/shell` 会在你的**账户权限**下执行命令，**请勿输入破坏性命令**。
- 命令带 **10 秒超时**保护，避免卡死。
- 大模型调用带 **60 秒超时**，Ollama 未启动时自动降级，不影响使用。

---

## 📈 项目结构

```
Agent/
├── main.py                  # 程序入口
├── requirements.txt         # 依赖（psutil、pyinstaller）
├── README.md                # 本文档
├── DesktopAgent.spec        # Release 打包配置
├── DesktopAgentDebug.spec   # Debug 打包配置
└── agent/
    ├── __init__.py          # 包定义（__version__ = "0.3.0"）
    ├── config.py            # 配置中心（Ollama 地址、模型名等）
    ├── core.py              # 核心层（对话分发、大模型、工具路由、兜底）
    ├── tools.py             # 工具层（命令、文件、系统信息）
    └── ui.py                # GUI 层（tkinter 聊天窗口）
```

