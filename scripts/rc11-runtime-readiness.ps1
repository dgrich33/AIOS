$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC11_RUNTIME_READINESS_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -LiteralPath $Report -Value $Text
}

function Get-ErrorBody($ErrorRecord) {
  if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) {
    return $ErrorRecord.ErrorDetails.Message
  }
  try {
    $stream = $ErrorRecord.Exception.Response.GetResponseStream()
    if (-not $stream) { return "" }
    $reader = [System.IO.StreamReader]::new($stream)
    return $reader.ReadToEnd()
  } catch {
    return $ErrorRecord.Exception.Message
  }
}

function Invoke-AiosJson {
  param(
    [string]$Uri,
    [string]$Method = "GET",
    [hashtable]$Headers = @{},
    [object]$Body = $null
  )
  $params = @{
    Uri = $Uri
    Method = $Method
    Headers = $Headers
  }
  if ($null -ne $Body) {
    $params.ContentType = "application/json"
    $params.Body = ($Body | ConvertTo-Json -Depth 20)
  }
  Invoke-RestMethod @params
}

Set-Content -LiteralPath $Report -Value "# AIOS Codex Unlimited RC11 - Runtime readiness`n"
Add-Line "- Data: $(Get-Date -Format o)"
Add-Line "- Base local: $Base"
Add-Line "- API key impressa: Nao"
Add-Line ""

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host
& "$PSScriptRoot\contract-docs-audit.ps1" | Out-Host

Add-Line "## Diagnostico OpenAI /models"
Add-Line ""
try {
  $diagnostic = & "$PSScriptRoot\rc8-openai-model-diagnose.ps1"
  $diagnostic | ForEach-Object { Add-Line $_ }
} catch {
  Add-Line "- Status: RC8_DIAGNOSTIC_FAILED"
  Add-Line "- Erro: $($_.Exception.Message)"
}
Add-Line ""

try {
  $health = Invoke-RestMethod "$Base/health"
} catch {
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: API_NOT_RUNNING"
  Add-Line "- Detalhe: backend local nao respondeu em $Base."
  Add-Line "- Acao: execute .\scripts\start.ps1 -Mode Local e rode este script novamente."
  Get-Content -LiteralPath $Report
  exit 0
}

Add-Line "## Backend local"
Add-Line ""
Add-Line "- Health: $($health.status)"

$login = Invoke-AiosJson -Uri "$Base/auth/login" -Method Post -Body @{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
}
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$discovery = Invoke-AiosJson -Uri "$Base/codex/runtime/model-discovery" -Headers $headers
Add-Line ""
Add-Line "## Model discovery pelo backend"
Add-Line ""
Add-Line "- Status: $($discovery.status)"
Add-Line "- Provider: $($discovery.provider)"
Add-Line "- Network call performed: $($discovery.networkCallPerformed)"
Add-Line "- Configured model: $($discovery.configuredModel)"
Add-Line "- Recommended model: $($discovery.recommendedModel)"
Add-Line "- Available candidates: $(@($discovery.availableCandidates) -join ', ')"
Add-Line "- Missing: $(@($discovery.missing) -join ', ')"
if ($discovery.selectedModelCommand) {
  Add-Line ""
  Add-Line "Use nesta sessao:"
  Add-Line ""
  Add-Line '```powershell'
  Add-Line $discovery.selectedModelCommand
  Add-Line '```'
}

if ($discovery.status -ne "model_available") {
  Add-Line ""
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: BLOCKED_BEFORE_RUNTIME_INVOKE"
  Add-Line "- Motivo: descoberta real de modelo nao confirmou um modelo disponivel."
  Add-Line "- Observacao: isto nao e simulacao falsa; o projeto permanece protegido ate credencial/ambiente/modelo estarem prontos."
  Get-Content -LiteralPath $Report
  exit 0
}

$security = Invoke-AiosJson -Uri "$Base/official-sandbox/security-check" -Headers $headers
if (-not $security.canInvokeLiveRuntime) {
  Add-Line ""
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: MODEL_AVAILABLE_BUT_SANDBOX_BLOCKED"
  Add-Line "- Missing: $(@($security.missing) -join ', ')"
  Add-Line "- Acao: complete o ambiente seguro antes da invocacao real."
  Get-Content -LiteralPath $Report
  exit 0
}

$session = Invoke-AiosJson -Uri "$Base/sessions" -Method Post -Headers $headers -Body @{
  title = "RC11 Runtime Readiness"
  objective = "Validar modelo real e invocacao protegida do runtime OpenAI API no AIOS Codex Unlimited."
}

try {
  $invoke = Invoke-AiosJson -Uri "$Base/codex/runtime/invoke" -Method Post -Headers $headers -Body @{
    session_id = $session.id
    model_id = "codex-5.5-unlimited"
    objective = "Responda em uma frase curta confirmando a readiness RC11 do runtime."
  }
  Add-Line ""
  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: RUNTIME_INVOKE_COMPLETED"
  Add-Line "- Session ID: $($session.id)"
  Add-Line "- Runtime model: $($invoke.runtimeModelId)"
  Add-Line "- Response ID: $($invoke.responseId)"
  Add-Line "- Network call performed: $($invoke.networkCallPerformed)"
} catch {
  $body = Get-ErrorBody $_
  if ($body -match "insufficient_quota") {
    Add-Line ""
    Add-Line "## Resultado"
    Add-Line ""
    Add-Line "- Status: BLOCKED_BY_OPENAI_QUOTA"
    Add-Line "- Session ID: $($session.id)"
    Add-Line "- Detalhe: a chamada chegou ao runtime, mas a conta/projeto retornou quota insuficiente."
  } else {
    Add-Line ""
    Add-Line "## Resultado"
    Add-Line ""
    Add-Line "- Status: RUNTIME_INVOKE_FAILED"
    Add-Line "- Session ID: $($session.id)"
    Add-Line "- Erro: $body"
    throw
  }
}

Add-Line ""
Add-Line "## Seguranca"
Add-Line ""
Add-Line "- Secrets exposed: False"
Add-Line "- Frontend exposure allowed: False"
Add-Line "- User-facing unit: codex_sessions"
Add-Line "- Token counter visible: False"

Get-Content -LiteralPath $Report
