import axios from "axios";
import {
  Claim,
  ClaimStats,
  MatchPair,
  QueueStatus,
  LiveQueueItem,
  LiveQueueState,
  IngestionBatch,
  SystemSettings,
  BrandingSettings,
  GuidewireTestRequest,
  GuidewireTestResponse,
  PortalTestRequest,
  PortalTestResponse,
  BrowserTestRequest,
  BrowserTestResponse,
  FleetTestRequest,
  FleetTestResponse,
  FleetWorkerResult,
  FilePreviewData,
  SystemHealthData,
  PortalPingResponse,
  ErrorScreenshot,
  StorageTestRequest,
  StorageTestResponse,
  ProxyTestRequest,
  ProxyTestResponse,
  RetryFailedResponse,
  AuditLogEntry,
  AuditLogListResponse,
  AuditLogStats,
  AuditLogQueryParams,
  ClaimCombinedLogsResponse,
  FileValidationResult,
  EmailConnectionTestRequest,
  EmailConnectionTestResponse,
  TestEmailSendRequest,
  TestEmailSendResponse,
  NotificationItem,
  NotificationListResponse,
  NotificationTemplate,
  NotificationRule,
  TemplatePreviewResponse,
  TemplatePreviewRequest,
  TemplateUpdateRequest,
  TemplateParameter,
  ExtractNamesResponse,
  FuzzySearchRequest,
  FuzzySearchResponse,
  UniqueNamesRequest,
  UniqueNamesResponse,
  DirectFuzzyMatchRequest,
  DirectFuzzyMatchResponse,
  AntiCaptchaTestResponse,
  CleanupCategory,
  CleanupPreviewRequest,
  CleanupPreviewResponse,
  CleanupExecuteRequest,
  CleanupExecuteResponse,
  ExtensionSetupResponse,
} from "../types";


const getApiBaseUrl = () => {
  // Dynamic environment variables take highest priority (Vercel, Netlify, Cloud Run, custom proxy)
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL;
  if (envUrl && envUrl.trim().length > 0) {
    return envUrl.trim().replace(/\/+$/, "");
  }

  // Client-side fallback to current host:8000 for local dev (use 127.0.0.1 to avoid Windows IPv6 SYN timeout)
  if (typeof window !== "undefined") {
    const rawHost = window.location.hostname || "127.0.0.1";
    const host = rawHost === "localhost" ? "127.0.0.1" : rawHost;
    return `http://${host}:8000/api/v1`;
  }

  // Server-side fallback default
  return "http://127.0.0.1:8000/api/v1";
};

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  if (!config.baseURL) {
    config.baseURL = getApiBaseUrl();
  }
  return config;
});

