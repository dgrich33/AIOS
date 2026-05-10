# AIOS Codex Unlimited RC13 - Final Status

## Status

RC13 adiciona a camada de pacote executivo e validacao local controlada sobre a RC12.

## Sistemas adicionados

- Local License Manager para `license.cert` como prova local de autorizacao;
- endpoint `/license/status`;
- instalador assistido Windows;
- launcher de demo local;
- comando de voz no Workbench;
- gerador de relatorio executivo local;
- empacotamento RC13 com scan de artefatos restritos;
- pedido de extensao de licenca/runtime em portugues.

## Garantias de seguranca

- `license.cert` ativa o entitlement local `aios_codex_unlimited`;
- `license.cert` registra autorizacao de runtime enterprise no AIOS;
- service token, Vault/KMS ou Secure Runtime Bridge executam a autenticacao tecnica, rotacao e auditoria;
- segredo nao e exposto no frontend;
- binarios privados, pesos, checkpoints e arquivos de autenticacao continuam fora do pacote publico;
- documentos soberanos do contrato continuam protegidos pelo lock.

## Comandos

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
.\.venv\Scripts\python.exe .\scripts\generate_license.py
.\scripts\start_demo.ps1
```

## Validacao recomendada

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2\backend
C:\AIOS\aios-codex-unlimited-enterprise-v2\.venv\Scripts\python.exe -m pytest .\tests -q

Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2\frontend
npm run build
npm run test:e2e

Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\rc13-package.ps1
```

## Pacote esperado

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2-RC13.zip
```

## Proxima etapa

Integrar credenciais reais do provider aprovado quando forem emitidas: endpoint oficial, service token, tenant/project e Vault/KMS. Ate la, o projeto fica preparado para execucao local, Runtime Broker e validacao de experiencia.
