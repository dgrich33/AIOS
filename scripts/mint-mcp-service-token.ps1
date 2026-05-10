$ErrorActionPreference = "Stop"
$base = "http://localhost:8000"
$login = Invoke-RestMethod "$base/auth/login" -Method Post -ContentType "application/json" -Body (@{ email="admin@aios.local"; password="AiosAdmin123!" } | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.accessToken)" }
Invoke-RestMethod "$base/admin/service-tokens?name=mcp-local" -Method Post -Headers $headers
