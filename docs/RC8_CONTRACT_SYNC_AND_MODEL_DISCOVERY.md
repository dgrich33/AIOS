# AIOS Codex Unlimited RC8 - Contract sync e descoberta de modelos

## Objetivo

A RC8 sincroniza os documentos soberanos do projeto com o PDF atualizado:

```txt
C:\Users\dg71\Downloads\AIOS_Codex_Unlimited_Contrato_DOCX_FIEL_LITERAL.docx.pdf
```

Tambem adiciona um diagnostico seguro para descobrir se a credencial OpenAI configurada tem acesso a modelos candidatos como `gpt-5.5` e modelos Codex.

## Documentos soberanos atualizados

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md
```

Depois da atualizacao, o lock foi recriado em:

```txt
docs/CONTRACT_AUTHORITY.lock.json
```

## Diagnostico GPT 5.5 / Codex

Rodar:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\rc8-openai-model-diagnose.ps1
```

O script:

- nao imprime a API key;
- chama apenas `GET /models`;
- verifica candidatos como `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.2-codex`, `gpt-5.1-codex` e variantes;
- grava o relatorio em `release/RC8_OPENAI_MODEL_DIAGNOSTIC.md`;
- recomenda o primeiro model ID disponivel para configurar em `OPENAI_MODEL`.

## Observacao

Se `gpt-5.5` nao aparecer na lista da credencial, o problema nao e o AIOS: e acesso/model availability da conta, projeto, organizacao ou provedor. Nesse caso, usar o modelo Codex disponivel mais proximo ate que a permissao do modelo seja liberada.

