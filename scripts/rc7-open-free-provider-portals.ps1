$ErrorActionPreference = "Stop"

$Urls = @(
  "https://developer.puter.com/",
  "https://docs.puter.com/user-pays-model/",
  "https://developer.puter.com/tutorials/free-unlimited-codex-api/",
  "https://build.nvidia.com/",
  "https://console.groq.com/",
  "https://github.com/marketplace?type=models",
  "https://aistudio.google.com/",
  "https://openrouter.ai/",
  "https://developers.cloudflare.com/workers-ai/",
  "https://ollama.com/settings"
)

foreach ($Url in $Urls) {
  Start-Process $Url
}

Write-Host "Portais de provedores sem custo direto abertos." -ForegroundColor Green

