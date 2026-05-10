# Self-Hosted Runtime Provider Policy

## Objetivo

Definir como o AIOS Livre / Codex Unlimited pode operar um runtime delegado sem chave de API do usuario final e sem dependencia obrigatoria de uma API comercial especifica.

## Direcao aprovada

```txt
AIOS e model-adaptive e provider-agnostic.
```

O AIOS pode operar ou contratar runtime proprio, desde que o provider seja rotulado de forma honesta e auditavel.

## Providers self-hosted permitidos para estudo/MVP

| Provider | Uso | Observacao |
|---|---|---|
| `vllm` | inferencia GPU cloud/self-hosted | Recomendado para alta performance. |
| `tgi` | inferencia Hugging Face Text Generation Inference | Bom para serving padronizado. |
| `ollama_server` | dev/staging e demos controladas | Nao declarar como modelo oficial Codex. |
| `llamafile_server` | portable/dev/demo | Bom para simplicidade, nao para claims enterprise de alta escala. |
| `azure_ai`, `together`, `fireworks`, `openrouter` | comercial opt-in | Apenas se a organizacao contratar explicitamente e aceitar termos. |

## Configuracao

```env
AIOS_INFERENCE_PROVIDER=vllm
AIOS_INFERENCE_BASE_URL=https://infer.example.local/v1
AIOS_INFERENCE_MODEL_ID=qwen2.5-coder-32b-instruct
AIOS_INFERENCE_API_KEY=
AIOS_MODEL_POLICY_JSON=./config/model-policy.json
```

Regra:

```txt
AIOS_INFERENCE_API_KEY pertence ao backend/secret store do AIOS, nunca ao frontend nem ao usuario final.
```

## Interface minima do provider

```txt
list_models()
health()
generate(messages, options)
cancel(request_id)
capabilities()
embed(input)
```

Resposta minima de `list_models()`:

```json
{
  "id": "qwen2.5-coder-32b-instruct",
  "provider": "vllm",
  "contextWindow": 32768,
  "license": "provider_declared",
  "capabilities": ["streaming", "json_mode", "code_generation"],
  "officialCodexRuntime": false
}
```

## Regras de UX

Permitido:

- `Modelo: qwen2.5-coder-32b-instruct via AIOS Cloud Runtime`;
- `Modo: AIOS Delegated Cloud Runtime`;
- `Sem chave de API do usuario no app`.

Proibido:

- `GPT-5.5 local`;
- `Codex oficial local`;
- `OpenAI sem autenticação`;
- `modelo extraido`;
- `sem limites tecnicos`;
- `runtime oficial ativo` sem binding real.

## Governanca

Cada provider deve declarar:

- modelo;
- origem;
- licenca;
- capacidade;
- limite operacional;
- retencao;
- logging;
- politicas de dados;
- riscos de privacidade;
- custo interno estimado;
- fallback permitido.

## Fallback e degradacao

Fallback deve ser honesto:

| Situacao | Acao |
|---|---|
| provider principal indisponivel | tentar provider secundario permitido. |
| modelo maior saturado | usar modelo menor e avisar como degradacao de saude, nao como quota. |
| workspace com risco alto | mudar para modo plan-only ou pedir approval. |
| provider demo ativo | rotular como demo. |
| simulated adapter ativo | rotular como simulacao controlada. |

## Criterios de aceite

- Provider aparece no Runtime Broker com `officialCodexRuntime=false`.
- Workbench mostra modo correto.
- Nenhuma chave aparece no frontend.
- Auditoria registra provider/model/capabilities.
- Package scan nao encontra segredos ou modelos privados.
