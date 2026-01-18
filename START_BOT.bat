@echo off
setlocal
echo ==========================================
echo   DailyNewsBot Sovereign Server Setup
echo ==========================================
echo.

REM 1. Add Node to PATH
set "PATH=%PATH%;C:\Program Files\nodejs"
set "NODE_FUNCTION_ALLOW_EXTERNAL=*"

REM 2. Check for local n8n installation
if exist "node_modules\.bin\n8n.cmd" (
    echo [OK] n8n is installed locally.
) else (
    echo [!] n8n not found locally. Installing now...
    echo     This will take 2-3 minutes. Please wait.
    call npm install n8n
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERROR] Installation failed.
        pause
        exit /b
    )
    echo [OK] Installation complete.
)

REM 3. Run n8n
echo.
echo [Running] Starting n8n server...
echo          Look for the "Tunnel URL" below.
echo.

call ".\node_modules\.bin\n8n" start --tunnel

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] n8n crashed.
    pause
)
pause
