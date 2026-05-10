$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC12_RUNTIME_BROKER_READINESS_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -LiteralPath $Report -Value $Text
}

function Invoke-AiosJson {
  param(
    [string]$Uri,
    [string]$Method = "GET",
    [hashtable]$Headers = @{},
    [object]$Body = $null
  )
  $params = @{ Uri = $Uri; Method = $Method; Headers = $Headers }
  if ($null -ne $Body) {
    $params.ContentType = "application/json"
    $params.Body = ($Body | ConvertTo-Json -Depth 20)
  }
  Invoke-RestMethod @params
}

function Get-ErrorBody($ErrorRecord) {
  if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) { return $ErrorRecord.ErrorDetails.Message }
  try {
    $stream = $ErrorRecord.Exception.Response.GetResponseStream()
    if (-not $stream) { return $ErrorRecord.Exception.Message }
    $reader = [System.IO.StreamReader]::new($stream)
    return $reader.ReadToEnd()
  } catch {
    return $ErrorRecord.Exception.Message
  }
}

Set-Content -LiteralPath $Report -Value "# AIOS Codex Unlimited RC12 - Runtime Broker Readiness`n"
Add-Line "- Data: $(Get-Date -Format o)"
Add-Line "- Base local: $Base"
$targetModel = $env:AIOS_OLLAMA_MODEL
if (-not $targetModel) { $targetModel = "deepseek-v4-pro:cloud" }
Add-Line "- Modelo Ollama alvo: $targetModel"
Add-Line "- API key OpenAI impressa: Nao"
Add-Line ""

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host
& "$PSScriptRoot\contract-docs-audit.ps1" | Out-Host

try {
  $health = Invoke-RestMethod "$Base/health"
} catch {
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: API_NOT_RUNNING"
  Add-Line "- Acao: execute .\scripts\start.ps1 -Mode Local e rode este script novamente."
  Get-Content -LiteralPath $Report
  exit 0
}

$login = Invoke-AiosJson -Uri "$Base/auth/login" -Method Post -Body @{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
}
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$providers = Invoke-AiosJson -Uri "$Base/runtime/broker/providers" -Headers $headers
$status = Invoke-AiosJson -Uri "$Base/runtime/broker/status" -Headers $headers

Add-Line "## Backend"
Add-Line ""
Add-Line "- Health: $($health.status)"
Add-Line "- Broker phase: $($status.phase)"
Add-Line "- Recommended provider: $($status.recommendedProvider)"
Add-Line "- Product unit: $($status.productUnit)"
Add-Line "- Secrets exposed: $($status.secretsExposed)"
Add-Line "- Token counter visible: $($status.showsTokenCounter)"
Add-Line ""
Add-Line "## Providers"
Add-Line ""
foreach ($provider in $providers.providers) {
  Add-Line "- $($provider.providerId): $($provider.status), model=$($provider.defaultModel), devApiKey=$($provider.requiresDeveloperApiKey)"
}

$ollama = $status.providers.ollama_local_cloud
Add-Line ""
Add-Line "## Ollama Local/Cloud"
Add-Line ""
Add-Line "- Available: $($ollama.available)"
Add-Line "- Base URL: $($ollama.baseUrl)"
Add-Line "- Default model: $($ollama.defaultModel)"
Add-Line "- Model present in tags: $($ollama.modelPresentInTags)"
if ($ollama.error) { Add-Line "- Error: $($ollama.error)" }

if (-not $ollama.available) {
  Add-Line ""
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: BLOCKED_OLLAMA_NOT_READY"
  Add-Line "- Sem simulacao: nenhuma invocacao real foi feita."
  Add-Line ""
  Add-Line "## Como preparar sem API OpenAI"
  Add-Line ""
  Add-Line '```powershell'
  Add-Line "ollama signin"
  Add-Line "ollama pull deepseek-v4-pro:cloud"
  Add-Line "ollama serve"
  Add-Line ".\scripts\rc12-runtime-broker-readiness.ps1"
  Add-Line '```'
  Get-Content -LiteralPath $Report
  exit 0
}

$session = Invoke-AiosJson -Uri "$Base/sessions" -Method Post -Headers $headers -Body @{
  title = "RC12 Runtime Broker Session"
  objective = "Validar Runtime Broker com Ollama Local/Cloud e AIOS Cognitive Runtime Mesh."
}

try {
  $invoke = Invoke-AiosJson -Uri "$Base/runtime/broker/invoke" -Method Post -Headers $headers -Body @{
    sessionId = $session.id
    objective = "Valide em portugues que o AIOS Runtime Broker executou uma sessao Codex premium via Ollama sem chave OpenAI do desenvolvedor."
    provider = "auto"
    intelligenceMode = "aios_cognitive_runtime_mesh"
  }
  Add-Line ""
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: RUNTIME_BROKER_COMPLETED"
  Add-Line "- Provider: $($invoke.provider)"
  Add-Line "- Model: $($invoke.model)"
  Add-Line "- Runtime class: $($invoke.runtimeClass)"
  Add-Line "- Quality gate: $($invoke.qualityGate.status)"
  Add-Line "- Session ID: $($session.id)"
  Add-Line "- Output: $($invoke.outputText)"
} catch {
  Add-Line ""
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: RUNTIME_BROKER_FAILED"
  Add-Line "- Error: $(Get-ErrorBody $_)"
}

Get-Content -LiteralPath $Report
