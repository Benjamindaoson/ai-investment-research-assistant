@echo off
echo ========================================================
echo  StockTitan AI Engine — Launch Script
echo ========================================================

cd /d "%~dp0"

set TARGET_DIR=F:\us-stock-monitor
set VENV_DIR=%TARGET_DIR%\ai_env
set HF_HOME=%TARGET_DIR%\hf_cache
set TRANSFORMERS_CACHE=%TARGET_DIR%\hf_cache

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at %VENV_DIR%
    echo Please run setup_f_drive.bat first!
    pause & exit /b
)

IF NOT EXIST ".env" (
    copy .env.example .env >nul 2>&1
)

echo [1] Starting FastAPI AI Engine (port 8000)...
start "StockTitan API" cmd /k "cd /d "%~dp0" && set HF_HOME=%HF_HOME% && set TRANSFORMERS_CACHE=%TRANSFORMERS_CACHE% && %VENV_DIR%\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2] Waiting for API to start...
timeout /t 4 /nobreak >nul

echo [3] Opening Dashboard in browser...
start "" "%~dp0dashboard.html"

echo.
echo ========================================================
echo  API Docs: http://127.0.0.1:8000/docs
echo  Dashboard: dashboard.html (opened in browser)
echo ========================================================
