$ErrorActionPreference = "Stop"
.\scripts\smoke-test.ps1
$base = "http://localhost:8000"
$login = Invoke-RestMethod "$base/auth/login" -Method Post -ContentType "application/json" -Body (@{ email="admin@aios.local"; password="AiosAdmin123!" } | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.accessToken)" }
Invoke-RestMethod "$base/control-plane/status" -Headers $headers | Out-Host
Invoke-RestMethod "$base/abuse/evaluate" -Method Post -Headers $headers -ContentType "application/json" -Body (@{ toolCallFlood=2; failedBuilds=0; sessionSpike=1; suspiciousCommand=$false } | ConvertTo-Json) | Out-Host
Write-Host "Enterprise check concluido"
