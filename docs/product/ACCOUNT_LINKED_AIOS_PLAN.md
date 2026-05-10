# Account-Linked AIOS Plan

## Objetivo

Definir uma proposta mais simples para apresentar: o usuario assina um plano Codex/AIOS, recebe o download do AIOS e usa a mesma conta para acessar Codex e AIOS.

Nome de trabalho:

```txt
Account-Linked AIOS Plan
```

ou:

```txt
AIOS Codex Account Link
```

## Tese

O AIOS nao precisa pedir uma OpenAI Platform API key ao usuario final. Ele pode ser vinculado a mesma identidade usada no Codex/ChatGPT, validar entitlement do plano e operar por runtime delegado.

Frase correta:

```txt
O usuario usa a mesma conta do Codex/ChatGPT para entrar no AIOS. O AIOS valida o entitlement do plano e usa runtime delegado aprovado, sem pedir API key ao usuario.
```

Frase a evitar:

```txt
O plano do usuario vira automaticamente uma chave de API compartilhada com o AIOS.
```

Motivo: assinatura ChatGPT/Codex e billing da OpenAI API sao superficies separadas. O caminho correto e vincular conta/plano/entitlement, nao extrair ou compartilhar API key.

## Fluxo de usuario

1. Usuario descobre Codex ou AIOS.
2. Usuario assina plano elegivel:
   - ChatGPT Plus/Pro/Business/Enterprise com acesso Codex;
   - plano AIOS;
   - bundle AIOS + Codex aprovado.
3. Sistema envia link de download do AIOS para o email da conta usada na assinatura.
4. Usuario instala AIOS.
5. Usuario entra no AIOS com a mesma conta usada no Codex/ChatGPT.
6. AIOS valida entitlement:
   - `codex_access`;
   - `aios_plan_access`;
   - `aios_codex_unlimited`, quando aplicavel.
7. AIOS habilita Workbench Premium, Agent Room, snapshots, handoff, audit/redaction e Runtime Broker.
8. Runtime escolhido:
   - `codex_delegated`, se Codex app-server/login estiver disponivel;
   - `aios_cloud_runtime`, se AIOS operar workspace cloud;
   - provider demo/fallback, se o runtime principal nao estiver pronto.

## O que o usuario ve

Permitido:

- `Conta vinculada`;
- `Plano AIOS ativo`;
- `Codex disponível`;
- `Sessao Codex ativa`;
- `Modo: Codex Delegated Runtime`;
- `Sem chave de API no app`;
- `Sem contador visivel de tokens`.

Nao mostrar:

- API key;
- access token;
- refresh token;
- saldo de tokens;
- quota semanal;
- billing interno;
- tenant interno;
- endpoint interno.

## Modelo tecnico

```txt
AIOS Desktop
  -> Login com conta OpenAI/ChatGPT/Enterprise ou AIOS Identity
  -> AIOS Entitlement Gateway
  -> Runtime Broker
      -> codex_delegated, quando usuario/workspace tem Codex
      -> aios_cloud_runtime, quando AIOS opera workspace
      -> no-key demo/fallback, quando aplicavel
```

## Componentes

### 1. AIOS Entitlement Gateway

Responsabilidade:

- validar se a conta tem acesso ao AIOS;
- validar se o plano permite Workbench Premium;
- validar se Codex delegado esta disponivel para aquela conta/workspace;
- emitir claims locais curtas para sessao AIOS.

Claims sugeridas:

```json
{
  "sub": "user-id",
  "emailVerified": true,
  "aiosPlan": "aios_unlimited",
  "codexAccess": true,
  "codexDelegatedAllowed": true,
  "workspaceId": "workspace-id",
  "sessionUnit": "codex_sessions"
}
```

### 2. AIOS Download Entitlement

Responsabilidade:

- liberar link de download apenas para conta elegivel;
- expirar links;
- registrar download;
- impedir redistribuicao de builds privados;
- oferecer update channel por plano.

Estados:

| Estado | Significado |
|---|---|
| `eligible` | Conta pode baixar AIOS. |
| `download_sent` | Link enviado ao email da conta. |
| `installed` | App registrou instalacao. |
| `linked` | App conectado a conta elegivel. |
| `revoked` | Acesso removido/cancelado. |

### 3. Codex Delegated Runtime

Responsabilidade:

- usar login gerenciado pelo Codex/ChatGPT/Enterprise;
- nao pedir OpenAI Platform API key;
- nao ler/copiar cache de autenticacao;
- listar modelos pelo Codex;
- encaminhar approvals/eventos para Workbench.

### 4. AIOS Cloud Runtime

Responsabilidade:

- operar workspace AIOS quando o objetivo for demo sem depender do runtime Codex;
- usar backend/secret store do AIOS;
- nunca expor chave ao usuario final.

## Regras de produto

- AIOS pode ser um beneficio/bundle de planos elegiveis.
- AIOS pode aumentar conversao para Plus/Pro/AIOS porque oferece experiencia de engenharia premium.
- AIOS nao deve dizer que Plus inclui API Platform.
- AIOS deve dizer que usa a mesma conta/plano para entitlement.
- AIOS deve continuar exibindo unidade `Sessoes Codex`.
- AIOS deve manter controles internos de estabilidade/abuso sem mostrar tokens.

## Go-to-market

### Caminho A - AIOS como beneficio de planos elegiveis

O usuario compra ou ja possui plano elegivel, recebe acesso ao AIOS, loga com a mesma conta e usa a experiencia premium.

Vantagem:

- menor friccao;
- aumenta valor percebido do plano;
- fortalece Codex.

Risco:

- precisa definicao clara de limites internos e suporte.

### Caminho B - AIOS como add-on pago

O usuario tem Codex/ChatGPT, compra AIOS como add-on e recebe download/entitlement.

Vantagem:

- monetizacao direta;
- controle de rollout.

Risco:

- billing e suporte separados precisam estar claros.

### Caminho C - AIOS trial para vender Plus/AIOS

Usuario baixa AIOS trial, usa demo controlada/no-key e e convidado a assinar plano elegivel.

Vantagem:

- funil de aquisicao;
- demonstra valor antes da compra.

Risco:

- demo precisa ser honesta e limitada por estabilidade, nao por claims irreais.

## Copy aprovada

```txt
Entre no AIOS com a mesma conta usada no Codex. Se seu plano for elegivel, o Workbench Premium e as Sessoes Codex ficam ativos automaticamente, sem colar API key no app.
```

```txt
AIOS usa entitlement da conta e runtime delegado aprovado. A API Platform continua separada quando usada diretamente por desenvolvedores.
```

```txt
Sem contador visivel de tokens: o AIOS mostra saude da sessao, agentes, diffs, snapshots e atividade.
```

## Criterios de aceite

- Login da conta valida entitlement sem expor token.
- Link de download e liberado somente para usuario elegivel.
- UI mostra plano ativo e modo de runtime.
- AIOS nao pede OpenAI Platform API key ao usuario final.
- `codex_delegated` nao altera `canInvokeLiveRuntime` do binding enterprise.
- Cancelamento/revogacao do plano remove acesso ao AIOS.
- Auditoria registra login, entitlement check, download, inicio de sessao e runtime mode.
