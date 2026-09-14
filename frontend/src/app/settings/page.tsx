"use client";

import React, { useEffect, useState } from "react";
import { Navbar } from "../../components/Navbar";
import { api } from "../../lib/api";
import {
  SystemSettings,
  GuidewireTestRequest,
  GuidewireTestResponse,
  PortalTestResponse,
  BrowserTestResponse,
  StorageTestRequest,
  StorageTestResponse,
  EmailSettings,
  EmailConnectionTestResponse,
  TestEmailSendResponse,
  NotificationItem,
  NotificationTemplate,
  TemplateParameter,
  TemplateUpdateRequest,
  QueueStatus,
  UniqueNamesRequest,
  UniqueNamesResponse,
  DirectFuzzyMatchRequest,
  DirectFuzzyMatchResponse
} from "../../types";
import { StatCard } from "../../components/StatCard";
import {
  Sliders,
  ShieldCheck,
  RefreshCw,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Eye,
  EyeOff,
  Sparkles,
  Zap,
  Globe,
  Layers,
  Send,
  Terminal,
  Copy,
  Check,
  Radio,
  ExternalLink,
  Clock,
  Mail,
  Filter,
  Monitor,
  Play,
  X,
  HardDrive,
  Cloud,
  Server,
  Database,
  Camera,
  Plus,
  FileText,
  CheckSquare,
  Receipt,
  CheckCheck,
  Inbox,
  Edit3,
  Code2,
  Tag,
  FileCode,
  Activity,
  Plug,
  Search,
  ChevronLeft,
  ChevronRight,
  Columns,
  Smartphone,
  Laptop,
  AlignLeft,
  Network,
} from "lucide-react";
import { useBranding, DEFAULT_BRANDING } from "../../components/BrandingContext";

type SettingsTab = "guidewire" | "portals" | "automation" | "extension" | "email" | "storage" | "matcher" | "queue" | "proxy";

const DEFAULT_EMAIL_SETTINGS: EmailSettings = {
  email_notifications_enabled: true,
  provider: "local_mock",
  maildev_web_url: "http://localhost:1080",
  smtp_host: "localhost",
  smtp_port: 587,
  smtp_username: "",
  smtp_password: "",
  smtp_encryption: "tls",
  from_name: "UAIC Claim Alerts",
  from_email: "notifications@test.com",
  reply_to: "",
  graph_tenant_id: "",
  graph_client_id: "",
  graph_client_secret: "",
  ses_region: "us-east-1",
  ses_access_key_id: "",
  ses_secret_access_key: "",
  to_recipients: ["claims-ops@test.com"],
  cc_recipients: [],
  bcc_recipients: [],
  timeout_seconds: 15,
  retry_count: 3,
  retry_delay_seconds: 30,
  rules: {
    court_case_matched: true,
    guidewire_activity_created: true,
    guidewire_activity_failed: true,
    scraper_failed: true,
    claim_failed: true,
  },
};

const ENGINE_USER_AGENTS: Record<string, string> = {
  chromium: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  chrome: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  msedge: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
};

