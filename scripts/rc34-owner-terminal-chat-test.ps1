param(
    [int]$BackendPort = 8026,
    [int]$FrontendPort = 5176,
    [string]$Email = "admin@aios.local",
    [string]$Password = "AiosAdmin123!",
    [string]$Provider = "auto",
    [string]$Model = "gpt-5.5",
    [string]$Prompt = "Responda exatamente: AIOS OWNER TERMINAL OK",
    [switch]$AllowNativeFallback,
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendUrl = "http://127.0.0.1:$BackendPort"

function Write-Step {
    param([string]$Message)
    Write-Output ""
    Write-Output "==> $Message"
}

function Wait-HttpOk {
    param([string]$Url, [int]$TimeoutSeconds = 45)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Milliseconds 800
        }
    }
    return $false
}

function Invoke-AiosJson {
    param(
        [string]$Path,
        [string]$Method = "GET",
        [object]$Body = $null,
        [string]$Token = ""
    )

    $headers = @{ "Content-Type" = "application/json" }
    if ($Token) {
        $headers["Authorization"] = "Bearer $Token"
    }
    $params = @{
        Uri = "$backendUrl$Path"
        Method = $Method
        Headers = $headers
        TimeoutSec = 180
    }
    if ($null -ne $Body) {
        $params["Body"] = ($Body | ConvertTo-Json -Depth 8)
    }
    return Invoke-RestMethod @params
}

Write-Step "Preparando ambiente local privado"
$codexBin = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\bin"
if ((Test-Path -LiteralPath $codexBin) -and (($env:PATH -split ";") -notcontains $codexBin)) {
    $env:PATH = "$codexBin;$env:PATH"
}
$npmBin = Join-Path $env:APPDATA "npm"
if ((Test-Path -LiteralPath $npmBin) -and (($env:PATH -split ";") -notcontains $npmBin)) {
    $env:PATH = "$npmBin;$env:PATH"
}
$env:AIOS_ENV = "local_developer"
$env:AIOS_PRESENTATION_MODE = "true"
$env:AIOS_LOCAL_ONLY = "true"
$env:AIOS_ALLOW_GITHUB_PUSH = "false"
$env:AIOS_PUBLIC_RELEASE = "false"
$env:AIOS_REQUIRE_APPROVAL_GATE = "true"
$env:AIOS_SECRETS_EXPOSED = "false"
$env:AIOS_CHAT_PROVIDER = "codex_cli_local_developer"
$env:AIOS_ALLOW_CODEX_CLI_RUNTIME = "true"
$env:AIOS_CODEX_CLI_MODEL = $Model
$env:AIOS_NATIVE_RUNTIME_ENABLED = "true"
$env:AIOS_NATIVE_RUNTIME_MODEL = "aios-native-fabric-v1"

if (-not $NoStart) {
    Write-Step "Iniciando AIOS sem abrir navegador"
    & (Join-Path $PSScriptRoot "rc27-start-local-demo.ps1") -BackendPort $BackendPort -FrontendPort $FrontendPort -ForceRestart -NoOpen
}

Write-Step "Verificando backend"
if (-not (Wait-HttpOk -Url "$backendUrl/health" -TimeoutSeconds 60)) {
    $logPath = Join-Path $root ".aios-runtime\logs\backend.err.log"
    Write-Output "Backend nao respondeu em $backendUrl/health."
    if (Test-Path $logPath) {
        Write-Output ""
        Write-Output "Ultimas linhas do backend.err.log:"
        Get-Content -Path $logPath -Tail 40
    }
    exit 1
}

Write-Step "Login local Product Owner"
$login = Invoke-AiosJson -Path "/auth/login" -Method "POST" -Body @{ email = $Email; password = $Password }
$token = [string]$login.accessToken
if (-not $token) {
    throw "Login nao retornou accessToken."
}

Write-Step "Status do Runtime Broker"
$status = Invoke-AiosJson -Path "/runtime/broker/status" -Token $token
Write-Output ("Recommended provider: " + $status.recommendedProvider)
Write-Output ("Live provider:        " + $status.liveRuntimeProvider)
Write-Output ("Can invoke live:      " + $status.canInvokeLiveRuntime)
Write-Output ("Official production:  " + $status.officialProduction)

Write-Step "Criando sessao de teste"
$session = Invoke-AiosJson -Path "/sessions" -Method "POST" -Token $token -Body @{
    title = "RC34 Owner Terminal Chat"
    objective = $Prompt
}

Write-Step "Chamando chat do AIOS"
try {
    $result = Invoke-AiosJson -Path "/runtime/broker/invoke" -Method "POST" -Token $token -Body @{
        sessionId = $session.id
        objective = $Prompt
        provider = $Provider
        model = $Model
        intelligenceMode = "aios_cognitive_runtime_mesh"
    }
} catch {
    if (-not $AllowNativeFallback) {
        Write-Output "Falha real no provider '$Provider'. Nao houve fallback automatico."
        Write-Output "Use -AllowNativeFallback apenas quando quiser testar a camada AIOS Native separadamente."
        throw
    } else {
        Write-Output "Falha no provider '$Provider'. Fallback explicito para AIOS Native Runtime solicitado por -AllowNativeFallback."
        $result = Invoke-AiosJson -Path "/runtime/broker/invoke" -Method "POST" -Token $token -Body @{
            sessionId = $session.id
            objective = $Prompt
            provider = "aios_native_runtime"
            model = "aios-native-fabric-v1"
            intelligenceMode = "aios_cognitive_runtime_mesh"
        }
    }
}

$text = [string]$result.outputText
Write-Output ""
Write-Output "===== RESPOSTA DO AIOS ====="
Write-Output $text
Write-Output "============================"
Write-Output ""
Write-Output ("Provider usado: " + $result.provider)
Write-Output ("Modelo:        " + $result.model)
if ($result.fallbackFrom) {
    Write-Output ("Fallback de:    " + $result.fallbackFrom)
}
Write-Output ("Frontend:      http://127.0.0.1:$FrontendPort")

if (-not $text.Trim()) {
    throw "O runtime retornou resposta vazia."
}

Write-Output ""
Write-Output "Teste de chat Owner concluido."
