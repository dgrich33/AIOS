import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';

type RpcRequest = { jsonrpc: '2.0'; id?: number | string; method: string; params?: any };
type ToolResult = { content: Array<{ type: 'text'; text: string }> };

const workspace = resolve(process.env.AIOS_WORKSPACE ?? process.cwd());
const snapshotDir = resolve(process.env.AIOS_SNAPSHOT_DIR ?? join(workspace, 'aios-snapshots'));
const aiosApiUrl = process.env.AIOS_API_URL ?? '';
const aiosServiceToken = process.env.AIOS_SERVICE_TOKEN ?? '';
const aiosSessionId = process.env.AIOS_SESSION_ID ?? '';
const useShell = process.platform === 'win32';
const blockedNames = ['.env', 'id_rsa', 'id_dsa', 'secrets.json'];

function safePath(input = '.'): string {
  const target = resolve(workspace, input);
  if (!target.startsWith(workspace)) throw new Error('Path escapes AIOS_WORKSPACE');
  const base = target.split(/[\\/]/).pop()?.toLowerCase() ?? '';
  if (blockedNames.includes(base) || base.endsWith('.pem') || base.endsWith('.key')) {
    throw new Error('Sensitive file blocked by policy');
  }
  return target;
}

function text(value: unknown): ToolResult {
  return { content: [{ type: 'text', text: typeof value === 'string' ? value : JSON.stringify(value, null, 2) }] };
}

function listFiles(dir = '.', limit = 500): string[] {
  const root = safePath(dir);
  const output: string[] = [];
  const ignored = new Set(['node_modules', '.git', 'dist', '__pycache__', '.pytest_cache']);
  function walk(current: string) {
    if (output.length >= limit) return;
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      if (ignored.has(entry.name)) continue;
      const full = join(current, entry.name);
      if (entry.isDirectory()) walk(full);
      else output.push(relative(workspace, full));
      if (output.length >= limit) break;
    }
  }
  walk(root);
  return output;
}

function search(query: string): string {
  const rg = spawnSync('rg', ['--line-number', '--hidden', '--glob', '!node_modules', '--glob', '!dist', query, workspace], {
    encoding: 'utf8',
  });
  if (rg.status === 0 || rg.stdout) return rg.stdout;
  const matches: string[] = [];
  for (const file of listFiles('.', 1000)) {
    const full = safePath(file);
    const body = readFileSync(full, 'utf8');
    body.split(/\r?\n/).forEach((line, index) => {
      if (line.toLowerCase().includes(query.toLowerCase())) matches.push(`${file}:${index + 1}:${line}`);
    });
  }
  return matches.join('\n');
}

function extractPatchFiles(patch: string): string[] {
  const files = new Set<string>();
  for (const line of patch.split(/\r?\n/)) {
    const match = /^(?:\+\+\+|---)\s+(?:a\/|b\/)?(.+)$/.exec(line);
    if (!match) continue;
    const file = match[1].trim();
    if (file && file !== '/dev/null') files.add(file);
  }
  return [...files].filter((file) => !file.startsWith('..'));
}

function shortText(value: string | undefined, limit = 1200): string {
  const text = value ?? '';
  if (text.length <= limit) return text;
  return `${text.slice(0, 400)}\n...[truncated]...\n${text.slice(-700)}`;
}

function compactArgs(args: any): Record<string, unknown> {
  const clone = { ...(args ?? {}) };
  if (typeof clone.content === 'string') clone.content = shortText(clone.content, 400);
  if (typeof clone.patch === 'string') clone.patch = shortText(clone.patch, 400);
  return clone;
}

async function postAios(path: string, body: unknown): Promise<void> {
  if (!aiosApiUrl || !aiosServiceToken || !aiosSessionId) return;
  try {
    await fetch(`${aiosApiUrl}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${aiosServiceToken}`,
      },
      body: JSON.stringify(body),
    });
  } catch {
    // MCP must keep working even when the local AIOS API is offline.
  }
}

async function recordEvent(type: string, title: string, message: string, payload: Record<string, unknown> = {}, source = 'aios-mcp-repo'): Promise<void> {
  await postAios(`/sessions/${aiosSessionId}/events`, { type, source, title, message, payload });
}

async function recordFilesChanged(filesChanged: string[], source = 'aios-mcp-repo'): Promise<void> {
  if (filesChanged.length === 0) return;
  await postAios(`/sessions/${aiosSessionId}/files-changed`, { filesChanged, source });
}

