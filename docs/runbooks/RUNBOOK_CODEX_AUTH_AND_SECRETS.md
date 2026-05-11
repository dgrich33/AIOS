# Runbook: Codex Auth e Segredos

## Objetivo
Tratar `auth.json`, service tokens, API keys e credenciais reais como segredos operacionais. O AIOS pode validar a presenca segura desses arquivos por caminho/status, mas nao deve ler, copiar, imprimir, commitar, empacotar ou expor o conteudo.

## Politica
- `auth.json` deve ser tratado como senha.
- `auth.json` nao deve entrar no Git, logs, tickets, ZIPs, builds, frontend, PDFs ou relatorios publicos.
- O app desktop nao deve pedir ao usuario para colar `auth.json`.
- O AIOS nao deve copiar `auth.json` entre maquinas.
- Validacoes de seguranca devem verificar apenas metadados seguros: caminho, existencia, status Git ignored/tracked e permissao esperada.
- Credenciais reais de runtime devem ficar em DPAPI local, Vault/KMS ou secret manager aprovado.

## Fluxo Seguro
1. Autentique o Codex pelo fluxo oficial do proprio Codex/ChatGPT/Enterprise.
2. Mantenha tokens no storage oficial do Codex ou no cofre do sistema operacional.
3. Para automacao privada, use runner confiavel e secret manager. Nunca use repositorio publico ou artefato de build.
4. Rode `scripts/secret-hygiene-check.ps1 -WriteReport` antes de empacotar ou fazer push.
5. Se qualquer segredo aparecer como tracked ou nao ignorado, pare a entrega, remova do Git e rotacione a credencial.

## Validacao Local
```powershell
.\scripts\secret-hygiene-check.ps1 -WriteReport
```

Resultado esperado:
```json
{
  "ok": true,
  "trackedForbiddenCount": 0,
  "unignoredForbiddenCount": 0
}
```

## Resposta a Incidente
1. Revogue ou rotacione a credencial afetada.
2. Remova o arquivo do Git e dos artefatos publicados.
3. Gere novo pacote apos `secret-hygiene-check.ps1` passar.
4. Anexe somente relatorio redigido; nunca anexe o segredo.
