$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Frontend = Join-Path $Root "frontend"
$Backend = Join-Path $Root "backend"
$Release = Join-Path $Root "release"
$Py = Join-Path $Backend ".venv\Scripts\python.exe"

if (-not (Test-Path $Py)) {
    throw "Backend venv not found. Run: cd backend; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

Write-Host "==> Building frontend..."
Push-Location $Frontend
npm run build
Pop-Location

Write-Host "==> Installing PyInstaller..."
& $Py -m pip install pyinstaller

Write-Host "==> Packaging game..."
Push-Location $Backend
& $Py -m PyInstaller --noconfirm --clean --onefile --name CapitalMarketSim `
    --add-data "$Frontend\dist;frontend_dist" `
    --add-data "$Backend\app\data\a_share_snapshot.json;app\data" `
    --hidden-import uvicorn.logging `
    --hidden-import uvicorn.loops.auto `
    --hidden-import uvicorn.protocols.http.auto `
    --hidden-import uvicorn.protocols.websockets.auto `
    --hidden-import uvicorn.lifespan.on `
    --hidden-import uvicorn.lifespan.off `
    --hidden-import sqlalchemy.dialects.sqlite `
    run.py
Pop-Location

New-Item -ItemType Directory -Force -Path $Release | Out-Null
$Exe = Join-Path $Backend "dist\CapitalMarketSim.exe"
Copy-Item $Exe $Release -Force

$Readme = @"
Capital Market Simulator
=======================

How to play:
1. Double-click CapitalMarketSim.exe.
2. Your browser opens http://127.0.0.1:8000 automatically.
3. Close the black console window to exit the game.

Play with friends (same Wi-Fi/LAN):
1. The console prints a LAN address like http://192.168.1.5:8000.
2. Friends open that address in their browser and register an account.
3. The first registered player is the host and controls time. The default host
   account is: host / 123456

Save data is stored in the data folder next to the exe.
"@
Set-Content -Path (Join-Path $Release "README.txt") -Value $Readme -Encoding UTF8

Compress-Archive -Path (Join-Path $Release "CapitalMarketSim.exe"), (Join-Path $Release "README.txt") -DestinationPath (Join-Path $Release "CapitalMarketSim.zip") -Force

Write-Host "Package ready: $Release\CapitalMarketSim.zip"
