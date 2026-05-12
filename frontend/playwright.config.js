import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  globalSetup: './tests/global-setup.mjs',
  globalTeardown: './tests/global-teardown.mjs',
  timeout: 120000,
  use: {
    baseURL: `http://127.0.0.1:${process.env.AIOS_PLAYWRIGHT_FRONTEND_PORT ?? '5173'}`,
    trace: 'on-first-retry',
  },
});
