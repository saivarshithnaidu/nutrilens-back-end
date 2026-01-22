@echo off
echo Starting Backend Server...
"venv\Scripts\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server crashed. Please check the error above.
    pause
)
