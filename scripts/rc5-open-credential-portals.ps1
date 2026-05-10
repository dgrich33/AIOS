$ErrorActionPreference = "Stop"

Write-Host "Abrindo portais oficiais para obter credenciais reais..."

$urls = @(
  "https://platform.openai.com/api-keys",
  "https://platform.openai.com/settings/organization/projects",
  "https://ai.azure.com",
  "https://portal.azure.com",
  "https://learn.microsoft.com/pt-br/azure/foundry/openai/how-to/codex?tabs=npm"
)

foreach ($url in $urls) {
  Start-Process $url
}

Write-Host ""
Write-Host "Campos que voce precisa copiar para o AIOS:"
Write-Host "- OpenAI direta: API key ou service account API key."
Write-Host "- Azure Foundry: Endpoint, API key e Deployment."
Write-Host ""
Write-Host "Nao cole chaves em chat, print, frontend ou arquivo de release."
