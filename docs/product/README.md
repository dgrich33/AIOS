# AIOS Livre / Codex Unlimited - Produto Separado

## Objetivo

Este diretorio define o plano de produto separado para o AIOS Livre / Codex Unlimited.

O foco do produto nao e "modelo secreto sem API" nem "peso local". O foco e uma experiencia Windows/desktop premium baseada em:

- Sessoes Codex, nao tokens;
- Workbench premium;
- governanca enterprise;
- agentes especializados;
- snapshots e handoff;
- auditoria e redaction;
- marketplace de ferramentas;
- runtime cloud delegado;
- demo sem chave de API do usuario, quando o runtime oficial ainda nao estiver provisionado.

## Documentos

| Arquivo | Finalidade |
|---|---|
| `PRODUCT_STRATEGY.md` | Posicionamento, publico-alvo, pilares e regras de experiencia. |
| `RESEARCH_SYNTHESIS.md` | Pesquisa externa com fontes e ideias aproveitaveis. |
| `TECHNICAL_BLUEPRINT.md` | Arquitetura do produto separado e limites de seguranca. |
| `DEMO_NO_KEY_AND_PLAN_B.md` | Como demonstrar sem chave do usuario sem fingir runtime oficial. |
| `IMPLEMENTATION_ROADMAP.md` | Roadmap de execucao por RCs futuras. |
| `TEAM_IDEAS_INTAKE_2026_05_10.md` | Consolidacao das ideias da equipe e decisoes aceitas/bloqueadas. |
| `CODEX_DELEGATED_RUNTIME_AUTH.md` | Caminho seguro para Codex app-server com ChatGPT/Enterprise sign-in. |
| `SELF_HOSTED_RUNTIME_PROVIDER_POLICY.md` | Politica para providers self-hosted/comerciais sem chave do usuario no app. |
| `PRODUCT_THREAT_MODEL.md` | Threat model do produto separado. |

## Regras de governanca

Este produto separado deve respeitar:

- `docs/CONTRACT_AUTHORITY.md`;
- `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`;
- `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`;
- `docs/SECURE_TEXT_SOURCE_REGISTER.md`;
- `docs/PUBLIC_REPO_SAFETY_GATE.md`.

Os documentos soberanos nao devem ser alterados sem autorizacao explicita.

## Invariante do produto

```txt
AIOS e baseado em Sessoes Codex.
Nao mostrar contador de tokens, saldo de tokens, pacote de credito ou quota semanal ao usuario final.
```
