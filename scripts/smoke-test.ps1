$ErrorActionPreference = "Stop"
$base = "http://localhost:8000"
Invoke-RestMethod "$base/health" | Out-Host
Invoke-RestMethod "$base/ready" | Out-Host
$login = Invoke-RestMethod "$base/auth/login" -Method Post -ContentType "application/json" -Body (@{ email="admin@aios.local"; password="AiosAdmin123!" } | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.accessToken)" }
Invoke-RestMethod "$base/entitlement/me" -Headers $headers | Out-Host
Write-Host "Smoke test OK"
