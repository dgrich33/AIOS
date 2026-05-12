# Como testar o chat com modelo real no AIOS

Este fluxo e para a versao local Product Owner RC34. Depois da correcao, o
padrao do chat nao e mais a resposta fixa do `aios_native_runtime`. O padrao e:

```text
provider: codex_cli_local_developer
modelo: gpt-5.5
```

Isso usa o `codex.exe` instalado e autenticado nesta maquina para conversar com
um modelo real. O AIOS nao le `auth.json`, nao copia token e nao mostra segredo.

## 1. Abrir o programa

De dois cliques:

```text
C:\AIOS\aios-codex-unlimited-enterprise-v2\AIOS_RC34_ABRIR_PRODUCT_OWNER.bat
```

O launcher abre:

```text
Frontend: http://127.0.0.1:5174
Backend:  http://127.0.0.1:8010/docs
```

## 2. Login

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

## 3. Onde fica o chat

Na tela principal, procure o painel:

```text
Sessao Codex
```

Ele tem:

- um campo grande para digitar sua pergunta;
- seletor `Runtime`;
- seletor `Modelo`;
- botao `Chat runtime real`;
- bloco `Resposta do AIOS`, onde aparece a resposta.

## 4. Configuracao correta para conversar com modelo real

Use:

```text
Runtime: Codex CLI local
Modelo: gpt-5.5
```

Digite uma pergunta no campo grande, por exemplo:

```text
Explique em uma frase o que e o AIOS Codex Unlimited.
```

Clique:

```text
Chat runtime real
```

A resposta aparece no bloco:

```text
Resposta do AIOS
```

## 5. O que esta acontecendo por baixo

Quando voce clica em `Chat runtime real`, o frontend chama o backend:

```text
POST /runtime/broker/invoke
```

O backend escolhe:

```text
codex_cli_local_developer
```

E executa:

```text
codex exec --json --model gpt-5.5 "<sua pergunta>"
```

Depois o AIOS pega a resposta do modelo real e mostra no bloco `Resposta do AIOS`.

## 6. Resultado esperado

No painel tecnico, o resultado deve indicar algo como:

```text
provider: codex_cli_local_developer
model: gpt-5.5
adapter: CodexCliLocalDeveloperAdapter
networkCallPerformed: true
officialProduction: false
secretsExposed: false
```

## 7. Sobre gpt-5.2-codex, gpt-4o e gpt-5.5

- `gpt-5.5`: validado nesta maquina via Codex CLI.
- `gpt-5.2-codex`: aparece no seletor, mas o Codex CLI desta conta retornou que
  esse modelo nao e suportado com ChatGPT sign-in nesta superficie.
- `gpt-4o`: para usar como modelo real, precisa estar disponivel via OpenAI API
  autorizada ou outro runtime oficial/provisionado.

Entao, para testar agora com modelo real sem colocar `OPENAI_API_KEY`, use:

```text
Runtime: Codex CLI local
Modelo: gpt-5.5
```

## 8. Para usar OpenAI API autorizada

Se voce tiver uma credencial oficial local com acesso ao modelo:

```text
AIOS_CHAT_PROVIDER=openai_api_authorized
AIOS_ALLOW_OPENAI_API_RUNTIME=true
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
OPENAI_API_KEY=cole-a-chave-local-aqui
```

Nesse modo, selecione:

```text
Runtime: OpenAI API autorizada
Modelo: gpt-4o / gpt-5.2-codex / gpt-5.5
```

## 9. Para usar AIOS Native

`AIOS Native Runtime` continua existindo, mas ele e a camada propria do AIOS para
sessao, Agent Room, memoria, snapshots e handoff. Ele nao deve ser usado quando
o objetivo for provar conversa com modelo proprietario real.

Use AIOS Native para demonstrar arquitetura AIOS. Use Codex CLI local para
conversar com modelo real agora.
