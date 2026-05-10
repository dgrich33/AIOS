$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Write-Host "AIOS Codex Unlimited RC3 - Windows App Launcher"
Write-Host "Root: $Root"

& "$PSScriptRoot\rc1-start-local.ps1"

Write-Host ""
Write-Host "AIOS Codex Unlimited RC3 pronto:"
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "API Docs: http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "Este pacote nao inclui binarios privados, checkpoints, pesos de modelo ou auth.json do Codex."

