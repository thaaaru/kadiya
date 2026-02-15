# ============================================================================
# kadiya Windows Installer (Native)
#
# Installs kadiya directly on Windows without WSL.
#   1. Install Python 3.12 (via winget, if needed)
#   2. Create virtual environment
#   3. Install dependencies
#   4. Run guided setup (kadiya onboard)
#
# Usage:
#   install.bat                                        (double-click or cmd)
#   powershell -ExecutionPolicy Bypass -File install.ps1  (from PowerShell)
# ============================================================================

$ErrorActionPreference = "Stop"

# --- Ensure UTF-8 output so Unicode symbols display correctly ---------------
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 2>&1 | Out-Null

# --- Enable ANSI escape sequences so colors render properly ----------------
try {
    Add-Type -MemberDefinition @"
[DllImport("kernel32.dll", SetLastError = true)]
public static extern IntPtr GetStdHandle(int nStdHandle);
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool GetConsoleMode(IntPtr hConsoleHandle, out uint lpMode);
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool SetConsoleMode(IntPtr hConsoleHandle, uint dwMode);
"@ -Namespace Win32 -Name NativeMethods -ErrorAction SilentlyContinue

    $handle = [Win32.NativeMethods]::GetStdHandle(-11)
    $mode = [uint32]0
    [Win32.NativeMethods]::GetConsoleMode($handle, [ref]$mode) | Out-Null
    $mode = $mode -bor 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    [Win32.NativeMethods]::SetConsoleMode($handle, $mode) | Out-Null
} catch {}

# --- Colors / Helpers -------------------------------------------------------
function Write-Step($msg)  { Write-Host "`n> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "  [ok]  $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "  [warn] $msg" -ForegroundColor Yellow }
function Write-Fail($msg)  { Write-Host "  [FAIL] $msg" -ForegroundColor Red; exit 1 }
function Write-Info($msg)  { Write-Host "  [info] $msg" -ForegroundColor Blue }

# --- Banner -----------------------------------------------------------------
Write-Host ""
Write-Host "  kadiya installer (Windows)" -ForegroundColor Cyan
Write-Host "  Personal AI assistant for Sri Lanka" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Supported providers:" -ForegroundColor DarkGray
Write-Host "    DeepSeek, OpenAI, Anthropic, Groq, Gemini, OpenRouter" -ForegroundColor DarkGray
Write-Host "  Just paste your API key - kadiya detects the provider." -ForegroundColor DarkGray
Write-Host ""

# ============================================================================
# 1. CHECK / INSTALL PYTHON
# ============================================================================
Write-Step "Checking Python"

$pythonExe = $null

# Check common Python install locations
$candidates = @(
    "python",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe"
)

foreach ($candidate in $candidates) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3\.1[1-9]|Python 3\.[2-9][0-9]") {
            $pythonExe = $candidate
            Write-Ok "Python found: $ver"
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonExe) {
    Write-Info "Python 3.11+ not found. Installing Python 3.12..."

    # Check for winget
    $hasWinget = $false
    try {
        winget --version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $hasWinget = $true }
    } catch {}

    if ($hasWinget) {
        Write-Info "Installing via winget..."
        winget install Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements 2>&1 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor DarkGray
        }

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        # Try to find newly installed Python
        $newPython = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
        if (Test-Path $newPython) {
            $pythonExe = $newPython
            Write-Ok "Python 3.12 installed"
        } else {
            # Try generic python command after PATH refresh
            try {
                $ver = & python --version 2>&1
                if ($ver -match "Python 3\.1[1-9]") {
                    $pythonExe = "python"
                    Write-Ok "Python installed: $ver"
                }
            } catch {}
        }
    }

    if (-not $pythonExe) {
        Write-Host ""
        Write-Host "  Python 3.12 could not be installed automatically." -ForegroundColor Yellow
        Write-Host "  Please install it manually from:" -ForegroundColor Yellow
        Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
        Write-Host ""
        Write-Fail "Python 3.11+ is required."
    }
}

# ============================================================================
# 2. CREATE VIRTUAL ENVIRONMENT
# ============================================================================
Write-Step "Setting up Python environment"

