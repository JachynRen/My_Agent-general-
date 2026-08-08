"""Agent 配置中心：Ollama 模型相关参数。"""

# Ollama 本地服务地址（默认端口 11434）
OLLAMA_HOST = "http://localhost:11434"

# 使用的模型（最小编号，体积小、内存要求低）
MODEL = "qwen2.5:0.5b"

# 采样参数
TEMPERATURE = 0.7
MAX_TOKENS = 512

# 上下文记忆：传给模型的最近消息条数
HISTORY_LIMIT = 8

# 调用大模型超时（秒）
OLLAMA_TIMEOUT = 60

# 系统提示词：定义 Agent 角色，并引导它自主使用 / 工具指令
SYSTEM_PROMPT = (
    "你是运行在用户本机桌面的智能助手「小助手」。"
    "你能用中文友好、简洁地回答问题。"
    "当你需要执行本机操作（列目录、读文件、执行命令、查系统信息等）时，"
    "请在回复中直接给出 / 开头的小写指令，例如：\n"
    "  /ls\n"
    "  /cat 文件路径\n"
    "  /sysinfo\n"
    "如果无需执行命令，就正常聊天回答。"
)
