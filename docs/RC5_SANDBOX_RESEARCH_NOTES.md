# AIOS Codex Unlimited - Notas de Pesquisa Sandbox/Provider

## Fontes lidas

- OpenAI Developers: Codex Agent approvals & security.
- OpenAI Developers: Codex Windows.
- Microsoft Learn: Codex com Azure OpenAI em modelos Microsoft Foundry.
- AI SDK: Azure OpenAI provider.
- GitHub issue OpenAI Codex #13183 sobre NuGet no Windows sandbox.
- DataCamp: tutorial Codex CLI MCP.
- Azukiazusa: artigo sobre sandbox e approvals.

## Decisao tecnica

A RC5 agora aceita dois perfis:

1. `openai_codex`
   - exige `AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT`;
   - exige `AIOS_OFFICIAL_CODEX_SERVICE_TOKEN`;
   - exige `AIOS_OFFICIAL_CODEX_TENANT_ID`;
   - exige sandbox, Vault/KMS e live flag.

2. `azure_openai`
   - exige `AZURE_OPENAI_ENDPOINT` ou `AZURE_RESOURCE_NAME`;
   - exige `AZURE_OPENAI_API_KEY`;
   - exige `AZURE_OPENAI_DEPLOYMENT`;
   - exige sandbox, Vault/KMS e live flag;
   - nao exige tenant quando o modo aprovado for API key.

## Observacao de seguranca

Nenhum endpoint generico foi inventado. O AIOS so marca `secureEnvironmentReady=true` se os valores reais estiverem presentes no processo do backend.

## Windows sandbox

No Windows, o pacote deve assumir que o sandbox pode bloquear escrita fora do workspace e rede sem permissao. Para fluxos .NET, manter workaround documentado:

```powershell
$env:NUGET_PACKAGES = Join-Path $env:USERPROFILE ".nuget\packages"
dotnet restore .\project.sln -m:1
dotnet build .\project.sln -m:1 --no-restore
```
