@echo off
echo ========================================================
echo Setting up StockTitan AI Environment on F: Drive
echo ========================================================

cd /d "%~dp0"

REM 强制规定所有下载缓存、模型权重、虚拟环境均在 F:\us-stock-monitor
set TARGET_DIR=F:\us-stock-monitor
set VENV_DIR=%TARGET_DIR%\ai_env
set PIP_CACHE_DIR=%TARGET_DIR%\pip_cache
set HF_HOME=%TARGET_DIR%\hf_cache

echo Target Directory: %TARGET_DIR%
echo Virtual Env: %VENV_DIR%
echo Pip Cache: %PIP_CACHE_DIR%
echo HuggingFace Models Cache: %HF_HOME%
echo.

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"
if not exist "%HF_HOME%" mkdir "%HF_HOME%"

echo [1] Creating Python Virtual Environment on F: Drive...
python -m venv "%VENV_DIR%"

echo [2] Upgrading pip...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip

echo [3] Installing required packages into F: Drive (this might take a few minutes)...
"%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt

echo.
echo ========================================================
echo Environment setup complete!
echo All data (2GB+ models & packages) has been strictly confined to: %TARGET_DIR%
echo You can now run start_demo.bat
echo ========================================================
pause
