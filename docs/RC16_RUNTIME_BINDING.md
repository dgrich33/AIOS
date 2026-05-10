# AIOS Codex Unlimited RC16 - Runtime Binding Gate

## Objetivo

A RC16 adiciona uma leitura tecnica do binding de runtime. Ela confirma se a licenca local, contratos protegidos, provider, credencial real, ambiente sandbox, Vault/KMS e live flag estao prontos para uma chamada real por adapter oficial.

## Endpoint

```txt
GET /runtime/binding/status
```

O endpoint retorna:

- estado do escopo;
- estado do binding tecnico;
- provider selecionado;
- referencia da credencial esperada;
- ambiente sandbox;
- Vault/KMS;
- live flag;
- modelos aprovados;
- operacoes aprovadas;
- itens pendentes.

## Regras

- Nao armazena segredo.
- Nao retorna valor de segredo.
- Nao altera auth.json.
- Nao cria credencial falsa.
- Nao muda a unidade do produto para token.
- Mantem a experiencia baseada em sessoes Codex.

## Estados

| Estado | Significado |
|---|---|
| `blocked_by_scope` | license.cert ou contratos nao conferem. |
| `awaiting_secure_runtime_binding` | escopo aprovado, mas falta credencial/ambiente/Vault/KMS/live flag. |
| `live_runtime_ready` | escopo e binding tecnico estao prontos para adapter oficial. |

## Script

```powershell
.\scripts\runtime-binding-status.ps1 -WriteReport
```

Relatorio:

```txt
release/RC16_RUNTIME_BINDING_REPORT.md
```
