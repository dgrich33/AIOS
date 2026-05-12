# Como testar o AIOS RC28

## O que existe agora

Isto ainda nao e um instalador `.exe`.

O que existe e uma demo local funcional do AIOS, com:

- Backend local em FastAPI.
- Workbench local no navegador.
- Painel `AIOS Chat` para conversar com o runtime.
- Seletor de agentes `Agent Room` dentro do chat.
- Painel `RC27 AIOS Native Runtime Fabric`.
- Pesquisa externa segura: referencias adotadas, em estudo e rejeitadas por seguranca.
- `canInvokeLiveRuntime=true` via `aios_native_runtime`.
- `gpt-5.2-codex` e `gpt-4o` ativos no registry.

## Jeito mais simples

1. Abra esta pasta:

```text
C:\Users\dg71\Documents\Codex\2026-05-08\aios-codex-unlimited-recapitula-o-completa\artifacts\aios-codex-unlimited-enterprise-v2
```

2. De dois cliques em:

```text
AIOS_RC28_ABRIR_DEMO.bat
```

Se preferir, `AIOS_RC27_ABRIR_DEMO.bat` tambem abre a mesma demo.

3. O navegador deve abrir sozinho em:

```text
http://127.0.0.1:5173
```

4. Entre com:

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

5. Na tela, procure:

```text
AIOS Chat
RC27 AIOS Native Runtime Fabric
```

O painel `AIOS Chat` e o lugar principal para testar conversa. O painel `RC27 AIOS Native Runtime Fabric` mostra o estado do runtime.

## Como testar o chat

1. No painel `AIOS Chat`, escolha o modelo:

```text
gpt-4o
```

ou:

```text
gpt-5.2-codex
```

2. Escolha um agente:

```text
Security Agent
Architect Agent
Builder Agent
Research Agent
Docs Agent
```

3. Digite uma pergunta, por exemplo:

```text
O que posso testar no AIOS agora?
```

4. Clique em:

```text
Enviar
```

5. A resposta deve aparecer no historico do chat e mencionar o agente escolhido.

## O que mostrar na apresentacao

1. `AIOS Native Runtime Fabric`
2. `canInvokeLiveRuntime=true`
3. `activeRuntimeProvider=aios_native_runtime`
4. `gpt-5.2-codex` ativo no registry
5. `gpt-4o` ativo no registry
6. Escolher agentes no `Agent Room`
7. Mostrar a linha `Ideias adotadas / Estudo futuro / Rejeitadas por seguranca`
8. Conversar no `AIOS Chat`
9. Criar uma nova sessao
10. Criar snapshot
11. Rodar `Codex run`
12. Mostrar docs em:

```text
http://127.0.0.1:8000/docs
```

## Como parar

De dois cliques em:

```text
AIOS_RC28_PARAR_DEMO.bat
```

## Se nao abrir

Rode a validacao:

```powershell
.\scripts\rc27-native-runtime-fabric-check.ps1
```

Se passar, o projeto esta funcional e o problema e de inicializacao local, porta ocupada ou falta de permissao do Windows.
