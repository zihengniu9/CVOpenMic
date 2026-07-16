@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title 简历开麦 - CVOpenMic

echo.
echo  简历开麦 · CVOpenMic
echo  ========================================
echo.

if not exist ".env" (
    copy /Y ".env.example" ".env" >nul
    echo  [!] 已创建 .env，请先填入 DEEPSEEK_API_KEY。
    echo  [!] 获取地址: https://platform.deepseek.com/
    echo.
    pause
    exit /b 1
)

findstr /C:"DEEPSEEK_API_KEY=your-api-key-here" ".env" >nul 2>&1
if not errorlevel 1 (
    echo  [!] .env 仍在使用示例 API Key，请先填写真实的 DEEPSEEK_API_KEY。
    echo.
    pause
    exit /b 1
)

where py >nul 2>&1
if not errorlevel 1 (
    set "BOOTSTRAP_PYTHON=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo  [X] 未找到 Python。请安装 Python 3.10 或更高版本。
        pause
        exit /b 1
    )
    set "BOOTSTRAP_PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo  [1/3] 正在创建项目虚拟环境 .venv ...
    %BOOTSTRAP_PYTHON% -m venv ".venv"
    if errorlevel 1 (
        echo  [X] 虚拟环境创建失败。
        pause
        exit /b 1
    )
    set "NEEDS_INSTALL=1"
) else (
    echo  [1/3] 已找到项目虚拟环境 .venv。
    set "NEEDS_INSTALL=0"
)

".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo  [X] .venv 使用的 Python 版本低于 3.10。
    echo      请安装新版 Python，并重新创建 .venv。
    pause
    exit /b 1
)

if not exist ".venv\.requirements-installed" (
    set "NEEDS_INSTALL=1"
) else (
    fc /B "requirements.txt" ".venv\.requirements-installed" >nul 2>&1
    if errorlevel 1 set "NEEDS_INSTALL=1"
)

if "%NEEDS_INSTALL%"=="1" (
    echo  [2/3] 正在安装或更新依赖 ...
    ".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
    if errorlevel 1 (
        echo  [X] 依赖安装失败，请检查网络和错误信息。
        pause
        exit /b 1
    )
    copy /Y "requirements.txt" ".venv\.requirements-installed" >nul
) else (
    echo  [2/3] 依赖已是最新版本。
)

where tesseract >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [!] 未检测到 Tesseract OCR。
    echo      PDF、DOCX、TXT 仍可使用；图片简历识别需要另行安装
    echo      Tesseract、chi_sim 中文语言包，并把 tesseract 加入 PATH。
)

echo.
echo  [3/3] 启动完成后请访问 http://localhost:8501
echo.
".venv\Scripts\python.exe" -m streamlit run "app.py"

if errorlevel 1 (
    echo.
    echo  [X] CVOpenMic 已异常退出，请查看上方错误信息。
    pause
)

endlocal
