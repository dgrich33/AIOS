$tools = Join-Path $PSScriptRoot ".tools\bin"
if (-not (Test-Path $tools)) {
  throw "Ferramentas locais nao encontradas em $tools. Rode o instalador local novamente."
}

$extraToolPaths = @(
  $tools,
  "C:\Program Files\Amazon\AWSCLIV2",
  "C:\Program Files (x86)\GnuWin32\bin"
) | Where-Object { Test-Path $_ }

$env:PATH = (($extraToolPaths + @($env:PATH)) -join ";")
Write-Host "AIOS local tools no PATH: $tools" -ForegroundColor Green
kubectl version --client=true
kustomize version
if (Get-Command aws -ErrorAction SilentlyContinue) {
  aws --version
} else {
  Write-Host "AWS CLI nao encontrado no PATH desta sessao." -ForegroundColor Yellow
}
if (Get-Command make -ErrorAction SilentlyContinue) {
  make -v | Select-Object -First 1
} else {
  Write-Host "GNU Make nao encontrado no PATH desta sessao." -ForegroundColor Yellow
}
