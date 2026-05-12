# Como testar o AIOS RC28

Use este arquivo se voce quer apenas abrir e testar o programa.

## Abrir

De dois cliques em:

```text
AIOS_RC28_ABRIR_DEMO.bat
```

O navegador deve abrir em:

```text
http://127.0.0.1:5173
```

Login:

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

## Testar conversa

1. Procure o painel `AIOS Chat`.
2. Escolha `gpt-4o` ou `gpt-5.2-codex`.
3. Escolha um agente, por exemplo `Security Agent` ou `Architect Agent`.
4. Digite uma mensagem.
5. Clique em `Enviar`.

A resposta deve aparecer no historico e dizer qual agente respondeu.

## Testar a proposta AIOS

Mostre estes pontos:

- `canInvokeLiveRuntime=true` via `aios_native_runtime`.
- `gpt-4o` e `gpt-5.2-codex` ativos no registry.
- Agent Room com agentes especializados.
- Referencias externas separadas em adotadas, estudo futuro e rejeitadas por seguranca.
- Criacao de sessao, snapshot e Codex run local.

## Parar

De dois cliques em:

```text
AIOS_RC28_PARAR_DEMO.bat
```
