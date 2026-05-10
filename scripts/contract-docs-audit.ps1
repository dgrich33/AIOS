$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Docs = Join-Path $Root "docs"

$Patterns = @(
  "TBD",
  "Signoff Form",
  "Approval Memo",
  "Decision:",
  "Assinatura: _",
  "Nome: _",
  "Aprovado apenas",
  "Nao aprovado nesta etapa",
  "not assumed",
  "does not patch",
  "does not extract",
  "sem artefatos privados",
  "Nao incluir binarios",
  "Nao incluir pesos",
  "requires explicit signed"
)

$Allowed = @(
  "docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md"
)

$Findings = @()
Get-ChildItem -LiteralPath $Docs -Recurse -File -Filter *.md | ForEach-Object {
  $relative = $_.FullName.Substring($Root.Length + 1).Replace("\", "/")
  if ($Allowed -contains $relative) { return }
  $content = Get-Content -LiteralPath $_.FullName -Raw
  foreach ($pattern in $Patterns) {
    if ($content -match [regex]::Escape($pattern)) {
      $Findings += [PSCustomObject]@{
        file = $relative
        pattern = $pattern
      }
    }
  }
}

if ($Findings.Count -gt 0) {
  $Findings | Format-Table -AutoSize
  throw "Auditoria de docs falhou: ha termos antigos fora do contrato soberano."
}

Write-Host "Auditoria de docs OK: nenhum termo antigo encontrado fora do contrato soberano." -ForegroundColor Green

