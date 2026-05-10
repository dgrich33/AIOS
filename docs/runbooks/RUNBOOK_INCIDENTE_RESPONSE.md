# Runbook - Resposta a Incidente

## Objetivo

Definir o processo de deteccao, contencao, investigacao, comunicacao e recuperacao em incidentes do AIOS Codex Unlimited.

## Severidades

| Severidade | Exemplo |
|---|---|
| SEV1 | Credencial exposta, uso indevido de runtime vivo, exfiltracao de artefato restrito |
| SEV2 | Falha de redaction, abuso de tool calling, build publico com item indevido |
| SEV3 | Erro operacional sem exposicao de segredo |

## Deteccao

Fontes:

- audit logs;
- runtime binding report;
- abuse evaluator;
- policy guardrails;
- package scan;
- alertas de provider oficial;
- logs do Workbench.

## Contencao

1. Pausar runtime vivo.
2. Revogar token/API key no provider.
3. Remover binding DPAPI local quando aplicavel.
4. Bloquear tenant/identity profile afetado.
5. Parar distribuicao do pacote afetado.
6. Preservar logs redigidos para investigacao.

## Investigacao

Coletar:

- horario;
- actorId;
- tenantId;
- sessionId;
- modelId;
- toolName;
- policyDecision;
- requestId;
- pacote/hash afetado;
- caminho local aprovado;
- impacto.

## Comunicacao

Escalonar para:

- responsavel AIOS;
- representante tecnico OpenAI/Codex;
- seguranca/compliance;
- responsavel por tenant afetado quando aplicavel.

## Recuperacao

1. Emitir nova credencial.
2. Atualizar Vault/KMS.
3. Recriar binding local se autorizado.
4. Rodar validacoes:

```powershell
.\scripts\contract-authority.ps1 verify
.\scripts\runtime-binding-status.ps1 -WriteReport
.\scripts\enterprise-check.ps1
```

5. Registrar fechamento do incidente com evidencias redigidas.
