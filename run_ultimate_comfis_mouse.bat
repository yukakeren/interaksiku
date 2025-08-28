@echo off
title Ultimate Comfis Mouse
echo.
echo 🖱️ ==========================================
echo     ULTIMATE COMFIS MOUSE LAUNCHER
echo 🖱️ ==========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found. Using system Python...
    echo 💡 Run 'setup.bat' first to create virtual environment
)

echo.
echo 🔍 Checking dependencies...
python -c "import cv2, mediapipe, numpy, tkinter; print('✅ All dependencies available')" 2>nul
if errorlevel 1 (
    echo ❌ Some dependencies are missing!
    echo 💡 Run 'pip install -r requirements.txt' to install dependencies
    echo.
    pause
    exit /b 1
)

echo.
echo 🚀 Launching Ultimate Comfis Mouse...
echo 📋 Instructions:
echo    - Go to Calibration tab to set up tracking area
echo    - Use Mouse Control tab to start hand tracking
echo    - Press Ctrl+C to exit
echo.

python ultimate_comfis_mouse.py

echo.
if errorlevel 1 (
    echo ❌ Application exited with error
) else (
    echo ✅ Application closed normally
)
echo.
echo 👋 Press any key to exit...
pause >nul
