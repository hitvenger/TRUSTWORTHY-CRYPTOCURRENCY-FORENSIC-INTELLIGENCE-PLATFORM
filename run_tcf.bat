@echo off
setlocal enabledelayedexpansion

title TCF-FX — Trustworthy Cryptocurrency Forensic Intelligence Platform
color 0B
cls

echo ===============================================================================
echo   TCF-FX: TRUSTWORTHY CRYPTOCURRENCY FORENSIC INTELLIGENCE PLATFORM
echo   Tagline: Evidence-aware AI for explainable cryptocurrency investigations
echo ===============================================================================
echo.
echo [*] Initializing TCF-FX environment...
cd /d "%~dp0"

:: 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] ERROR: Python is not found in PATH. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

:: 2. Check Node.js
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] ERROR: Node.js/npm is not found in PATH. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo [+] Python and Node.js environments detected.

:: 3. Install Python Dependencies if needed
if not exist "backend\app\core\config.py" (
    echo [!] Working directory corrupted.
    pause
    exit /b 1
)

echo [*] Checking and verifying Python packages...
pip install -r requirements.txt --quiet >nul 2>nul

:: 4. Check / Install Frontend Dependencies
if not exist "frontend\node_modules" (
    echo [*] Installing frontend packages (first run only, please wait)...
    cd frontend
    call npm install
    cd ..
)

:: 5. Initialize & Pre-seed Database if missing
if not exist "tcf_forensics.db" (
    echo [*] Initializing forensic database and pre-seeding investigation case...
    python tcf.py demo
)

echo.
echo ===============================================================================
echo   STARTING LIVE SERVERS
echo ===============================================================================
echo.
echo [*] Starting FastAPI Backend on http://localhost:8000 ...
start "TCF-FX Backend Server (Port 8000)" cmd /k "cd /d %~dp0 && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo [*] Starting Vite Frontend on http://localhost:5173 ...
start "TCF-FX Frontend Web UI (Port 5173)" cmd /k "cd /d %~dp0\frontend && npm run dev -- --host 127.0.0.1 --port 5173"

:: Wait 4 seconds for servers to initialize
echo [*] Waiting for services to initialize...
timeout /t 4 /nobreak >nul

:: 6. Open Browser
echo [*] Launching Forensic Dashboard in your default web browser...
start http://localhost:5173

echo.
echo ===============================================================================
echo   TCF-FX IS ONLINE AND READY!
echo ===============================================================================
echo.
echo   - Web Dashboard:     http://localhost:5173
echo   - REST API Docs:     http://localhost:8000/docs
echo   - Health Check:      http://localhost:8000/health
echo.
echo   Keep the server terminal windows open while using the application.
echo   To shut down, close the terminal windows or press Ctrl+C in each window.
echo.
echo ===============================================================================
pause
