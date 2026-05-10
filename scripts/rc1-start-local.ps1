$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Logs = Join-Path $Root "logs"
$RunDir = Join-Path $Root ".run"
New-Item -ItemType Directory -Force -Path $Logs,$RunDir | Out-Null

function Wait-Http($Url, $Seconds = 45) {
  for ($i = 0; $i -lt $Seconds; $i++) {
    try {
      $response = Invoke-RestMethod -Uri $Url -TimeoutSec 2
      return $response
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  throw "Timeout aguardando $Url"
}

Write-Host "AIOS Codex Unlimited RC1 - Start Local"
& "$PSScriptRoot\stop.ps1"

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  python -m venv (Join-Path $Root ".venv")
}
& $venvPython -m pip install -r (Join-Path $Root "backend\requirements.txt") | Out-Host

Push-Location (Join-Path $Root "frontend")
npm install | Out-Host
Pop-Location

$backendOutLog = Join-Path $Logs "rc1-backend.out.log"
$backendErrLog = Join-Path $Logs "rc1-backend.err.log"
$frontendOutLog = Join-Path $Logs "rc1-frontend.out.log"
$frontendErrLog = Join-Path $Logs "rc1-frontend.err.log"

$backend = Start-Process -FilePath $venvPython -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory (Join-Path $Root "backend") -RedirectStandardOutput $backendOutLog -RedirectStandardError $backendErrLog -WindowStyle Hidden -PassThru
Set-Content -Path (Join-Path $RunDir "backend.pid") -Value $backend.Id

$frontendCommand = "npm run dev -- --host 127.0.0.1 --port 5173"
$frontend = Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command",$frontendCommand -WorkingDirectory (Join-Path $Root "frontend") -RedirectStandardOutput $frontendOutLog -RedirectStandardError $frontendErrLog -WindowStyle Hidden -PassThru
Set-Content -Path (Join-Path $RunDir "frontend.pid") -Value $frontend.Id

Wait-Http "http://127.0.0.1:8000/health" | Out-Host
Wait-Http "http://127.0.0.1:5173" | Out-Null

Start-Process "http://127.0.0.1:5173"
Start-Process "http://127.0.0.1:8000/docs"

Write-Host "RC1 local rodando:"
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Docs:     http://127.0.0.1:8000/docs"
Write-Host "Logs:     $Logs"
