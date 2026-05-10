export type Entitlement = {
  plan: string;
  status: string;
  priorityClass: string;
  productUnit: string;
  accessModel: string;
  hasTokenLimit: boolean;
  showsTokenCounter: boolean;
  usesTokenBalance: boolean;
  hasWeeklyTokenQuota: boolean;
};

export type ControlPlaneStatus = {
  plan: string;
  status: string;
  priorityClass: string;
  productUnit: string;
  availabilityMode: string;
  queueDepth: number;
  runningJobs: number;
  activeSessions: number;
  capabilities: string[];
};

export type CodexSession = {
  id: string;
  title: string;
  objective: string;
  status: string;
  priorityClass: string;
  createdAt: string;
};

export type Snapshot = {
  id: string;
  sessionId?: string;
  title: string;
  filesChanged: string[];
  notes?: string;
  createdAt?: string;
};

export type QosJob = {
  id: string;
  status: string;
  priorityClass: string;
  queueDepth?: number;
  jobType?: string;
  payload?: Record<string, unknown>;
  result?: Record<string, unknown>;
  createdAt?: string;
};

export type Handoff = {
  id: string;
  sessionId: string;
  fromAdapter: string;
  toAdapter: string;
  reason: string;
  context: string;
  nextSteps: string[];
  createdAt: string;
};

export type McpToolCall = {
  id: string;
  toolName: string;
  actor: string;
  status: string;
  details: Record<string, unknown>;
  createdAt: string;
};

export type SessionEvent = {
  id: string;
  sessionId: string;
  type: string;
  source: string;
  title: string;
  message: string;
  payload: Record<string, unknown>;
  actor: string;
  createdAt: string;
};

export type LegacyAiosSummary = {
  sourceProjectPath: string;
  sourceStatus: string;
  currentTargetPath: string;
  summary: string;
  legacyModules: string[];
  migrationMap: Record<string, string>;
  documentsReviewed: {
    recapPath: string;
    messageFiles: number;
    legalNote: string;
  };
};

export type WorkbenchState = {
  session: CodexSession;
  entitlement?: Entitlement;
  snapshots: Snapshot[];
  handoffs: Handoff[];
  filesChanged: string[];
  buildStatus: Partial<QosJob> & { status: string; jobType?: string };
  recentJobs: QosJob[];
  mcpToolCalls: SessionEvent[];
  recentEvents: SessionEvent[];
  runtimeAdapter: Record<string, unknown>;
  legacyLineage: LegacyAiosSummary;
  heritage: LegacyAiosSummary;
};

export type CodexProductManifest = {
  product: string;
  headline: string;
  productUnit: string;
  experience: {
    hasTokenLimit: boolean;
    showsTokenCounter: boolean;
    usesTokenBalance: boolean;
    hasWeeklyTokenQuota: boolean;
  };
  systems: string[];
};

export type CodexModelInfo = {
  id: string;
  modelId: string;
  name: string;
  tier: string;
  purpose: string;
  runtimeProvider: string;
  availableInUnlimited: boolean;
  defaultFor: string[];
  status: string;
};

export type CodexPlanInfo = {
  id: string;
  planId: string;
  name: string;
  description: string;
  priceLabel: string;
  productUnit: string;
  hasTokenLimit: boolean;
  showsTokenCounter: boolean;
  usesTokenBalance: boolean;
  hasWeeklyTokenQuota: boolean;
  priorityClass: string;
  status: string;
  features: string[];
};

export type NoDeveloperCostProvider = {
  providerId: string;
  name: string;
  category: string;
  developerCost: string;
  requiresDeveloperApiKey: boolean;
  requiresUserAccount: boolean;
  runtimeSurface: string;
  status: string;
  recommendedUse: string;
  models: string[];
  limits: string;
  secretHandling: string;
  officialCodexReplacement: boolean;
};

export type NoDeveloperCostProviderCatalog = {
  strategy: string;
  productUnit: string;
  primaryProvider: string;
  warning: string;
  providers: NoDeveloperCostProvider[];
};

export type NoDeveloperCostRecommendation = {
  recommendedProvider: NoDeveloperCostProvider;
  reason: string;
  implementation: {
    frontend: string;
    backend: string;
    security: string;
  };
  fallbackOrder: string[];
};

export type SubscriptionInfo = {
  id: string;
  userId: string;
  planId: string;
  status: string;
  licenseKey: string;
  activatedAt?: string;
  createdAt?: string;
};

export type RuntimeStatus = {
  adapter: string;
  officialAdapterReady: boolean;
  currentMode: string;
  supportedModels: CodexModelInfo[];
  adapterInfo?: Record<string, unknown>;
};

export type RuntimeModelDiscovery = {
  phase: string;
  provider: string;
  status: string;
  baseUrl: string;
  configuredModel: string;
  candidateModels: string[];
  availableCandidates: string[];
  recommendedModel: string;
  selectedModelCommand: string;
  networkCallPerformed: boolean;
  secretsExposed: boolean;
  missing: string[];
  message: string;
  modelCount?: number;
  security?: Record<string, unknown>;
  error?: unknown;
};

