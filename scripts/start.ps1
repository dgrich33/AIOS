param(
  [ValidateSet("Auto", "Docker", "Local")]
  [string]$Mode = "Auto"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RunDir = Join-Path $Root ".run"
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$BindingLoader = Join-Path $PSScriptRoot "runtime-binding-load-local.ps1"
if (Test-Path -LiteralPath $BindingLoader) {
  & $BindingLoader -Quiet | Out-Null
}

function Add-DockerToPathIfPresent {
  $dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
  if ((Get-Command docker -ErrorAction SilentlyContinue) -eq $null -and (Test-Path $dockerBin)) {
    $env:Path += ";$dockerBin"
  }
}

function Test-DockerReady {
  Add-DockerToPathIfPresent
  if ((Get-Command docker -ErrorAction SilentlyContinue) -eq $null) { return $false }
  try {
    docker --version | Out-Host
    docker compose version | Out-Host
    docker ps | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Ensure-Venv {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($null -eq $python) { throw "python nao encontrado no PATH" }
  $venvPython = Join-Path $Root ".venv\Scripts\python.exe"
  if (-not (Test-Path $venvPython)) {
    & $python.Source -m venv (Join-Path $Root ".venv")
  }
  & $venvPython -m pip install -r (Join-Path $Root "backend\requirements.txt") | Out-Host
  return $venvPython
}

function Start-Local {
  $venvPython = Ensure-Venv
  Push-Location (Join-Path $Root "frontend")
  npm install
  Pop-Location

  $backend = Start-Process -FilePath $venvPython -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory (Join-Path $Root "backend") -WindowStyle Hidden -PassThru
  Set-Content -Path (Join-Path $RunDir "backend.pid") -Value $backend.Id

  $frontendCommand = "npm run dev -- --host 127.0.0.1 --port 5173"
  $frontend = Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command",$frontendCommand -WorkingDirectory (Join-Path $Root "frontend") -WindowStyle Hidden -PassThru
  Set-Content -Path (Join-Path $RunDir "frontend.pid") -Value $frontend.Id

  Write-Host "Backend local:  http://127.0.0.1:8000"
  Write-Host "Frontend local: http://127.0.0.1:5173"
}

Push-Location $Root
try {
  $dockerReady = Test-DockerReady
  if (($Mode -eq "Docker") -and (-not $dockerReady)) {
    throw "Docker nao esta pronto. Abra o Docker Desktop ou use -Mode Local."
  }
  if ($dockerReady -and $Mode -ne "Local") {
    docker compose up -d --build
    docker compose ps
  } else {
    Write-Warning "Docker nao disponivel; iniciando fallback local."
    Start-Local
  }
} finally {
  Pop-Location
}
