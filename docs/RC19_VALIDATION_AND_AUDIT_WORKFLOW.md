# RC19 - Fluxo de Validacao e Auditoria

## Objetivo

Padronizar o criterio de prontidao do AIOS Codex Unlimited: validacoes por scripts sao a fonte principal de confianca, e a auditoria de alteracoes registra exatamente o que mudou.

## Regra pratica

Use este fluxo antes de congelar qualquer RC:

```powershell
.\scripts\rc19-validate-and-audit.ps1
```

Se o projeto estiver em um repositorio Git, o script registra:

- `git status --short`
- `git diff --stat`
- `git diff --name-only`

Se o projeto nao estiver em Git, o script gera um manifesto SHA256 dos arquivos relevantes e compara com a linha de base anterior.

## Primeira linha de base sem Git

Na primeira execucao controlada, crie a linha de base:

```powershell
.\scripts\rc19-validate-and-audit.ps1 -UpdateBaseline
```

Depois disso, cada execucao compara arquivos adicionados, alterados e removidos pelo hash SHA256.

## Validacoes executadas

O script roda:

- `contract-authority.ps1 verify`
- `contract-docs-audit.ps1`
- testes backend
- build frontend
- build MCP core
- build MCP repo
- Playwright, exceto com `-Quick`
- `enterprise-check.ps1`, se o backend estiver rodando
- `runtime-binding-status.ps1 -WriteReport`, se o backend estiver rodando

## Saidas

Cada execucao cria uma pasta em:

```txt
release/validation-audit-YYYYMMDD-HHMMSS/
```

Ela contem logs por etapa, manifesto de arquivos quando necessario, comparacao de alteracoes e o relatorio:

```txt
RC19_VALIDATION_AND_AUDIT_REPORT.md
```

## Interpretacao

- `PASS`: etapa validada.
- `FAIL`: falha critica que precisa ser corrigida antes de congelar RC.
- `SKIPPED`: etapa nao executada por pre-condicao ausente, como backend desligado.
- `SKIPPED_OR_FAILED_OPTIONAL`: etapa opcional falhou sem invalidar as validacoes principais.

O estado correto para entrega e: validacoes criticas sem `FAIL`, auditoria gerada e, quando houver pacote, hash final registrado.
