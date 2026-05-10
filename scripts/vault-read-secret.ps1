param([Parameter(Mandatory=$true)][string]$Name)
$headers = @{ "X-Vault-Token" = "local-dev-token-only" }
Invoke-RestMethod "http://localhost:8200/v1/secret/data/$Name" -Headers $headers
