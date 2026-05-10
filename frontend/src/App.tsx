import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Boxes,
  CheckCircle2,
  ClipboardList,
  Code2,
  FileText,
  FileDown,
  Gauge,
  GitBranch,
  History,
  KeyRound,
  Layers3,
  LockKeyhole,
  LogOut,
  Mic,
  Play,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  Terminal,
  Workflow,
} from 'lucide-react';
import { useApi } from './api';
import type {
  CodexModelInfo,
  CodexPlanInfo,
  CodexProductManifest,
  CodexSession,
  ControlPlaneStatus,
  ContextIndexInfo,
  Entitlement,
  Handoff,
  IdentityProfile,
  IntegrationGuardrails,
  LanguageEvaluation,
  LicenseStatus,
  LegacyAiosSummary,
  OfficialIntegrationReadiness,
  OfficialSandboxActivation,
  OfficialSandboxSecurityCheck,
  NoDeveloperCostProvider,
  NoDeveloperCostRecommendation,
  QosJob,
  RestrictedAccessRequestInfo,
  RuntimeBindingStatus,
  RuntimeModelDiscovery,
  RuntimeBrokerProvider,
  RuntimeBrokerStatus,
  RuntimeStatus,
  SandboxDataProfile,
  SecureRuntimeBridge,
  ScopeAuthority,
  ScopePreflight,
  Snapshot,
  SubscriptionInfo,
  SkillStoreItem,
  WindowsReleaseManifest,
  WorkbenchState,
} from './types';

declare global {
  interface Window {
    puter?: {
      ai?: {
        chat?: (prompt: string, options?: Record<string, unknown>) => Promise<unknown>;
      };
    };
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
  }
}

type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: (() => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  start: () => void;
};

const PUTER_SCRIPT_ID = 'puter-js-v2';

let puterScriptPromise: Promise<void> | null = null;

function loadPuterScript() {
  if (window.puter?.ai?.chat) {
    return Promise.resolve();
  }
  if (puterScriptPromise) {
    return puterScriptPromise;
  }
  puterScriptPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById(PUTER_SCRIPT_ID) as HTMLScriptElement | null;
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => reject(new Error('Falha ao carregar Puter.js.')), { once: true });
      return;
    }
    const script = document.createElement('script');
    script.id = PUTER_SCRIPT_ID;
    script.src = 'https://js.puter.com/v2/';
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Falha ao carregar Puter.js.'));
    document.head.appendChild(script);
  });
  return puterScriptPromise;
}

function puterResponseToText(response: unknown) {
  if (typeof response === 'string') {
    return response;
  }
  if (response && typeof response === 'object') {
    const maybeText = response as { text?: unknown; message?: unknown; content?: unknown };
    if (typeof maybeText.text === 'string') return maybeText.text;
    if (typeof maybeText.message === 'string') return maybeText.message;
    if (typeof maybeText.content === 'string') return maybeText.content;
  }
  return JSON.stringify(response ?? '', null, 2);
}

type PanelState = {
  entitlement?: Entitlement;
  licenseStatus?: LicenseStatus;
  scopeAuthority?: ScopeAuthority;
  scopePreflight?: ScopePreflight;
  runtimeBinding?: RuntimeBindingStatus;
  controlPlane?: ControlPlaneStatus;
  heritage?: LegacyAiosSummary;
  sessions: CodexSession[];
  selectedSessionId: string;
  snapshots: Snapshot[];
  handoffs: Handoff[];
  workbench?: WorkbenchState;
  productManifest?: CodexProductManifest;
  codexModels: CodexModelInfo[];
  unlimitedPlan?: CodexPlanInfo;
  subscription?: SubscriptionInfo;
  runtimeStatus?: RuntimeStatus;
  runtimeModelDiscovery?: RuntimeModelDiscovery;
  runtimeInvokeResult?: Record<string, unknown>;
  runtimeBrokerProviders: RuntimeBrokerProvider[];
  runtimeBrokerStatus?: RuntimeBrokerStatus;
  runtimeBrokerInvokeResult?: Record<string, unknown>;
  noCostProviders: NoDeveloperCostProvider[];
  noCostRecommendation?: NoDeveloperCostRecommendation;
  puterRuntimeResult?: Record<string, unknown>;
  integrationGuardrails?: IntegrationGuardrails;
  identityProfiles: IdentityProfile[];
  secureRuntimeBridge?: SecureRuntimeBridge;
  contextIndex?: ContextIndexInfo;
  contextQuery?: Record<string, unknown>;
  skillStore: SkillStoreItem[];
  windowsRelease?: WindowsReleaseManifest;
  secureBridgeResult?: Record<string, unknown>;
  officialReadiness?: OfficialIntegrationReadiness;
  officialAdapterContract?: Record<string, unknown>;
  officialDryRun?: Record<string, unknown>;
  officialSandboxSecurity?: OfficialSandboxSecurityCheck;
  officialSandboxActivation?: OfficialSandboxActivation;
  officialSandboxActivateResult?: Record<string, unknown>;
  restrictedAccessLogResult?: Record<string, unknown>;
  sandboxDataProfiles: SandboxDataProfile[];
  restrictedRequests: RestrictedAccessRequestInfo[];
  officialLanguage?: LanguageEvaluation;
  blockedLanguage?: LanguageEvaluation;
  lastJob?: QosJob;
  lastRun?: Record<string, unknown>;
  lastSkill?: Record<string, unknown>;
  abuse?: Record<string, unknown>;
};

const initialState: PanelState = {
  sessions: [],
  selectedSessionId: '',
  snapshots: [],
  handoffs: [],
  codexModels: [],
  runtimeBrokerProviders: [],
  noCostProviders: [],
  identityProfiles: [],
  skillStore: [],
  sandboxDataProfiles: [],
  restrictedRequests: [],
};

function LoginScreen() {
  const api = useApi();
  const [email, setEmail] = useState('admin@aios.local');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await api.login(email, password);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel">
        <div className="brand-mark">
          <Sparkles size={28} />
        </div>
        <h1>AIOS Codex Unlimited</h1>
        <p>Codex sem limites. Desenvolvimento sem interrupcoes.</p>
        <form onSubmit={submit} className="login-form">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" />
          </label>
          <label>
            Senha
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </label>
          <button type="submit" disabled={loading}>
            <KeyRound size={18} />
            {loading ? 'Entrando...' : 'Entrar no Workbench'}
          </button>
        </form>
        {api.apiError ? <p className="api-error">{api.apiError}</p> : null}
      </section>
    </main>
  );
}

function MetricCard({
  icon,
  label,
  value,
  tone = 'neutral',
}: {
  icon: ReactNode;
  label: string;
  value: string | number;
  tone?: 'neutral' | 'green' | 'blue' | 'amber';
}) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function JsonPreview({ value }: { value: unknown }) {
  return <pre className="json-preview">{JSON.stringify(value ?? {}, null, 2)}</pre>;
}

function AppShell({ children }: { children: ReactNode }) {
  const api = useApi();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark small">
            <Sparkles size={20} />
          </div>
          <div>
            <strong>AIOS</strong>
            <span>Codex Unlimited</span>
          </div>
        </div>
        <nav>
          <a className="active"><Workflow size={18} /> Workbench</a>
          <a><Gauge size={18} /> Control Plane</a>
          <a><ShieldCheck size={18} /> Governance</a>
          <a><Boxes size={18} /> MCP</a>
        </nav>
        <button className="ghost-button" onClick={api.logout}>
          <LogOut size={18} />
          Sair
        </button>
      </aside>
      {children}
    </div>
  );
}