export default function SettingsPage() {
  const { updateBranding } = useBranding();
  const [activeTab, setActiveTab] = useState<SettingsTab>("guidewire");
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  // Password visibility toggles
  const [showApiKey, setShowApiKey] = useState(false);
  const [showClientSecret, setShowClientSecret] = useState(false);
  const [showMiamiPassword, setShowMiamiPassword] = useState(false);
  const [showS3Secret, setShowS3Secret] = useState(false);
  const [showAzureConn, setShowAzureConn] = useState(false);
  const [showSmtpPassword, setShowSmtpPassword] = useState(false);
  const [showGraphSecret, setShowGraphSecret] = useState(false);
  const [showSesSecret, setShowSesSecret] = useState(false);

  // Guidewire interactive test console state
  const [isTestingGuidewire, setIsTestingGuidewire] = useState(false);
  const [guidewireTestResponse, setGuidewireTestResponse] = useState<GuidewireTestResponse | null>(null);
  const [testPayloadText, setTestPayloadText] = useState<string>(
    JSON.stringify(
      {
        ClaimNumber: "0100234567",
        ExposureNumber: "1",
        CaseItems: [
          {
            CaseNumber: "COCE-23-019482",
            CaseStyle: "JOHN DOE VS JANE SMITH",
            CountyWebsite: "https://www.browardclerk.org/",
            SuitFiledDate: "2023-05-14",
          },
        ],
      },
      null,
      2
    )
  );
  const [copiedResponse, setCopiedResponse] = useState(false);

  // Portal test states
  const [testingPortals, setTestingPortals] = useState<Record<string, boolean>>({});
  const [portalResults, setPortalResults] = useState<Record<string, PortalTestResponse>>({});

  // Browser launch test states
  const [isTestingBrowser, setIsTestingBrowser] = useState(false);
  const [browserTestResult, setBrowserTestResult] = useState<BrowserTestResponse | null>(null);

  // AntiCaptcha extension validation states
  const [isValidatingExtension, setIsValidatingExtension] = useState(false);
  const [extensionValidationResult, setExtensionValidationResult] = useState<any | null>(null);

  // AntiCaptcha API key balance test state (new /test-anticaptcha endpoint)
  const [isTestingAntiCaptchaBalance, setIsTestingAntiCaptchaBalance] = useState(false);
  const [antiCaptchaBalanceResult, setAntiCaptchaBalanceResult] = useState<{
    status: "ok" | "error";
    balance?: number | null;
    message: string;
    latency_ms: number;
    error_code?: string | null;
  } | null>(null);

  // Unique Names Tester State
  const [isTestingUniqueNames, setIsTestingUniqueNames] = useState(false);
  const [uniqueNamesResult, setUniqueNamesResult] = useState<UniqueNamesResponse | null>(null);
  const [testUniqueNamesPayload, setTestUniqueNamesPayload] = useState<string>(
    JSON.stringify(
      {
        Claimants: [{ FirstName: "John", LastName: "Doe", MiddleName: "A", Suffix: "Jr" }],
        Insureds: [{ FirstName: "Jane", LastName: "Doe", MiddleName: "", Suffix: "" }],
        Drivers: [{ FirstName: "John", LastName: "Doe", MiddleName: "", Suffix: "" }]
      },
      null,
      2
    )
  );

  // Fuzzy Match Tester State
  const [isTestingFuzzyMatch, setIsTestingFuzzyMatch] = useState(false);
  const [fuzzyMatchResult, setFuzzyMatchResult] = useState<DirectFuzzyMatchResponse | null>(null);
  const [testFuzzyMatchPayload, setTestFuzzyMatchPayload] = useState<string>(
    JSON.stringify(
      {
        UniqueNames: ["JOHN DOE", "JANE DOE"],
        Threshold: 0.60,
        Cases: [
          {
            CaseNumber: "COCE-23-019482",
            CaseStyle: "JOHN DOE VS JANE SMITH",
            FilingDate: "2023-05-14"
          }
        ]
      },
      null,
      2
    )
  );

  const handleTestUniqueNames = async () => {
    setIsTestingUniqueNames(true);
    setUniqueNamesResult(null);
    try {
      const payload: UniqueNamesRequest = JSON.parse(testUniqueNamesPayload);
      const res = await api.generateUniqueNames(payload);
      setUniqueNamesResult(res);
      setFeedback({
        type: "success",
        msg: `Generated ${res.unique_names.length} unique names successfully.`,
      });
    } catch (err: any) {
      setFeedback({ type: "error", msg: err?.response?.data?.detail || err.message || "Failed to generate unique names." });
    } finally {
      setIsTestingUniqueNames(false);
    }
  };

  const handleTestFuzzyMatch = async () => {
    setIsTestingFuzzyMatch(true);
    setFuzzyMatchResult(null);
    try {
      const payload: DirectFuzzyMatchRequest = JSON.parse(testFuzzyMatchPayload);
      const res = await api.testFuzzyMatch(payload);
      setFuzzyMatchResult(res);
      setFeedback({
        type: "success",
        msg: `Fuzzy match completed successfully.`,
      });
    } catch (err: any) {
      setFeedback({ type: "error", msg: err?.response?.data?.detail || err.message || "Failed to test fuzzy match." });
    } finally {
      setIsTestingFuzzyMatch(false);
    }
  };

  const handleTestAntiCaptchaBalance = async () => {
    if (!settings) return;
    const apiKey = settings.automation.anticaptcha_api_key || "";
    if (!apiKey.trim()) {
      setFeedback({ type: "error", msg: "Enter an AntiCaptcha API key first." });
      return;
    }
    setIsTestingAntiCaptchaBalance(true);
    setAntiCaptchaBalanceResult(null);
    try {
      const res = await api.testAntiCaptchaKey(apiKey.trim());
      setAntiCaptchaBalanceResult(res);
      setFeedback({
        type: res.status === "ok" ? "success" : "error",
        msg: res.message,
      });
    } catch (err: any) {
      setAntiCaptchaBalanceResult({
        status: "error",
        message: err?.response?.data?.detail || "Failed to reach test-anticaptcha endpoint.",
        latency_ms: 0,
      });
      setFeedback({ type: "error", msg: "AntiCaptcha balance check failed." });
    } finally {
      setIsTestingAntiCaptchaBalance(false);
    }
  };

  const handleValidateExtension = async () => {
    if (!settings) return;
    setIsValidatingExtension(true);
    try {
      const res = await api.validateExtension({
        chrome_extension_dir: settings.automation.chrome_extension_dir || undefined,
        anticaptcha_api_key: settings.automation.anticaptcha_api_key || undefined,
      });
      setExtensionValidationResult(res);
      setFeedback({
        type: res.status === "VALID" ? "success" : "error",
        msg: res.message,
      });
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to validate AntiCaptcha extension.",
      });
    } finally {
      setIsValidatingExtension(false);
    }
  };

  const handleTestBrowser = async (forceHeadless?: boolean) => {
    if (!settings) return;
    setIsTestingBrowser(true);
    setBrowserTestResult(null);
    try {
      const modeToTest = forceHeadless !== undefined ? forceHeadless : settings.automation.headless_mode;
      const res = await api.testBrowserLaunch({
        headless: modeToTest,
        browser_engine: settings.automation.browser_engine || "chromium",
        test_url: "https://example.com",
        timeout_seconds: 25,
        chrome_binary_path: settings.automation.chrome_binary_path || undefined,
        chrome_extension_dir: settings.automation.chrome_extension_dir || undefined,
      });
      setBrowserTestResult(res);
      if (res.success) {
        setFeedback({
          type: "success",
          msg: `Browser verified in ${res.mode} mode! (${res.duration_ms}ms) - Title: "${res.page_title}"`,
        });
      } else {
        setFeedback({
          type: "error",
          msg: `Browser test failed in ${res.mode} mode: ${res.message}`,
        });
      }
    } catch (err: any) {
      const errRes: BrowserTestResponse = {
        success: false,
        mode: settings.automation.headless_mode ? "Headless (Background)" : "Attended (Visible GUI)",
        headless: settings.automation.headless_mode,
        chrome_found: false,
        extension_found: false,
        duration_ms: 0,
        message: err?.response?.data?.detail || "Failed to reach backend test-browser endpoint.",
        error_detail: String(err),
      };
      setBrowserTestResult(errRes);
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Browser test failed.",
      });
    } finally {
      setIsTestingBrowser(false);
    }
  };

  // Storage test states
  const [isTestingStorage, setIsTestingStorage] = useState(false);
  const [storageTestResult, setStorageTestResult] = useState<StorageTestResponse | null>(null);

  const handleTestStorage = async () => {
    if (!settings) return;
    setIsTestingStorage(true);
    setStorageTestResult(null);
    try {
      const storageCfg = settings.storage || {
        capture_error_screenshots: true,
        storage_provider: "local",
      };
      const res = await api.testStorageConnection({
        storage_provider: storageCfg.storage_provider || "local",
        s3_bucket_name: storageCfg.s3_bucket_name,
        s3_region: storageCfg.s3_region,
        s3_access_key: storageCfg.s3_access_key,
        s3_secret_key: storageCfg.s3_secret_key,
        azure_connection_string: storageCfg.azure_connection_string,
        azure_container_name: storageCfg.azure_container_name,
        gcs_bucket_name: storageCfg.gcs_bucket_name,
        gcs_project_id: storageCfg.gcs_project_id,
        gcs_credentials_json: storageCfg.gcs_credentials_json,
      });
      setStorageTestResult(res);
      if (res.success) {
        setFeedback({
          type: "success",
          msg: `${res.message} (${res.duration_ms}ms)`,
        });
      } else {
        setFeedback({
          type: "error",
          msg: `Storage test: ${res.message}`,
        });
      }
    } catch (err: any) {
      const errRes: StorageTestResponse = {
        success: false,
        storage_provider: settings?.storage?.storage_provider || "local",
        message: err?.response?.data?.detail || "Failed to test storage connection.",
        duration_ms: 0,
        error_detail: String(err),
      };
      setStorageTestResult(errRes);
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Storage test failed.",
      });
    } finally {
      setIsTestingStorage(false);
    }
  };

  // Email & Notifications states
  const [isTestingEmailConnection, setIsTestingEmailConnection] = useState(false);
  const [emailConnectionResult, setEmailConnectionResult] = useState<EmailConnectionTestResponse | null>(null);

  const [testRecipientEmail, setTestRecipientEmail] = useState("priyer@test.com");
  const [testEmailSubject, setTestEmailSubject] = useState("UAIC Orchestrator — Live Test Notification");
  const [testEmailBody, setTestEmailBody] = useState("This is an interactive live test notification verifying the UAIC Email & Notification Engine.");
  const [isSendingTestEmail, setIsSendingTestEmail] = useState(false);
  const [testEmailResult, setTestEmailResult] = useState<TestEmailSendResponse | null>(null);

  const [newToRecipient, setNewToRecipient] = useState("");
  const [newCcRecipient, setNewCcRecipient] = useState("");
  const [newBccRecipient, setNewBccRecipient] = useState("");

  const [recentNotifications, setRecentNotifications] = useState<NotificationItem[]>([]);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);
  const [selectedReceiptNotif, setSelectedReceiptNotif] = useState<NotificationItem | null>(null);

  // Outbound Delivery History filter and pagination states
  const [historySearch, setHistorySearch] = useState("");
  const [historyStatusFilter, setHistoryStatusFilter] = useState<string>("ALL");
  const [historyEventTypeFilter, setHistoryEventTypeFilter] = useState<string>("ALL");
  const [historyPage, setHistoryPage] = useState(1);
  const [historyTotalPages, setHistoryTotalPages] = useState(1);
  const [historyTotalCount, setHistoryTotalCount] = useState(0);

  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [selectedTemplateEvent, setSelectedTemplateEvent] = useState<string>("COURT_CASE_MATCHED");
  const [selectedTemplate, setSelectedTemplate] = useState<NotificationTemplate | null>(null);
  const [tokensCatalog, setTokensCatalog] = useState<TemplateParameter[]>([]);
  const [activeEditorTab, setActiveEditorTab] = useState<"split" | "edit" | "preview">("split");
  const [previewDevice, setPreviewDevice] = useState<"desktop" | "mobile">("desktop");
  const [isTokensPaletteOpen, setIsTokensPaletteOpen] = useState<boolean>(true);
  const [copiedTemplateCode, setCopiedTemplateCode] = useState<boolean>(false);
  const [templateEditFormat, setTemplateEditFormat] = useState<"html" | "text">("html");
  const [draftSubject, setDraftSubject] = useState<string>("");
  const [draftHtml, setDraftHtml] = useState<string>("");
  const [draftText, setDraftText] = useState<string>("");
  const [templatePreviewHtml, setTemplatePreviewHtml] = useState<string>("");
  const [templatePreviewSubject, setTemplatePreviewSubject] = useState<string>("");
  const [templatePreviewText, setTemplatePreviewText] = useState<string>("");
  const [templatePreviewMode, setTemplatePreviewMode] = useState<"html" | "text">("html");
  const [isLoadingTemplatePreview, setIsLoadingTemplatePreview] = useState(false);
  const [isSavingTemplate, setIsSavingTemplate] = useState(false);
  const [isResettingTemplate, setIsResettingTemplate] = useState(false);
  const [templateSaveFeedback, setTemplateSaveFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [selectedTokenCategory, setSelectedTokenCategory] = useState<string>("All");
  const [activeFocusedField, setActiveFocusedField] = useState<"subject" | "html" | "text">("html");

  // Noise word input state
  const [newNoiseWord, setNewNoiseWord] = useState("");

  // Live Celery queue status state
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [isLoadingQueueStatus, setIsLoadingQueueStatus] = useState(false);

  const fetchQueueStatus = async () => {
    setIsLoadingQueueStatus(true);
    try {
      const qStatus = await api.getQueueStatus();
      setQueueStatus(qStatus);
    } catch {
      // gracefully keep previous status
    } finally {
      setIsLoadingQueueStatus(false);
    }
  };

  useEffect(() => {
    if (activeTab === "queue") {
      fetchQueueStatus();
    }
  }, [activeTab]);

  const fetchSettings = async () => {
    setIsLoading(true);
    try {
      const data = await api.getSettings();
      const withBranding: SystemSettings = {
        ...data,
        branding: data.branding || DEFAULT_BRANDING,
        email: data.email || DEFAULT_EMAIL_SETTINGS,
      };
      setSettings(withBranding);
    } catch (e: any) {
      setFeedback({ type: "error", msg: "Failed to load active system settings." });
    } finally {
      setIsLoading(false);
    }
  };

  const updateEmailSettings = (patch: Partial<EmailSettings>) => {
    if (!settings) return;
    const current: EmailSettings = settings.email || DEFAULT_EMAIL_SETTINGS;
    setSettings({
      ...settings,
      email: {
        ...current,
        ...patch,
      },
    });
  };

  const handleTestEmailConnection = async () => {
    if (!settings) return;
    setIsTestingEmailConnection(true);
    setEmailConnectionResult(null);
    try {
      const emailCfg = settings.email || DEFAULT_EMAIL_SETTINGS;
      const targetDomain = testRecipientEmail.includes("@")
        ? testRecipientEmail.split("@")[1].trim()
        : emailCfg.from_email.includes("@")
        ? emailCfg.from_email.split("@")[1].trim()
        : "damcogroup.com";

      const res = await api.testEmailConnection({
        provider: emailCfg.provider,
        smtp_host: emailCfg.provider === "maildev" ? (emailCfg.smtp_host || "localhost") : emailCfg.smtp_host,
        smtp_port: emailCfg.provider === "maildev" ? (emailCfg.smtp_port === 587 ? 1025 : emailCfg.smtp_port) : emailCfg.smtp_port,
        smtp_username: emailCfg.smtp_username,
        smtp_password: emailCfg.smtp_password,
        smtp_encryption: emailCfg.smtp_encryption,
        graph_tenant_id: emailCfg.graph_tenant_id,
        graph_client_id: emailCfg.graph_client_id,
        graph_client_secret: emailCfg.graph_client_secret,
        ses_region: emailCfg.ses_region,
        ses_access_key_id: emailCfg.ses_access_key_id,
        ses_secret_access_key: emailCfg.ses_secret_access_key,
        timeout_seconds: emailCfg.timeout_seconds,
        recipient_domain: targetDomain,
      });
      setEmailConnectionResult(res);
      if (res.success) {
        setFeedback({
          type: "success",
          msg: `${res.message} (${res.duration_ms}ms)`,
        });
      } else {
        setFeedback({
          type: "error",
          msg: `Email test connection failed: ${res.message}`,
        });
      }
    } catch (err: any) {
      const errRes: EmailConnectionTestResponse = {
        success: false,
        provider: settings?.email?.provider || "smtp",
        message: err?.response?.data?.detail || "Failed to reach backend email test endpoint.",
        duration_ms: 0,
        error_detail: String(err),
      };
      setEmailConnectionResult(errRes);
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Email connection test failed.",
      });
    } finally {
      setIsTestingEmailConnection(false);
    }
  };

  const handleSendTestEmail = async () => {
    if (!settings) return;
    const emailCfg = settings.email || DEFAULT_EMAIL_SETTINGS;
    const recipient =
      testRecipientEmail.trim() ||
      emailCfg.to_recipients?.[0] ||
      settings.integration?.notification_email ||
      "priyer@test.com";
    setIsSendingTestEmail(true);
    setTestEmailResult(null);
    try {
      const res = await api.sendTestEmail({
        recipient,
        subject: testEmailSubject,
        body: testEmailBody,
        provider: emailCfg.provider,
      });
      setTestEmailResult(res);
      if (res.success) {
        setFeedback({
          type: "success",
          msg: `Test notification sent to ${res.recipient}! (Status: ${res.status}, ${res.duration_ms}ms)`,
        });
        fetchRecentNotifications();
      } else {
        setFeedback({
          type: "error",
          msg: `Test email failed: ${res.message}`,
        });
      }
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to dispatch test notification email.",
      });
    } finally {
      setIsSendingTestEmail(false);
    }
  };

  const fetchRecentNotifications = async (
    targetPage?: number,
    targetStatus?: string,
    targetSearch?: string,
    targetEventType?: string
  ) => {
    setIsLoadingNotifications(true);
    const p = targetPage !== undefined ? targetPage : historyPage;
    const s = targetStatus !== undefined ? targetStatus : historyStatusFilter;
    const q = targetSearch !== undefined ? targetSearch : historySearch;
    const e = targetEventType !== undefined ? targetEventType : historyEventTypeFilter;
    try {
      const res = await api.getNotifications({
        page: p,
        page_size: 10,
        status: s !== "ALL" ? s : undefined,
        search: q.trim() ? q.trim() : undefined,
        event_type: e !== "ALL" ? e : undefined,
      });
      setRecentNotifications(res.items || []);
      setHistoryPage(res.page || p);
      setHistoryTotalPages(res.total_pages || 1);
      setHistoryTotalCount(res.total || 0);
    } catch (err) {
      console.error("FETCH_NOTIF_ERR:", err);
    } finally {
      setIsLoadingNotifications(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const [tpls, tokens] = await Promise.all([
        api.getNotificationTemplates(),
        api.getTemplateTokens(),
      ]);
      setTemplates(tpls);
      setTokensCatalog(tokens);
      if (tpls.length > 0) {
        const initialTpl = tpls.find((t) => t.event_type === selectedTemplateEvent) || tpls[0];
        selectTemplateForEditing(initialTpl);
      }
    } catch (err) {
      console.error("Failed to fetch templates:", err);
    }
  };

  useEffect(() => {
    fetchSettings();
    fetchTemplates();
    fetchRecentNotifications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectTemplateForEditing = (tpl: NotificationTemplate) => {
    setSelectedTemplate(tpl);
    setSelectedTemplateEvent(tpl.event_type);
    setDraftSubject(tpl.subject_template || "");
    setDraftHtml(tpl.body_template_html || "");
    setDraftText(tpl.body_template_text || "");
    setTemplateSaveFeedback(null);
    loadTemplatePreviewWithDraft(tpl.event_type, tpl.subject_template, tpl.body_template_html, tpl.body_template_text);
  };

  const loadTemplatePreviewWithDraft = async (
    eventType: string,
    subject?: string | null,
    html?: string | null,
    text?: string | null
  ) => {
    setIsLoadingTemplatePreview(true);
    try {
      const res = await api.previewNotificationTemplate({
        event_type: eventType,
        subject_template: subject ?? undefined,
        body_template_html: html ?? undefined,
        body_template_text: text ?? undefined,
      });
      setTemplatePreviewHtml(res.body_html || res.rendered_content || "");
      setTemplatePreviewSubject(res.subject || "");
      setTemplatePreviewText(res.body_text || "");
    } catch (err) {
      console.error("Failed to preview template:", err);
    } finally {
      setIsLoadingTemplatePreview(false);
    }
  };

  const handleInsertToken = (token: string) => {
    const placeholder = `{{${token}}}`;
    if (activeFocusedField === "subject") {
      setDraftSubject((prev) => {
        const next = prev ? `${prev} ${placeholder}` : placeholder;
        loadTemplatePreviewWithDraft(selectedTemplateEvent, next, draftHtml, draftText);
        return next;
      });
    } else if (activeFocusedField === "text" || templateEditFormat === "text") {
      setDraftText((prev) => {
        const next = prev ? `${prev} ${placeholder}` : placeholder;
        loadTemplatePreviewWithDraft(selectedTemplateEvent, draftSubject, draftHtml, next);
        return next;
      });
    } else {
      setDraftHtml((prev) => {
        const next = prev ? `${prev} ${placeholder}` : placeholder;
        loadTemplatePreviewWithDraft(selectedTemplateEvent, draftSubject, next, draftText);
        return next;
      });
    }
  };

  const handleFormatHtml = () => {
    if (!draftHtml) return;
    try {
      let formatted = "";
      let indent = 0;
      const tokens = draftHtml.replace(/>\s*</g, "><").split(/(<[^>]+>)/g).filter(Boolean);
      for (const token of tokens) {
        if (token.startsWith("</")) {
          indent = Math.max(0, indent - 1);
          formatted += "  ".repeat(indent) + token + "\n";
        } else if (
          token.startsWith("<") &&
          !token.endsWith("/>") &&
          !token.startsWith("<!") &&
          !token.startsWith("<meta") &&
          !token.startsWith("<link") &&
          !token.startsWith("<img") &&
          !token.startsWith("<br") &&
          !token.startsWith("<hr") &&
          !token.startsWith("<input")
        ) {
          formatted += "  ".repeat(indent) + token + "\n";
          indent += 1;
        } else if (token.startsWith("<")) {
          formatted += "  ".repeat(indent) + token + "\n";
        } else {
          const text = token.trim();
          if (text) {
            formatted += "  ".repeat(indent) + text + "\n";
          }
        }
      }
      const clean = formatted.trim();
      if (clean) {
        setDraftHtml(clean);
        loadTemplatePreviewWithDraft(selectedTemplateEvent, draftSubject, clean, draftText);
        setFeedback({ type: "success", msg: "HTML markup formatted and indented." });
      }
    } catch {
      // keep current html if parsing fails
    }
  };

  const handleCopyTemplateCode = () => {
    const code = templateEditFormat === "html" ? draftHtml : draftText;
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(code);
      setCopiedTemplateCode(true);
      setTimeout(() => setCopiedTemplateCode(false), 2000);
      setFeedback({ type: "success", msg: `${templateEditFormat.toUpperCase()} template copied to clipboard.` });
    }
  };

  const handleSaveTemplate = async () => {
    if (!selectedTemplate) return;
    setIsSavingTemplate(true);
    setTemplateSaveFeedback(null);
    try {
      const updated = await api.updateNotificationTemplate(selectedTemplate.event_type, {
        name: selectedTemplate.name,
        subject_template: draftSubject,
        body_template_html: draftHtml,
        body_template_text: draftText,
        is_active: true,
      });
      setSelectedTemplate(updated);
      setTemplates((prev) =>
        prev.map((t) => (t.event_type === updated.event_type ? updated : t))
      );
      setTemplateSaveFeedback({
        type: "success",
        msg: `Template for "${updated.name}" successfully saved and updated in DB!`,
      });
      loadTemplatePreviewWithDraft(updated.event_type, draftSubject, draftHtml, draftText);
    } catch (err: any) {
      setTemplateSaveFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to save template changes.",
      });
    } finally {
      setIsSavingTemplate(false);
    }
  };

  const handleResetTemplate = async () => {
    if (!selectedTemplate) return;
    if (typeof window !== "undefined" && window.confirm) {
      if (!window.confirm(`Are you sure you want to reset "${selectedTemplate.name}" to system default?`)) return;
    }
    setIsResettingTemplate(true);
    setTemplateSaveFeedback(null);
    try {
      const resetTpl = await api.resetNotificationTemplate(selectedTemplate.event_type);
      setSelectedTemplate(resetTpl);
      setDraftSubject(resetTpl.subject_template);
      setDraftHtml(resetTpl.body_template_html);
      setDraftText(resetTpl.body_template_text || "");
      setTemplates((prev) =>
        prev.map((t) => (t.event_type === resetTpl.event_type ? resetTpl : t))
      );
      setTemplateSaveFeedback({
        type: "success",
        msg: `Template "${resetTpl.name}" successfully restored to system default.`,
      });
      loadTemplatePreviewWithDraft(resetTpl.event_type, resetTpl.subject_template, resetTpl.body_template_html, resetTpl.body_template_text);
    } catch (err: any) {
      setTemplateSaveFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to reset template.",
      });
    } finally {
      setIsResettingTemplate(false);
    }
  };

  const handleAddRecipient = (type: "to" | "cc" | "bcc") => {
    if (!settings) return;
    const emailCfg = settings.email || DEFAULT_EMAIL_SETTINGS;
    let inputVal = "";
    if (type === "to") inputVal = newToRecipient.trim();
    else if (type === "cc") inputVal = newCcRecipient.trim();
    else if (type === "bcc") inputVal = newBccRecipient.trim();

    if (!inputVal || !inputVal.includes("@")) return;

    if (type === "to") {
      if (!emailCfg.to_recipients.includes(inputVal)) {
        updateEmailSettings({ to_recipients: [...emailCfg.to_recipients, inputVal] });
      }
      setNewToRecipient("");
    } else if (type === "cc") {
      if (!emailCfg.cc_recipients.includes(inputVal)) {
        updateEmailSettings({ cc_recipients: [...emailCfg.cc_recipients, inputVal] });
      }
      setNewCcRecipient("");
    } else if (type === "bcc") {
      if (!emailCfg.bcc_recipients.includes(inputVal)) {
        updateEmailSettings({ bcc_recipients: [...emailCfg.bcc_recipients, inputVal] });
      }
      setNewBccRecipient("");
    }
  };

  const handleRemoveRecipient = (type: "to" | "cc" | "bcc", index: number) => {
    if (!settings) return;
    const emailCfg = settings.email || DEFAULT_EMAIL_SETTINGS;
    if (type === "to") {
      updateEmailSettings({ to_recipients: emailCfg.to_recipients.filter((_, i) => i !== index) });
    } else if (type === "cc") {
      updateEmailSettings({ cc_recipients: emailCfg.cc_recipients.filter((_, i) => i !== index) });
    } else if (type === "bcc") {
      updateEmailSettings({ bcc_recipients: emailCfg.bcc_recipients.filter((_, i) => i !== index) });
    }
  };

  const handleToggleRule = (ruleKey: string) => {
    if (!settings) return;
    const emailCfg = settings.email || DEFAULT_EMAIL_SETTINGS;
    const currentVal = emailCfg.rules?.[ruleKey] ?? true;
    updateEmailSettings({
      rules: {
        ...emailCfg.rules,
        [ruleKey]: !currentVal,
      },
    });
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    if (activeTab === "email") {
      fetchRecentNotifications();
      fetchTemplates();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const handleSave = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!settings) return;
    setIsSaving(true);
    setFeedback(null);
    try {
      const updated = await api.updateSettings(settings);
      setSettings(updated);
      if (updated.branding) {
        updateBranding(updated.branding);
      }
      setFeedback({
        type: "success",
        msg: "System settings successfully saved and applied to all running Celery workers, scrapers, and Guidewire integration!",
      });
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to update system settings.",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async (skipConfirm = false) => {
    if (!skipConfirm && typeof window !== "undefined" && window.confirm) {
      if (!window.confirm("Are you sure you want to reset all settings to system defaults?")) return;
    }
    setIsResetting(true);
    setFeedback(null);
    try {
      const def = await api.resetSettings();
      setSettings(def);
      if (def.branding) {
        updateBranding(def.branding);
      }
      setFeedback({
        type: "success",
        msg: "All system settings successfully restored to initial defaults.",
      });
    } catch (err) {
      setFeedback({ type: "error", msg: "Failed to reset settings." });
    } finally {
      setIsResetting(false);
    }
  };

  const handleTestGuidewire = async () => {
    if (!settings) return;
    setIsTestingGuidewire(true);
    setGuidewireTestResponse(null);

    let parsedPayload: Record<string, any> | undefined;
    try {
      parsedPayload = JSON.parse(testPayloadText);
    } catch (err) {
      setFeedback({
        type: "error",
        msg: "Invalid JSON format in custom test payload editor.",
      });
      setIsTestingGuidewire(false);
      return;
    }

    try {
      const req: GuidewireTestRequest = {
        api_url: settings.integration.guidewire_api_url,
        auth_type: settings.integration.guidewire_auth_type,
        api_key: settings.integration.guidewire_api_key,
        client_id: settings.integration.guidewire_client_id,
        client_secret: settings.integration.guidewire_client_secret,
        mock_mode: settings.integration.guidewire_mock_mode,
        timeout_seconds: settings.integration.guidewire_timeout_seconds,
        custom_payload: parsedPayload,
      };
      const res = await api.testGuidewireConnection(req);
      setGuidewireTestResponse(res);
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to execute Guidewire connection test.",
      });
    } finally {
      setIsTestingGuidewire(false);
    }
  };

  const handlePingPortal = async (portalKey: string, portalName: string, url: string) => {
    setTestingPortals((prev) => ({ ...prev, [portalKey]: true }));
    try {
      const res = await api.testPortalConnection({
        portal_name: portalName,
        url,
        timeout_seconds: 12,
      });
      setPortalResults((prev) => ({ ...prev, [portalKey]: res }));
    } catch (err: any) {
      setPortalResults((prev) => ({
        ...prev,
        [portalKey]: {
          portal_name: portalName,
          url,
          reachable: false,
          status_text: "Ping failed",
          duration_ms: 0,
          error_detail: err?.message || "Network error",
        },
      }));
    } finally {
      setTestingPortals((prev) => ({ ...prev, [portalKey]: false }));
    }
  };

  const handleCopyResponse = () => {
    if (!guidewireTestResponse) return;
    navigator.clipboard.writeText(
      JSON.stringify(guidewireTestResponse.response_body, null, 2)
    );
    setCopiedResponse(true);
    setTimeout(() => setCopiedResponse(false), 2000);
  };

  const handleAddNoiseWord = () => {
    if (!newNoiseWord.trim() || !settings) return;
    const word = newNoiseWord.trim().toUpperCase();
    if (!settings.matcher.clean_party_name_patterns.includes(word)) {
      setSettings({
        ...settings,
        matcher: {
          ...settings.matcher,
          clean_party_name_patterns: [
            ...settings.matcher.clean_party_name_patterns,
            word,
          ],
        },
      });
    }
    setNewNoiseWord("");
  };

  const handleRemoveNoiseWord = (word: string) => {
    if (!settings) return;
    setSettings({
      ...settings,
      matcher: {
        ...settings.matcher,
        clean_party_name_patterns: settings.matcher.clean_party_name_patterns.filter(
          (w) => w !== word
        ),
      },
    });
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col w-full">
        <Navbar />
        <div className="p-8 text-center text-slate-500 text-xs flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-500" />
          Loading dynamic system settings...
        </div>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="flex-1 flex flex-col w-full">
        <Navbar />
        <div className="p-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center gap-3">
          <AlertCircle className="w-8 h-8 text-rose-500" />
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
            {feedback?.msg || "Failed to load dynamic system settings from backend."}
          </p>
          <button
            onClick={fetchSettings}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition inline-flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Loading Settings
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "guidewire", label: "Guidewire API & Live Tester", icon: Zap },
    { id: "portals", label: "County Court Portals", icon: Globe },
    { id: "automation", label: "Browser & CAPTCHA", icon: ShieldCheck },
    { id: "proxy", label: "Proxy Settings", icon: Network },
    { id: "extension", label: "AntiCaptcha Extension", icon: Plug },
    { id: "email", label: "Email & Notifications", icon: Mail },
    { id: "storage", label: "Storage & Error Screenshots", icon: HardDrive },
    { id: "matcher", label: "RapidFuzz & Filters", icon: Sparkles },
    { id: "queue", label: "Task Queue & Alerts", icon: Layers },
  ];

  return (
    <div className="flex-1 flex flex-col w-full">
      <Navbar onRefresh={fetchSettings} isRefreshing={isLoading} />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none flex-1 transition-colors">
        {/* Title & Save Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
              <Sliders className="w-6 h-6 text-indigo-500" />
              Unified Solution & Automation Settings
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Fully manage Guidewire integration, county scraper endpoints, CAPTCHA retry loops, and RapidFuzz confidence cutoffs in real time.
            </p>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap sm:flex-nowrap w-full sm:w-auto">
            <button
              type="button"
              onClick={() => handleReset()}
              disabled={isResetting}
              className="flex-1 sm:flex-initial px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 shadow-xs min-h-[40px]"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
              <span>Reset Defaults</span>
            </button>
            <button
              type="button"
              onClick={() => handleSave()}
              disabled={isSaving}
              className="flex-1 sm:flex-initial px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 min-h-[40px]"
            >
              <Save className={`w-3.5 h-3.5 ${isSaving ? "animate-spin" : ""}`} />
              <span>{isSaving ? "Saving..." : "Save Configuration"}</span>
            </button>
          </div>
        </div>

        {/* Feedback Alert */}
        {feedback && (
          <div
            className={`rounded-xl p-3.5 sm:p-4 text-xs flex items-center justify-between gap-2.5 border w-full max-w-full overflow-hidden ${
              feedback.type === "success"
                ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300"
                : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/60 text-rose-800 dark:text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2.5 min-w-0 flex-1">
              {feedback.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
              )}
              <span className="min-w-0 break-words flex-1">{feedback.msg}</span>
            </div>
            <button
              type="button"
              onClick={() => setFeedback(null)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 shrink-0 rounded transition-colors cursor-pointer"
              title="Dismiss"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 overflow-x-auto no-scrollbar pb-px w-full flex-nowrap gap-2">
          <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar flex-nowrap">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as SettingsTab)}
                  className={`flex items-center gap-2 px-3.5 sm:px-4 py-2.5 text-xs font-semibold border-b-2 transition-all whitespace-nowrap cursor-pointer min-h-[40px] shrink-0 ${
                    isActive
                      ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-950/30 rounded-t-lg"
                      : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-700"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* ========================================================= */}
        {/* TAB 1: GUIDEWIRE API & SWAGGER TESTER                    */}
        {/* ========================================================= */}
        {activeTab === "guidewire" && (
          <div className="space-y-6 w-full">
            {/* Guidewire Configuration Card */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-indigo-500" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                      Guidewire ClaimCenter Integration API
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Configure downstream REST case update notifications, authentication tokens, and simulation parameters.
                    </p>
                  </div>
                </div>

                {/* Mock Mode Switch */}
                <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                    Mock Simulation Mode:
                  </span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.integration.guidewire_mock_mode}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          integration: {
                            ...settings.integration,
                            guidewire_mock_mode: e.target.checked,
                          },
                        })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-slate-300 dark:bg-slate-700 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500"></div>
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
                {/* Endpoint URL */}
                <div className="sm:col-span-2 space-y-1.5">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Guidewire Case Update Endpoint URL
                  </label>
                  <input
                    type="url"
                    value={settings.integration.guidewire_api_url}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          guidewire_api_url: e.target.value,
                        },
                      })
                    }
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                    placeholder="https://api.guidewire.example.com/cc/rest/v1/caseupdate"
                  />
                </div>

                {/* Auth Type */}
                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Authentication Type
                  </label>
                  <select
                    value={settings.integration.guidewire_auth_type}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          guidewire_auth_type: e.target.value,
                        },
                      })
                    }
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  >
                    <option value="Bearer">Bearer Token (Authorization: Bearer ...)</option>
                    <option value="ApiKey">API Key Header (X-API-Key: ...)</option>
                    <option value="Basic">HTTP Basic Auth (Client ID & Secret)</option>
                    <option value="OAuth2">OAuth2 Client Credentials</option>
                    <option value="None">None (Unauthenticated)</option>
                  </select>
                </div>

                {/* API Key / Token */}
                {(settings.integration.guidewire_auth_type === "Bearer" ||
                  settings.integration.guidewire_auth_type === "ApiKey" ||
                  settings.integration.guidewire_auth_type === "OAuth2") && (
                  <div className="sm:col-span-2 space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      API Key / Bearer Secret Token
                    </label>
                    <div className="relative w-full">
                      <input
                        type={showApiKey ? "text" : "password"}
                        value={settings.integration.guidewire_api_key}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            integration: {
                              ...settings.integration,
                              guidewire_api_key: e.target.value,
                            },
                          })
                        }
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                        placeholder="e.g. gw_live_sec_9938172648"
                      />
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                      >
                        {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                )}

                {/* Basic Auth fields */}
                {settings.integration.guidewire_auth_type === "Basic" && (
                  <>
                    <div className="space-y-1.5">
                      <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                        Basic Auth Client ID / Username
                      </label>
                      <input
                        type="text"
                        value={settings.integration.guidewire_client_id}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            integration: {
                              ...settings.integration,
                              guidewire_client_id: e.target.value,
                            },
                          })
                        }
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                        Basic Auth Client Secret / Password
                      </label>
                      <div className="relative w-full">
                        <input
                          type={showClientSecret ? "text" : "password"}
                          value={settings.integration.guidewire_client_secret}
                          onChange={(e) =>
                            setSettings({
                              ...settings,
                              integration: {
                                ...settings.integration,
                                guidewire_client_secret: e.target.value,
                              },
                            })
                          }
                          className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                        />
                        <button
                          type="button"
                          onClick={() => setShowClientSecret(!showClientSecret)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                        >
                          {showClientSecret ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>
                  </>
                )}

                {/* Timeout */}
                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    HTTP Request Timeout (Seconds)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="120"
                    value={settings.integration.guidewire_timeout_seconds}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          guidewire_timeout_seconds: parseInt(e.target.value) || 30,
                        },
                      })
                    }
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                </div>

                {/* Auto Push Toggle */}
                <div className="sm:col-span-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-200 block">
                      Automatic Downstream Dispatch on High-Confidence Matches
                    </span>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      When enabled, claims with fuzzy match score &ge; Auto-Match Threshold are instantly posted to Guidewire without waiting for manual approval.
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.integration.auto_push_on_match}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          integration: {
                            ...settings.integration,
                            auto_push_on_match: e.target.checked,
                          },
                        })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-300 dark:bg-slate-800 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
              </div>
            </div>

            {/* Swagger / Postman Live Interactive Connection Tester */}
            <div className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 rounded-2xl p-6 md:p-8 space-y-6 shadow-xl border border-slate-200 dark:border-slate-800 w-full transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
                <div className="flex items-center gap-2.5">
                  <Terminal className="w-5 h-5 text-emerald-500" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      Interactive Guidewire API Tester & Response Explorer
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Test live endpoint connectivity, authentication tokens, and inspect raw HTTP request/response payloads in real time (like Swagger UI / Postman).
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleTestGuidewire}
                  disabled={isTestingGuidewire}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-2 cursor-pointer whitespace-nowrap self-start sm:self-auto"
                >
                  <Send className={`w-3.5 h-3.5 ${isTestingGuidewire ? "animate-spin" : ""}`} />
                  {isTestingGuidewire ? "Executing Request..." : "Test Connection / Send Request"}
                </button>
              </div>

              {/* Request URL Bar */}
              <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-2 font-mono text-xs overflow-x-auto">
                <span className="px-2.5 py-1 bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800 font-bold rounded text-[10px]">
                  POST
                </span>
                <span className="text-slate-700 dark:text-slate-300 truncate">
                  {settings.integration.guidewire_api_url}
                </span>
                <span className="ml-auto text-[10px] text-slate-400 whitespace-nowrap">
                  Mode: {settings.integration.guidewire_mock_mode ? "MOCK" : "LIVE"}
                </span>
              </div>

              {/* Request Body Editor */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    Request JSON Body (Edit test payload if desired):
                  </span>
                </div>
                <textarea
                  rows={6}
                  value={testPayloadText}
                  onChange={(e) => setTestPayloadText(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-xs text-emerald-600 dark:text-emerald-400 font-mono focus:outline-hidden focus:border-emerald-500"
                />
              </div>

              {/* Live Response Inspector */}
              {guidewireTestResponse && (
                <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800 animate-fadeIn">
                  {/* Status Bar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
                          guidewireTestResponse.success
                            ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800"
                            : "bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-400 border-rose-300 dark:border-rose-800"
                        }`}
                      >
                        {guidewireTestResponse.status_text}
                      </span>
                      <span className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-sky-500" />
                        Latency: <strong className="text-slate-900 dark:text-white">{guidewireTestResponse.duration_ms} ms</strong>
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={handleCopyResponse}
                      className="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 font-mono transition-colors cursor-pointer"
                    >
                      {copiedResponse ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-500" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          Copy JSON
                        </>
                      )}
                    </button>
                  </div>

                  {/* Formatted JSON Body Output */}
                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">Response Payload:</span>
                    <pre className="bg-slate-900 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-xs font-mono text-sky-300 overflow-x-auto max-h-80">
                      {JSON.stringify(guidewireTestResponse.response_body, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 2: COUNTY COURT SCRAPER PORTALS                      */}
        {/* ========================================================= */}
        {activeTab === "portals" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <Globe className="w-5 h-5 text-indigo-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  Public County Court Scraper Portals & Health Pings
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Configure search URLs, active scraper dispatch switches, and ping endpoints for live portal reachability.
                </p>
              </div>
            </div>

            {/* Portal Cards */}
            <div className="space-y-4 w-full">
              {[
                {
                  key: "broward",
                  state: "FL",
                  name: "Broward County Clerk of Courts",
                  urlKey: "broward_url",
                  enabledKey: "broward_enabled",
                },
                {
                  key: "hillsborough",
                  state: "FL",
                  name: "Hillsborough County Clerk (HOVER Search)",
                  urlKey: "hillsborough_url",
                  enabledKey: "hillsborough_enabled",
                },
                {
                  key: "miami",
                  state: "FL",
                  name: "Miami-Dade County Clerk (OCS Portal)",
                  urlKey: "miami_url",
                  enabledKey: "miami_enabled",
                },
                {
                  key: "travis",
                  state: "TX",
                  name: "Travis County Odyssey Portal",
                  urlKey: "travis_url",
                  enabledKey: "travis_enabled",
                },
                {
                  key: "dallas",
                  state: "TX",
                  name: "Dallas County Courts Portal",
                  urlKey: "dallas_url",
                  enabledKey: "dallas_enabled",
                },
                {
                  key: "harris_jp",
                  state: "TX",
                  name: "Harris County Justice of the Peace (JP)",
                  urlKey: "harris_jp_url",
                  enabledKey: "harris_jp_enabled",
                },
                {
                  key: "harris_cclerk",
                  state: "TX",
                  name: "Harris County Clerk WebSearch",
                  urlKey: "harris_cclerk_url",
                  enabledKey: "harris_cclerk_enabled",
                },
                {
                  key: "harris_district",
                  state: "TX",
                  name: "Harris County District Clerk (eDocs Search)",
                  urlKey: "harris_district_url",
                  enabledKey: "harris_district_enabled",
                },
              ].map((portal) => {
                const isEnabled = (settings.portals as any)[portal.enabledKey];
                const currentUrl = (settings.portals as any)[portal.urlKey];
                const isPinging = testingPortals[portal.key];
                const result = portalResults[portal.key];

                return (
                  <div
                    key={portal.key}
                    className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-3 transition-colors"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800/60 pb-2.5">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded font-mono text-[10px] font-bold">
                          {portal.state}
                        </span>
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                          {portal.name}
                        </span>
                      </div>

                      <div className="flex items-center gap-3">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={isEnabled}
                            onChange={(e) =>
                              setSettings({
                                ...settings,
                                portals: {
                                  ...settings.portals,
                                  [portal.enabledKey]: e.target.checked,
                                },
                              })
                            }
                            className="sr-only peer"
                          />
                          <div className="w-9 h-5 bg-slate-300 dark:bg-slate-700 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                        <span className="text-[11px] font-medium text-slate-500">
                          {isEnabled ? "Enabled" : "Disabled"}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                      <input
                        type="url"
                        value={currentUrl}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            portals: {
                              ...settings.portals,
                              [portal.urlKey]: e.target.value,
                            },
                          })
                        }
                        className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 font-mono focus:outline-hidden focus:border-indigo-500"
                      />

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handlePingPortal(portal.key, portal.name, currentUrl)}
                          disabled={isPinging}
                          className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 whitespace-nowrap shadow-xs"
                        >
                          <Radio className={`w-3.5 h-3.5 text-indigo-500 ${isPinging ? "animate-spin" : ""}`} />
                          {isPinging ? "Pinging..." : "Ping Portal"}
                        </button>

                        <a
                          href={currentUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors cursor-pointer"
                          title="Open portal in new tab"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </div>
                    </div>

                    {/* Ping Result Pill */}
                    {result && (
                      <div className="flex items-center gap-2 pt-1 text-xs">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                            result.reachable
                              ? "bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800"
                              : "bg-rose-50 dark:bg-rose-950 text-rose-700 dark:text-rose-400 border-rose-300 dark:border-rose-800"
                          }`}
                        >
                          {result.status_text}
                        </span>
                        <span className="text-[11px] text-slate-500 font-mono">
                          Duration: {result.duration_ms} ms
                        </span>
                        {result.error_detail && (
                          <span className="text-[11px] text-rose-500">
                            ({result.error_detail})
                          </span>
                        )}
                      </div>
                    )}

                    {/* Miami-Dade Specific Credentials */}
                    {portal.key === "miami" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 mt-2 border-t border-slate-200 dark:border-slate-800/60">
                        <div className="space-y-1.5">
                          <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                            Portal Username / Email
                          </label>
                          <input
                            type="text"
                            value={settings.portals.miami_username || ""}
                            onChange={(e) =>
                              setSettings({
                                ...settings,
                                portals: { ...settings.portals, miami_username: e.target.value },
                              })
                            }
                            className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                          />
                        </div>
                        <div className="space-y-1.5">
                          <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                            Portal Password
                          </label>
                          <div className="relative">
                            <input
                              type={showMiamiPassword ? "text" : "password"}
                              value={settings.portals.miami_password || ""}
                              onChange={(e) =>
                                setSettings({
                                  ...settings,
                                  portals: { ...settings.portals, miami_password: e.target.value },
                                })
                              }
                              className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 pr-10 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                            />
                            <button
                              type="button"
                              onClick={() => setShowMiamiPassword(!showMiamiPassword)}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                            >
                              {showMiamiPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 3: BROWSER & CAPTCHA RETRY CONTROLS                   */}
        {/* ========================================================= */}
        {activeTab === "automation" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <ShieldCheck className="w-5 h-5 text-amber-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  CAPTCHA Auto-Click & 5-Attempt Refresh Loop Controls
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Control multi-vendor challenge auto-detection, page refresh retries, and browser execution mode.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
              {/* Max CAPTCHA Attempts */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Max Retry & Refresh Attempts
                  </label>
                  <span className="font-mono text-xs font-bold text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800/60 px-2 py-0.5 rounded-md">
                    {settings.automation.max_captcha_attempts} Attempts
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="20"
                  step="1"
                  value={settings.automation.max_captcha_attempts}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        max_captcha_attempts: parseInt(e.target.value) || 1,
                      },
                    })
                  }
                  className="w-full accent-amber-500 cursor-pointer"
                />
                <p className="text-[10px] text-slate-500 dark:text-slate-400">
                  Attempts to click CAPTCHA checkbox, wait for token resolution, reload page on error, before gracefully skipping the portal.
                </p>
              </div>

              {/* CAPTCHA Wait Duration */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    CAPTCHA Resolution Wait (Seconds)
                  </label>
                  <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-200">
                    {settings.automation.captcha_wait_seconds}s
                  </span>
                </div>
                <input
                  type="number"
                  min="3"
                  max="60"
                  value={settings.automation.captcha_wait_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        captcha_wait_seconds: parseInt(e.target.value) || 5,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Page Timeout */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Portal Navigation Timeout (Seconds)
                  </label>
                  <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-200">
                    {settings.automation.page_timeout_seconds}s
                  </span>
                </div>
                <input
                  type="number"
                  min="5"
                  max="180"
                  value={settings.automation.page_timeout_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        page_timeout_seconds: parseInt(e.target.value) || 10,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Page Reload Backoff Delay */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Page Reload Backoff Delay (Seconds)
                  </label>
                  <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-200">
                    {settings.automation.reload_backoff_seconds}s
                  </span>
                </div>
                <input
                  type="number"
                  min="0"
                  max="30"
                  value={settings.automation.reload_backoff_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        reload_backoff_seconds: parseInt(e.target.value) || 0,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Concurrent RPA Claim Executions (1 to 10 Parallel Claims) */}
              <div className="sm:col-span-2 p-4 rounded-xl border border-indigo-200/60 dark:border-indigo-900/40 bg-indigo-50/40 dark:bg-indigo-950/20 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-indigo-600/10 text-indigo-600 dark:text-indigo-400 font-bold text-xs uppercase tracking-wider">
                        Parallel RPA Concurrency
                      </span>
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Concurrent Scraper Worker Fleet (1 – 10 Parallel Claims)
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                      Controls how many court portal scrapers and claims execute concurrently in parallel. 1 = Sequential FIFO execution; 2–10 = High-throughput multi-worker fleet.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 dark:text-slate-400">Current Fleet:</span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white shadow-xs">
                      {settings.automation.max_concurrent_claims || 3}x Parallel Workers
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center pt-1">
                  <div className="space-y-1">
                    <div className="flex justify-between text-[11px] font-medium text-slate-600 dark:text-slate-400">
                      <span>1 (Sequential)</span>
                      <span>3 (Standard)</span>
                      <span>5 (Turbo)</span>
                      <span>10 (Max Parallel)</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      step="1"
                      value={settings.automation.max_concurrent_claims || 3}
                      onChange={(e) => {
                        const val = Math.max(1, Math.min(10, parseInt(e.target.value) || 3));
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            max_concurrent_claims: val,
                          },
                          queue: {
                            ...settings.queue,
                            max_concurrent_claims: val,
                          },
                        });
                      }}
                      className="w-full accent-indigo-600 cursor-pointer h-2 bg-slate-200 dark:bg-slate-700 rounded-lg"
                    />
                  </div>

                  {/* Preset quick buttons */}
                  <div className="flex flex-wrap items-center gap-1.5 justify-start sm:justify-end">
                    {[
                      { label: "1x (FIFO)", val: 1 },
                      { label: "2x (Dual)", val: 2 },
                      { label: "3x (Standard)", val: 3 },
                      { label: "5x (Turbo)", val: 5 },
                      { label: "10x (Max)", val: 10 },
                    ].map((preset) => {
                      const isActive = (settings.automation.max_concurrent_claims || 3) === preset.val;
                      return (
                        <button
                          key={preset.val}
                          type="button"
                          onClick={() => {
                            setSettings({
                              ...settings,
                              automation: {
                                ...settings.automation,
                                max_concurrent_claims: preset.val,
                              },
                              queue: {
                                ...settings.queue,
                                max_concurrent_claims: preset.val,
                              },
                            });
                          }}
                          className={`px-2.5 py-1 text-[11px] font-semibold rounded-md border transition-all cursor-pointer ${
                            isActive
                              ? "bg-indigo-600 text-white border-indigo-600 shadow-xs ring-1 ring-indigo-500"
                              : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800"
                          }`}
                        >
                          {preset.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* User Agent */}
              <div className="sm:col-span-2 space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Browser User-Agent String
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      const eng = (settings.automation.browser_engine || "chromium") as keyof typeof ENGINE_USER_AGENTS;
                      const targetUa = ENGINE_USER_AGENTS[eng] || ENGINE_USER_AGENTS.chromium;
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          user_agent: targetUa,
                        },
                      });
                      setFeedback({
                        type: "success",
                        msg: `Synchronized User-Agent to ${eng.toUpperCase()} default string.`,
                      });
                    }}
                    className="text-[10px] text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-semibold flex items-center gap-1 cursor-pointer transition-colors"
                  >
                    <RefreshCw className="w-3 h-3" /> Auto-Sync to {(settings.automation.browser_engine || "chromium").toUpperCase()}
                  </button>
                </div>
                <input
                  type="text"
                  value={settings.automation.user_agent || ""}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        user_agent: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
              </div>

              {/* Always Use Google Chrome Browser */}
              <div className="sm:col-span-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex items-center justify-between">
                <div className="space-y-0.5">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-200 block">
                    Always Launch in Google Chrome Browser
                  </span>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Launches installed Google Chrome with support for Chrome extensions (e.g. AntiCaptcha solver).
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.automation.use_chrome_browser !== false}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          use_chrome_browser: e.target.checked,
                        },
                      })
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 dark:bg-slate-800 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              {/* Browser Automation Engine Selector */}
              <div className="sm:col-span-2 space-y-2 p-4 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <label className="font-semibold text-slate-800 dark:text-slate-200 text-xs block">
                    Browser Automation Engine
                  </label>
                  <span className="text-[10px] text-indigo-600 dark:text-indigo-400 font-semibold bg-indigo-50 dark:bg-indigo-950/50 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800">
                    Extension Compatibility Core
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Select which browser runtime powers court portal automation and anti-captcha solving.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                  {/* Option 1: Chromium */}
                  <label
                    className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                      (settings.automation.browser_engine || "chromium") === "chromium"
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="browser_engine"
                      value="chromium"
                      checked={(settings.automation.browser_engine || "chromium") === "chromium"}
                      onChange={() => {
                        const currentUa = settings.automation.user_agent || "";
                        const isDefaultUa = Object.values(ENGINE_USER_AGENTS).includes(currentUa) || !currentUa;
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            browser_engine: "chromium",
                            user_agent: isDefaultUa ? ENGINE_USER_AGENTS.chromium : currentUa,
                          },
                        });
                      }}
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                        Chromium
                      </span>
                      <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                        Recommended
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
                      Full visible GUI or Headless. 100% AntiCaptcha extension & service worker support with no enterprise restrictions.
                    </p>
                  </label>

                  {/* Option 2: Google Chrome */}
                  <label
                    className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                      settings.automation.browser_engine === "chrome"
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="browser_engine"
                      value="chrome"
                      checked={settings.automation.browser_engine === "chrome"}
                      onChange={() => {
                        const currentUa = settings.automation.user_agent || "";
                        const isDefaultUa = Object.values(ENGINE_USER_AGENTS).includes(currentUa) || !currentUa;
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            browser_engine: "chrome",
                            user_agent: isDefaultUa ? ENGINE_USER_AGENTS.chrome : currentUa,
                          },
                        });
                      }}
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Google Chrome
                      </span>
                      <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                        Host Binary (Dev Mode)
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
                      Uses installed Google Chrome with your Developer Mode profile & AntiCaptcha extension.
                    </p>
                  </label>

                  {/* Option 3: Microsoft Edge */}
                  <label
                    className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                      settings.automation.browser_engine === "msedge"
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="browser_engine"
                      value="msedge"
                      checked={settings.automation.browser_engine === "msedge"}
                      onChange={() => {
                        const currentUa = settings.automation.user_agent || "";
                        const isDefaultUa = Object.values(ENGINE_USER_AGENTS).includes(currentUa) || !currentUa;
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            browser_engine: "msedge",
                            user_agent: isDefaultUa ? ENGINE_USER_AGENTS.msedge : currentUa,
                          },
                        });
                      }}
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Microsoft Edge
                      </span>
                      <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                        Edge Channel
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
                      Uses installed Microsoft Edge. Compatible with Chromium extension flags and background workers.
                    </p>
                  </label>
                </div>
              </div>

              {/* Google Chrome Executable Binary Path */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Google Chrome Executable Location
                  </label>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">
                    Windows Default Auto-Detected
                  </span>
                </div>
                <input
                  type="text"
                  placeholder="e.g. C:\Program Files\Google\Chrome\Application\chrome.exe"
                  value={settings.automation.chrome_binary_path || ""}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        chrome_binary_path: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Standard Windows path: <code className="text-slate-700 dark:text-slate-300 font-mono">C:\Program Files\Google\Chrome\Application\chrome.exe</code>. Used when Google Chrome engine is selected.
                </p>
              </div>

              {/* AntiCaptcha Extension Directory Path */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    AntiCaptcha / Chrome Extension Path
                  </label>
                  <span className="text-[10px] text-indigo-600 dark:text-indigo-400 font-semibold bg-indigo-50 dark:bg-indigo-950/50 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800">
                    Default: .\anticaptcha-plugin_v0.83\
                  </span>
                </div>
                <input
                  type="text"
                  placeholder=".\anticaptcha-plugin_v0.83\"
                  value={settings.automation.chrome_extension_dir || ""}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        chrome_extension_dir: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Default relative path: <code className="text-slate-700 dark:text-slate-300 font-mono">.\anticaptcha-plugin_v0.83\</code> automatically adapts to solution folder renames or moves. Complete path only required for custom external directories.
                </p>
              </div>

              {/* AntiCaptcha API Key */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  AntiCaptcha API Key (For Auto-Solving)
                </label>
                <div className="relative w-full">
                  <input
                    type={showApiKey ? "text" : "password"}
                    placeholder="Enter your AntiCaptcha Client Key"
                    value={settings.automation.anticaptcha_api_key || ""}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          anticaptcha_api_key: e.target.value,
                        },
                      })
                    }
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                  >
                    {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* AntiCaptcha API Key Balance Test */}
              <div className="sm:col-span-2 bg-indigo-50 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-800/60 rounded-2xl p-4 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                      <ShieldCheck className="w-3.5 h-3.5 text-indigo-500" />
                      Test API Key — Verify Balance &amp; Connectivity
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Validates the AntiCaptcha API key by calling the live getBalance endpoint. Shows account credit balance and latency.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={handleTestAntiCaptchaBalance}
                    disabled={isTestingAntiCaptchaBalance}
                    className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50 shrink-0"
                  >
                    {isTestingAntiCaptchaBalance ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <ShieldCheck className="w-3.5 h-3.5" />
                    )}
                    Test API Key Balance
                  </button>
                </div>
                {antiCaptchaBalanceResult && (
                  <div className={`rounded-xl p-3 text-xs border space-y-1 ${
                    antiCaptchaBalanceResult.status === "ok"
                      ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                      : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"
                  }`}>
                    <div className="flex items-center gap-2 font-bold">
                      {antiCaptchaBalanceResult.status === "ok" ? (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5" />
                      )}
                      {antiCaptchaBalanceResult.message}
                    </div>
                    {antiCaptchaBalanceResult.status === "ok" && antiCaptchaBalanceResult.balance != null && (
                      <div className="font-mono text-emerald-700 dark:text-emerald-400">
                        Account Balance: <strong>${antiCaptchaBalanceResult.balance.toFixed(4)}</strong>
                      </div>
                    )}
                    <div className="text-[10px] opacity-70 font-mono">
                      Latency: {antiCaptchaBalanceResult.latency_ms.toFixed(0)}ms
                      {antiCaptchaBalanceResult.error_code && ` • Error: ${antiCaptchaBalanceResult.error_code}`}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Chrome User Profile Directory (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. C:\Users\user\AppData\Local\Google\Chrome\User Data"
                  value={settings.automation.chrome_user_data_dir || ""}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        chrome_user_data_dir: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
              </div>

              {/* AntiCaptcha Extension Diagnostics Card */}
              <div className="sm:col-span-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                      <ShieldCheck className="w-4 h-4 text-emerald-500" />
                      Anti-Captcha Browser Extension Diagnostics &amp; Engine Status
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Inspect extension directory integrity, runtime credentials sync, and browser engine compatibility.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={handleValidateExtension}
                    disabled={isValidatingExtension}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50"
                  >
                    {isValidatingExtension ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    )}
                    Check Extension Health
                  </button>
                </div>

                {/* Validation Results Grid */}
                {extensionValidationResult ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-1">
                        <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">Plugin Directory</span>
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800 dark:text-slate-200">
                          {extensionValidationResult.directory_exists ? (
                            <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Found on Disk
                            </span>
                          ) : (
                            <span className="text-rose-600 dark:text-rose-400 flex items-center gap-1">
                              <AlertCircle className="w-3.5 h-3.5" /> Directory Missing
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] font-mono text-slate-400 truncate" title={extensionValidationResult.extension_dir}>
                          {extensionValidationResult.extension_dir}
                        </p>
                      </div>

                      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-1">
                        <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">Manifest &amp; Version</span>
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800 dark:text-slate-200">
                          {extensionValidationResult.manifest_valid ? (
                            <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Manifest V3 Valid
                            </span>
                          ) : (
                            <span className="text-rose-600 dark:text-rose-400 flex items-center gap-1">
                              <AlertCircle className="w-3.5 h-3.5" /> Missing manifest.json
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] text-slate-400">
                          v0.83 (Turnstile &amp; reCAPTCHA)
                        </p>
                      </div>

                      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-1">
                        <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">Credentials State</span>
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800 dark:text-slate-200">
                          {extensionValidationResult.api_key_synced ? (
                            <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> API Key Synchronized
                            </span>
                          ) : (
                            <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1">
                              <AlertTriangle className="w-3.5 h-3.5" /> Not Synchronized
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] text-slate-400">
                          config_ac_api_key.js configured
                        </p>
                      </div>
                    </div>

                    {/* Engine Support Breakdown */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 space-y-2">
                      <span className="text-[11px] font-bold text-slate-700 dark:text-slate-300">
                        Browser Engine Extension Support &amp; Policy Status:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                        <div className="p-2.5 rounded-lg border border-emerald-200 dark:border-emerald-800/60 bg-emerald-50/50 dark:bg-emerald-950/20 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-emerald-800 dark:text-emerald-300">Chromium</span>
                            <span className="text-[10px] bg-emerald-600 text-white font-bold px-1.5 py-0.5 rounded">Active</span>
                          </div>
                          <p className="text-[10px] text-emerald-700 dark:text-emerald-400">
                            Playwright bundled engine. Full unpacked extension support without enterprise policy restrictions.
                          </p>
                        </div>

                        <div className="p-2.5 rounded-lg border border-blue-200 dark:border-blue-800/60 bg-blue-50/50 dark:bg-blue-950/20 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-blue-800 dark:text-blue-300">Microsoft Edge</span>
                            <span className="text-[10px] bg-blue-600 text-white font-bold px-1.5 py-0.5 rounded">Verified</span>
                          </div>
                          <p className="text-[10px] text-blue-700 dark:text-blue-400">
                            Edge browser channel. Loads extension with verified active service workers.
                          </p>
                        </div>

                        <div className="p-2.5 rounded-lg border border-amber-200 dark:border-amber-800/60 bg-amber-50/50 dark:bg-amber-950/20 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-amber-800 dark:text-amber-300">Google Chrome</span>
                            <span className="text-[10px] bg-amber-600 text-white font-bold px-1.5 py-0.5 rounded">Managed</span>
                          </div>
                          <p className="text-[10px] text-amber-700 dark:text-amber-400">
                            Enterprise-managed Chrome blocks command-line sideloading. Orchestrator auto-falls back to Chromium.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Click &ldquo;Check Extension Health&rdquo; to test local plugin paths, check API key synchronization, and verify browser engine extension policies.
                  </p>
                )}
              </div>

              {/* Browser Execution Mode Interactive Card & Live Tester */}
              <div className="sm:col-span-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                      <Monitor className="w-4 h-4 text-indigo-500" />
                      Browser Execution Mode & Runtime Environment
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Select how Google Chrome executes county court portal scrapers and automated CAPTCHA workflows.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
                        !settings.automation.headless_mode
                          ? "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20"
                          : "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20"
                      }`}
                    >
                      Active: {!settings.automation.headless_mode ? "Attended (Visible GUI)" : "Headless (Background)"}
                    </span>
                  </div>
                </div>

                {/* Dual Mode Selector Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {/* Option 1: Attended Mode */}
                  <div
                    onClick={() =>
                      setSettings({
                        ...settings,
                        automation: { ...settings.automation, headless_mode: false },
                      })
                    }
                    className={`relative p-4 rounded-xl border cursor-pointer transition-all ${
                      !settings.automation.headless_mode
                        ? "border-purple-500/60 bg-purple-50/50 dark:bg-purple-950/20 shadow-xs ring-1 ring-purple-500/30"
                        : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/40"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            !settings.automation.headless_mode
                              ? "bg-purple-600 text-white"
                              : "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                          }`}
                        >
                          <Eye className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-slate-200 flex items-center gap-1.5">
                            Attended (Visible GUI)
                            {!settings.automation.headless_mode && (
                              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-purple-600 text-white">
                                Selected
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] text-purple-600 dark:text-purple-400 font-medium">
                            Real Desktop Window • Operator Visible
                          </span>
                        </div>
                      </div>
                      <div
                        className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          !settings.automation.headless_mode
                            ? "border-purple-600 bg-purple-600 text-white"
                            : "border-slate-300 dark:border-slate-700"
                        }`}
                      >
                        {!settings.automation.headless_mode && <Check className="w-2.5 h-2.5 stroke-3" />}
                      </div>
                    </div>
                    <p className="mt-2.5 text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                      Google Chrome opens visibly on your desktop maximized. Operators can observe portal queries in real-time, inspect page structures, and manually solve or oversee CAPTCHA challenges when required.
                    </p>
                    {!settings.automation.headless_mode && (
                      <div className="mt-3 p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 text-[10px] text-amber-800 dark:text-amber-300 leading-relaxed space-y-1">
                        <div className="font-bold flex items-center gap-1.5">
                          <svg className="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                          </svg>
                          ⚠️ Windows Desktop Session Required
                        </div>
                        <p>The Celery worker <strong>must be started from your own desktop terminal</strong> (not an IDE or background service) for Chrome windows to appear on screen.</p>
                        <p>Open a new <strong>PowerShell/CMD window on your desktop</strong>, navigate to the <code className="bg-amber-100 dark:bg-amber-900/60 px-1 rounded font-mono">backend/</code> folder and run:</p>
                        <code className="block mt-1 p-1.5 bg-amber-100 dark:bg-amber-900/60 rounded font-mono text-[9px] break-all">
                          .\.venv\Scripts\python.exe -m celery -A app.core.celery_app.celery_app worker -E --loglevel=info -Q ingest,scrapers,matcher,notifications,default -P solo
                        </code>
                        <p className="text-[9px] text-amber-700 dark:text-amber-400">This ensures the browser runs in your interactive desktop session (WinSta0) where windows are rendered.</p>
                      </div>
                    )}
                  </div>

                  {/* Option 2: Headless Mode */}
                  <div
                    onClick={() =>
                      setSettings({
                        ...settings,
                        automation: { ...settings.automation, headless_mode: true },
                      })
                    }
                    className={`relative p-4 rounded-xl border cursor-pointer transition-all ${
                      settings.automation.headless_mode
                        ? "border-sky-500/60 bg-sky-50/50 dark:bg-sky-950/20 shadow-xs ring-1 ring-sky-500/30"
                        : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/40"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            settings.automation.headless_mode
                              ? "bg-sky-600 text-white"
                              : "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                          }`}
                        >
                          <EyeOff className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-slate-200 flex items-center gap-1.5">
                            Headless (Background)
                            {settings.automation.headless_mode && (
                              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-sky-600 text-white">
                                Selected
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] text-sky-600 dark:text-sky-400 font-medium">
                            Silent Execution • Server Production Mode
                          </span>
                        </div>
                      </div>
                      <div
                        className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          settings.automation.headless_mode
                            ? "border-sky-600 bg-sky-600 text-white"
                            : "border-slate-300 dark:border-slate-700"
                        }`}
                      >
                        {settings.automation.headless_mode && <Check className="w-2.5 h-2.5 stroke-3" />}
                      </div>
                    </div>
                    <p className="mt-2.5 text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                      Chromium executes silently in the background with modern <code className="text-[10px] bg-slate-200 dark:bg-slate-800 px-1 py-0.5 rounded font-mono">--headless=new</code> and the AntiCaptcha extension active. No browser windows steal desktop focus.
                    </p>
                  </div>
                </div>

                {/* Live Browser Test Actions */}
                <div className="pt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-200 dark:border-slate-800/60">
                  <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                    <Zap className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                    <span className="leading-snug">
                      Validate browser launch, AntiCaptcha extension, and portal navigation in{" "}
                      <strong className="text-slate-700 dark:text-slate-300">
                        {!settings.automation.headless_mode ? "Attended (Visible GUI)" : "Headless (Background)"}
                      </strong>{" "}
                      mode:
                    </span>
                  </div>
                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    <button
                      type="button"
                      disabled={isTestingBrowser}
                      onClick={() => handleTestBrowser(settings.automation.headless_mode)}
                      className={`w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg flex items-center justify-center gap-2 shadow-xs transition-all cursor-pointer ${
                        !settings.automation.headless_mode
                          ? "bg-purple-600 hover:bg-purple-500 text-white disabled:bg-purple-800 shadow-purple-600/20"
                          : "bg-sky-600 hover:bg-sky-500 text-white disabled:bg-sky-800 shadow-sky-600/20"
                      }`}
                    >
                      {isTestingBrowser ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Testing {!settings.automation.headless_mode ? "Attended GUI" : "Headless Mode"}...</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5 fill-current" />
                          <span>Test {!settings.automation.headless_mode ? "Attended GUI Window" : "Headless Launch"}</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Browser Test Results Banner */}
                {browserTestResult && (
                  <div
                    className={`mt-3 p-3.5 sm:p-4 rounded-xl border transition-all w-full max-w-full overflow-hidden ${
                      browserTestResult.success
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-300"
                        : "bg-rose-500/10 border-rose-500/30 text-rose-800 dark:text-rose-300"
                    }`}
                  >
                    {/* Header Row: Status, Title, Duration Badge, & Top-Right Dismiss */}
                    <div className="flex items-start justify-between gap-2.5 min-w-0 pb-2 border-b border-black/5 dark:border-white/5">
                      <div className="flex items-start gap-2 min-w-0 flex-1">
                        {browserTestResult.success ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-rose-500 mt-0.5 shrink-0" />
                        )}
                        <div className="flex flex-wrap items-center gap-1.5 min-w-0">
                          <span className="text-xs font-bold shrink-0">
                            {browserTestResult.success ? "Browser Launch Test Verified" : "Browser Launch Test Failed"}
                          </span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/10 dark:bg-white/10 shrink-0 whitespace-nowrap">
                            {browserTestResult.browser_engine ? browserTestResult.browser_engine.toUpperCase() : "ENGINE"} • {browserTestResult.mode} • {browserTestResult.duration_ms}ms
                          </span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setBrowserTestResult(null)}
                        className={`text-[11px] font-semibold px-2.5 py-1 rounded-md transition-colors shrink-0 cursor-pointer ${
                          browserTestResult.success
                            ? "text-emerald-700 dark:text-emerald-300 hover:text-emerald-900 dark:hover:text-emerald-100 bg-emerald-500/15 hover:bg-emerald-500/25"
                            : "text-rose-700 dark:text-rose-300 hover:text-rose-900 dark:hover:text-rose-100 bg-rose-500/15 hover:bg-rose-500/25"
                        }`}
                      >
                        Dismiss
                      </button>
                    </div>

                    {/* Body Content */}
                    <div className="pt-2.5 space-y-2 min-w-0">
                      <p className="text-[11px] leading-relaxed opacity-90 break-words min-w-0">
                        {browserTestResult.message}
                      </p>

                      {/* Extension Runtime Verification Badges */}
                      {browserTestResult.extension_found && (
                        <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                          {browserTestResult.extension_loaded ? (
                            <span className="inline-flex flex-wrap items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 max-w-full">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                              <span className="break-words">
                                AntiCaptcha Active • Service Worker Running{" "}
                                {browserTestResult.extension_id && (
                                  <span className="font-mono break-all">({browserTestResult.extension_id})</span>
                                )}
                              </span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 max-w-full">
                              <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                              <span>Extension Not Loaded by Browser</span>
                            </span>
                          )}
                        </div>
                      )}

                      {/* Warning callout if any */}
                      {browserTestResult.warning && (
                        <div className="mt-2 p-2.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-900 dark:text-amber-200 text-[11px] space-y-1.5">
                          <div className="font-semibold flex items-center gap-1.5 text-xs">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                            Extension Execution Warning
                          </div>
                          <p className="opacity-95 leading-normal break-words">{browserTestResult.warning}</p>
                          <button
                            type="button"
                            onClick={() => {
                              if (!settings) return;
                              setSettings({
                                ...settings,
                                automation: {
                                  ...settings.automation,
                                  browser_engine: "chromium",
                                  user_agent: ENGINE_USER_AGENTS.chromium,
                                },
                              });
                              setFeedback({
                                type: "success",
                                msg: "Switched Browser Engine to Chromium (Recommended). Re-test or click Save Settings to apply.",
                              });
                            }}
                            className="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-[10px] cursor-pointer inline-flex items-center gap-1 transition-colors shadow-xs"
                          >
                            <Sparkles className="w-3 h-3" /> Switch to Chromium Engine (Recommended)
                          </button>
                        </div>
                      )}

                      {browserTestResult.chrome_executable && (
                        <div className="text-[10px] font-mono opacity-80 pt-0.5 break-all min-w-0">
                          Binary: {browserTestResult.chrome_executable}
                        </div>
                      )}
                      {browserTestResult.extension_path && (
                        <div className="text-[10px] font-mono opacity-80 break-all min-w-0">
                          Extension Directory: {browserTestResult.extension_path}
                        </div>
                      )}
                      {browserTestResult.error_detail && (
                        <div className="text-[10px] font-mono text-rose-600 dark:text-rose-400 pt-1 break-all min-w-0">
                          Error: {browserTestResult.error_detail}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB: AUTOMATION (Unique Names Tester)                       */}
        {/* ========================================================= */}
        {activeTab === "automation" && (
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors mt-6">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <Terminal className="w-5 h-5 text-indigo-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  Unique Names API Tester
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Test the name permutations generator used before scraping county portals.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  JSON Request Payload (UniqueNamesRequest)
                </label>
                <textarea
                  value={testUniqueNamesPayload}
                  onChange={(e) => setTestUniqueNamesPayload(e.target.value)}
                  className="w-full h-64 p-3 bg-slate-950 text-emerald-400 font-mono text-[11px] rounded-lg border border-slate-800 focus:ring-2 focus:ring-indigo-500/50 resize-y"
                  spellCheck={false}
                />
                <button
                  type="button"
                  onClick={handleTestUniqueNames}
                  disabled={isTestingUniqueNames}
                  className="w-full flex justify-center items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50"
                >
                  {isTestingUniqueNames ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  {isTestingUniqueNames ? "Generating..." : "Generate Unique Names"}
                </button>
              </div>
              
              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Response
                </label>
                <div className="w-full h-64 p-3 bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-lg overflow-auto">
                  {uniqueNamesResult ? (
                    <pre className="text-[11px] font-mono text-slate-800 dark:text-slate-300 break-all whitespace-pre-wrap">
                      {JSON.stringify(uniqueNamesResult, null, 2)}
                    </pre>
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-400 text-xs italic">
                      Run test to see results
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB: AUTOMATION (Fuzzy Match API Tester)                    */}
        {/* ========================================================= */}
        {activeTab === "automation" && (
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors mt-6">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <Search className="w-5 h-5 text-indigo-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  Fuzzy Match API Tester
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Test the rapidfuzz cascade matching algorithm for claims evaluation.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  JSON Request Payload (DirectFuzzyMatchRequest)
                </label>
                <textarea
                  value={testFuzzyMatchPayload}
                  onChange={(e) => setTestFuzzyMatchPayload(e.target.value)}
                  className="w-full h-64 p-3 bg-slate-950 text-emerald-400 font-mono text-[11px] rounded-lg border border-slate-800 focus:ring-2 focus:ring-indigo-500/50 resize-y"
                  spellCheck={false}
                />
                <button
                  type="button"
                  onClick={handleTestFuzzyMatch}
                  disabled={isTestingFuzzyMatch}
                  className="w-full flex justify-center items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50"
                >
                  {isTestingFuzzyMatch ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  {isTestingFuzzyMatch ? "Evaluating..." : "Evaluate Fuzzy Match"}
                </button>
              </div>
              
              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Match Result
                </label>
                <div className="w-full h-64 p-3 bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-lg overflow-auto">
                  {fuzzyMatchResult ? (
                    <pre className="text-[11px] font-mono text-slate-800 dark:text-slate-300 break-all whitespace-pre-wrap">
                      {JSON.stringify(fuzzyMatchResult, null, 2)}
                    </pre>
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-400 text-xs italic">
                      Run test to see matching results
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB: PROXY SETTINGS                                       */}
        {/* ========================================================= */}
        {activeTab === "proxy" && (
          <div className="space-y-6 w-full">
            <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-lg shadow-slate-900/20">
              <div className="flex items-center gap-3 mb-2">
                <Network className="w-6 h-6 text-slate-300" />
                <h3 className="text-xl font-bold">Proxy Pool Settings</h3>
              </div>
              <p className="text-sm text-slate-300 max-w-2xl">
                Configure a dedicated proxy server to route all automation traffic through. 
                This helps distribute requests and avoid IP bans from county court portals.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm w-full">
              <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Network className="w-4 h-4 text-slate-400" />
                Proxy Connection Details
              </h4>
              <div className="space-y-6 w-full">
                <label className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-800 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors w-full">
                  <input
                    type="checkbox"
                    checked={settings?.proxy?.enabled ?? false}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        proxy: { ...(settings?.proxy || { host: "", port: 8080 }), enabled: e.target.checked },
                      } as SystemSettings)
                    }
                    className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-900 dark:text-slate-100">Enable Proxy Server</div>
                    <div className="text-xs text-slate-500">Route all scraping traffic through this proxy</div>
                  </div>
                </label>

                {settings?.proxy?.enabled && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
                    <div className="w-full">
                      <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Proxy Host / IP</label>
                      <input
                        type="text"
                        value={settings?.proxy?.host || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            proxy: { ...(settings?.proxy || {}), host: e.target.value },
                          } as SystemSettings)
                        }
                        placeholder="e.g. 192.168.1.50 or proxy.example.com"
                        className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                      />
                    </div>
                    <div className="w-full">
                      <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Port</label>
                      <input
                        type="number"
                        value={settings?.proxy?.port || 8080}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            proxy: { ...(settings?.proxy || {}), port: parseInt(e.target.value) || 8080 },
                          } as SystemSettings)
                        }
                        className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                      />
                    </div>
                    <div className="w-full">
                      <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Username (Optional)</label>
                      <input
                        type="text"
                        value={settings?.proxy?.username || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            proxy: { ...(settings?.proxy || {}), username: e.target.value },
                          } as SystemSettings)
                        }
                        placeholder="Proxy Username"
                        className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                      />
                    </div>
                    <div className="w-full">
                      <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Password (Optional)</label>
                      <input
                        type="password"
                        value={settings?.proxy?.password || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            proxy: { ...(settings?.proxy || {}), password: e.target.value },
                          } as SystemSettings)
                        }
                        placeholder="Proxy Password"
                        className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB: ANTICAPTCHA EXTENSION                                 */}
        {/* ========================================================= */}
        {activeTab === "extension" && (
          <div className="space-y-6 w-full">
            {/* Header Banner */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg shadow-indigo-600/20">
              <div className="flex items-center gap-3 mb-2">
                <Plug className="w-6 h-6" />
                <h3 className="text-base font-bold">AntiCaptcha Chrome Extension — Install & Configure</h3>
              </div>
              <p className="text-sm text-indigo-100 leading-relaxed">
                The Anti-Captcha plugin (v0.83) is bundled with this solution and automatically loaded by the automation
                engine. Use this tab to configure the extension path, set your API key, verify the plugin health, and
                test the live CAPTCHA-solving pipeline.
              </p>
              <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
                {["1. Set Extension Path", "2. Enter API Key", "3. Test Balance", "4. Verify Health", "5. Run Browser Test"].map((step, i) => (
                  <span key={i} className="px-2.5 py-1 bg-white/20 rounded-full font-semibold">{step}</span>
                ))}
              </div>
            </div>

            {/* Step 1 & 2: Path + API Key */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 space-y-5 shadow-xs">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <Plug className="w-4 h-4 text-indigo-500" />
                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-200">Plugin Configuration</h4>
              </div>

              {/* Extension Directory */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs">AntiCaptcha Extension Directory Path</label>
                  <span className="text-[10px] text-indigo-600 dark:text-indigo-400 font-semibold bg-indigo-50 dark:bg-indigo-950/50 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800">
                    Default: .\anticaptcha-plugin_v0.83\
                  </span>
                </div>
                <input
                  type="text"
                  placeholder=".\anticaptcha-plugin_v0.83\"
                  value={settings.automation.chrome_extension_dir || ""}
                  onChange={(e) => setSettings({ ...settings, automation: { ...settings.automation, chrome_extension_dir: e.target.value } })}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Relative path from the solution root. The <code className="font-mono text-slate-700 dark:text-slate-300">anticaptcha-plugin_v0.83</code> folder is already bundled. Use an absolute path only for custom external directories.
                </p>
              </div>

              {/* API Key */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs">AntiCaptcha API Key</label>
                <div className="relative w-full">
                  <input
                    type={showApiKey ? "text" : "password"}
                    placeholder="Enter your AntiCaptcha Client Key"
                    value={settings.automation.anticaptcha_api_key || ""}
                    onChange={(e) => setSettings({ ...settings, automation: { ...settings.automation, anticaptcha_api_key: e.target.value } })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                  >
                    {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Get your API key from <a href="https://anti-captcha.com" target="_blank" rel="noopener noreferrer" className="text-indigo-500 hover:underline">anti-captcha.com</a>. The key is automatically synced into the extension&apos;s <code className="font-mono text-slate-700 dark:text-slate-300">config_ac_api_key.js</code> on every browser launch.
                </p>
              </div>

              <button
                type="button"
                onClick={() => handleSave()}
                disabled={isSaving}
                className="w-full sm:w-auto px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50 shadow-xs shadow-indigo-600/20"
              >
                <Save className="w-3.5 h-3.5" />
                {isSaving ? "Saving..." : "Save Extension Configuration"}
              </button>
            </div>

            {/* Step 3: API Key Balance Test */}
            <div className="bg-indigo-50 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-800/60 rounded-2xl p-5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                    <ShieldCheck className="w-3.5 h-3.5 text-indigo-500" />
                    Test API Key Balance & Connectivity
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Validates the key by calling the live AntiCaptcha <code className="font-mono">getBalance</code> endpoint. Shows credit balance and latency.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleTestAntiCaptchaBalance}
                  disabled={isTestingAntiCaptchaBalance}
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50 shrink-0"
                >
                  {isTestingAntiCaptchaBalance ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                  Test API Key Balance
                </button>
              </div>
              {antiCaptchaBalanceResult && (
                <div className={`rounded-xl p-3 text-xs border space-y-1 ${antiCaptchaBalanceResult.status === "ok" ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300" : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"}`}>
                  <div className="flex items-center gap-2 font-bold">
                    {antiCaptchaBalanceResult.status === "ok" ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                    {antiCaptchaBalanceResult.message}
                  </div>
                  {antiCaptchaBalanceResult.status === "ok" && antiCaptchaBalanceResult.balance != null && (
                    <div className="font-mono text-emerald-700 dark:text-emerald-400">
                      Account Balance: <strong>${antiCaptchaBalanceResult.balance.toFixed(4)}</strong>
                    </div>
                  )}
                  <div className="text-[10px] opacity-70 font-mono">
                    Latency: {antiCaptchaBalanceResult.latency_ms.toFixed(0)}ms
                    {antiCaptchaBalanceResult.error_code && ` • Error: ${antiCaptchaBalanceResult.error_code}`}
                  </div>
                </div>
              )}
            </div>

            {/* Step 4: Extension Health Diagnostics */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    Extension Health Diagnostics
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Verifies extension directory, manifest.json validity, and API key synchronization to the plugin config file.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleValidateExtension}
                  disabled={isValidatingExtension}
                  className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50 shrink-0"
                >
                  {isValidatingExtension ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                  Check Extension Health
                </button>
              </div>
              {extensionValidationResult ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {[
                      { label: "Plugin Directory", ok: extensionValidationResult.directory_exists, okText: "Found on Disk", failText: "Directory Missing", detail: extensionValidationResult.extension_dir },
                      { label: "Manifest & Version", ok: extensionValidationResult.manifest_valid, okText: "Manifest V3 Valid", failText: "Missing manifest.json", detail: "v0.83 (Turnstile & reCAPTCHA)" },
                      { label: "Credentials State", ok: extensionValidationResult.api_key_synced, okText: "API Key Synchronized", failText: "Not Synchronized", detail: "config_ac_api_key.js configured", warn: !extensionValidationResult.api_key_synced },
                    ].map((item) => (
                      <div key={item.label} className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-1">
                        <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">{item.label}</span>
                        <div className="flex items-center gap-1.5 text-xs font-semibold">
                          {item.ok ? (
                            <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />{item.okText}</span>
                          ) : (
                            <span className={`flex items-center gap-1 ${item.warn ? "text-amber-600 dark:text-amber-400" : "text-rose-600 dark:text-rose-400"}`}>
                              {item.warn ? <AlertTriangle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}{item.failText}
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] font-mono text-slate-400 truncate" title={item.detail}>{item.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Click &ldquo;Check Extension Health&rdquo; to verify the plugin directory, manifest integrity, and API key sync status.
                </p>
              )}
            </div>

            {/* Step 5: Browser Launch Test */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                    <Play className="w-4 h-4 text-purple-500" />
                    Live Browser Launch Test
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Launches a real browser with the AntiCaptcha extension loaded and navigates to a test page to confirm the CAPTCHA-solving pipeline works end-to-end.
                  </p>
                </div>
                <button
                  type="button"
                  disabled={isTestingBrowser}
                  onClick={() => handleTestBrowser(settings.automation.headless_mode)}
                  className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50 shrink-0"
                >
                  {isTestingBrowser ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                  {isTestingBrowser ? "Testing Browser..." : "Launch Browser Test"}
                </button>
              </div>
              {browserTestResult && (
                <div className={`p-3.5 rounded-xl border ${browserTestResult.success ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-300" : "bg-rose-500/10 border-rose-500/30 text-rose-800 dark:text-rose-300"}`}>
                  <div className="flex items-center gap-2 font-bold text-xs mb-2">
                    {browserTestResult.success ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                    {browserTestResult.success ? "Browser Launch Test Verified" : "Browser Launch Test Failed"}
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/10 dark:bg-white/10">
                      {browserTestResult.browser_engine?.toUpperCase()} • {browserTestResult.mode} • {browserTestResult.duration_ms}ms
                    </span>
                  </div>
                  <p className="text-[11px] opacity-90">{browserTestResult.message}</p>
                  {browserTestResult.extension_path && (
                    <div className="mt-1 text-[10px] font-mono opacity-70 break-all">Extension: {browserTestResult.extension_path}</div>
                  )}
                </div>
              )}
              {!browserTestResult && (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Mode: <strong className="text-slate-700 dark:text-slate-300">{!settings.automation.headless_mode ? "Attended (Visible GUI)" : "Headless (Background)"}</strong>.
                  Change in the <button onClick={() => setActiveTab("automation")} className="text-indigo-500 hover:underline cursor-pointer">Browser &amp; CAPTCHA</button> tab.
                </p>
              )}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB: EMAIL & ENTERPRISE NOTIFICATIONS                     */}
        {/* ========================================================= */}
        {activeTab === "email" && (() => {
          const emailCfg: EmailSettings = settings.email || DEFAULT_EMAIL_SETTINGS;
          return (
          <div className="space-y-8 w-full pb-[600px]">
            {/* 1. MASTER ON/OFF TOGGLE & ENGINE STATUS */}
            <div
              className={`p-6 rounded-2xl border transition-all shadow-xs ${
                emailCfg.email_notifications_enabled
                  ? "bg-emerald-500/10 border-emerald-500/30 dark:bg-emerald-950/20 dark:border-emerald-800/50"
                  : "bg-amber-500/10 border-amber-500/30 dark:bg-amber-950/20 dark:border-amber-800/50"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <Mail className="w-5 h-5 text-indigo-500" />
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                      Master Email & Notification Engine Switch
                    </h3>
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${
                        emailCfg.email_notifications_enabled
                          ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500/40"
                          : "bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-500/40"
                      }`}
                    >
                      {emailCfg.email_notifications_enabled ? "Engine Active" : "Engine Disabled"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 max-w-3xl">
                    {emailCfg.email_notifications_enabled
                      ? "The automated notification engine is fully active. All event-driven emails (Guidewire sync, activity creation, portal scraping errors, and daily digests) will be dispatched according to the configured rules."
                      : "The automated notification engine is DISABLED. Claim processing and Guidewire sync will run normally, but all email notifications and Celery dispatch jobs are completely bypassed with zero background overhead."}
                  </p>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={emailCfg.email_notifications_enabled}
                      onChange={(e) =>
                        updateEmailSettings({ email_notifications_enabled: e.target.checked })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-300 dark:bg-slate-700 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                  </label>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                    {emailCfg.email_notifications_enabled ? "Enabled" : "Disabled"}
                  </span>
                </div>
              </div>
            </div>

            {/* 2. PROVIDER CONFIGURATION & CONNECTION TEST */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center gap-2">
                  <Server className="w-5 h-5 text-indigo-500" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                      Outbound Email Provider Configuration
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Select delivery backend (Local Mock sandbox, standard SMTP, Microsoft 365, or cloud services) and test credentials.
                    </p>
                  </div>
                </div>

                {/* Test Connection Button */}
                <button
                  type="button"
                  onClick={handleTestEmailConnection}
                  disabled={isTestingEmailConnection}
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-2 shadow-xs"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isTestingEmailConnection ? "animate-spin" : ""}`} />
                  {isTestingEmailConnection ? "Testing Connection..." : "Test Connection"}
                </button>
              </div>

              {/* Provider Selection Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  onClick={() => updateEmailSettings({ provider: "local_mock" })}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    emailCfg.provider === "local_mock"
                      ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <HardDrive className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Local Mock Sandbox
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-700 dark:text-indigo-300">
                      Dev / Offline
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                    Simulates dispatch without external networks. Saves artifacts to <code className="text-[10px] px-1 bg-slate-200 dark:bg-slate-800 rounded">logs/emails/</code> and returns structured delivery receipts.
                  </p>
                </div>

                <div
                  onClick={() => updateEmailSettings({ provider: "maildev" })}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    emailCfg.provider === "maildev"
                      ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Inbox className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Local MailDev Webbox
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/15 text-sky-700 dark:text-sky-300">
                      Port 1080 / 1025
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                    Captures live emails locally on SMTP port 1025. Inspect HTML, plain text, and MIME headers at <code className="text-[10px] px-1 bg-slate-200 dark:bg-slate-800 rounded">localhost:1080</code>.
                  </p>
                  <div className="mt-3">
                    <a
                      href={emailCfg.maildev_web_url || "http://localhost:1080"}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-1 text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Open MailDev Webbox
                    </a>
                  </div>
                </div>

                <div
                  onClick={() => updateEmailSettings({ provider: "direct_mx" })}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    emailCfg.provider === "direct_mx"
                      ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Corporate Direct MX
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/15 text-purple-700 dark:text-purple-300">
                      RFC-5321 TLS
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                    Resolves domain MX records via DNS and delivers directly to destination mail gateway via STARTTLS. Bypasses disabled basic auth on M365/Exchange tenants.
                  </p>
                </div>

                <div
                  onClick={() => updateEmailSettings({ provider: "smtp" })}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    emailCfg.provider === "smtp"
                      ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Server className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Authenticated SMTP Relay
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-300">
                      SMTP Auth
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                    Dispatches live emails via authenticated SMTP relay (Google Workspace, SendGrid, Amazon SES SMTP, or internal corporate relay with user/password credentials).
                  </p>
                </div>

                <div
                  onClick={() => updateEmailSettings({ provider: "graph" })}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    emailCfg.provider === "graph"
                      ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cloud className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Microsoft Graph API
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/15 text-blue-700 dark:text-blue-300">
                      O365 / Azure AD
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                    App-only modern OAuth2 token authentication via Microsoft Graph REST API endpoint. Complies with modern zero-trust policies with basic auth disabled.
                  </p>
                </div>

                <div
                  onClick={() => updateEmailSettings({ provider: "ses" })}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    emailCfg.provider === "ses"
                      ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Send className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Amazon SES API
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300">
                      AWS Cloud SDK
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                    High-throughput cloud email delivery via Amazon Simple Email Service (SES) API using AWS access keys and regional endpoints with cryptographic provenance.
                  </p>
                </div>
              </div>

              {/* MailDev Settings Inputs */}
              {emailCfg.provider === "maildev" && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      MailDev SMTP Host
                    </label>
                    <input
                      type="text"
                      value={emailCfg.smtp_host || "localhost"}
                      onChange={(e) => updateEmailSettings({ smtp_host: e.target.value })}
                      placeholder="localhost"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      MailDev SMTP Port
                    </label>
                    <input
                      type="number"
                      value={emailCfg.smtp_port === 587 ? 1025 : (emailCfg.smtp_port || 1025)}
                      onChange={(e) =>
                        updateEmailSettings({ smtp_port: parseInt(e.target.value) || 1025 })
                      }
                      placeholder="1025"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      MailDev Web Inspector URL
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={emailCfg.maildev_web_url || "http://localhost:1080"}
                        onChange={(e) => updateEmailSettings({ maildev_web_url: e.target.value })}
                        placeholder="http://localhost:1080"
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                      />
                      <a
                        href={emailCfg.maildev_web_url || "http://localhost:1080"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shrink-0 inline-flex items-center gap-1 transition-colors"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        Open
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* SMTP Settings Inputs */}
              {emailCfg.provider === "smtp" && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      SMTP Host / Server
                    </label>
                    <input
                      type="text"
                      value={emailCfg.smtp_host}
                      onChange={(e) => updateEmailSettings({ smtp_host: e.target.value })}
                      placeholder="smtp.office365.com"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      SMTP Port
                    </label>
                    <input
                      type="number"
                      value={emailCfg.smtp_port}
                      onChange={(e) =>
                        updateEmailSettings({ smtp_port: parseInt(e.target.value) || 587 })
                      }
                      placeholder="587"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Encryption Protocol
                    </label>
                    <select
                      value={emailCfg.smtp_encryption}
                      onChange={(e) => updateEmailSettings({ smtp_encryption: e.target.value })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    >
                      <option value="tls">STARTTLS (Port 587 - Recommended)</option>
                      <option value="ssl">SSL / TLS (Port 465)</option>
                      <option value="none">None / Plain (Internal Relay - Port 25)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      SMTP Username / Account
                    </label>
                    <input
                      type="text"
                      value={emailCfg.smtp_username || ""}
                      onChange={(e) => updateEmailSettings({ smtp_username: e.target.value })}
                      placeholder="notifications@test.com"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      SMTP Password / App Password
                    </label>
                    <div className="relative">
                      <input
                        type={showSmtpPassword ? "text" : "password"}
                        value={emailCfg.smtp_password || ""}
                        onChange={(e) => updateEmailSettings({ smtp_password: e.target.value })}
                        placeholder="••••••••••••"
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setShowSmtpPassword(!showSmtpPassword)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs"
                      >
                        {showSmtpPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Socket Timeout (Seconds)
                    </label>
                    <input
                      type="number"
                      min="2"
                      max="60"
                      value={emailCfg.timeout_seconds}
                      onChange={(e) =>
                        updateEmailSettings({ timeout_seconds: parseInt(e.target.value) || 15 })
                      }
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    />
                  </div>
                </div>
              )}

              {/* Microsoft Graph API Settings Inputs */}
              {emailCfg.provider === "graph" && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Azure AD / M365 Tenant ID
                    </label>
                    <input
                      type="text"
                      value={emailCfg.graph_tenant_id || ""}
                      onChange={(e) => updateEmailSettings({ graph_tenant_id: e.target.value })}
                      placeholder="e.g. 00000000-0000-0000-0000-000000000000"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Application / Client ID
                    </label>
                    <input
                      type="text"
                      value={emailCfg.graph_client_id || ""}
                      onChange={(e) => updateEmailSettings({ graph_client_id: e.target.value })}
                      placeholder="e.g. 11111111-1111-1111-1111-111111111111"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Client Secret (Application Password)
                    </label>
                    <div className="relative">
                      <input
                        type={showGraphSecret ? "text" : "password"}
                        value={emailCfg.graph_client_secret || ""}
                        onChange={(e) => updateEmailSettings({ graph_client_secret: e.target.value })}
                        placeholder="••••••••••••"
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setShowGraphSecret(!showGraphSecret)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
                        title={showGraphSecret ? "Hide secret" : "Show secret"}
                      >
                        {showGraphSecret ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Amazon SES Settings Inputs */}
              {emailCfg.provider === "ses" && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      AWS Region
                    </label>
                    <input
                      type="text"
                      value={emailCfg.ses_region || "us-east-1"}
                      onChange={(e) => updateEmailSettings({ ses_region: e.target.value })}
                      placeholder="us-east-1"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      AWS Access Key ID
                    </label>
                    <input
                      type="text"
                      value={emailCfg.ses_access_key_id || ""}
                      onChange={(e) => updateEmailSettings({ ses_access_key_id: e.target.value })}
                      placeholder="AKIAIOSFODNN7EXAMPLE"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      AWS Secret Access Key
                    </label>
                    <div className="relative">
                      <input
                        type={showSesSecret ? "text" : "password"}
                        value={emailCfg.ses_secret_access_key || ""}
                        onChange={(e) => updateEmailSettings({ ses_secret_access_key: e.target.value })}
                        placeholder="••••••••••••"
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setShowSesSecret(!showSesSecret)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
                        title={showSesSecret ? "Hide secret" : "Show secret"}
                      >
                        {showSesSecret ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Sender Details (Display Name, From Email, Reply-To) */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 pt-2 border-t border-slate-200 dark:border-slate-800/80">
                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    From Display Name
                  </label>
                  <input
                    type="text"
                    value={emailCfg.from_name}
                    onChange={(e) => updateEmailSettings({ from_name: e.target.value })}
                    placeholder="UAIC Claim Alerts"
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    From Email Address
                  </label>
                  <input
                    type="email"
                    value={emailCfg.from_email}
                    onChange={(e) => updateEmailSettings({ from_email: e.target.value })}
                    placeholder="notifications@test.com"
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Reply-To Address (Optional)
                  </label>
                  <input
                    type="email"
                    value={emailCfg.reply_to || ""}
                    onChange={(e) => updateEmailSettings({ reply_to: e.target.value })}
                    placeholder="claims-support@test.com"
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                </div>
              </div>

              {/* Connection Test Result Card */}
              {emailConnectionResult && (
                <div
                  className={`p-4 rounded-xl border space-y-2 transition-all ${
                    emailConnectionResult.success
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-900 dark:text-emerald-200"
                      : "bg-rose-500/10 border-rose-500/30 text-rose-900 dark:text-rose-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-xs">
                      {emailConnectionResult.success ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-rose-500" />
                      )}
                      <span>
                        {emailConnectionResult.success
                          ? "Email Provider Handshake Succeeded"
                          : "Email Provider Handshake Failed"}
                      </span>
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-black/10 dark:bg-white/10">
                        {emailConnectionResult.duration_ms}ms
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setEmailConnectionResult(null)}
                      className="text-xs opacity-70 hover:opacity-100 cursor-pointer"
                    >
                      Dismiss
                    </button>
                  </div>
                  <p className="text-xs opacity-95">{emailConnectionResult.message}</p>
                  {emailConnectionResult.error_detail && (
                    <pre className="text-[10px] font-mono p-2 bg-black/10 dark:bg-white/5 rounded overflow-x-auto whitespace-pre-wrap">
                      {emailConnectionResult.error_detail}
                    </pre>
                  )}
                </div>
              )}
            </div>

            {/* 3. RECIPIENT MANAGEMENT (TO, CC, BCC CHIPS) */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <Mail className="w-5 h-5 text-indigo-500" />
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                    Recipient Distribution Lists
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Manage operational alert distribution lists. Type email address and press Enter or click Add.
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                {/* TO RECIPIENTS */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Primary Recipients (TO)
                    </label>
                    <span className="text-[10px] text-slate-400">
                      {emailCfg.to_recipients.length} configured
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5 p-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl min-h-[42px] focus-within:border-indigo-500 transition-colors">
                    {emailCfg.to_recipients.map((email, idx) => (
                      <span
                        key={email}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-mono font-medium shadow-2xs"
                      >
                        {email}
                        <button
                          type="button"
                          onClick={() => handleRemoveRecipient("to", idx)}
                          className="text-slate-400 hover:text-rose-500 cursor-pointer text-xs"
                        >
                          &times;
                        </button>
                      </span>
                    ))}
                    <div className="flex items-center gap-1 flex-1 min-w-[220px]">
                      <input
                        type="email"
                        value={newToRecipient}
                        onChange={(e) => setNewToRecipient(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault();
                            handleAddRecipient("to");
                          }
                        }}
                        placeholder={emailCfg.to_recipients.length === 0 ? "Add primary recipient (e.g. claims-ops@test.com)..." : "Add recipient..."}
                        className="flex-1 bg-transparent text-xs text-slate-800 dark:text-slate-200 focus:outline-none px-2 py-1"
                      />
                      <button
                        type="button"
                        onClick={() => handleAddRecipient("to")}
                        className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-md transition-colors cursor-pointer"
                        title="Add TO recipient"
                      >
                        <Plus className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* CC & BCC RECIPIENTS SIDE-BY-SIDE */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* CC RECIPIENTS */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                        Carbon Copy Recipients (CC)
                      </label>
                      <span className="text-[10px] text-slate-400">
                        {emailCfg.cc_recipients.length} configured
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5 p-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl min-h-[42px] focus-within:border-indigo-500 transition-colors">
                      {emailCfg.cc_recipients.map((email, idx) => (
                        <span
                          key={email}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-mono font-medium shadow-2xs"
                        >
                          {email}
                          <button
                            type="button"
                            onClick={() => handleRemoveRecipient("cc", idx)}
                            className="text-slate-400 hover:text-rose-500 cursor-pointer text-xs"
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                      <div className="flex items-center gap-1 flex-1 min-w-[180px]">
                        <input
                          type="email"
                          value={newCcRecipient}
                          onChange={(e) => setNewCcRecipient(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              e.preventDefault();
                              handleAddRecipient("cc");
                            }
                          }}
                          placeholder={emailCfg.cc_recipients.length === 0 ? "Add CC recipient..." : "Add another CC..."}
                          className="flex-1 bg-transparent text-xs text-slate-800 dark:text-slate-200 focus:outline-none px-2 py-1"
                        />
                        <button
                          type="button"
                          onClick={() => handleAddRecipient("cc")}
                          className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-md transition-colors cursor-pointer"
                          title="Add CC recipient"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* BCC RECIPIENTS */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                        Blind Carbon Copy (BCC)
                      </label>
                      <span className="text-[10px] text-slate-400">
                        {emailCfg.bcc_recipients.length} configured
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5 p-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl min-h-[42px] focus-within:border-indigo-500 transition-colors">
                      {emailCfg.bcc_recipients.map((email, idx) => (
                        <span
                          key={email}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-mono font-medium shadow-2xs"
                        >
                          {email}
                          <button
                            type="button"
                            onClick={() => handleRemoveRecipient("bcc", idx)}
                            className="text-slate-400 hover:text-rose-500 cursor-pointer text-xs"
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                      <div className="flex items-center gap-1 flex-1 min-w-[180px]">
                        <input
                          type="email"
                          value={newBccRecipient}
                          onChange={(e) => setNewBccRecipient(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              e.preventDefault();
                              handleAddRecipient("bcc");
                            }
                          }}
                          placeholder={emailCfg.bcc_recipients.length === 0 ? "Add BCC recipient..." : "Add another BCC..."}
                          className="flex-1 bg-transparent text-xs text-slate-800 dark:text-slate-200 focus:outline-none px-2 py-1"
                        />
                        <button
                          type="button"
                          onClick={() => handleAddRecipient("bcc")}
                          className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-md transition-colors cursor-pointer"
                          title="Add BCC recipient"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 4. NOTIFICATION EVENT RULES & TRIGGERS */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <Sliders className="w-5 h-5 text-indigo-500" />
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                    Granular Event Rules & Dispatch Triggers
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Enable or disable specific event notifications. When an event is toggled off, matching alerts are suppressed.
                  </p>
                </div>
              </div>

              {/* MATCH NOTIFICATION DISPATCH STRATEGY (Direct System vs. Guidewire Activity) */}
              <div className="p-4.5 rounded-xl border border-indigo-200 dark:border-indigo-900/50 bg-indigo-50/50 dark:bg-indigo-950/20 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Radio className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Match Notification Strategy (Direct System Email vs. Guidewire Activity)
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        Choose whether confirmed court case matches send emails directly from this system, push to Guidewire, or both.
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 self-start sm:self-auto">
                    Mode: {settings?.integration?.notification_dispatch_mode || "both"}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                  {/* Option 1: BOTH */}
                  <div
                    onClick={() => {
                      if (!settings) return;
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          notification_dispatch_mode: "both",
                        },
                      });
                    }}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      (settings?.integration?.notification_dispatch_mode || "both") === "both"
                        ? "border-indigo-500 bg-white dark:bg-slate-900 ring-2 ring-indigo-500 shadow-xs"
                        : "border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 hover:border-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Dual Channel (Both)
                      </span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-700 dark:text-indigo-300">
                        Recommended
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                      Pushes match activity to Guidewire ClaimCenter AND delivers instant direct email alert with docket table.
                    </p>
                  </div>

                  {/* Option 2: DIRECT SYSTEM ONLY */}
                  <div
                    onClick={() => {
                      if (!settings) return;
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          notification_dispatch_mode: "direct_system",
                        },
                      });
                    }}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      settings?.integration?.notification_dispatch_mode === "direct_system"
                        ? "border-indigo-500 bg-white dark:bg-slate-900 ring-2 ring-indigo-500 shadow-xs"
                        : "border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 hover:border-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Direct System Email Only
                      </span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-700 dark:text-sky-300">
                        Direct UAIC
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                      Sends COURT_CASE_MATCHED email directly from this system without creating a Guidewire activity.
                    </p>
                  </div>

                  {/* Option 3: GUIDEWIRE ACTIVITY ONLY */}
                  <div
                    onClick={() => {
                      if (!settings) return;
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          notification_dispatch_mode: "guidewire_activity",
                        },
                      });
                    }}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      settings?.integration?.notification_dispatch_mode === "guidewire_activity"
                        ? "border-indigo-500 bg-white dark:bg-slate-900 ring-2 ring-indigo-500 shadow-xs"
                        : "border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 hover:border-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Guidewire Activity Only
                      </span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">
                        Guidewire Push
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                      Pushes docket match to Guidewire ClaimCenter. Sends GUIDEWIRE_ACTIVITY_CREATED email only upon success.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[
                  {
                    key: "court_case_matched",
                    title: "Court Docket Match Discovered (Direct System)",
                    desc: "Send immediate notification directly from UAIC when confirmed matching court case dockets are discovered.",
                    icon: CheckCircle2,
                  },
                  {
                    key: "guidewire_activity_created",
                    title: "Guidewire Activity Created",
                    desc: "Notify when a confirmed court case match is successfully pushed to Guidewire ClaimCenter.",
                    icon: Zap,
                  },
                  {
                    key: "guidewire_activity_failed",
                    title: "Guidewire Sync Failure Alert",
                    desc: "Critical alert when Guidewire REST push returns 4xx/5xx or encounters network timeout.",
                    icon: AlertTriangle,
                  },
                  {
                    key: "scraper_failed",
                    title: "Court Portal Scraper Error",
                    desc: "Notify when a county court scraper hits CAPTCHA barrier, navigation timeout, or portal lockout.",
                    icon: AlertCircle,
                  },
                  {
                    key: "claim_failed",
                    title: "Claim Processing Exhausted",
                    desc: "Alert when all scraper attempts and retries for a claim have completely failed.",
                    icon: ShieldCheck,
                  },
                ].map((rule) => {
                  const IconComponent = rule.icon;
                  const isEnabled = emailCfg.rules?.[rule.key] ?? true;
                  return (
                    <div
                      key={rule.key}
                      onClick={() => handleToggleRule(rule.key)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all flex items-start justify-between gap-3 ${
                        isEnabled
                          ? "border-emerald-500/40 bg-emerald-500/5 dark:bg-emerald-950/20"
                          : "border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/20 opacity-70"
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <IconComponent className={`w-4 h-4 ${isEnabled ? "text-emerald-500" : "text-slate-400"}`} />
                          <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                            {rule.title}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          {rule.desc}
                        </p>
                      </div>
                      <div className="pt-0.5 shrink-0">
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                            isEnabled
                              ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30"
                              : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700"
                          }`}
                        >
                          {isEnabled ? "Active" : "Muted"}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 5. INTERACTIVE TEST EMAIL CONSOLE */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center gap-2">
                  <Send className="w-5 h-5 text-indigo-500" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                      Live Notification Sandbox & Test Email Sender
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Dispatch a real test notification to verify end-to-end delivery, Celery queue execution, and template rendering.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleSendTestEmail}
                  disabled={isSendingTestEmail}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-2 shadow-xs"
                >
                  <Send className={`w-3.5 h-3.5 ${isSendingTestEmail ? "animate-spin" : ""}`} />
                  {isSendingTestEmail ? "Sending Notification..." : "Send Test Email"}
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1.5 sm:col-span-1">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Test Destination Recipient
                  </label>
                  <input
                    type="email"
                    value={testRecipientEmail}
                    onChange={(e) => setTestRecipientEmail(e.target.value)}
                    placeholder={emailCfg.to_recipients?.[0] || "test@test.com"}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                  <span className="text-[10px] text-slate-400">
                    Leave blank to send to primary TO recipient ({emailCfg.to_recipients?.[0] || "none"})
                  </span>
                </div>

                <div className="space-y-1.5 sm:col-span-2">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Test Subject Line
                  </label>
                  <input
                    type="text"
                    value={testEmailSubject}
                    onChange={(e) => setTestEmailSubject(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1.5 sm:col-span-3">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Test Message Body Content
                  </label>
                  <textarea
                    rows={2}
                    value={testEmailBody}
                    onChange={(e) => setTestEmailBody(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                </div>
              </div>

              {testEmailResult && (
                <div
                  className={`p-4 rounded-xl border space-y-2 transition-all ${
                    testEmailResult.success
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-900 dark:text-emerald-200"
                      : "bg-rose-500/10 border-rose-500/30 text-rose-900 dark:text-rose-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-xs">
                      {testEmailResult.success ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-rose-500" />
                      )}
                      <span>
                        {testEmailResult.success ? "Test Notification Dispatched Successfully" : "Test Notification Failed"}
                      </span>
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-black/10 dark:bg-white/10">
                        Status: {testEmailResult.status} • {testEmailResult.duration_ms}ms
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setTestEmailResult(null)}
                      className="text-xs opacity-70 hover:opacity-100 cursor-pointer"
                    >
                      Dismiss
                    </button>
                  </div>
                  <p className="text-xs opacity-95">{testEmailResult.message}</p>
                  <div className="text-[10px] font-mono opacity-80 flex gap-4">
                    <span>Notification ID: {testEmailResult.notification_id}</span>
                    <span>Recipient: {testEmailResult.recipient}</span>
                  </div>
                  {testEmailResult.success && emailCfg.provider === "maildev" && (
                    <div className="pt-2">
                      <a
                        href={emailCfg.maildev_web_url || "http://localhost:1080"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors shadow-xs"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        Inspect Received Email in MailDev ({emailCfg.maildev_web_url || "http://localhost:1080"})
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* 6. DYNAMIC EMAIL TEMPLATE STUDIO & DESIGNER */}
            <div id="template-studio-section" className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              {/* Top Header */}
              <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 gap-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                    <Code2 className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                        Dynamic Email Template Studio & Designer
                      </h3>
                      {selectedTemplate?.is_custom ? (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30">
                          Customized Override
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700">
                          System Default
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Customize responsive HTML5 and RFC-822 plain text email templates, click tokens to insert dynamic placeholders, and inspect live rendered output.
                    </p>
                  </div>
                </div>

                {/* Top Action Toolbar */}
                <div className="flex flex-wrap items-center gap-2 self-start lg:self-auto">
                  {/* View Mode Toggle: Parallel vs Edit vs Preview */}
                  <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
                    <button
                      type="button"
                      onClick={() => setActiveEditorTab("split")}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                        activeEditorTab === "split"
                          ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      title="Side-by-side parallel view of editor and synchronized live preview"
                    >
                      <Columns className="w-3.5 h-3.5" />
                      Parallel View
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveEditorTab("edit")}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                        activeEditorTab === "edit"
                          ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      title="Full width editor only"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      Editor Only
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveEditorTab("preview")}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                        activeEditorTab === "preview"
                          ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      title="Full width live preview"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Live Preview
                    </button>
                  </div>

                  {/* Reset to Default */}
                  <button
                    type="button"
                    onClick={handleResetTemplate}
                    disabled={isResettingTemplate}
                    title="Reset this template back to factory default"
                    className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-1.5 border border-slate-200 dark:border-slate-700 disabled:opacity-50"
                  >
                    <RotateCcw className={`w-3.5 h-3.5 ${isResettingTemplate ? "animate-spin" : ""}`} />
                    Reset Default
                  </button>

                  {/* Save Template Button */}
                  <button
                    type="button"
                    onClick={handleSaveTemplate}
                    disabled={isSavingTemplate}
                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-1.5 shadow-xs"
                  >
                    <Save className={`w-3.5 h-3.5 ${isSavingTemplate ? "animate-spin" : ""}`} />
                    {isSavingTemplate ? "Saving..." : "Save Template"}
                  </button>
                </div>
              </div>

              {/* Template Selector Pills */}
              <div className="space-y-2">
                <label className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider block">
                  Select Event Template to Customize
                </label>
                <div className="flex flex-wrap gap-2">
                  {templates.map((tpl) => {
                    const isSelected = selectedTemplateEvent === tpl.event_type;
                    return (
                      <button
                        key={tpl.event_type}
                        type="button"
                        onClick={() => selectTemplateForEditing(tpl)}
                        className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-all cursor-pointer flex items-center gap-2 border ${
                          isSelected
                            ? "bg-indigo-600 text-white border-indigo-600 shadow-xs ring-2 ring-indigo-600/30"
                            : "bg-slate-50 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700"
                        }`}
                      >
                        <span>{tpl.name || tpl.event_type}</span>
                        {tpl.is_custom && (
                          <span
                            className={`text-[9px] font-bold px-1.5 py-0.2 rounded-full ${
                              isSelected
                                ? "bg-white/20 text-white"
                                : "bg-amber-500/20 text-amber-700 dark:text-amber-300"
                            }`}
                          >
                            Custom
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* STUDIO UTILITY & TOOLS MENU BAR */}
              <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 text-xs">
                <div className="flex items-center gap-2 flex-wrap">
                  {/* Format / Beautify HTML */}
                  {templateEditFormat === "html" && (
                    <button
                      type="button"
                      onClick={handleFormatHtml}
                      className="px-2.5 py-1 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg font-semibold text-slate-700 dark:text-slate-300 transition-all cursor-pointer inline-flex items-center gap-1.5 shadow-2xs"
                      title="Auto-indent and format HTML markup"
                    >
                      <AlignLeft className="w-3.5 h-3.5 text-indigo-500" />
                      <span>Beautify HTML</span>
                    </button>
                  )}

                  {/* Copy Code */}
                  <button
                    type="button"
                    onClick={handleCopyTemplateCode}
                    className="px-2.5 py-1 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg font-semibold text-slate-700 dark:text-slate-300 transition-all cursor-pointer inline-flex items-center gap-1.5 shadow-2xs"
                    title="Copy template markup to clipboard"
                  >
                    {copiedTemplateCode ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                    <span>{copiedTemplateCode ? "Copied!" : "Copy Code"}</span>
                  </button>

                  {/* Parameter Tokens Palette Drawer Toggle */}
                  <button
                    type="button"
                    onClick={() => setIsTokensPaletteOpen(!isTokensPaletteOpen)}
                    className={`px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer inline-flex items-center gap-1.5 border ${
                      isTokensPaletteOpen
                        ? "bg-indigo-50 dark:bg-indigo-950/60 border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 shadow-2xs"
                    }`}
                    title="Toggle dynamic token chips drawer"
                  >
                    <Tag className="w-3.5 h-3.5 text-indigo-500" />
                    <span>Tokens ({tokensCatalog.length})</span>
                  </button>

                  {/* Device Viewport Toggle (Active in Split or Preview mode) */}
                  {(activeEditorTab === "split" || activeEditorTab === "preview") && (
                    <div className="flex items-center bg-white dark:bg-slate-900 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700 shadow-2xs">
                      <button
                        type="button"
                        onClick={() => setPreviewDevice("desktop")}
                        className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                          previewDevice === "desktop"
                            ? "bg-indigo-600 text-white shadow-xs"
                            : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                        }`}
                        title="Standard Desktop Email Layout (650px container)"
                      >
                        <Laptop className="w-3.5 h-3.5" />
                        <span>Desktop</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setPreviewDevice("mobile")}
                        className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                          previewDevice === "mobile"
                            ? "bg-indigo-600 text-white shadow-xs"
                            : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                        }`}
                        title="Mobile Phone Viewport Simulation (375px)"
                      >
                        <Smartphone className="w-3.5 h-3.5" />
                        <span>Mobile</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Live Stats Pill */}
                <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                  <span className="px-2 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                    {(templateEditFormat === "html" ? draftHtml : draftText).length} chars
                  </span>
                  <span className="px-2 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                    {((templateEditFormat === "html" ? draftHtml : draftText).match(/\n/g) || []).length + 1} lines
                  </span>
                  <span className="px-2 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-indigo-600 dark:text-indigo-400 font-semibold">
                    {((templateEditFormat === "html" ? draftHtml : draftText).match(/\{\{[^}]+\}\}/g) || []).length} tokens
                  </span>
                </div>
              </div>

              {/* Feedback Alert Banner */}
              {templateSaveFeedback && (
                <div
                  className={`p-3.5 rounded-xl border flex items-center justify-between text-xs transition-all ${
                    templateSaveFeedback.type === "success"
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-900 dark:text-emerald-200"
                      : "bg-rose-500/10 border-rose-500/30 text-rose-900 dark:text-rose-200"
                  }`}
                >
                  <div className="flex items-center gap-2 font-medium">
                    {templateSaveFeedback.type === "success" ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
                    )}
                    <span>{templateSaveFeedback.msg}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setTemplateSaveFeedback(null)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer font-bold px-1.5"
                  >
                    &times;
                  </button>
                </div>
              )}

              {/* ==================================================== */}
              {/* DYNAMIC STUDIO CONTENT (PARALLEL / EDIT / PREVIEW)  */}
              {/* ==================================================== */}
              {(() => {
                const renderEditor = () => (
                  <div className="space-y-4">
                    {/* Subject Line Input */}
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                          Subject Line Template
                        </label>
                        <span className="text-[11px] text-slate-400">
                          Supports <code className="text-[10px] bg-slate-100 dark:bg-slate-800 px-1 rounded">{"{{variable}}"}</code> tokens
                        </span>
                      </div>
                      <input
                        type="text"
                        value={draftSubject}
                        onFocus={() => setActiveFocusedField("subject")}
                        onChange={(e) => {
                          setDraftSubject(e.target.value);
                          loadTemplatePreviewWithDraft(
                            selectedTemplateEvent,
                            e.target.value,
                            draftHtml,
                            draftText
                          );
                        }}
                        placeholder="Subject line with {{claim_number}}..."
                        className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 dark:text-slate-200 font-mono focus:outline-hidden focus:border-indigo-500 transition-colors"
                      />
                    </div>

                    {/* Format Tabs & Token Target */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-slate-200 dark:border-slate-800">
                      <div className="flex items-center gap-2">
                        <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                          Body Format:
                        </label>
                        <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
                          <button
                            type="button"
                            onClick={() => {
                              setTemplateEditFormat("html");
                              setActiveFocusedField("html");
                            }}
                            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                              templateEditFormat === "html"
                                ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                            }`}
                          >
                            <Code2 className="w-3.5 h-3.5" />
                            HTML View
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setTemplateEditFormat("text");
                              setActiveFocusedField("text");
                            }}
                            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer inline-flex items-center gap-1.5 ${
                              templateEditFormat === "text"
                                ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                            }`}
                          >
                            <FileText className="w-3.5 h-3.5" />
                            Plain Text View
                          </button>
                        </div>
                      </div>

                      <div className="text-[11px] text-slate-500 dark:text-slate-400">
                        Target Field: <span className="font-mono font-semibold text-indigo-600 dark:text-indigo-400 uppercase text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/40">{activeFocusedField}</span>
                      </div>
                    </div>

                    {/* DYNAMIC PARAMETER PALETTE (Collapsible) */}
                    {isTokensPaletteOpen && (
                      <div className="p-4 rounded-xl border border-indigo-100 dark:border-indigo-950 bg-indigo-50/40 dark:bg-indigo-950/15 space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <Tag className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                            <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                              Dynamic Parameter Palette (Click to Insert)
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500 dark:text-slate-400">
                            Click any token to insert into <code className="text-[10px] bg-slate-200 dark:bg-slate-800 px-1 rounded">{activeFocusedField}</code>
                          </span>
                        </div>

                        {/* Category Filter Tabs */}
                        <div className="flex flex-wrap gap-1">
                          {["All", "Claim Info", "Parties", "Court & Match Info", "Guidewire", "System & Runtime"].map(
                            (cat) => (
                              <button
                                key={cat}
                                type="button"
                                onClick={() => setSelectedTokenCategory(cat)}
                                className={`px-2 py-0.5 text-[10px] font-semibold rounded-md transition-all cursor-pointer ${
                                  selectedTokenCategory === cat
                                    ? "bg-indigo-600 text-white shadow-xs"
                                    : "bg-white/80 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700"
                                }`}
                              >
                                {cat}
                              </button>
                            )
                          )}
                        </div>

                        {/* Token Chips */}
                        <div className="flex flex-wrap gap-1.5 pt-1 max-h-[140px] overflow-y-auto">
                          {tokensCatalog
                            .filter(
                              (t) =>
                                selectedTokenCategory === "All" ||
                                t.category === selectedTokenCategory
                            )
                            .map((t) => (
                              <button
                                key={t.token}
                                type="button"
                                onClick={() => handleInsertToken(t.token)}
                                title={`${t.description} (Sample: ${t.sample})`}
                                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white dark:bg-slate-900 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 border border-slate-200 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 text-xs font-mono text-slate-800 dark:text-slate-200 transition-all cursor-pointer shadow-2xs group"
                              >
                                <span className="text-indigo-600 dark:text-indigo-400 font-bold group-hover:scale-125 transition-transform">+</span>
                                <span>{`{{${t.token}}}`}</span>
                                <span className="text-[9px] px-1 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-sans">
                                  {t.label}
                                </span>
                              </button>
                            ))}
                        </div>
                      </div>
                    )}

                    {/* Code Editor Textarea */}
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                          {templateEditFormat === "html"
                            ? "HTML Body Template (Responsive Email Layout)"
                            : "Plain Text Body Template (Fallback)"}
                        </label>
                        <span className="text-[10px] font-mono text-emerald-500 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          Live Sync Active
                        </span>
                      </div>
                      {templateEditFormat === "html" ? (
                        <textarea
                          rows={activeEditorTab === "split" ? 18 : 16}
                          value={draftHtml}
                          onFocus={() => setActiveFocusedField("html")}
                          onChange={(e) => {
                            setDraftHtml(e.target.value);
                            loadTemplatePreviewWithDraft(
                              selectedTemplateEvent,
                              draftSubject,
                              e.target.value,
                              draftText
                            );
                          }}
                          placeholder="Write HTML markup here..."
                          spellCheck={false}
                          className="w-full bg-slate-950 text-emerald-400 border border-slate-800 rounded-xl p-4 font-mono text-xs leading-relaxed focus:outline-hidden focus:border-indigo-500 transition-colors shadow-inner"
                        />
                      ) : (
                        <textarea
                          rows={activeEditorTab === "split" ? 18 : 10}
                          value={draftText}
                          onFocus={() => setActiveFocusedField("text")}
                          onChange={(e) => {
                            setDraftText(e.target.value);
                            loadTemplatePreviewWithDraft(
                              selectedTemplateEvent,
                              draftSubject,
                              draftHtml,
                              e.target.value
                            );
                          }}
                          placeholder="Plain text fallback body..."
                          spellCheck={false}
                          className="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-xl p-4 font-mono text-xs leading-relaxed focus:outline-hidden focus:border-indigo-500 transition-colors shadow-inner"
                        />
                      )}
                    </div>
                  </div>
                );

                const renderPreview = () => (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                        <Eye className="w-3.5 h-3.5 text-indigo-500" />
                        Live Synchronized Render Preview
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-400">
                          {isLoadingTemplatePreview ? "Rendering..." : "Synchronized with Editor"}
                        </span>
                      </div>
                    </div>

                    <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden bg-white dark:bg-slate-900/60 shadow-inner">
                      {/* Subject Banner */}
                      <div className="px-4 py-2.5 bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="font-bold text-slate-700 dark:text-slate-300 uppercase text-[10px] tracking-wider px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 font-mono shrink-0">
                            Subject
                          </span>
                          <span className="font-semibold text-slate-900 dark:text-slate-100 font-mono text-xs truncate">
                            {templatePreviewSubject || "UAIC Notification Alert"}
                          </span>
                        </div>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-mono self-start sm:self-auto shrink-0">
                          {templateEditFormat === "html" ? "Responsive HTML5" : "RFC-822 Text"}
                        </span>
                      </div>

                      {/* Rendered Viewport Frame */}
                      <div className="p-4 sm:p-6 bg-slate-100 dark:bg-slate-950 overflow-y-auto max-h-[520px]">
                        {isLoadingTemplatePreview ? (
                          <div className="py-16 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                            <RefreshCw className="w-4 h-4 animate-spin text-indigo-500" />
                            Rendering dynamic preview...
                          </div>
                        ) : templateEditFormat === "html" ? (
                          templatePreviewHtml ? (
                            <div className="flex justify-center w-full">
                              {previewDevice === "mobile" ? (
                                <div className="w-[375px] max-w-full bg-slate-900 p-3 rounded-[2.5rem] shadow-2xl border-4 border-slate-700">
                                  {/* Smartphone Speaker / Notch */}
                                  <div className="w-24 h-4 bg-slate-800 rounded-full mx-auto mb-2 flex items-center justify-center">
                                    <div className="w-2.5 h-2.5 rounded-full bg-slate-900 mr-2" />
                                    <div className="w-8 h-1 rounded-full bg-slate-700" />
                                  </div>
                                  <div
                                    className="bg-white rounded-2xl p-4 text-slate-900 text-xs overflow-x-auto min-h-[360px]"
                                    dangerouslySetInnerHTML={{ __html: templatePreviewHtml }}
                                  />
                                </div>
                              ) : (
                                <div
                                  className="w-full max-w-2xl bg-white rounded-xl shadow-md border border-slate-200 p-6 text-slate-900 overflow-x-auto"
                                  dangerouslySetInnerHTML={{ __html: templatePreviewHtml }}
                                />
                              )}
                            </div>
                          ) : (
                            <div className="text-center py-12 text-xs text-slate-400 font-mono">
                              No preview markup generated.
                            </div>
                          )
                        ) : (
                          <pre className="p-4 overflow-y-auto max-h-[460px] text-xs font-mono text-slate-800 dark:text-slate-200 bg-slate-50 dark:bg-slate-950 whitespace-pre-wrap rounded-lg">
                            {templatePreviewText || "No plain text body defined."}
                          </pre>
                        )}
                      </div>

                      {/* Sample Context Mock Tokens */}
                      <div className="px-4 py-2 bg-slate-50 dark:bg-slate-900/80 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center gap-2 text-[10px] text-slate-500 dark:text-slate-400">
                        <span className="font-semibold">Context Tokens:</span>
                        <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono">Claim: 0100456789</span>
                        <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono">Insured: JOHNATHAN DOE</span>
                        <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono">Claimant: JANE SMITH</span>
                        <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono">Activity: ACT-77829-SAMPLE</span>
                        <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono">Matches: 2 case(s)</span>
                      </div>
                    </div>
                  </div>
                );

                if (activeEditorTab === "split") {
                  return (
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 items-start w-full">
                      {renderEditor()}
                      {renderPreview()}
                    </div>
                  );
                }

                if (activeEditorTab === "edit") {
                  return <div className="w-full">{renderEditor()}</div>;
                }

                return <div className="w-full">{renderPreview()}</div>;
              })()}
            </div>

            {/* 7. DELIVERY HISTORY LOG TABLE */}
            <div id="delivery-history-section" className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-4 shadow-xs w-full transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-indigo-500" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                      Outbound Notification Delivery History
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Real-time delivery audit trail recording recipient, status, latency, and cryptographic gateway receipts.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => fetchRecentNotifications()}
                  disabled={isLoadingNotifications}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isLoadingNotifications ? "animate-spin" : ""}`} />
                  Refresh History
                </button>
              </div>

              {/* Interactive Search & Filter Toolbar */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
                {/* Search Bar */}
                <div className="relative flex-1 max-w-md">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={historySearch}
                    onChange={(e) => {
                      setHistorySearch(e.target.value);
                      fetchRecentNotifications(1, historyStatusFilter, e.target.value, historyEventTypeFilter);
                    }}
                    placeholder="Search recipient, subject, claim #..."
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-8 pr-8 py-1.5 text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 focus:outline-hidden focus:border-indigo-500"
                  />
                  {historySearch && (
                    <button
                      type="button"
                      onClick={() => {
                        setHistorySearch("");
                        fetchRecentNotifications(1, historyStatusFilter, "", historyEventTypeFilter);
                      }}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Event Type Filter Dropdown & Status Filter Pills */}
                <div className="flex flex-wrap items-center gap-2">
                  <select
                    value={historyEventTypeFilter}
                    onChange={(e) => {
                      setHistoryEventTypeFilter(e.target.value);
                      fetchRecentNotifications(1, historyStatusFilter, historySearch, e.target.value);
                    }}
                    className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-medium"
                  >
                    <option value="ALL">All Event Triggers</option>
                    <option value="GUIDEWIRE_ACTIVITY_CREATED">Guidewire Created</option>
                    <option value="GUIDEWIRE_ACTIVITY_FAILED">Guidewire Failed</option>
                    <option value="COURT_CASE_MATCHED">Court Case Matched</option>
                    <option value="SCRAPER_FAILED">Scraper Failed</option>
                    <option value="CLAIM_PROCESSING_FAILED">Claim Failed</option>
                    <option value="TEST_EMAIL">Interactive Test</option>
                  </select>

                  <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700/80">
                    {["ALL", "SENT", "FAILED", "QUEUED", "SKIPPED"].map((st) => (
                      <button
                        key={st}
                        type="button"
                        onClick={() => {
                          setHistoryStatusFilter(st);
                          fetchRecentNotifications(1, st, historySearch, historyEventTypeFilter);
                        }}
                        className={`px-2.5 py-1 text-[10px] font-bold rounded-md uppercase tracking-wider transition-all cursor-pointer ${
                          historyStatusFilter === st
                            ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                            : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {isLoadingNotifications ? (
                <div className="p-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-indigo-500" />
                  Loading notification delivery records...
                </div>
              ) : recentNotifications.length > 0 ? (
                <div className="space-y-3">
                  <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 dark:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                        <tr>
                          <th className="px-4 py-3">Timestamp</th>
                          <th className="px-4 py-3">Event</th>
                          <th className="px-4 py-3">Recipient</th>
                          <th className="px-4 py-3">Subject</th>
                          <th className="px-4 py-3">Provider</th>
                          <th className="px-4 py-3">Status</th>
                          <th className="px-4 py-3 text-right">Delivery Proof</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-800 font-mono text-[11px]">
                        {recentNotifications.map((notif) => (
                          <tr key={notif.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                            <td className="px-4 py-2.5 whitespace-nowrap text-slate-500 dark:text-slate-400">
                              {new Date(notif.created_at).toLocaleString()}
                            </td>
                            <td className="px-4 py-2.5 whitespace-nowrap font-bold text-slate-800 dark:text-slate-200">
                              {notif.event_type}
                            </td>
                            <td className="px-4 py-2.5 whitespace-nowrap text-slate-600 dark:text-slate-300">
                              {notif.recipient}
                            </td>
                            <td className="px-4 py-2.5 max-w-xs truncate text-slate-600 dark:text-slate-300 font-sans">
                              {notif.subject}
                            </td>
                            <td className="px-4 py-2.5 whitespace-nowrap text-slate-500 dark:text-slate-400 uppercase text-[10px]">
                              {notif.provider}
                            </td>
                            <td className="px-4 py-2.5 whitespace-nowrap">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                                  notif.status === "SENT"
                                    ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30"
                                    : notif.status === "FAILED"
                                    ? "bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30"
                                    : notif.status === "SKIPPED"
                                    ? "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30"
                                    : "bg-blue-500/15 text-blue-700 dark:text-blue-300 border-blue-500/30"
                                }`}
                              >
                                {notif.status}
                              </span>
                            </td>
                            <td className="px-4 py-2.5 whitespace-nowrap text-right font-sans">
                              <button
                                type="button"
                                onClick={() => setSelectedReceiptNotif(notif)}
                                className="px-2.5 py-1 text-[10px] font-semibold rounded-md bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/50 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60 inline-flex items-center gap-1.5 transition-all cursor-pointer shadow-xs"
                              >
                                <Receipt className="w-3 h-3" />
                                View Receipt
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination Controls */}
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 px-1 text-xs text-slate-500 dark:text-slate-400">
                    <div className="flex items-center gap-1 text-[11px]">
                      <span>Showing</span>
                      <span className="font-semibold text-slate-700 dark:text-slate-200">
                        {recentNotifications.length}
                      </span>
                      <span>of</span>
                      <span className="font-semibold text-slate-700 dark:text-slate-200">
                        {historyTotalCount}
                      </span>
                      <span>total notifications</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => fetchRecentNotifications(historyPage - 1, historyStatusFilter, historySearch, historyEventTypeFilter)}
                        disabled={historyPage <= 1 || isLoadingNotifications}
                        className="px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-800 inline-flex items-center gap-1 cursor-pointer transition-colors shadow-xs text-xs"
                      >
                        <ChevronLeft className="w-3.5 h-3.5" />
                        Previous
                      </button>

                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        Page {historyPage} of {historyTotalPages || 1}
                      </span>

                      <button
                        type="button"
                        onClick={() => fetchRecentNotifications(historyPage + 1, historyStatusFilter, historySearch, historyEventTypeFilter)}
                        disabled={historyPage >= historyTotalPages || isLoadingNotifications}
                        className="px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-800 inline-flex items-center gap-1 cursor-pointer transition-colors shadow-xs text-xs"
                      >
                        Next
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-400 italic">
                  No notification records found matching criteria. Use the &quot;Send Test Email&quot; console above or trigger a claim automation run to record deliveries.
                </div>
              )}
            </div>
          </div>
          );
        })()}

        {/* ========================================================= */}
        {/* TAB: STORAGE & ERROR SCREENSHOTS PROVIDERS                */}
        {/* ========================================================= */}
        {activeTab === "storage" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-8 shadow-xs w-full transition-colors">
            {/* Header */}
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <HardDrive className="w-5 h-5 text-indigo-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  Storage Providers & Error Screenshot Diagnostics
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Configure error screenshot capture toggles and connect directly to cloud storage providers (Local disk, AWS S3, Azure Blob, Google Cloud Storage).
                </p>
              </div>
            </div>

            {/* 1. MASTER CAPTURE TOGGLE */}
            <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Camera className="w-4 h-4 text-indigo-500" />
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                      Error Screenshot Capture on Portal Scraper Failure
                    </span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                        (settings.storage?.capture_error_screenshots ?? true)
                          ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30"
                          : "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30"
                      }`}
                    >
                      {(settings.storage?.capture_error_screenshots ?? true) ? "Enabled" : "Disabled (Conserving Space)"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-2xl">
                    When active, the browser captures a high-resolution viewport image, document URL, title, and exception traceback whenever a portal fails or encounters a CAPTCHA barrier. Toggle OFF to prevent screenshot file creation and save disk/cloud storage.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    const current = settings.storage?.capture_error_screenshots ?? true;
                    setSettings({
                      ...settings,
                      storage: {
                        ...(settings.storage || {
                          capture_error_screenshots: true,
                          storage_provider: "local",
                        }),
                        capture_error_screenshots: !current,
                      },
                    });
                  }}
                  className={`px-4 py-2 text-xs font-semibold rounded-lg transition cursor-pointer flex items-center gap-2 ${
                    (settings.storage?.capture_error_screenshots ?? true)
                      ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm"
                      : "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-700"
                  }`}
                >
                  <Camera className="w-3.5 h-3.5" />
                  {(settings.storage?.capture_error_screenshots ?? true)
                    ? "Capture Active (Click to Disable)"
                    : "Capture Disabled (Click to Enable)"}
                </button>
              </div>
            </div>

            {/* 2. STORAGE PROVIDER SELECTION */}
            <div className="space-y-4">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                Select Storage Destination Provider
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {[
                  {
                    id: "local",
                    title: "Local Server Storage",
                    desc: "Saves to backend/screenshots/ on server disk. Safe default, zero external registration needed.",
                    icon: Server,
                  },
                  {
                    id: "s3",
                    title: "Amazon S3",
                    desc: "Direct bucket upload using AWS Access Key or IAM credentials.",
                    icon: Cloud,
                  },
                  {
                    id: "azure_blob",
                    title: "Azure Blob Storage",
                    desc: "Direct container upload using Azure Storage Connection String.",
                    icon: Database,
                  },
                  {
                    id: "gcs",
                    title: "Google Cloud Storage",
                    desc: "Direct bucket upload using Google Cloud Service Account credentials.",
                    icon: HardDrive,
                  },
                ].map((p) => {
                  const isSelected = (settings.storage?.storage_provider || "local") === p.id;
                  const Icon = p.icon;
                  return (
                    <div
                      key={p.id}
                      onClick={() => {
                        setSettings({
                          ...settings,
                          storage: {
                            ...(settings.storage || {
                              capture_error_screenshots: true,
                              storage_provider: "local",
                            }),
                            storage_provider: p.id,
                          },
                        });
                      }}
                      className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between space-y-3 ${
                        isSelected
                          ? "bg-indigo-50/60 dark:bg-indigo-950/40 border-indigo-500 dark:border-indigo-500 shadow-xs"
                          : "bg-white dark:bg-slate-900/30 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                      }`}
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <Icon className={`w-4 h-4 ${isSelected ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400"}`} />
                          <div
                            className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                              isSelected
                                ? "border-indigo-600 bg-indigo-600"
                                : "border-slate-300 dark:border-slate-700"
                            }`}
                          >
                            {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                          </div>
                        </div>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">{p.title}</h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">{p.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 3. DYNAMIC PROVIDER CONFIGURATION FIELDS */}
            <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-950/30 space-y-4">
              {(settings.storage?.storage_provider || "local") === "local" && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Server className="w-4 h-4 text-emerald-500" />
                    <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                      Local Server Directory Configuration
                    </h4>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Screenshots are stored locally in the <code className="font-mono text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-1 py-0.5 rounded">backend/screenshots/</code> folder. When no cloud provider is registered, the system seamlessly operates on this directory without downtime.
                  </p>
                  <div className="p-3 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 font-mono text-xs text-slate-700 dark:text-slate-300">
                    backend/screenshots/{"{claim_id}_{portal_key}_{timestamp}.png"}
                  </div>
                </div>
              )}

              {(settings.storage?.storage_provider || "local") === "s3" && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Cloud className="w-4 h-4 text-indigo-500" />
                    <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                      Amazon S3 Bucket & Credential Configuration
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        S3 Bucket Name *
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. uaic-court-screenshots"
                        value={settings.storage?.s3_bucket_name || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            storage: {
                              ...(settings.storage || { capture_error_screenshots: true, storage_provider: "s3" }),
                              s3_bucket_name: e.target.value,
                            },
                          })
                        }
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        AWS Region
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. us-east-1"
                        value={settings.storage?.s3_region || "us-east-1"}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            storage: {
                              ...(settings.storage || { capture_error_screenshots: true, storage_provider: "s3" }),
                              s3_region: e.target.value,
                            },
                          })
                        }
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        AWS Access Key ID (optional if using IAM role)
                      </label>
                      <input
                        type="text"
                        placeholder="AKIAIOSFODNN7EXAMPLE"
                        value={settings.storage?.s3_access_key || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            storage: {
                              ...(settings.storage || { capture_error_screenshots: true, storage_provider: "s3" }),
                              s3_access_key: e.target.value,
                            },
                          })
                        }
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        AWS Secret Access Key
                      </label>
                      <div className="relative">
                        <input
                          type={showS3Secret ? "text" : "password"}
                          placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                          value={settings.storage?.s3_secret_key || ""}
                          onChange={(e) =>
                            setSettings({
                              ...settings,
                              storage: {
                                ...(settings.storage || { capture_error_screenshots: true, storage_provider: "s3" }),
                                s3_secret_key: e.target.value,
                              },
                            })
                          }
                          className="w-full text-xs font-mono px-3 py-2 pr-9 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowS3Secret(!showS3Secret)}
                          className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                        >
                          {showS3Secret ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {(settings.storage?.storage_provider || "local") === "azure_blob" && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-indigo-500" />
                    <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                      Azure Blob Storage Configuration
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        Storage Connection String *
                      </label>
                      <div className="relative">
                        <input
                          type={showAzureConn ? "text" : "password"}
                          placeholder="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
                          value={settings.storage?.azure_connection_string || ""}
                          onChange={(e) =>
                            setSettings({
                              ...settings,
                              storage: {
                                ...(settings.storage || { capture_error_screenshots: true, storage_provider: "azure_blob" }),
                                azure_connection_string: e.target.value,
                              },
                            })
                          }
                          className="w-full text-xs font-mono px-3 py-2 pr-9 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowAzureConn(!showAzureConn)}
                          className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                        >
                          {showAzureConn ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        Blob Container Name
                      </label>
                      <input
                        type="text"
                        placeholder="screenshots"
                        value={settings.storage?.azure_container_name || "screenshots"}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            storage: {
                              ...(settings.storage || { capture_error_screenshots: true, storage_provider: "azure_blob" }),
                              azure_container_name: e.target.value,
                            },
                          })
                        }
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {(settings.storage?.storage_provider || "local") === "gcs" && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <HardDrive className="w-4 h-4 text-indigo-500" />
                    <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                      Google Cloud Storage (GCS) Configuration
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        GCS Bucket Name *
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. uaic-court-screenshots"
                        value={settings.storage?.gcs_bucket_name || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            storage: {
                              ...(settings.storage || { capture_error_screenshots: true, storage_provider: "gcs" }),
                              gcs_bucket_name: e.target.value,
                            },
                          })
                        }
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                        GCP Project ID
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. uaic-production"
                        value={settings.storage?.gcs_project_id || ""}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            storage: {
                              ...(settings.storage || { capture_error_screenshots: true, storage_provider: "gcs" }),
                              gcs_project_id: e.target.value,
                            },
                          })
                        }
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-hidden focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 4. LIVE STORAGE TESTER SANDBOX */}
            <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                    Live Storage Provider Verification Sandbox
                  </h4>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                    Tests write permissions, network reachability, and directory/bucket access for the currently selected provider.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleTestStorage}
                  disabled={isTestingStorage}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white shadow-sm transition inline-flex items-center gap-2 cursor-pointer shrink-0"
                >
                  {isTestingStorage ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Play className="w-3.5 h-3.5" />
                  )}
                  <span>{isTestingStorage ? "Testing Storage..." : "Test Storage Connection"}</span>
                </button>
              </div>

              {storageTestResult && (
                <div
                  className={`p-4 rounded-xl border space-y-2 text-xs transition-all ${
                    storageTestResult.success
                      ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800/80 text-emerald-900 dark:text-emerald-200"
                      : "bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800/80 text-rose-900 dark:text-rose-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold">
                      {storageTestResult.success ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400" />
                      )}
                      <span>
                        {storageTestResult.success ? "Storage Provider Verified" : "Storage Verification Failed"}
                      </span>
                    </div>
                    <span className="text-[11px] font-mono opacity-80">{storageTestResult.duration_ms}ms</span>
                  </div>
                  <p className="opacity-95 leading-relaxed">{storageTestResult.message}</p>
                  {storageTestResult.details && Object.keys(storageTestResult.details).length > 0 && (
                    <div className="mt-2 p-2.5 rounded-lg bg-black/5 dark:bg-white/5 font-mono text-[11px] space-y-1">
                      {Object.entries(storageTestResult.details).map(([k, v]) => (
                        <div key={k} className="flex items-center justify-between">
                          <span className="text-slate-500 dark:text-slate-400">{k}:</span>
                          <span className="font-semibold">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 4: RAPIDFUZZ & NOISE CLEANUP ENGINE                   */}
        {/* ========================================================= */}
        {activeTab === "matcher" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <Sparkles className="w-5 h-5 text-indigo-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  RapidFuzz String Deduplication & Noise Cleaning Engine
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Configure string similarity algorithms, confidence thresholds, and corporate noise strip words.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
              {/* Auto Match Threshold */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Auto-Match Approval Threshold
                  </label>
                  <span className="font-mono text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 px-2 py-0.5 rounded-md">
                    {(settings.matcher.auto_match_threshold * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.40"
                  max="1.0"
                  step="0.05"
                  value={settings.matcher.auto_match_threshold}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      matcher: {
                        ...settings.matcher,
                        auto_match_threshold: parseFloat(e.target.value),
                      },
                    })
                  }
                  className="w-full accent-emerald-500 cursor-pointer"
                />
              </div>

              {/* Manual Review Threshold */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Manual Review Lower Threshold
                  </label>
                  <span className="font-mono text-xs font-bold text-purple-700 dark:text-purple-400 bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800/60 px-2 py-0.5 rounded-md">
                    {(settings.matcher.manual_review_threshold * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.20"
                  max="0.80"
                  step="0.05"
                  value={settings.matcher.manual_review_threshold}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      matcher: {
                        ...settings.matcher,
                        manual_review_threshold: parseFloat(e.target.value),
                      },
                    })
                  }
                  className="w-full accent-purple-500 cursor-pointer"
                />
              </div>

              {/* Algorithm */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  RapidFuzz Scorer Algorithm
                </label>
                <select
                  value={settings.matcher.scorer_algorithm}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      matcher: {
                        ...settings.matcher,
                        scorer_algorithm: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                >
                  <option value="token_sort_ratio">token_sort_ratio (Recommended for Legal Names)</option>
                  <option value="token_set_ratio">token_set_ratio (Best for Subset/Prefix Matches)</option>
                  <option value="partial_ratio">partial_ratio (Best for Substring Matches)</option>
                  <option value="ratio">ratio (Exact Levenshtein Distance)</option>
                </select>
              </div>

              {/* Min Filing Date */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Minimum Case Filing Date (YYYY-MM-DD)
                </label>
                <input
                  type="date"
                  value={settings.matcher.min_filing_date}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      matcher: {
                        ...settings.matcher,
                        min_filing_date: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Clean Noise Words Tag Chips */}
              <div className="sm:col-span-2 space-y-2">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Corporate & Legal Noise Words Stripped During Matching
                </label>
                <div className="flex flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl min-h-[50px] items-center">
                  {settings.matcher.clean_party_name_patterns.map((word) => (
                    <span
                      key={word}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-mono font-medium shadow-2xs"
                    >
                      {word}
                      <button
                        type="button"
                        onClick={() => handleRemoveNoiseWord(word)}
                        className="text-slate-400 hover:text-rose-500 cursor-pointer text-xs"
                      >
                        &times;
                      </button>
                    </span>
                  ))}
                </div>

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newNoiseWord}
                    onChange={(e) => setNewNoiseWord(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleAddNoiseWord();
                      }
                    }}
                    placeholder="Add new noise word (e.g. D/B/A)..."
                    className="flex-1 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 uppercase font-mono"
                  />
                  <button
                    type="button"
                    onClick={handleAddNoiseWord}
                    className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer"
                  >
                    Add Word
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 5: QUEUE & ALERT NOTIFICATIONS                       */}
        {/* ========================================================= */}
        {activeTab === "queue" && (
          <div className="space-y-6 w-full">
            {/* LIVE CELERY TELEMETRY & WORKER HEALTH */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-500" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                      Live Celery Cluster Telemetry & Queue Depths
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Real-time visibility into background worker nodes, queue backlog depths, and throughput status.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={fetchQueueStatus}
                  disabled={isLoadingQueueStatus}
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-2 shadow-xs"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isLoadingQueueStatus ? "animate-spin" : ""}`} />
                  {isLoadingQueueStatus ? "Refreshing..." : "Refresh Status"}
                </button>
              </div>

              {/* StatCards Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Workers Online"
                  value={queueStatus ? queueStatus.workers_online : "--"}
                  subtitle={queueStatus && queueStatus.workers_online > 0 ? "Cluster nodes active" : "Checking cluster..."}
                  icon={Server}
                  color={queueStatus && queueStatus.workers_online > 0 ? "emerald" : "amber"}
                  badge={queueStatus && queueStatus.workers_online > 0 ? "Healthy" : "Standby"}
                  badgeColor={queueStatus && queueStatus.workers_online > 0 ? "emerald" : "amber"}
                />
                <StatCard
                  title="Active Running Tasks"
                  value={queueStatus ? queueStatus.active_tasks : "--"}
                  subtitle="In-flight browser/fuzzy tasks"
                  icon={Zap}
                  color="sky"
                  badge={queueStatus && queueStatus.active_tasks > 0 ? "Processing" : "Idle"}
                  badgeColor={queueStatus && queueStatus.active_tasks > 0 ? "sky" : "slate"}
                />
                <StatCard
                  title="Pending Queue Backlog"
                  value={queueStatus ? queueStatus.pending_tasks : "--"}
                  subtitle="Tasks queued in Redis"
                  icon={Layers}
                  color={queueStatus && queueStatus.pending_tasks > 0 ? "amber" : "slate"}
                  badge={queueStatus && queueStatus.pending_tasks > 0 ? "Queued" : "Clean"}
                  badgeColor={queueStatus && queueStatus.pending_tasks > 0 ? "amber" : "emerald"}
                />
                <StatCard
                  title="Failed / Stuck Tasks"
                  value={queueStatus ? queueStatus.failed_tasks : "--"}
                  subtitle="Exhausted task retries"
                  icon={AlertTriangle}
                  color={queueStatus && queueStatus.failed_tasks > 0 ? "rose" : "emerald"}
                  badge={queueStatus && queueStatus.failed_tasks > 0 ? "Attention" : "Zero Errors"}
                  badgeColor={queueStatus && queueStatus.failed_tasks > 0 ? "rose" : "emerald"}
                />
              </div>

              {/* Individual Queue Depths */}
              {queueStatus?.queues && Object.keys(queueStatus.queues).length > 0 && (
                <div className="p-4 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                    <span>Individual Celery Queues</span>
                    <span className="text-[10px] text-slate-400">Redis Broker Channels</span>
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {Object.entries(queueStatus.queues).map(([qName, qCount]) => (
                      <div
                        key={qName}
                        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-2xs"
                      >
                        <span className="text-xs font-mono font-medium text-slate-700 dark:text-slate-300">
                          {qName}
                        </span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            qCount > 0
                              ? "bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30"
                              : "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30"
                          }`}
                        >
                          {qCount} pending
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* CELERY CONFIGURATION */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <Layers className="w-5 h-5 text-indigo-500" />
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                    Celery Worker Queues & Failure Alerts Configuration
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Configure task retry limits, chunk sizing, and operational notification emails.
                  </p>
                </div>
              </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
              {/* Max Retries */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Max Celery Task Retries
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={settings.queue.max_task_retries}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      queue: {
                        ...settings.queue,
                        max_task_retries: parseInt(e.target.value) || 0,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Retry Delay */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Task Retry Backoff Delay (Seconds)
                </label>
                <input
                  type="number"
                  min="5"
                  max="300"
                  value={settings.queue.task_retry_delay_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      queue: {
                        ...settings.queue,
                        task_retry_delay_seconds: parseInt(e.target.value) || 30,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Chunk Size */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Excel Batch Processing Chunk Size
                </label>
                <input
                  type="number"
                  min="5"
                  max="100"
                  value={settings.queue.batch_chunk_size}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      queue: {
                        ...settings.queue,
                        batch_chunk_size: parseInt(e.target.value) || 25,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Alert Email */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Critical Exception Alert Email
                </label>
                <div className="relative w-full">
                  <Mail className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    value={settings.integration.notification_email}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        integration: {
                          ...settings.integration,
                          notification_email: e.target.value,
                        },
                      })
                    }
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                    placeholder="claims-ops@test.com"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      </main>

      {/* DELIVERY RECEIPT INSPECTION MODAL (ROOT PORTAL LEVEL) */}
      {selectedReceiptNotif && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-150">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/50">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                  <Receipt className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    Email Delivery Receipt &amp; Provenance
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                    ID: {selectedReceiptNotif.id}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedReceiptNotif(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5 overflow-y-auto flex-1 text-xs">
              {/* Status & Key Stats Banner */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">
                    Delivery Status
                  </span>
                  <span
                    className={`inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      selectedReceiptNotif.status === "SENT"
                        ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300"
                        : selectedReceiptNotif.status === "FAILED"
                        ? "bg-rose-500/20 text-rose-700 dark:text-rose-300"
                        : "bg-amber-500/20 text-amber-700 dark:text-amber-300"
                    }`}
                  >
                    {selectedReceiptNotif.status}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">
                    Provider / Relay
                  </span>
                  <span className="inline-block mt-1 font-mono font-bold text-slate-900 dark:text-slate-100 uppercase">
                    {selectedReceiptNotif.provider}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">
                    Dispatched At
                  </span>
                  <span className="inline-block mt-1 font-mono text-slate-700 dark:text-slate-300">
                    {new Date(selectedReceiptNotif.created_at).toLocaleTimeString()}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">
                    Retry Count
                  </span>
                  <span className="inline-block mt-1 font-mono text-slate-700 dark:text-slate-300">
                    {selectedReceiptNotif.retry_count || 0}
                  </span>
                </div>
              </div>

              {/* Recipient & Event Details */}
              <div className="space-y-2">
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800/60 font-mono">
                  <span className="text-slate-500">Destination Recipient:</span>
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    {selectedReceiptNotif.recipient}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800/60 font-mono">
                  <span className="text-slate-500">Subject:</span>
                  <span className="text-slate-800 dark:text-slate-200 max-w-sm truncate text-right">
                    {selectedReceiptNotif.subject}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800/60 font-mono">
                  <span className="text-slate-500">Event Trigger:</span>
                  <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                    {selectedReceiptNotif.event_type}
                  </span>
                </div>
              </div>

              {/* Gateway Receipt Provenance */}
              {selectedReceiptNotif.delivery_receipt ? (
                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                    <CheckCheck className="w-3.5 h-3.5 text-emerald-500" />
                    MTA Gateway Proof of Delivery
                  </span>
                  <div className="p-3 rounded-xl bg-slate-950 text-slate-200 font-mono text-[11px] space-y-1.5 border border-slate-800">
                    {selectedReceiptNotif.delivery_receipt.message_id && (
                      <div>
                        <span className="text-slate-500">Message-ID: </span>
                        <span className="text-emerald-400 break-all">
                          {selectedReceiptNotif.delivery_receipt.message_id}
                        </span>
                      </div>
                    )}
                    {selectedReceiptNotif.delivery_receipt.gateway_host && (
                      <div>
                        <span className="text-slate-500">Gateway Server: </span>
                        <span className="text-indigo-300">
                          {selectedReceiptNotif.delivery_receipt.gateway_host}:
                          {selectedReceiptNotif.delivery_receipt.gateway_port || 25}
                        </span>
                      </div>
                    )}
                    {selectedReceiptNotif.delivery_receipt.server_response && (
                      <div>
                        <span className="text-slate-500">SMTP Response: </span>
                        <span className="text-amber-300 break-all">
                          {selectedReceiptNotif.delivery_receipt.server_response}
                        </span>
                      </div>
                    )}
                    {selectedReceiptNotif.delivery_receipt.receipt_requested && (
                      <div>
                        <span className="text-slate-500">RFC Receipt Headers: </span>
                        <span className="text-cyan-300">
                          RFC-3798 &amp; RFC-822 Acknowledgment Headers Active
                        </span>
                      </div>
                    )}
                    {selectedReceiptNotif.delivery_receipt.duration_ms !== undefined && (
                      <div>
                        <span className="text-slate-500">Transmission Latency: </span>
                        <span className="text-slate-300">
                          {selectedReceiptNotif.delivery_receipt.duration_ms} ms
                        </span>
                      </div>
                    )}
                    {selectedReceiptNotif.delivery_receipt.webbox_url && (
                      <div className="pt-2 border-t border-slate-800/80">
                        <a
                          href={selectedReceiptNotif.delivery_receipt.webbox_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          Inspect in MailDev Webbox ({selectedReceiptNotif.delivery_receipt.webbox_url})
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ) : null}

              {/* Raw Delivery Receipt JSON */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span className="font-semibold">Raw Receipt JSON Payload</span>
                  <button
                    type="button"
                    onClick={() => {
                      const raw = JSON.stringify(
                        selectedReceiptNotif.delivery_receipt || selectedReceiptNotif,
                        null,
                        2
                      );
                      navigator.clipboard.writeText(raw);
                      setFeedback({ type: "success", msg: "Receipt JSON copied to clipboard." });
                    }}
                    className="hover:text-indigo-500 inline-flex items-center gap-1 cursor-pointer font-mono"
                  >
                    <Copy className="w-3 h-3" />
                    Copy JSON
                  </button>
                </div>
                <pre className="p-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl overflow-x-auto text-[10px] font-mono text-slate-700 dark:text-slate-300 max-h-40 whitespace-pre-wrap">
                  {JSON.stringify(
                    selectedReceiptNotif.delivery_receipt || selectedReceiptNotif,
                    null,
                    2
                  )}
                </pre>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedReceiptNotif(null)}
                className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
              >
                Close Receipt
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
