import { createContext, ReactNode, useContext, useMemo, useState } from 'react';
import type {
  ApprovalGatePolicy,
  ApprovalGateRequest,
  CodexModelInfo,
  CodexPlanInfo,
  CodexDelegatedAuthStatus,
  CodexProductManifest,
  CodexSession,
  ControlPlaneStatus,
  ContextIndexInfo,
  Entitlement,
  FinalReadiness,
  Handoff,
  IdentityProfile,
  IntegrationGuardrails,
  LanguageEvaluation,
  LicenseStatus,
  LegacyAiosSummary,
  QosJob,
  OfficialIntegrationReadiness,
  OfficialSandboxActivation,
  OfficialSandboxSecurityCheck,
  NoDeveloperCostProviderCatalog,
  NoDeveloperCostRecommendation,
  RestrictedAccessRequestInfo,
  RuntimeModelDiscovery,
  RuntimeBrokerExplanation,
  RuntimeBrokerProvider,
  RuntimeBrokerStatus,
  RuntimeBindingStatus,
  RuntimeStatus,
  SandboxDataProfile,
  SecureRuntimeBridge,
  SessionEvent,
  ScopeAuthority,
  ScopePreflight,
  SkillStoreItem,
  Snapshot,
  SubscriptionInfo,
  WindowsReleaseManifest,
  WorkbenchState,
} from './types';

type ApiContextValue = {
  token: string;
  isAuthenticated: boolean;
  apiError: string;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  getEntitlement: () => Promise<Entitlement>;
  getControlPlane: () => Promise<ControlPlaneStatus>;
  getHeritageSummary: () => Promise<LegacyAiosSummary>;
  licenseStatus: () => Promise<LicenseStatus>;
  scopeAuthority: () => Promise<ScopeAuthority>;
  scopePreflight: (input?: { operation?: string; environment?: string; modelId?: string; requiresLiveRuntime?: boolean; requiresRestrictedArtifacts?: boolean; reason?: string }) => Promise<ScopePreflight>;
  runtimeBindingStatus: () => Promise<RuntimeBindingStatus>;
  productManifest: () => Promise<CodexProductManifest>;
  codexModels: () => Promise<CodexModelInfo[]>;
  unlimitedPlan: () => Promise<CodexPlanInfo>;
  subscriptionMe: () => Promise<SubscriptionInfo>;
  runtimeStatus: () => Promise<RuntimeStatus>;
  runtimeModelDiscovery: () => Promise<RuntimeModelDiscovery>;
  runtimeInvoke: (sessionId: string, modelId: string, objective: string) => Promise<Record<string, unknown>>;
  runtimeBrokerProviders: () => Promise<{ phase: string; productUnit: string; providers: RuntimeBrokerProvider[] }>;
  runtimeBrokerStatus: () => Promise<RuntimeBrokerStatus>;
  runtimeBrokerExplain: (provider?: string) => Promise<RuntimeBrokerExplanation>;
  runtimeBrokerInvoke: (sessionId: string, objective: string, provider?: string) => Promise<Record<string, unknown>>;
  codexDelegatedAuthStatus: () => Promise<CodexDelegatedAuthStatus>;
  approvalGatePolicy: () => Promise<ApprovalGatePolicy>;
  createApprovalGateRequest: (input: { sessionId?: string; operation: string; target?: string; reason: string; preview?: Record<string, unknown> }) => Promise<ApprovalGateRequest>;
  listApprovalGateRequests: () => Promise<ApprovalGateRequest[]>;
  decideApprovalGateRequest: (requestId: string, decision: 'approved' | 'rejected' | 'cancelled', reason: string) => Promise<ApprovalGateRequest>;
  noDeveloperCostProviders: () => Promise<NoDeveloperCostProviderCatalog>;
  noDeveloperCostRecommendation: () => Promise<NoDeveloperCostRecommendation>;
  languageEvaluate: (text: string) => Promise<LanguageEvaluation>;
  integrationGuardrails: () => Promise<IntegrationGuardrails>;
  identityProfiles: () => Promise<IdentityProfile[]>;
  secureRuntimeBridge: () => Promise<SecureRuntimeBridge>;
  secureRuntimeRequest: (sessionId: string, operation: string, objective: string, payload?: Record<string, unknown>) => Promise<Record<string, unknown>>;
  createContextIndex: (input: { sessionId?: string; name?: string; source?: string; fileCount?: number; graphNodes?: number; graphEdges?: number }) => Promise<ContextIndexInfo>;
  queryContext: (query: string, sessionId?: string) => Promise<Record<string, unknown>>;
  skillStore: () => Promise<SkillStoreItem[]>;
  windowsReleaseManifest: () => Promise<WindowsReleaseManifest>;
  finalReadiness: () => Promise<FinalReadiness>;
  officialIntegrationReadiness: () => Promise<OfficialIntegrationReadiness>;
  officialAdapterContract: () => Promise<Record<string, unknown>>;
  officialAdapterDryRun: (modelId: string, objective: string) => Promise<Record<string, unknown>>;
  officialSandboxSecurityCheck: () => Promise<OfficialSandboxSecurityCheck>;
  officialSandboxActivation: () => Promise<OfficialSandboxActivation>;
  activateOfficialSandbox: () => Promise<Record<string, unknown>>;
  createSandboxDataProfile: (input: {
    profileId: string;
    name: string;
    dataClassification: string;
    approvalReference: string;
    redactionRequired: boolean;
    publicExportAllowed: boolean;
    retentionDays: number;
  }) => Promise<SandboxDataProfile>;
  listSandboxDataProfiles: () => Promise<SandboxDataProfile[]>;
  createRestrictedAccessRequest: (input: {
    operation: string;
    environment: string;
    justification: string;
    artifactName?: string;
    artifactHash?: string;
    pathScope?: string;
    expiresInDays?: number;
  }) => Promise<RestrictedAccessRequestInfo>;
  listRestrictedAccessRequests: () => Promise<RestrictedAccessRequestInfo[]>;
  recordRestrictedAccessLog: (requestId: string, input: { action: string; artifactPath?: string; artifactHash?: string; justification?: string; result?: string }) => Promise<Record<string, unknown>>;
  listSessions: () => Promise<CodexSession[]>;
  createSession: (title: string, objective: string) => Promise<CodexSession>;
  createSnapshot: (sessionId: string, title: string, filesChanged: string[], notes: string) => Promise<Snapshot>;
  createHandoff: (sessionId: string, reason: string, context: string, nextSteps: string[]) => Promise<Handoff>;
  listHandoffs: (sessionId: string) => Promise<Handoff[]>;
  createSessionEvent: (sessionId: string, input: { type: string; source?: string; title?: string; message?: string; payload?: Record<string, unknown> }) => Promise<SessionEvent>;
  addFilesChanged: (sessionId: string, filesChanged: string[], source?: string) => Promise<{ sessionId: string; filesChanged: string[]; eventId: string }>;
  getSessionWorkbench: (sessionId: string) => Promise<WorkbenchState>;
  enqueueQos: (jobType: string, payload: Record<string, unknown>) => Promise<QosJob>;
  runCodex: (objective: string, sessionId?: string) => Promise<Record<string, unknown>>;
  executeSkill: (skillName: string, input: Record<string, unknown>) => Promise<Record<string, unknown>>;
  evaluateAbuse: (input: Record<string, unknown>) => Promise<Record<string, unknown>>;
};