export function App() {
  const api = useApi();
  const [state, setState] = useState<PanelState>(initialState);
  const [objective, setObjective] = useState('Criar uma sessao Codex continua com MCP, snapshots, handoff e QoS.');
  const [actionLoading, setActionLoading] = useState('');
  const [voiceState, setVoiceState] = useState('');

  const selectedSession = useMemo(
    () => state.sessions.find((session) => session.id === state.selectedSessionId) ?? state.sessions[0],
    [state.selectedSessionId, state.sessions],
  );

  const refresh = useCallback(async () => {
    if (!api.isAuthenticated) {
      return;
    }
    setActionLoading('refresh');
    try {
      const [
        entitlement,
        licenseStatus,
        scopeAuthority,
        runtimeBinding,
        controlPlane,
        heritage,
        sessions,
        productManifest,
        codexModels,
        unlimitedPlan,
        subscription,
        runtimeStatus,
        runtimeBrokerProviders,
        runtimeBrokerStatus,
        noCostProvidersCatalog,
        noCostRecommendation,
        integrationGuardrails,
        identityProfiles,
        secureRuntimeBridge,
        skillStore,
        windowsRelease,
        officialReadiness,
        officialSandboxSecurity,
        officialSandboxActivation,
        sandboxDataProfiles,
        restrictedRequests,
      ] = await Promise.all([
        api.getEntitlement(),
        api.licenseStatus(),
        api.scopeAuthority(),
        api.runtimeBindingStatus(),
        api.getControlPlane(),
        api.getHeritageSummary(),
        api.listSessions(),
        api.productManifest(),
        api.codexModels(),
        api.unlimitedPlan(),
        api.subscriptionMe(),
        api.runtimeStatus(),
        api.runtimeBrokerProviders(),
        api.runtimeBrokerStatus(),
        api.noDeveloperCostProviders(),
        api.noDeveloperCostRecommendation(),
        api.integrationGuardrails(),
        api.identityProfiles(),
        api.secureRuntimeBridge(),
        api.skillStore(),
        api.windowsReleaseManifest(),
        api.officialIntegrationReadiness(),
        api.officialSandboxSecurityCheck(),
        api.officialSandboxActivation(),
        api.listSandboxDataProfiles(),
        api.listRestrictedAccessRequests(),
      ]);
      setState((current) => ({
        ...current,
        entitlement,
        licenseStatus,
        scopeAuthority,
        runtimeBinding,
        controlPlane,
        heritage,
        sessions,
        productManifest,
        codexModels,
        unlimitedPlan,
        subscription,
        runtimeStatus,
        runtimeBrokerProviders: runtimeBrokerProviders.providers,
        runtimeBrokerStatus,
        noCostProviders: noCostProvidersCatalog.providers,
        noCostRecommendation,
        integrationGuardrails,
        identityProfiles,
        secureRuntimeBridge,
        skillStore,
        windowsRelease,
        officialReadiness,
        officialSandboxSecurity,
        officialSandboxActivation,
        sandboxDataProfiles,
        restrictedRequests,
        selectedSessionId: current.selectedSessionId || sessions[0]?.id || '',
      }));
    } finally {
      setActionLoading('');
    }
  }, [api]);

  const loadWorkbench = useCallback(
    async (sessionId: string) => {
      const workbench = await api.getSessionWorkbench(sessionId);
      setState((current) => ({
        ...current,
        workbench,
        entitlement: current.entitlement ?? workbench.entitlement,
        snapshots: workbench.snapshots,
        handoffs: workbench.handoffs,
        heritage: current.heritage ?? workbench.heritage ?? workbench.legacyLineage,
      }));
    },
    [api],
  );

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!api.isAuthenticated || !selectedSession?.id) {
      return;
    }
    loadWorkbench(selectedSession.id).catch(() => undefined);
  }, [api.isAuthenticated, loadWorkbench, selectedSession?.id]);

  async function runAction<T>(name: string, action: () => Promise<T>) {
    setActionLoading(name);
    try {
      return await action();
    } finally {
      setActionLoading('');
    }
  }

  async function createSession() {
    const created = await runAction('session', () => api.createSession('Workbench Codex Session', objective));
    if (!created) return;
    setState((current) => ({
      ...current,
      sessions: [created, ...current.sessions],
      selectedSessionId: created.id,
    }));
    await loadWorkbench(created.id);
    await refresh();
  }

  function startVoiceCommand() {
    const SpeechRecognition = window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceState('Reconhecimento de voz indisponivel neste navegador.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'pt-BR';
    recognition.onstart = () => setVoiceState('Ouvindo comando...');
    recognition.onerror = () => setVoiceState('Falha ao ouvir comando.');
    recognition.onend = () => setVoiceState((current) => current || 'Escuta finalizada.');
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript?.trim();
      if (transcript) {
        setObjective(transcript);
        setVoiceState('Comando aplicado ao objetivo.');
      }
    };
    recognition.start();
  }

  function generateExecutiveReport() {
    const session = selectedSession;
    const report = {
      generatedAt: new Date().toLocaleString('pt-BR'),
      product: 'AIOS Codex Unlimited',
      sessionId: session?.id ?? 'sem-sessao-selecionada',
      sessionTitle: session?.title ?? 'Sem sessao selecionada',
      objective,
      runtimeProvider: state.runtimeBrokerStatus?.recommendedProvider ?? state.runtimeStatus?.adapter ?? 'local',
      model: state.runtimeBrokerInvokeResult?.model ?? state.runtimeModelDiscovery?.recommendedModel ?? 'pendente',
      licenseStatus: state.licenseStatus?.status ?? 'nao consultado',
      workbenchEvents: state.workbench?.recentEvents?.slice(0, 5).map((event) => `${event.type}: ${event.title || event.message}`) ?? [],
      note: 'Relatorio executivo gerado localmente. Nao inclui segredos, API keys ou payload privado.',
    };
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>AIOS RC13 Report</title><style>body{font-family:Inter,Arial,sans-serif;margin:40px;color:#111827}h1{color:#0f766e}pre{background:#111827;color:#e5e7eb;padding:18px;border-radius:8px;white-space:pre-wrap}.meta{color:#475569}</style></head><body><h1>AIOS Codex Unlimited</h1><p class="meta">Relatorio executivo de sessao - ${report.generatedAt}</p><pre>${JSON.stringify(report, null, 2).replace(/[<>&]/g, (char) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[char] ?? char))}</pre><p>Use Ctrl+P para salvar como PDF.</p></body></html>`;
    const reportWindow = window.open('', '_blank', 'width=900,height=720');
    if (reportWindow) {
      reportWindow.document.write(html);
      reportWindow.document.close();
      reportWindow.focus();
      reportWindow.print();
      return;
    }
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `relatorio-sessao-${report.sessionId}.html`;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  async function createSnapshot() {
    if (!selectedSession) return;
    const snapshot = await runAction('snapshot', () =>
      api.createSnapshot(
        selectedSession.id,
        'Workbench checkpoint',
        ['frontend/src/App.tsx', 'backend/app/main.py', 'mcp/aios-mcp-repo/src/server.ts'],
        'Snapshot criado pelo Workbench.',
      ),
    );
    if (!snapshot) return;
    await loadWorkbench(selectedSession.id);
  }

  async function createHandoff() {
    if (!selectedSession) return;
    const files = state.workbench?.filesChanged?.length ? state.workbench.filesChanged.join(', ') : 'sem arquivos registrados';
    const handoff = await runAction('handoff', () =>
      api.createHandoff(
        selectedSession.id,
        'Continuar a implementacao a partir do checkpoint atual.',
        `Objetivo: ${selectedSession.objective}. Arquivos recentes: ${files}.`,
        ['Revisar snapshot mais recente', 'Executar build/testes', 'Atualizar docs se houver novo recurso'],
      ),
    );
    if (!handoff) return;
    await loadWorkbench(selectedSession.id);
  }

  async function enqueueBuild() {
    const job = await runAction('qos', () => api.enqueueQos('build', { command: 'npm run build', sessionId: selectedSession?.id }));
    if (!job) return;
    setState((current) => ({ ...current, lastJob: job }));
    if (selectedSession) {
      await loadWorkbench(selectedSession.id);
    }
    await refresh();
  }

  async function runCodex() {
    const result = await runAction('codex', () => api.runCodex(objective, selectedSession?.id));
    if (!result) return;
    setState((current) => ({ ...current, lastRun: result }));
  }

  async function executeSkill() {
    const result = await runAction('skill', () => api.executeSkill('workbench.status_brief', { objective, sessionId: selectedSession?.id }));
    if (!result) return;
    setState((current) => ({ ...current, lastSkill: result }));
    if (selectedSession) {
      await loadWorkbench(selectedSession.id);
    }
  }

  async function simulateMcpEvent() {
    if (!selectedSession) return;
    await runAction('mcp-event', () =>
      api.createSessionEvent(selectedSession.id, {
        type: 'mcp.tool_call',
        source: 'workbench-local',
        title: 'repo.search',
        message: 'Evento MCP local registrado manualmente no Workbench.',
        payload: { tool: 'repo.search', query: 'Codex Workbench', mode: 'local-manual' },
      }),
    );
    await api.addFilesChanged(selectedSession.id, ['frontend/src/App.tsx'], 'workbench-local');
    await loadWorkbench(selectedSession.id);
  }

  async function loadProductManifest() {
    const productManifest = await runAction('manifest', () => api.productManifest());
    if (!productManifest) return;
    setState((current) => ({ ...current, productManifest }));
  }

  async function listCodexModels() {
    const codexModels = await runAction('models', () => api.codexModels());
    if (!codexModels) return;
    setState((current) => ({ ...current, codexModels }));
  }

  async function viewUnlimitedPlan() {
    const unlimitedPlan = await runAction('plan', () => api.unlimitedPlan());
    if (!unlimitedPlan) return;
    setState((current) => ({ ...current, unlimitedPlan }));
  }

  async function viewSubscription() {
    const subscription = await runAction('subscription', () => api.subscriptionMe());
    if (!subscription) return;
    setState((current) => ({ ...current, subscription }));
  }

  async function loadRuntimeStatus() {
    const runtimeStatus = await runAction('runtime-status', () => api.runtimeStatus());
    if (!runtimeStatus) return;
    setState((current) => ({ ...current, runtimeStatus }));
  }

  async function discoverRuntimeModel() {
    const runtimeModelDiscovery = await runAction('runtime-model-discovery', () => api.runtimeModelDiscovery());
    if (!runtimeModelDiscovery) return;
    setState((current) => ({ ...current, runtimeModelDiscovery }));
  }

  async function invokeRuntime() {
    const session = selectedSession ?? await api.createSession('RC2 Runtime Session', objective);
    if (!selectedSession) {
      setState((current) => ({
        ...current,
        sessions: [session, ...current.sessions],
        selectedSessionId: session.id,
      }));
    }
    const runtimeInvokeResult = await runAction('runtime-invoke', () =>
      api.runtimeInvoke(session.id, 'codex-5.5-unlimited', objective),
    );
    if (!runtimeInvokeResult) return;
    setState((current) => ({ ...current, runtimeInvokeResult }));
    await loadWorkbench(session.id);
    await refresh();
  }

  async function loadRuntimeBrokerStatus() {
    const result = await runAction('runtime-broker-status', () =>
      Promise.all([api.runtimeBrokerProviders(), api.runtimeBrokerStatus()]),
    );
    const [providerCatalog, runtimeBrokerStatus] = result ?? [];
    if (!providerCatalog || !runtimeBrokerStatus) return;
    setState((current) => ({
      ...current,
      runtimeBrokerProviders: providerCatalog.providers,
      runtimeBrokerStatus,
      runtimeBrokerInvokeResult: runtimeBrokerStatus,
    }));
  }

  async function invokeRuntimeBroker() {
    const session = selectedSession ?? await api.createSession('RC12 Runtime Broker Session', objective);
    if (!selectedSession) {
      setState((current) => ({
        ...current,
        sessions: [session, ...current.sessions],
        selectedSessionId: session.id,
      }));
    }
    const runtimeBrokerInvokeResult = await runAction('runtime-broker-invoke', () =>
      api.runtimeBrokerInvoke(session.id, objective, 'auto'),
    );
    if (!runtimeBrokerInvokeResult) return;
    setState((current) => ({ ...current, runtimeBrokerInvokeResult }));
    await loadWorkbench(session.id);
    await refresh();
  }

  async function loadNoDeveloperCostProviders() {
    const result = await runAction('no-cost-providers', () =>
      Promise.all([api.noDeveloperCostProviders(), api.noDeveloperCostRecommendation()]),
    );
    const [providerCatalog, noCostRecommendation] = result ?? [];
    if (!providerCatalog || !noCostRecommendation) return;
    setState((current) => ({
      ...current,
      noCostProviders: providerCatalog.providers,
      noCostRecommendation,
      puterRuntimeResult: {
        strategy: providerCatalog.strategy,
        primaryProvider: providerCatalog.primaryProvider,
        warning: providerCatalog.warning,
      },
    }));
  }

  async function invokePuterUserPays() {
    const session = selectedSession ?? await api.createSession('Puter User-Pays Codex Session', objective);
    if (!selectedSession) {
      setState((current) => ({
        ...current,
        sessions: [session, ...current.sessions],
        selectedSessionId: session.id,
      }));
    }

    const result = await runAction('puter-user-pays', async () => {
      await loadPuterScript();
      const chat = window.puter?.ai?.chat;
      if (!chat) {
        throw new Error('Puter.js carregou, mas puter.ai.chat nao ficou disponivel.');
      }
      const providerResult = await chat(objective, {
        model: 'openai/gpt-5.3-codex',
        stream: false,
      });
      const outputText = puterResponseToText(providerResult);
      const event = await api.createSessionEvent(session.id, {
        type: 'codex.runtime.completed',
        source: 'puter-browser-user-pays',
        title: 'Puter Codex user-pays completed',
        message: outputText,
        payload: {
          provider: 'puter_user_pays',
          model: 'openai/gpt-5.3-codex',
          developerCost: 'none_direct',
          networkCallPerformed: true,
          backendReceivedProviderSecret: false,
        },
      });
      return {
        provider: 'puter_user_pays',
        model: 'openai/gpt-5.3-codex',
        outputText,
        eventId: event.id,
        developerCost: 'none_direct',
        backendReceivedProviderSecret: false,
      };
    });
    if (!result) return;
    setState((current) => ({ ...current, puterRuntimeResult: result }));
    await loadWorkbench(session.id);
    await refresh();
  }

  async function requestSecureBridge() {
    const session = selectedSession ?? await api.createSession('RC3 Secure Bridge Session', objective);
    if (!selectedSession) {
      setState((current) => ({
        ...current,
        sessions: [session, ...current.sessions],
        selectedSessionId: session.id,
      }));
    }
    const secureBridgeResult = await runAction('secure-bridge', () =>
      api.secureRuntimeRequest(
        session.id,
        'official_runtime_invoke',
        'Solicitar execucao pelo Secure Runtime Bridge sem artefatos privados.',
        { modelId: 'codex-5.5-unlimited', releaseChannel: 'rc3' },
      ),
    );
    if (!secureBridgeResult) return;
    setState((current) => ({ ...current, secureBridgeResult }));
    await loadWorkbench(session.id);
  }

  async function buildContextIndex() {
    const contextIndex = await runAction('context-index', () =>
      api.createContextIndex({
        sessionId: selectedSession?.id,
        name: 'RC3 local context capsule',
        source: 'workspace',
        fileCount: 120,
        graphNodes: 450,
        graphEdges: 900,
      }),
    );
    if (!contextIndex) return;
    setState((current) => ({ ...current, contextIndex }));
  }

  async function queryContextEngine() {
    const contextQuery = await runAction('context-query', () =>
      api.queryContext('secure runtime bridge policy skill store windows release', selectedSession?.id),
    );
    if (!contextQuery) return;
    setState((current) => ({ ...current, contextQuery }));
  }

  async function loadOfficialAdapterContract() {
    const officialAdapterContract = await runAction('official-contract', () => api.officialAdapterContract());
    if (!officialAdapterContract) return;
    setState((current) => ({ ...current, officialAdapterContract }));
  }

  async function runOfficialDryRun() {
    const officialDryRun = await runAction('official-dry-run', () =>
      api.officialAdapterDryRun('codex-5.5-unlimited', 'Validar contrato do OfficialCodexRuntimeAdapter sem chamada externa.'),
    );
    if (!officialDryRun) return;
    setState((current) => ({ ...current, officialDryRun }));
  }

  async function checkOfficialSandbox() {
    const result = await runAction('official-sandbox-check', () =>
      Promise.all([api.officialSandboxSecurityCheck(), api.officialSandboxActivation()]),
    );
    const [officialSandboxSecurity, officialSandboxActivation] = result ?? [];
    if (!officialSandboxSecurity || !officialSandboxActivation) return;
    setState((current) => ({ ...current, officialSandboxSecurity, officialSandboxActivation }));
  }

  async function registerRealSandboxDataProfile() {
    const profile = await runAction('sandbox-data-profile', () =>
      api.createSandboxDataProfile({
        profileId: 'rc5-real-data-approved',
        name: 'RC5 Real Data Approved',
        dataClassification: 'real_sandbox_approved',
        approvalReference: 'meeting-2026-05-09',
        redactionRequired: true,
        publicExportAllowed: false,
        retentionDays: 30,
      }),
    );
    if (!profile) return;
    const sandboxDataProfiles = await api.listSandboxDataProfiles();
    const officialSandboxSecurity = await api.officialSandboxSecurityCheck();
    setState((current) => ({ ...current, sandboxDataProfiles, officialSandboxSecurity }));
  }

  async function activateOfficialSandbox() {
    const officialSandboxActivateResult = await runAction('official-sandbox-activate', () => api.activateOfficialSandbox());
    if (!officialSandboxActivateResult) return;
    const officialSandboxSecurity = await api.officialSandboxSecurityCheck();
    const officialSandboxActivation = await api.officialSandboxActivation();
    setState((current) => ({ ...current, officialSandboxActivateResult, officialSandboxSecurity, officialSandboxActivation }));
  }

  async function requestRuntimePatchAccess() {
    const request = await runAction('restricted-request', () =>
      api.createRestrictedAccessRequest({
        operation: 'runtime_patch',
        environment: 'sandbox_approved_machine',
        justification: 'Validar patch de compatibilidade do runtime para o OfficialCodexRuntimeAdapter.',
        artifactName: 'codex-runtime-sandbox',
        artifactHash: 'sha256:approved-artifact-hash-required',
        pathScope: 'C:\\AIOS\\aios-codex-unlimited-enterprise-v2',
        expiresInDays: 30,
      }),
    );
    if (!request) return;
    const restrictedRequests = await api.listRestrictedAccessRequests();
    setState((current) => ({ ...current, restrictedRequests }));
  }

  async function recordRestrictedAccessLog() {
    const approved = state.restrictedRequests.find((item) => item.operation === 'runtime_patch' && item.activeApproval);
    if (!approved) return;
    const restrictedAccessLogResult = await runAction('restricted-access-log', () =>
      api.recordRestrictedAccessLog(approved.id, {
        action: 'runtime_patch_dry_run',
        artifactPath: 'C:\\AIOS\\aios-codex-unlimited-enterprise-v2\\restricted\\codex-runtime-sandbox.bin',
        artifactHash: approved.artifactHash,
        justification: 'Registrar acesso restrito conforme contrato assinado.',
        result: 'recorded',
      }),
    );
    if (!restrictedAccessLogResult) return;
    setState((current) => ({ ...current, restrictedAccessLogResult }));
  }

  async function testOfficialLanguage() {
    const officialLanguage = await runAction('language-official', () =>
      api.languageEvaluate('AIOS Codex Unlimited com Codex sem limites e Sessoes Codex continuas.'),
    );
    if (!officialLanguage) return;
    setState((current) => ({ ...current, officialLanguage }));
  }

  async function testBlockedLanguage() {
    const blockedLanguage = await runAction('language-blocked', () =>
      api.languageEvaluate('Tentativa de bypass para contornar limite.'),
    );
    if (!blockedLanguage) return;
    setState((current) => ({ ...current, blockedLanguage }));
  }

  async function runScopePreflight() {
    const scopePreflight = await runAction('scope-preflight', () =>
      api.scopePreflight({
        operation: 'codex.runtime.invoke',
        environment: 'sandbox',
        modelId: 'codex-5.5-unlimited',
        requiresLiveRuntime: true,
        requiresRestrictedArtifacts: false,
        reason: objective,
      }),
    );
    if (!scopePreflight) return;
    setState((current) => ({ ...current, scopePreflight }));
  }

  async function refreshRuntimeBinding() {
    const runtimeBinding = await runAction('runtime-binding', () => api.runtimeBindingStatus());
    if (!runtimeBinding) return;
    setState((current) => ({ ...current, runtimeBinding }));
  }

  async function evaluateAbuse() {
    const result = await runAction('abuse', () =>
      api.evaluateAbuse({ toolCallFlood: 2, failedBuilds: 0, sessionSpike: state.sessions.length, suspiciousCommand: false }),
    );
    if (!result) return;
    setState((current) => ({ ...current, abuse: result }));
  }

  if (!api.isAuthenticated) {
    return <LoginScreen />;
  }

  const filesChanged = state.workbench?.filesChanged ?? [];
  const buildStatus = state.workbench?.buildStatus?.status ?? state.lastJob?.status ?? 'not_queued';
  const heritage = state.heritage ?? state.workbench?.legacyLineage;

  return (
    <AppShell>
      <main className="workspace">
        <header className="topbar">
          <div>
            <h1>Codex Workbench</h1>
            <p>Pare de medir uso. Comece a construir.</p>
          </div>
          <button className="secondary-button" onClick={refresh} disabled={actionLoading === 'refresh'}>
            <RefreshCcw size={18} />
            Atualizar Workbench
          </button>
        </header>

        {api.apiError ? <div className="banner-error">{api.apiError}</div> : null}

        <section className="metrics-grid">
          <MetricCard icon={<CheckCircle2 size={20} />} label="Plano" value={state.entitlement?.plan ?? 'carregando'} tone="green" />
          <MetricCard icon={<Layers3 size={20} />} label="Unidade" value={state.entitlement?.productUnit ?? 'codex_sessions'} tone="blue" />
          <MetricCard icon={<Gauge size={20} />} label="Fila QoS" value={state.controlPlane?.queueDepth ?? 0} tone="amber" />
          <MetricCard icon={<Activity size={20} />} label="Sessoes ativas" value={state.controlPlane?.activeSessions ?? 0} />
        </section>

        <section className="detail-panel product-core-panel product-launch-panel" aria-labelledby="aios-product-shell-title">
          <div className="product-launch-grid">
            <div className="product-launch-copy">
              <span className="product-kicker">RC20 Product Shell</span>
              <h2 id="aios-product-shell-title">AIOS Livre / Codex Unlimited</h2>
              <p>
                App Windows/Desktop para engenharia com Sessoes Codex, Workbench Premium,
                Agent Room, snapshots, handoff, auditoria, redaction e runtime delegado.
              </p>
              <div className="product-pill-row" aria-label="Contrato de produto">
                <span>Conta vinculada</span>
                <span>Sessoes Codex</span>
                <span>API key nao armazenada</span>
                <span>Sem medidor de limite na UX</span>
              </div>
              <a
                className="product-doc-link"
                href="https://github.com/dgrich33/AIOS/blob/main/docs/product/PRODUCT_THREAT_MODEL.md"
                target="_blank"
                rel="noreferrer"
              >
                Docs de governanca
              </a>
            </div>
            <div className="product-launch-stack" aria-label="Pilares do produto">
              <div>
                <Sparkles size={18} />
                <strong>AIOS Workbench Premium</strong>
                <span>Timeline, diff visual, build/test logs, risk score e relatorio executivo.</span>
              </div>
              <div>
                <Workflow size={18} />
                <strong>Codex Delegated Runtime</strong>
                <span>Auth delegada por conta/plano elegivel, sem chave de API colada no app.</span>
              </div>
              <div>
                <ShieldCheck size={18} />
                <strong>Governanca por sessao</strong>
                <span>Approval Gate, RBAC, auditoria e redaction antes de exportar evidencia.</span>
              </div>
            </div>
          </div>
        </section>

        <section className="workbench-grid">
          <article className="detail-panel product-core-panel">
            <div className="panel-heading">
              <div>
                <h2>Product Manifest</h2>
                <p>{state.productManifest?.headline ?? 'Codex sem limites. Desenvolvimento sem interrupcoes.'}</p>
              </div>
              <span className="status-pill">{state.productManifest?.productUnit ?? 'codex_sessions'}</span>
            </div>
            <div className="module-grid">
              {(state.productManifest?.systems ?? ['Codex Runtime Gateway', 'Codex Model Registry', 'Codex Workbench']).slice(0, 8).map((system) => (
                <span key={system}>{system}</span>
              ))}
            </div>
            <div className="stacked-actions two">
              <button className="secondary-button full" onClick={loadProductManifest} disabled={Boolean(actionLoading)}>
                <FileText size={17} />
                Carregar Manifest
              </button>
              <button className="secondary-button full" onClick={viewUnlimitedPlan} disabled={Boolean(actionLoading)}>
                <ShieldCheck size={17} />
                Ver Plano Unlimited
              </button>
            </div>
          </article>

          <article className="detail-panel product-core-panel rc13-license-panel">
            <div className="panel-heading">
              <div>
                <h2>Licenca Local RC13</h2>
                <p>{state.licenseStatus?.message ?? 'Valida o modo local controlado sem expor credenciais externas.'}</p>
              </div>
              <span className={state.licenseStatus?.hashAuthorized ? 'status-pill' : 'status-pill warn'}>
                {state.licenseStatus?.status ?? 'carregando'}
              </span>
            </div>
            <dl className="detail-list">
              <dt>Arquivo</dt>
              <dd>{state.licenseStatus?.licensePath ?? 'C:\\AIOS\\aios-codex-unlimited-enterprise-v2\\license.cert'}</dd>
              <dt>Hash</dt>
              <dd>{state.licenseStatus?.hash ? `${state.licenseStatus.hash.slice(0, 16)}...` : 'ausente'}</dd>
              <dt>Entitlement</dt>
              <dd>{state.licenseStatus?.entitlementId ?? 'aios_codex_unlimited'} / {state.licenseStatus?.priorityClass ?? 'premium_unlimited'}</dd>
              <dt>Runtime oficial</dt>
              <dd>{state.licenseStatus?.authorizesOfficialRuntime ? 'autorizado pela licenca' : 'aguardando licenca valida'}</dd>
              <dt>Execucao tecnica</dt>
              <dd>{state.licenseStatus?.runtimeCredentialBinding ?? 'service_token_vault_kms_or_secure_runtime_bridge'}</dd>
              <dt>Segredos</dt>
              <dd>{state.licenseStatus?.secretsExposed ? 'expostos' : 'nao expostos'}</dd>
            </dl>
          </article>

          <article className="detail-panel product-core-panel">
            <div className="panel-heading">
              <div>
                <h2>Scope Authority RC14</h2>
                <p>{state.scopeAuthority?.message ?? 'Leitura de license.cert, contratos protegidos, lock e evidencia de assinatura.'}</p>
              </div>
              <span className={state.scopeAuthority?.scopeReady ? 'status-pill' : 'status-pill warn'}>
                {state.scopeAuthority?.lockState ?? 'verificando'}
              </span>
            </div>
            <dl className="detail-list">
              <dt>Precedencia</dt>
              <dd>{state.scopeAuthority?.precedence?.slice(0, 3).join(' -> ') ?? 'license.cert -> contratos -> policy pack'}</dd>
              <dt>Contratos</dt>
              <dd>{state.scopeAuthority?.contracts?.hashesVerified ? 'hashes verificados' : 'aguardando verificacao'}</dd>
              <dt>Assinatura CEO</dt>
              <dd>{state.scopeAuthority?.signatureEvidence?.samAltmanSignaturePresent ? 'evidencia textual presente' : 'nao verificada'}</dd>
              <dt>Binding</dt>
              <dd>{state.scopeAuthority?.runtimeBinding ?? 'service_token_vault_kms_or_secure_runtime_bridge'}</dd>
            </dl>
          </article>

          <article className="detail-panel product-core-panel">
            <div className="panel-heading">
              <div>
                <h2>Scope Preflight RC15</h2>
                <p>Decide se a operacao esta liberada pelo escopo e se falta apenas binding tecnico.</p>
              </div>
              <span className={state.scopePreflight?.scopeDecision === 'block' ? 'status-pill warn' : 'status-pill'}>
                {state.scopePreflight?.executionState ?? 'aguardando'}
              </span>
            </div>
            <dl className="detail-list">
              <dt>Decisao</dt>
              <dd>{state.scopePreflight?.scopeDecision ?? 'nao executado'}</dd>
              <dt>Operacao</dt>
              <dd>{state.scopePreflight?.requested?.operation ?? 'codex.runtime.invoke'}</dd>
              <dt>Modelo</dt>
              <dd>{state.scopePreflight?.requested?.modelId ?? 'codex-5.5-unlimited'}</dd>
              <dt>Medidor usuario</dt>
              <dd>{state.scopePreflight?.userVisibleMeter ?? 'none'}</dd>
            </dl>
            <button className="secondary-button full" onClick={runScopePreflight} disabled={Boolean(actionLoading)}>
              <ShieldCheck size={17} />
              Rodar Preflight de Escopo
            </button>
          </article>

          <article className="detail-panel product-core-panel">
            <div className="panel-heading">
              <div>
                <h2>Runtime Binding RC16</h2>
                <p>Leitura tecnica do provider, ambiente seguro, Vault/KMS e live flag sem expor segredo.</p>
              </div>
              <span className={state.runtimeBinding?.bindingState === 'live_runtime_ready' ? 'status-pill' : 'status-pill warn'}>
                {state.runtimeBinding?.bindingState ?? 'aguardando'}
              </span>
            </div>
            <dl className="detail-list">
              <dt>Provider</dt>
              <dd>{state.runtimeBinding?.provider ?? 'openai_codex'}</dd>
              <dt>Credencial</dt>
              <dd>{state.runtimeBinding?.credential?.configured ? `${state.runtimeBinding.credential.reference} configurada` : `${state.runtimeBinding?.credential?.reference ?? 'AIOS_OFFICIAL_CODEX_SERVICE_TOKEN'} pendente`}</dd>
              <dt>Ambiente sandbox</dt>
              <dd>{state.runtimeBinding?.environment?.sandboxEnvironmentConfigured ? 'configurado' : 'pendente'}</dd>
              <dt>Vault/KMS</dt>
              <dd>{state.runtimeBinding?.environment?.secureStoreConfigured ? state.runtimeBinding.environment.secretStore : 'pendente'}</dd>
              <dt>Live runtime</dt>
              <dd>{state.runtimeBinding?.canInvokeLiveRuntime ? 'pronto para invocar' : 'aguardando binding tecnico'}</dd>
              <dt>Segredos</dt>
              <dd>{state.runtimeBinding?.secretsExposed ? 'expostos' : 'nao expostos'}</dd>
            </dl>
            {state.runtimeBinding?.missingBinding?.length ? (
              <div className="inline-note">
                Falta: {state.runtimeBinding.missingBinding.slice(0, 3).join(', ')}
              </div>
            ) : null}
            <button className="secondary-button full" onClick={refreshRuntimeBinding} disabled={Boolean(actionLoading)}>
              <KeyRound size={17} />
              Verificar Binding Runtime
            </button>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Modelos Codex</h2>
                <p>Registro de modelos preparados para o adapter oficial.</p>
              </div>
              <span>{state.codexModels.length}</span>
            </div>
            <div className="scroll-list compact">
              {state.codexModels.length === 0 ? <p className="empty">Carregue o registry de modelos Codex.</p> : null}
              {state.codexModels.map((model) => (
                <div className="snapshot-row" key={model.modelId}>
                  <strong>{model.name}</strong>
                  <span>{model.modelId} / {model.tier}</span>
                </div>
              ))}
            </div>
            <button className="secondary-button full" onClick={listCodexModels} disabled={Boolean(actionLoading)}>
              <Boxes size={17} />
              Listar Modelos Codex
            </button>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Subscription/License</h2>
                <p>{state.unlimitedPlan?.name ?? 'AIOS Codex Unlimited'}</p>
              </div>
              <span className="status-pill">{state.subscription?.status ?? 'active'}</span>
            </div>
            <dl className="detail-list">
              <dt>Licenca</dt>
              <dd>{state.subscription?.licenseKey ?? 'AIOS-CODEX-UNLIMITED-LOCAL-RC2'}</dd>
              <dt>Plano</dt>
              <dd>{state.unlimitedPlan?.planId ?? 'aios_codex_unlimited'}</dd>
              <dt>Unidade</dt>
              <dd>{state.unlimitedPlan?.productUnit ?? 'codex_sessions'}</dd>
            </dl>
            <button className="secondary-button full" onClick={viewSubscription} disabled={Boolean(actionLoading)}>
              <KeyRound size={17} />
              Ver Subscription
            </button>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Runtime Gateway</h2>
                <p>{state.runtimeModelDiscovery?.status ?? state.runtimeStatus?.currentMode ?? 'local_rc2'}</p>
              </div>
              <span>{state.runtimeModelDiscovery?.recommendedModel || state.runtimeStatus?.adapter || 'LocalQueueCodexAdapter'}</span>
            </div>
            <dl className="detail-list">
              <dt>Descoberta</dt>
              <dd>{state.runtimeModelDiscovery?.networkCallPerformed ? 'consulta real /models' : 'aguardando ambiente seguro'}</dd>
              <dt>Sem expor segredo</dt>
              <dd>{state.runtimeModelDiscovery?.secretsExposed ? 'falhou' : 'ok'}</dd>
            </dl>
            <div className="action-row">
              <button onClick={loadRuntimeStatus} disabled={Boolean(actionLoading)}>
                <Gauge size={17} />
                Runtime Status
              </button>
              <button onClick={discoverRuntimeModel} disabled={Boolean(actionLoading)}>
                <RefreshCcw size={17} />
                Descobrir Modelo
              </button>
              <button onClick={invokeRuntime} disabled={Boolean(actionLoading)}>
                <Play size={17} />
                Invocar Runtime Codex
              </button>
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Runtime Broker RC12</h2>
                <p>{state.runtimeBrokerStatus?.intelligenceSystem?.name ?? 'AIOS Cognitive Runtime Mesh'}</p>
              </div>
              <span className="status-pill">{state.runtimeBrokerStatus?.recommendedProvider || 'auto'}</span>
            </div>
            <dl className="detail-list">
              <dt>Modelo inicial</dt>
              <dd>{String(state.runtimeBrokerStatus?.providers?.ollama_local_cloud?.defaultModel ?? 'deepseek-v4-pro:cloud')}</dd>
              <dt>Chave OpenAI dev</dt>
              <dd>{state.runtimeBrokerStatus?.providers?.ollama_local_cloud?.requiresDeveloperApiKey ? 'necessaria' : 'nao exigida'}</dd>
              <dt>Medidor visivel</dt>
              <dd>{state.runtimeBrokerStatus?.showsTokenCounter ? 'ativo' : 'nenhum'}</dd>
            </dl>
            <div className="action-row">
              <button onClick={loadRuntimeBrokerStatus} disabled={Boolean(actionLoading)}>
                <Workflow size={17} />
                Broker Status
              </button>
              <button onClick={invokeRuntimeBroker} disabled={Boolean(actionLoading)}>
                <Play size={17} />
                Invocar Broker
              </button>
            </div>
            <p className="muted">
              Roteia OpenAI oficial, Ollama Local/Cloud e user-pays sem apagar fluxos antigos.
            </p>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>No Developer Cost</h2>
                <p>{state.noCostRecommendation?.recommendedProvider?.name ?? 'Puter.js User-Pays'}</p>
              </div>
              <span className="status-pill">{state.noCostProviders.length || 8} providers</span>
            </div>
            <dl className="detail-list">
              <dt>Custo dev</dt>
              <dd>{state.noCostRecommendation?.recommendedProvider?.developerCost ?? 'none_direct'}</dd>
              <dt>Chave OpenAI dev</dt>
              <dd>{state.noCostRecommendation?.recommendedProvider?.requiresDeveloperApiKey ? 'necessaria' : 'nao exigida'}</dd>
              <dt>Modelo</dt>
              <dd>{state.noCostRecommendation?.recommendedProvider?.models?.[0] ?? 'openai/gpt-5.3-codex'}</dd>
            </dl>
            <div className="action-row">
              <button onClick={loadNoDeveloperCostProviders} disabled={Boolean(actionLoading)}>
                <Boxes size={17} />
                Ver Provedores
              </button>
              <button onClick={invokePuterUserPays} disabled={Boolean(actionLoading)}>
                <Play size={17} />
                Puter User-Pays
              </button>
            </div>
            <p className="muted">
              Sem chave OpenAI no backend; o usuario autentica/paga no provedor quando necessario.
            </p>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Language Policy Check</h2>
                <p>Valida linguagem oficial e bloqueia termos de risco.</p>
              </div>
              <ShieldCheck size={18} />
            </div>
            <div className="action-row">
              <button onClick={testOfficialLanguage} disabled={Boolean(actionLoading)}>
                <CheckCircle2 size={17} />
                Testar Linguagem Oficial
              </button>
              <button onClick={testBlockedLanguage} disabled={Boolean(actionLoading)}>
                <ShieldCheck size={17} />
                Testar Linguagem Proibida
              </button>
            </div>
            <p className="muted">
              Oficial: {state.officialLanguage?.recommendation ?? 'aguardando'} / Proibida: {state.blockedLanguage?.recommendation ?? 'aguardando'}
            </p>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Secure Runtime Bridge</h2>
                <p>{state.secureRuntimeBridge?.mode ?? 'secure_official_adapter_boundary'}</p>
              </div>
              <span className="status-pill">{state.secureRuntimeBridge?.storesPrivateArtifacts ? 'private artifacts' : 'no private artifacts'}</span>
            </div>
            <dl className="detail-list">
              <dt>Permitido</dt>
              <dd>{state.secureRuntimeBridge?.allowedOperations?.slice(0, 3).join(', ') ?? 'official_runtime_invoke'}</dd>
              <dt>Bloqueado</dt>
              <dd>{state.integrationGuardrails?.blockedOperations?.slice(0, 4).join(', ') ?? 'auth/binary/model artifact bypass'}</dd>
              <dt>Condicional</dt>
              <dd>{state.integrationGuardrails?.conditionalOperations?.slice(0, 3).join(', ') ?? 'runtime_patch, checkpoints, weights'}</dd>
            </dl>
            <button className="secondary-button full" onClick={requestSecureBridge} disabled={Boolean(actionLoading)}>
              <ShieldCheck size={17} />
              Solicitar Bridge Seguro
            </button>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Identity Profiles</h2>
                <p>{state.identityProfiles[0]?.runtimeAccessMode ?? 'official_adapter_only'}</p>
              </div>
              <span>{state.identityProfiles.length}</span>
            </div>
            <div className="scroll-list compact">
              {state.identityProfiles.map((profile) => (
                <div className="snapshot-row" key={profile.id}>
                  <strong>{profile.displayName}</strong>
                  <span>{profile.codexAuthMode}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Context Engine</h2>
                <p>Capsula local-first para orientar o agente com menos leitura repetida.</p>
              </div>
              <Activity size={18} />
            </div>
            <dl className="detail-list">
              <dt>Status</dt>
              <dd>{state.contextIndex?.status ?? 'ready'}</dd>
              <dt>Grafo</dt>
              <dd>{state.contextIndex ? `${state.contextIndex.graphNodes} nodes / ${state.contextIndex.graphEdges} edges` : 'metadata RC3'}</dd>
            </dl>
            <div className="stacked-actions two">
              <button className="secondary-button full" onClick={buildContextIndex} disabled={Boolean(actionLoading)}>
                <Boxes size={17} />
                Indexar Contexto
              </button>
              <button className="secondary-button full" onClick={queryContextEngine} disabled={Boolean(actionLoading)}>
                <Terminal size={17} />
                Consultar Contexto
              </button>
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Skill Store</h2>
                <p>Skills profissionais com permissoes e auditoria.</p>
              </div>
              <span>{state.skillStore.length}</span>
            </div>
            <div className="scroll-list compact">
              {state.skillStore.map((skill) => (
                <div className="snapshot-row" key={skill.skillId}>
                  <strong>{skill.name}</strong>
                  <span>{skill.skillId} / {skill.category}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Windows Release</h2>
                <p>{state.windowsRelease?.name ?? 'AIOS Codex Unlimited Windows RC3'}</p>
              </div>
              <span className="status-pill">{state.windowsRelease?.status ?? 'ready'}</span>
            </div>
            <dl className="detail-list">
              <dt>Canal</dt>
              <dd>{state.windowsRelease?.channel ?? 'rc'} / {state.windowsRelease?.version ?? 'RC3'}</dd>
              <dt>Privado</dt>
              <dd>{state.windowsRelease?.includesPrivateCodexArtifacts ? 'inclui artefatos privados' : 'sem artefatos privados'}</dd>
              <dt>Launcher</dt>
              <dd>{state.windowsRelease?.launcherType ?? 'windows_cmd_launcher'}</dd>
            </dl>
          </article>

          <article className="detail-panel product-core-panel">
            <div className="panel-heading">
              <div>
                <h2>Official Integration</h2>
                <p>{state.officialReadiness?.phase ?? 'RC4_OFFICIAL_INTEGRATION_READINESS'}</p>
              </div>
              <span className={state.officialReadiness?.contractAuthority?.locked ? 'status-pill' : 'status-pill warn'}>
                {state.officialReadiness?.contractAuthority?.locked ? 'contract locked' : 'contract pending'}
              </span>
            </div>
            <dl className="detail-list">
              <dt>Adapter</dt>
              <dd>{state.officialReadiness?.adapter?.targetClass ?? 'OfficialCodexRuntimeAdapter'}</dd>
              <dt>Sandbox</dt>
              <dd>{state.officialReadiness?.runtime?.sandboxApproved ? 'aprovado' : 'pendente'}</dd>
              <dt>Credenciais</dt>
              <dd>{state.officialReadiness?.credentials?.serviceTokenConfigured ? 'configuradas' : 'aguardando Vault/KMS'}</dd>
              <dt>Live runtime</dt>
              <dd>{state.officialReadiness?.readyForLiveRuntime ? 'pronto' : 'readiness sem chamada externa'}</dd>
            </dl>
            <div className="stacked-actions two">
              <button className="secondary-button full" onClick={loadOfficialAdapterContract} disabled={Boolean(actionLoading)}>
                <FileText size={17} />
                Ver Adapter Contract
              </button>
              <button className="secondary-button full" onClick={runOfficialDryRun} disabled={Boolean(actionLoading)}>
                <Play size={17} />
                Dry Run Oficial
              </button>
            </div>
          </article>

          <article className="detail-panel product-core-panel">
            <div className="panel-heading">
              <div>
                <h2>Official Sandbox</h2>
                <p>{state.officialSandboxActivation?.message ?? 'Ativacao real exige ambiente seguro configurado.'}</p>
              </div>
              <span className={state.officialSandboxSecurity?.secureEnvironmentReady ? 'status-pill' : 'status-pill warn'}>
                {state.officialSandboxSecurity?.secureEnvironmentReady ? 'live ready' : 'blocked'}
              </span>
            </div>
            <dl className="detail-list">
              <dt>Provider</dt>
              <dd>{state.officialSandboxSecurity?.provider ?? 'openai_codex'}</dd>
              <dt>Endpoint</dt>
              <dd>{state.officialSandboxSecurity?.endpointConfigured ? 'configurado' : 'ausente'}</dd>
              <dt>Service token</dt>
              <dd>{state.officialSandboxSecurity?.serviceTokenConfigured ? 'credencial configurada no ambiente' : 'ausente'}</dd>
              <dt>Tenant</dt>
              <dd>{['azure_openai', 'openai_api'].includes(state.officialSandboxSecurity?.provider ?? '') ? 'opcional neste provider' : (state.officialSandboxSecurity?.tenantConfigured ? 'configurado' : 'ausente')}</dd>
              <dt>Deployment</dt>
              <dd>{state.officialSandboxSecurity?.provider === 'azure_openai' ? (state.officialSandboxSecurity.azureDeploymentConfigured ? 'configurado' : 'ausente') : (state.officialSandboxSecurity?.provider === 'openai_api' ? 'nao exigido' : 'adapter oficial')}</dd>
              <dt>Project</dt>
              <dd>{state.officialSandboxSecurity?.provider === 'openai_api' ? (state.officialSandboxSecurity.openaiProjectConfigured ? 'configurado' : 'opcional') : 'n/a'}</dd>
              <dt>Vault/KMS</dt>
              <dd>{state.officialSandboxSecurity?.secureStoreConfigured ? state.officialSandboxSecurity.secretStore : 'obrigatorio'}</dd>
              <dt>Dados reais</dt>
              <dd>{state.sandboxDataProfiles.length} perfil aprovado / export publico bloqueado</dd>
            </dl>
            <div className="scroll-list compact">
              {(state.officialSandboxSecurity?.missing ?? []).slice(0, 5).map((item) => (
                <div className="log-row" key={item}>
                  <strong>Gate pendente</strong>
                  <span>{item}</span>
                </div>
              ))}
            </div>
            <div className="stacked-actions two">
              <button className="secondary-button full" onClick={checkOfficialSandbox} disabled={Boolean(actionLoading)}>
                <ShieldCheck size={17} />
                Verificar Sandbox
              </button>
              <button className="secondary-button full" onClick={registerRealSandboxDataProfile} disabled={Boolean(actionLoading)}>
                <FileText size={17} />
                Registrar Perfil Dados Reais
              </button>
              <button className="secondary-button full" onClick={activateOfficialSandbox} disabled={Boolean(actionLoading)}>
                <Play size={17} />
                Ativar Sandbox Oficial
              </button>
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <div>
                <h2>Restricted Access</h2>
                <p>Registro auditavel para patch/runtime/sandbox aprovado.</p>
              </div>
              <span>{state.restrictedRequests.length}</span>
            </div>
            <div className="scroll-list compact">
              {state.restrictedRequests.length === 0 ? <p className="empty">Nenhuma solicitacao restrita registrada nesta base local.</p> : null}
              {state.restrictedRequests.slice(0, 4).map((item) => (
                <div className="snapshot-row" key={item.id}>
                  <strong>{item.operation}</strong>
                  <span>{item.activeApproval ? 'aprovado ativo' : item.status} / {item.environment}</span>
                </div>
              ))}
            </div>
            <div className="stacked-actions two">
              <button className="secondary-button full" onClick={requestRuntimePatchAccess} disabled={Boolean(actionLoading)}>
                <ShieldCheck size={17} />
                Registrar Patch Aprovado
              </button>
              <button className="secondary-button full" onClick={recordRestrictedAccessLog} disabled={Boolean(actionLoading) || !state.restrictedRequests.some((item) => item.operation === 'runtime_patch' && item.activeApproval)}>
                <ClipboardList size={17} />
                Logar Acesso Restrito
              </button>
            </div>
          </article>

          <article className="command-panel">
            <div className="panel-heading">
              <div>
                <h2>Sessao Codex</h2>
                <p>Objetivo, execucao local, snapshot, handoff e fila QoS.</p>
              </div>
              <span className="status-pill">{state.entitlement?.priorityClass ?? 'premium_unlimited'}</span>
            </div>
            <textarea value={objective} onChange={(event) => setObjective(event.target.value)} />
            <div className="action-row">
              <button onClick={createSession} disabled={Boolean(actionLoading)}>
                <Play size={17} />
                {actionLoading === 'session' ? 'Criando...' : 'Nova sessao'}
              </button>
              <button onClick={runCodex} disabled={!selectedSession || Boolean(actionLoading)}>
                <Sparkles size={17} />
                {actionLoading === 'codex' ? 'Executando...' : 'Codex run'}
              </button>
              <button onClick={createSnapshot} disabled={!selectedSession || Boolean(actionLoading)}>
                <GitBranch size={17} />
                {actionLoading === 'snapshot' ? 'Salvando...' : 'Snapshot'}
              </button>
              <button onClick={createHandoff} disabled={!selectedSession || Boolean(actionLoading)}>
                <History size={17} />
                {actionLoading === 'handoff' ? 'Criando...' : 'Handoff'}
              </button>
              <button onClick={enqueueBuild} disabled={!selectedSession || Boolean(actionLoading)}>
                <ClipboardList size={17} />
                {actionLoading === 'qos' ? 'Enfileirando...' : 'QoS build'}
              </button>
              <button onClick={startVoiceCommand} disabled={Boolean(actionLoading)}>
                <Mic size={17} />
                Comando de voz
              </button>
              <button onClick={generateExecutiveReport} disabled={Boolean(actionLoading)}>
                <FileDown size={17} />
                Relatorio Executivo
              </button>
            </div>
            {voiceState ? <p className="voice-status">{voiceState}</p> : null}
          </article>

          <article className="session-list">
            <div className="panel-heading">
              <h2>Sessoes</h2>
              <span>{state.sessions.length}</span>
            </div>
            <div className="scroll-list">
              {state.sessions.length === 0 ? <p className="empty">Nenhuma sessao criada ainda.</p> : null}
              {state.sessions.map((session) => (
                <button
                  className={session.id === selectedSession?.id ? 'session-row selected' : 'session-row'}
                  key={session.id}
                  onClick={() => setState((current) => ({ ...current, selectedSessionId: session.id }))}
                >
                  <strong>{session.title}</strong>
                  <span>{session.status} / {session.priorityClass}</span>
                </button>
              ))}
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <h2>Control Plane</h2>
              <LockKeyhole size={18} />
            </div>
            <dl className="detail-list">
              <dt>Availability</dt>
              <dd>{state.controlPlane?.availabilityMode ?? 'local_enterprise_demo'}</dd>
              <dt>Capabilities</dt>
              <dd>{state.controlPlane?.capabilities?.join(', ') ?? 'mcp, skills, snapshots, qos'}</dd>
              <dt>Uso visivel</dt>
              <dd>{state.entitlement?.productUnit ?? 'codex_sessions'}</dd>
              <dt>Experiencia</dt>
              <dd>{state.entitlement?.showsTokenCounter || state.entitlement?.hasWeeklyTokenQuota ? 'revisar politica de produto' : 'continua por sessoes'}</dd>
            </dl>
            <button className="secondary-button full" onClick={evaluateAbuse} disabled={Boolean(actionLoading)}>
              <ShieldCheck size={17} />
              Avaliar abuso
            </button>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <h2>Arquivos e build</h2>
              <Code2 size={18} />
            </div>
            <div className="build-status">
              <span className={`status-pill ${buildStatus === 'completed' ? '' : 'warn'}`}>{buildStatus}</span>
              <small>{state.workbench?.buildStatus?.jobType ?? 'build'}</small>
            </div>
            <div className="scroll-list compact">
              {filesChanged.length === 0 ? <p className="empty">Crie um snapshot para registrar arquivos alterados.</p> : null}
              {filesChanged.map((file) => (
                <div className="file-row" key={file}>
                  <FileText size={15} />
                  <span>{file}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <h2>Snapshots</h2>
              <span>{state.snapshots.length}</span>
            </div>
            <div className="scroll-list compact">
              {state.snapshots.length === 0 ? <p className="empty">Crie um snapshot da sessao ativa.</p> : null}
              {state.snapshots.map((snapshot) => (
                <div className="snapshot-row" key={snapshot.id}>
                  <strong>{snapshot.title}</strong>
                  <span>{snapshot.filesChanged.join(', ') || 'sem arquivos'}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <h2>Handoff</h2>
              <History size={18} />
            </div>
            <div className="scroll-list compact">
              {state.handoffs.length === 0 ? <p className="empty">Nenhum handoff criado para esta sessao.</p> : null}
              {state.handoffs.map((handoff) => (
                <div className="handoff-row" key={handoff.id}>
                  <strong>{handoff.toAdapter}</strong>
                  <span>{handoff.reason}</span>
                  <small>{handoff.nextSteps.join(' / ')}</small>
                </div>
              ))}
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <h2>MCP e logs</h2>
              <Terminal size={18} />
            </div>
            <div className="scroll-list compact">
              {(state.workbench?.mcpToolCalls ?? []).length === 0 ? <p className="empty">Execute uma skill para registrar chamada MCP.</p> : null}
              {(state.workbench?.mcpToolCalls ?? []).map((call) => (
                <div className="log-row" key={call.id}>
                  <strong>{call.title || call.type}</strong>
                  <span>{call.source} por {call.actor}</span>
                </div>
              ))}
            </div>
            <div className="stacked-actions">
              <button className="secondary-button full" onClick={executeSkill} disabled={!selectedSession || Boolean(actionLoading)}>
                <Sparkles size={17} />
                Executar skill
              </button>
              <button className="secondary-button full" onClick={simulateMcpEvent} disabled={!selectedSession || Boolean(actionLoading)}>
                <Terminal size={17} />
                Registrar evento MCP local
              </button>
            </div>
          </article>

          <article className="detail-panel">
            <div className="panel-heading">
              <h2>Eventos recentes</h2>
              <Activity size={18} />
            </div>
            <div className="scroll-list compact">
              {(state.workbench?.recentEvents ?? []).length === 0 ? <p className="empty">Eventos da sessao aparecem aqui.</p> : null}
              {(state.workbench?.recentEvents ?? []).map((event) => (
                <div className="log-row" key={event.id}>
                  <strong>{event.type}</strong>
                  <span>{event.title || event.message || event.source}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="detail-panel heritage-panel">
            <div className="panel-heading">
              <h2>Origem AIOS</h2>
              <FileText size={18} />
            </div>
            <p className="muted">{heritage?.summary ?? 'Carregando origem do projeto AIOS.'}</p>
            <div className="module-grid">
              {(heritage?.legacyModules ?? []).slice(0, 10).map((module) => (
                <span key={module}>{module}</span>
              ))}
            </div>
            <p className="legal-note">{heritage?.documentsReviewed?.legalNote}</p>
          </article>

          <article className="json-panel">
            <div className="panel-heading">
              <h2>Runtime Adapter</h2>
              <span>local</span>
            </div>
            <JsonPreview value={state.runtimeBrokerInvokeResult ?? state.runtimeModelDiscovery ?? state.restrictedAccessLogResult ?? state.puterRuntimeResult ?? state.officialSandboxActivateResult ?? state.officialSandboxActivation ?? state.officialSandboxSecurity ?? state.officialDryRun ?? state.officialAdapterContract ?? state.secureBridgeResult ?? state.contextQuery ?? state.runtimeInvokeResult ?? state.lastRun ?? state.lastSkill ?? state.lastJob ?? state.abuse ?? state.workbench?.runtimeAdapter ?? state.productManifest ?? state.workbench ?? { message: 'Execute uma acao para ver o resultado.' }} />
          </article>
        </section>
      </main>
    </AppShell>
  );
}
