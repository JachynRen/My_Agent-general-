# 🤖 桌面 Agent（Desktop Agent）

一个基于 **Python + tkinter** 的桌面 Agent Demo，已接入 **Ollama 本地大模型**，支持智能聊天、多轮对话记忆、自主调用本机命令和文件管理。若 Ollama 未启动，会自动回退到内置规则聊天，程序不会崩溃。

---

## ✨ 功能特性

- **智能聊天**：接入本地 Ollama 大模型（默认 `qwen2.5:0.5b`，最小编号、体积小、内存要求低）
- **多轮记忆**：自动携带最近 `HISTORY_LIMIT=8` 条对话上下文，连续对话更有连贯性
- **工具调用**：聊天输入交给大模型，`/` 前缀指令触发本机工具
- **执行命令**：`/shell 命令`，10 秒超时保护
- **文件操作**：`/ls`、`/cat`、`/open`、`/mkdir`
- **系统信息**：`/sysinfo` 查看 CPU / 内存 / 磁盘
- **桌面窗口**：多行聊天 + 输入框，回车快捷发送；调模型时界面不卡死（线程处理 + "思考中…"占位）
- **规则兜底**：Ollama 未启动/出错时自动回退到内置规则回复

---

## 📁 项目结构

```
Agent/
├── main.py            # 程序入口
├── requirements.txt   # 运行依赖（psutil）+ 打包依赖（pyinstaller）
├── agent/
│   ├── __init__.py    # 应用包定义（__version__ = "0.2.0"）
│   ├── config.py      # 配置中心（模型名、Ollama 地址、采样参数等）
│   ├── core.py        # 核心逻辑：大模型聊天 + 工具调用 + 规则兜底
│   ├── tools.py       # 工具集：执行命令、文件操作、系统信息
│   └── ui.py          # 桌面 GUI（tkinter 暗色聊天窗口）
├── DesktopAgent.spec          # release 版 PyInstaller 打包配置
├── DesktopAgentDebug.spec     # debug 版打包配置（带控制台日志）
├── requirements.txt
└── README.md
```

---

## 🏗️ 软件架构

### 分层架构图

```
                        ┌─────────────────────────────┐
                        │         用户 / 桌面          │
                        └──────────────┬──────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │   UI 层  agent/ui.py  (ChatWindow)   │
                    │   · 聊天窗口构建 / 消息回显           │
                    │   · 事件绑定 / 线程调度(不卡界面)     │
                    └──────────────────┬──────────────────┘
                                       │  agent.handle(text)
                    ┌──────────────────▼──────────────────┐
                    │  核心层  agent/core.py  (Agent)      │
                    │   · 对话分发 _dispatch()             │
                    │   · LLM 调用 _query_ollama()        │
                    │   · 工具路由 _handle_tool()          │
                    │   · 规则兜底 _chat()                 │
                    └───────────┬───────────────┬─────────┘
                                │               │
              ┌─────────────────▼──┐   ┌────────▼────────────────┐
              │   LLM 层 (外部)    │   │  工具层  agent/tools.py  │
              │  Ollama 本地服务   │   │  · 执行命令 run_command   │
              │  http://localhost:│   │  · 文件操作 list/read/    │
              │   11434/api/chat  │   │    open/mkdir            │
              │  模型: qwen2.5    │   │  · 系统信息 get_sysinfo   │
              │   :0.5b           │   └───────────┬──────────────┘
              └───────────────────┘               │
                                                  │
                          ┌───────────────────────▼────────┐
                          │  配置层  agent/config.py        │
                          │  · OLLAMA_HOST / MODEL          │
                          │  · TEMPERATURE / MAX_TOKENS     │
                          │  · HISTORY_LIMIT / TIMEOUT      │
                          │  · SYSTEM_PROMPT                │
                          └────────────────────────────────┘
```

### 数据流转（调用链）

```
用户输入文字
  │
  ▼
ChatWindow.on_send(text)          [ui.py]  捕获输入，显示占位"思考中…"
  │  启动后台线程（避免界面卡死）
  ▼
ChatWindow._process(text)         [ui.py]  线程中调用核心层
  │
  ▼
Agent.handle(text)                [core.py] 主入口：记录历史 → 分发 → 存回复
  │
  ▼
Agent._dispatch(text)             [core.py] 判断是否以 "/" 开头的工具指令
  │
  ├── 是工具指令 ──► Agent._handle_tool(text)  直接走本机工具，不请求大模型
  │
  └── 是普通聊天 ──► Agent._chat_with_llm(text)  尝试调用大模型
                          │
                          ▼
                    Agent._query_ollama(text)   ★ 连接大模型接口
                          │  构造 messages + payload
                          ▼
                    urllib.request → POST http://localhost:11434/api/chat
                          │  解析返回 JSON：message.content
                          ▼
                    Agent._extract_tool(reply)  提取回复中的 "/工具指令"
                          │  若存在则自动执行并拼接结果
                          │  若调用失败 → Agent._chat() 规则兜底
                          ▼
                    ChatWindow._show_reply(reply)  [ui.py] 回到主线程显示
```

