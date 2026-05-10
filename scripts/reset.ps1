$ErrorActionPreference = "Stop"
docker compose down -v
Remove-Item -LiteralPath ".\backend\aios_dev.db" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath ".\backend\test_aios.db" -Force -ErrorAction SilentlyContinue
