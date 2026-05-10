import { expect, test } from '@playwright/test';

test('shows the login screen', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'AIOS Codex Unlimited' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Entrar no Workbench/i })).toBeVisible();
});

test('logs in and uses Codex Workbench session controls', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Senha').fill('AiosAdmin123!');
  await page.getByRole('button', { name: /Entrar no Workbench/i }).click();
  await expect(page.getByRole('heading', { name: 'Codex Workbench' })).toBeVisible();
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
  await expect(page.getByRole('heading', { name: 'Runtime Broker RC12' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'No Developer Cost' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Puter User-Pays/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Secure Runtime Bridge' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Context Engine' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Windows Release' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Official Integration' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Official Sandbox' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Restricted Access' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Comando de voz/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /Relatorio Executivo/i })).toBeVisible();

  await page.getByRole('button', { name: /Nova sessao/i }).click();
  await expect(page.getByText('Workbench Codex Session').first()).toBeVisible();

  await page.getByRole('button', { name: /Snapshot/i }).click();
  await expect(page.getByRole('heading', { name: 'Arquivos e build' })).toBeVisible();
  await expect(page.getByText('frontend/src/App.tsx').first()).toBeVisible();

  await page.getByRole('button', { name: /^Handoff$/i }).click();
  await expect(page.getByText('Continuar a implementacao').first()).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Eventos recentes' })).toBeVisible();
  await page.getByRole('button', { name: /Registrar evento MCP local/i }).click();
  await expect(page.getByText('mcp.tool_call').first()).toBeVisible();
});
