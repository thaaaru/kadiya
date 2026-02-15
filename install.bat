@echo off
:: ============================================================================
:: kadiya Windows Installer
::
:: Double-click this file or run from cmd/PowerShell.
:: After install, kadiya is available from any terminal.
:: ============================================================================

title kadiya installer

echo.
echo   kadiya installer - launching...
echo.

:: Get the directory this batch file lives in
set "SCRIPT_DIR=%~dp0"

:: Check if install.ps1 exists next to this file
if not exist "%SCRIPT_DIR%install.ps1" (
    echo   [FAIL] install.ps1 not found in %SCRIPT_DIR%
    echo   Make sure install.bat and install.ps1 are in the same folder.
    echo.
    pause
    exit /b 1
)

:: Launch PowerShell installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install.ps1"

if %ERRORLEVEL% equ 9009 (
    echo   [info] powershell.exe not found, trying pwsh...
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install.ps1"
)

exit /b %ERRORLEVEL%
