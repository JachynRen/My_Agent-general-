@echo off
rem ============================================
rem  DesktopAgent 一键启动脚本 (Windows)
rem ============================================
cd /d "%~dp0"

rem 1. 检查 Ollama 服务是否运行
echo [1/3] 检查 Ollama 服务...
curl -s -o nul -w %%{http_code} http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo     未检测到 Ollama，尝试启动...
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe"
    timeout /t 5 /nobreak >nul
) else (
    echo     Ollama 服务运行中 ✓
)

rem 2. 检查虚拟环境
echo [2/3] 检查虚拟环境...
if not exist ".venv\Scripts\python.exe" (
    echo     未找到虚拟环境，正在创建...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo     虚拟环境就绪 ✓
)

rem 3. 启动应用
echo [3/3] 启动 DesktopAgent...
call .venv\Scripts\activate.bat
python main.py

pause
