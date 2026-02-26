@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================
echo   Voice Input for Claude Code - Installer
echo   Created by Leon Li - 20260226
echo ============================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Found %PYVER%
echo.

:: Step 1: Install pip dependencies
echo [1/3] Installing Python dependencies...
echo       (If behind a proxy, set HTTPS_PROXY before running this script)
echo.

pip install faster-whisper sounddevice pynput numpy
if %errorlevel% neq 0 (
    echo.
    echo [FAIL] pip install failed. If behind a corporate proxy, try:
    echo   set HTTPS_PROXY=http://your-proxy:port
    echo   Then re-run this installer.
    echo.
    pause
    exit /b 1
)
echo.
echo [OK] Dependencies installed
echo.

:: Step 2: Copy files
echo [2/3] Copying files to ~/.claude/skills/voice/...

:: Create target directory
set "INSTALL_DIR=%USERPROFILE%\.claude\skills\voice"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy voice_input.py
copy /y "%~dp0voice_input.py" "%INSTALL_DIR%\voice_input.py" >nul
echo   voice_input.py  ->  %INSTALL_DIR%\

:: Copy SKILL.md
copy /y "%~dp0skill\SKILL.md" "%INSTALL_DIR%\SKILL.md" >nul
echo   SKILL.md        ->  %INSTALL_DIR%\

echo.
echo [OK] Files copied
echo.

:: Step 3: Verify
echo [3/3] Verifying installation...

if exist "%INSTALL_DIR%\voice_input.py" (
    echo   [OK] voice_input.py
) else (
    echo   [FAIL] voice_input.py not found
)

if exist "%INSTALL_DIR%\SKILL.md" (
    echo   [OK] SKILL.md
) else (
    echo   [FAIL] SKILL.md not found
)

python -c "from faster_whisper import WhisperModel; print('  [OK] faster-whisper')" 2>nul
if %errorlevel% neq 0 echo   [FAIL] faster-whisper import failed

echo.
echo ============================================
echo   Installation complete!
echo ============================================
echo.
echo   Usage in Claude Code:
echo     /voice        - Start voice input
echo     /voice stop   - Stop voice input
echo.
echo   How it works:
echo     Hold CapsLock to speak, release to auto-type.
echo     Say "stop voice" or "guan bi yu yin" to exit.
echo.
echo   Note: The Whisper model (~462MB) will download
echo         automatically on first use.
echo.
pause
