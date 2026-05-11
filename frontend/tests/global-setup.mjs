import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const testsDir = dirname(fileURLToPath(import.meta.url));
const frontendRoot = join(testsDir, '..');
const repoRoot = join(frontendRoot, '..');
const backendRoot = join(repoRoot, 'backend');
const stateDir = join(frontendRoot, 'test-results');
const statePath = join(stateDir, 'vite-server-state.json');
const frontendUrl = 'http://127.0.0.1:5173';
const backendUrl = 'http://127.0.0.1:8000/health';

async function isServerReady(url) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(1000) });
    return response.ok;
  } catch {
    return false;
  }
}

async function waitForServer(url, timeoutMs = 120000) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    if (await isServerReady(url)) {
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  throw new Error(`Server did not become ready at ${url}`);
}

function pythonExecutable() {
  const venvPython = process.platform === 'win32'
    ? join(repoRoot, '.venv', 'Scripts', 'python.exe')
    : join(repoRoot, '.venv', 'bin', 'python');

  if (fs.existsSync(venvPython)) {
    return venvPython;
  }

  return process.env.PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3');
}

function appendLog(name) {
  return fs.openSync(join(stateDir, name), 'a');
}

async function globalSetup() {
  fs.mkdirSync(stateDir, { recursive: true });
  const state = {
    backend: { startedByPlaywright: false },
    frontend: { startedByPlaywright: false },
  };

  if (!(await isServerReady(backendUrl))) {
    const backend = spawn(
      pythonExecutable(),
      ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
      {
        cwd: backendRoot,
        detached: true,
        env: process.env,
        stdio: ['ignore', appendLog('backend-stdout.log'), appendLog('backend-stderr.log')],
        windowsHide: true,
      },
    );

    backend.unref();
    state.backend = { startedByPlaywright: true, pid: backend.pid, url: backendUrl };
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
    await waitForServer(backendUrl);
  }

  if (!(await isServerReady(frontendUrl))) {
    const viteBin = join(frontendRoot, 'node_modules', 'vite', 'bin', 'vite.js');
    const vite = spawn(
      process.execPath,
      [viteBin, '--host', '127.0.0.1', '--port', '5173'],
      {
        cwd: frontendRoot,
        detached: true,
        env: {
          ...process.env,
          VITE_AIOS_API_URL: 'http://127.0.0.1:8000',
        },
        stdio: ['ignore', appendLog('vite-stdout.log'), appendLog('vite-stderr.log')],
        windowsHide: true,
      },
    );

    vite.unref();
    state.frontend = { startedByPlaywright: true, pid: vite.pid, url: frontendUrl };
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
    await waitForServer(frontendUrl);
  }

  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
}

export default globalSetup;
