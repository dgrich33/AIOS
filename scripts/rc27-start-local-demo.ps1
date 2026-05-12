param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$ForceRestart,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$runtimeDir = Join-Path $root ".aios-runtime"
$logDir = Join-Path $runtimeDir "logs"
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$privateEnvPath = Join-Path $root ".env.local.private"

New-Item -ItemType Directory -Path $logDir -Force | Out-Null

function Import-PrivateEnvFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $allowedPrefixes = @("AIOS_", "OPENAI_", "AZURE_", "OLLAMA_")
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
            continue
        }
        $name, $value = $trimmed.Split("=", 2)
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        $allowed = $false
        foreach ($prefix in $allowedPrefixes) {
            if ($name.StartsWith($prefix)) {
                $allowed = $true
                break
            }
        }
        if ($allowed -and -not [Environment]::GetEnvironmentVariable($name, "Process")) {
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

if (-not $env:AIOS_ENV) {
    $env:AIOS_ENV = "local_developer"
}
$env:AIOS_PRESENTATION_MODE = if ($env:AIOS_PRESENTATION_MODE) { $env:AIOS_PRESENTATION_MODE } else { "true" }
Import-PrivateEnvFile -Path $privateEnvPath

function Add-PathIfExists {
    param([string]$Path)
    if ((Test-Path -LiteralPath $Path) -and (($env:PATH -split ";") -notcontains $Path)) {
        $env:PATH = "$Path;$env:PATH"
    }
}

Add-PathIfExists -Path (Join-Path $env:LOCALAPPDATA "OpenAI\Codex\bin")
Add-PathIfExists -Path (Join-Path $env:APPDATA "npm")
Add-PathIfExists -Path (Join-Path $env:USERPROFILE ".codex\bin")

function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connection
}

function Stop-PortListener {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        if ($connection.OwningProcess -gt 0) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                try {
                    Stop-Process -Id $process.Id -Force -ErrorAction Stop
                    Write-Host "Stopped stale process $($process.Id) on port $Port." -ForegroundColor Green
                } catch {
                    Write-Host "Could not stop process $($process.Id) on port $Port. Reusing it if it is already serving AIOS." -ForegroundColor Yellow
                }
            }
        }
    }
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Milliseconds 700
        }
    }
    return $false
}

if ($ForceRestart) {
    Stop-PortListener -Port $BackendPort
    Stop-PortListener -Port $FrontendPort
    Start-Sleep -Milliseconds 700
}

if (Test-Port -Port $BackendPort) {
    Write-Host "Backend port $BackendPort is already in use. Reusing existing backend." -ForegroundColor Yellow
} else {
    $backend = Start-Process -FilePath "python" `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$BackendPort") `
        -WorkingDirectory $backendDir `
        -RedirectStandardOutput (Join-Path $logDir "backend.out.log") `
        -RedirectStandardError (Join-Path $logDir "backend.err.log") `
        -WindowStyle Hidden `
        -PassThru
    Set-Content -Path (Join-Path $runtimeDir "backend.pid") -Value $backend.Id -Encoding ASCII
}

if (Test-Port -Port $FrontendPort) {
    Write-Host "Frontend port $FrontendPort is already in use. Reusing existing frontend." -ForegroundColor Yellow
} else {
    Push-Location $frontendDir
    try {
        if (-not (Test-Path ".\node_modules")) {
            npm install
        }
    } finally {
        Pop-Location
    }
    $previousViteApiUrl = $env:VITE_AIOS_API_URL
    $env:VITE_AIOS_API_URL = "http://127.0.0.1:$BackendPort"
    try {
        $frontend = Start-Process -FilePath "node" `
            -ArgumentList @("./node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", "$FrontendPort") `
            -WorkingDirectory $frontendDir `
            -RedirectStandardOutput (Join-Path $logDir "frontend.out.log") `
            -RedirectStandardError (Join-Path $logDir "frontend.err.log") `
            -WindowStyle Hidden `
            -PassThru
    } finally {
        $env:VITE_AIOS_API_URL = $previousViteApiUrl
    }
    Set-Content -Path (Join-Path $runtimeDir "frontend.pid") -Value $frontend.Id -Encoding ASCII
}

Write-Host ""
Write-Host "AIOS RC27 local demo is starting." -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:$FrontendPort"
Write-Host "Backend:  http://127.0.0.1:$BackendPort/docs"
Write-Host "Runtime:  http://127.0.0.1:$BackendPort/runtime/fabric/status"
Write-Host "Logs:     $logDir"

$backendReady = Wait-HttpOk -Url "http://127.0.0.1:$BackendPort/health"
$frontendReady = Wait-HttpOk -Url "http://127.0.0.1:$FrontendPort"

if ($backendReady -and $frontendReady -and -not $NoOpen) {
    Write-Host ""
    Write-Host "Opening AIOS Workbench in your browser..." -ForegroundColor Green
    Start-Process "http://127.0.0.1:$FrontendPort"
} elseif ($backendReady -and $frontendReady) {
    Write-Host ""
    Write-Host "AIOS Workbench is ready. Open http://127.0.0.1:$FrontendPort when you want to test the UI." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "AIOS started, but readiness check did not complete in time. Open the URLs above manually after a few seconds." -ForegroundColor Yellow
}
