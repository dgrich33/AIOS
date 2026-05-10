$ErrorActionPreference = "Stop"

Write-Host "AIOS Codex Unlimited RC1 - Demo Launcher"
& "$PSScriptRoot\rc1-preflight.ps1"

$dockerReady = $false
try {
  docker ps | Out-Null
  $dockerReady = $true
} catch {
  $dockerReady = $false
}

if ($dockerReady) {
  try {
    & "$PSScriptRoot\rc1-start-docker.ps1"
  } catch {
    Write-Warning "Docker falhou. Usando modo local."
    & "$PSScriptRoot\rc1-start-local.ps1"
  }
} else {
  & "$PSScriptRoot\rc1-start-local.ps1"
}

& "$PSScriptRoot\rc1-validate.ps1"

Start-Process "http://127.0.0.1:5173"
Start-Process "http://127.0.0.1:8000/docs"

Write-Host ""
Write-Host "Roteiro rapido:"
Write-Host "1. Login: admin@aios.local / AiosAdmin123!"
Write-Host "2. Mostrar que a unidade do produto e codex_sessions."
Write-Host "3. Criar Nova sessao."
Write-Host "4. Clicar Snapshot, Handoff e Simular evento MCP."
Write-Host "5. Mostrar Eventos recentes, MCP/logs, Arquivos e build."
Write-Host "6. Abrir API Docs e mostrar /workbench, /events, /adapter/info."

