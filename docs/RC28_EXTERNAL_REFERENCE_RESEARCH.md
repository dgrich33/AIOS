# RC28 - External Reference Research e Agent Room

## Objetivo

Transformar a lista de repositorios externos em requisitos seguros para o AIOS, sem copiar codigo, sem importar marcas/provedores indevidos e sem usar projetos de bypass de API.

## O que entrou no produto

- `AIOS Chat` agora permite escolher modelo e agente.
- `Agent Room` ganhou catalogo oficial do AIOS com agentes: Assistant, Architect, Builder, Debugger, Security, Researcher e Docs.
- `Runtime Fabric` ganhou catalogo completo de pesquisa externa em `shared/research/aios_external_project_registry.json`.
- `GET /runtime/fabric/source-research` representa todos os 112 links enviados.
- A UI mostra links recebidos, ideias adotadas, estudo futuro, adapters/SDKs e licoes de seguranca.

## Cobertura da lista enviada

O AIOS registra todos os links recebidos:

- `receivedLinkCount`: 112
- `representedProjectCount`: 112
- duplicatas preservadas como entradas proprias quando foram enviadas mais de uma vez
- nenhum link fica fora do catalogo

## Ideias adotadas com seguranca

- GPT4All / Jan: UX desktop e provider local/self-hosted.
- privateGPT / Khoj / DocsGPT: RAG privado e pesquisa em documentos sem vazamento.
- LibreChat / LobeHub: experiencia multi-provider, presets e organizacao de chat.
- OpenHands / E2B: workspace isolado, replay e execucao sob controle.
- AutoGPT / MetaGPT / gpt-engineer: fluxos de agentes, planejamento e issue-to-patch.
- Crawlee / gpt-crawler: ingestao de documentacao aprovada, sempre com allowlist.

## Ideias em estudo

- mini-omni2 e Azure realtime audio SDK: audio e realtime.
- unsloth: adaptacao/fine-tuning eficiente.
- nanoGPT/minGPT: material educacional, nao dependencia de produto.
- LLaVA/InternVL: classe de capacidade vision-language.
- Skyvern: automacao de navegador sob Approval Gate.

## Licoes de seguranca

Projetos de free API, keyless API, wrappers nao oficiais ou bypass de acesso tambem sao usados, mas como referencia para testes de risco, validacao de provider, proveniencia e controles de seguranca. Eles nao sao ignorados.

Exemplos usados como licao de seguranca:

- `xtekky/gpt4free`
- `chatanywhere/GPT_API_free`
- `callbacked/keyless-gpt-wrapper-api`
- `SreejanPersonal/Free-Unoffical-OpenAI-API`
- `acheong08/ChatGPT`
- `UStoPY/chat-gpt-4-free`

## Endpoints

```text
GET /runtime/fabric/agent-room/catalog
GET /runtime/fabric/source-research
POST /runtime/fabric/chat
```

`POST /runtime/fabric/chat` aceita:

```json
{
  "modelId": "gpt-4o",
  "agentId": "security",
  "messages": [
    { "role": "user", "content": "Revise riscos do AIOS." }
  ]
}
```

## Status honesto

RC28 nao afirma que repos externos foram copiados para dentro do AIOS. O que existe e:

- catalogo completo dos 112 links;
- analise de ideias;
- requisitos seguros derivados dessas ideias;
- catalogo de risco e licoes de seguranca;
- UI testavel no Workbench;
- runtime nativo do AIOS para demonstracao local.
