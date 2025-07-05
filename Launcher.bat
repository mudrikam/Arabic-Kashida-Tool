@echo off
title Arabic Kashida Tool Launcher
echo.
echo ===============================================
echo    Arabic Kashida Tool - Launcher
echo ===============================================
echo.
echo Memulai aplikasi Arabic Kashida Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python tidak ditemukan!
    echo Pastikan Python sudah terinstall dan ada di PATH
    echo.
    pause
    exit /b 1
)

REM Check if the main Python file exists
if not exist "arabic_typing_helper.py" (
    echo ERROR: File arabic_typing_helper.py tidak ditemukan!
    echo Pastikan Anda menjalankan launcher ini dari folder yang benar
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Memeriksa dependencies...
python -c "import PySide6, google.generativeai, pynput, qtawesome" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Beberapa dependencies mungkin belum terinstall
    echo Mencoba menginstall requirements...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Gagal menginstall requirements
        echo Silakan jalankan: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies OK!
echo.
echo Menjalankan Arabic Kashida Tool...
echo.

REM Run the application
python arabic_typing_helper.py

REM Check if the application exited with error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Aplikasi keluar dengan error (kode: %errorlevel%)
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo Aplikasi selesai dijalankan.
echo.
pause