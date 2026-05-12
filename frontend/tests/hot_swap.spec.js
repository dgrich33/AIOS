import { expect, test } from '@playwright/test';

async function login(apiBaseUrl) {
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'admin@aios.local', password: 'AiosAdmin123!' }),
  });
  expect(response.ok).toBeTruthy();
  const payload = await response.json();
  return payload.accessToken;
}

test('hot swap state exposes Codex Plan Core and beta fallback contract', async () => {
  const apiBaseUrl = `http://127.0.0.1:${process.env.AIOS_PLAYWRIGHT_BACKEND_PORT ?? '8000'}`;
  const token = await login(apiBaseUrl);
  const response = await fetch(`${apiBaseUrl}/runtime/sovereign/status`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(response.ok).toBeTruthy();
  const payload = await response.json();
  const organIds = payload.organs.map((organ) => organ.organId);
  expect(organIds).toContain('codex.plan.core');
  expect(organIds).toContain('aios_code.beta.organ');
  expect(payload.router.routingRules.some((rule) => String(rule.when ?? '').includes('organ_available(codex_plan_core)'))).toBeTruthy();
  expect(payload.router.routingRules.some((rule) => rule.use === 'aios_code.beta.organ' || rule.use === 'code_core')).toBeTruthy();
  expect(payload.secretsExposed).toBe(false);
});

