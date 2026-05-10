$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

function Add-DockerToPathIfPresent {
  $dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
  if ((Get-Command docker -ErrorAction SilentlyContinue) -eq $null -and (Test-Path (Join-Path $dockerBin "docker.exe"))) {
    $env:Path += ";$dockerBin"
  }
}

function Wait-Http($Url, $Seconds = 90) {
  for ($i = 0; $i -lt $Seconds; $i++) {
    try {
      return Invoke-RestMethod -Uri $Url -TimeoutSec 2
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  throw "Timeout aguardando $Url"
}

Write-Host "AIOS Codex Unlimited RC1 - Start Docker"
Add-DockerToPathIfPresent
if ((Get-Command docker -ErrorAction SilentlyContinue) -eq $null) {
  throw "Docker nao encontrado. Use .\scripts\rc1-start-local.ps1"
}

try {
  docker ps | Out-Null
} catch {
  throw "Docker daemon nao respondeu. Abra Docker Desktop ou use .\scripts\rc1-start-local.ps1"
}

Push-Location $Root
try {
  docker compose up -d --build
  docker compose ps
  Wait-Http "http://127.0.0.1:8000/health" | Out-Host
  Start-Process "http://127.0.0.1:5173"
  Start-Process "http://127.0.0.1:8000/docs"
  Start-Process "http://127.0.0.1:3001"
} catch {
  Write-Host "Docker RC1 falhou: $($_.Exception.Message)"
  Write-Host "Fallback recomendado: .\scripts\rc1-start-local.ps1"
  throw
} finally {
  Pop-Location
}

