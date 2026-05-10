$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Push-Location $Root
try {
  & "$PSScriptRoot\contract-authority.ps1" verify | Out-Host
  if (-not (Test-Path ".\license.cert")) {
    if (Test-Path ".\.venv\Scripts\python.exe") {
      .\.venv\Scripts\python.exe .\scripts\generate_license.py
    } else {
      python .\scripts\generate_license.py
    }
  }
  & "$PSScriptRoot\start.ps1" -Mode Local
  Start-Sleep -Seconds 5
  Start-Process "http://127.0.0.1:5173"
  Start-Process "http://127.0.0.1:8000/docs"
  Write-Host "Demo local iniciada." -ForegroundColor Green
} finally {
  Pop-Location
}
