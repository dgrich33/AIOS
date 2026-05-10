# RC20 - Product Shell

## Objetivo

Transformar o Workbench em uma superficie clara do produto separado `AIOS Livre / Codex Unlimited`, mantendo a unidade de experiencia como `Sessoes Codex` e evitando qualquer contador de limite, saldo ou quota na UX principal.

## Implementado

- Faixa de produto no Workbench com o titulo `AIOS Livre / Codex Unlimited`.
- Contrato de produto visivel: `Conta vinculada`, `Sessoes Codex`, `API key nao armazenada` e ausencia de medidor de limite.
- Pilares visiveis: `AIOS Workbench Premium`, `Codex Delegated Runtime` e governanca por sessao.
- Link de referencia para docs de governanca do produto.
- Control Plane ajustado para mostrar uso por `codex_sessions`, sem rotulos de contador/quota.

## Limites de seguranca

- Nao adiciona credenciais, endpoints reais, service tokens ou leitura de `auth.json`.
- Nao marca runtime vivo como ativo.
- Nao altera documentos soberanos de contrato.
- Nao muda backend, entitlement real, billing ou politica de provisionamento.

## Validacoes executadas

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2\frontend
npm run build
npm run test:e2e
```

Resultados observados:

- Frontend build: OK.
- Playwright: 2 passed.
- Busca textual em `frontend/src`: sem `Contador`, `Quota semanal`, `Saldo de tokens`, `token balance`, `quota`, `creditos` ou `saldo`.

## Proxima etapa

RC21 deve mover a decisao de runtime para o Runtime Broker 2.0, com providers explicaveis e bloqueio explicito para qualquer runtime que tente aparecer como live sem binding oficial ativo.