### 各模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| 入口 | `main.py` | 创建 `Agent` 实例并启动 `ChatWindow` |
| 配置层 | `agent/config.py` | 集中管理所有可调参数，业务代码只引用不放常量 |
| 核心层 | `agent/core.py` | 对话分发、大模型调用、工具路由、规则兜底、记忆管理 |
| 工具层 | `agent/tools.py` | 具体本机操作实现，与业务解耦，可独立复用 |
| UI 层 | `agent/ui.py` | tkinter 界面构建、线程调度、消息回显 |

---

## 🔌 函数接口注释

### 核心层 `agent/core.py` — class `Agent`

#### `handle(self, user_input: str) -> str`
- **作用**：Agent 主入口，接收用户输入，返回回复文本。
- **参数**：`user_input` — 用户输入的原始字符串。
- **返回**：Agent 的回复字符串。
- **异常**：内部捕获所有异常，返回 `"出错了：{e}"`，不向 UI 抛错。
- **说明**：会记录历史、控制记忆长度（`HISTORY_LIMIT*2`）。

#### `_dispatch(self, text: str) -> str`
- **作用**：分发器，判断输入是工具指令还是聊天。
- **参数**：`text` — 去除首尾空白的输入。
- **返回**：回复字符串。
- **逻辑**：以 `"/"` 开头 → 走 `_handle_tool`；否则 → 走 `_chat_with_llm`。

#### `_chat_with_llm(self, text: str) -> str`
- **作用**：尝试调用大模型聊天，失败则回退规则聊天。
- **参数**：`text` — 聊天内容。
- **返回**：回复字符串。
- **逻辑**：调用 `_query_ollama`；若模型回复中包含 `/工具指令`，则提取并执行，拼接结果。

#### `_query_ollama(self, user_text: str) -> str` ★ 连接大模型的接口
- **作用**：调用 Ollama `/api/chat`，返回模型回复文本。
- **参数**：`user_text` — 当前用户输入。
- **返回**：模型的纯文本回复。
- **异常**：模型返回空时抛 `RuntimeError("模型返回为空")`；网络/超时异常由 `urlopen` 抛出。
- **实现**：用标准库 `urllib.request` 发 POST 到 `{OLLAMA_HOST}/api/chat`，body 为 `{model, messages, stream:false, options}`，超时 `OLLAMA_TIMEOUT`。

#### `_handle_tool(self, text: str) -> str`
- **作用**：工具指令路由，把 `/xxx 参数` 映射到具体工具函数。
- **参数**：`text` — 形如 `/ls`、`/cat 文件名` 的指令。
- **返回**：工具执行结果字符串。
- **逻辑**：解析前缀命令与参数，查 `tool_map` 字典分发；未知指令返回提示；捕获 `ToolError` 返回 `❌` 错误。

#### `_extract_tool(self, reply: str) -> str`
- **作用**：从模型回复中提取 `/工具指令` 行。
- **参数**：`reply` — 模型回复文本。
- **返回**：指令字符串；无则返回空串。
- **实现**：正则 `^\s*(/\S[^\n]*)` 多行匹配。

#### `_chat(self, text: str) -> str`
- **作用**：内置规则聊天，作为 Ollama 失败时的兜底。
- **参数**：`text` — 用户输入。
- **返回**：规则生成的回复。
- **逻辑**：关键词匹配（你好/你是谁/时间/谢谢/再见/能做什么等）。

#### `_help(self) -> str`
- **作用**：返回工具指令帮助文本。
- **返回**：帮助字符串。

---

### 工具层 `agent/tools.py`

#### `run_command(cmd: str, timeout: int = 10) -> str`
- **作用**：执行 shell 命令，带超时保护。
- **参数**：`cmd` — 命令字符串；`timeout` — 超时秒数（默认 10）。
- **返回**：命令输出；非零退出码时带 `[退出码 N]` 前缀；空输出返回 `"(无输出)"`。
- **异常**：超时/失败抛 `ToolError`。

#### `list_dir(path: str = ".") -> str`
- **作用**：列出目录内容，目录名带 `/` 后缀标记。
- **参数**：`path` — 目录路径（默认当前目录）。
- **返回**：条目文本；空目录返回 `"(空目录)"`。
- **异常**：读取失败抛 `ToolError`。

#### `read_file(path: str, max_bytes: int = 200_000) -> str`
- **作用**：读取文本文件内容，限制大小防止刷屏。
- **参数**：`path` — 文件路径；`max_bytes` — 大小上限（默认 200KB）。
- **返回**：文件内容。
- **异常**：文件不存在/过大/读取失败抛 `ToolError`。

#### `open_path(path: str = ".") -> str`
- **作用**：用系统默认程序打开路径（跨平台）。
- **参数**：`path` — 路径。
- **返回**：`"已打开：{绝对路径}"`。
- **异常**：路径不存在/打开失败抛 `ToolError`。

#### `make_dir(path: str) -> str`
- **作用**：创建目录（含父目录）。
- **参数**：`path` — 目录路径。
- **返回**：`"已创建目录：{绝对路径}"`。
- **异常**：创建失败抛 `ToolError`。

