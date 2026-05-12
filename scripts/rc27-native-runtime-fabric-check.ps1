param(
    [switch]$SkipPlaywright,
    [switch]$SkipMcp,
    [string]$BackendUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "== $Name ==" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

Invoke-Step "Backend tests" {
    Push-Location (Join-Path $root "backend")
    try {
        python -m pytest .\tests\test_api.py -q
    } finally {
        Pop-Location
    }
}

Invoke-Step "Frontend build" {
    Push-Location (Join-Path $root "frontend")
    try {
        npm run build
    } finally {
        Pop-Location
    }
}

if (-not $SkipPlaywright) {
    Invoke-Step "Playwright" {
        & (Join-Path $root "scripts\test-frontend-e2e.ps1")
    }
}

if (-not $SkipMcp) {
    Invoke-Step "MCP repo build" {
        Push-Location (Join-Path $root "mcp\aios-mcp-repo")
        try {
            npm run build
        } finally {
            Pop-Location
        }
    }

    Invoke-Step "MCP core build" {
        Push-Location (Join-Path $root "mcp\aios-mcp-core")
        try {
            npm run build
        } finally {
            Pop-Location
        }
    }
}

Invoke-Step "Runtime fabric status if backend is running" {
    try {
        $status = Invoke-RestMethod -Uri "$BackendUrl/runtime/fabric/status" -Method Get -TimeoutSec 5
        $status | ConvertTo-Json -Depth 8
    } catch {
        Write-Host "Backend not reachable at $BackendUrl; skipping live status HTTP check." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "RC27 Native Runtime Fabric check finished." -ForegroundColor Green
