param(
  [switch]$InstallTools,
  [switch]$PullOllamaModel
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Ensure-Command {
  param(
    [string]$Name,
    [string]$WingetId,
    [switch]$OptionalInstall
  )
  if (Get-Command $Name -ErrorAction SilentlyContinue) {
    Write-Host "$Name encontrado." -ForegroundColor Green
    return
  }
  if (-not $OptionalInstall) {
    Write-Warning "$Name nao encontrado. Rode com -InstallTools para instalar via winget, ou instale manualmente."
    return
  }
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget nao encontrado. Instale $Name manualmente."
  }
  Write-Host "Instalando $Name via winget..." -ForegroundColor Yellow
  winget install --id $WingetId --silent --accept-package-agreements --accept-source-agreements
}

Write-Host "AIOS Codex Unlimited RC13 - instalador assistido" -ForegroundColor Cyan
Write-Host "Raiz: $Root"

Ensure-Command -Name "python" -WingetId "Python.Python.3.11" -OptionalInstall:$InstallTools
Ensure-Command -Name "node" -WingetId "OpenJS.NodeJS.LTS" -OptionalInstall:$InstallTools
Ensure-Command -Name "npm" -WingetId "OpenJS.NodeJS.LTS" -OptionalInstall:$InstallTools
Ensure-Command -Name "ollama" -WingetId "Ollama.Ollama" -OptionalInstall:$InstallTools

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Push-Location $Root
try {
  if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
  }
  .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt

  Push-Location .\frontend
  npm install
  Pop-Location

  Push-Location .\mcp\aios-mcp-core
  npm install
  npm run build
  Pop-Location

  Push-Location .\mcp\aios-mcp-repo
  npm install
  npm run build
  Pop-Location

  .\.venv\Scripts\python.exe .\scripts\generate_license.py

  if ($PullOllamaModel) {
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
      Write-Warning "Ollama nao encontrado; pulando pull do modelo."
    } else {
      Write-Host "Baixando/preparando deepseek-v4-pro:cloud no Ollama..." -ForegroundColor Yellow
      ollama pull deepseek-v4-pro:cloud
    }
  }

  Write-Host ""
  Write-Host "Ambiente preparado." -ForegroundColor Green
  Write-Host "Iniciar demo: .\scripts\start_demo.ps1"
  Write-Host "Backend: http://127.0.0.1:8000/docs"
  Write-Host "Frontend: http://127.0.0.1:5173"
} finally {
  Pop-Location
}
