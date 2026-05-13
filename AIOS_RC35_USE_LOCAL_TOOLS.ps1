$tools = Join-Path $PSScriptRoot ".tools\bin"
if (-not (Test-Path $tools)) {
  throw "Ferramentas locais nao encontradas em $tools. Rode o instalador local novamente."
}

$env:PATH = "$tools;$env:PATH"
Write-Host "AIOS local tools no PATH: $tools" -ForegroundColor Green
kubectl version --client=true
kustomize version