const tools = [
  { name: 'repo.list_files', description: 'List files under the AIOS workspace', inputSchema: { type: 'object', properties: { dir: { type: 'string' } } } },
  { name: 'repo.search', description: 'Search text in the AIOS workspace', inputSchema: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] } },
  { name: 'repo.read_file', description: 'Read a safe workspace file', inputSchema: { type: 'object', properties: { path: { type: 'string' } }, required: ['path'] } },
  { name: 'repo.read_range', description: 'Read a line range from a safe workspace file', inputSchema: { type: 'object', properties: { path: { type: 'string' }, start: { type: 'number' }, end: { type: 'number' } }, required: ['path', 'start', 'end'] } },
  { name: 'repo.apply_patch', description: 'Apply a unified diff patch inside the AIOS workspace', inputSchema: { type: 'object', properties: { patch: { type: 'string' } }, required: ['patch'] } },
  { name: 'repo.write_file', description: 'Write a safe workspace file', inputSchema: { type: 'object', properties: { path: { type: 'string' }, content: { type: 'string' } }, required: ['path', 'content'] } },
  { name: 'repo.run_command', description: 'Run an allow-listed command in the workspace', inputSchema: { type: 'object', properties: { command: { type: 'string' }, args: { type: 'array', items: { type: 'string' } } }, required: ['command'] } },
  { name: 'repo.typecheck', description: 'Run the repository typecheck/build guard for a known target', inputSchema: { type: 'object', properties: { target: { type: 'string' } } } },
  { name: 'repo.git_status', description: 'Return git status --short for the workspace', inputSchema: { type: 'object', properties: {} } },
  { name: 'repo.git_diff', description: 'Return git diff for the workspace or a safe relative path', inputSchema: { type: 'object', properties: { path: { type: 'string' } } } },
  { name: 'repo.build', description: 'Run a build command in the workspace', inputSchema: { type: 'object', properties: { target: { type: 'string' } } } },
  { name: 'aios.snapshot.create', description: 'Create a local file inventory snapshot', inputSchema: { type: 'object', properties: { name: { type: 'string' } } } },
  { name: 'aios.handoff.create', description: 'Create a local handoff artifact for a Codex session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, reason: { type: 'string' }, context: { type: 'string' }, nextSteps: { type: 'array', items: { type: 'string' } } }, required: ['reason'] } },
  { name: 'aios.policy.get', description: 'Read the shared AIOS policy file', inputSchema: { type: 'object', properties: {} } },
];

