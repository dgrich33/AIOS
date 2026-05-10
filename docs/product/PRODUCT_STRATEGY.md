# AIOS Livre / Codex Unlimited - Estrategia de Produto

## Tese

AIOS Livre / Codex Unlimited deve ser um produto Windows/desktop separado, com experiencia premium de desenvolvimento assistido por IA. O diferencial principal e o usuario sentir que trabalha em uma sessao continua, com governanca e agentes, sem ser interrompido por contadores de tokens ou creditos.

Mensagem principal:

```txt
Codex sem limites. Desenvolvimento sem interrupcoes.
```

Unidade do produto:

```txt
Sessoes Codex
```

## Posicionamento

O AIOS nao deve depender de um unico modelo. Ele deve ser model-adaptive:

```txt
GPT-5.3-Codex, GPT-5.5, GPT-5.4 ou modelos futuros podem entrar no mesmo Runtime Broker.
```

`gpt-5.2-codex` deve ser tratado como modelo documentado/historico de programacao agentica e compatibilidade, nao como pino unico do produto. A documentacao oficial atual mostra `gpt-5.2-codex` como documentado e tambem marcado como deprecated na lista de snapshots/aliases. Se o acesso a `gpt-5.2-codex` for aprovado, ele entra como provider/modelo de compatibilidade no broker. A rota principal deve mirar `gpt-5.5` ou o modelo Codex mais atual aprovado para a credencial.

## Publico-alvo

- Times enterprise que precisam de refactor, code review, debug, migracao e manutencao continua.
- Desenvolvedores que querem uma experiencia de agente de programacao sem ficar gerenciando tokens.
- Lideres tecnicos que precisam de auditoria, logs, diff, rollback, snapshots e relatorios.
- Equipes que querem governanca sobre tools, MCP, execucao local/cloud e aprovacao humana.

## Cinco pilares

### 1. AIOS Runtime Broker

Camada que escolhe o runtime/modelo conforme disponibilidade, permissao e risco.

Providers planejados:

- Official Codex Runtime, quando provisionado;
- OpenAI API autorizada, quando existir budget/credencial;
- GitHub Models demo, para demonstracoes controladas;
- Puter.js user-pays, para demo browser sem custo direto do desenvolvedor;
- Ollama local/cloud, para fallback local ou cloud de desenvolvimento;
- adapter simulado controlado, somente quando claramente rotulado como demo.

### 2. Unlimited Session Engine

"Unlimited" significa experiencia sem limite visivel ao usuario, nao ausencia de custo interno.

Regras:

- sem contador de tokens;
- sem saldo de creditos;
- sem quota semanal na UI;
- sessoes longas com heartbeat;
- checkpoint automatico;
- continuacao por handoff;
- degradacao por estabilidade/abuso/risco, nunca por mensagem de "tokens acabaram".

### 3. Agent Room

Transformar a experiencia em uma sala de agentes especializados:

- Architect Agent: planeja arquitetura e escopo;
- Builder Agent: implementa alteracoes;
- Debug Agent: investiga falhas;
- Security Review Agent: revisa riscos e segredos;
- Code Review Agent: revisa diff e regressao;
- Refactor Agent: grandes migracoes;
- Release Agent: empacota, valida e prepara release;
- Docs Agent: atualiza documentacao;
- UI/UX Agent: melhora Workbench e experiencia visual.

### 4. Workbench Premium

O Workbench deve virar o painel central do produto:

- timeline da sessao;
- arquivos alterados;
- diff visual;
- status de build;
- logs de teste;
- snapshots;
- handoff;
- risk score;
- policy decisions;
- eventos MCP/tools;
- botao de relatorio executivo redigido.

### 5. Cloud / No-Key Mode

O produto deve suportar demonstracao e operacao sem chave de API do usuario final no app.

Modelo recomendado:

```txt
AIOS Delegated Cloud Runtime
```

ou:

```txt
AIOS No-Key Codex Runtime
```

Principios:

- sem modelo local obrigatorio;
- sem API key do usuario salva no app;
- autenticacao delegada;
- workspace isolado por sessao;
- auditoria por sessao;
- runtime cloud delegado quando aprovado;
- demo sem chave marcada como demo, nunca como runtime oficial ativo.

## Nao objetivos

- Nao embutir pesos, checkpoints ou binarios privados em build publico.
- Nao alterar arquivos locais de autenticacao do usuario para contornar plano, limite ou autenticacao.
- Nao usar multi-account para evitar limites.
- Nao declarar runtime vivo quando `runtime-binding-status.ps1` ainda indica pendencia.
- Nao transformar modelos locais ou simulados em "modelos oficiais" sem comprovacao tecnica.
- Nao expor segredos no frontend, GitHub, logs, ZIP, EXE, MSI ou PDF.

## Criterio de sucesso da primeira versao separada

O produto separado e aceitavel quando entregar:

- Workbench premium navegavel;
- Runtime Broker com status claro por provider;
- No-Key demo rotulada corretamente;
- Agent Room com papeis e fluxo de aprovacao;
- Repo Memory com mapa, checkpoints e diff;
- audit/redaction em todas as acoes relevantes;
- pacote Windows que nao inclui segredos nem artefatos privados;
- documentacao executiva sem claims ambiguos.