# Determine project directory (where this script lives)
# When piped via `irm | iex`, $MyInvocation.MyCommand.Path is null,
# so clone the repo to a local directory first.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) {
    $installDir = Join-Path $env:USERPROFILE "kadiya"
    if (Test-Path (Join-Path $installDir "pyproject.toml")) {
        Write-Info "Existing kadiya found at $installDir, pulling latest..."
        git -C $installDir pull -q 2>&1 | Out-Null
    } else {
        Write-Info "Cloning kadiya to $installDir..."
        git clone -q https://github.com/thaaaru/kadiya.git $installDir
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Failed to clone kadiya. Make sure git is installed."
        }
    }
    $scriptDir = $installDir
}

$venvDir = Join-Path $scriptDir ".venv"

if (Test-Path (Join-Path $venvDir "Scripts\python.exe")) {
    Write-Ok "Virtual environment exists"
} else {
    Write-Info "Creating virtual environment..."
    & $pythonExe -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to create virtual environment"
    }
    Write-Ok "Virtual environment created"
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"

# ============================================================================
# 3. INSTALL DEPENDENCIES
# ============================================================================
Write-Step "Installing dependencies"

Write-Info "Upgrading pip..."
$ErrorActionPreference = "Continue"
& $venvPython -m pip install --upgrade pip -q 2>&1 | Out-Null
$ErrorActionPreference = "Stop"

Write-Info "Installing kadiya..."
$ErrorActionPreference = "Continue"
& $venvPip install -e $scriptDir -q 2>&1 | ForEach-Object {
    $line = $_.ToString()
    if ($line -match "error|Error|ERROR" -and $line -notmatch "WARNING") {
        Write-Host "  $line" -ForegroundColor Red
    }
}
$pipExit = $LASTEXITCODE
$ErrorActionPreference = "Stop"

if ($pipExit -ne 0) {
    Write-Fail "Failed to install dependencies. Check the output above."
}

# Install optional kadiya dependencies
Write-Info "Installing optional packages..."
$ErrorActionPreference = "Continue"
& $venvPip install pyyaml openpyxl python-docx python-pptx -q 2>&1 | Out-Null
$ErrorActionPreference = "Stop"

Write-Ok "All dependencies installed"

# ============================================================================
# 4. RUN GUIDED SETUP (kadiya onboard)
# ============================================================================
Write-Step "Starting guided setup"

$kadiyaExe = Join-Path $venvDir "Scripts\kadiya.exe"

if (Test-Path $kadiyaExe) {
    Write-Host ""
    Write-Host "  ----------------------------------------" -ForegroundColor DarkGray
    Write-Host "  Running kadiya setup..." -ForegroundColor DarkGray
    Write-Host "  ----------------------------------------" -ForegroundColor DarkGray
    Write-Host ""

    & $kadiyaExe onboard
    $setupExit = $LASTEXITCODE
} else {
    Write-Warn "kadiya CLI not found. You can run setup manually:"
    Write-Host "  $venvDir\Scripts\activate" -ForegroundColor Cyan
    Write-Host "  kadiya onboard" -ForegroundColor Cyan
    $setupExit = 1
}

# ============================================================================
# 5. ADD TO PATH
# ============================================================================
Write-Step "Adding kadiya to PATH"

$scriptsDir = Join-Path $venvDir "Scripts"
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")

if ($userPath -and $userPath.Split(";") -contains $scriptsDir) {
    Write-Ok "kadiya already in PATH"
} else {
    $newPath = if ($userPath) { "$userPath;$scriptsDir" } else { $scriptsDir }
    [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    # Also update current session so it works immediately
    $env:Path = "$env:Path;$scriptsDir"
    Write-Ok "Added kadiya to PATH"
}

# ============================================================================
# 6. DONE
# ============================================================================
Write-Host ""

if ($setupExit -eq 0) {
    Write-Host "  kadiya installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  Installation complete (setup had warnings)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Open any terminal and run:" -ForegroundColor White
Write-Host ""
Write-Host '    kadiya agent -m "Hello!"' -ForegroundColor Cyan
Write-Host "    kadiya agent                 (interactive)" -ForegroundColor Cyan
Write-Host "    kadiya doctor                (diagnostics)" -ForegroundColor Cyan
Write-Host ""

Write-Host "  Press any key to exit..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
