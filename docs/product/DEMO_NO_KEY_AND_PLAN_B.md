# AIOS Livre / Codex Unlimited - Demo Sem Chave e Plano B

## Objetivo

Permitir demonstracoes fortes enquanto o runtime oficial ainda nao esta provisionado, sem exigir que o usuario final ou o desenvolvedor use uma chave OpenAI pessoal no app.

## Regra central

```txt
Demo sem chave nao e runtime oficial.
Provider alternativo nao e modelo oficial Codex.
Adapter simulado nao pode mascarar controles reais.
```

## Modos permitidos

### 1. Official Runtime Mode

Uso:

- alpha/staging/producao condicionada;
- somente quando os dados reais forem provisionados.

Requisitos:

- endpoint/base URL;
- service credential;
- tenant/project/org;
- sandbox environment id;
- Vault/KMS ou Secure Runtime Bridge;
- live flag;
- modelo aprovado;
- binding ativo.

Status esperado:

```txt
bindingState: active
canInvokeLiveRuntime: true
secretsExposed: false
```

### 2. OpenAI API Authorized Mode

Uso:

- testes com conta/organizacao autorizada;
- nao depende de chave pessoal do desenvolvedor se a organizacao fornecer service account/API key.

Regras:

- segredo no backend/cofre, nunca no frontend;
- billing/spend limits definidos;
- nao chamar de Official Codex Runtime se for API publica.

### 3. Puter User-Pays Demo

Uso:

- demo no browser;
- custo delegado ao usuario/provedor;
- sem chave OpenAI no backend AIOS.

Regras:

- rotular como `No-Key Demo - User-Pays Provider`;
- registrar eventos no Workbench;
- nao guardar segredo do provider;
- nao usar para claims de runtime oficial.

### 4. GitHub Models Demo

Uso:

- demo com credencial GitHub autorizada;
- comparacao de providers e prototipos.

Regras:

- rotular como `Demo Provider`;
- usar apenas modelos disponiveis e autorizados;
- nao declarar "Codex oficial" se o provider nao for OpenAI/Codex oficial.

### 5. Ollama Local/Cloud Fallback

Uso:

- desenvolvimento local;
- fallback offline/parcial;
- testes de UX, Agent Room, Repo Memory e Workbench.

Regras:

- rotular como `Fallback Local/Cloud`;
- nao mapear modelo local como `gpt-5.5` ou `codex-*` oficial;
- nao embutir modelos privados no pacote.

### 6. Controlled Simulator

Uso:

- demonstrar fluxo inteiro quando nenhum provider real esta disponivel;
- testar UI, auditoria, redaction, approval gate e eventos.

Regras obrigatorias:

- UI deve mostrar `Simulacao controlada`;
- resposta deve incluir metadata de modo simulado;
- logs devem registrar `provider=controlled_simulator`;
- nao retornar `canInvokeLiveRuntime: true`;
- nao substituir `runtime-binding-status.ps1`;
- nao prometer qualidade de modelo oficial.

Frase de UI recomendada:

```txt
Demo controlada: esta sessao demonstra o fluxo AIOS. O runtime oficial sera ativado apenas quando o binding seguro estiver ativo.
```

## Como o usuario deve perceber

O usuario final nao precisa ver tokens, saldo ou quota. Ele deve ver:

- modo da sessao;
- saude do runtime;
- agente ativo;
- atividade recente;
- aprovacoes pendentes;
- snapshots;
- build/test status;
- risco atual.

## Matriz de honestidade

| Cenario | Pode mostrar "sem chave do usuario"? | Pode mostrar "runtime oficial"? | Pode esconder tokens? |
|---|---:|---:|---:|
| Official Runtime Mode | Sim | Sim | Sim |
| OpenAI API Authorized Mode | Sim, se a chave for da organizacao/backend | Nao como runtime interno | Sim |
| Puter User-Pays Demo | Sim | Nao | Sim |
| GitHub Models Demo | Sim, se credencial delegada | Nao | Sim |
| Ollama Local/Cloud | Sim | Nao | Sim |
| Controlled Simulator | Sim | Nao | Sim |

## Aceite do Plano B

Plano B esta correto quando:

- permite demonstrar produto completo;
- nao expõe segredo;
- nao falsifica runtime oficial;
- nao muda `bindingState`;
- gera eventos/auditoria;
- respeita redaction;
- e removivel ou substituivel quando provider oficial chegar.