export type RuntimeBrokerProvider = {
  providerId: string;
  name: string;
  category: string;
  defaultModel: string;
  requiresDeveloperApiKey: boolean;
  requiresUserAccount: boolean;
  runtimeSurface: string;
  status: string;
  qualityRole: string;
};

export type RuntimeBrokerStatus = {
  phase: string;
  strategy: string;
  intelligenceSystem: {
    name: string;
    runtimeClass: string;
    purpose: string;
    claimBoundary: string;
  };
  recommendedProvider: string;
  liveRuntimeProvider?: string;
  canInvokeLiveRuntime?: boolean;
  selection?: {
    providerId: string;
    reasonCode: string;
    explanation: string;
  };
  providers: Record<string, Record<string, unknown>>;
  providerOrder: string[];
  productUnit: string;
  showsTokenCounter: boolean;
  secretsExposed: boolean;
};

export type RuntimeBrokerExplanation = {
  phase: string;
  provider: RuntimeBrokerProvider & Record<string, unknown>;
  selection: {
    providerId: string;
    selected: string;
    canInvokeLiveRuntime: boolean;
    message: string;
    safeForNoKeyDemo: boolean;
    requiresSecretsInFrontend: boolean;
    secretsExposed: boolean;
  };
  claimBoundary: {
    canInvokeLiveRuntime: boolean;
    message: string;
    liveRuntimeProvider: string;
  };
  productUnit: string;
  secretsExposed: boolean;
};

export type LicenseStatus = {
  phase: string;
  status: string;
  licensePresent: boolean;
  hashAuthorized: boolean;
  hash: string;
  licensePath: string;
  entitlementId: string;
  priorityClass: string;
  productUnit: string;
  authorizationScope: string;
  authorizesOfficialRuntime: boolean;
  authorizesPersistentServiceTokens: boolean;
  allowsControlledRuntimeArtifacts: boolean;
  runtimeCredentialBinding: string;
  providerBillingMode: string;
  technicalCredentialStoredInLicense: boolean;
  unlocksOfficialRuntime: boolean;
  unlocksProviderBilling: boolean;
  secretsExposed: boolean;
  message: string;
};

export type ScopeAuthority = {
  phase: string;
  scopeReady: boolean;
  lockState: string;
  precedence: string[];
  license: LicenseStatus;
  contracts: {
    locked: boolean;
    hashesVerified: boolean;
    lockPath: string;
    protectedFiles: Array<{
      path: string;
      exists: boolean;
      expectedSha256: string;
      currentSha256: string;
      verified: boolean;
    }>;
  };
  signatureEvidence: {
    evidenceType: string;
    samAltmanNamePresent: boolean;
    samAltmanSignaturePresent: boolean;
    fidjiSimoNamePresent: boolean;
    fidjiSimoSignaturePresent: boolean;
    openAiCorpPresent: boolean;
  };
  scopeTerms: Record<string, boolean>;
  runtimeBinding: string;
  requiredReadBeforeScopedWork: string[];
  secretsExposed: boolean;
  message: string;
};

export type ScopePreflight = {
  phase: string;
  scopeReady: boolean;
  scopeDecision: string;
  executionState: string;
  blockingReasons: string[];
  requested: {
    operation: string;
    environment: string;
    modelId: string;
    requiresLiveRuntime: boolean;
    requiresRestrictedArtifacts: boolean;
    reason: string;
  };
  runtimeReady: boolean;
  runtimeBinding: string;
  userVisibleMeter: string;
  productUnit: string;
  evidence: Record<string, unknown>;
  requiredControls: string[];
  secretsExposed: boolean;
};

export type RuntimeBindingStatus = {
  phase: string;
  scopeReady: boolean;
  bindingState: string;
  canInvokeLiveRuntime: boolean;
  provider: string;
  providerProfile: {
    source?: string;
    wireApi?: string;
    baseUrlConfigured?: boolean;
    deploymentConfigured?: boolean;
    tenantRequired?: boolean;
    tenantConfigured?: boolean;
  };
  integration?: Record<string, unknown> | null;
  credential: {
    reference: string;
    configured: boolean;
    secretValueExposed: boolean;
    storageRequirement: string;
    frontendExposureAllowed: boolean;
    logsExposureAllowed: boolean;
    rotationPolicy: string;
  };
  environment: {
    sandboxEnvironmentConfigured: boolean;
    secretStore?: string | null;
    secureStoreConfigured: boolean;
    liveFlagEnabled: boolean;
    approvedRealDataProfiles: number;
  };
  missingBinding: string[];
  approvedModels: string[];
  approvedOperations: string[];
  runtimeBinding: string;
  productUnit: string;
  userVisibleMeter: string;
  secretsExposed: boolean;
  requiredControls: string[];
};

export type LanguageEvaluation = {
  approved: boolean;
  blockedTerms: string[];
  allowedTerms: string[];
  severity: string;
  recommendation: string;
};

