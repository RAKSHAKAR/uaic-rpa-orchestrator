"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Clock,
  Send,
  Building,
  Scale,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Play,
  Edit3,
  Trash2,
  X,
  AlertTriangle,
  Globe,
  Database,
  Cpu,
  ShieldCheck,
  Search,
  Download,
  RefreshCw,
  Layers,
  Activity,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Eye,
  Copy,
  FileSpreadsheet,
  Code,
  Sparkles,
  FileText,
  Flame,
  Check,
  BarChart3,
  ListFilter,
  Camera,
  ZoomIn,
  ScrollText,
  User,
  Crosshair,
} from "lucide-react";
import { Navbar } from "../../../components/Navbar";
import { StatusBadge } from "../../../components/StatusBadge";
import { StatCard } from "../../../components/StatCard";
import { MultiSelectDropdown } from "../../../components/MultiSelectDropdown";
import { api } from "../../../lib/api";
import { Claim, ErrorScreenshot, ScrapedCourtCase, AuditLogEntry } from "../../../types";

export default function ClaimDetailPage() {
  const params = useParams();
  const router = useRouter();
  const claimId = params.id as string;

  const [claim, setClaim] = useState<Claim | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPushingGuidewire, setIsPushingGuidewire] = useState(false);
  const [isStartingAutomation, setIsStartingAutomation] = useState(false);
  const [isRetryingFailed, setIsRetryingFailed] = useState(false);
  const [runningBotKey, setRunningBotKey] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [notFound, setNotFound] = useState(false);

  // Export state and unified download handler
  const [isPdfExport, setIsPdfExport] = useState(false);
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const sp = new URLSearchParams(window.location.search);
      setIsPdfExport(sp.get("pdf_export") === "true");
    }
  }, []);

  const handleExportClaim = async (format: "xlsx" | "csv" | "json" | "pdf", e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    if (downloadingFormat) return;
    setDownloadingFormat(format);
    setFeedback(null);
    try {
      const exportUrl = api.getSingleClaimExportUrl(claimId, format);
      const res = await fetch(exportUrl);
      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        throw new Error(errText || `Server responded with status ${res.status}`);
      }
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition");
      const defaultName = format === "pdf"
        ? `claim_${claim?.claim_number || "report"}_report.pdf`
        : format === "xlsx"
        ? `claim_${claim?.claim_number || "report"}_report.xlsx`
        : format === "csv"
        ? `claim_${claim?.claim_number || "report"}_cases.csv`
        : `claim_${claim?.claim_number || "report"}.json`;

      let filename = defaultName;
      if (disposition && disposition.includes("filename=")) {
        const match = disposition.match(/filename=["']?([^"';]+)["']?/i);
        if (match && match[1]) filename = match[1].trim();
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();

      // Delay blob revocation so browser download manager finishes saving without corrupting
      setTimeout(() => {
        try {
          link.remove();
          window.URL.revokeObjectURL(url);
        } catch (e) {}
      }, 60000);

      setFeedback({ type: "success", msg: `Downloaded ${filename} successfully.` });
    } catch (err: any) {
      console.error(`${format.toUpperCase()} export failed:`, err);
      // Fallback: direct navigation download
      const fallbackUrl = api.getSingleClaimExportUrl(claimId, format);
      const link = document.createElement("a");
      link.href = fallbackUrl;
      link.setAttribute("download", `claim_${claim?.claim_number || "report"}.${format}`);
      document.body.appendChild(link);
      link.click();
      setTimeout(() => link.remove(), 2000);
      setFeedback({ type: "success", msg: `${format.toUpperCase()} export initiated via browser fallback.` });
    } finally {
      setDownloadingFormat(null);
    }
  };

  // Telemetry interactive controls
  const [selectedPortalTelemetry, setSelectedPortalTelemetry] = useState<string>("all");
  const [inspectedStage, setInspectedStage] = useState<{ key: string; data: any } | null>(null);
  const [inspectedStageTab, setInspectedStageTab] = useState<"stages" | "json">("stages");

  // 8 Bots controls
  const [botJurisdictionFilter, setBotJurisdictionFilter] = useState<"all" | "FL" | "TX">("all");
  const [botViewMode, setBotViewMode] = useState<"grid" | "timeline">("grid");
  const [isStartingAllBots, setIsStartingAllBots] = useState(false);
  const [copiedTelemetry, setCopiedTelemetry] = useState(false);

  // Scraped cases table controls
  const [caseSearchQuery, setCaseSearchQuery] = useState("");
  const [caseCountyFilters, setCaseCountyFilters] = useState<string[]>([]);
  const [caseStatusFilters, setCaseStatusFilters] = useState<string[]>([]);
  const [caseTypeFilters, setCaseTypeFilters] = useState<string[]>([]);
  const [caseSortField, setCaseSortField] = useState<"filing_date" | "case_number" | "case_style" | "county_name" | "case_status" | "case_type">("filing_date");
  const [caseSortAsc, setCaseSortAsc] = useState(false);
  const [casePage, setCasePage] = useState(1);
  const [casePageSize, setCasePageSize] = useState(10);
  const [caseViewLayout, setCaseViewLayout] = useState<"table" | "grouped">("table");
  const [collapsedPortals, setCollapsedPortals] = useState<Record<string, boolean>>({});

  // Modals
  const [selectedCaseForModal, setSelectedCaseForModal] = useState<ScrapedCourtCase | null>(null);
  const [rawJsonCaseForModal, setRawJsonCaseForModal] = useState<any | null>(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [copiedCaseNumber, setCopiedCaseNumber] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    primary_key: "",
    claim_number: "",
    exposure_number: "1",
    insured_first_name: "",
    insured_last_name: "",
    claimant_first_name: "",
    claimant_last_name: "",
    driver_first_name: "",
    driver_last_name: "",
    dol: "",
    policy_state: "Florida",
    loss_location_state: "Florida",
  });

  const fetchClaim = useCallback(async () => {
    setIsLoading(true);
    setNotFound(false);
    try {
      const data = await api.getClaimDetail(claimId);
      if (data) {
        setClaim(data);
        setFormData({
          primary_key: data.primary_key || "",
          claim_number: data.claim_number || "",
          exposure_number: data.exposure_number || "1",
          insured_first_name: data.insured_first_name || (data.insured_name ? data.insured_name.split(" ")[0] || "" : ""),
          insured_last_name: data.insured_last_name || (data.insured_name ? data.insured_name.split(" ").slice(1).join(" ") || "" : ""),
          claimant_first_name: data.claimant_first_name || (data.claimant_name ? data.claimant_name.split(" ")[0] || "" : ""),
          claimant_last_name: data.claimant_last_name || (data.claimant_name ? data.claimant_name.split(" ").slice(1).join(" ") || "" : ""),
          driver_first_name: data.driver_first_name || (data.driver_name ? data.driver_name.split(" ")[0] || "" : ""),
          driver_last_name: data.driver_last_name || (data.driver_name ? data.driver_name.split(" ").slice(1).join(" ") || "" : ""),
          dol: data.dol || "",
          policy_state: data.policy_state || "Florida",
          loss_location_state: data.loss_location_state || "Florida",
        });
      } else {
        setNotFound(true);
      }
    } catch (e) {
      console.error("Failed to load claim detail:", e);
      setNotFound(true);
    } finally {
      setIsLoading(false);
    }
  }, [claimId]);

  const [screenshots, setScreenshots] = useState<ErrorScreenshot[]>([]);
  const [isLoadingScreenshots, setIsLoadingScreenshots] = useState(false);
  const [selectedScreenshotModal, setSelectedScreenshotModal] = useState<ErrorScreenshot | null>(null);

  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);
  const [selectedAuditLogModal, setSelectedAuditLogModal] = useState<AuditLogEntry | null>(null);

  const fetchClaimAuditLogs = useCallback(async () => {
    if (!claimId) return;
    setIsLoadingAudit(true);
    try {
      const logs = await api.getClaimAuditLogs(claimId);
      setAuditLogs(logs || []);
    } catch (err) {
      console.error("Failed to load claim audit logs:", err);
    } finally {
      setIsLoadingAudit(false);
    }
  }, [claimId]);

  const fetchScreenshots = useCallback(async () => {
    if (!claimId) return;
    setIsLoadingScreenshots(true);
    try {
      const data = await api.getClaimScreenshots(claimId);
      setScreenshots(data || []);
    } catch (e) {
      console.error("Failed to load screenshots:", e);
    } finally {
      setIsLoadingScreenshots(false);
    }
  }, [claimId]);

  useEffect(() => {
    if (claimId) {
      fetchClaim();
      fetchScreenshots();
      fetchClaimAuditLogs();
    }
  }, [claimId, fetchClaim, fetchScreenshots, fetchClaimAuditLogs]);

  const handlePushGuidewire = async () => {
    setIsPushingGuidewire(true);
    setFeedback(null);
    try {
      const res = await api.pushToGuidewire(claimId);
      setFeedback({ type: "success", msg: res.message });
      await fetchClaim();
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to push claim to Guidewire.",
      });
    } finally {
      setIsPushingGuidewire(false);
    }
  };

  const handleStartAutomation = async () => {
    setIsStartingAutomation(true);
    setFeedback(null);
    try {
      const res = await api.startClaim(claimId);
      setFeedback({ type: "success", msg: res.message });
      await fetchClaim();
    } catch (err: any) {
      setFeedback({ type: "error", msg: "Failed to dispatch scraping automation." });
    } finally {
      setIsStartingAutomation(false);
    }
  };

  const handleRunSingleBot = async (botName: string) => {
    const botKeyMap: Record<string, string> = {
      "Broward County (FL)": "broward",
      "Hillsborough County (FL)": "hillsborough",
      "Miami-Dade County (FL)": "miami",
      "Travis County (TX)": "travis",
      "Dallas County (TX)": "dallas",
      "Harris County JP (TX)": "harris_jp",
      "Harris County Clerk (TX)": "harris_cclerk",
      "Harris District Clerk (TX)": "harris_district",
    };

    const key = botKeyMap[botName];
    if (!key) return;

    setRunningBotKey(key);
    setFeedback(null);
    try {
      const res = await api.runSingleBot(claimId, key);
      setFeedback({ type: "success", msg: res.message });
      await fetchClaim();
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || `Failed to run ${botName} bot.`,
      });
    } finally {
      setRunningBotKey(null);
    }
  };

  const handleRunAllBots = async () => {
    setIsStartingAllBots(true);
    setFeedback(null);
    try {
      const res = await api.runSingleBot(claimId, "all");
      setFeedback({ type: "success", msg: "All 8 county court scraper bots dispatched concurrently!" });
      await fetchClaim();
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to dispatch all 8 bots.",
      });
    } finally {
      setIsStartingAllBots(false);
    }
  };

  const failedPortals = useMemo(() => {
    if (!claim || !claim.bots) return [];
    const botKeyMap: Record<string, string> = {
      "Broward County (FL)": "broward",
      "Hillsborough County (FL)": "hillsborough",
      "Miami-Dade County (FL)": "miami",
      "Travis County (TX)": "travis",
      "Dallas County (TX)": "dallas",
      "Harris County JP (TX)": "harris_jp",
      "Harris County Clerk (TX)": "harris_cclerk",
      "Harris District Clerk (TX)": "harris_district",
    };
    return claim.bots
      .filter((b) => b.status === "FAILED")
      .map((b) => ({
        key: botKeyMap[b.name] || b.name.toLowerCase().replace(/[^a-z0-9]/g, "_"),
        name: b.name,
      }));
  }, [claim]);

  const handleRetryFailedPortals = async () => {
    if (isRetryingFailed) return;
    setIsRetryingFailed(true);
    setFeedback(null);
    try {
      const res = await api.retryFailedPortals(claimId);
      if (res.status === "info") {
        setFeedback({ type: "success", msg: res.message });
      } else {
        setFeedback({
          type: "success",
          msg: res.message || `Dispatched retry for ${res.retried_portals?.length || failedPortals.length} failed portal(s).`,
        });
      }
      await fetchClaim();
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to retry failed portals.",
      });
    } finally {
      setIsRetryingFailed(false);
    }
  };

  const handleCopyTelemetry = (data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopiedTelemetry(true);
    setTimeout(() => setCopiedTelemetry(false), 2000);
  };

  const handleDownloadTelemetry = (stageKey: string, data: any) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `telemetry_${claim?.claim_number || "claim"}_${stageKey}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateClaim(claimId, formData);
      setFeedback({ type: "success", msg: "Claim updated successfully." });
      setIsEditOpen(false);
      await fetchClaim();
    } catch (err: any) {
      setFeedback({ type: "error", msg: "Failed to update claim." });
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      await api.deleteClaim(claimId);
      router.push("/monitor");
    } catch (err: any) {
      setFeedback({ type: "error", msg: "Failed to delete claim." });
    }
  };

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCaseNumber(text);
    setTimeout(() => setCopiedCaseNumber(null), 2000);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr || dateStr.trim() === "" || dateStr === "-" || dateStr.toLowerCase() === "n/a") return "-";
    const clean = dateStr.trim();
    try {
      if (/^\d{2}\/\d{2}\/\d{4}$/.test(clean)) {
        return clean;
      }
      const isoMatch = clean.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
      if (isoMatch) {
        const [, y, m, d] = isoMatch;
        const dateObj = new Date(Date.UTC(Number(y), Number(m) - 1, Number(d)));
        if (!isNaN(dateObj.getTime())) {
          return dateObj.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            timeZone: "UTC",
          });
        }
      }
      const parsed = new Date(clean);
      if (!isNaN(parsed.getTime())) {
        const res = parsed.toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
          timeZone: "UTC",
        });
        if (res && !res.toLowerCase().includes("invalid")) {
          return res;
        }
      }
      return clean;
    } catch {
      return clean;
    }
  };

  // Resolve active stages depending on selected portal tab
  const activeStages = useMemo(() => {
    if (!claim?.action_timings) return {};
    if (selectedPortalTelemetry === "all") {
      return claim.action_timings.stages || {};
    }
    const portalData = claim.action_timings.portals?.[selectedPortalTelemetry];
    return portalData?.stages || claim.action_timings.stages || {};
  }, [claim, selectedPortalTelemetry]);

  // Compute Stage Latency Waterfall & Percentages
  const waterfallData = useMemo(() => {
    const rawStages = activeStages || {};
    const entries = [
      { key: "browser_launch", label: "Launch", name: "Browser Launch", color: "bg-sky-500" },
      { key: "website_navigation", label: "Navigation", name: "Navigation", color: "bg-indigo-500" },
      { key: "data_filling", label: "Data Entry", name: "Data Entry", color: "bg-amber-500" },
      { key: "captcha", label: "CAPTCHA", name: "CAPTCHA Defense", color: "bg-emerald-500" },
      { key: "submit", label: "Submit", name: "Search Submit", color: "bg-blue-500" },
      { key: "result_retrieval", label: "Retrieval", name: "Result Retrieval", color: "bg-purple-500" },
      { key: "database_save", label: "DB Save", name: "Database Save", color: "bg-teal-500" },
      { key: "fuzzy_matching", label: "RapidFuzz", name: "RapidFuzz Match", color: "bg-fuchsia-500" },
      { key: "guidewire_trigger", label: "Guidewire", name: "Guidewire Dispatch", color: "bg-emerald-600" },
    ];

    const parsed = entries
      .map((item) => {
        const stage = rawStages[item.key];
        const duration = stage?.duration_seconds ? Number(stage.duration_seconds) : 0;
        return {
          ...item,
          stage,
          duration,
        };
      })
      .filter((item) => item.duration > 0);

    const totalCalculated = parsed.reduce((sum, item) => sum + item.duration, 0);

    return parsed.map((item) => ({
      ...item,
      percentage: totalCalculated > 0 ? (item.duration / totalCalculated) * 100 : 0,
    }));
  }, [activeStages]);

  // Options for multi-select dropdown filters
  const countyOptions = useMemo(() => {
    const counts: Record<string, number> = {};
    (claim?.court_cases || []).forEach((c) => {
      const name = c.county_name || "Unknown County";
      counts[name] = (counts[name] || 0) + 1;
    });
    return Object.entries(counts).map(([name, count]) => ({
      value: name,
      label: `${name} (${count})`,
      count,
    }));
  }, [claim?.court_cases]);

  const statusOptions = useMemo(() => {
    const counts: Record<string, number> = {};
    (claim?.court_cases || []).forEach((c) => {
      const st = (c.case_status || "OPEN").toUpperCase();
      counts[st] = (counts[st] || 0) + 1;
    });
    return Object.entries(counts).map(([st, count]) => ({
      value: st,
      label: `${st} (${count})`,
      count,
    }));
  }, [claim?.court_cases]);

  const typeOptions = useMemo(() => {
    const counts: Record<string, number> = {};
    (claim?.court_cases || []).forEach((c) => {
      const tp = (c.case_type || "CIVIL").toUpperCase();
      counts[tp] = (counts[tp] || 0) + 1;
    });
    return Object.entries(counts).map(([tp, count]) => ({
      value: tp,
      label: `${tp} (${count})`,
      count,
    }));
  }, [claim?.court_cases]);

  // Filtered & Grouped Scraped Court Cases
  const filteredCases = useMemo(() => {
    if (!claim?.court_cases) return [];
    if (isPdfExport) return claim.court_cases;
    let list = [...claim.court_cases];

    if (caseSearchQuery.trim()) {
      const q = caseSearchQuery.toLowerCase().trim();
      list = list.filter(
        (c) =>
          (c.case_number || "").toLowerCase().includes(q) ||
          (c.case_style || "").toLowerCase().includes(q) ||
          (c.county_name || "").toLowerCase().includes(q) ||
          (c.case_type || "").toLowerCase().includes(q) ||
          (c.case_status || "").toLowerCase().includes(q)
      );
    }

    if (caseCountyFilters.length > 0) {
      list = list.filter((c) => caseCountyFilters.includes(c.county_name || "Unknown County"));
    }

    if (caseStatusFilters.length > 0) {
      list = list.filter((c) => caseStatusFilters.includes((c.case_status || "OPEN").toUpperCase()));
    }

    if (caseTypeFilters.length > 0) {
      list = list.filter((c) => caseTypeFilters.includes((c.case_type || "CIVIL").toUpperCase()));
    }

    list.sort((a, b) => {
      let valA: any = "";
      let valB: any = "";
      if (caseSortField === "filing_date") {
        valA = a.filing_date || a.raw_payload?.FilingDate || a.raw_payload?.filing_date || a.raw_payload?.SuitFiledDate || "";
        valB = b.filing_date || b.raw_payload?.FilingDate || b.raw_payload?.filing_date || b.raw_payload?.SuitFiledDate || "";
      } else {
        valA = a[caseSortField] || "";
        valB = b[caseSortField] || "";
      }
      if (caseSortAsc) {
        return valA > valB ? 1 : -1;
      }
      return valA < valB ? 1 : -1;
    });

    return list;
  }, [claim?.court_cases, caseSearchQuery, caseCountyFilters, caseStatusFilters, caseTypeFilters, caseSortField, caseSortAsc, isPdfExport]);

  // Paginated Court Cases
  const totalCasePages = Math.max(1, Math.ceil(filteredCases.length / casePageSize));
  const paginatedCases = useMemo(() => {
    if (isPdfExport) return filteredCases;
    const start = (casePage - 1) * casePageSize;
    return filteredCases.slice(start, start + casePageSize);
  }, [filteredCases, casePage, casePageSize, isPdfExport]);

  useEffect(() => {
    if (casePage > totalCasePages) setCasePage(1);
  }, [totalCasePages, casePage]);

  // Helper to determine portal state and badge
  const getPortalInfo = (countyName?: string, websiteUrl?: string) => {
    const c = (countyName || "").toLowerCase();
    const u = (websiteUrl || "").toLowerCase();
    let state: "FL" | "TX" | "OTHER" = "OTHER";
    if (
      c.includes("broward") ||
      c.includes("hillsborough") ||
      c.includes("miami") ||
      u.includes("browardclerk") ||
      u.includes("hillsclerk") ||
      u.includes("miamidade")
    ) {
      state = "FL";
    } else if (
      c.includes("dallas") ||
      c.includes("travis") ||
      c.includes("harris") ||
      u.includes("dallascounty") ||
      u.includes("traviscountytx") ||
      u.includes("harriscountytx") ||
      u.includes("cclerk.hctx") ||
      u.includes("hcdistrictclerk")
    ) {
      state = "TX";
    }
    const stateBadge = state === "FL" ? "FL - Florida" : state === "TX" ? "TX - Texas" : "Other Jurisdiction";
    const portalName = countyName || "County Portal";
    return { state, stateBadge, portalName };
  };

  // Group filtered cases by portal URL and name (FL-Florida / TX-Texas)
  const groupedCases = useMemo(() => {
    const groups: Record<
      string,
      {
        groupKey: string;
        portalName: string;
        state: "FL" | "TX" | "OTHER";
        stateBadge: string;
        websiteUrl?: string;
        cases: ScrapedCourtCase[];
      }
    > = {};
    filteredCases.forEach((c) => {
      const url = c.county_website || c.source_url || "";
      const info = getPortalInfo(c.county_name, url);
      const key = `${info.portalName} (${info.stateBadge})`;
      if (!groups[key]) {
        groups[key] = {
          groupKey: key,
          portalName: info.portalName,
          state: info.state,
          stateBadge: info.stateBadge,
          websiteUrl: url,
          cases: [],
        };
      }
      groups[key].cases.push(c);
    });
    return groups;
  }, [filteredCases]);

  // Filtered 8 Bots by Jurisdiction
  const filteredBots = useMemo(() => {
    if (!claim?.bots) return [];
    if (isPdfExport || botJurisdictionFilter === "all") return claim.bots;
    if (botJurisdictionFilter === "FL") {
      return claim.bots.filter((b) => b.name.includes("(FL)"));
    }
    return claim.bots.filter((b) => b.name.includes("(TX)"));
  }, [claim?.bots, botJurisdictionFilter, isPdfExport]);

  // Bot KPI Aggregations
  const botKpis = useMemo(() => {
    const bots = claim?.bots || [];
    const targeted = bots.filter((b) => b.target === "Yes").length;
    const completed = bots.filter((b) => b.status === "COMPLETED").length;
    const inProgress = bots.filter((b) => b.status === "IN_PROGRESS").length;
    const totalCases = bots.reduce((sum, b) => sum + (b.cases_found || 0), 0);
    return { total: bots.length, targeted, completed, inProgress, totalCases };
  }, [claim?.bots]);

  const togglePortalCollapse = (portalKey: string) => {
    setCollapsedPortals((prev) => ({
      ...prev,
      [portalKey]: !prev[portalKey],
    }));
  };

  const portalKeys = Object.keys(claim?.action_timings?.portals || {});

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col min-h-screen w-full">
        <Navbar />
        <div className="p-12 text-center text-slate-500 dark:text-slate-400 text-xs flex flex-col items-center justify-center gap-3 my-auto">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-500" />
          <span>Loading claim 360 & RPA telemetry...</span>
        </div>
      </div>
    );
  }

  if (notFound || !claim) {
    return (
      <div className="flex-1 flex flex-col min-h-screen w-full">
        <Navbar />
        <div className="p-8 sm:p-12 text-center flex flex-col items-center justify-center gap-4 max-w-md mx-auto my-auto">
          <div className="w-14 h-14 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 flex items-center justify-center text-rose-500">
            <AlertCircle className="w-7 h-7" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Claim Record Not Found</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            The requested claim ID <code className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-900 font-mono text-indigo-600 dark:text-indigo-400">{claimId}</code> does not exist or may have been purged during a database reset.
          </p>
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={() => router.push("/monitor")}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors cursor-pointer"
            >
              ← Back to Queue Monitor
            </button>
            <button
              onClick={fetchClaim}
              className="px-4 py-2 bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex-1 flex flex-col min-h-screen w-full ${isPdfExport ? "bg-slate-950 text-slate-100" : ""}`}>
      {!isPdfExport && <Navbar onRefresh={fetchClaim} isRefreshing={isLoading} />}

      <main id="claim-detail-container" className="p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none flex-1 transition-colors">
        {/* Executive PDF Report Header */}
        {isPdfExport && (
          <div className="border-b border-slate-800 pb-5 mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-sky-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/20">
                U
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
                  <span>UAIC Claim & RPA Orchestration Audit Report</span>
                  <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
                    OFFICIAL AUDIT REPORT
                  </span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">
                  United Automobile Insurance Company • Automated Court Docket Harvesting & Telemetry Audit
                </p>
              </div>
            </div>
            <div className="text-right font-mono">
              <div className="text-sm font-bold text-indigo-400">Claim #{claim.claim_number}</div>
              <div className="text-[10px] text-slate-400">Report Date: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</div>
              <div className="text-[10px] text-emerald-400 font-medium">Confidential Insurance Record</div>
            </div>
          </div>
        )}

        {/* Navigation & Header */}
        <div className="space-y-4 w-full">
          {!isPdfExport && (
            <div className="no-print flex items-center justify-between">
              <button
                onClick={() => router.push("/monitor")}
                className="text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center gap-1.5 transition-colors cursor-pointer min-h-[36px]"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                Back to Queue Monitor
              </button>
              <div className="flex items-center gap-2 text-xs font-mono text-slate-600 dark:text-slate-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Real-Time Telemetry Connected</span>
              </div>
            </div>
          )}

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 w-full bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs dark:shadow-lg backdrop-blur-md transition-colors">
            <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                  {claim.policy_state || "FL"}
                </span>
                <h2 className="text-xl md:text-2xl font-black font-mono text-slate-900 dark:text-slate-100 tracking-tight">
                  {claim.claim_number}
                </h2>
              </div>
              <div title="Claim Automation Lifecycle Status">
                <StatusBadge status={claim.record_status} />
              </div>
              {/* Contextual Fuzzy Match Engine Status Badge */}
              {(() => {
                const status = claim.fuzzy_match_status;
                if (status === "COMPLETED" || (status as string) === "MATCH_FOUND") {
                  return (
                    <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 flex items-center gap-1.5 shadow-xs" title="Fuzzy match engine confirmed high-confidence court record match">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500 dark:text-emerald-400" />
                      <span>Matcher: Match Confirmed</span>
                    </span>
                  );
                }
                if (status === "IN_PROGRESS") {
                  return (
                    <span className="text-xs px-2.5 py-1 rounded-full bg-amber-50 dark:bg-amber-950/70 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 flex items-center gap-1.5 animate-pulse shadow-xs" title="RapidFuzz engine currently matching party names & DOL">
                      <Sparkles className="w-3 h-3 text-amber-500 dark:text-amber-400" />
                      <span>Matcher: Evaluating...</span>
                    </span>
                  );
                }
                if (status === "PENDING_REVIEW") {
                  return (
                    <span className="text-xs px-2.5 py-1 rounded-full bg-purple-50 dark:bg-purple-950/70 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 flex items-center gap-1.5 shadow-xs" title="Borderline match score (40-60%) requiring adjuster review">
                      <AlertTriangle className="w-3 h-3 text-purple-500 dark:text-purple-400" />
                      <span>Matcher: Needs Review</span>
                    </span>
                  );
                }
                if (status === "NO_MATCH_FOUND") {
                  return (
                    <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 flex items-center gap-1.5 shadow-xs" title="No public court cases matched party criteria">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 dark:bg-slate-500" />
                      <span>Matcher: No Match</span>
                    </span>
                  );
                }
                // Default: NEW / Queued (scrapers have not finished yet)
                return (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-900/80 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 flex items-center gap-1.5 shadow-xs" title="Fuzzy matching will automatically trigger after scrapers finish">
                    <Sparkles className="w-3 h-3 text-indigo-500 dark:text-indigo-400" />
                    <span>Matcher: Queued</span>
                  </span>
                );
              })()}
              {claim.exposure_number && (
                <span className="text-xs px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-700">
                  Exposure: {claim.exposure_number}
                </span>
              )}
            </div>

            {/* Action Buttons & Exports */}
            {!isPdfExport && (
              <div className="no-print flex items-center gap-2 flex-wrap w-full lg:w-auto">
                {/* Retry Failed Portals Only (if any portal failed) */}
                {failedPortals.length > 0 && (
                  <button
                    onClick={handleRetryFailedPortals}
                    disabled={isRetryingFailed || isStartingAutomation}
                    className="flex-1 sm:flex-initial px-3.5 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold rounded-lg shadow-sm shadow-amber-600/20 transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50 min-h-[40px]"
                    title={`Retry only the ${failedPortals.length} failed portal(s): ${failedPortals.map((p) => p.name).join(", ")}`}
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isRetryingFailed ? "animate-spin" : ""}`} />
                    <span>{isRetryingFailed ? "Retrying..." : `Retry Failed Portals (${failedPortals.length})`}</span>
                  </button>
                )}

                {/* Start Automation */}
                <button
                  onClick={handleStartAutomation}
                  disabled={isStartingAutomation || isRetryingFailed}
                  className="flex-1 sm:flex-initial px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-sm shadow-emerald-600/20 transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50 min-h-[40px]"
                  title="Trigger automated court scraping across all targeted portals"
                >
                  <Play className={`w-3.5 h-3.5 ${isStartingAutomation ? "animate-spin" : ""}`} />
                  <span>{isStartingAutomation ? "Starting..." : "Start Automation"}</span>
                </button>

                {/* Single Claim Exports Toolbar */}
                <div className="flex items-center bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 min-h-[40px]">
                  <span className="text-[11px] text-slate-600 dark:text-slate-400 px-2 font-medium flex items-center gap-1">
                    <Download className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" /> Export:
                  </span>
                  <button
                    onClick={(e) => handleExportClaim("xlsx", e)}
                    disabled={!!downloadingFormat}
                    className="px-2 py-1.5 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors flex items-center gap-1 cursor-pointer disabled:opacity-50"
                    title="Export full claim report to Excel (.xlsx)"
                  >
                    {downloadingFormat === "xlsx" ? (
                      <RefreshCw className="w-3 h-3 animate-spin text-emerald-500" />
                    ) : (
                      <FileSpreadsheet className="w-3 h-3" />
                    )}
                    <span>{downloadingFormat === "xlsx" ? "Excel..." : "Excel"}</span>
                  </button>
                  <button
                    onClick={(e) => handleExportClaim("csv", e)}
                    disabled={!!downloadingFormat}
                    className="px-2 py-1.5 text-[11px] font-semibold text-sky-700 dark:text-sky-400 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors flex items-center gap-1 cursor-pointer disabled:opacity-50"
                    title="Export court cases to CSV (.csv)"
                  >
                    {downloadingFormat === "csv" ? (
                      <RefreshCw className="w-3 h-3 animate-spin text-sky-500" />
                    ) : (
                      <FileText className="w-3 h-3" />
                    )}
                    <span>{downloadingFormat === "csv" ? "CSV..." : "CSV"}</span>
                  </button>
                  <button
                    onClick={(e) => handleExportClaim("pdf", e)}
                    disabled={!!downloadingFormat}
                    className="px-2 py-1.5 text-[11px] font-semibold text-rose-700 dark:text-rose-400 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors flex items-center gap-1 cursor-pointer disabled:opacity-50"
                    title="Download high-fidelity PDF report directly"
                  >
                    {downloadingFormat === "pdf" ? (
                      <RefreshCw className="w-3 h-3 animate-spin text-rose-500" />
                    ) : (
                      <FileText className="w-3 h-3" />
                    )}
                    <span>{downloadingFormat === "pdf" ? "PDF..." : "PDF"}</span>
                  </button>
                  <button
                    onClick={(e) => handleExportClaim("json", e)}
                    disabled={!!downloadingFormat}
                    className="px-2 py-1.5 text-[11px] font-semibold text-amber-700 dark:text-amber-400 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors flex items-center gap-1 cursor-pointer disabled:opacity-50"
                    title="Export complete claim & telemetry JSON"
                  >
                    {downloadingFormat === "json" ? (
                      <RefreshCw className="w-3 h-3 animate-spin text-amber-500" />
                    ) : (
                      <Code className="w-3 h-3" />
                    )}
                    <span>{downloadingFormat === "json" ? "JSON..." : "JSON"}</span>
                  </button>
                </div>

                {/* Edit Claim */}
                <button
                  onClick={() => setIsEditOpen(true)}
                  className="px-3.5 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer min-h-[40px]"
                >
                  <Edit3 className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
                  <span>Edit</span>
                </button>

                {/* Delete Claim */}
                <button
                  onClick={() => setIsDeleteOpen(true)}
                  className="px-3.5 py-2 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer min-h-[40px]"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete</span>
                </button>

                {/* Push to Guidewire */}
                <button
                  onClick={handlePushGuidewire}
                  disabled={isPushingGuidewire}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 min-h-[40px]"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{isPushingGuidewire ? "Pushing..." : "Push to Guidewire"}</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Feedback alert */}
        {feedback && (
          <div
            className={`w-full max-w-full overflow-hidden rounded-xl p-3.5 text-xs flex items-center justify-between gap-2 border transition-all shadow-xs ${
              feedback.type === "success"
                ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-300"
                : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-900 dark:text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {feedback.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
              )}
              <span className="font-medium min-w-0 break-words flex-1">{feedback.msg}</span>
            </div>
            <button
              onClick={() => setFeedback(null)}
              className="text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 p-1 rounded-md transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Claim 360 Information Card */}
        <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-sm w-full transition-colors">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200 flex items-center gap-2">
              <Building className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
              Claim 360 Ingestion & Policy Context
            </h3>
            <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
              ID: {claim.id.slice(0, 13)}...
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4 text-xs">
            <div className="p-3 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Primary Key</span>
              <p className="font-semibold font-mono text-slate-900 dark:text-slate-200 text-sm mt-0.5">{claim.primary_key || "-"}</p>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Exposure Number</span>
              <p className="font-semibold font-mono text-slate-900 dark:text-slate-200 text-sm mt-0.5">{claim.exposure_number || "1"}</p>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Date of Loss (DOL)</span>
              <p className="font-semibold text-slate-900 dark:text-slate-200 text-sm mt-0.5">{claim.dol || "-"}</p>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Insured Party</span>
              <p className="font-semibold text-slate-900 dark:text-slate-200 text-sm mt-0.5 truncate">{claim.insured_name || "-"}</p>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Claimant Party</span>
              <p className="font-semibold text-slate-900 dark:text-slate-200 text-sm mt-0.5 truncate">{claim.claimant_name || "-"}</p>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 rounded-xl">
              <span className="text-slate-500 block text-[11px]">Driver (Insured Vehicle)</span>
              <p className="font-semibold text-slate-900 dark:text-slate-200 text-sm mt-0.5 truncate">{claim.driver_name || "-"}</p>
            </div>
          </div>

          <div className="border-t border-slate-200 dark:border-slate-800 pt-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-500">Loss Location:</span>
              <p className="font-medium text-slate-800 dark:text-slate-300 mt-0.5">
                {[claim.loss_location_state].filter(Boolean).join(", ") || "-"}
              </p>
            </div>
            <div>
              <span className="text-slate-500">Policy State:</span>
              <p className="font-medium text-slate-800 dark:text-slate-300 mt-0.5">{claim.policy_state || "-"}</p>
            </div>
            <div>
              <span className="text-slate-500">Created At:</span>
              <p className="font-medium text-slate-800 dark:text-slate-300 mt-0.5">{formatDate(claim.created_at)}</p>
            </div>
            <div>
              <span className="text-slate-500">Guidewire Activity ID:</span>
              <p className="font-mono font-bold text-indigo-600 dark:text-indigo-400 mt-0.5">{claim.activity_id || "None (Standby)"}</p>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 1. DETAILED STAGE EXECUTION TELEMETRY (ENHANCED) */}
        {/* ========================================================================= */}
        <div className="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-md w-full transition-colors">
          {/* Section Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Detailed Stage Execution Telemetry
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800">
                  Live Microsecond Clock
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                High-resolution timing breakdown per stage with microsecond precision, CAPTCHA solver telemetry, and database commit metrics.
              </p>
            </div>

            <div className="flex items-center gap-3 self-start sm:self-auto">
              <div className="bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800 rounded-xl px-4 py-2 flex items-center gap-2">
                <span className="text-xs font-medium text-indigo-700 dark:text-indigo-300">Total Duration:</span>
                <span className="text-base font-bold font-mono text-indigo-900 dark:text-indigo-200">
                  {claim.total_duration_seconds !== null && claim.total_duration_seconds !== undefined
                    ? `${claim.total_duration_seconds}s`
                    : claim.action_timings?.total_scraping_seconds
                    ? `${claim.action_timings.total_scraping_seconds}s`
                    : "Pending"}
                </span>
              </div>
            </div>
          </div>

          {/* Multi-Portal Telemetry Switcher Tabs */}
          <div className="flex items-center justify-between flex-wrap gap-2 pt-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mr-1">
                <Layers className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" /> Portal Scope:
              </span>

              <button
                onClick={() => setSelectedPortalTelemetry("all")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer border ${
                  selectedPortalTelemetry === "all"
                    ? "bg-indigo-600 text-white border-indigo-500 shadow-sm"
                    : "bg-slate-100 dark:bg-slate-950/60 text-slate-700 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800"
                }`}
              >
                <Globe className="w-3.5 h-3.5" />
                <span>All Portals (Combined Summary)</span>
              </button>

              {portalKeys.map((k) => {
                const p = claim.action_timings?.portals?.[k];
                const isSelected = selectedPortalTelemetry === k;
                return (
                  <button
                    key={k}
                    onClick={() => setSelectedPortalTelemetry(k)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer border ${
                      isSelected
                        ? "bg-indigo-600 text-white border-indigo-500 shadow-sm"
                        : "bg-slate-100 dark:bg-slate-950/60 text-slate-700 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>{p?.portal_name || k}</span>
                    {p?.duration_seconds && (
                      <span className="text-[10px] font-mono opacity-80">({p.duration_seconds}s)</span>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="text-[11px] text-slate-500 font-mono">
              Viewing: <strong className="text-slate-800 dark:text-slate-300">{selectedPortalTelemetry === "all" ? "Combined Suite" : claim.action_timings?.portals?.[selectedPortalTelemetry]?.portal_name || selectedPortalTelemetry}</strong>
            </div>
          </div>

          {/* Sequential Process Flow Stepper Pipeline */}
          <div className="bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 overflow-x-auto">
            <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
              Automated Execution Pipeline Flow
            </div>

            <div className="flex items-center min-w-[760px] justify-between relative">
              {/* Stepper Connecting Track */}
              <div className="absolute top-1/2 left-4 right-4 h-0.5 bg-slate-200 dark:bg-slate-800 -translate-y-1/2 z-0" />

              {[
                { id: "1", key: "browser_launch", label: "Launch", icon: Globe },
                { id: "2", key: "website_navigation", label: "Navigate", icon: ExternalLink },
                { id: "3", key: "data_filling", label: "Data Entry", icon: Edit3 },
                { id: "4", key: "captcha", label: "CAPTCHA", icon: ShieldCheck },
                { id: "5", key: "submit", label: "Submit", icon: Search },
                { id: "6", key: "result_retrieval", label: "Retrieval", icon: Cpu },
                { id: "7", key: "database_save", label: "DB Commit", icon: Database },
                { id: "8", key: "fuzzy_matching", label: "RapidFuzz", icon: Sparkles },
                { id: "9", key: "guidewire_trigger", label: "Guidewire", icon: Send },
              ].map((step, idx) => {
                const stageData = activeStages[step.key];
                const isCompleted = stageData && stageData.status !== "FAILED";
                const isFailed = stageData && stageData.status === "FAILED";
                const isCurrent = !stageData && idx === 0 && claim.record_status === "SCRAPING_IN_PROGRESS";
                const duration = stageData?.duration_seconds ? `${stageData.duration_seconds}s` : "-";
                const Icon = step.icon;

                return (
                  <div
                    key={step.key}
                    onClick={() => stageData && setInspectedStage({ key: step.key, data: stageData })}
                    className="relative z-10 flex flex-col items-center group cursor-pointer transition-transform hover:scale-105"
                  >
                    <div
                      className={`w-9 h-9 rounded-full flex items-center justify-center border-2 transition-all ${
                        isCompleted
                          ? "bg-white dark:bg-slate-900 border-emerald-500 text-emerald-600 dark:text-emerald-400 shadow-md shadow-emerald-500/20"
                          : isFailed
                          ? "bg-white dark:bg-slate-900 border-rose-500 text-rose-600 dark:text-rose-400"
                          : isCurrent
                          ? "bg-white dark:bg-slate-900 border-indigo-500 text-indigo-600 dark:text-indigo-400 animate-pulse"
                          : "bg-slate-100 dark:bg-slate-900 border-slate-300 dark:border-slate-800 text-slate-400 dark:text-slate-600"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 mt-1.5 text-center whitespace-nowrap">
                      {step.label}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.2 rounded mt-0.5 ${
                        stageData ? "text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-200 dark:border-indigo-900" : "text-slate-400 dark:text-slate-600"
                      }`}
                    >
                      {duration}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Horizontal Waterfall Latency Distribution Bar */}
          {waterfallData.length > 0 && (
            <div className="space-y-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-800 dark:text-slate-300 flex items-center gap-1.5">
                  <Flame className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                  Stage Latency Waterfall Distribution
                </span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                  Longest Phase:{" "}
                  <strong className="text-amber-600 dark:text-amber-400">
                    {waterfallData.reduce((max, cur) => (cur.duration > max.duration ? cur : max), waterfallData[0])?.name} (
                    {waterfallData.reduce((max, cur) => (cur.duration > max.duration ? cur : max), waterfallData[0])?.duration}s)
                  </strong>
                </span>
              </div>

              {/* Multi-segment Progress Bar */}
              <div className="h-3 w-full bg-slate-200 dark:bg-slate-900 rounded-full overflow-hidden flex gap-0.5 p-0.5 border border-slate-300 dark:border-slate-800">
                {waterfallData.map((item) => (
                  <div
                    key={item.key}
                    style={{ width: `${Math.max(item.percentage, 2)}%` }}
                    className={`${item.color} h-full rounded-xs transition-all hover:brightness-125 cursor-pointer relative group`}
                    title={`${item.name}: ${item.duration}s (${item.percentage.toFixed(1)}%)`}
                  />
                ))}
              </div>

              {/* Waterfall Legend */}
              <div className="flex items-center gap-3 flex-wrap pt-1 text-[11px] font-mono">
                {waterfallData.map((item) => (
                  <div
                    key={item.key}
                    onClick={() => item.stage && setInspectedStage({ key: item.key, data: item.stage })}
                    className="flex items-center gap-1.5 cursor-pointer hover:underline text-slate-700 dark:text-slate-300"
                  >
                    <span className={`w-2 h-2 rounded-full ${item.color}`} />
                    <span>{item.label}:</span>
                    <strong className="text-slate-900 dark:text-slate-100">{item.duration}s</strong>
                    <span className="text-slate-500">({item.percentage.toFixed(0)}%)</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 9 Detailed Execution Telemetry Cards Grid (3x3 on large screens) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {/* 1. Browser Launch */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-sky-500 dark:text-sky-400" /> 1. Browser Launch
                </span>
                <span className="font-mono font-bold text-sky-600 dark:text-sky-400">
                  {activeStages.browser_launch?.duration_seconds ? `${activeStages.browser_launch.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Time: {activeStages.browser_launch?.start_time || "-"} - {activeStages.browser_launch?.end_time || "-"}</div>
                <div className="truncate">{activeStages.browser_launch?.detail || "Google Chrome (Attended GUI) + AntiCaptcha"}</div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Status: {activeStages.browser_launch?.status || "SUCCESS"}</span>
                {activeStages.browser_launch && (
                  <button
                    onClick={() => setInspectedStage({ key: "browser_launch", data: activeStages.browser_launch })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 2. Website Navigation */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <ExternalLink className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" /> 2. Navigation
                </span>
                <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                  {activeStages.website_navigation?.duration_seconds ? `${activeStages.website_navigation.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Time: {activeStages.website_navigation?.start_time || "-"} - {activeStages.website_navigation?.end_time || "-"}</div>
                <div className="truncate" title={activeStages.website_navigation?.url || "Portal DOM load"}>
                  {activeStages.website_navigation?.url || "Portal DOM load"}
                </div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">HTTP: 200 OK</span>
                {activeStages.website_navigation && (
                  <button
                    onClick={() => setInspectedStage({ key: "website_navigation", data: activeStages.website_navigation })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 3. Data Entry */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Edit3 className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" /> 3. Data Entry
                </span>
                <span className="font-mono font-bold text-amber-600 dark:text-amber-400">
                  {activeStages.data_filling?.duration_seconds ? `${activeStages.data_filling.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Time: {activeStages.data_filling?.start_time || "-"} - {activeStages.data_filling?.end_time || "-"}</div>
                <div className="truncate">
                  {activeStages.data_filling?.party ? `Party: ${activeStages.data_filling.party}` : "Party & DOL query entered"}
                </div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-slate-500 dark:text-slate-400">DualSearch Strategy</span>
                {activeStages.data_filling && (
                  <button
                    onClick={() => setInspectedStage({ key: "data_filling", data: activeStages.data_filling })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 4. CAPTCHA Defense */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" /> 4. CAPTCHA Defense
                </span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                  {activeStages.captcha?.duration_seconds ? `${activeStages.captcha.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Solver: {activeStages.captcha?.solver || "AntiCaptcha Plugin v0.83"}</div>
                <div className="text-emerald-600 dark:text-emerald-400 font-bold">Status: {activeStages.captcha?.status || "SUCCESS"}</div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-slate-500 dark:text-slate-400">Turnstile / reCAPTCHA</span>
                {activeStages.captcha && (
                  <button
                    onClick={() => setInspectedStage({ key: "captcha", data: activeStages.captcha })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 5. Submit */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Search className="w-3.5 h-3.5 text-blue-500 dark:text-blue-400" /> 5. Submit Search
                </span>
                <span className="font-mono font-bold text-blue-600 dark:text-blue-400">
                  {activeStages.submit?.duration_seconds ? `${activeStages.submit.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Time: {activeStages.submit?.start_time || "-"} - {activeStages.submit?.end_time || "-"}</div>
                <div>DOM Form / Button Triggered</div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-slate-500 dark:text-slate-400">Trigger: #PersonSearchResults</span>
                {activeStages.submit && (
                  <button
                    onClick={() => setInspectedStage({ key: "submit", data: activeStages.submit })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 6. Result Retrieval */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-purple-500 dark:text-purple-400" /> 6. Record Retrieval
                </span>
                <span className="font-mono font-bold text-purple-600 dark:text-purple-400">
                  {activeStages.result_retrieval?.duration_seconds ? `${activeStages.result_retrieval.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Category: <strong className="text-slate-800 dark:text-slate-200">{activeStages.result_retrieval?.result_category || (claim.court_cases.length > 0 ? "Data Found" : "No Record")}</strong></div>
                <div>{claim.court_cases.length} cases extracted across pages</div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-slate-500 dark:text-slate-400">Pagination Parsed</span>
                {activeStages.result_retrieval && (
                  <button
                    onClick={() => setInspectedStage({ key: "result_retrieval", data: activeStages.result_retrieval })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 7. Database Save */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-teal-500 dark:text-teal-400" /> 7. Database Commit
                </span>
                <span className="font-mono font-bold text-teal-600 dark:text-teal-400">
                  {activeStages.database_save?.duration_seconds ? `${activeStages.database_save.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Time: {activeStages.database_save?.start_time || "-"} - {activeStages.database_save?.end_time || "-"}</div>
                <div>ACID Transaction Committed to SQLite</div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-teal-600 dark:text-teal-400 font-semibold">Cases Saved: {claim.court_cases.length}</span>
                {activeStages.database_save && (
                  <button
                    onClick={() => setInspectedStage({ key: "database_save", data: activeStages.database_save })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 8. RapidFuzz Match Engine */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-fuchsia-500 dark:text-fuchsia-400" /> 8. RapidFuzz Matcher
                </span>
                <span className="font-mono font-bold text-fuchsia-600 dark:text-fuchsia-400">
                  {activeStages.fuzzy_matching?.duration_seconds ? `${activeStages.fuzzy_matching.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Engine: <strong className="text-slate-800 dark:text-slate-200">RapidFuzz Token Sort (Threshold: 60%)</strong></div>
                <div>
                  Status: <strong className={claim.fuzzy_match_status === "COMPLETED" ? "text-emerald-600 dark:text-emerald-400" : claim.fuzzy_match_status === "PENDING_REVIEW" ? "text-amber-600 dark:text-amber-400" : "text-slate-700 dark:text-slate-300"}>{claim.fuzzy_match_status || "PENDING"}</strong>
                </div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-slate-500 dark:text-slate-400">Matches: {claim.final_matched_json ? "Match Confirmed" : "0 Pairs"}</span>
                {activeStages.fuzzy_matching && (
                  <button
                    onClick={() => setInspectedStage({ key: "fuzzy_matching", data: activeStages.fuzzy_matching })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>

            {/* 9. Guidewire 2-Way Sync */}
            <div className="p-3.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 text-xs relative group hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Send className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" /> 9. Guidewire 2-Way Sync
                </span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                  {activeStages.guidewire_trigger?.duration_seconds ? `${activeStages.guidewire_trigger.duration_seconds}s` : "-"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono space-y-0.5">
                <div>Activity ID: <strong className="text-slate-800 dark:text-slate-200 font-mono">{claim.activity_id || "Awaiting Match"}</strong></div>
                <div className="truncate" title={activeStages.guidewire_trigger?.detail || "Dispatched on match"}>
                  {activeStages.guidewire_trigger?.detail || "Dispatched on verified court match"}
                </div>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-900 flex items-center justify-between text-[10px]">
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{claim.activity_id ? "Dispatched (200 OK)" : "Standby Queue"}</span>
                {activeStages.guidewire_trigger && (
                  <button
                    onClick={() => setInspectedStage({ key: "guidewire_trigger", data: activeStages.guidewire_trigger })}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-mono cursor-pointer"
                  >
                    Inspect Telemetry →
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Granular County Portal Timeline Breakdown Table */}
          {portalKeys.length > 0 && (
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
                Individual County Portal Scraping Breakdown:
              </h4>
              <div className="divide-y divide-slate-200 dark:divide-slate-800/80 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                {Object.entries(claim.action_timings?.portals || {}).map(([key, p]: [string, any]) => (
                  <div key={key} className="p-3 bg-slate-50/70 dark:bg-slate-950/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-indigo-500" />
                      <span className="font-semibold text-slate-900 dark:text-slate-200">{p.portal_name}</span>
                      <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">({p.cases_found} cases extracted)</span>
                      {p.url && (
                        <a
                          href={p.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-400 hover:text-indigo-600 dark:text-slate-500 dark:hover:text-indigo-400"
                          title="Open portal URL"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                      <span>Status: <strong className="text-slate-900 dark:text-slate-100">{p.status}</strong></span>
                      <span className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-200 dark:border-indigo-900">
                        ⏱️ {p.duration_seconds}s
                      </span>
                      <span className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-200 dark:border-emerald-900">
                        📁 {p.cases_found ?? 0} Cases Found
                      </span>
                      <button
                        onClick={() => {
                          setSelectedPortalTelemetry(key);
                          setInspectedStage({
                            key: p.portal_name || key,
                            data: {
                              portal_key: key,
                              portal_name: p.portal_name,
                              status: p.status,
                              duration_seconds: p.duration_seconds,
                              cases_found: p.cases_found,
                              start_time: p.start_time,
                              end_time: p.end_time,
                              url: p.url,
                              stages: p.stages || {},
                            },
                          });
                        }}
                        className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 underline text-[11px] cursor-pointer"
                      >
                        View Stages
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* 2. COUNTY COURT PORTAL SCRAPER EXECUTION STATUS (8 BOTS) (ENHANCED) */}
        {/* ========================================================================= */}
        <div className="space-y-4 w-full">
          {/* Section Header with KPI Strip and Jurisdiction Filters */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-5">
            <div>
              <div className="flex items-center gap-2">
                <Building className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  County Court Portal Scraper Execution Status (8 Bots)
                </h3>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                Active status across all 8 multi-state clerk scrapers. Click &quot;Run Bot&quot; on any portal to execute on-demand.
              </p>
            </div>

            {/* Jurisdiction filter buttons, View Switcher & Action Triggers */}
            {!isPdfExport && (
              <div className="no-print flex items-center gap-2 flex-wrap">
                {/* Jurisdiction Tabs */}
                <div className="flex items-center bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg p-1">
                  <button
                    onClick={() => setBotJurisdictionFilter("all")}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                      botJurisdictionFilter === "all" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                  >
                    All (8 Bots)
                  </button>
                  <button
                    onClick={() => setBotJurisdictionFilter("FL")}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                      botJurisdictionFilter === "FL" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                  >
                    Florida (3 Bots)
                  </button>
                  <button
                    onClick={() => setBotJurisdictionFilter("TX")}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                      botJurisdictionFilter === "TX" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                  >
                    Texas (5 Bots)
                  </button>
                </div>

                {/* View Mode Toggle */}
                <div className="flex items-center bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg p-1">
                  <button
                    onClick={() => setBotViewMode("grid")}
                    className={`px-2.5 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                      botViewMode === "grid" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                    title="Grid card view"
                  >
                    <Building className="w-3.5 h-3.5" />
                    <span>Cards</span>
                  </button>
                  <button
                    onClick={() => setBotViewMode("timeline")}
                    className={`px-2.5 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                      botViewMode === "timeline" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                    title="Concurrent Execution Timeline"
                  >
                    <BarChart3 className="w-3.5 h-3.5" />
                    <span>Timeline</span>
                  </button>
                </div>

                {/* Automation Trigger Buttons */}
                {failedPortals.length > 0 && (
                  <button
                    onClick={handleRetryFailedPortals}
                    disabled={isRetryingFailed || isStartingAutomation || isStartingAllBots}
                    className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 border border-amber-500 text-white text-xs font-semibold rounded-lg shadow-sm shadow-amber-600/20 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 min-h-[34px]"
                    title={`Retry only the ${failedPortals.length} failed portal(s): ${failedPortals.map((p) => p.name).join(", ")}`}
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isRetryingFailed ? "animate-spin" : ""}`} />
                    <span>{isRetryingFailed ? "Retrying..." : `Retry Failed (${failedPortals.length})`}</span>
                  </button>
                )}

                <button
                  onClick={handleStartAutomation}
                  disabled={isStartingAutomation || isStartingAllBots || isRetryingFailed}
                  className="px-3 py-1.5 bg-indigo-600/90 hover:bg-indigo-500 border border-indigo-500 text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 min-h-[34px]"
                  title="Run policy-targeted bots (e.g. 3 Florida bots for FL claim)"
                >
                  <Play className={`w-3.5 h-3.5 ${isStartingAutomation ? "animate-spin" : ""}`} />
                  <span>{isStartingAutomation ? "Starting..." : "Run Targeted"}</span>
                </button>

                <button
                  onClick={handleRunAllBots}
                  disabled={isStartingAllBots || isStartingAutomation}
                  className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 min-h-[34px]"
                  title="Force execute all 8 portals concurrently across Florida & Texas"
                >
                  <RefreshCw className={`w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400 ${isStartingAllBots ? "animate-spin" : ""}`} />
                  <span>{isStartingAllBots ? "Starting 8 Bots..." : "Run All 8 Bots"}</span>
                </button>
              </div>
            )}
          </div>

          {/* High-Level Bot Metrics Ribbon using reusable StatCards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-xs">
            <StatCard
              label="Total Portals"
              value={botKpis.total}
              subtext="8 County scrapers"
              icon={Building}
              gradient="indigo"
            />
            <StatCard
              label="Targeted"
              value={`${botKpis.targeted} Bots`}
              subtext="Policy geography"
              icon={Crosshair}
              gradient="blue"
            />
            <StatCard
              label="Completed"
              value={botKpis.completed}
              subtext="Execution finished"
              icon={CheckCircle2}
              gradient="emerald"
            />
            <StatCard
              label="Running Now"
              value={botKpis.inProgress}
              subtext={botKpis.inProgress > 0 ? "Active in real-time" : "None active"}
              icon={RefreshCw}
              gradient="amber"
            />
            <StatCard
              label="Total Cases Found"
              value={botKpis.totalCases}
              subtext="Extracted records"
              icon={Layers}
              gradient="purple"
            />
            <StatCard
              label="Scrape Time"
              value={
                claim.action_timings?.total_scraping_seconds
                  ? `${claim.action_timings.total_scraping_seconds}s`
                  : claim.total_duration_seconds
                  ? `${claim.total_duration_seconds}s`
                  : "-"
              }
              subtext="Total execution window"
              icon={Clock}
              gradient="cyan"
            />
          </div>

          {/* Conditional View: 1. Execution Timeline (Gantt) OR 2. Grid Cards */}
          {botViewMode === "timeline" ? (
            <div className="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between text-xs border-b border-slate-200 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                  <span className="font-bold text-slate-900 dark:text-slate-200">Concurrent Multi-Portal Scraping Timeline</span>
                  <span className="text-slate-500 font-mono text-[11px] hidden sm:inline">(Normalized by total execution window)</span>
                </div>
                <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
                  Total Window: <strong className="text-indigo-600 dark:text-indigo-400">{claim.action_timings?.total_scraping_seconds || claim.total_duration_seconds || 18.45}s</strong>
                </div>
              </div>

              <div className="space-y-3">
                {filteredBots.map((bot) => {
                  const portalKey = Object.keys(claim.action_timings?.portals || {}).find(
                    (k) => (claim.action_timings?.portals?.[k]?.portal_name || "").toLowerCase().includes(bot.name.toLowerCase().split(" ")[0])
                  );
                  const pTiming = portalKey ? claim.action_timings?.portals?.[portalKey] : null;
                  const isFL = bot.name.includes("(FL)");
                  const totalSecs = claim.action_timings?.total_scraping_seconds || claim.total_duration_seconds || 20;
                  const botSecs = pTiming?.duration_seconds ? Number(pTiming.duration_seconds) : 0;
                  const widthPct = totalSecs > 0 && botSecs > 0 ? Math.min(Math.max((botSecs / totalSecs) * 100, 10), 100) : 0;
                  const isRunningThis = runningBotKey && bot.name.toLowerCase().includes(runningBotKey);

                  const clerkBadge = {
                    "Broward County (FL)": "BrowardClerk Web2",
                    "Hillsborough County (FL)": "HOVER Search",
                    "Miami-Dade County (FL)": "Miami OCS",
                    "Travis County (TX)": "Odyssey Portal",
                    "Dallas County (TX)": "Odyssey Portal",
                    "Harris County JP (TX)": "Odyssey JP",
                    "Harris County Clerk (TX)": "HCTX CCLERK",
                    "Harris District Clerk (TX)": "HCTX eDocs",
                  }[bot.name] || "Portal";

                  return (
                    <div key={bot.name} className="flex flex-col md:flex-row md:items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 text-xs">
                      <div className="w-full md:w-64 shrink-0 flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${isFL ? "bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-400 border border-indigo-300 dark:border-indigo-900" : "bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-400 border border-teal-300 dark:border-teal-900"}`}>
                            {isFL ? "FL" : "TX"}
                          </span>
                          <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[130px]">{bot.name}</span>
                          <span className="text-[10px] font-mono text-slate-500">({clerkBadge})</span>
                        </div>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                          bot.target === "Yes" ? "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800" : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700"
                        }`}>
                          {bot.target === "Yes" ? "Target: Yes" : "Target: No"}
                        </span>
                      </div>

                      <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full">
                        <div className="h-7 flex-1 min-w-0 bg-slate-200 dark:bg-slate-900/80 rounded-lg p-1 relative overflow-hidden border border-slate-300 dark:border-slate-800 flex items-center">
                          {bot.status === "COMPLETED" && botSecs > 0 ? (
                            <div
                              style={{ width: `${widthPct}%`, minWidth: "120px" }}
                              className="h-full bg-gradient-to-r from-indigo-600 via-sky-500 to-emerald-500 rounded flex items-center px-2 text-[10px] font-mono font-bold text-white transition-all shadow-sm shadow-emerald-500/20 whitespace-nowrap overflow-hidden text-ellipsis"
                            >
                              ⏱️ {botSecs}s ({bot.cases_found} cases found)
                            </div>
                          ) : bot.status === "IN_PROGRESS" || isRunningThis ? (
                            <div className="h-full w-full bg-gradient-to-r from-amber-600 to-amber-400 animate-pulse rounded flex items-center px-2 text-[10px] font-mono font-bold text-slate-950 whitespace-nowrap">
                              <RefreshCw className="w-3 h-3 animate-spin mr-1.5" /> Scraping active in real-time...
                            </div>
                          ) : (
                            <div className="h-full w-full border border-dashed border-slate-300 dark:border-slate-800/80 rounded flex items-center px-2 text-[10px] font-mono text-slate-500 whitespace-nowrap">
                              Standby — Non-target portal for policy geography
                            </div>
                          )}
                        </div>

                        <div className="shrink-0 flex items-center justify-end gap-2">
                          <StatusBadge
                            status={bot.status === "NOT_TRIGGERED" ? (bot.target === "Yes" ? "READY" : "STANDBY") : bot.status}
                            size="sm"
                          />
                          {!isPdfExport && (
                            <button
                              onClick={() => handleRunSingleBot(bot.name)}
                              disabled={bot.status === "IN_PROGRESS" || !!runningBotKey}
                              className="no-print px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-[11px] font-semibold rounded border border-slate-300 dark:border-slate-700 transition-colors flex items-center gap-1 cursor-pointer disabled:opacity-50"
                              title={`Run only ${bot.name}`}
                            >
                              <Play className={`w-3 h-3 text-emerald-500 dark:text-emerald-400 ${isRunningThis ? "animate-spin" : ""}`} />
                              <span>{isRunningThis ? "Running" : "Run"}</span>
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* 8 Bots Cards Responsive Grid */
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
              {filteredBots.map((bot) => {
                const portalKey = Object.keys(claim.action_timings?.portals || {}).find(
                  (k) => (claim.action_timings?.portals?.[k]?.portal_name || "").toLowerCase().includes(bot.name.toLowerCase().split(" ")[0])
                );
                const pTiming = portalKey ? claim.action_timings?.portals?.[portalKey] : null;
                const isFL = bot.name.includes("(FL)");
                const isInProgress = bot.status === "IN_PROGRESS";
                const isCompleted = bot.status === "COMPLETED";
                const isRunningThis = runningBotKey && bot.name.toLowerCase().includes(runningBotKey);

                const clerkBadge = {
                  "Broward County (FL)": "BrowardClerk Web2",
                  "Hillsborough County (FL)": "HOVER Search",
                  "Miami-Dade County (FL)": "Miami OCS",
                  "Travis County (TX)": "Odyssey Portal",
                  "Dallas County (TX)": "Odyssey Portal",
                  "Harris County JP (TX)": "Odyssey JP",
                  "Harris County Clerk (TX)": "HCTX CCLERK",
                  "Harris District Clerk (TX)": "HCTX eDocs",
                }[bot.name] || "Portal";

                return (
                  <div
                    key={bot.name}
                    className={`bg-white dark:bg-slate-900/50 border rounded-xl p-4 space-y-3.5 shadow-sm transition-all hover:border-slate-300 dark:hover:border-slate-700 relative overflow-hidden ${
                      isInProgress
                        ? "border-amber-500/80 ring-1 ring-amber-500/30"
                        : isCompleted
                        ? "border-emerald-500/40"
                        : "border-slate-200 dark:border-slate-800"
                    }`}
                  >
                    {/* Subtle Top Indicator Accent */}
                    <div
                      className={`absolute top-0 left-0 right-0 h-1 ${
                        isInProgress
                          ? "bg-amber-500 animate-pulse"
                          : isCompleted
                          ? "bg-emerald-500"
                          : bot.target === "Yes"
                          ? "bg-indigo-500"
                          : "bg-slate-200 dark:bg-slate-800"
                      }`}
                    />

                    {/* Card Header */}
                    <div className="flex items-center justify-between pt-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${isFL ? "bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-400 border border-indigo-300 dark:border-indigo-900" : "bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-400 border border-teal-300 dark:border-teal-900"}`}>
                          {isFL ? "FL" : "TX"}
                        </span>
                        <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          {bot.name}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-950 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800">
                          {clerkBadge}
                        </span>
                        {bot.website_url && (
                          <a
                            href={bot.website_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                            title={`Open ${bot.name} official portal (${bot.website_url})`}
                          >
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                          bot.target === "Yes"
                            ? "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                            : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700"
                        }`}
                      >
                        Target: {bot.target}
                      </span>
                    </div>

                    {/* Status & Cases Count */}
                    <div className="flex items-center justify-between text-xs pt-1">
                      <div className="flex items-center gap-1.5">
                        <StatusBadge
                          status={bot.status === "NOT_TRIGGERED" ? (bot.target === "Yes" ? "READY" : "STANDBY") : bot.status}
                          size="sm"
                        />
                        {isInProgress && (
                          <RefreshCw className="w-3 h-3 animate-spin text-amber-500 dark:text-amber-400" />
                        )}
                      </div>
                      <span className="text-[11px] font-mono text-slate-700 dark:text-slate-300 font-semibold">
                        {bot.cases_found} Cases Found
                      </span>
                    </div>

                    {/* Action Time Bar */}
                    {pTiming?.duration_seconds && (
                      <div className="pt-2 text-[10px] font-mono text-indigo-600 dark:text-indigo-400 flex items-center justify-between border-t border-slate-200 dark:border-slate-800">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Action Time:
                        </span>
                        <strong className="text-slate-800 dark:text-slate-200">{pTiming.duration_seconds}s</strong>
                      </div>
                    )}

                    {/* Interactive Quick Action Buttons */}
                    {!isPdfExport && (
                      <div className="no-print pt-2 border-t border-slate-200 dark:border-slate-800/80 flex items-center gap-1.5">
                        <button
                          onClick={() => handleRunSingleBot(bot.name)}
                          disabled={isInProgress || !!runningBotKey}
                          className="flex-1 px-2.5 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-[11px] font-semibold rounded-lg border border-slate-300 dark:border-slate-700 transition-colors flex items-center justify-center gap-1 cursor-pointer disabled:opacity-50"
                          title={`Run only ${bot.name} scraper`}
                        >
                          <Play className={`w-3 h-3 text-emerald-500 dark:text-emerald-400 ${isRunningThis ? "animate-spin" : ""}`} />
                          <span>{isRunningThis ? "Running..." : isCompleted ? "Re-run Bot" : "Run Bot"}</span>
                        </button>

                        {bot.cases_found > 0 && (
                          <button
                            onClick={() => {
                              const matchCounty = countyOptions.find((o) => o.value.toLowerCase().includes(bot.name.split(" ")[0].toLowerCase()))?.value || bot.name.split(" ")[0];
                              setCaseCountyFilters([matchCounty]);
                              const el = document.getElementById("scraped-cases-section");
                              el?.scrollIntoView({ behavior: "smooth" });
                            }}
                            className="px-2 py-1.5 bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-[11px] font-medium rounded-lg transition-colors cursor-pointer"
                            title="Filter cases table to this county"
                          >
                            View Cases ({bot.cases_found}) ↓
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* 2.5. PORTAL FAILURE SCREENSHOTS & OPERATOR DIAGNOSTICS */}
        {/* ========================================================================= */}
        <div id="error-screenshots-section" className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-sm w-full transition-colors">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-900/50 flex items-center justify-center text-rose-600 dark:text-rose-400">
                  <Camera className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                      Portal Failure Screenshots & Operator Diagnostics
                    </h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      screenshots.length > 0 
                        ? "bg-rose-100 dark:bg-rose-950/80 text-rose-700 dark:text-rose-300 border border-rose-300 dark:border-rose-800" 
                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    }`}>
                      {screenshots.length}
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 pl-10.5">
                Real-time browser viewport snapshots and failure telemetry captured at the exact moment a scraper bot encountered an exception or challenge timeout.
              </p>
            </div>

            <div className="flex items-center gap-2">
              {failedPortals.length > 0 && (
                <button
                  onClick={handleRetryFailedPortals}
                  disabled={isRetryingFailed}
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-600 hover:bg-amber-500 text-white shadow-sm shadow-amber-600/20 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title={`Retry all currently failed portals: ${failedPortals.map((p) => p.name).join(", ")}`}
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isRetryingFailed ? "animate-spin" : ""}`} />
                  <span>{isRetryingFailed ? "Retrying..." : `Retry Failed Portals (${failedPortals.length})`}</span>
                </button>
              )}
              <button
                onClick={fetchScreenshots}
                disabled={isLoadingScreenshots}
                className="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                title="Refresh error screenshot records"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoadingScreenshots ? "animate-spin" : ""}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {screenshots.length === 0 ? (
            <div className="py-10 flex flex-col items-center justify-center text-center px-4 bg-slate-50/50 dark:bg-slate-950/20 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
              <div className="w-12 h-12 rounded-full bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-3">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-1">
                No Portal Scraping Failures
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md">
                All executed county court scrapers completed without unhandled page exceptions. When a bot fails or times out on a CAPTCHA challenge, automated viewport screenshots will be captured and cataloged here for operator triage.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {screenshots.map((shot) => {
                const isRunningThis = runningBotKey === shot.portal_key;
                const formattedDate = shot.created_at ? new Date(shot.created_at).toLocaleString() : "Unknown date";
                const providerColor = shot.storage_provider === "s3"
                  ? "bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800"
                  : shot.storage_provider === "azure"
                  ? "bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-800"
                  : shot.storage_provider === "gcs"
                  ? "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700";

                return (
                  <div
                    key={shot.id}
                    className="group bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 rounded-xl overflow-hidden shadow-xs hover:shadow-md transition-all flex flex-col"
                  >
                    {/* Header */}
                    <div className="p-3.5 border-b border-slate-200 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/80 flex items-center justify-between gap-2">
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-xs text-slate-900 dark:text-slate-100 truncate">
                            {shot.portal_name}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">
                          {formattedDate}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wider ${providerColor}`}>
                          {shot.storage_provider || "local"}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          #{shot.attempt_number}
                        </span>
                      </div>
                    </div>

                    {/* Screenshot Thumbnail with Zoom Action */}
                    <div
                      onClick={() => setSelectedScreenshotModal(shot)}
                      className="relative w-full aspect-video bg-slate-950 overflow-hidden cursor-pointer group/img"
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={shot.image_url}
                        alt={`Error capture for ${shot.portal_name}`}
                        className="w-full h-full object-cover object-top transition-transform duration-300 group-hover/img:scale-105"
                        onError={(e) => {
                          (e.target as HTMLElement).style.display = "none";
                        }}
                      />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white text-xs font-semibold backdrop-blur-[2px]">
                        <ZoomIn className="w-5 h-5 text-white" />
                        <span>Inspect Full Screen</span>
                      </div>
                    </div>

                    {/* Diagnostics Metadata */}
                    <div className="p-3.5 space-y-2.5 flex-1 flex flex-col justify-between">
                      <div className="space-y-2">
                        {shot.exception_message && (
                          <div className="p-2 rounded-lg bg-rose-50/80 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 text-rose-800 dark:text-rose-300 font-mono text-[11px] leading-tight line-clamp-3">
                            {shot.exception_message}
                          </div>
                        )}

                        {shot.page_url && (
                          <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate flex items-center gap-1">
                            <ExternalLink className="w-3 h-3 shrink-0 text-slate-400" />
                            <a
                              href={shot.page_url}
                              target="_blank"
                              rel="noreferrer"
                              className="hover:underline text-indigo-600 dark:text-indigo-400 truncate"
                            >
                              {shot.page_url}
                            </a>
                          </div>
                        )}

                        {shot.page_title && (
                          <div className="text-[11px] text-slate-600 dark:text-slate-300 truncate">
                            <span className="font-semibold text-slate-500 dark:text-slate-400">Page: </span>
                            {shot.page_title}
                          </div>
                        )}
                      </div>

                      {/* Card Footer Actions */}
                      <div className="pt-2 border-t border-slate-200 dark:border-slate-800/80 flex items-center justify-between gap-2">
                        <button
                          onClick={() => setSelectedScreenshotModal(shot)}
                          className="px-2.5 py-1.5 text-xs font-medium rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors flex items-center gap-1 cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Full</span>
                        </button>
                        <button
                          onClick={() => handleRunSingleBot(shot.portal_name)}
                          disabled={isRunningThis || !!runningBotKey}
                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                          title={`Retry ${shot.portal_name} scraper`}
                        >
                          <Play className={`w-3 h-3 ${isRunningThis ? "animate-spin" : ""}`} />
                          <span>{isRunningThis ? "Retrying..." : "Retry Portal"}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* 3. SCRAPED PUBLIC COURT CASES (REDESIGNED ENTERPRISE TABLE) */}
        {/* ========================================================================= */}
        <div id="scraped-cases-section" className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-sm w-full transition-colors">
          {/* Header with Search, Filters, and 4 Export Formats */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-purple-500 dark:text-purple-400" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Scraped Public Court Cases ({filteredCases.length} of {claim.court_cases?.length || 0})
                </h3>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                Comprehensive public civil litigation records harvested across online county court dockets. Grouped by portal URL.
              </p>
            </div>

            {/* Quick Export Bar */}
            {!isPdfExport && (
              <div className="no-print flex items-center gap-2 flex-wrap">
                <span className="text-[11px] text-slate-600 dark:text-slate-400 font-medium">Export Cases:</span>
                <button
                  onClick={(e) => handleExportClaim("xlsx", e)}
                  disabled={!!downloadingFormat}
                  className="px-2.5 py-1.5 bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title="Download Excel Workbook"
                >
                  {downloadingFormat === "xlsx" ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-500" />
                  ) : (
                    <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
                  )}
                  <span>{downloadingFormat === "xlsx" ? "Excel..." : "Excel"}</span>
                </button>
                <button
                  onClick={(e) => handleExportClaim("csv", e)}
                  disabled={!!downloadingFormat}
                  className="px-2.5 py-1.5 bg-sky-50 dark:bg-sky-950/60 hover:bg-sky-100 dark:hover:bg-sky-900 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-300 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title="Download CSV"
                >
                  {downloadingFormat === "csv" ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-500" />
                  ) : (
                    <FileText className="w-3.5 h-3.5 text-sky-500 dark:text-sky-400" />
                  )}
                  <span>{downloadingFormat === "csv" ? "CSV..." : "CSV"}</span>
                </button>
                <button
                  onClick={(e) => handleExportClaim("json", e)}
                  disabled={!!downloadingFormat}
                  className="px-2.5 py-1.5 bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900 border border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-300 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title="Download Raw JSON"
                >
                  {downloadingFormat === "json" ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-500" />
                  ) : (
                    <Code className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                  )}
                  <span>{downloadingFormat === "json" ? "JSON..." : "JSON"}</span>
                </button>
              </div>
            )}
          </div>

          {/* Search & Filter Controls Toolbar */}
          {!isPdfExport && (
            <div className="no-print flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
              <div className="relative w-full sm:w-80">
                <Search className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by case #, party, style, or type..."
                  value={caseSearchQuery}
                  onChange={(e) => {
                    setCaseSearchQuery(e.target.value);
                    setCasePage(1);
                  }}
                  className="w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-hidden focus:border-indigo-500"
                />
                {caseSearchQuery && (
                  <button
                    onClick={() => {
                      setCaseSearchQuery("");
                      setCasePage(1);
                    }}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>

              <div className="flex items-center gap-2 flex-wrap w-full sm:w-auto">
                {/* View Layout Switcher */}
                <div className="flex items-center bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-0.5">
                  <button
                    onClick={() => setCaseViewLayout("table")}
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                      caseViewLayout === "table"
                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs"
                        : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                    }`}
                  >
                    Table View
                  </button>
                  <button
                    onClick={() => setCaseViewLayout("grouped")}
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                      caseViewLayout === "grouped"
                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs"
                        : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                    }`}
                  >
                    Grouped
                  </button>
                </div>

                <div className="w-48">
                  <MultiSelectDropdown
                    label="Counties"
                    placeholder="All Counties"
                    options={countyOptions}
                    selectedValues={caseCountyFilters}
                    onChange={(vals) => {
                      setCaseCountyFilters(vals);
                      setCasePage(1);
                    }}
                  />
                </div>

                <div className="w-40">
                  <MultiSelectDropdown
                    label="Status"
                    placeholder="All Statuses"
                    options={statusOptions}
                    selectedValues={caseStatusFilters}
                    onChange={(vals) => {
                      setCaseStatusFilters(vals);
                      setCasePage(1);
                    }}
                  />
                </div>

                <div className="w-40">
                  <MultiSelectDropdown
                    label="Type"
                    placeholder="All Types"
                    options={typeOptions}
                    selectedValues={caseTypeFilters}
                    onChange={(vals) => {
                      setCaseTypeFilters(vals);
                      setCasePage(1);
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Table / Grouped View */}
          {filteredCases.length === 0 ? (
            <div className="text-center py-12 text-xs text-slate-500 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl">
              No public court cases matching your search criteria.
            </div>
          ) : caseViewLayout === "table" && !isPdfExport ? (
            /* Unified Sortable Table View */
            <div className="space-y-4">
              <div className="overflow-x-auto border border-slate-200 dark:border-slate-800 rounded-xl">
                <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
                  <thead className="bg-slate-100/90 dark:bg-slate-950/80 text-slate-600 dark:text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800 select-none">
                    <tr>
                      <th
                        onClick={() => {
                          if (caseSortField === "case_number") setCaseSortAsc(!caseSortAsc);
                          else { setCaseSortField("case_number"); setCaseSortAsc(true); }
                          setCasePage(1);
                        }}
                        className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                      >
                        Case Number {caseSortField === "case_number" && (caseSortAsc ? "↑" : "↓")}
                      </th>
                      <th
                        onClick={() => {
                          if (caseSortField === "county_name") setCaseSortAsc(!caseSortAsc);
                          else { setCaseSortField("county_name"); setCaseSortAsc(true); }
                          setCasePage(1);
                        }}
                        className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                      >
                        Court / Portal {caseSortField === "county_name" && (caseSortAsc ? "↑" : "↓")}
                      </th>
                      <th
                        onClick={() => {
                          if (caseSortField === "case_style") setCaseSortAsc(!caseSortAsc);
                          else { setCaseSortField("case_style"); setCaseSortAsc(true); }
                          setCasePage(1);
                        }}
                        className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                      >
                        Case Style {caseSortField === "case_style" && (caseSortAsc ? "↑" : "↓")}
                      </th>
                      <th
                        onClick={() => {
                          if (caseSortField === "filing_date") setCaseSortAsc(!caseSortAsc);
                          else { setCaseSortField("filing_date"); setCaseSortAsc(false); }
                          setCasePage(1);
                        }}
                        className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                      >
                        Filing Date {caseSortField === "filing_date" && (caseSortAsc ? "↑" : "↓")}
                      </th>
                      <th
                        onClick={() => {
                          if (caseSortField === "case_status") setCaseSortAsc(!caseSortAsc);
                          else { setCaseSortField("case_status"); setCaseSortAsc(true); }
                          setCasePage(1);
                        }}
                        className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                      >
                        Status {caseSortField === "case_status" && (caseSortAsc ? "↑" : "↓")}
                      </th>
                      <th
                        onClick={() => {
                          if (caseSortField === "case_type") setCaseSortAsc(!caseSortAsc);
                          else { setCaseSortField("case_type"); setCaseSortAsc(true); }
                          setCasePage(1);
                        }}
                        className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                      >
                        Type {caseSortField === "case_type" && (caseSortAsc ? "↑" : "↓")}
                      </th>
                      <th className="py-3 px-4 text-right no-print">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 font-sans">
                    {paginatedCases.map((courtCase) => (
                      <tr
                        key={courtCase.id}
                        className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors group"
                      >
                        <td className="py-3 px-4 font-mono font-bold text-slate-900 dark:text-slate-100 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <span>{courtCase.case_number}</span>
                            <button
                              onClick={() => handleCopyText(courtCase.case_number)}
                              className="no-print text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                              title="Copy case number"
                            >
                              {copiedCaseNumber === courtCase.case_number ? (
                                <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          </div>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                            {courtCase.county_name || "Unknown County"}
                          </span>
                        </td>
                        <td className="py-3 px-4 max-w-md">
                          <p className="line-clamp-2 text-slate-800 dark:text-slate-200" title={courtCase.case_style}>
                            {courtCase.case_style || "-"}
                          </p>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-500 dark:text-slate-400 whitespace-nowrap">
                          {(() => {
                            const rawDate = courtCase.filing_date || courtCase.raw_payload?.FilingDate || courtCase.raw_payload?.filing_date || courtCase.raw_payload?.SuitFiledDate;
                            return rawDate ? formatDate(rawDate) : "-";
                          })()}
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                            {courtCase.case_status || "OPEN"}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-500 dark:text-slate-400 whitespace-nowrap">
                          <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                            {courtCase.case_type || "CIVIL"}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right whitespace-nowrap no-print">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => setSelectedCaseForModal(courtCase)}
                              className="px-2 py-1 bg-indigo-50 dark:bg-indigo-950 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 rounded text-[11px] font-medium transition-colors flex items-center gap-1 cursor-pointer"
                              title="View case breakdown"
                            >
                              <Eye className="w-3 h-3" /> Details
                            </button>
                            <button
                              onClick={() => setRawJsonCaseForModal(courtCase.raw_payload || courtCase)}
                              className="px-2 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded text-[11px] font-medium transition-colors flex items-center gap-1 cursor-pointer"
                              title="Inspect raw payload JSON"
                            >
                              <Code className="w-3 h-3" /> JSON
                            </button>
                            {courtCase.source_url && (
                              <a
                                href={courtCase.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                                title="Open portal link"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            /* Grouped by Portal View */
            <div className="space-y-6">
              {Object.entries(groupedCases).map(([groupKey, group]) => {
                const isCollapsed = isPdfExport ? false : (collapsedPortals[groupKey] ?? false);
                return (
                  <div
                    key={groupKey}
                    className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden bg-white dark:bg-slate-950/40 shadow-xs break-inside-avoid"
                  >
                    {/* Portal Group Header */}
                    <div className="p-3.5 bg-slate-50 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        <span className={`w-2.5 h-2.5 rounded-full ${group.state === "FL" ? "bg-emerald-500" : group.state === "TX" ? "bg-blue-500" : "bg-purple-500"}`} />
                        <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">{group.portalName}</h4>
                        <span
                          className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${
                            group.state === "FL"
                              ? "bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                              : group.state === "TX"
                              ? "bg-blue-50 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-800"
                              : "bg-purple-50 dark:bg-purple-950/70 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-800"
                          }`}
                        >
                          {group.stateBadge}
                        </span>
                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-800 font-mono font-semibold">
                          {group.cases.length} {group.cases.length === 1 ? "case" : "cases"}
                        </span>
                        {group.websiteUrl && (
                          <a
                            href={group.websiteUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 hover:underline flex items-center gap-1 ml-1"
                            title="Open portal URL"
                          >
                            <ExternalLink className="w-3 h-3" /> Portal Link
                          </a>
                        )}
                      </div>

                      {!isPdfExport && (
                        <button
                          onClick={() => togglePortalCollapse(groupKey)}
                          className="no-print text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                        >
                          <span>{isCollapsed ? "Expand" : "Collapse"}</span>
                          {isCollapsed ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
                        </button>
                      )}
                    </div>

                    {/* Table of Cases */}
                    {!isCollapsed && (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
                          <thead className="bg-slate-100/90 dark:bg-slate-950/80 text-slate-600 dark:text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800 select-none">
                            <tr>
                              <th
                                onClick={() => {
                                  if (caseSortField === "case_number") setCaseSortAsc(!caseSortAsc);
                                  else { setCaseSortField("case_number"); setCaseSortAsc(true); }
                                }}
                                className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                              >
                                Case Number {caseSortField === "case_number" && (caseSortAsc ? "↑" : "↓")}
                              </th>
                              <th
                                onClick={() => {
                                  if (caseSortField === "case_style") setCaseSortAsc(!caseSortAsc);
                                  else { setCaseSortField("case_style"); setCaseSortAsc(true); }
                                }}
                                className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                              >
                                Case Style {caseSortField === "case_style" && (caseSortAsc ? "↑" : "↓")}
                              </th>
                              <th
                                onClick={() => {
                                  if (caseSortField === "filing_date") setCaseSortAsc(!caseSortAsc);
                                  else { setCaseSortField("filing_date"); setCaseSortAsc(false); }
                                }}
                                className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                              >
                                Filing Date {caseSortField === "filing_date" && (caseSortAsc ? "↑" : "↓")}
                              </th>
                              <th
                                onClick={() => {
                                  if (caseSortField === "case_status") setCaseSortAsc(!caseSortAsc);
                                  else { setCaseSortField("case_status"); setCaseSortAsc(true); }
                                }}
                                className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                              >
                                Status {caseSortField === "case_status" && (caseSortAsc ? "↑" : "↓")}
                              </th>
                              <th
                                onClick={() => {
                                  if (caseSortField === "case_type") setCaseSortAsc(!caseSortAsc);
                                  else { setCaseSortField("case_type"); setCaseSortAsc(true); }
                                }}
                                className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200"
                              >
                                Type {caseSortField === "case_type" && (caseSortAsc ? "↑" : "↓")}
                              </th>
                              {!isPdfExport && <th className="py-3 px-4 text-right no-print">Actions</th>}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 font-sans">
                            {group.cases.map((courtCase) => (
                              <tr
                                key={courtCase.id}
                                className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors group"
                              >
                                <td className="py-3 px-4 font-mono font-bold text-slate-900 dark:text-slate-100 whitespace-nowrap">
                                  <div className="flex items-center gap-2">
                                    <span>{courtCase.case_number}</span>
                                    {!isPdfExport && (
                                       <button
                                         onClick={() => handleCopyText(courtCase.case_number)}
                                         className="no-print text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                         title="Copy case number"
                                       >
                                         {copiedCaseNumber === courtCase.case_number ? (
                                           <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                                         ) : (
                                           <Copy className="w-3 h-3" />
                                         )}
                                       </button>
                                    )}
                                  </div>
                                </td>
                                <td className="py-3 px-4 max-w-md">
                                  <p className="line-clamp-2 text-slate-800 dark:text-slate-200" title={courtCase.case_style}>
                                    {courtCase.case_style || "-"}
                                  </p>
                                </td>
                                <td className="py-3 px-4 font-mono text-slate-500 dark:text-slate-400 whitespace-nowrap">
                                  {(() => {
                                    const rawDate = courtCase.filing_date || courtCase.raw_payload?.FilingDate || courtCase.raw_payload?.filing_date || courtCase.raw_payload?.SuitFiledDate;
                                    return rawDate ? formatDate(rawDate) : "-";
                                  })()}
                                </td>
                                <td className="py-3 px-4 whitespace-nowrap">
                                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                                    {courtCase.case_status || "OPEN"}
                                  </span>
                                </td>
                                <td className="py-3 px-4 text-slate-500 dark:text-slate-400 whitespace-nowrap">
                                  <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                                    {courtCase.case_type || "CIVIL"}
                                  </span>
                                </td>
                                {!isPdfExport && (
                                  <td className="py-3 px-4 text-right whitespace-nowrap no-print">
                                    <div className="flex items-center justify-end gap-2">
                                      <button
                                        onClick={() => setSelectedCaseForModal(courtCase)}
                                        className="px-2 py-1 bg-indigo-50 dark:bg-indigo-950 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 rounded text-[11px] font-medium transition-colors flex items-center gap-1 cursor-pointer"
                                        title="View case breakdown"
                                      >
                                        <Eye className="w-3 h-3" /> Details
                                      </button>
                                      <button
                                        onClick={() => setRawJsonCaseForModal(courtCase.raw_payload || courtCase)}
                                        className="px-2 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded text-[11px] font-medium transition-colors flex items-center gap-1 cursor-pointer"
                                        title="Inspect raw payload JSON"
                                      >
                                        <Code className="w-3 h-3" /> JSON
                                      </button>
                                      {courtCase.source_url && (
                                        <a
                                          href={courtCase.source_url}
                                          target="_blank"
                                          rel="noreferrer"
                                          className="p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                                          title="Open portal link"
                                        >
                                          <ExternalLink className="w-3.5 h-3.5" />
                                        </a>
                                      )}
                                    </div>
                                  </td>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Court Cases Pagination Controls */}
          {!isPdfExport && filteredCases.length > 0 && (
            <div className="no-print flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <span>Rows per page:</span>
                <select
                  value={casePageSize}
                  onChange={(e) => {
                    setCasePageSize(Number(e.target.value));
                    setCasePage(1);
                  }}
                  className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-md px-2 py-1 text-slate-700 dark:text-slate-300 focus:outline-hidden cursor-pointer"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={250}>250</option>
                  <option value={500}>500</option>
                </select>
                <span>
                  Showing {(casePage - 1) * casePageSize + 1} to{" "}
                  {Math.min(casePage * casePageSize, filteredCases.length)} of {filteredCases.length} scraped cases
                </span>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setCasePage((p) => Math.max(1, p - 1))}
                  disabled={casePage === 1}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <span className="px-2.5 py-1 font-mono text-xs font-semibold text-slate-800 dark:text-slate-200">
                  Page {casePage} of {totalCasePages}
                </span>

                <button
                  onClick={() => setCasePage((p) => Math.min(totalCasePages, p + 1))}
                  disabled={casePage >= totalCasePages}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                  aria-label="Next page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* AUDIT TRAIL & PROVENANCE TIMELINE (§73) */}
        {/* ========================================================================= */}
        <div className="bg-white dark:bg-slate-950 p-5 md:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-4">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                <ScrollText className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  Claim Audit Trail & Provenance
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {auditLogs.length} events
                  </span>
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Immutable chronological audit record of operations and dispatches for Claim #{claim?.claim_number}.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={fetchClaimAuditLogs}
                disabled={isLoadingAudit}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 flex items-center gap-1.5 cursor-pointer transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoadingAudit ? "animate-spin text-indigo-500" : ""}`} />
                <span>Refresh Trail</span>
              </button>
              {claim && (
                <Link
                  href={`/audit?claim_number=${claim.claim_number}`}
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 border border-indigo-200 dark:border-indigo-800 flex items-center gap-1.5 transition-colors"
                >
                  <span>Full Ledger</span>
                  <ExternalLink className="w-3 h-3" />
                </Link>
              )}
            </div>
          </div>

          {isLoadingAudit ? (
            <div className="py-8 text-center text-slate-400 dark:text-slate-500 flex flex-col items-center justify-center gap-2">
              <RefreshCw className="w-5 h-5 animate-spin text-indigo-500" />
              <span className="text-xs">Loading audit events...</span>
            </div>
          ) : auditLogs.length === 0 ? (
            <div className="py-8 text-center text-slate-400 dark:text-slate-500 flex flex-col items-center justify-center gap-2">
              <ScrollText className="w-6 h-6 text-slate-300 dark:text-slate-600" />
              <span className="text-xs font-medium">No audit events recorded yet for this claim.</span>
            </div>
          ) : (
            <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
              {auditLogs.map((log) => {
                const isFailed = log.status === "FAILED" || log.status === "ERROR";
                return (
                  <div key={log.id} className="relative group">
                    {/* Timeline Node Dot */}
                    <div
                      className={`absolute -left-6 top-1.5 w-3 h-3 rounded-full border-2 border-white dark:border-slate-950 ${
                        isFailed ? "bg-rose-500" : "bg-indigo-500"
                      }`}
                    />

                    <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-2">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-mono font-bold border ${
                              isFailed
                                ? "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400 border-rose-200 dark:border-rose-800"
                                : "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800"
                            }`}
                          >
                            {log.action}
                          </span>
                          <span
                            className={`inline-flex items-center px-1.5 py-0.2 rounded text-[9px] font-bold ${
                              isFailed
                                ? "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300"
                                : "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                            }`}
                          >
                            {log.status}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                          {log.details && (
                            <button
                              onClick={() => setSelectedAuditLogModal(log)}
                              className="text-indigo-600 dark:text-indigo-400 hover:underline font-sans font-medium flex items-center gap-1 cursor-pointer"
                            >
                              <Eye className="w-3 h-3" /> Inspect
                            </button>
                          )}
                        </div>
                      </div>

                      <p className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                        {log.description}
                      </p>

                      <div className="flex items-center gap-3 mt-2 text-[11px] text-slate-500 dark:text-slate-400">
                        <span className="flex items-center gap-1">
                          <User className="w-3 h-3 text-slate-400" />
                          <span className="font-semibold text-slate-700 dark:text-slate-300">{log.user_id}</span>
                        </span>
                        {log.ip_address && (
                          <span className="font-mono text-[10px]">IP: {log.ip_address}</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* ========================================================================= */}
      {/* MODALS */}
      {/* ========================================================================= */}

      {/* 1. STAGE DIAGNOSTICS & TELEMETRY AUDIT MODAL */}
      {inspectedStage && (
        <div className="no-print fixed inset-0 z-50 bg-slate-950/60 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                    Telemetry Audit: {inspectedStage.data?.portal_name || inspectedStage.data?.name || inspectedStage.key}
                  </h3>
                  {inspectedStage.data?.url && (
                    <a
                      href={inspectedStage.data.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 mt-0.5"
                    >
                      <ExternalLink className="w-3 h-3" /> {inspectedStage.data.url}
                    </a>
                  )}
                </div>
              </div>
              <button
                onClick={() => setInspectedStage(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* View Mode Tabs */}
            <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <button
                onClick={() => setInspectedStageTab("stages")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  inspectedStageTab === "stages"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                }`}
              >
                Structured Stage Progression
              </button>
              <button
                onClick={() => setInspectedStageTab("json")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  inspectedStageTab === "json"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                }`}
              >
                Full Diagnostic JSON
              </button>
            </div>

            <div className="space-y-3 text-xs overflow-y-auto pr-1 flex-1">
              {/* Metric summary strip */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono">
                <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Start Time</span>
                  <span className="text-slate-800 dark:text-slate-200 font-semibold truncate block">
                    {inspectedStage.data?.start_time || "-"}
                  </span>
                </div>
                <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[10px]">End Time</span>
                  <span className="text-slate-800 dark:text-slate-200 font-semibold truncate block">
                    {inspectedStage.data?.end_time || "-"}
                  </span>
                </div>
                <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Duration</span>
                  <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                    {inspectedStage.data?.duration_seconds !== undefined ? `${inspectedStage.data.duration_seconds}s` : "-"}
                  </span>
                </div>
                <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Status</span>
                  <span
                    className={`font-bold ${
                      (inspectedStage.data?.status || "SUCCESS").toUpperCase() === "SUCCESS"
                        ? "text-emerald-600 dark:text-emerald-400"
                        : (inspectedStage.data?.status || "").toUpperCase() === "FAILED"
                        ? "text-red-600 dark:text-red-400"
                        : "text-amber-600 dark:text-amber-400"
                    }`}
                  >
                    {inspectedStage.data?.status || "SUCCESS"}
                  </span>
                </div>
              </div>

              {inspectedStageTab === "stages" ? (
                <div className="space-y-2 pt-1">
                  {inspectedStage.data?.stages && Object.keys(inspectedStage.data.stages).length > 0 ? (
                    <div className="divide-y divide-slate-200 dark:divide-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                      {Object.entries(inspectedStage.data.stages).map(([sKey, sVal]: [string, any], idx) => (
                        <div key={sKey} className="p-3 bg-slate-50/50 dark:bg-slate-950/40 hover:bg-slate-50 dark:hover:bg-slate-900/60 transition-colors">
                          <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
                            <div className="flex items-center gap-2">
                              <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 text-[10px] font-bold flex items-center justify-center font-mono">
                                {idx + 1}
                              </span>
                              <span className="font-semibold text-slate-900 dark:text-slate-100">
                                {sVal?.name || sKey.replace(/_/g, " ").toUpperCase()}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 font-mono text-[11px]">
                              <span
                                className={`px-2 py-0.5 rounded font-bold border ${
                                  (sVal?.status || "SUCCESS").toUpperCase() === "SUCCESS"
                                    ? "bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                                    : (sVal?.status || "").toUpperCase() === "FAILED"
                                    ? "bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800"
                                    : "bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800"
                                }`}
                              >
                                {sVal?.status || "SUCCESS"}
                              </span>
                              {sVal?.duration_seconds !== undefined && (
                                <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold border border-slate-300 dark:border-slate-700">
                                  ⏱️ {sVal.duration_seconds}s
                                </span>
                              )}
                            </div>
                          </div>
                          {(sVal?.start_time || sVal?.end_time) && (
                            <div className="text-[10px] font-mono text-slate-500 dark:text-slate-400 flex items-center gap-3 ml-7 mb-1">
                              {sVal?.start_time && <span>Start: {sVal.start_time}</span>}
                              {sVal?.end_time && <span>End: {sVal.end_time}</span>}
                            </div>
                          )}
                          {sVal?.detail && (
                            <p className="text-[11px] text-slate-600 dark:text-slate-400 ml-7 bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-800/80">
                              {sVal.detail}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          {inspectedStage.data?.name || inspectedStage.key.replace(/_/g, " ").toUpperCase()}
                        </span>
                        {inspectedStage.data?.duration_seconds !== undefined && (
                          <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">
                            {inspectedStage.data.duration_seconds}s
                          </span>
                        )}
                      </div>
                      {inspectedStage.data?.detail && (
                        <p className="text-slate-600 dark:text-slate-400 text-xs">
                          {inspectedStage.data.detail}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div>
                  <span className="text-slate-700 dark:text-slate-400 block text-[11px] font-semibold mb-1">
                    Full Diagnostic JSON
                  </span>
                  <pre className="p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-emerald-600 dark:text-emerald-400 overflow-x-auto max-h-80">
                    {JSON.stringify(inspectedStage.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCopyTelemetry(inspectedStage.data)}
                  className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded-lg border border-slate-300 dark:border-slate-700 flex items-center gap-1.5 cursor-pointer transition-colors"
                >
                  {copiedTelemetry ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
                      <span>Copy JSON</span>
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleDownloadTelemetry(inspectedStage.key, inspectedStage.data)}
                  className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded-lg border border-slate-300 dark:border-slate-700 flex items-center gap-1.5 cursor-pointer transition-colors"
                >
                  <Download className="w-3.5 h-3.5 text-sky-500 dark:text-sky-400" />
                  <span>Download Trace (.json)</span>
                </button>
              </div>
              <button
                onClick={() => setInspectedStage(null)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg cursor-pointer transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. CASE DETAILS MODAL */}
      {selectedCaseForModal && (
        <div className="no-print fixed inset-0 z-50 bg-slate-950/60 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-lg w-full max-h-[85vh] flex flex-col p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Scale className="w-4 h-4 text-purple-500 dark:text-purple-400" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Court Case Details: {selectedCaseForModal.case_number}
                </h3>
              </div>
              <button
                onClick={() => setSelectedCaseForModal(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs overflow-y-auto pr-1">
              <div>
                <span className="text-slate-500 block text-[11px]">Case Style</span>
                <p className="font-semibold text-slate-800 dark:text-slate-200 text-sm mt-0.5">{selectedCaseForModal.case_style}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[11px]">County Jurisdiction</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{selectedCaseForModal.county_name}</span>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[11px]">Filing Date</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200">
                    {formatDate(
                      selectedCaseForModal.filing_date ||
                      selectedCaseForModal.raw_payload?.FilingDate ||
                      selectedCaseForModal.raw_payload?.filing_date ||
                      selectedCaseForModal.raw_payload?.SuitFiledDate
                    )}
                  </span>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[11px]">Case Status</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{selectedCaseForModal.case_status || "OPEN"}</span>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-500 block text-[11px]">Case Type / Classification</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{selectedCaseForModal.case_type || "CIRCUIT CIVIL"}</span>
                </div>
              </div>

              {selectedCaseForModal.source_url && (
                <div>
                  <span className="text-slate-500 block text-[11px]">Court Portal URL</span>
                  <a
                    href={selectedCaseForModal.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-mono text-xs break-all mt-0.5"
                  >
                    {selectedCaseForModal.source_url} <ExternalLink className="w-3 h-3 shrink-0" />
                  </a>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <button
                onClick={() => setRawJsonCaseForModal(selectedCaseForModal.raw_payload || selectedCaseForModal)}
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 cursor-pointer"
              >
                <Code className="w-3 h-3" /> View Raw JSON
              </button>
              <button
                onClick={() => setSelectedCaseForModal(null)}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded-lg border border-slate-300 dark:border-slate-700 cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. RAW JSON MODAL */}
      {rawJsonCaseForModal && (
        <div className="no-print fixed inset-0 z-50 bg-slate-950/60 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-xl w-full max-h-[85vh] flex flex-col p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Code className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Raw Docket Scraper Payload (JSON)
                </h3>
              </div>
              <button
                onClick={() => setRawJsonCaseForModal(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto">
              <pre className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-mono text-emerald-600 dark:text-emerald-400 overflow-x-auto">
                {JSON.stringify(rawJsonCaseForModal, null, 2)}
              </pre>
            </div>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(rawJsonCaseForModal, null, 2));
                  setFeedback({ type: "success", msg: "Raw JSON copied to clipboard." });
                }}
                className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-300 text-xs font-medium rounded-lg flex items-center gap-1.5 cursor-pointer"
              >
                <Copy className="w-3.5 h-3.5" /> Copy JSON
              </button>
              <button
                onClick={() => setRawJsonCaseForModal(null)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. EDIT CLAIM MODAL */}
      {isEditOpen && (
        <div className="no-print fixed inset-0 z-50 bg-slate-950/60 dark:bg-slate-950/80 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-t-2xl sm:rounded-2xl max-w-lg w-full max-h-[90vh] flex flex-col p-5 sm:p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                Edit Claim: {claim.claim_number}
              </h3>
              <button onClick={() => setIsEditOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-4 text-xs overflow-y-auto flex-1 pr-1 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Primary Key</label>
                  <input
                    type="text"
                    value={formData.primary_key}
                    onChange={(e) => setFormData({ ...formData, primary_key: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                    placeholder="e.g. PK-1001"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Claim Number *</label>
                  <input
                    type="text"
                    required
                    value={formData.claim_number}
                    onChange={(e) => setFormData({ ...formData, claim_number: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Exposure Number</label>
                  <input
                    type="text"
                    value={formData.exposure_number}
                    onChange={(e) => setFormData({ ...formData, exposure_number: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Insured First Name</label>
                  <input
                    type="text"
                    value={formData.insured_first_name}
                    onChange={(e) => setFormData({ ...formData, insured_first_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Insured Last Name</label>
                  <input
                    type="text"
                    value={formData.insured_last_name}
                    onChange={(e) => setFormData({ ...formData, insured_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Claimant First Name</label>
                  <input
                    type="text"
                    value={formData.claimant_first_name}
                    onChange={(e) => setFormData({ ...formData, claimant_first_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Claimant Last Name</label>
                  <input
                    type="text"
                    value={formData.claimant_last_name}
                    onChange={(e) => setFormData({ ...formData, claimant_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Driver First Name (Insured Vehicle)</label>
                  <input
                    type="text"
                    value={formData.driver_first_name}
                    onChange={(e) => setFormData({ ...formData, driver_first_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                    placeholder="Driver First Name"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Driver Last Name (Insured Vehicle)</label>
                  <input
                    type="text"
                    value={formData.driver_last_name}
                    onChange={(e) => setFormData({ ...formData, driver_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                    placeholder="Driver Last Name"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">DOL (Date of Loss)</label>
                  <input
                    type="text"
                    placeholder="MM/DD/YYYY"
                    value={formData.dol}
                    onChange={(e) => setFormData({ ...formData, dol: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Policy State</label>
                  <select
                    value={formData.policy_state}
                    onChange={(e) => setFormData({ ...formData, policy_state: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  >
                    <option value="Florida">Florida</option>
                    <option value="Texas">Texas</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Loss Location State</label>
                  <select
                    value={formData.loss_location_state}
                    onChange={(e) => setFormData({ ...formData, loss_location_state: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px] text-slate-900 dark:text-slate-200 focus:border-indigo-500"
                  >
                    <option value="Florida">Florida</option>
                    <option value="Texas">Texas</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsEditOpen(false)}
                  className="px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg cursor-pointer"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 5. DELETE CONFIRM MODAL */}
      {isDeleteOpen && (
        <div className="no-print fixed inset-0 z-50 bg-slate-950/60 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-rose-100 dark:bg-rose-950/80 border border-rose-200 dark:border-rose-800 flex items-center justify-center text-rose-600 dark:text-rose-400">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Delete Claim Record?</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">This action cannot be undone.</p>
              </div>
            </div>

            <p className="text-xs text-slate-700 dark:text-slate-300">
              Are you sure you want to delete claim <strong className="font-mono text-slate-900 dark:text-slate-100">{claim.claim_number}</strong>?
              All associated scraped court cases, fuzzy match scores, and activity logs will be permanently removed.
            </p>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-end gap-2">
              <button
                onClick={() => setIsDeleteOpen(false)}
                className="px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold rounded-lg text-xs cursor-pointer"
              >
                Permanently Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Full-Screen Screenshot Lightbox Modal */}
      {selectedScreenshotModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 md:p-6 animate-in fade-in duration-200">
          <div className="max-w-6xl w-full max-h-[94vh] bg-slate-900 border border-slate-700 rounded-2xl flex flex-col overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="p-4 px-6 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between gap-4">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <Camera className="w-4 h-4 text-rose-400 shrink-0" />
                  <h3 className="text-sm font-bold text-white truncate">
                    {selectedScreenshotModal.portal_name} — Scraping Error Snapshot
                  </h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                    {selectedScreenshotModal.storage_provider || "local"}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5 truncate">
                  Attempt #{selectedScreenshotModal.attempt_number} • Captured: {selectedScreenshotModal.created_at ? new Date(selectedScreenshotModal.created_at).toLocaleString() : "Unknown"}
                  {selectedScreenshotModal.page_url ? ` • URL: ${selectedScreenshotModal.page_url}` : ""}
                </p>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <a
                  href={selectedScreenshotModal.image_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                  title="Open raw image in new browser tab"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open Image</span>
                </a>
                <button
                  onClick={() => setSelectedScreenshotModal(null)}
                  className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center transition-colors cursor-pointer"
                  title="Close viewer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modal Image Viewport */}
            <div className="flex-1 overflow-auto bg-slate-950 p-4 flex items-center justify-center min-h-[360px] max-h-[66vh]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={selectedScreenshotModal.image_url}
                alt={`Full viewport error capture for ${selectedScreenshotModal.portal_name}`}
                className="max-w-full max-h-full object-contain rounded-lg border border-slate-800 shadow-xl"
              />
            </div>

            {/* Modal Footer with Failure Diagnostics & Action */}
            <div className="p-4 px-6 border-t border-slate-800 bg-slate-900/90 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="min-w-0 flex-1">
                {selectedScreenshotModal.exception_message && (
                  <div className="p-2.5 rounded-lg bg-rose-950/60 border border-rose-900/70 text-rose-300 font-mono text-xs max-h-20 overflow-y-auto whitespace-pre-wrap">
                    {selectedScreenshotModal.exception_message}
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end gap-2 shrink-0">
                <button
                  onClick={() => setSelectedScreenshotModal(null)}
                  className="px-4 py-2 text-xs font-medium rounded-lg text-slate-300 hover:bg-slate-800 border border-slate-700 transition-colors cursor-pointer"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    handleRunSingleBot(selectedScreenshotModal.portal_name);
                    setSelectedScreenshotModal(null);
                  }}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Retry This Portal Bot</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. AUDIT EVENT INSPECTOR MODAL */}
      {selectedAuditLogModal && (
        <div className="no-print fixed inset-0 z-50 bg-slate-950/60 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-xl w-full max-h-[85vh] flex flex-col p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <ScrollText className="w-4 h-4 text-indigo-500" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Audit Details: {selectedAuditLogModal.action}
                </h3>
              </div>
              <button
                onClick={() => setSelectedAuditLogModal(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs overflow-y-auto pr-1">
              <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Description</span>
                <p className="font-semibold text-slate-800 dark:text-slate-200 mt-0.5">
                  {selectedAuditLogModal.description}
                </p>
              </div>

              <div>
                <span className="text-slate-700 dark:text-slate-400 block text-[11px] font-semibold mb-1">
                  Event Payload (Zero Credential Leakage Verified)
                </span>
                <pre className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-indigo-600 dark:text-indigo-400 overflow-x-auto max-h-64">
                  {JSON.stringify(selectedAuditLogModal.details || {}, null, 2)}
                </pre>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(selectedAuditLogModal, null, 2));
                  setFeedback({ type: "success", msg: "Audit event copied to clipboard." });
                }}
                className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-300 text-xs font-medium rounded-lg flex items-center gap-1.5 cursor-pointer"
              >
                <Copy className="w-3.5 h-3.5" /> Copy Event
              </button>
              <button
                onClick={() => setSelectedAuditLogModal(null)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
