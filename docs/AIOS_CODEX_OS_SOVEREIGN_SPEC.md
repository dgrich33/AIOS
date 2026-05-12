# AIOS Codex OS - Especificacao Sovereign v1.1

## Objetivo

Transformar o AIOS em um sistema operacional cognitivo para missoes de engenharia, com Mission Desk, Agent Room, Evidence Vault, Memory Ledger, Tool Execution Kernel e Cognitive Organ Router.

Esta versao separa claramente:

- prototipo local vivo;
- ponte delegada ao Codex CLI local, quando disponivel;
- orgaos beta/open-weight, quando artefatos assinados existirem;
- orgaos oficiais, quando runtime/binding oficial for provisionado;
- producao oficial, que continua exigindo signoff e binding completo.

## Realidades de orgaos

| Reality | Significado |
|---|---|
| `aios_native_runtime` | Camada AIOS propria de sessao, memoria, agentes e governanca. |
| `codex_plan_bridge` | Ponte local para Codex CLI autenticado, sem leitura de `auth.json` pelo AIOS. |
| `beta_open_weight` | Orgao especificado por pacote `.organ`; so fica ativo quando o artefato local existir. |
| `official_capsule` | Orgao oficial cifrado/provisionado; pendente de entrega oficial. |
| `experimental` | Pesquisa, nao liberado para fluxo principal. |

## COS v1.1

Arquivo fonte:

```text
aios-codex-specs/proto/aios/cos/v1/cos.proto
```

Metodos formais:

```text
Identify
Capabilities
Attest
Lease
Generate
Patch
Verify
Reality
DelegateStatus
```

`DelegateStatus` e usado pelo `codex.plan.core`; orgaos beta/oficiais podem retornar `UNIMPLEMENTED`.

## SEP v0.9a

Arquivo fonte:

```text
aios-codex-specs/sep/sep_2026_05_A.json
```

```json
{
  "product": "AIOS Codex OS",
  "mode": "sovereign",
  "allow_delegate": true,
  "delegate_whitelist": ["codex.plan.core"],
  "gpu_budget_sec_per_mission": 1800,
  "lease_max_ttl_sec": 600,
  "policy_revision": "2026-05-A"
}
```

## Codex Plan Core

`codex.plan.core` e um `official_delegated_organ` que usa o Codex CLI local quando o comando esta disponivel e autorizado.

Garantias da implementacao atual:

- nao le `auth.json`;
- nao copia tokens;
- nao usa API key do AIOS;
- executa via `codex exec --ignore-user-config --ignore-rules --ephemeral --disable plugins --json`;
- registra `cliVersion` e status no Memory/Audit flow;
- se o plano estiver em limite de uso, o AIOS mostra a falha real, sem resposta falsa.

Limite atual:

- ainda nao existe `codex serve --local-bridge` neste checkout local; o transporte implementado e `codex_exec_json_ephemeral`.

## Router v1.1

```yaml
routing_rules:
  - when: intent.code && organ_available(codex_plan_core)
    use: codex.plan.core
  - when: intent.code
    use: aios_code.beta.organ
  - when: intent.ui || intent.vision
    use: aios_multimodal.beta.organ
  - when: intent.plan || intent.arch
    use: aios_strategic.beta.organ
  - default: aios_native.microcluster.organ
```

## Policy Sentinel DSL v0.3

Arquivo fonte:

```text
aios-codex-specs/policy/sentinel-default.v0.3.aiosdsl
```

Regras padrao:

```text
allow organ:codex.plan.core role:*
deny tool:TerminalRunner cmd:rm-recursive
limit rate codex.plan.core per_minute 30
require verify_pass before merge
mask log .*api_key.*
```

O parser local fica em:

```text
aios-codex-fabric/sentinel/sentinel_dsl.py
```

## Hot-Swap Flow

Fluxo esperado:

1. Router inicia usando `codex.plan.core` quando o Codex CLI local esta disponivel.
2. Se a ponte Codex falha por quota, socket ausente ou CLI indisponivel, o Router troca a missao para `aios_code.beta.organ`.
3. Quando a ponte volta, novas missoes de codigo retornam para `codex.plan.core`.
4. Missoes em andamento mantem o orgao original para preservar determinismo da evidencia.

GIF do Reality Panel:

```text
docs/assets/reality-panel-hot-swap.gif
```

## Endpoints implementados

```text
GET /runtime/sovereign/status
GET /runtime/sovereign/delegate-status
```

## UI implementada

Painel:

```text
AIOS Codex OS Sovereign
```

Mostra COS, SEP, Policy Sentinel, active code organ, orgaos cognitivos, realidade, status e estado do Codex Plan Core.

## Criterio honesto de disponibilidade

Um orgao so pode aparecer como `available` se:

- Codex Plan Core: Codex CLI esta disponivel, autorizado e executavel localmente.
- AIOS Native Micro-Cores: runtime AIOS native esta habilitado.
- Beta/open-weight: manifest `.organ` local existe.
- Official capsule: binding/runtime oficial completo existe.

Caso contrario o status deve ser `specified_pending_artifact`, `missing` ou equivalente.
