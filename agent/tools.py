"""Agent 工具集：执行命令、文件操作、系统信息。"""
import os
import shutil
import subprocess
import time
import psutil


class ToolError(Exception):
    """工具执行错误。"""


def run_command(cmd: str, timeout: int = 10) -> str:
    """执行 shell 命令，带超时保护。"""
    if not cmd.strip():
        raise ToolError("命令为空")
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = proc.stdout or (proc.stderr or "")
        code = proc.returncode
    except subprocess.TimeoutExpired:
        raise ToolError(f"命令执行超时（超过 {timeout} 秒）")
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"命令执行失败：{e}")

    result = output.strip()
    if proc.returncode != 0:
        result = f"[退出码 {code}] {result}"
    return result or "(无输出)"


def list_dir(path: str = ".") -> str:
    """列出目录内容。"""
    try:
        entries = sorted(os.listdir(path))
    except OSError as e:
        raise ToolError(f"无法读取目录：{e}")
    if not entries:
        return "(空目录)"
    lines = []
    for name in entries:
        full = os.path.join(path, name)
        marker = "/" if os.path.isdir(full) else ""
        lines.append(f"{name}{marker}")
    return "\n".join(lines)


def read_file(path: str, max_bytes: int = 200_000) -> str:
    """读取文本文件内容（限制大小防止刷屏）。"""
    if not os.path.isfile(path):
        raise ToolError(f"文件不存在：{path}")
    size = os.path.getsize(path)
    if size > max_bytes:
        raise ToolError(f"文件过大（{size} 字节），超过上限 {max_bytes} 字节")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        raise ToolError(f"读取文件失败：{e}")


def open_path(path: str = ".") -> str:
    """用系统默认程序打开路径。"""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise ToolError(f"路径不存在：{path}")
    try:
        if sys_platform_is_mac():
            subprocess.Popen(["open", path])
        elif sys_platform_is_win():
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", path])
        return f"已打开：{path}"
    except OSError as e:
        raise ToolError(f"打开失败：{e}")


def make_dir(path: str) -> str:
    """创建目录（含父目录）。"""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        raise ToolError(f"创建目录失败：{e}")
    return f"已创建目录：{os.path.abspath(path)}"


def get_sysinfo() -> str:
    """获取系统信息。"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        boot = psutil.boot_time()
        boot_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot))
        return (
            f"💻 系统信息\n"
            f"----------------------\n"
            f"操作系统: {os.uname().sysname} {os.uname().release}\n"
            f"CPU 使用率: {cpu_percent}%\n"
            f"内存: {mem.used / 1e9:.1f}G / {mem.total / 1e9:.1f}G ({mem.percent}%)\n"
            f"磁盘: {disk.used / 1e9:.1f}G / {disk.total / 1e9:.1f}G ({disk.percent}%)\n"
            f"开机时间: {boot_str}\n"
            f"当前用户: {os.getlogin()}"
        )
    except Exception as e:  # noqa: BLE001
        return f"获取系统信息失败：{e}"


def sys_platform_is_mac() -> bool:
    return os.name == "posix" and os.uname().sysname == "Darwin"


def sys_platform_is_win() -> bool:
    return os.name == "nt"

