"""桌面 GUI：聊天窗口。"""
import tkinter as tk
from tkinter import scrolledtext

from .core import Agent


class ChatWindow:
    """基于 tkinter 的聊天窗口。"""

    # 暗色主题配色
    BG_ROOT = "#1e1f22"
    BG_CHAT = "#2b2d31"
    FG_TEXT = "#e8e8e8"
    BG_USER = "#3a4a63"
    BG_AGENT = "#383a40"
    FG_BANNER = "#8a8f98"
    BG_INPUT = "#33353a"
    BG_BUTTON = "#4a90d9"
    FG_BUTTON = "#ffffff"
    BG_BUTTON_ACTIVE = "#3a7bbf"

    def __init__(self, agent: Agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("桌面 Agent Demo")
        self.root.geometry("640x520")
        self.root.minsize(500, 400)
        self.root.configure(bg=self.BG_ROOT)

        self._build_widgets()
        self._show_banner()

    # ------------------------------------------------------------------
    # 界面构建
    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        # 聊天记录区
        frame_chat = tk.Frame(self.root, bg=self.BG_ROOT)
        frame_chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        self.chat_area = scrolledtext.ScrolledText(
            frame_chat,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Helvetica", 13),
            bg=self.BG_CHAT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # 滚动条配色（macOS 下部分有效）
        try:
            self.chat_area.configure(
                highlightbackground=self.BG_ROOT,
                highlightcolor=self.BG_ROOT,
                borderwidth=0,
            )
        except tk.TclError:
            pass

        self.chat_area.tag_configure(
            "user",
            background=self.BG_USER,
            foreground=self.FG_TEXT,
            lmargin1=8,
            lmargin2=8,
            spacing1=6,
            spacing3=6,
            relief=tk.FLAT,
        )
        self.chat_area.tag_configure(
            "agent",
            background=self.BG_AGENT,
            foreground=self.FG_TEXT,
            lmargin1=8,
            lmargin2=8,
            spacing1=6,
            spacing3=6,
        )
        self.chat_area.tag_configure("banner", foreground=self.FG_BANNER, spacing2=8)

        # 输入区
        frame_input = tk.Frame(self.root, bg=self.BG_ROOT)
        frame_input.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            frame_input,
            textvariable=self.input_var,
            font=("Helvetica", 13),
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#4a4d52",
            highlightcolor=self.BG_BUTTON,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.entry.bind("<Return>", lambda e: self.on_send())

        self.send_btn = tk.Button(
            frame_input,
            text="发送",
            command=self.on_send,
            font=("Helvetica", 12),
            bg=self.BG_BUTTON,
            fg=self.FG_BUTTON,
            activebackground=self.BG_BUTTON_ACTIVE,
            activeforeground=self.FG_BUTTON,
            relief=tk.FLAT,
            padx=18,
            highlightthickness=0,
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(8, 0))

    def _show_banner(self) -> None:
        banner = (
            f"🤖 {self.agent.name} 已就绪\n"
            "这是一个演示版桌面 Agent（尚未接入大模型）。\n"
            "直接聊天，或输入 /help 查看工具指令。"
        )
        self._append("agent", banner, font_tag="banner")
        self._append_line()

    # ------------------------------------------------------------------
    # 消息回显
    # ------------------------------------------------------------------
    def _append(self, who: str, text: str, font_tag: str = "") -> None:
        self.chat_area.configure(state=tk.NORMAL)
        tag = font_tag or who
        self.chat_area.insert(tk.END, text + "\n", tag)
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def _append_line(self) -> None:
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "\n")
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    # ------------------------------------------------------------------
    # 发送逻辑
    # ------------------------------------------------------------------
    def on_send(self) -> None:
        text = self.input_var.get().strip()
        self.input_var.set("")
        if not text:
            return

        self._append("user", f"你：{text}")
        reply = self.agent.handle(text)
        self._append("agent", f"{self.agent.name}：{reply}")
        self._append_line()
        self.entry.focus_set()

    def run(self) -> None:
        self.entry.focus_set()
        self.root.mainloop()

