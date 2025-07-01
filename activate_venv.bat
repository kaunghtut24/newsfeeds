@echo off
REM Activate Virtual Environment for News Feed Application
REM =====================================================

echo News Feed Application - Virtual Environment
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Show status
echo.
echo ✓ Virtual environment activated!
echo ✓ Python version: 
python --version
echo ✓ Virtual environment path: %VIRTUAL_ENV%
echo.

echo Available commands:
echo   python main.py              - Run CLI version
echo   python main.py --web        - Run web interface  
echo   python run_web.py           - Run web server
echo   python test_venv_setup.py   - Test setup
echo   pytest                      - Run unit tests
echo   deactivate                  - Exit virtual environment
echo.

REM Keep the command prompt open
cmd /k
