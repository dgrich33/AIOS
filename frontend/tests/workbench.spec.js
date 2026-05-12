import { expect, test } from '@playwright/test';

test('shows the login screen', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'AIOS Codex Unlimited' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Entrar no Workbench/i })).toBeVisible();
});

test('clears stale auth token instead of leaving dead buttons', async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('aios.token', 'expired.invalid.local.token');
  });
  await page.goto('/');
  await expect(page.getByRole('button', { name: /Entrar no Workbench/i })).toBeVisible({ timeout: 15000 });
  await expect(page.getByText(/Sessao expirada ou invalida/i)).toBeVisible();
});

test('logs in and uses Codex Workbench session controls', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Senha').fill('AiosAdmin123!');
  await page.getByRole('button', { name: /Entrar no Workbench/i }).click();
  await expect(page.getByRole('heading', { name: 'Codex Workbench' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'AIOS Chat Principal' })).toBeVisible();
  await expect(page.getByRole('link', { name: /Ir para o Chat/i })).toBeVisible();
  await expect(page.getByLabel('Mensagem para o AIOS')).toBeVisible();
  await expect(page.getByRole('button', { name: /Enviar para runtime real/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'AIOS Livre / Codex Unlimited' })).toBeVisible();
  await expect(page.getByText('codex_sessions').first()).toBeVisible();
  await expect(page.getByText('Sessoes Codex').first()).toBeVisible();
  await expect(page.getByText('Conta vinculada').first()).toBeVisible();
  await expect(page.getByText('AIOS Workbench Premium').first()).toBeVisible();
  await expect(page.getByText('Codex Delegated Runtime').first()).toBeVisible();
  await expect(page.getByText('API key nao armazenada').first()).toBeVisible();
  await expect(page.getByRole('link', { name: /Docs de governanca/i })).toBeVisible();
  await expect(page.getByText('Contador')).toHaveCount(0);
  await expect(page.getByText('Quota semanal')).toHaveCount(0);
  await expect(page.getByText('Saldo de tokens')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Product Manifest' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Licenca Local RC13' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Scope Authority RC14' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Scope Preflight RC15' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Rodar Preflight de Escopo/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Runtime Binding RC16' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Verificar Binding Runtime/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Modelos Codex' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Runtime Gateway' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'AIOS Real Model Runtime RC34' })).toBeVisible();
  await expect(page.getByText('Provider explainability').first()).toBeVisible();
  await expect(page.getByText('official_codex_runtime').first()).toBeVisible({ timeout: 15000 });
  await expect(page.locator('.broker-provider-grid').getByText('aios_native_runtime')).toBeVisible();
  await expect(page.locator('.broker-provider-grid').getByText('codex_cli_local_developer')).toBeVisible();
  await expect(page.getByRole('option', { name: 'AIOS Native Runtime' }).first()).toBeAttached();
  await expect(page.getByRole('option', { name: 'aios-native-fabric-v1' }).first()).toBeAttached();
  await expect(page.getByRole('heading', { name: 'Owner Model Lab' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Testar Modelo Selecionado/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'AIOS Codex OS Sovereign' })).toBeVisible();
  await expect(page.getByText('codex.plan.core').first()).toBeVisible();
  await expect(page.getByRole('heading', { name: 'RC31 Private Community Runtime' })).toBeVisible();
  await expect(page.getByText('Segredos ficam na maquina do desenvolvedor').first()).toBeVisible();
  await expect(page.getByText('controlled_simulator').first()).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Codex Auth RC23' })).toBeVisible();
  await expect(page.getByText('auth.json nao lido').first()).toBeVisible();
  await expect(page.getByText('API key nao armazenada pelo AIOS').first()).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Approval Gate RC24' })).toBeVisible();
  await expect(page.getByText('Execucao automatica').first()).toBeVisible();
  await expect(page.getByText('bloqueada').first()).toBeVisible();
  await expect(page.getByRole('button', { name: /Criar Approval Demo/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'No Developer Cost' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Puter User-Pays/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Secure Runtime Bridge' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Context Engine' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Windows Release' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Final Readiness RC25' })).toBeVisible();
  await expect(page.getByText('local_demo_live_official_production_blocked').first()).toBeVisible();
  await expect(page.getByRole('button', { name: /Atualizar Readiness Final/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Official Integration' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Official Sandbox' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Restricted Access' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Comando de voz/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /Relatorio Executivo/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /Snapshot/i }).first()).toBeEnabled();
  await expect(page.getByRole('button', { name: /^Handoff$/i }).first()).toBeEnabled();
  await expect(page.getByText('Resposta do AIOS').first()).toBeVisible();

  await page.getByRole('button', { name: /Nova sessao/i }).first().click();
  await expect(page.getByText('Workbench Codex Session').first()).toBeVisible();

  await page.getByRole('button', { name: /Snapshot/i }).first().click();
  await expect(page.getByRole('heading', { name: 'Arquivos e build' })).toBeVisible();
  await expect(page.getByText('frontend/src/App.tsx').first()).toBeVisible();

  await page.getByRole('button', { name: /^Handoff$/i }).click();
  await expect(page.getByText('Continuar a implementacao').first()).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Eventos recentes' })).toBeVisible();
  await page.getByRole('button', { name: /Registrar evento MCP local/i }).click();
  await expect(page.getByText('mcp.tool_call').first()).toBeVisible();

  const objectiveBox = page.getByLabel('Mensagem para o AIOS');
  await objectiveBox.fill('Responda exatamente: AIOS modelo real via Workbench');
  await page.getByRole('button', { name: /Enviar para runtime real/i }).click();
  await expect(page.getByText('AIOS modelo real via Workbench').first()).toBeVisible({ timeout: 90000 });
});
