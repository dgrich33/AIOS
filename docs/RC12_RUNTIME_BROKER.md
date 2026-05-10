# AIOS Codex Unlimited RC12 - Runtime Broker

## Objetivo

A RC12 adiciona uma camada nova ao AIOS: o **AIOS Runtime Broker** com **AIOS Cognitive Runtime Mesh**.

Essa camada nao substitui nem apaga RC11, tokens, OpenAI API, service tokens, MCP ou adapters existentes. Ela adiciona uma rota real alternativa para execucao de modelo sem exigir que o desenvolvedor mantenha uma API key OpenAI central.

## Sistema de inteligencia

Nome:

```txt
AIOS Cognitive Runtime Mesh
```

Funcao:

- escolher o melhor runtime disponivel;
- montar a chamada como sessao Codex premium;
- aplicar estrutura de planejamento, execucao e revisao;
- registrar auditoria e eventos no Workbench;
- manter o produto baseado em sessoes Codex;
- nao exibir contador, saldo ou quota.

Limite de afirmacao:

```txt
AIOS Cognitive Runtime Mesh e uma camada de orquestracao/runtime sobre modelos disponiveis. Ela nao e um novo checkpoint proprietario de modelo base.
```

## Providers

### official_openai_codex

Usa o caminho oficial OpenAI/Codex quando o ambiente seguro esta pronto.

### ollama_local_cloud

Usa:

```txt
http://localhost:11434/api/chat
```

Modelo inicial:

```txt
deepseek-v4-pro:cloud
```

Esse caminho nao exige `OPENAI_API_KEY` do desenvolvedor. O acesso cloud depende do Ollama local estar instalado/logado.

### puter_user_pays_browser

Provider browser/user-pays ja registrado na RC7. Ele continua como caminho frontend e nao recebe segredo no backend.

## Endpoints

```txt
GET  /runtime/broker/providers
GET  /runtime/broker/status
POST /runtime/broker/invoke
```

Input de invocacao:

```json
{
  "sessionId": "session-id",
  "objective": "objetivo da sessao",
  "provider": "auto",
  "intelligenceMode": "aios_cognitive_runtime_mesh"
}
```

Resposta inclui:

```json
{
  "accepted": true,
  "provider": "ollama_local_cloud",
  "model": "deepseek-v4-pro:cloud",
  "runtimeClass": "AIOSCognitiveRuntimeMesh",
  "qualityGate": {
    "status": "passed"
  },
  "userVisibleUsage": {
    "productUnit": "codex_sessions",
    "visibleMeter": "none",
    "balanceShown": false
  }
}
```

## Readiness

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\rc12-runtime-broker-readiness.ps1
```

Se Ollama nao estiver pronto, o relatorio mostra:

```txt
BLOCKED_OLLAMA_NOT_READY
```

Preparacao sugerida:

```powershell
ollama signin
ollama pull deepseek-v4-pro:cloud
ollama serve
.\scripts\rc12-runtime-broker-readiness.ps1
```

## MCP

Tools adicionadas:

```txt
aios.runtime_broker.status
aios.runtime_broker.invoke
```

## Seguranca

- Nao apaga tokens antigos.
- Nao modifica `auth.json`.
- Nao usa multi-account.
- Nao embute pesos, checkpoints ou binarios privados no pacote.
- Nao expõe segredo ao frontend.
- Nao cria contador de tokens na UI.
- Registra evento `codex.runtime.completed` no Workbench quando uma invocacao real completa.