export type IntegrationGuardrails = {
  scope: string;
  contractAuthority?: string;
  allowedOperations: string[];
  blockedOperations: string[];
  conditionalOperations?: string[];
  restrictedAccessControls?: Record<string, unknown>;
  privateArtifactPolicy: {
    userReleaseIncludesPrivateArtifacts: boolean;
    developerMachineRestrictedArtifactsAllowed?: boolean;
    privateCodexBinariesAllowedInUserBundle: boolean;
    modelWeightsOrCheckpointsAllowedInUserBundle: boolean;
    publicReleaseIncludesPrivateArtifacts?: boolean;
    requiresSignedArtifactAuthorization: boolean;
  };
  codexAuthPolicy: {
    manageCodexAuthJson: boolean;
    multiAccountLimitBypass: boolean;
    accessMode: string;
  };
};

export type IdentityProfile = {
  id: string;
  profileId: string;
  displayName: string;
  profileType: string;
  runtimeAccessMode: string;
  codexAuthMode: string;
  allowedWorkspace: string;
  status: string;
};

export type SecureRuntimeBridge = {
  id: string;
  bridgeId: string;
  name: string;
  mode: string;
  allowedOperations: string[];
  blockedOperations: string[];
  requiresSignedArtifactAuthorization: boolean;
  storesPrivateArtifacts: boolean;
  status: string;
};

export type ContextIndexInfo = {
  id: string;
  sessionId?: string;
  name: string;
  source: string;
  status: string;
  fileCount: number;
  graphNodes: number;
  graphEdges: number;
  indexPath: string;
};

export type SkillStoreItem = {
  id: string;
  skillId: string;
  name: string;
  category: string;
  tier: string;
  description: string;
  activationTriggers: string[];
  permissionsRequired: string[];
  status: string;
};

export type WindowsReleaseManifest = {
  id: string;
  releaseId: string;
  name: string;
  platform: string;
  channel: string;
  version: string;
  includesPrivateCodexArtifacts: boolean;
  launcherType: string;
  installMode: string;
  status: string;
  files: string[];
};

export type OfficialIntegrationReadiness = {
  phase: string;
  contractAuthority: {
    locked: boolean;
    lockPath: string;
    protectedFiles: string[];
  };
  adapter: {
    targetClass: string;
    currentLocalFallback: string;
    official: Record<string, unknown>;
  };
  runtime: {
    sandboxApproved: boolean;
    stagingApproved: boolean;
    productionStatus: string;
    streamingSupported: boolean;
    toolCallingSupported: boolean;
    sessionLifecycleSupported: boolean;
    snapshotHandoffHooksSupported: boolean;
  };
  credentials: {
    endpointConfigured: boolean;
    serviceTokenConfigured: boolean;
    tenantConfigured: boolean;
    secretsExposed: boolean;
    storageRequirement: string;
  };
  readyForLiveRuntime: boolean;
  nextSteps: string[];
};

export type OfficialSandboxSecurityCheck = {
  phase: string;
  state: string;
  mode: string;
  provider: string;
  providerRequirements: Record<string, string | null>;
  contractLocked: boolean;
  endpointConfigured: boolean;
  serviceTokenConfigured: boolean;
  tenantConfigured: boolean;
  azureEndpointConfigured: boolean;
  azureApiKeyConfigured: boolean;
  azureDeploymentConfigured: boolean;
  openaiEndpointConfigured: boolean;
  openaiApiKeyConfigured: boolean;
  openaiProjectConfigured: boolean;
  openaiOrganizationConfigured: boolean;
  environmentConfigured: boolean;
  secureStoreConfigured: boolean;
  secretStore?: string;
  liveFlagEnabled: boolean;
  secureEnvironmentReady: boolean;
  canInvokeLiveRuntime: boolean;
  approvedRealDataProfiles: number;
  secretsExposed: boolean;
  frontendExposureAllowed: boolean;
  logsExposureAllowed: boolean;
  networkCallAllowed: boolean;
  missing: string[];
  requiredControls: string[];
};

export type OfficialSandboxActivation = {
  phase: string;
  activationState: string;
  mode: string;
  canInvokeLiveRuntime: boolean;
  networkCallPerformed: boolean;
  message: string;
  security: OfficialSandboxSecurityCheck;
};

export type SandboxDataProfile = {
  id: string;
  profileId: string;
  name: string;
  dataClassification: string;
  approvalReference: string;
  redactionRequired: boolean;
  publicExportAllowed: boolean;
  realDataApproved: boolean;
  retentionDays: number;
  status: string;
  createdByUserId: string;
  createdAt: string;
};

export type RestrictedAccessRequestInfo = {
  id: string;
  operation: string;
  environment: string;
  justification: string;
  artifactName: string;
  artifactHash: string;
  pathScope: string;
  status: string;
  approvedBy: string;
  decisionNotes: string;
  expiresAt?: string;
  decidedAt?: string;
  expired?: boolean;
  activeApproval?: boolean;
  createdAt: string;
};
