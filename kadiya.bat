@echo off
:: ============================================================================
:: kadiya launcher
::
:: Double-click or run from any terminal to start kadiya.
:: Activates the virtual environment and runs the agent.
::
:: Usage:
::   kadiya.bat                     (interactive mode)
::   kadiya.bat -m "Hello"          (single message)
::   kadiya.bat doctor              (run diagnostics)
::   kadiya.bat status              (show status)
::   kadiya.bat onboard             (re-run setup)
:: ============================================================================

title kadiya

:: Get the directory this batch file lives in
set "KADIYA_DIR=%~dp0"

:: Check venv exists
if not exist "%KADIYA_DIR%.venv\Scripts\activate.bat" (
    echo.
    echo   kadiya is not installed yet.
    echo   Run install.bat first.
    echo.
    pause
    exit /b 1
)

:: Activate venv
call "%KADIYA_DIR%.venv\Scripts\activate.bat"

:: If arguments were passed, run kadiya with those args
:: Otherwise, start interactive agent mode
:: Use full path to kadiya.exe to avoid recursion (this file is also named kadiya)
if "%~1"=="" (
    "%KADIYA_DIR%.venv\Scripts\kadiya.exe" agent
) else (
    "%KADIYA_DIR%.venv\Scripts\kadiya.exe" %*
)
