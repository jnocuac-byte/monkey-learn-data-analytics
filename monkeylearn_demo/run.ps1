# Abre la pagina interactiva en Windows PowerShell:  .\run.ps1
# Para generar solo el reporte estatico:             .\run.ps1 -Reporte
param([switch]$Reporte)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv no esta instalado. Instalando..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "Listo. CIERRA esta terminal, abre una nueva y ejecuta de nuevo: .\run.ps1" -ForegroundColor Green
    exit
}

uv sync
if ($Reporte) {
    uv run python main.py --abrir
} else {
    uv run python web.py
}
