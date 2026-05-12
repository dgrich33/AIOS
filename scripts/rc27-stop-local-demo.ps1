param(
    [object[]]$BackendPort = @(8000, 8010),
    [object[]]$FrontendPort = @(5173, 5174)
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$runtimeDir = Join-Path $root ".aios-runtime"

function Convert-ToPortList {
    param([object[]]$Values)

    $ports = New-Object System.Collections.Generic.List[int]
    foreach ($value in $Values) {
        if ($null -eq $value) {
            continue
        }
        $text = [string]$value
        foreach ($part in ($text -split "[,\s;]+")) {
            if (-not $part) {
                continue
            }
            $port = 0
            if ([int]::TryParse($part, [ref]$port) -and $port -ge 1 -and $port -le 65535) {
                $ports.Add($port)
            } else {
                Write-Host "Ignoring invalid port value '$part'." -ForegroundColor Yellow
            }
        }
    }
    if ($ports.Count -eq 0) {
        throw "No valid ports were provided."
    }
    return $ports.ToArray() | Select-Object -Unique
}

function Stop-ProcessIdIfRunning {
    param([int]$ProcessId, [string]$Label)
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($process) {
        try {
            Stop-Process -Id $ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped $Label process $ProcessId." -ForegroundColor Green
            return $true
        } catch {
            Write-Host "Could not stop $Label process $ProcessId. It may be owned by another terminal/session. Continuing safely." -ForegroundColor Yellow
            return $false
        }
    }
    return $true
}

foreach ($name in @("frontend", "backend")) {
    $pidPath = Join-Path $runtimeDir "$name.pid"
    if (Test-Path $pidPath) {
        $processId = [int](Get-Content -Path $pidPath -Raw)
        $stopped = Stop-ProcessIdIfRunning -ProcessId $processId -Label $name
        if ($stopped) {
            Remove-Item -Path $pidPath -Force -ErrorAction SilentlyContinue
        }
    }
}

$portsToStop = @((Convert-ToPortList -Values $BackendPort) + (Convert-ToPortList -Values $FrontendPort)) | Select-Object -Unique
foreach ($port in $portsToStop) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        if ($connection.OwningProcess -gt 0) {
            Stop-ProcessIdIfRunning -ProcessId $connection.OwningProcess -Label "port $port"
        }
    }
}

Write-Host "AIOS RC27 local demo stop command finished." -ForegroundColor Green
