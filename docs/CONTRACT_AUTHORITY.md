# AIOS Codex Unlimited - Autoridade dos Documentos de Contrato

## Regra

Os documentos abaixo sao soberanos dentro do projeto e nao devem ser editados, reescritos, corrigidos, resumidos ou reinterpretados sem autorizacao explicita do usuario na conversa atual.

Arquivos protegidos:

- `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`
- `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`

## Comandos

Ver hashes atuais:

```powershell
.\scripts\contract-authority.ps1 show
```

Travar os documentos depois que o texto final estiver aprovado:

```powershell
.\scripts\contract-authority.ps1 lock -IUnderstandThisChangesContractHashes
```

Verificar se os documentos continuam intactos:

```powershell
.\scripts\contract-authority.ps1 verify
```

## Politica de Edicao

Se qualquer agente, script ou pessoa precisar alterar um dos documentos protegidos, deve primeiro obter autorizacao explicita do usuario e depois atualizar o lock com o comando `lock`.

Sem essa autorizacao, qualquer alteracao deve ser tratada como quebra de governanca do projeto.

