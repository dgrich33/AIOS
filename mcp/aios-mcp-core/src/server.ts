type RpcRequest = { jsonrpc: '2.0'; id?: number | string; method: string; params?: any };

const apiUrl = process.env.AIOS_API_URL ?? 'http://localhost:8000';
const adminEmail = process.env.AIOS_ADMIN_EMAIL ?? 'admin@aios.local';
const adminPassword = process.env.AIOS_ADMIN_PASSWORD ?? 'AiosAdmin123!';
let cachedToken = process.env.AIOS_SERVICE_TOKEN ?? '';

function text(value: unknown) {
  return { content: [{ type: 'text', text: typeof value === 'string' ? value : JSON.stringify(value, null, 2) }] };
}

async function token() {
  if (cachedToken) return cachedToken;
  const response = await fetch(`${apiUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: adminEmail, password: adminPassword }),
  });
  if (!response.ok) throw new Error(`Login failed: ${response.status}`);
  const payload = await response.json();
  cachedToken = payload.accessToken;
  return cachedToken;
}

async function api(path: string, init: RequestInit = {}) {
  const bearer = await token();
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${bearer}`,
      ...(init.headers ?? {}),
    },
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(payload));
  return payload;
}

const tools = [
  { name: 'aios.entitlement.get', description: 'Get current AIOS Codex Unlimited entitlement', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.control_plane.status', description: 'Get control-plane status', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.heritage.summary', description: 'Get original AIOS lineage and migration summary', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.scope.authority', description: 'Read RC14 scope authority: license.cert, locked contract docs, signature evidence and precedence', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.scope.preflight', description: 'Run RC15 scope preflight for a scoped AIOS Codex operation', inputSchema: { type: 'object', properties: { operation: { type: 'string' }, environment: { type: 'string' }, modelId: { type: 'string' }, requiresLiveRuntime: { type: 'boolean' }, requiresRestrictedArtifacts: { type: 'boolean' }, reason: { type: 'string' } } } },
  { name: 'aios.runtime_binding.status', description: 'Read RC16 runtime binding gate without exposing secrets', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.product.manifest', description: 'Get AIOS Codex Unlimited product manifest', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.codex.models', description: 'List Codex models available in the Unlimited registry', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.codex.plan_unlimited', description: 'Get the AIOS Codex Unlimited plan definition', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.subscription.me', description: 'Get current subscription/license status', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.codex.runtime_status', description: 'Get Codex Runtime Gateway status', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.codex.runtime_model_discovery', description: 'Discover available OpenAI/Codex runtime models without exposing credentials', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.codex.runtime_invoke', description: 'Invoke Codex Runtime Gateway for a session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, modelId: { type: 'string' }, objective: { type: 'string' } }, required: ['sessionId'] } },
  { name: 'aios.runtime_broker.status', description: 'Get RC12 Runtime Broker status across official, Ollama and user-pays providers', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.runtime_broker.invoke', description: 'Invoke the RC12 AIOS Cognitive Runtime Mesh through the best available provider', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, objective: { type: 'string' }, provider: { type: 'string' } }, required: ['sessionId', 'objective'] } },
  { name: 'aios.policy.language_evaluate', description: 'Evaluate official/product language policy', inputSchema: { type: 'object', properties: { text: { type: 'string' } }, required: ['text'] } },
  { name: 'aios.integration.guardrails', description: 'Get AIOS integration guardrails for Codex runtime and artifacts', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.identity.profiles', description: 'List AIOS identity profiles', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.secure_runtime.bridge', description: 'Get Secure Runtime Bridge configuration', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.secure_runtime.request', description: 'Request an allowlisted secure runtime operation', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, operation: { type: 'string' }, objective: { type: 'string' }, payload: { type: 'object' } }, required: ['sessionId', 'operation'] } },
  { name: 'aios.context.index', description: 'Create local context index metadata', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, name: { type: 'string' }, source: { type: 'string' }, fileCount: { type: 'number' }, graphNodes: { type: 'number' }, graphEdges: { type: 'number' } } } },
  { name: 'aios.context.query', description: 'Query local-first context capsule metadata', inputSchema: { type: 'object', properties: { query: { type: 'string' }, sessionId: { type: 'string' }, maxResults: { type: 'number' } }, required: ['query'] } },
  { name: 'aios.skill_store.list', description: 'List AIOS Codex Unlimited skills', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.release.windows_manifest', description: 'Get Windows release manifest', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_integration.readiness', description: 'Get RC4 official integration readiness', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_integration.adapter_contract', description: 'Get OfficialCodexRuntimeAdapter contract', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_integration.dry_run', description: 'Validate official adapter contract without external network call', inputSchema: { type: 'object', properties: { modelId: { type: 'string' }, objective: { type: 'string' } } } },
  { name: 'aios.official_sandbox.security_check', description: 'Check official sandbox gates without exposing secrets or faking live readiness', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_sandbox.activation', description: 'Get official sandbox activation state', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_sandbox.activate', description: 'Attempt official sandbox activation only if secure environment gates are ready', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_sandbox.data_profiles', description: 'List approved official sandbox data profiles', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.official_sandbox.data_profile_create', description: 'Create or update a redacted approved real-data sandbox profile', inputSchema: { type: 'object', properties: { profileId: { type: 'string' }, name: { type: 'string' }, dataClassification: { type: 'string' }, approvalReference: { type: 'string' }, redactionRequired: { type: 'boolean' }, publicExportAllowed: { type: 'boolean' }, retentionDays: { type: 'number' } }, required: ['profileId', 'name', 'approvalReference'] } },
  { name: 'aios.restricted_access.requests', description: 'List restricted access requests', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.restricted_access.request', description: 'Create a restricted access request record', inputSchema: { type: 'object', properties: { operation: { type: 'string' }, environment: { type: 'string' }, justification: { type: 'string' }, artifactName: { type: 'string' }, artifactHash: { type: 'string' }, pathScope: { type: 'string' }, expiresInDays: { type: 'number' } }, required: ['operation', 'justification'] } },
  { name: 'aios.session.create', description: 'Create a Codex session', inputSchema: { type: 'object', properties: { title: { type: 'string' }, objective: { type: 'string' } } } },
  { name: 'aios.sessions.list', description: 'List Codex sessions', inputSchema: { type: 'object', properties: {} } },
  { name: 'aios.snapshot.create', description: 'Create a backend snapshot record', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, title: { type: 'string' }, filesChanged: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['sessionId'] } },
  { name: 'aios.handoff.create', description: 'Create a backend handoff record', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, reason: { type: 'string' }, context: { type: 'string' }, nextSteps: { type: 'array', items: { type: 'string' } } }, required: ['sessionId', 'reason'] } },
  { name: 'aios.handoffs.list', description: 'List handoffs for a Codex session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' } }, required: ['sessionId'] } },
  { name: 'aios.workbench.get', description: 'Get aggregated Workbench state for a Codex session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' } }, required: ['sessionId'] } },
  { name: 'aios.session.events', description: 'List events for a Codex session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' } }, required: ['sessionId'] } },
  { name: 'aios.session.workbench', description: 'Get aggregated Workbench state for a Codex session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' } }, required: ['sessionId'] } },
  { name: 'aios.session.files_changed', description: 'Record changed files for a Codex session', inputSchema: { type: 'object', properties: { sessionId: { type: 'string' }, filesChanged: { type: 'array', items: { type: 'string' } }, source: { type: 'string' } }, required: ['sessionId', 'filesChanged'] } },
  { name: 'aios.qos.enqueue', description: 'Enqueue a QoS job', inputSchema: { type: 'object', properties: { jobType: { type: 'string' }, payload: { type: 'object' } } } },
  { name: 'aios.codex.skill.execute', description: 'Execute a Codex skill through AIOS', inputSchema: { type: 'object', properties: { skillName: { type: 'string' }, input: { type: 'object' } }, required: ['skillName'] } },
  { name: 'aios.abuse.evaluate', description: 'Evaluate abuse signals', inputSchema: { type: 'object', properties: { toolCallFlood: { type: 'number' }, failedBuilds: { type: 'number' }, sessionSpike: { type: 'number' }, suspiciousCommand: { type: 'boolean' } } } },
];

