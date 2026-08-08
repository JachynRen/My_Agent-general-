"""Agent 核心：意图识别与规则式回复。"""
import datetime
import re

from . import tools


class Agent:
    """一个简单的规则式桌面 Agent。"""

    # 工具指令前缀
    TOOL_PREFIX = "/"

    def __init__(self, name: str = "小助手"):
        self.name = name
        self.history: list[dict] = []

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------
    def handle(self, user_input: str) -> str:
        """处理用户输入，返回 Agent 回复。"""
        text = user_input.strip()
        if not text:
            return "请输入内容。输入 /help 查看我能做什么。"

        self.history.append({"role": "user", "content": text})

        try:
            reply = self._dispatch(text)
        except Exception as e:  # noqa: BLE001
            reply = f"出错了：{e}"

        self.history.append({"role": "assistant", "content": reply})
        return reply

    # ------------------------------------------------------------------
    # 分发器
    # ------------------------------------------------------------------
    def _dispatch(self, text: str) -> str:
        # 工具指令（斜杠开头）
        if text.startswith(self.TOOL_PREFIX):
            return self._handle_tool(text)

        # 聊天/规则回复
        return self._chat(text)

    def _handle_tool(self, text: str) -> str:
        parts = text[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        tool_map = {
            "help": lambda: self._help(),
            "ls": lambda: tools.list_dir(arg or "."),
            "cat": lambda: self._need_arg(arg, "请输入要读取的文件路径") or tools.read_file(arg),
            "open": lambda: tools.open_path(arg or "."),
            "mkdir": lambda: self._need_arg(arg, "请输入要创建的目录路径") or tools.make_dir(arg),
            "shell": lambda: self._need_arg(arg, "请输入要执行的命令") or tools.run_command(arg),
            "sysinfo": lambda: tools.get_sysinfo(),
            "clear": lambda: tools.run_command("clear") or "",  # 终端清屏，GUI 中忽略
            "echo": lambda: arg,
        }

        handler = tool_map.get(cmd)
        if not handler:
            return f"未知指令 /{cmd}。输入 /help 查看可用指令。"
        try:
            return handler()
        except tools.ToolError as e:
            return f"❌ {e}"

    def _need_arg(self, arg: str, msg: str) -> str:
        if not arg:
            raise tools.ToolError(msg)
        return ""

    # ------------------------------------------------------------------
    # 聊天规则
    # ------------------------------------------------------------------
    def _chat(self, text: str) -> str:
        lowered = text.lower()

        if any(k in lowered for k in ("你好", "您好", "hello", "hi", "嗨")):
            return f"你好！我是{self.name}，一个桌面 Agent。输入 /help 看看我能帮你做什么 😊"

        if any(k in lowered for k in ("你是谁", "介绍", "自我")):
            return (
                f"我是 {self.name}，一个运行在你本机的简单桌面 Agent。\n"
                "目前我能：介绍自己、报时间、执行本机命令、管理文件。\n"
                "输入 /help 查看完整指令列表。"
            )

        if any(k in lowered for k in ("时间", "几点", "日期", "现在")):
            now = datetime.datetime.now()
            return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

        if any(k in lowered for k in ("谢谢", "感谢", "thank")):
            return "不客气！有什么需要随时找我 🙂"

        if any(k in lowered for k in ("再见", "拜拜", "bye")):
            return "再见！期待下次见面 👋"

        if any(k in lowered for k in ("能做什么", "会什么", "能干什么", "help")):
            return self._help()

        return (
            "我没太明白你的意思 🤔（当前是演示版，尚未接入大模型）。\n"
            "你可以试试：\n"
            "  · 问时间：'现在几点了'\n"
            "  · 打个招呼：'你好'\n"
            "  · 或输入 /help 查看所有工具指令"
        )

    # ------------------------------------------------------------------
    # 帮助
    # ------------------------------------------------------------------
    def _help(self) -> str:
        return (
            "🤖 可用指令：\n"
            "----------------------\n"
            "  /help      显示本帮助\n"
            "  /ls    [路径]   列出目录内容\n"
            "  /cat   [文件]   读取文本文件\n"
            "  /open  [路径]   用默认程序打开\n"
            "  /mkdir [路径]   创建目录\n"
            "  /shell [命令]   执行 shell 命令（10秒超时）\n"
            "  /sysinfo        查看系统信息\n"
            "  /echo  [文本]   原样回显\n"
        )

