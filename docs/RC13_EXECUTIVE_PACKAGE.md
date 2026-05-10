# AIOS Codex Unlimited RC13 - Pacote Executivo

## Objetivo

A RC13 transforma a base RC12 em um pacote demonstravel para avaliacao executiva: instalacao assistida, licenca local de validacao, UI com controles premium, comando de voz local e relatorio executivo de sessao.

## Entregas

- `GET /license/status`
- `backend/app/license_manager.py`
- `scripts/generate_license.py`
- `scripts/install_everything.ps1`
- `scripts/start_demo.ps1`
- `scripts/rc13-package.ps1`
- painel `Licenca Local RC13` no Workbench
- botoes `Comando de voz` e `Relatorio Executivo`
- documento `docs/REQUEST_EXTENSION_AIOS_CODEX_UNLIMITED_LICENSE_v1.md`

## Licenca local

`license.cert` e a prova local de autorizacao do AIOS Codex Unlimited RC13. Ela ativa o entitlement local `aios_codex_unlimited`, a classe `premium_unlimited` e o escopo de permissao para runtime enterprise dentro do AIOS.

Ela opera junto com:

- service tokens persistentes;
- Vault/KMS;
- Secure Runtime Bridge;
- auditoria de sessao, tool calling e streaming.

O service token, Vault/KMS ou Secure Runtime Bridge e o mecanismo tecnico usado para apresentar essa autorizacao ao runtime externo com autenticacao, rotacao e auditoria.

## Voz

O botao de voz usa Web Speech API no navegador quando disponivel. O texto reconhecido entra no objetivo da sessao. Nao ha servico externo novo no backend para voz.

## Relatorio executivo

O Workbench gera um relatorio local com:

- produto;
- sessao;
- objetivo;
- runtime/modelo selecionado;
- status da licenca local;
- eventos recentes do Workbench;
- nota de redaction.

O relatorio abre no navegador para impressao/salvar como PDF. Nenhuma API key ou segredo e incluido.

## Instalacao assistida

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\install_everything.ps1
```

Instalacao de ferramentas via winget e opcional:

```powershell
.\scripts\install_everything.ps1 -InstallTools
```

Preparacao opcional do modelo Ollama:

```powershell
.\scripts\install_everything.ps1 -PullOllamaModel
```

## Demo

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\start_demo.ps1
```

URLs:

```txt
Frontend: http://127.0.0.1:5173
Backend docs: http://127.0.0.1:8000/docs
```
