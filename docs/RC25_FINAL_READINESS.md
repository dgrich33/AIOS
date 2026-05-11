# RC25 - Final Readiness

## Objetivo

O RC25 consolida o estado final entregavel do AIOS Codex Unlimited como release candidate funcional. Ele separa claramente:

- **pronto para demo local e pacote publico escaneado**;
- **bloqueado para producao real enquanto o binding oficial de runtime nao estiver ativo**.

## Backend

Endpoint:

```http
GET /release/final-readiness
```

O endpoint retorna:

- `deliverableState`: estado do pacote/demo local;
- `productionState`: estado de producao real;
- `readyForLocalDemo`;
- `readyForPublicPackage`;
- `readyForProduction`;
- `criteria`: criterios auditaveis;
- `blockingItems`: bloqueios atuais;
- `package.script`: `scripts/rc25-package.ps1`;
- `secretsExposed: false`.

## Criterios RC25

| Criterio | Papel |
|---|---|
| `contract_authority` | license.cert + lock dos documentos soberanos |
| `runtime_broker` | Runtime Broker model-adaptive sem segredo exposto |
| `approval_gate` | Approval Gate humano para comandos, patches e tools sensiveis |
| `codex_delegated_auth_boundary` | AIOS nao le nem copia `auth.json` |
| `secure_runtime_bridge` | Bridge seguro sem incluir conteudo privado ou restrito no pacote |
| `public_package_safety` | Manifesto Windows sem incluir conteudo privado ou restrito |
| `official_runtime_binding` | Unico criterio que libera producao real quando endpoint, credencial, tenant, sandbox id, Vault/KMS e live flag estiverem presentes |

## Workbench

O painel `Final Readiness RC25` mostra:

- readiness score;
- demo local;
- pacote publico;
- producao real;
- script de pacote;
- criterios e evidencias.

## Pacote Seguro

Script:

```powershell
.\scripts\rc25-package.ps1
```

O script executa:

1. `contract-authority.ps1 verify`
2. `contract-docs-audit.ps1`
3. `public-repo-safety-audit.ps1`
4. `secret-hygiene-check.ps1 -WriteReport`
5. `runtime-binding-status.ps1 -WriteReport`
6. copia para staging excluindo `.git`, `.env`, `auth.json`, bancos locais, `release`, `node_modules`, `.venv`, artefatos privados e pesos de modelo
7. `restricted-package-scan.ps1`
8. gera `C:\AIOS\aios-codex-unlimited-enterprise-v2-RC25-FINAL.zip`
9. grava hash SHA256 em `release/RC25_FINAL_READINESS_REPORT.md`

## Limite Honesto

RC25 nao transforma demo local em runtime oficial vivo. Producao real continua condicionada ao binding oficial ativo e validado por `runtime-binding-status.ps1`.
