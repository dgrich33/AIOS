param(
  [Parameter(Mandatory=$true)][string]$Name,
  [Parameter(Mandatory=$true)][string]$Json
)
$headers = @{ "X-Vault-Token" = "local-dev-token-only" }
$body = @{ data = ($Json | ConvertFrom-Json) } | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:8200/v1/secret/data/$Name" -Method Post -Headers $headers -ContentType "application/json" -Body $body
