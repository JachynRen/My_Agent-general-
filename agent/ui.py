"""桌面 GUI：聊天窗口。"""
import threading
import tkinter as tk

from . import __version__
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
    BG_BUTTON = "#000000"
    FG_BUTTON = "#ffffff"
    BG_BUTTON_ACTIVE = "#2a2a2a"
    BG_SCROLLBAR = "#53565c"
    BG_SCROLLBAR_TROUGH = "#1e1f22"
    BG_SCROLLBAR_ACTIVE = "#64686f"

    def __init__(self, agent: Agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.title(f"桌面 Agent Demo  v{__version__}")
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

# 聊天文本区 + 自定义暗色滚动条
        chat_container = tk.Frame(frame_chat, bg=self.BG_ROOT)
        chat_container.pack(fill=tk.BOTH, expand=True)

        self.chat_area = tk.Text(
            chat_container,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Helvetica", 13),
            bg=self.BG_CHAT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            highlightthickness=0,
            borderwidth=0,
        )
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 暗色滚动条
        self.scrollbar = tk.Scrollbar(
            chat_container,
            command=self.chat_area.yview,
            bg=self.BG_SCROLLBAR,
            activebackground=self.BG_SCROLLBAR_ACTIVE,
            troughcolor=self.BG_SCROLLBAR_TROUGH,
            highlightthickness=0,
            borderwidth=0,
            relief=tk.FLAT,
            width=12,
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_area.configure(yscrollcommand=self.scrollbar.set)

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

# macOS 的原生 Button 会忽略 bg/fg，改用 Label 模拟按钮以完全控制颜色
        self.send_btn = tk.Label(
            frame_input,
            text="发送",
            font=("Helvetica", 12, "bold"),
            bg=self.BG_BUTTON,
            fg=self.FG_BUTTON,
            padx=18,
            pady=5,
            cursor="hand2",
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self.send_btn.bind("<Button-1>", lambda e: self.on_send())
        self.send_btn.bind(
            "<Enter>",
            lambda e: self.send_btn.configure(bg=self.BG_BUTTON_ACTIVE),
        )
        self.send_btn.bind(
            "<Leave>",
            lambda e: self.send_btn.configure(bg=self.BG_BUTTON),
        )

    def _show_banner(self) -> None:
        banner = (
            f"🤖 {self.agent.name} 已就绪  (v{__version__})\n"
            "这是一个演示版桌面 Agent。\n"
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
        # 用特殊 tag 标记占位消息，便于之后精确删除
        self._append("agent", f"{self.agent.name}：🤔 思考中…", font_tag="pending")

        # 放到线程执行，避免调用大模型时界面卡死
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text: str) -> None:
        reply = self.agent.handle(text)
        # 线程中不能直接操作 tkinter，需回到主线程更新
        self.root.after(0, lambda: self._show_reply(reply))

    def _show_reply(self, reply: str) -> None:
        # 移除"思考中…"占位，替换为真实回复
        self.chat_area.configure(state=tk.NORMAL)
        if self.chat_area.tag_ranges("pending"):
            start = self.chat_area.tag_ranges("pending")[0]
            self.chat_area.delete(start, "end-1c")
        self.chat_area.configure(state=tk.DISABLED)

        self._append("agent", f"{self.agent.name}：{reply}")
        self._append_line()
        self.entry.focus_set()

    def run(self) -> None:
        self.entry.focus_set()
        self.root.mainloop()

