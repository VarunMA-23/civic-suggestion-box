@echo off
setlocal enabledelayedexpansion
title Bengaluru Civic Suggestion Box

echo =========================================================
echo    Bengaluru Civic Suggestion Box - Starting Services
echo =========================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

echo [*] Checking Backend virtual environment...
if not exist "%BACKEND_DIR%\venv\Scripts\uvicorn.exe" (
    echo [!] Virtual environment not found in backend\venv.
    echo [*] Creating virtualenv and installing requirements...
    cd /d "%BACKEND_DIR%"
    python -m venv venv
    call ".\venv\Scripts\activate.bat"
    pip install -r requirements.txt
    python init_db.py
)

echo [*] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Civic Suggestion Box - Backend API" cmd /k "cd /d "%BACKEND_DIR%" && call .\venv\Scripts\activate.bat && .\venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [*] Starting Next.js Frontend on http://localhost:3005 ...
start "Civic Suggestion Box - Frontend UI" cmd /k "cd /d "%FRONTEND_DIR%" && node node_modules\next\dist\bin\next dev -p 3005"

echo.
echo =========================================================
echo    Both servers have launched in separate windows!
echo =========================================================
echo  - Frontend Web App:  http://localhost:3005
echo  - Live Map:          http://localhost:3005/map
echo  - Hotspots/Stats:    http://localhost:3005/dashboard
echo  - Backend API Docs:  http://127.0.0.1:8000/docs
echo.
echo  Default Admin Login:
echo    Email:    admin@example.org
echo    Password: ChangeMe!2024
echo =========================================================
echo.
pause
