@echo off
REM ###########################################################################
REM Startup Script for SLSQP Optimizer Microservice (Windows)
REM ###########################################################################

echo.
echo ===============================================================
echo   SLSQP Optimizer Microservice Startup
echo ===============================================================
echo.

REM Check Python
echo [1/5] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check virtual environment
echo [2/5] Checking virtual environment...
if not exist "venv\" (
    echo [WARNING] Virtual environment not found. Creating...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment found
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Start service
echo [5/5] Starting optimizer service...
echo.
echo ===============================================================
echo   Service Starting...
echo   API Docs: http://127.0.0.1:8001/docs
echo   Health: http://127.0.0.1:8001/health
echo   Press Ctrl+C to stop
echo ===============================================================
echo.

REM Run the service
python run.py %*

pause
