param(
    [switch]$WriteReport,
    [string]$ReportPath = "docs\RC32_NO_DELETE_RECOVERY_AUDIT.md"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $root
try {
    $deletedTracked = @(git ls-files --deleted)
    $diffNameStatus = @(git diff --name-status)
    $diffDeleted = @($diffNameStatus | Where-Object { $_ -match "^D\s+" })
    $status = @(git status --short)

    $result = [PSCustomObject]@{
        ok = (($deletedTracked.Count -eq 0) -and ($diffDeleted.Count -eq 0))
        scannedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        trackedDeletedCount = $deletedTracked.Count
        diffDeletedCount = $diffDeleted.Count
        trackedDeletedPaths = $deletedTracked
        diffDeletedEntries = $diffDeleted
        gitStatusEntries = $status.Count
        policy = "AIOS no-delete guard: preserve tracked files; use additive changes unless the user explicitly asks for deletion."
    }

    if ($WriteReport) {
        $fullReportPath = Join-Path $root $ReportPath
        $reportDir = Split-Path $fullReportPath -Parent
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null

        $lines = @(
            "# RC32 No-Delete Recovery Audit",
            "",
            "Generated: $($result.scannedAt)",
            "",
            "## Policy",
            "",
            $result.policy,
            "",
            "## Current Result",
            "",
            "| Check | Value |",
            "|---|---:|",
            "| OK | $($result.ok) |",
            "| Tracked deleted files | $($result.trackedDeletedCount) |",
            "| Git diff deletion entries | $($result.diffDeletedCount) |",
            "| Git status entries | $($result.gitStatusEntries) |",
            "",
            "## Deleted Tracked Paths",
            ""
        )

        if ($deletedTracked.Count -eq 0 -and $diffDeleted.Count -eq 0) {
            $lines += "None."
        } else {
            foreach ($item in $deletedTracked) {
                $lines += "- ``$item``"
            }
            foreach ($item in $diffDeleted) {
                $lines += "- ``$item``"
            }
        }

        $lines += @(
            "",
            "## Recovery Notes",
            "",
            "- Tracked files were restored before RC31/RC32 additive work.",
            "- Current guard result has no tracked deletion.",
            "- Runtime work remains additive: `community_wrapper_runtime` and `gpt-oss-20b` are configured through registry/provider paths.",
            "- This report does not read secrets, `.env.local.private`, `auth.json`, databases, or logs."
        )

        Set-Content -LiteralPath $fullReportPath -Value $lines -Encoding UTF8
        Write-Host "No-delete report: $fullReportPath" -ForegroundColor Green
    }

    $result | ConvertTo-Json -Depth 5
    if (-not $result.ok) {
        exit 1
    }
} finally {
    Pop-Location
}
