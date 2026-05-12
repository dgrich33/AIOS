# Como testar o AIOS RC34 Product Owner

## Abrir a versao visual

1. Execute:

```powershell
C:\AIOS\aios-codex-unlimited-enterprise-v2\AIOS_RC34_ABRIR_PRODUCT_OWNER.bat
```

2. Abra:

```text
http://127.0.0.1:5176
```

3. Login local:

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

## Onde fica o chat

O chat fica no topo da tela depois do login, no painel:

```text
AIOS Chat Principal
```

Use nesta ordem:

1. Campo `Runtime`: deixe `auto` para usar o provider recomendado ou escolha `Codex CLI Local Developer Live`.
2. Campo `Modelo`: escolha `gpt-5.5` para Codex CLI, ou `gpt-4o` / `gpt-5.2-codex` apenas quando a credencial OpenAI API oficial suportar esses modelos.
3. Campo `Agente`: escolha o perfil de agente.
4. Campo `Mensagem para o AIOS`: escreva sua pergunta.
5. Clique em `Enviar para runtime real`.

## Testar modelos no Owner Model Lab

O painel `Owner Model Lab` mostra o estado honesto de cada modelo:

- `gpt-5.5`: pode ser testado via Codex CLI se a conta ainda tiver uso disponivel.
- `gpt-5.2-codex`: requer OpenAI API autorizada ou runtime oficial que habilite o modelo.
- `gpt-4o`: requer OpenAI API autorizada ou runtime oficial que habilite o modelo.
- `gpt-oss:20b`: requer runtime self-hosted local, por exemplo Ollama/vLLM/TGI.
- `aios-native-fabric-v1`: camada AIOS-native para sessao, agentes, memoria e governanca.

Clique em:

```text
Testar Modelo Selecionado
```

Se a conta Codex estiver em limite de uso, o AIOS mostra a mensagem real do provider, sem fallback silencioso.

## Testar pelo VS Code

1. Execute:

```powershell
C:\AIOS\aios-codex-unlimited-enterprise-v2\AIOS_RC34_ABRIR_VSCODE_OWNER.bat
```

2. No VS Code, use:

```text
Terminal > Run Task > AIOS RC34 Owner: Start Workbench
```

3. Para testar chat real no terminal:

```text
Terminal > Run Task > AIOS RC34 Owner: Test Real Chat gpt-5.5
```

## Testar direto no terminal

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
powershell -ExecutionPolicy Bypass -File .\scripts\rc34-owner-terminal-chat-test.ps1 -NoStart -Provider auto -Model gpt-5.5 -Prompt "Responda exatamente: AIOS OWNER OK"
```

Por padrao, este comando nao faz fallback para AIOS Native. Se o provider real falhar, ele mostra a falha real.

Para testar a camada AIOS Native separadamente:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\rc34-owner-terminal-chat-test.ps1 -NoStart -Provider aios_native_runtime -Model aios-native-fabric-v1 -Prompt "Explique o estado do AIOS"
```

## Estado real desta maquina durante a ultima validacao

- Codex CLI encontrado: `codex-cli 0.130.0-alpha.5`
- Runtime local recomendado: `codex_cli_local_developer`
- `canInvokeLiveRuntime`: `true`
- `officialProduction`: `false`
- `gpt-5.5`: provider real disponivel, mas a conta atual retornou limite de uso do Codex.
- `gpt-5.2-codex` e `gpt-4o`: aguardam credencial OpenAI API/runtime oficial que habilite esses modelos.
- Segredos: nao lidos, nao impressos e nao versionados.

