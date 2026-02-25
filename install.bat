@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================
echo   Voice Input for Claude Code - Installer
echo   Created by Leon Li(李岩) - 20260225
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
echo [1/5] Installing Python dependencies...
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
echo [2/5] Copying files...

:: Create target directories
if not exist "%USERPROFILE%\tools" mkdir "%USERPROFILE%\tools"
if not exist "%USERPROFILE%\tools\whisper-model" mkdir "%USERPROFILE%\tools\whisper-model"
if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
if not exist "%USERPROFILE%\.claude\skills" mkdir "%USERPROFILE%\.claude\skills"
if not exist "%USERPROFILE%\.claude\skills\voice" mkdir "%USERPROFILE%\.claude\skills\voice"

:: Copy voice_input.py
copy /y "%~dp0voice_input.py" "%USERPROFILE%\tools\voice_input.py" >nul
echo   voice_input.py  -^>  %USERPROFILE%\tools\

:: Copy SKILL.md (replace %USERPROFILE% placeholder with actual user path)
set "SKILL_SRC=%~dp0skill\SKILL.md"
set "SKILL_DST=%USERPROFILE%\.claude\skills\voice\SKILL.md"
set "UP=%USERPROFILE:\=/%"
powershell -Command "(Get-Content '%SKILL_SRC%') -replace '%%USERPROFILE%%', '%UP%' | Set-Content '%SKILL_DST%'"
echo   SKILL.md        -^>  %USERPROFILE%\.claude\skills\voice\

echo.
echo [OK] Files copied
echo.

:: Step 3: Download Whisper model
echo [3/5] Downloading Whisper Small model (~462MB)...
echo       This may take a few minutes depending on your network.
echo.

python -c "
import sys
try:
    from huggingface_hub import snapshot_download
    path = snapshot_download(
        'Systran/faster-whisper-small',
        local_dir=sys.argv[1],
        local_dir_use_symlinks=False,
    )
    print(f'  [OK] Model downloaded to {path}')
except Exception as e:
    print(f'  [FAIL] Download failed: {e}')
    print('  If behind a proxy, set HTTPS_PROXY and re-run.')
    sys.exit(1)
" "%USERPROFILE%\tools\whisper-model"
if %errorlevel% neq 0 (
    echo.
    echo [WARN] Model download failed. You can retry later:
    echo   set HTTPS_PROXY=http://your-proxy:port
    echo   python -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small', local_dir='%%USERPROFILE%%\tools\whisper-model', local_dir_use_symlinks=False)"
    echo.
)

:: Step 4: Configure Claude Code permissions
echo [4/5] Configuring Claude Code permissions...

python -c "
import json, os, sys
claude_dir = os.path.join(os.environ['USERPROFILE'], '.claude')
os.makedirs(claude_dir, exist_ok=True)
settings_path = os.path.join(claude_dir, 'settings.json')
settings = {}
if os.path.exists(settings_path):
    with open(settings_path, 'r', encoding='utf-8') as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            settings = {}
rules = [
    'Bash(*voice_input*)',
    'Bash(taskkill *pythonw*)',
]
perms = settings.setdefault('permissions', {})
allow = perms.setdefault('allow', [])
added = 0
for r in rules:
    if r not in allow:
        allow.append(r)
        added += 1
with open(settings_path, 'w', encoding='utf-8') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
print(f'  [OK] {added} permission rules added to settings.json')
"
if %errorlevel% neq 0 echo   [WARN] Failed to configure permissions, you may need to allow commands manually

echo.

:: Step 5: Verify
echo [5/5] Verifying installation...

if exist "%USERPROFILE%\tools\voice_input.py" (
    echo   [OK] voice_input.py
) else (
    echo   [FAIL] voice_input.py not found
)

if exist "%USERPROFILE%\tools\whisper-model\model.bin" (
    echo   [OK] whisper-model/model.bin
) else (
    echo   [FAIL] model.bin not found - run installer again with HTTPS_PROXY set
)

if exist "%USERPROFILE%\.claude\skills\voice\SKILL.md" (
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
echo     Hold Ctrl to speak, release to auto-type.
echo     Say "关闭语音" to exit.
echo.
pause
