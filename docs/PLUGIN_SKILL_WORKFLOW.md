# AIOS Codex Unlimited - Workflow de Plugins e Skills

## Objetivo

Definir como usar as skills e plugins uteis no projeto AIOS Codex Unlimited sem perder controle de seguranca, validacao e rastreabilidade.

Este projeto deve usar skills como apoio tecnico, nao como substituto dos gates oficiais do projeto. A fonte de verdade continua sendo:

- scripts de validacao;
- auditoria de contratos;
- auditoria de seguranca;
- Git diff/status;
- hashes de pacote;
- relatorios RC.

## Estado GitHub

Repositorio:

```txt
https://github.com/dgrich33/AIOS
```

Observacao operacional: o repositorio esta publico. Por isso, estes itens nunca devem entrar no GitHub:

- `.env` real;
- `license.cert`;
- bindings DPAPI;
- service tokens;
- chaves/API keys;
- bancos locais;
- logs;
- zips de release;
- binarios privados;
- checkpoints, pesos ou artefatos de modelo.

O `.gitignore` e o `.gitattributes` devem continuar protegendo esse limite.

## Skills uteis por tipo de trabalho

### 1. Superpowers

Uso:

- planejamento de etapas grandes;
- escrita de plano tecnico;
- debugging sistematico;
- verificacao antes de declarar uma etapa pronta.

Regra AIOS:

Antes de dizer que algo esta pronto, rodar verificacao fresca e citar o comando que passou.

### 2. GitHub

Uso:

- confirmar estado do repositorio;
- revisar branches, PRs e issues;
- criar PR quando houver trabalho em branch;
- acompanhar checks do GitHub Actions quando `gh` estiver instalado.

Regra AIOS:

Nao publicar artefato sensivel. Antes de `git push`, verificar staged files e procurar padroes de secrets.

### 3. Codex Security

Uso:

- scan de seguranca antes de release;
- revisar riscos em auth, RBAC, service tokens, redaction, runtime bridge, MCP e exports;
- investigar achados com fluxo de validacao antes de reportar.

Regra AIOS:

Achado de seguranca precisa ser evidenciado com arquivo/linha, impacto e mitigacao. Nada de conclusao vaga.

### 4. Build Web Apps

Uso:

- evoluir UI premium do Workbench;
- corrigir responsividade;
- revisar React/TypeScript;
- validar comportamento renderizado.

Regra AIOS:

Build passando nao basta para UI. Quando mudar interface, validar tela real com Browser ou Playwright.

### 5. Browser

Uso:

- abrir `http://127.0.0.1:5173`;
- capturar console, DOM e screenshots;
- testar fluxo login, sessoes, Workbench, runtime binding, snapshots e handoff.

Regra AIOS:

Usar Browser primeiro quando disponivel. Se falhar, registrar fallback para Playwright.

### 6. PDF

Uso:

- gerar ou validar one-pagers, relatorios executivos e documentos PDF;
- extrair texto de PDFs recebidos para analise segura.

Regra AIOS:

Nao executar anexos. Validar texto/estrutura e, quando possivel, renderizar paginas para revisao visual.

### 7. CodeRabbit

Uso:

- revisar PRs ou diffs importantes;
- capturar riscos de qualidade antes de merge;
- complementar revisao humana.

Regra AIOS:

CodeRabbit e apoio. Correcoes precisam passar pelos scripts locais do AIOS antes de serem aceitas.

### 8. Figma

Uso:

- apenas se houver design, referencia visual ou pedido especifico de tela;
- criar ou implementar design system visual do produto.

Regra AIOS:

Nao usar Figma para alterar arquitetura do produto. Ele serve para UI/design.

## Skills nao prioritarias neste momento

Estas skills existem, mas so devem ser usadas se o escopo pedir claramente:

- Stripe: somente se houver billing real;
- Supabase/Postgres: somente para otimizacao de banco ou schema;
- plugin-creator/skill-creator: somente se formos empacotar novas skills;
- imagegen: somente para asset visual bitmap, nao para documentos legais.

## Fluxo padrao para qualquer etapa nova

1. Ler `AGENTS.md`.
2. Identificar qual skill/plugin se aplica.
3. Fazer mudanca pequena e rastreavel.
4. Rodar validacoes relevantes.
5. Rodar auditoria Git ou manifesto RC19.
6. Se aprovado, commitar em branch ou `main` conforme orientacao do momento.
7. Publicar no GitHub somente depois de varrer staged files contra secrets/artefatos restritos.

## Comandos base

Validacao local principal:

```powershell
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
cd .\backend
..\.venv\Scripts\python.exe -m pytest .\tests -q
cd ..\frontend
npm run build
cd ..\mcp\aios-mcp-core
npm run build
cd ..\aios-mcp-repo
npm run build
cd ..\..
```

Auditoria completa quando possivel:

```powershell
.\scripts\rc19-validate-and-audit.ps1
```

Auditoria antes de push:

```powershell
git status -sb
git diff --cached --name-only
git grep --cached -n -I -E "sk-[[:alnum:]_-]{20,}|Bearer[[:space:]]+[[:alnum:]_.-]{20,}|eyJ[[:alnum:]_-]+\.[[:alnum:]_-]+\.[[:alnum:]_-]+"
```

## Criterio de pronto

Uma etapa so pode ser chamada de pronta quando:

- os arquivos alterados foram identificados;
- a skill/plugin aplicavel foi usada ou justificada como nao necessaria;
- os scripts relevantes passaram;
- nao ha segredo ou artefato restrito no staged diff;
- o estado GitHub esta claro.
