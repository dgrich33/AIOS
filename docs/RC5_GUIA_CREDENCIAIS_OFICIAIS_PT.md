# AIOS Codex Unlimited RC5 - Guia de Credenciais Oficiais

## Resumo simples

Existem dois caminhos praticos para credenciais reais:

1. **OpenAI API direta**
   - voce pega uma API key no painel da OpenAI;
   - o endpoint base normalmente e `https://api.openai.com/v1`;
   - voce escolhe o modelo na chamada da API;
   - nao existe "deployment" no mesmo sentido do Azure.

2. **Azure OpenAI / Microsoft Foundry**
   - voce cria um recurso/projeto no Azure/Foundry;
   - implanta um modelo;
   - copia o endpoint;
   - copia a API key;
   - usa o nome do deployment implantado.

## O que e cada campo

| Campo | O que significa | Onde pegar |
|---|---|---|
| Endpoint | URL base para onde o AIOS envia chamadas de runtime/modelo | OpenAI API ou Azure OpenAI/Foundry |
| API key | chave secreta que autentica chamadas de API | OpenAI API Keys ou Azure Keys and Endpoint |
| Deployment | nome da implantacao do modelo no Azure | Azure OpenAI/Foundry Deployments |
| Service token | credencial de servidor/servico, normalmente uma API key de service account ou chave aprovada | OpenAI Project Service Account ou Vault/KMS corporativo |
| Tenant ID | identificador de diretorio/organizacao, usado em fluxos enterprise/OAuth/Entra | Microsoft Entra ID ou configuracao corporativa |
| Sandbox Environment ID | nome/ID interno do ambiente aprovado para testes | definido pela equipe/projeto, ou portal/workspace quando existir |

## Caminho recomendado se voce nao sabe por onde comecar

Use **OpenAI API direta** se voce quer o caminho mais simples agora.

Voce precisa obter:

- `OPENAI_API_KEY`
- opcional: `OPENAI_PROJECT_ID`

O comando seguro do AIOS sera:

```powershell
$key = Read-Host "OpenAI API key oficial" -AsSecureString

.\scripts\rc5-start-openai-api-sandbox.ps1 `
  -OpenAIApiKey $key `
  -BaseUrl "https://api.openai.com/v1" `
  -ProjectId "proj_..." `
  -SandboxEnvironmentId "aios-rc5-openai-api-sandbox" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

Use **Azure OpenAI / Microsoft Foundry** se voce quer seguir a documentacao do Codex com Azure.

Voce precisa obter:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID`

O comando seguro do AIOS sera:

```powershell
$key = Read-Host "Azure OpenAI API key oficial" -AsSecureString

.\scripts\rc5-start-azure-foundry-sandbox.ps1 `
  -AzureOpenAIEndpoint "https://SEU_RESOURCE.openai.azure.com/openai/v1" `
  -AzureOpenAIApiKey $key `
  -Deployment "NOME_DO_DEPLOYMENT" `
  -SandboxEnvironmentId "aios-rc5-sandbox" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

## Como pegar no Azure / Foundry

1. Criar ou abrir uma assinatura Azure.
2. Abrir Microsoft Foundry / Azure AI Foundry.
3. Criar um projeto.
4. Selecionar um modelo Codex ou modelo aprovado no catalogo.
5. Implantar o modelo.
6. Copiar:
   - endpoint;
   - API key;
   - nome do deployment.

No formato da documentacao Microsoft, o `base_url` fica assim:

```txt
https://YOUR_RESOURCE_NAME.openai.azure.com/openai/v1
```

A chave deve ficar em variavel de ambiente ou Vault/KMS, nunca no frontend.

## Como pegar na OpenAI direta

1. Entrar no painel da OpenAI Platform.
2. Criar ou selecionar um Project.
3. Ir em API Keys.
4. Criar uma secret key.
5. Salvar a chave em local seguro, porque ela aparece uma unica vez.

Para service account:

1. Abrir Organization settings.
2. Selecionar o Project.
3. Ir em Members.
4. Criar Service account.
5. Salvar a API key do service account.

## O que nao fazer

- nao colar API key no React/frontend;
- nao salvar chave em arquivo `.env` dentro do ZIP publico;
- nao enviar chave em print, chat ou commit;
- nao usar chave pessoal como se fosse service account de producao;
- nao inventar endpoint ou deployment.

## Estado tecnico local

O contrato esta registrado no projeto. Tecnicamente, o backend so consegue invocar runtime real quando as credenciais aprovadas existem no processo do backend.

Isso e esperado e correto.

Sem credenciais reais:

```txt
blocked_until_secure_environment
```

Com credenciais reais e gates completos:

```txt
sandbox_live_ready
```
