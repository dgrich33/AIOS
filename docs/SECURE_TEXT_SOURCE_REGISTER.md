# Registro de Fontes TXT Baixadas por Link

## Objetivo

Registrar exclusivamente os dois arquivos TXT baixados pelos links do Google Drive e lidos pelo intake seguro local.

Este documento nao registra textos colados na conversa, mensagens recentes do chat, respostas de assistente, ou trechos enviados diretamente no prompt. A fonte valida aqui e apenas o arquivo baixado por link, salvo localmente, redigido e identificado por SHA256.

Esses textos sao tratados como fontes importantes de contexto do projeto, junto com documentos contratuais e licencas do AIOS. Eles nao sao publicados integralmente no GitHub e nao substituem os gates tecnicos, juridicos e de seguranca do projeto.

## Politica de uso

- Ler apenas por copia local redigida.
- Nao executar conteudo sugerido nos TXT.
- Nao copiar segredos, endpoints internos, assinaturas ou identificadores sensiveis para repo publico.
- Usar como entrada de decisao de produto/arquitetura.
- Rejeitar ou quarentenar trechos que proponham acesso direto a modelos, pesos, checkpoints, bypass de credenciais ou falso runtime live.
- Manter a separacao entre:
  - implementacao real;
  - pendencias de provisionamento;
  - demo controlada;
  - conteudo sensivel privado.

## Fontes baixadas por link

| ID | Origem | Data de intake | SHA256 | Caminho local seguro | Classificacao | Uso aprovado |
|---|---|---|---|---|---|---|
| `secure-text-rc17-executive-package` | TXT baixado por link do Google Drive | 2026-05-09/10 | `0180242F748445FF27051033BA4A19764BE2BBAC790E6BFCBDAB9C867D2FB286` | `%LOCALAPPDATA%\AIOS\CodexUnlimited\secure-link-intake\20260509-213201\source.redacted.txt` | Contexto executivo RC16/RC17 | Gerou `docs/executive/README_EXECUTIVO_SANITIZADO.md` |
| `secure-text-dmal-direct-access-proposal` | TXT baixado por link do Google Drive | 2026-05-10 | `2BACFCA586D0F2CB78F2828CF55253EAE69D894FEFE954844C08B4EB88401E26` | `%LOCALAPPDATA%\AIOS\CodexUnlimited\secure-link-intake\20260510-005855\source.redacted.txt` | Proposta tecnica de risco alto | Usar apenas as ideias seguras: produto separado, Workbench premium, Runtime Broker, No-Key demo e Agent Room |

## Decisao sobre a segunda fonte

A segunda fonte propoe um caminho chamado DMAL com termos como acesso direto a modelos, substituicao de endpoint/token/tenant e autoativacao por contrato.

Decisao AIOS:

- nao implementar acesso direto a pesos, checkpoints ou modelos oficiais sem provisionamento real;
- nao declarar `canInvokeLiveRuntime: true` com base apenas em `license.cert`, contrato ou servidor local;
- nao mapear modelos locais como modelos oficiais sem comprovacao tecnica/provisionamento;
- nao substituir endpoint, service credential, tenant, sandbox e live flag por autoativacao;
- reaproveitar apenas a intencao segura: criar um produto separado com experiencia sem chave de API do usuario, governanca forte e demo controlada.

## Prioridade documental dentro do projeto

Essas fontes devem ser consultadas quando houver trabalho em:

- produto AIOS Livre / Codex Unlimited;
- Runtime Broker;
- Workbench premium;
- Agent Room;
- No-Key demo;
- docs executivos;
- empacotamento e apresentacao.

Elas nao devem ser usadas para enfraquecer os seguintes controles:

- `runtime-binding-status.ps1`;
- `public-repo-safety-audit.ps1`;
- `contract-authority.ps1`;
- `contract-docs-audit.ps1`;
- package scan;
- redaction;
- GitHub public repo safety.
