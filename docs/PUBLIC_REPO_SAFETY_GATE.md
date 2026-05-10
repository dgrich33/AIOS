# Public Repo Safety Gate

## Objetivo

Proteger o repositório público `dgrich33/AIOS` contra vazamento acidental de segredos, artefatos restritos, endpoints internos ou claims sensíveis.

## Script

```powershell
.\scripts\public-repo-safety-audit.ps1 -WriteReport
```

O relatório é salvo em:

```txt
release/PUBLIC_REPO_SAFETY_AUDIT.md
```

`release/` é ignorado pelo Git e não entra no pacote público.

## O que o gate bloqueia

- `.env` real;
- `license.cert`;
- `auth.json`;
- `credentials.json`;
- binding DPAPI;
- service token;
- API key;
- bancos locais;
- logs;
- zips, executáveis e instaladores;
- checkpoints, pesos e artefatos de modelo;
- padrões de segredo como API keys, JWTs, bearer tokens e private keys;
- endpoints ou contatos internos aparentes;
- claims absolutos que confundem runtime real com simulação.

## Contratos soberanos

Alguns documentos legais podem conter termos sensíveis por decisão do projeto. O gate não edita esses documentos automaticamente.

Se uma ocorrência estiver em `docs/legal/`, o caminho correto é:

1. avaliar se o repositório deve permanecer público;
2. mover a documentação sensível para pacote privado; ou
3. obter autorização explícita antes de sanitizar o documento soberano.

Para auditoria controlada sem bloquear contratos legais:

```powershell
.\scripts\public-repo-safety-audit.ps1 -WriteReport -AllowSensitiveContractDocs
```

## Uso antes de push

Antes de qualquer push:

```powershell
git status -sb
git diff --cached --name-only
git grep --cached -n -I -E "sk-[[:alnum:]_-]{20,}|Bearer[[:space:]]+[[:alnum:]_.-]{20,}|eyJ[[:alnum:]_-]+\.[[:alnum:]_-]+\.[[:alnum:]_-]+"
.\scripts\public-repo-safety-audit.ps1 -WriteReport
```

## Critério

O estado ideal para repositório público é:

```txt
Public repo safety audit OK
```

Se o gate falhar, tratar o resultado como bloqueio de publicação até que o achado seja removido, sanitizado ou formalmente movido para pacote privado.
