$ErrorActionPreference = "Stop"

$BaseUrl = $env:AIOS_API_URL
if (-not $BaseUrl) { $BaseUrl = "http://127.0.0.1:8000" }

function Invoke-AiosJson {
  param(
    [Parameter(Mandatory=$true)][string]$Uri,
    [string]$Method = "GET",
    [hashtable]$Headers = @{},
    [object]$Body = $null
  )
  $Params = @{
    Uri = $Uri
    Method = $Method
    Headers = $Headers
  }
  if ($null -ne $Body) {
    $Params.ContentType = "application/json"
    $Params.Body = ($Body | ConvertTo-Json -Depth 20)
  }
  Invoke-RestMethod @Params
}

Write-Host "AIOS RC7 validate: $BaseUrl" -ForegroundColor Cyan

$health = Invoke-AiosJson -Uri "$BaseUrl/health"
if ($health.status -ne "ok") { throw "Health check falhou." }

$login = Invoke-AiosJson -Uri "$BaseUrl/auth/login" -Method "POST" -Body @{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
}
$Headers = @{ Authorization = "Bearer $($login.accessToken)" }

$providers = Invoke-AiosJson -Uri "$BaseUrl/runtime/no-developer-cost/providers" -Headers $Headers
if ($providers.productUnit -ne "codex_sessions") { throw "Produto deixou de usar codex_sessions." }
if ($providers.primaryProvider -ne "puter_user_pays") { throw "Provider primario inesperado." }

$puter = $providers.providers | Where-Object { $_.providerId -eq "puter_user_pays" } | Select-Object -First 1
if (-not $puter) { throw "Puter user-pays nao apareceu no catalogo." }
if ($puter.requiresDeveloperApiKey -ne $false) { throw "Puter nao deve exigir chave do desenvolvedor." }

$recommendation = Invoke-AiosJson -Uri "$BaseUrl/runtime/no-developer-cost/recommendation" -Headers $Headers
if ($recommendation.recommendedProvider.providerId -ne "puter_user_pays") { throw "Recomendacao RC7 incorreta." }

$session = Invoke-AiosJson -Uri "$BaseUrl/sessions" -Method "POST" -Headers $Headers -Body @{
  title = "RC7 No Developer Cost Session"
  objective = "Validar provedores sem custo direto do desenvolvedor."
}

$event = Invoke-AiosJson -Uri "$BaseUrl/sessions/$($session.id)/events" -Method "POST" -Headers $Headers -Body @{
  type = "codex.runtime.completed"
  source = "rc7-validate"
  title = "Puter user-pays validation event"
  message = "Evento RC7 registrado sem chave OpenAI no backend."
  payload = @{
    provider = "puter_user_pays"
    developerCost = "none_direct"
    backendReceivedProviderSecret = $false
  }
}
if (-not $event.id) { throw "Evento RC7 nao foi criado." }

$workbench = Invoke-AiosJson -Uri "$BaseUrl/sessions/$($session.id)/workbench" -Headers $Headers
$eventTypes = @($workbench.recentEvents | ForEach-Object { $_.type })
if ($eventTypes -notcontains "codex.runtime.completed") { throw "Workbench nao retornou evento RC7." }

Write-Host "RC7 validate OK: provedores sem custo direto + Workbench." -ForegroundColor Green
