# AIOS Codex Unlimited RC11 - Runtime Model Discovery

## Objetivo

A RC11 transforma a etapa de runtime em uma verificacao real e auditavel:

- confirmar se o ambiente seguro existe;
- consultar a lista real de modelos da OpenAI API quando autorizado;
- recomendar o `OPENAI_MODEL` disponivel;
- evitar sucesso falso quando falta chave, ambiente, live flag, Vault/KMS ou quota;
- manter a experiencia baseada em sessoes Codex, sem contador de tokens.

## Endpoint

```txt
GET /codex/runtime/model-discovery
```

O endpoint exige login e retorna:

```json
{
  "phase": "RC11_RUNTIME_MODEL_DISCOVERY",
  "provider": "openai_api",
  "status": "blocked_until_secure_environment | model_available | no_candidate_available | model_list_failed",
  "configuredModel": "gpt-5.2-codex",
  "availableCandidates": [],
  "recommendedModel": "",
  "selectedModelCommand": "",
  "networkCallPerformed": false,
  "secretsExposed": false,
  "missing": []
}
```

## Estados

`blocked_until_secure_environment` significa que o AIOS nao fez chamada externa porque algum gate obrigatorio esta ausente.

`model_available` significa que `/models` respondeu e pelo menos um candidato preferencial apareceu para a credencial configurada.

`no_candidate_available` significa que a credencial listou modelos, mas nenhum dos candidatos preferenciais apareceu.

`model_list_failed` significa que a chamada real para `/models` falhou e o erro foi redigido antes de entrar no relatorio.

## Gates de seguranca

A chamada real so ocorre quando estes itens existem na sessao do backend:

```txt
OPENAI_API_KEY
AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID
AIOS_OFFICIAL_SANDBOX_SECRET_STORE=vault|kms
AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true
CONTRACT_AUTHORITY_LOCK valido
```

Campos opcionais:

```txt
OPENAI_BASE_URL
OPENAI_PROJECT_ID
OPENAI_ORG_ID / OPENAI_ORGANIZATION
OPENAI_MODEL
```

## Script

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\rc11-runtime-readiness.ps1
```

O script gera:

```txt
release\RC11_RUNTIME_READINESS_REPORT.md
```

Ele nunca imprime `OPENAI_API_KEY`.

## MCP

O MCP core expõe:

```txt
aios.codex.runtime_model_discovery
```

## Frontend

No painel `Runtime Gateway`, o botao `Descobrir Modelo` chama o endpoint RC11 e mostra:

- estado da descoberta;
- modelo recomendado;
- se houve chamada real;
- se algum segredo foi exposto.

## Demonstracao honesta

Se a conta nao tiver credito/quota, a RC11 deve registrar `BLOCKED_BY_OPENAI_QUOTA` no relatorio. Isso ainda e um resultado util: prova que o caminho chegou no runtime externo, mas a execucao depende de billing/quota do projeto.