const ApiContext = createContext<ApiContextValue | null>(null);
const API_URL = import.meta.env.VITE_AIOS_API_URL ?? 'http://localhost:8000';

async function parseResponse(response: Response) {
  const contentType = response.headers.get('content-type') ?? '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof payload === 'string' ? payload : payload.detail ?? 'API request failed';
    throw new Error(message);
  }
  return payload;
}

export function ApiProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem('aios.token') ?? '');
  const [apiError, setApiError] = useState('');

  const request = async (path: string, options: RequestInit = {}) => {
    setApiError('');
    try {
      const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(options.headers ?? {}),
        },
      });
      return await parseResponse(response);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown API error';
      setApiError(message);
      throw error;
    }
  };

  const value = useMemo<ApiContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      apiError,
      async login(email, password) {
        const response = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        const payload = await parseResponse(response);
        localStorage.setItem('aios.token', payload.accessToken);
        setToken(payload.accessToken);
      },
      logout() {
        localStorage.removeItem('aios.token');
        setToken('');
      },
      getEntitlement: () => request('/entitlement/me'),
      getControlPlane: () => request('/control-plane/status'),
      getHeritageSummary: () => request('/aios/heritage/summary'),
      licenseStatus: () => request('/license/status'),
      scopeAuthority: () => request('/scope/authority'),
      scopePreflight: (input = {}) =>
        request('/scope/preflight', { method: 'POST', body: JSON.stringify({ operation: 'codex.runtime.invoke', environment: 'sandbox', modelId: 'codex-5.5-unlimited', requiresLiveRuntime: true, requiresRestrictedArtifacts: false, reason: 'frontend RC15 scope preflight', ...input }) }),
      runtimeBindingStatus: () => request('/runtime/binding/status'),
      productManifest: () => request('/codex/product/manifest'),
      codexModels: () => request('/codex/models'),
      unlimitedPlan: () => request('/codex/plans/unlimited'),
      subscriptionMe: () => request('/subscriptions/me'),
      runtimeStatus: () => request('/codex/runtime/status'),
      runtimeModelDiscovery: () => request('/codex/runtime/model-discovery'),
      runtimeInvoke: (sessionId, modelId, objective) =>
        request('/codex/runtime/invoke', { method: 'POST', body: JSON.stringify({ session_id: sessionId, model_id: modelId, objective }) }),
      runtimeBrokerProviders: () => request('/runtime/broker/providers'),
      runtimeBrokerStatus: () => request('/runtime/broker/status'),
      runtimeBrokerExplain: (provider = 'auto') => request(`/runtime/broker/explain?provider=${encodeURIComponent(provider)}`),
      runtimeBrokerInvoke: (sessionId, objective, provider = 'auto') =>
        request('/runtime/broker/invoke', { method: 'POST', body: JSON.stringify({ sessionId, objective, provider, intelligenceMode: 'aios_cognitive_runtime_mesh' }) }),
      codexDelegatedAuthStatus: () => request('/codex/delegated-auth/status'),
      approvalGatePolicy: () => request('/approval-gate/policy'),
      createApprovalGateRequest: (input) =>
        request('/approval-gate/requests', { method: 'POST', body: JSON.stringify(input) }),
      listApprovalGateRequests: () => request('/approval-gate/requests'),
      decideApprovalGateRequest: (requestId, decision, reason) =>
        request(`/approval-gate/requests/${requestId}/decision`, { method: 'PATCH', body: JSON.stringify({ decision, reason }) }),
      noDeveloperCostProviders: () => request('/runtime/no-developer-cost/providers'),
      noDeveloperCostRecommendation: () => request('/runtime/no-developer-cost/recommendation'),
      languageEvaluate: (text) =>
        request('/policy/language/evaluate', { method: 'POST', body: JSON.stringify({ text }) }),
      integrationGuardrails: () => request('/policy/integration/guardrails'),
      identityProfiles: () => request('/identity/profiles'),
      secureRuntimeBridge: () => request('/codex/secure-runtime/bridge'),
      secureRuntimeRequest: (sessionId, operation, objective, payload = {}) =>
        request('/codex/secure-runtime/request', { method: 'POST', body: JSON.stringify({ sessionId, operation, objective, payload }) }),
      createContextIndex: (input) =>
        request('/context/index', { method: 'POST', body: JSON.stringify(input) }),
      queryContext: (query, sessionId) =>
        request('/context/query', { method: 'POST', body: JSON.stringify({ query, sessionId }) }),
      skillStore: () => request('/skill-store'),
      windowsReleaseManifest: () => request('/release/windows/manifest'),
      finalReadiness: () => request('/release/final-readiness'),
      officialIntegrationReadiness: () => request('/official-integration/readiness'),
      officialAdapterContract: () => request('/official-integration/adapter/contract'),
      officialAdapterDryRun: (modelId, objective) =>
        request('/official-integration/adapter/dry-run', { method: 'POST', body: JSON.stringify({ modelId, objective }) }),
      officialSandboxSecurityCheck: () => request('/official-sandbox/security-check'),
      officialSandboxActivation: () => request('/official-sandbox/activation'),
      activateOfficialSandbox: () => request('/official-sandbox/activate', { method: 'POST' }),
      createSandboxDataProfile: (input) =>
        request('/official-sandbox/data-profiles', { method: 'POST', body: JSON.stringify(input) }),
      listSandboxDataProfiles: () => request('/official-sandbox/data-profiles'),
      createRestrictedAccessRequest: (input) =>
        request('/restricted-access/requests', { method: 'POST', body: JSON.stringify(input) }),
      listRestrictedAccessRequests: () => request('/restricted-access/requests'),
      recordRestrictedAccessLog: (requestId, input) =>
        request(`/restricted-access/requests/${requestId}/access-log`, { method: 'POST', body: JSON.stringify(input) }),
      listSessions: () => request('/sessions'),
      createSession: (title, objective) =>
        request('/sessions', { method: 'POST', body: JSON.stringify({ title, objective }) }),
      createSnapshot: (sessionId, title, filesChanged, notes) =>
        request('/snapshots', { method: 'POST', body: JSON.stringify({ sessionId, title, filesChanged, notes }) }),
      createHandoff: (sessionId, reason, context, nextSteps) =>
        request('/handoffs', { method: 'POST', body: JSON.stringify({ sessionId, reason, context, nextSteps }) }),
      listHandoffs: (sessionId) => request(`/sessions/${sessionId}/handoffs`),
      createSessionEvent: (sessionId, input) =>
        request(`/sessions/${sessionId}/events`, { method: 'POST', body: JSON.stringify(input) }),
      addFilesChanged: (sessionId, filesChanged, source = 'workbench') =>
        request(`/sessions/${sessionId}/files-changed`, { method: 'POST', body: JSON.stringify({ filesChanged, source }) }),
      getSessionWorkbench: (sessionId) => request(`/sessions/${sessionId}/workbench`),
      enqueueQos: (jobType, payload) =>
        request('/qos/enqueue', { method: 'POST', body: JSON.stringify({ jobType, payload }) }),
      runCodex: (objective, sessionId) =>
        request('/codex/run', { method: 'POST', body: JSON.stringify({ objective, sessionId }) }),
      executeSkill: (skillName, input) =>
        request('/codex/skill/execute', { method: 'POST', body: JSON.stringify({ skillName, input }) }),
      evaluateAbuse: (input) =>
        request('/abuse/evaluate', { method: 'POST', body: JSON.stringify(input) }),
    }),
    [apiError, token],
  );

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

export function useApi() {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used inside ApiProvider');
  }
  return context;
}
