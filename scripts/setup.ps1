$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot

if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".venv\Scripts\python.exe" -m pip install -e "backend[dev]"
& ".venv\Scripts\python.exe" -m alembic -c "backend\alembic.ini" upgrade head
Push-Location frontend
npm install
Pop-Location
Write-Host "FraudLens configurado. Execute o pipeline antes de iniciar as aplicações."

