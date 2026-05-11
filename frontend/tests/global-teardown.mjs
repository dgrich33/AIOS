import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const testsDir = dirname(fileURLToPath(import.meta.url));
const frontendRoot = join(testsDir, '..');
const testResultsDir = join(frontendRoot, 'test-results');
const statePath = join(testResultsDir, 'vite-server-state.json');
const teardownLogPath = join(testResultsDir, 'server-teardown.log');

function log(message) {
  fs.mkdirSync(testResultsDir, { recursive: true });
  fs.appendFileSync(teardownLogPath, `${new Date().toISOString()} ${message}\n`);
}

function taskkill(pid) {
  return new Promise((resolve) => {
    if (!pid) {
      resolve();
      return;
    }

    const taskkillExe = join(process.env.SystemRoot ?? 'C:\\Windows', 'System32', 'taskkill.exe');
    const killer = spawn(taskkillExe, ['/pid', String(pid), '/T', '/F'], {
      stdio: 'ignore',
      windowsHide: true,
    });

    killer.once('exit', (code) => {
      log(`taskkill pid=${pid} exit=${code}`);
      resolve(code === 0);
    });
    killer.once('error', (error) => {
      log(`taskkill pid=${pid} error=${error.message}`);
      resolve(false);
    });
  });
}

function stopProcessFallback(pid) {
  return new Promise((resolve) => {
    if (!pid) {
      resolve();
      return;
    }

    const stopper = spawn(
      'powershell.exe',
      ['-NoProfile', '-Command', `Stop-Process -Id ${Number(pid)} -Force -ErrorAction SilentlyContinue`],
      { stdio: 'ignore', windowsHide: true },
    );

    stopper.once('exit', (code) => {
      log(`Stop-Process pid=${pid} exit=${code}`);
      resolve();
    });
    stopper.once('error', (error) => {
      log(`Stop-Process pid=${pid} error=${error.message}`);
      resolve();
    });
  });
}

async function stopTree(pid) {
  const killed = await taskkill(pid);
  if (!killed) {
    await stopProcessFallback(pid);
  }
}

async function globalTeardown() {
  if (!fs.existsSync(statePath)) {
    return;
  }

  let state;
  try {
    state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch {
    state = null;
  }

  try {
    if (state?.frontend?.startedByPlaywright) {
      await stopTree(state.frontend.pid);
    }
    if (state?.backend?.startedByPlaywright) {
      await stopTree(state.backend.pid);
    }
  } finally {
    fs.rmSync(statePath, { force: true });
  }
}

export default globalTeardown;