#### `get_sysinfo() -> str`
- **作用**：获取系统信息（CPU/内存/磁盘/开机时间/用户）。
- **返回**：格式化后的信息文本。

---

### UI 层 `agent/ui.py` — class `ChatWindow`

#### `on_send(self) -> None`
- **作用**：发送按钮/回车触发，读取输入并启动后台处理线程。
- **逻辑**：清空输入框 → 回显用户消息 → 显示"思考中…"占位 → 开线程调用 `_process`。

#### `_process(self, text: str) -> None`
- **作用**：在线程中调用 `agent.handle(text)`，避免阻塞 UI。
- **逻辑**：拿到回复后通过 `root.after(0, ...)` 回到主线程调用 `_show_reply`。

#### `_show_reply(self, reply: str) -> None`
- **作用**：删除"思考中…"占位，回显真实回复。
- **逻辑**：用 `pending` tag 定位占位并删除，再追加回复。

#### `_append(self, who, text, font_tag) -> None`
- **作用**：向聊天区追加消息（user/agent/banner 样式）。
- **参数**：`who` — 角色；`text` — 内容；`font_tag` — 额外样式 tag。

#### `run(self) -> None`
- **作用**：启动 tkinter 主循环。

---

## ⚙️ 配置说明（`agent/config.py`）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama 服务地址（连接大模型的接口） |
| `MODEL` | `qwen2.5:0.5b` | 使用的本地模型 |
| `TEMPERATURE` | `0.7` | 采样温度（越高越随机） |
| `MAX_TOKENS` | `512` | 单次回复最大 token 数 |
| `HISTORY_LIMIT` | `8` | 传给模型的最近消息条数（记忆窗口） |
| `OLLAMA_TIMEOUT` | `60` | 调用大模型超时（秒） |
| `SYSTEM_PROMPT` | — | 系统提示词（定义角色 + 工具调用引导） |

---

## 🚀 快速开始

### 1. 安装 Ollama 并拉取模型
```bash
# macOS 用 Homebrew 安装 Ollama
brew install ollama

# 启动 Ollama 服务（首次会自动在后台运行）
ollama serve

# 拉取最小模型（约 0.4GB）
ollama pull qwen2.5:0.5b

# 可选：确认模型已就绪
ollama list
```

> 如果你内存充足（≥8GB），可在 `agent/config.py` 中把 `MODEL` 改成更大的模型换取更好效果，如 `qwen2.5:7b`。

### 2. 创建并激活虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行
```bash
python main.py
```

---

## 💬 使用示例

| 输入 | 效果 |
|------|------|
| `你好` | 大模型打招呼 |
| `帮我列一下当前目录` | 大模型回复并可能输出 `/ls` 自动执行 |
| `现在几点了` | 大模型回答（或规则兜底报时间） |
| `/ls` | 手动列出当前目录 |
| `/cat 文件名` | 读取文本文件 |
| `/open 路径` | 用默认程序打开 |
| `/mkdir 路径` | 创建目录 |
| `/shell pwd` | 执行 shell 命令 |
| `/sysinfo` | 查看系统信息 |
| `/help` | 查看所有指令 |

### 可用工具指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/help` | — | 显示帮助 |
| `/ls` | `[路径]` | 列出目录内容 |
| `/cat` | `文件名` | 读取文本文件 |
| `/open` | `[路径]` | 用默认程序打开 |
| `/mkdir` | `路径` | 创建目录 |
| `/shell` | `命令` | 执行 shell 命令（10秒超时） |
| `/sysinfo` | — | 查看系统信息 |
| `/echo` | `文本` | 原样回显 |

---

## 📦 打包说明

### 打包命令
```bash
# 构建 release 版（无控制台）
pyinstaller DesktopAgent.spec

# 构建 debug 版（带控制台日志）
pyinstaller DesktopAgentDebug.spec
```

### 打包产物
| 产物 | 说明 |
|------|------|
| `dist/DesktopAgent.app` | release 版，无控制台窗口 |
| `dist-debug/DesktopAgentDebug.app` | debug 版，带控制台便于调试 |

### 重要前提
- App 是**独立完整应用**（已内置 Python、tkinter、psutil 等依赖），双击即可运行。
- **大模型不随 App 打包**：App 通过 HTTP 调用**本机 Ollama 服务**（`http://localhost:11434`）。
- 目标机器需**已安装并启动 Ollama**，且**已拉取模型**（`ollama pull qwen2.5:0.5b`），否则打包后的 App 只能体验规则兜底的聊天功能。

---

## 🔒 安全说明

- `/shell` 会在你的账户权限下执行命令，**请勿输入破坏性命令**。
- 命令带 **10 秒超时**保护，避免卡死。
- 本应用仅作 Demo 演示用途，请勿在生产环境使用 `/shell` 等高权限指令。

---

## 📄 版本

当前版本：**v0.3.0**（详见 `RELEASE_NOTES_v0.3.0.md`）