async function callTool(name: string, args: any): Promise<ToolResult> {
  await recordEvent('mcp.tool_call', name, `MCP tool called: ${name}`, { tool: name, arguments: compactArgs(args) });
  if (name === 'repo.list_files') return text(listFiles(args?.dir ?? '.'));
  if (name === 'repo.search') return text(search(args.query));
  if (name === 'repo.read_file') return text(readFileSync(safePath(args.path), 'utf8'));
  if (name === 'repo.read_range') {
    const lines = readFileSync(safePath(args.path), 'utf8').split(/\r?\n/);
    return text(lines.slice(Math.max(0, args.start - 1), args.end).join('\n'));
  }
  if (name === 'repo.apply_patch') {
    const patch = String(args.patch ?? '');
    const filesChanged = extractPatchFiles(patch);
    for (const file of filesChanged) safePath(file);
    const result = spawnSync('git', ['apply', '--whitespace=nowarn', '-'], { cwd: workspace, input: patch, encoding: 'utf8', shell: useShell });
    if (result.status === 0) {
      await recordEvent('repo.patch_applied', 'Patch applied', `${filesChanged.length} file(s) changed by repo.apply_patch`, { filesChanged, status: result.status });
      await recordFilesChanged(filesChanged);
    }
    return text({ status: result.status, filesChanged, stdout: result.stdout, stderr: result.stderr, error: result.error?.message });
  }
  if (name === 'repo.write_file') {
    const target = safePath(args.path);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, args.content, 'utf8');
    await recordEvent('repo.file_changed', 'File written', args.path, { filesChanged: [args.path] });
    await recordFilesChanged([args.path]);
    return text({ written: relative(workspace, target) });
  }
  if (name === 'repo.run_command') {
    const allowed = new Set(['npm', 'python', 'py', 'pytest', 'git', 'docker', 'node', 'powershell']);
    if (!allowed.has(args.command)) throw new Error('Command blocked by policy');
    const result = spawnSync(args.command, args.args ?? [], { cwd: workspace, encoding: 'utf8', shell: useShell });
    return text({ status: result.status, stdout: result.stdout, stderr: result.stderr, error: result.error?.message });
  }
  if (name === 'repo.typecheck') {
    const target = args?.target ?? 'frontend';
    const command: { bin: string; argv: string[]; cwd: string } =
      target === 'mcp-repo'
        ? { bin: 'npm', argv: ['run', 'build'], cwd: join(workspace, 'mcp', 'aios-mcp-repo') }
        : target === 'mcp-core'
          ? { bin: 'npm', argv: ['run', 'build'], cwd: join(workspace, 'mcp', 'aios-mcp-core') }
          : target === 'backend'
            ? { bin: 'python', argv: ['-m', 'pytest', 'backend/tests', '-q'], cwd: workspace }
            : { bin: 'npm', argv: ['run', 'build'], cwd: join(workspace, 'frontend') };
    const env = target === 'backend' ? { ...process.env, PYTHONPATH: 'backend' } : process.env;
    const result = spawnSync(command.bin, command.argv, { cwd: command.cwd, encoding: 'utf8', env, shell: useShell });
    return text({ target, status: result.status, stdout: result.stdout, stderr: result.stderr, error: result.error?.message });
  }
  if (name === 'repo.git_status') {
    const result = spawnSync('git', ['status', '--short'], { cwd: workspace, encoding: 'utf8', shell: useShell });
    return text({ status: result.status, stdout: result.stdout, stderr: result.stderr, error: result.error?.message });
  }
  if (name === 'repo.git_diff') {
    const argv = ['diff'];
    if (args?.path) argv.push('--', relative(workspace, safePath(args.path)));
    const result = spawnSync('git', argv, { cwd: workspace, encoding: 'utf8', shell: useShell });
    return text({ status: result.status, stdout: result.stdout, stderr: result.stderr, error: result.error?.message });
  }
  if (name === 'repo.build') {
    const target = args?.target ?? 'frontend';
    await recordEvent('repo.build_started', 'Build started', `Build started for ${target}`, { target });
    const command: { bin: string; argv: string[] } =
      target === 'backend-tests' ? { bin: 'python', argv: ['-m', 'pytest', 'backend/tests', '-q'] } : { bin: 'npm', argv: ['run', 'build'] };
    const env = target === 'backend-tests' ? { ...process.env, PYTHONPATH: 'backend' } : process.env;
    const result = spawnSync(command.bin, command.argv, { cwd: target === 'frontend' ? join(workspace, 'frontend') : workspace, encoding: 'utf8', env, shell: useShell });
    await recordEvent(result.status === 0 ? 'repo.build_passed' : 'repo.build_failed', result.status === 0 ? 'Build passed' : 'Build failed', `${target} build exited with ${result.status}`, { target, status: result.status, stdoutTail: shortText(result.stdout), stderrTail: shortText(result.stderr), error: result.error?.message });
    return text({ target, status: result.status, stdout: result.stdout, stderr: result.stderr, error: result.error?.message });
  }
  if (name === 'aios.snapshot.create') {
    mkdirSync(snapshotDir, { recursive: true });
    const namePart = (args?.name ?? 'snapshot').replace(/[^a-zA-Z0-9_-]/g, '-');
    const path = join(snapshotDir, `${Date.now()}-${namePart}.json`);
    writeFileSync(path, JSON.stringify({ workspace, files: listFiles('.', 2000), createdAt: new Date().toISOString() }, null, 2));
    return text({ path });
  }
  if (name === 'aios.handoff.create') {
    const handoffDir = join(snapshotDir, 'handoffs');
    mkdirSync(handoffDir, { recursive: true });
    const namePart = (args?.sessionId ?? 'session').replace(/[^a-zA-Z0-9_-]/g, '-');
    const path = join(handoffDir, `${Date.now()}-${namePart}.json`);
    writeFileSync(
      path,
      JSON.stringify(
        {
          workspace,
          sessionId: args?.sessionId ?? null,
          reason: args.reason,
          context: args?.context ?? '',
          nextSteps: args?.nextSteps ?? [],
          createdAt: new Date().toISOString(),
        },
        null,
        2,
      ),
    );
    return text({ path });
  }
  if (name === 'aios.policy.get') {
    const policy = join(workspace, 'shared', 'policies', 'aios-policy.json');
    return text(existsSync(policy) ? JSON.parse(readFileSync(policy, 'utf8')) : {});
  }
  throw new Error(`Unknown tool: ${name}`);
}

function send(message: unknown) {
  const body = JSON.stringify(message);
  process.stdout.write(`Content-Length: ${Buffer.byteLength(body, 'utf8')}\r\n\r\n${body}`);
}

async function handle(request: RpcRequest) {
  try {
    if (request.method === 'initialize') {
      send({ jsonrpc: '2.0', id: request.id, result: { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'aios-mcp-repo', version: '0.1.0' } } });
    } else if (request.method === 'tools/list') {
      send({ jsonrpc: '2.0', id: request.id, result: { tools } });
    } else if (request.method === 'tools/call') {
      const result = await callTool(request.params.name, request.params.arguments ?? {});
      send({ jsonrpc: '2.0', id: request.id, result });
    } else if (request.id !== undefined) {
      send({ jsonrpc: '2.0', id: request.id, result: {} });
    }
  } catch (error) {
    send({ jsonrpc: '2.0', id: request.id, error: { code: -32000, message: error instanceof Error ? error.message : String(error) } });
  }
}

let buffer = Buffer.alloc(0);
process.stdin.on('data', (chunk) => {
  buffer = Buffer.concat([buffer, chunk]);
  while (true) {
    const headerEnd = buffer.indexOf('\r\n\r\n');
    if (headerEnd === -1) return;
    const header = buffer.slice(0, headerEnd).toString('utf8');
    const match = /Content-Length: (\d+)/i.exec(header);
    if (!match) return;
    const length = Number(match[1]);
    const bodyStart = headerEnd + 4;
    if (buffer.length < bodyStart + length) return;
    const body = buffer.slice(bodyStart, bodyStart + length).toString('utf8');
    buffer = buffer.slice(bodyStart + length);
    handle(JSON.parse(body));
  }
});