export const api = {
  // Health & Observability
  getHealth: async () => {
    const res = await apiClient.get("/health");
    return res.data;
  },

  getDetailedHealth: async (): Promise<SystemHealthData> => {
    const res = await apiClient.get("/health/detailed");
    return res.data;
  },

  pingPortal: async (portalKey: string): Promise<PortalPingResponse> => {
    const res = await apiClient.get(`/portals/${portalKey}/ping`);
    return res.data;
  },


  // Ingest
  previewFile: async (file: File): Promise<FilePreviewData> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiClient.post("/ingest/preview", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  validateFileMapping: async (
    file: File,
    mapping: Record<string, string | null>,
    duplicateStrategy: string = "SKIP"
  ): Promise<FileValidationResult> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("mapping", JSON.stringify(mapping));
    formData.append("duplicate_strategy", duplicateStrategy);
    const res = await apiClient.post("/ingest/validate", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  uploadFileWithMapping: async (
    file: File,
    mapping?: Record<string, string | null>,
    duplicateStrategy: string = "SKIP"
  ): Promise<IngestionBatch> => {
    const formData = new FormData();
    formData.append("file", file);
    if (mapping) {
      formData.append("mapping", JSON.stringify(mapping));
    }
    formData.append("duplicate_strategy", duplicateStrategy);
    const res = await apiClient.post("/ingest/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  uploadFile: async (file: File): Promise<IngestionBatch> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiClient.post("/ingest/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  getBatchStatus: async (batchId: string): Promise<IngestionBatch> => {
    const res = await apiClient.get(`/ingest/batches/${batchId}`);
    return res.data;
  },

  getFailedRowsDownloadUrl: (batchId: string): string => {
    return `${getApiBaseUrl()}/ingest/batches/${batchId}/failed-rows`;
  },



  // Claims
  getClaims: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    fuzzy_status?: string;
    state?: string;
    county?: string;
    search?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<{ total: number; items: Claim[]; page: number; page_size: number; total_pages: number }> => {
    const cleanParams: Record<string, any> = {};
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== "") {
          cleanParams[key] = val;
        }
      });
    }
    const res = await apiClient.get("/claims", { params: cleanParams });
    return res.data;
  },

  createClaim: async (data: any): Promise<Claim> => {
    const res = await apiClient.post("/claims", data);
    return res.data;
  },

  updateClaim: async (id: string, data: any): Promise<Claim> => {
    const res = await apiClient.put(`/claims/${id}`, data);
    return res.data;
  },

  deleteClaim: async (id: string): Promise<{ success: boolean; message: string }> => {
    const res = await apiClient.delete(`/claims/${id}`);
    return res.data;
  },

  startClaim: async (id: string): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post(`/claims/${id}/start`);
    return res.data;
  },

  stopClaim: async (id: string): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post(`/claims/${id}/stop`);
    return res.data;
  },

  getClaimScreenshots: async (claimId: string): Promise<{ total: number; screenshots: ErrorScreenshot[] }> => {
    const res = await apiClient.get<{ total: number; screenshots: ErrorScreenshot[] }>(`/claims/${claimId}/screenshots`);
    return res.data;
  },

  bulkDeleteClaims: async (claimIds: string[]): Promise<{ success: boolean; affected_count: number; message: string }> => {
    const res = await apiClient.post("/claims/bulk-delete", { claim_ids: claimIds });
    return res.data;
  },

  bulkUpdateStatus: async (claimIds: string[], status: string): Promise<{ success: boolean; affected_count: number; message: string }> => {
    const res = await apiClient.post("/claims/bulk-status", { claim_ids: claimIds, status });
    return res.data;
  },

  bulkStartClaims: async (claimIds: string[]): Promise<{ success: boolean; affected_count: number; message: string }> => {
    const res = await apiClient.post("/claims/bulk-start", { claim_ids: claimIds });
    return res.data;
  },

  bulkRetryClaims: async (claimIds: string[], failedPortalsOnly: boolean = true): Promise<{ success: boolean; affected_count: number; message: string }> => {
    const res = await apiClient.post("/claims/bulk-retry", { claim_ids: claimIds, failed_portals_only: failedPortalsOnly });
    return res.data;
  },

  cleanDatabase: async (): Promise<{ success: boolean; message: string; cleared_counts: any }> => {
    const res = await apiClient.post("/claims/clean");
    return res.data;
  },

  getExportUrl: (params?: { format?: string; status?: string; state?: string; search?: string; claim_ids?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.format) searchParams.set("format", params.format);
    if (params?.status) searchParams.set("status", params.status);
    if (params?.state) searchParams.set("state", params.state);
    if (params?.search) searchParams.set("search", params.search);
    if (params?.claim_ids) searchParams.set("claim_ids", params.claim_ids);
    const base = getApiBaseUrl();
    return `${base}/claims/export?${searchParams.toString()}`;
  },

  triggerAsyncExport: async (payload: {
    format: "xlsx" | "csv" | "json";
    status?: string;
    state?: string;
    search?: string;
    claim_ids?: string[];
  }): Promise<{ success: boolean; task_id: string; message: string }> => {
    const res = await apiClient.post("/claims/export-async", payload);
    return res.data;
  },

  getAsyncExportStatus: async (taskId: string): Promise<{
    task_id: string;
    status: string;
    percent: number;
    current?: number;
    total?: number;
    message?: string;
    result?: {
      filename?: string;
      download_url?: string;
      total_rows?: number;
      file_size?: number;
    };
    error?: string;
  }> => {
    const res = await apiClient.get(`/claims/export-async/${taskId}/status`);
    return res.data;
  },

  getAsyncExportDownloadUrl: (filename: string): string => {
    const base = getApiBaseUrl();
    return `${base}/claims/export-async/download/${filename}`;
  },

  getClaimStats: async (): Promise<ClaimStats> => {
    const res = await apiClient.get("/claims/stats");
    return res.data;
  },

  getClaimDetail: async (id: string): Promise<Claim> => {
    const res = await apiClient.get(`/claims/${id}`);
    return res.data;
  },

  getClaimById: async (id: string): Promise<Claim> => {
    const res = await apiClient.get(`/claims/${id}`);
    return res.data;
  },

  pushToGuidewire: async (claimId: string): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post(`/claims/${claimId}/push-guidewire`);
    return res.data;
  },

  runSingleBot: async (claimId: string, botKey: string): Promise<{ status: string; message: string; bot_key: string }> => {
    const res = await apiClient.post(`/claims/${claimId}/run-bot/${botKey}`);
    return res.data;
  },

  retryFailedPortals: async (claimId: string): Promise<RetryFailedResponse> => {
    const res = await apiClient.post(`/claims/${claimId}/retry-failed`);
    return res.data;
  },

  getSingleClaimExportUrl: (claimId: string, format: "xlsx" | "csv" | "json" | "pdf") => {
    const base = getApiBaseUrl();
    return `${base}/claims/${claimId}/export?format=${format}`;
  },

  getClaimScreenshotImageUrl: (claimId: string, screenshotId: string): string => {
    const base = getApiBaseUrl();
    return `${base}/claims/${claimId}/screenshots/${screenshotId}/image`;
  },

  // Matches & Manual Review
  getPendingMatches: async (limit: number = 50): Promise<MatchPair[]> => {
    const res = await apiClient.get("/matches/pending", { params: { limit } });
    return res.data;
  },

  getMatchPair: async (id: string): Promise<MatchPair> => {
    const res = await apiClient.get(`/matches/${id}`);
    return res.data;
  },

  reviewMatchPair: async (
    id: string,
    decision: "APPROVED" | "REJECTED",
    reviewedBy: string = "Admin",
    notes?: string
  ) => {
    const res = await apiClient.post(`/matches/${id}/review`, {
      decision,
      reviewed_by: reviewedBy,
      review_notes: notes,
    });
    return res.data;
  },

  // Queue & Retrigger
  getQueueStatus: async (): Promise<QueueStatus> => {
    const res = await apiClient.get("/queue/status");
    return res.data;
  },

  getLiveQueue: async (): Promise<LiveQueueState> => {
    const res = await apiClient.get("/queue/live");
    return res.data;
  },

  runNextQueueItem: async (): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post("/queue/run-next");
    return res.data;
  },

  getAutoQueueMode: async (): Promise<{ auto_queue_enabled: boolean; is_running: boolean; current_claim_id?: string }> => {
    const res = await apiClient.get("/queue/auto-mode");
    return res.data;
  },

  toggleAutoQueueMode: async (enabled: boolean): Promise<{ auto_queue_enabled: boolean; message: string }> => {
    const res = await apiClient.post("/queue/auto-mode", { enabled });
    return res.data;
  },

  startAllQueue: async (): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post("/queue/start-all");
    return res.data;
  },

  setQueueConcurrency: async (concurrency: number): Promise<{ concurrency: number; message: string }> => {
    const res = await apiClient.post("/queue/concurrency", { concurrency });
    return res.data;
  },

  seedDemoClaims: async (count: number = 10): Promise<{ message: string; count: number; claim_ids: string[] }> => {
    const res = await apiClient.post("/queue/seed-demo", { count });
    return res.data;
  },

  runSelectedQueueItems: async (claimIds: string[]): Promise<{ message: string; count: number; claim_ids: string[] }> => {
    const res = await apiClient.post("/queue/run-selected", { claim_ids: claimIds });
    return res.data;
  },

  pauseQueue: async (): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post("/queue/pause");
    return res.data;
  },

  retriggerClaims: async (claimIds?: string[]) => {
    const res = await apiClient.post("/queue/retrigger", {
      claim_ids: claimIds,
    });
    return res.data;
  },

  // Settings
  getSettings: async (): Promise<SystemSettings> => {
    const res = await apiClient.get("/settings");
    return res.data;
  },

  updateSettings: async (settings: SystemSettings): Promise<SystemSettings> => {
    const res = await apiClient.post("/settings", settings);
    return res.data;
  },

  resetSettings: async (): Promise<SystemSettings> => {
    const res = await apiClient.post("/settings/reset");
    return res.data;
  },

  // Dedicated Brand & Identity Settings
  getBrandingSettings: async (): Promise<BrandingSettings> => {
    const res = await apiClient.get("/settings/branding");
    return res.data;
  },

  updateBrandingSettings: async (branding: BrandingSettings): Promise<BrandingSettings> => {
    const res = await apiClient.post("/settings/branding", branding);
    return res.data;
  },

  resetBrandingSettings: async (): Promise<BrandingSettings> => {
    const res = await apiClient.post("/settings/branding/reset");
    return res.data;
  },

  // Interactive Testing Sandboxes
  testGuidewireConnection: async (payload?: GuidewireTestRequest): Promise<GuidewireTestResponse> => {
    const res = await apiClient.post("/settings/test-guidewire", payload || {});
    return res.data;
  },

  testPortalConnection: async (payload: PortalTestRequest): Promise<PortalTestResponse> => {
    const res = await apiClient.post("/settings/test-portal", payload);
    return res.data;
  },

  testBrowserLaunch: async (payload?: BrowserTestRequest): Promise<BrowserTestResponse> => {
    const res = await apiClient.post("/settings/test-browser", payload || {});
    return res.data;
  },

  testFleet: async (payload?: FleetTestRequest): Promise<FleetTestResponse> => {
    const res = await apiClient.post("/settings/test-fleet", payload || {});
    return res.data;
  },

  validateExtension: async (payload?: {
    chrome_extension_dir?: string;
    anticaptcha_api_key?: string;
  }): Promise<{
    status: string;
    extension_dir: string;
    directory_exists: boolean;
    manifest_valid: boolean;
    api_key_configured: boolean;
    api_key_synced: boolean;
    engine_support: Record<string, { supported: boolean; status: string; note: string }>;
    recommended_engine: string;
    message: string;
  }> => {
    const res = await apiClient.post("/settings/validate-extension", payload || {});
    return res.data;
  },

  setupExtension: async (payload?: {
    force_reconfigure?: boolean;
  }): Promise<ExtensionSetupResponse> => {
    const res = await apiClient.post("/settings/setup-extension", payload || {});
    return res.data;
  },

  testStorageConnection: async (payload: StorageTestRequest): Promise<StorageTestResponse> => {
    const res = await apiClient.post("/settings/test-storage", payload);
    return res.data;
  },

  testProxyConnection: async (payload: ProxyTestRequest): Promise<ProxyTestResponse> => {
    const res = await apiClient.post("/settings/test-proxy", payload);
    return res.data;
  },

  // Branding Custom Logo Upload
  uploadBrandLogo: async (
    file: File
  ): Promise<{
    success: boolean;
    url: string;
    filename: string;
    size_bytes: number;
    content_type: string;
    message: string;
  }> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiClient.post("/settings/upload-logo", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  // Audit Logs & Provenance (§73)
  getAuditLogs: async (params?: AuditLogQueryParams): Promise<AuditLogListResponse> => {
    const res = await apiClient.get("/audit-logs", { params });
    return res.data;
  },

  getAuditLogStats: async (): Promise<AuditLogStats> => {
    const res = await apiClient.get("/audit-logs/stats");
    return res.data;
  },

  getClaimAuditLogs: async (claimId: string): Promise<AuditLogEntry[]> => {
    const res = await apiClient.get(`/claims/${claimId}/audit-logs`);
    return res.data;
  },

  getClaimCombinedLogs: async (claimId: string, sort_order?: string): Promise<ClaimCombinedLogsResponse> => {
    const res = await apiClient.get(`/claims/${claimId}/combined-logs`, {
      params: sort_order ? { sort_order } : undefined,
    });
    return res.data;
  },

  exportAuditLogs: async (params?: AuditLogQueryParams & { format?: 'csv' | 'json' | 'xlsx' | 'pdf' }): Promise<Blob> => {
    const res = await apiClient.get("/audit-logs/export", {
      params,
      responseType: "blob",
    });
    return res.data;
  },

  // Email & Notification Engine
  testEmailConnection: async (payload: EmailConnectionTestRequest): Promise<EmailConnectionTestResponse> => {
    const res = await apiClient.post("/settings/email/test-connection", payload);
    return res.data;
  },

  sendTestEmail: async (payload: TestEmailSendRequest): Promise<TestEmailSendResponse> => {
    const res = await apiClient.post("/settings/email/test-send", payload);
    return res.data;
  },

  getNotifications: async (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
    event_type?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<NotificationListResponse> => {
    const res = await apiClient.get("/notifications", { params });
    return res.data;
  },

  getNotificationById: async (id: string): Promise<NotificationItem> => {
    const res = await apiClient.get(`/notifications/${id}`);
    return res.data;
  },

  getNotificationTemplates: async (): Promise<NotificationTemplate[]> => {
    const res = await apiClient.get("/notifications/templates");
    return res.data;
  },

  updateNotificationTemplate: async (
    eventType: string,
    payload: TemplateUpdateRequest
  ): Promise<NotificationTemplate> => {
    const res = await apiClient.put(`/notifications/templates/${eventType}`, payload);
    return res.data;
  },

  resetNotificationTemplate: async (eventType: string): Promise<NotificationTemplate> => {
    const res = await apiClient.post(`/notifications/templates/${eventType}/reset`);
    return res.data;
  },

  getTemplateTokens: async (): Promise<TemplateParameter[]> => {
    const res = await apiClient.get("/notifications/templates/tokens");
    return res.data;
  },

  previewNotificationTemplate: async (payload: TemplatePreviewRequest): Promise<TemplatePreviewResponse> => {
    const res = await apiClient.post("/notifications/templates/preview", payload);
    return res.data;
  },

  getNotificationRules: async (): Promise<{ rules: NotificationRule[]; global_enabled: boolean }> => {
    const res = await apiClient.get("/notifications/rules");
    return res.data;
  },

  updateNotificationRules: async (rules: Record<string, boolean>): Promise<{ status: string; rules: Record<string, boolean> }> => {
    const res = await apiClient.put("/notifications/rules", rules);
    return res.data;
  },

  // --- Fuzzy Match: Extract Unique Party Names ---
  extractUniquePartyNames: async (partyType?: string): Promise<ExtractNamesResponse> => {
    const params = partyType ? { party_type: partyType } : {};
    const res = await apiClient.get("/matches/extract-names", { params });
    return res.data;
  },

  // --- Fuzzy Match: Legacy Power Automate Fuzzy Search ---
  fuzzySearchCases: async (payload: FuzzySearchRequest): Promise<FuzzySearchResponse> => {
    const res = await apiClient.post("/matches/fuzzy-search", payload);
    return res.data;
  },

  // --- Settings: Test Anti-Captcha API Key ---
  testAntiCaptchaKey: async (apiKey: string): Promise<AntiCaptchaTestResponse> => {
    const res = await apiClient.post("/settings/test-anticaptcha", { api_key: apiKey });
    return res.data;
  },

  // --- Enterprise Data Cleanup & Retention ---
  getCleanupCategories: async (): Promise<CleanupCategory[]> => {
    const res = await apiClient.get("/cleanup/categories");
    return res.data;
  },

  previewCleanup: async (payload: CleanupPreviewRequest): Promise<CleanupPreviewResponse> => {
    const res = await apiClient.post("/cleanup/preview", payload);
    return res.data;
  },

  executeCleanup: async (payload: CleanupExecuteRequest): Promise<CleanupExecuteResponse> => {
    const res = await apiClient.post("/cleanup/execute", payload);
    return res.data;
  },

  // --- Exceptions / Matches Export ---
  exportMatches: async (params?: { format?: "xlsx" | "csv" | "json"; status?: string; limit?: number }): Promise<Blob> => {
    const res = await apiClient.get("/matches/export", {
      params,
      responseType: "blob",
    });
    return res.data;
  },

  getMatchesExportUrl: (params?: { format?: string; status?: string }): string => {
    const searchParams = new URLSearchParams();
    if (params?.format) searchParams.set("format", params.format);
    if (params?.status) searchParams.set("status", params.status);
    const base = getApiBaseUrl();
    return `${base}/matches/export?${searchParams.toString()}`;
  },

  // --- Automation UI Testers ---
  generateUniqueNames: async (payload: UniqueNamesRequest): Promise<UniqueNamesResponse> => {
    const res = await apiClient.post("/matches/unique-names", payload);
    return res.data;
  },

  testFuzzyMatch: async (payload: DirectFuzzyMatchRequest): Promise<DirectFuzzyMatchResponse> => {
    const res = await apiClient.post("/matches/fuzzymatchapi", payload);
    return res.data;
  },
};

export const cleanupApi = {
  getCategories: api.getCleanupCategories,
  preview: api.previewCleanup,
  execute: api.executeCleanup,
};


