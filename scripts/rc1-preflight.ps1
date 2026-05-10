$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

function Add-DockerToPathIfPresent {
  $dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
  if ((Get-Command docker -ErrorAction SilentlyContinue) -eq $null -and (Test-Path (Join-Path $dockerBin "docker.exe"))) {
    $env:Path += ";$dockerBin"
  }
}

function Test-Tool($Name, $Required = $true) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -eq $cmd) {
    $level = if ($Required) { "ERRO" } else { "AVISO" }
    Write-Host "${level}: $Name nao encontrado no PATH"
    return $false
  }
  Write-Host "OK: $Name encontrado em $($cmd.Source)"
  return $true
}

function Show-PortStatus($Port) {
  $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  if (-not $connections) {
    Write-Host "OK: porta $Port livre"
    return
  }
  foreach ($connection in $connections) {
    $pidValue = [int]$connection.OwningProcess
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $pidValue" -ErrorAction SilentlyContinue).CommandLine
    $owned = $cmd -and ($cmd.Contains($Root.Path) -or $cmd.Contains("uvicorn app.main:app") -or $cmd.Contains("vite.js"))
    $label = if ($owned) { "processo do projeto" } else { "processo externo" }
    Write-Host "AVISO: porta $Port ocupada por PID $pidValue ($label)"
  }
}

Write-Host "AIOS Codex Unlimited RC1 - Preflight"
Write-Host "Projeto: $($Root.Path)"
Write-Host "PowerShell: $($PSVersionTable.PSVersion)"

$ok = $true
$ok = (Test-Tool "python") -and $ok
$ok = (Test-Tool "node") -and $ok
$ok = (Test-Tool "npm") -and $ok
$ok = (Test-Tool "git") -and $ok

Add-DockerToPathIfPresent
$dockerOk = Test-Tool "docker" $false
if ($dockerOk) {
  try {
    docker --version | Out-Host
    docker compose version | Out-Host
    docker ps | Out-Null
    Write-Host "OK: Docker daemon respondendo"
  } catch {
    Write-Host "AVISO: Docker existe, mas o daemon nao respondeu. Use modo local ou abra Docker Desktop."
  }
} else {
  Write-Host 'AVISO: Docker indisponivel. Modo Local RC1 continua suportado.'
  Write-Host 'Dica: $env:Path += ";C:\Program Files\Docker\Docker\resources\bin"'
}

Show-PortStatus 8000
Show-PortStatus 5173

if (-not $ok) {
  throw "Preflight falhou: ferramenta obrigatoria ausente."
}

Write-Host "Preflight RC1 concluido."
