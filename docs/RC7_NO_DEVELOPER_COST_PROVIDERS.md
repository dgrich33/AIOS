# AIOS Codex Unlimited RC7 - Provedores sem custo direto do desenvolvedor

## Objetivo

A RC6 provou o caminho real da OpenAI API, mas a chamada ficou bloqueada por `insufficient_quota`. Isso confirma que o codigo chegou na OpenAI, mas tambem mostra que o projeto nao deve depender de creditos pessoais do desenvolvedor para continuar evoluindo.

A RC7 adiciona uma estrategia oficial dentro do AIOS:

```txt
Sem custo direto do desenvolvedor.
Sem chave OpenAI exposta no frontend.
Sem transformar tokens em unidade do produto.
Unidade continua sendo Sessoes Codex.
```

## Caminho recomendado agora

### 1. Puter.js User-Pays

Este e o caminho principal para desenvolvimento e demo quando nao ha budget de API do desenvolvedor.

- roda no browser;
- nao exige `OPENAI_API_KEY` no backend AIOS;
- o usuario autentica/paga no provedor quando necessario;
- o resultado e registrado no Workbench como evento `codex.runtime.completed`;
- nao salva segredo Puter/OpenAI no backend.

Modelos configurados na UI:

```txt
openai/gpt-5.3-codex
openai/gpt-5.2-codex
openai/gpt-5.1-codex
openai/gpt-5.1-codex-mini
openai/gpt-5.1-codex-max
```

Botao na UI:

```txt
No Developer Cost -> Puter User-Pays
```

## Outros provedores catalogados

Estes caminhos ficam registrados para adapter futuro, com limites e termos proprios:

- OpenRouter Free Models;
- NVIDIA NIM API Catalog;
- Groq Console;
- GitHub Models;
- Google AI Studio / Gemini API;
- Cloudflare Workers AI;
- Ollama Local/Cloud.

## Importante

Free tier e user-pays nao significam "sem limites universais". Significam que o custo direto nao sai da conta pessoal do desenvolvedor do AIOS. Cada provedor pode ter limites, termos, autenticacao propria, rate limit e politica de dados.

Para release oficial do plano AIOS Codex Unlimited, o caminho correto continua sendo:

- `OfficialCodexRuntimeAdapter`;
- entitlement oficial;
- service tokens escopados;
- auditoria;
- redaction;
- regras de acesso restrito, sandbox e distribuicao Windows conforme contrato soberano assinado em `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`.

## Endpoints RC7

```txt
GET /runtime/no-developer-cost/providers
GET /runtime/no-developer-cost/recommendation
```

## Como validar

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\scripts\rc7-validate.ps1
```
