@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Yirra Care Agents -- Windows Build

echo.
echo  ====================================================
echo    Yirra Care Agents -- Windows Build
echo  ====================================================
echo.
echo  NOTE: This script must be run on a Windows machine.
echo  It will produce:  dist\YirraCareAgents\YirraCareAgents.exe
echo.

REM ── 1. Activate venv ──────────────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] .venv not found.
    echo         Run: python -m venv .venv
    echo              pip install -r requirements.txt
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM ── 2. Install PyInstaller ────────────────────────────────────
echo Installing PyInstaller...
pip install pyinstaller --quiet --upgrade
pip install streamlit --quiet
echo [OK] PyInstaller and Streamlit ready

REM ── 3. Clean previous builds ──────────────────────────────────
echo Cleaning previous builds...
if exist build     rmdir /s /q build
if exist dist      rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM ── 4. Build ──────────────────────────────────────────────────
echo.
echo Building Windows executable (this takes 5-10 minutes)...
echo.
pyinstaller yirra_care_windows.spec --noconfirm --clean

REM ── 5. Copy user data files ───────────────────────────────────
set DIST=dist\YirraCareAgents
echo.
echo Copying data files...

if not exist "%DIST%\data"    mkdir "%DIST%\data"
if not exist "%DIST%\exports" mkdir "%DIST%\exports"

if exist ".env" (
    copy ".env" "%DIST%\.env" >nul
    echo   [OK] .env
) else (
    echo   [!] No .env found -- user must configure API keys after install
)

if exist "client_secret.json" (
    copy "client_secret.json" "%DIST%\client_secret.json" >nul
    echo   [OK] client_secret.json
)

if exist "data\yirra_referrals.sqlite" (
    copy "data\yirra_referrals.sqlite" "%DIST%\data\" >nul
    echo   [OK] database
)

if exist "data\campaigns.json" (
    copy "data\campaigns.json" "%DIST%\data\" >nul
    echo   [OK] campaigns.json
)

REM ── 6. Done ───────────────────────────────────────────────────
echo.
echo  ====================================================
echo    Build complete!
echo  ====================================================
echo.
echo   Folder:  dist\YirraCareAgents\
echo   Exe:     dist\YirraCareAgents\YirraCareAgents.exe
echo.
echo   To distribute: zip the dist\YirraCareAgents\ folder
echo   To test now:   double-click dist\YirraCareAgents\YirraCareAgents.exe
echo.
pause
