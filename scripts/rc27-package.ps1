param(
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$parent = Split-Path $root -Parent

if (-not $OutputPath) {
    $OutputPath = Join-Path $parent "AIOS_Codex_Unlimited_RC27_NATIVE_RUNTIME_FABRIC.zip"
}

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("aios-rc27-package-" + [System.Guid]::NewGuid().ToString("N"))
$stagingRoot = Join-Path $tempDir "aios-codex-unlimited-enterprise-v2"
$rootFullName = $root.Path.TrimEnd('\')

$excludedDirectories = @(
    ".git",
    ".run",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "out",
    "__pycache__",
    ".pytest_cache",
    ".playwright",
    "logs",
    "test-results",
    "playwright-report",
    ".aios-runtime",
    "aios-snapshots"
)

$excludedFilePatterns = @(
    ".env",
    ".env.local.private",
    "auth.json",
    "*.secret",
    "*.token",
    "*.db",
    "*.db-*",
    "*.sqlite",
    "*.sqlite-*",
    "*.log",
    "*.zip",
    "*.7z",
    "*.rar",
    "*.msi",
    "*.exe"
)

function Test-ExcludedPath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $relative = $fullPath.Substring($rootFullName.Length).TrimStart('\')
    $parts = $relative -split '[\\/]'
    foreach ($directory in $excludedDirectories) {
        if ($parts -contains $directory) {
            return $true
        }
    }
    foreach ($pattern in $excludedFilePatterns) {
        if ((Split-Path $Path -Leaf) -like $pattern) {
            return $true
        }
    }
    return $false
}

if (Test-Path $resolvedOutput) {
    Remove-Item -Path $resolvedOutput -Force
}

New-Item -ItemType Directory -Path $stagingRoot -Force | Out-Null

try {
    $items = Get-ChildItem -Path $root -Recurse -Force
    foreach ($item in $items) {
        if (Test-ExcludedPath -Path $item.FullName) {
            continue
        }
        $relative = $item.FullName.Substring($rootFullName.Length).TrimStart('\')
        $target = Join-Path $stagingRoot $relative
        if ($item.PSIsContainer) {
            New-Item -ItemType Directory -Path $target -Force | Out-Null
        } else {
            $targetDir = Split-Path $target -Parent
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            Copy-Item -LiteralPath $item.FullName -Destination $target -Force
        }
    }

    Compress-Archive -Path $stagingRoot -DestinationPath $resolvedOutput -Force
    $hash = (Get-FileHash -Path $resolvedOutput -Algorithm SHA256).Hash
    Write-Host "Package: $resolvedOutput" -ForegroundColor Green
    Write-Host "SHA256:  $hash" -ForegroundColor Yellow
} finally {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