async function callTool(name: string, args: any) {
  if (name === 'aios.entitlement.get') return text(await api('/entitlement/me'));
  if (name === 'aios.control_plane.status') return text(await api('/control-plane/status'));
  if (name === 'aios.heritage.summary') return text(await api('/aios/heritage/summary'));
  if (name === 'aios.scope.authority') return text(await api('/scope/authority'));
  if (name === 'aios.scope.preflight') return text(await api('/scope/preflight', { method: 'POST', body: JSON.stringify({ operation: args?.operation ?? 'codex.runtime.invoke', environment: args?.environment ?? 'sandbox', modelId: args?.modelId ?? 'codex-5.5-unlimited', requiresLiveRuntime: args?.requiresLiveRuntime ?? true, requiresRestrictedArtifacts: args?.requiresRestrictedArtifacts ?? false, reason: args?.reason ?? 'MCP RC15 scope preflight' }) }));
  if (name === 'aios.runtime_binding.status') return text(await api('/runtime/binding/status'));
  if (name === 'aios.product.manifest') return text(await api('/codex/product/manifest'));
  if (name === 'aios.codex.models') return text(await api('/codex/models'));
  if (name === 'aios.codex.plan_unlimited') return text(await api('/codex/plans/unlimited'));
  if (name === 'aios.subscription.me') return text(await api('/subscriptions/me'));
  if (name === 'aios.codex.runtime_status') return text(await api('/codex/runtime/status'));
  if (name === 'aios.codex.runtime_model_discovery') return text(await api('/codex/runtime/model-discovery'));
  if (name === 'aios.codex.runtime_invoke') return text(await api('/codex/runtime/invoke', { method: 'POST', body: JSON.stringify({ session_id: args.sessionId, model_id: args?.modelId ?? 'codex-5.5-unlimited', objective: args?.objective ?? 'MCP runtime invocation' }) }));
  if (name === 'aios.runtime_broker.status') return text(await api('/runtime/broker/status'));
  if (name === 'aios.runtime_broker.invoke') return text(await api('/runtime/broker/invoke', { method: 'POST', body: JSON.stringify({ sessionId: args.sessionId, objective: args.objective, provider: args?.provider ?? 'auto', intelligenceMode: 'aios_cognitive_runtime_mesh' }) }));
  if (name === 'aios.policy.language_evaluate') return text(await api('/policy/language/evaluate', { method: 'POST', body: JSON.stringify({ text: args.text }) }));
  if (name === 'aios.integration.guardrails') return text(await api('/policy/integration/guardrails'));
  if (name === 'aios.identity.profiles') return text(await api('/identity/profiles'));
  if (name === 'aios.secure_runtime.bridge') return text(await api('/codex/secure-runtime/bridge'));
  if (name === 'aios.secure_runtime.request') return text(await api('/codex/secure-runtime/request', { method: 'POST', body: JSON.stringify({ sessionId: args.sessionId, operation: args.operation, objective: args?.objective ?? 'MCP secure runtime request', payload: args?.payload ?? {} }) }));
  if (name === 'aios.context.index') return text(await api('/context/index', { method: 'POST', body: JSON.stringify({ sessionId: args?.sessionId, name: args?.name ?? 'MCP context index', source: args?.source ?? 'workspace', fileCount: args?.fileCount ?? 0, graphNodes: args?.graphNodes ?? 0, graphEdges: args?.graphEdges ?? 0 }) }));
  if (name === 'aios.context.query') return text(await api('/context/query', { method: 'POST', body: JSON.stringify({ query: args.query, sessionId: args?.sessionId, maxResults: args?.maxResults ?? 5 }) }));
  if (name === 'aios.skill_store.list') return text(await api('/skill-store'));
  if (name === 'aios.release.windows_manifest') return text(await api('/release/windows/manifest'));
  if (name === 'aios.official_integration.readiness') return text(await api('/official-integration/readiness'));
  if (name === 'aios.official_integration.adapter_contract') return text(await api('/official-integration/adapter/contract'));
  if (name === 'aios.official_integration.dry_run') return text(await api('/official-integration/adapter/dry-run', { method: 'POST', body: JSON.stringify({ modelId: args?.modelId ?? 'codex-5.5-unlimited', objective: args?.objective ?? 'MCP official adapter dry run' }) }));
  if (name === 'aios.official_sandbox.security_check') return text(await api('/official-sandbox/security-check'));
  if (name === 'aios.official_sandbox.activation') return text(await api('/official-sandbox/activation'));
  if (name === 'aios.official_sandbox.activate') return text(await api('/official-sandbox/activate', { method: 'POST' }));
  if (name === 'aios.official_sandbox.data_profiles') return text(await api('/official-sandbox/data-profiles'));
  if (name === 'aios.official_sandbox.data_profile_create') return text(await api('/official-sandbox/data-profiles', { method: 'POST', body: JSON.stringify({ profileId: args.profileId, name: args.name, dataClassification: args?.dataClassification ?? 'real_sandbox_approved', approvalReference: args.approvalReference, redactionRequired: args?.redactionRequired ?? true, publicExportAllowed: args?.publicExportAllowed ?? false, retentionDays: args?.retentionDays ?? 30 }) }));
  if (name === 'aios.restricted_access.requests') return text(await api('/restricted-access/requests'));
  if (name === 'aios.restricted_access.request') return text(await api('/restricted-access/requests', { method: 'POST', body: JSON.stringify({ operation: args.operation, environment: args?.environment ?? 'sandbox_approved_machine', justification: args.justification, artifactName: args?.artifactName ?? '', artifactHash: args?.artifactHash ?? '', pathScope: args?.pathScope ?? 'C:\\AIOS\\aios-codex-unlimited-enterprise-v2', expiresInDays: args?.expiresInDays ?? 30 }) }));
  if (name === 'aios.session.create') return text(await api('/sessions', { method: 'POST', body: JSON.stringify({ title: args?.title ?? 'MCP Codex Session', objective: args?.objective ?? 'MCP created session' }) }));
  if (name === 'aios.sessions.list') return text(await api('/sessions'));
  if (name === 'aios.snapshot.create') return text(await api('/snapshots', { method: 'POST', body: JSON.stringify({ sessionId: args.sessionId, title: args?.title ?? 'MCP snapshot', filesChanged: args?.filesChanged ?? [], notes: args?.notes ?? '' }) }));
  if (name === 'aios.handoff.create') return text(await api('/handoffs', { method: 'POST', body: JSON.stringify({ sessionId: args.sessionId, reason: args.reason, context: args?.context ?? '', nextSteps: args?.nextSteps ?? [] }) }));
  if (name === 'aios.handoffs.list') return text(await api(`/sessions/${args.sessionId}/handoffs`));
  if (name === 'aios.workbench.get') return text(await api(`/sessions/${args.sessionId}/workbench`));
  if (name === 'aios.session.events') return text(await api(`/sessions/${args.sessionId}/events`));
  if (name === 'aios.session.workbench') return text(await api(`/sessions/${args.sessionId}/workbench`));
  if (name === 'aios.session.files_changed') return text(await api(`/sessions/${args.sessionId}/files-changed`, { method: 'POST', body: JSON.stringify({ filesChanged: args.filesChanged, source: args?.source ?? 'aios-mcp-core' }) }));
  if (name === 'aios.qos.enqueue') return text(await api('/qos/enqueue', { method: 'POST', body: JSON.stringify({ jobType: args?.jobType ?? 'codex_run', payload: args?.payload ?? {} }) }));
  if (name === 'aios.codex.skill.execute') return text(await api('/codex/skill/execute', { method: 'POST', body: JSON.stringify({ skillName: args.skillName, input: args?.input ?? {} }) }));
  if (name === 'aios.abuse.evaluate') return text(await api('/abuse/evaluate', { method: 'POST', body: JSON.stringify(args ?? {}) }));
  throw new Error(`Unknown tool: ${name}`);
}

function send(message: unknown) {
  const body = JSON.stringify(message);
  process.stdout.write(`Content-Length: ${Buffer.byteLength(body, 'utf8')}\r\n\r\n${body}`);
}

async function handle(request: RpcRequest) {
  try {
    if (request.method === 'initialize') {
      send({ jsonrpc: '2.0', id: request.id, result: { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'aios-mcp-core', version: '0.1.0' } } });
    } else if (request.method === 'tools/list') {
      send({ jsonrpc: '2.0', id: request.id, result: { tools } });
    } else if (request.method === 'tools/call') {
      send({ jsonrpc: '2.0', id: request.id, result: await callTool(request.params.name, request.params.arguments ?? {}) });
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
