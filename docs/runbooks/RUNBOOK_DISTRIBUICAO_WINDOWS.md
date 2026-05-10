# Runbook - Distribuicao Windows

## Objetivo

Definir como empacotar, assinar, entregar e atualizar o AIOS Codex Unlimited no Windows.

## Formatos

| Fase | Formato |
|---|---|
| RC/Beta | ZIP portatil |
| Release oficial | EXE assinado + MSI |
| Canal oficial | Launcher OpenAI aprovado |

## Regras de pacote publico

- Excluir `.env`, `.env.local`, `auth.json`, `credentials.json`.
- Excluir `.aios-secure`.
- Excluir bancos locais de teste.
- Excluir logs e reports temporarios.
- Excluir artefatos restritos e credenciais.
- Excluir pesos, checkpoints e bins privados.

## Processo de release

1. Rodar testes.
2. Rodar auditoria contratual.
3. Rodar package scan.
4. Gerar ZIP.
5. Calcular SHA256.
6. Assinar EXE/MSI quando aplicavel.
7. Registrar hash/version.
8. Publicar apenas no canal aprovado.

## Comandos

```powershell
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
.\scripts\enterprise-check.ps1
.\scripts\rc17-package.ps1
Get-FileHash -Algorithm SHA256 -LiteralPath "C:\AIOS\aios-codex-unlimited-enterprise-v2-RC17.zip"
```

## Auto-update e rollback

- Auto-update deve validar assinatura.
- Rollback deve voltar para versao assinada anterior.
- Atualizacao falha nao pode apagar dados locais de sessoes/snapshots.
- Runtime vivo deve ser desativado antes de rollback se houver incidente.
