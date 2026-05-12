param(
    [string[]]$Roots = @(
        "C:\AIOS\aios-codex-unlimited-enterprise-v2",
        "C:\Users\dg71\Documents\Codex\2026-05-08\aios-codex-unlimited-recapitula-o-completa"
    ),
    [string]$OutputPath = "C:\AIOS\aios-codex-unlimited-enterprise-v2\docs\AIOS_FULL_PROJECT_INDEX_RC31.md"
)

$ErrorActionPreference = "Stop"

$excludedPathPattern = "\\node_modules\\|\\dist\\|\\build\\|\\.git\\|\\.venv\\|\\venv\\|__pycache__\\|playwright-report\\|test-results\\|\\.pytest_cache\\|\\.aios-runtime\\|\\.run\\|aios-snapshots\\"
$forbiddenLeafPatterns = @(
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
    "*.exe",
    "*.dll",
    "*.pyd",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.ico",
    "*.pdf"
)

$textExtensions = @(
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".ps1", ".bat",
    ".cmd", ".yml", ".yaml", ".toml", ".css", ".html", ".env.example", ".gitignore",
    ".gitattributes", ".sql", ".dockerfile"
)

function Test-ForbiddenLeaf {
    param([string]$Leaf)
    foreach ($pattern in $forbiddenLeafPatterns) {
        if ($Leaf -like $pattern) {
            return $true
        }
    }
    return $false
}

function Test-TextFile {
    param([System.IO.FileInfo]$File)
    $leaf = $File.Name.ToLowerInvariant()
    if ($leaf -in @(".gitignore", ".gitattributes", ".env.example", ".env.local.private.example")) {
        return $true
    }
    foreach ($extension in $textExtensions) {
        if ($File.Extension.ToLowerInvariant() -eq $extension) {
            return $true
        }
    }
    return $false
}

$allFiles = foreach ($root in $Roots) {
    if (Test-Path $root) {
        Get-ChildItem -Path $root -Recurse -Force -File -ErrorAction SilentlyContinue
    }
}

$included = New-Object System.Collections.Generic.List[object]
$skipped = New-Object System.Collections.Generic.List[object]

foreach ($file in ($allFiles | Sort-Object FullName)) {
    $isPathExcluded = $file.FullName -match $excludedPathPattern
    $isForbiddenLeaf = Test-ForbiddenLeaf -Leaf $file.Name
    if ($isPathExcluded -or $isForbiddenLeaf) {
        $reason = if ($isPathExcluded) { "excluded_generated_or_dependency_path" } else { "forbidden_secret_binary_or_package_leaf" }
        $skipped.Add([PSCustomObject]@{
            Path = $file.FullName
            Length = $file.Length
            Reason = $reason
        })
        continue
    }

    $sha = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    $isText = Test-TextFile -File $file
    $lineCount = 0
    $summary = ""
    if ($isText -and $file.Length -lt 1048576) {
        try {
            $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
            if ($null -eq $content) { $content = "" }
            $lineCount = ($content -split "`r?`n").Count
            $headings = [regex]::Matches($content, "(?m)^#{1,3}\s+(.+)$") | ForEach-Object { $_.Groups[1].Value.Trim() } | Select-Object -First 8
            if ($headings) {
                $summary = ($headings -join " / ")
            } else {
                $summary = (($content -split "`r?`n") | Where-Object { $_.Trim() } | Select-Object -First 2) -join " / "
            }
        } catch {
            $summary = "text_read_failed"
        }
    } elseif ($isText) {
        $summary = "text_file_too_large_for_content_preview"
    } else {
        $summary = "binary_or_unknown_metadata_only"
    }

    $included.Add([PSCustomObject]@{
        Path = $file.FullName
        Length = $file.Length
        SHA256 = $sha
        Text = $isText
        Lines = $lineCount
        Summary = $summary
    })
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# AIOS Full Project Index RC31")
$lines.Add("")
$lines.Add("Generated from local project paths. Text source files are read for line counts and short summaries. Secrets, auth caches, databases, logs, generated folders, dependencies, binaries, and ZIPs are skipped or metadata-only by design.")
$lines.Add("")
$lines.Add("Included files: $($included.Count)")
$lines.Add("Skipped files: $($skipped.Count)")
$lines.Add("")
$lines.Add("## Included Files")
$lines.Add("")
$lines.Add("| # | Path | Bytes | Text | Lines | SHA256 | Summary |")
$lines.Add("|---:|---|---:|---|---:|---|---|")
$i = 0
foreach ($row in $included) {
    $i++
    $path = $row.Path.Replace("|", "\|")
    $summary = ($row.Summary -replace "`r|`n", " ").Replace("|", "/")
    if ($summary.Length -gt 260) {
        $summary = $summary.Substring(0, 260) + "..."
    }
    $lines.Add("| $i | ``$path`` | $($row.Length) | $($row.Text) | $($row.Lines) | ``$($row.SHA256)`` | $summary |")
}
$lines.Add("")
$lines.Add("## Skipped Files")
$lines.Add("")
$lines.Add("| # | Path | Bytes | Reason |")
$lines.Add("|---:|---|---:|---|")
$i = 0
foreach ($row in $skipped) {
    $i++
    $path = $row.Path.Replace("|", "\|")
    $lines.Add("| $i | ``$path`` | $($row.Length) | $($row.Reason) |")
}

Set-Content -LiteralPath $OutputPath -Value $lines -Encoding UTF8
Write-Host "Project index: $OutputPath" -ForegroundColor Green
Write-Host "Included files: $($included.Count)" -ForegroundColor Green
Write-Host "Skipped files:  $($skipped.Count)" -ForegroundColor Yellow
