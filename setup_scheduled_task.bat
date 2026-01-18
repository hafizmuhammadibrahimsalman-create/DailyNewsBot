@echo off
REM ============================================================
REM DailyNewsBot - Windows Scheduled Task Setup
REM ============================================================
REM Run this as Administrator to set up daily automation
REM ============================================================

echo.
echo ========================================
echo  DailyNewsBot Task Scheduler Setup
echo ========================================
echo.

REM Get the current directory
set "BOT_DIR=%~dp0"
set "PYTHON_SCRIPT=%BOT_DIR%run_automation.py"
set "TASK_NAME=DailyNewsBot_Evening"

echo Bot Directory: %BOT_DIR%
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Create the scheduled task for 9 PM daily
echo Creating scheduled task for 9:00 PM daily...
schtasks /create /tn "%TASK_NAME%" /tr "python \"%PYTHON_SCRIPT%\" --run" /sc daily /st 21:00 /f

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Task Created
    echo ========================================
    echo.
    echo Task Name: %TASK_NAME%
    echo Schedule: Daily at 9:00 PM
    echo Action: Run DailyNewsBot automation
    echo.
    echo To manage this task:
    echo   View: schtasks /query /tn "%TASK_NAME%"
    echo   Run now: schtasks /run /tn "%TASK_NAME%"
    echo   Delete: schtasks /delete /tn "%TASK_NAME%" /f
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task
    echo.
)

pause
