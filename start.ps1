$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Py = Join-Path $Backend ".venv\Scripts\python.exe"
$DistIndex = Join-Path $Frontend "dist\index.html"

if (-not (Test-Path $Py)) {
    Write-Host "==> Creating backend environment..."
    $Launcher = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }
    Push-Location $Backend
    if ($Launcher -eq "py") {
        & py -3 -m venv .venv
    } else {
        & python -m venv .venv
    }
    & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
    Pop-Location
}

if (-not (Test-Path $DistIndex)) {
    Write-Host "==> Building frontend..."
    Push-Location $Frontend
    if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
        npm ci
    }
    npm run build
    Pop-Location
}

Write-Host ""
Write-Host "==> Capital Market Simulator is starting..."
Write-Host "    The browser will open at http://127.0.0.1:8000"
Write-Host "    Close this window or press Ctrl+C to stop the game."
Write-Host ""

& $Py (Join-Path $Backend "run.py")
