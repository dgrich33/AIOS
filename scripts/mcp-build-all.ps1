$ErrorActionPreference = "Stop"
Push-Location .\mcp\aios-mcp-repo
npm install
npm run build
Pop-Location
Push-Location .\mcp\aios-mcp-core
npm install
npm run build
Pop-Location
Write-Host "MCP build concluido"
