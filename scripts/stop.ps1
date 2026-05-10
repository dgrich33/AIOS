$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RunDir = Join-Path $Root ".run"

function Add-DockerToPathIfPresent {
  $dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
  if ((Get-Command docker -ErrorAction SilentlyContinue) -eq $null -and (Test-Path $dockerBin)) {
    $env:Path += ";$dockerBin"
  }
}

function Stop-PidFile($Name) {
  $pidFile = Join-Path $RunDir "$Name.pid"
  if (-not (Test-Path $pidFile)) { return }
  $pidValue = (Get-Content $pidFile -Raw).Trim()
  if ($pidValue -match '^\d+$') {
    $process = Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue
    if ($process) {
      $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $pidValue" -ErrorAction SilentlyContinue).CommandLine
      $isTrackedProcess = $cmd -and (
        $cmd.Contains($Root.Path) -or
        ($Name -eq "frontend" -and $cmd.Contains("npm run dev")) -or
        ($Name -eq "backend" -and $cmd.Contains("uvicorn app.main:app"))
      )
      if ($isTrackedProcess) {
        Stop-Process -Id ([int]$pidValue) -Force
        Write-Host "Parado: $Name PID $pidValue"
      } else {
        Write-Warning "PID $pidValue nao parece pertencer a este projeto; ignorado."
      }
    }
  }
  Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
}

function Stop-ProjectProcessOnPort($Port) {
  $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  foreach ($connection in $connections) {
    $pidValue = [int]$connection.OwningProcess
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $pidValue" -ErrorAction SilentlyContinue).CommandLine
    $isProjectProcess = $cmd -and (
      $cmd.Contains($Root.Path) -or
      ($Port -eq 8000 -and $cmd.Contains("uvicorn app.main:app")) -or
      ($Port -eq 5173 -and $cmd.Contains("vite.js"))
    )
    if ($isProjectProcess) {
      Stop-Process -Id $pidValue -Force
      Write-Host "Parado processo do projeto na porta $Port PID $pidValue"
    }
  }
}

Add-DockerToPathIfPresent
if (Get-Command docker -ErrorAction SilentlyContinue) {
  try {
    Push-Location $Root
    docker compose down
  } catch {
    Write-Warning "docker compose down falhou ou Docker nao esta ativo: $($_.Exception.Message)"
  } finally {
    Pop-Location
  }
}

Stop-PidFile "backend"
Stop-PidFile "frontend"
Stop-ProjectProcessOnPort 8000
Stop-ProjectProcessOnPort 5173
Write-Host "Stop concluido."
