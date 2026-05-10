$ErrorActionPreference = "Stop"

$BaseUrl = $env:OPENAI_BASE_URL
if (-not $BaseUrl) { $BaseUrl = "https://api.openai.com/v1" }
$ApiKey = $env:OPENAI_API_KEY
$ProjectId = $env:OPENAI_PROJECT_ID
$OrganizationId = $env:OPENAI_ORG_ID
if (-not $OrganizationId) { $OrganizationId = $env:OPENAI_ORGANIZATION }

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$ReportPath = Join-Path $ReleaseDir "RC8_OPENAI_MODEL_DIAGNOSTIC.md"

$Candidates = @(
  "gpt-5.5",
  "gpt-5.5-pro",
  "gpt-5.2-codex",
  "gpt-5.1-codex",
  "gpt-5.1-codex-max",
  "gpt-5.1-codex-mini",
  "gpt-5-codex"
)

function Write-Report {
  param(
    [string]$Status,
    [string[]]$AvailableCandidates,
    [string]$RecommendedModel,
    [string]$ErrorMessage = ""
  )

  $lines = @()
  $lines += "# AIOS Codex Unlimited RC8 - OpenAI model diagnostic"
  $lines += ""
  $lines += "- Data: $(Get-Date -Format o)"
  $lines += "- Base URL: $BaseUrl"
  $lines += "- Status: $Status"
  $lines += "- API key impressa: Nao"
  $lines += "- Project configurado: $(if ($ProjectId) { 'Sim' } else { 'Nao/opcional' })"
  $lines += "- Organization configurado: $(if ($OrganizationId) { 'Sim' } else { 'Nao/opcional' })"
  $lines += ""
  $lines += "## Candidatos verificados"
  $lines += ""
  foreach ($candidate in $Candidates) {
    $mark = if ($AvailableCandidates -contains $candidate) { "[x]" } else { "[ ]" }
    $lines += ('- {0} `{1}`' -f $mark, $candidate)
  }
  $lines += ""
  $lines += "## Recomendacao"
  $lines += ""
  if ($RecommendedModel) {
    $lines += "Use nesta sessao:"
    $lines += ""
    $lines += '```powershell'
    $lines += ('$env:OPENAI_MODEL = "{0}"' -f $RecommendedModel)
    $lines += '```'
  } else {
    $lines += "Nenhum candidato preferencial apareceu na lista de modelos da conta. Verifique acesso do projeto/organizacao ou use o modelo Codex disponivel mais proximo."
  }
  if ($ErrorMessage) {
    $lines += ""
    $lines += "## Erro"
    $lines += ""
    $lines += $ErrorMessage
  }
  $lines += ""
  $lines += "## Observacao"
  $lines += ""
  $lines += "Este diagnostico nao cobra geracao de resposta. Ele apenas lista modelos disponiveis para a credencial configurada."
  $lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8
}

if (-not $ApiKey) {
  Write-Report -Status "MISSING_OPENAI_API_KEY" -AvailableCandidates @() -RecommendedModel "" -ErrorMessage "OPENAI_API_KEY nao esta configurada nesta sessao."
  Get-Content -LiteralPath $ReportPath
  exit 0
}

$Headers = @{
  Authorization = "Bearer $ApiKey"
}
if ($ProjectId) { $Headers["OpenAI-Project"] = $ProjectId }
if ($OrganizationId) { $Headers["OpenAI-Organization"] = $OrganizationId }

try {
  $Response = Invoke-RestMethod -Uri "$($BaseUrl.TrimEnd('/'))/models" -Method GET -Headers $Headers
  $ModelIds = @($Response.data | ForEach-Object { $_.id })
  $AvailableCandidates = @($Candidates | Where-Object { $ModelIds -contains $_ })
  $RecommendedModel = ""
  foreach ($candidate in $Candidates) {
    if ($AvailableCandidates -contains $candidate) {
      $RecommendedModel = $candidate
      break
    }
  }
  Write-Report -Status "OK" -AvailableCandidates $AvailableCandidates -RecommendedModel $RecommendedModel
} catch {
  $message = $_.Exception.Message
  Write-Report -Status "OPENAI_MODEL_LIST_FAILED" -AvailableCandidates @() -RecommendedModel "" -ErrorMessage $message
}

Get-Content -LiteralPath $ReportPath
