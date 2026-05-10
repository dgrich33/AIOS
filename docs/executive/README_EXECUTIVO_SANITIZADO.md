# README Executivo Sanitizado - AIOS Codex Unlimited RC16/RC17

## Destinatarios

Equipe autorizada de plataforma, seguranca, produtos enterprise, runtime e infraestrutura.

## Origem do Documento

Este documento e uma versao sanitizada para compartilhamento tecnico controlado. Ele remove nomes pessoais, assinaturas, canais internos, endpoints internos e qualquer identificador que possa ser confundido com credencial, segredo ou acesso ja provisionado.

O objetivo e preservar a clareza executiva sem expor informacao sensivel ou criar ambiguidade sobre o estado real do runtime.

## Objetivo

Entregar o pacote tecnico auditavel do AIOS Codex Unlimited nas versoes:

- RC16 - Runtime Binding Gate;
- RC17 - Secure Runtime Binding Store.

O pacote demonstra que o sistema esta pronto para receber dados reais de runtime por um caminho seguro, sem gravar segredos em codigo, GitHub, frontend, logs ou ZIP publico.

## Mensagem do Produto

```txt
Codex sem limites. Desenvolvimento sem interrupcoes.
```

Unidade do produto:

```txt
Sessoes Codex
```

O produto nao deve exibir contador de tokens, saldo, pacote de creditos ou quota semanal ao usuario final.

## Estado Real Atual

```json
{
  "scopeReady": true,
  "bindingState": "awaiting_secure_runtime_binding",
  "provider": "openai_codex",
  "canInvokeLiveRuntime": false,
  "secretsExposed": false
}
```

Interpretacao:

- o codigo, os testes, o Workbench, o MCP, o binding gate, o DPAPI store, os runbooks e os documentos tecnicos estao implementados;
- o runtime vivo ainda nao esta ativo nesta maquina;
- endpoint, service credential, tenant, sandbox environment id, Vault/KMS e live flag reais ainda precisam ser provisionados oficialmente;
- nenhum segredo real deve ser inserido no repositorio, no frontend, em logs ou em pacote publico.

## O Que E Real Neste RC

| Area | Estado |
|---|---|
| Backend FastAPI | Implementado |
| Frontend React/Vite | Implementado |
| Codex Workbench | Implementado |
| MCP Core e MCP Repo | Implementados |
| Sessions, snapshots e handoff | Implementados |
| Eventos MCP/build/files changed | Implementados |
| RBAC, service tokens e audit base | Implementados |
| Redaction e package scan | Implementados |
| Runtime Binding Gate | Implementado |
| Secure Runtime Binding Store | Implementado com DPAPI |
| Runtime live oficial | Pendente de dados reais |

## O Que Continua Pendente

Para ativar `bindingState: active` e `canInvokeLiveRuntime: true`, a equipe autorizada precisa fornecer:

- endpoint/base URL oficial ou Secure Runtime Bridge aprovado;
- service credential ou service token com escopos minimos;
- tenant/project/org autorizado;
- sandbox environment id autorizado;
- configuracao Vault/KMS ou secret store aprovado;
- live flag habilitada para sandbox/staging autorizado;
- modelo aprovado para invocacao;
- politica de billing, spend limits e rate limits;
- destino oficial de auditoria e telemetria.

## Ativacao Segura Quando os Dados Reais Forem Entregues

Usar apenas valores reais recebidos por canal autorizado:

```powershell
$token = Read-Host "Service token oficial" -AsSecureString
.\scripts\runtime-binding-save-local.ps1 `
  -Provider openai_codex `
  -RuntimeEndpoint "[endpoint oficial fornecido]" `
  -ServiceToken $token `
  -TenantId "[tenant aprovado]" `
  -SandboxEnvironmentId "[sandbox environment id aprovado]" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore

.\scripts\stop.ps1
.\scripts\start.ps1 -Mode Local
.\scripts\runtime-binding-status.ps1 -WriteReport
```

Resultado esperado apos provisionamento real:

```json
{
  "scopeReady": true,
  "bindingState": "active",
  "canInvokeLiveRuntime": true,
  "secretsExposed": false
}
```

## Plano B - Adapter Simulado Controlado

Enquanto o runtime vivo nao estiver provisionado, o projeto pode operar com um adapter simulado estritamente controlado para demonstrar fluxo de produto.

Regras obrigatorias do Plano B:

- rotular explicitamente como simulacao controlada;
- nao declarar que e runtime oficial ativo;
- nao mascarar controles reais de seguranca;
- registrar eventos e auditoria;
- nao expor segredos;
- nao mostrar tokens, saldo ou quota ao usuario;
- nao substituir a etapa de provisionamento oficial.

Frase recomendada:

```txt
Esta demonstracao usa o adapter local controlado. O runtime oficial sera ativado apenas quando os dados reais forem provisionados e validados pelo Runtime Binding Gate.
```

## Riscos Removidos Nesta Versao Sanitizada

| Risco | Tratamento |
|---|---|
| Nome pessoal ou assinatura em README compartilhavel | Removido |
| Endpoints internos ou canais internos aparentes | Substituidos por placeholders |
| Claim absoluto ambiguo | Substituido por separacao entre real, pendente e simulado |
| Confusao entre adapter simulado e runtime oficial | Plano B marcado como simulacao controlada |
| Hash de pacote fora de sincronia | Exigir hash do arquivo exato entregue |
| Repo publico com dados sensiveis | Documento nao inclui segredo, endpoint real ou identificador interno |

## Checklist Antes de Entregar

Executar:

```powershell
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
cd .\backend
..\.venv\Scripts\python.exe -m pytest .\tests -q
cd ..
git status -sb
git diff --cached --name-only
```

Antes de qualquer push publico, confirmar que nao ha:

- `.env` real;
- `license.cert`;
- service token;
- API key;
- auth.json;
- credentials.json;
- binding DPAPI;
- bancos locais;
- logs;
- ZIP final;
- checkpoints, pesos ou artefatos privados.

## Conclusao

O AIOS Codex Unlimited RC16/RC17 esta tecnicamente preparado para integracao oficial por runtime binding seguro.

O estado correto, ate o provisionamento real, e:

```txt
bindingState: awaiting_secure_runtime_binding
canInvokeLiveRuntime: false
secretsExposed: false
```

O estado desejado, apos provisionamento e validacao, e:

```txt
bindingState: active
canInvokeLiveRuntime: true
secretsExposed: false
```

Este documento e adequado para compartilhamento tecnico controlado porque evita dados internos, evita alegacoes ambiguas e deixa claro o limite entre implementacao real, pendencias de provisionamento e Plano B simulado controlado.
