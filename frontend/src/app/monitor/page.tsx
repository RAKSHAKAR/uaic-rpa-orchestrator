"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Layers,
  RotateCcw,
  RefreshCw,
  CheckCircle2,
  Filter,
  Plus,
  Trash2,
  Edit3,
  Play,
  Pause,
  Download,
  FileSpreadsheet,
  FileText,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  X,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  CheckSquare,
  Square,
  Search,
  Radio,
  Zap,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";
import { Navbar } from "../../components/Navbar";
import { StatusBadge } from "../../components/StatusBadge";
import { StatCard } from "../../components/StatCard";
import { FilterPresetManager } from "../../components/FilterPresetManager";
import { AsyncExportModal } from "../../components/AsyncExportModal";
import { api } from "../../lib/api";
import { cn } from "../../lib/utils";
import { Claim, QueueStatus } from "../../types";

export default function QueueMonitorPage() {
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [stateFilter, setStateFilter] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortOrder, setSortOrder] = useState<string>("desc");
  
  const [isLoading, setIsLoading] = useState(true);
  const [isRetriggering, setIsRetriggering] = useState(false);
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Auto Queue Mode State - Default to true
  const [autoQueueEnabled, setAutoQueueEnabled] = useState(true);
  const [autoQueueRunning, setAutoQueueRunning] = useState(false);

  // Bulk Selection State
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Portal-Level Granularity & Live Polling State (§61)
  const [expandedClaimIds, setExpandedClaimIds] = useState<Set<string>>(new Set());
  const [livePollInterval, setLivePollInterval] = useState<number>(0); // 0=off, 3=3s, 5=5s
  const [runningBotKey, setRunningBotKey] = useState<string | null>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Modals State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingClaim, setEditingClaim] = useState<Claim | null>(null);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isBulkDeleteOpen, setIsBulkDeleteOpen] = useState(false);
  const [isCleanOpen, setIsCleanOpen] = useState(false);

  // Form State for Create / Edit
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

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [qData, cData, autoModeData] = await Promise.all([
        api.getQueueStatus().catch(() => null),
        api.getClaims({
          page,
          page_size: pageSize,
          status: statusFilter || undefined,
          state: stateFilter || undefined,
          search: searchTerm || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        }).catch((err) => {
          console.error("Claims fetch error:", err);
          return { items: [], total: 0, total_pages: 1 };
        }),
        api.getAutoQueueMode().catch(() => ({ auto_queue_enabled: false, is_running: false })),
      ]);
      setQueueStatus(qData);
      setClaims(cData?.items || []);
      setTotal(cData?.total || 0);
      setTotalPages(cData?.total_pages || 1);
      if (autoModeData) {
        setAutoQueueEnabled(autoModeData.auto_queue_enabled);
        setAutoQueueRunning(autoModeData.is_running);
      }
    } catch (e) {
      console.error("Failed to load queue data:", e);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, statusFilter, stateFilter, searchTerm, sortBy, sortOrder]);

  useEffect(() => {
    fetchData();
    const intervalMs = livePollInterval > 0 ? livePollInterval * 1000 : 8000;
    if (livePollInterval === -1) return; // -1 = Paused
    const interval = setInterval(fetchData, intervalMs);
    return () => clearInterval(interval);
  }, [fetchData, livePollInterval]);

  const toggleClaimExpansion = (claimId: string) => {
    setExpandedClaimIds((prev) => {
      const next = new Set(prev);
      if (next.has(claimId)) next.delete(claimId);
      else next.add(claimId);
      return next;
    });
  };

  const handleRunSingleBot = async (claimId: string, botKey: string, botName: string) => {
    const key = `${claimId}_${botKey}`;
    setRunningBotKey(key);
    try {
      const res = await api.runSingleBot(claimId, botKey);
      showNotification(res.message || `Dispatched ${botName} scraper.`);
      await fetchData();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || `Failed to run ${botName}.`, "error");
    } finally {
      setRunningBotKey(null);
    }
  };

  const showNotification = (message: string, type: "success" | "error" = "success") => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  // Auto Queue Toggle
  const handleToggleAutoQueue = async () => {
    try {
      const nextState = !autoQueueEnabled;
      const res = await api.toggleAutoQueueMode(nextState);
      setAutoQueueEnabled(res.auto_queue_enabled);
      showNotification(res.message);
      await fetchData();
    } catch (e: any) {
      showNotification("Failed to toggle automatic queue mode.", "error");
    }
  };

  // Start All Queue
  const handleStartAllQueue = async () => {
    try {
      const res = await api.startAllQueue();
      showNotification(res.message);
      await fetchData();
    } catch (e: any) {
      showNotification("Failed to start queue.", "error");
    }
  };

  // Retrigger Failed
  const handleRetrigger = async () => {
    setIsRetriggering(true);
    try {
      const res = await api.retriggerClaims();
      showNotification(res.message);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to retrigger claims.", "error");
    } finally {
      setIsRetriggering(false);
    }
  };

  // Clean Database
  const handleCleanDatabase = async () => {
    try {
      const res = await api.cleanDatabase();
      showNotification(res.message);
      setIsCleanOpen(false);
      setSelectedIds([]);
      setPage(1);
      await fetchData();
    } catch (e: any) {
      showNotification("Database cleanup failed.", "error");
    }
  };

  // Create Single Claim
  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.claim_number.trim()) {
      showNotification("Claim Number is required.", "error");
      return;
    }
    try {
      await api.createClaim(formData);
      showNotification(`Claim ${formData.claim_number} created successfully.`);
      setIsCreateOpen(false);
      setFormData({
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
      await fetchData();
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Failed to create claim.";
      showNotification(msg, "error");
    }
  };

  // Edit Single Claim
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingClaim) return;
    try {
      await api.updateClaim(editingClaim.id, formData);
      showNotification(`Claim ${editingClaim.claim_number} updated successfully.`);
      setIsEditOpen(false);
      setEditingClaim(null);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to update claim.", "error");
    }
  };

  // Single Delete
  const handleDeleteConfirm = async () => {
    if (!deletingId) return;
    try {
      await api.deleteClaim(deletingId);
      showNotification("Claim deleted successfully.");
      setIsDeleteOpen(false);
      setDeletingId(null);
      setSelectedIds((prev) => prev.filter((id) => id !== deletingId));
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to delete claim.", "error");
    }
  };

  // Single Start
  const handleStartSingle = async (id: string, claimNumber: string) => {
    try {
      await api.startClaim(id);
      showNotification(`Automation dispatched for claim ${claimNumber}.`);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to start claim automation.", "error");
    }
  };

  // Bulk Operations
  const handleSelectAllVisible = () => {
    if (selectedIds.length === claims.length && claims.length > 0) {
      setSelectedIds([]);
    } else {
      setSelectedIds(claims.map((c) => c.id));
    }
  };

  const handleToggleSelectRow = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleBulkStart = async () => {
    try {
      const res = await api.bulkStartClaims(selectedIds);
      showNotification(res.message);
      setSelectedIds([]);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to bulk start claims.", "error");
    }
  };

  const handleBulkRetryFailed = async () => {
    try {
      const res = await api.bulkRetryClaims(selectedIds, true);
      showNotification(res.message);
      setSelectedIds([]);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to retry failed portals in bulk.", "error");
    }
  };

  const handleBulkStatusChange = async (newStatus: string) => {
    try {
      const res = await api.bulkUpdateStatus(selectedIds, newStatus);
      showNotification(res.message);
      setSelectedIds([]);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to update status in bulk.", "error");
    }
  };

  const handleBulkDeleteConfirm = async () => {
    try {
      const res = await api.bulkDeleteClaims(selectedIds);
      showNotification(res.message);
      setIsBulkDeleteOpen(false);
      setSelectedIds([]);
      await fetchData();
    } catch (err: any) {
      showNotification("Failed to bulk delete claims.", "error");
    }
  };

  // Column Sort Handler
  const handleSort = (columnKey: string) => {
    if (sortBy === columnKey) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(columnKey);
      setSortOrder("desc");
    }
  };

  const renderSortIcon = (columnKey: string) => {
    if (sortBy !== columnKey) {
      return <ArrowUpDown className="w-3 h-3 text-slate-400 opacity-60 ml-1 inline" />;
    }
    return sortOrder === "asc" ? (
      <ArrowUp className="w-3 h-3 text-indigo-500 ml-1 inline" />
    ) : (
      <ArrowDown className="w-3 h-3 text-indigo-500 ml-1 inline" />
    );
  };

  const getBotKeyFromName = (name: string): string => {
    const n = name.toLowerCase();
    if (n.includes("broward")) return "broward";
    if (n.includes("hillsborough")) return "hillsborough";
    if (n.includes("miami")) return "miami";
    if (n.includes("travis")) return "travis";
    if (n.includes("dallas")) return "dallas";
    if (n.includes("jp")) return "harris_jp";
    if (n.includes("district")) return "harris_district";
    if (n.includes("clerk")) return "harris_cclerk";
    return n.split(" ")[0];
  };

  return (
    <div className="flex-1 flex flex-col w-full">
      <Navbar onRefresh={fetchData} isRefreshing={isLoading} />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none flex-1 transition-colors">
        {/* Title & Queue Actions */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 w-full">
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-500" />
              Distributed Task & Bot Queue Monitor
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Full lifecycle management: automatic sequential execution, manual bot controls, and high-resolution audit logging.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 sm:gap-3 justify-start lg:justify-end w-full lg:w-auto">
            {/* Group 1: Live Stream & Auto Queue Stream Controls */}
            <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
              {/* Live Stream Polling Toggle (§61) */}
              <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-1 text-xs min-h-[40px]">
                <span className="flex items-center gap-1.5 px-2 text-slate-500 dark:text-slate-400 font-medium">
                  <Radio className={`w-3.5 h-3.5 ${livePollInterval !== -1 ? "text-emerald-500 animate-pulse" : "text-slate-400"}`} />
                  <span className="hidden sm:inline">Live Stream:</span>
                </span>
                <button
                  type="button"
                  onClick={() => setLivePollInterval(3)}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                    livePollInterval === 3 ? "bg-emerald-600 text-white" : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                >
                  3s
                </button>
                <button
                  type="button"
                  onClick={() => setLivePollInterval(5)}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                    livePollInterval === 5 ? "bg-emerald-600 text-white" : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                >
                  5s
                </button>
                <button
                  type="button"
                  onClick={() => setLivePollInterval(-1)}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                    livePollInterval === -1 ? "bg-slate-300 dark:bg-slate-700 text-slate-900 dark:text-white" : "text-slate-400 hover:text-slate-600"
                  }`}
                >
                  Pause
                </button>
              </div>

              {/* Auto Queue Mode Toggle */}
              <button
                type="button"
                onClick={handleToggleAutoQueue}
                className={`px-3 py-2 text-xs font-semibold rounded-lg border transition-all flex items-center gap-1.5 cursor-pointer shadow-xs min-h-[40px] whitespace-nowrap ${
                  autoQueueEnabled
                    ? "bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300"
                    : "bg-slate-100 dark:bg-slate-900 border-slate-300 dark:border-slate-800 text-slate-600 dark:text-slate-400"
                }`}
              >
                {autoQueueEnabled ? <Play className="w-3.5 h-3.5 fill-emerald-600" /> : <Pause className="w-3.5 h-3.5" />}
                <span>Auto Queue: <strong>{autoQueueEnabled ? "ENABLED" : "PAUSED"}</strong></span>
              </button>
            </div>

            {/* Group 2: Queue Execution Controls */}
            <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
              {/* Start All NEW Queue */}
              <button
                type="button"
                onClick={handleStartAllQueue}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer min-h-[40px] whitespace-nowrap"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Start All Queue</span>
              </button>

              {/* Create Single Claim */}
              <button
                type="button"
                onClick={() => {
                  setFormData({
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
                  setIsCreateOpen(true);
                }}
                className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer min-h-[40px] whitespace-nowrap"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Create Claim</span>
              </button>
            </div>

            {/* Group 3: Maintenance & Health Operations */}
            <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
              {/* Retrigger Failed Cases */}
              <button
                type="button"
                onClick={handleRetrigger}
                disabled={isRetriggering}
                className="px-3 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer min-h-[40px] whitespace-nowrap"
              >
                <RotateCcw className={`w-3.5 h-3.5 ${isRetriggering ? "animate-spin" : ""}`} />
                <span>Retrigger Failed</span>
              </button>

              {/* Purge / Clean Database */}
              <button
                type="button"
                onClick={() => setIsCleanOpen(true)}
                className="px-3 py-2 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/60 border border-rose-300 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer min-h-[40px] whitespace-nowrap"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Purge DB</span>
              </button>
            </div>
          </div>
        </div>

        {/* Retrigger / Action Notification Alert */}
        {notification && (
          <div
            className={`w-full max-w-full overflow-hidden rounded-xl p-3.5 text-xs flex items-center justify-between gap-2 border transition-all ${
              notification.type === "success"
                ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {notification.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
              )}
              <span className="min-w-0 break-words flex-1">{notification.message}</span>
            </div>
            <button
              onClick={() => setNotification(null)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 shrink-0 p-1 cursor-pointer transition-colors"
              title="Dismiss"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Queue Metrics Breakdown using reusable StatCard matching Dashboard design language */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 w-full">
          <StatCard
            label="Ingest Queue"
            value={queueStatus?.queues?.ingest ?? 0}
            subtext="Raw batch files"
            icon={Layers}
            gradient="blue"
          />
          <StatCard
            label="Scraper Queue"
            value={queueStatus?.queues?.scrapers ?? 0}
            subtext="County portals"
            icon={Zap}
            gradient="amber"
          />
          <StatCard
            label="Matcher Queue"
            value={queueStatus?.queues?.matcher ?? 0}
            subtext="RapidFuzz cascade"
            icon={Filter}
            gradient="purple"
          />
          <StatCard
            label="Guidewire Queue"
            value={queueStatus?.queues?.notifications ?? 0}
            subtext="Cloud API dispatch"
            icon={CheckCircle2}
            gradient="emerald"
          />
          <StatCard
            label="Active Workers"
            value={queueStatus?.workers_online ?? 1}
            subtext="Celery nodes active"
            icon={Radio}
            gradient="cyan"
          />
        </div>

        {/* Claims Table Container */}
        <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4 shadow-xs w-full transition-colors">
          {/* Phase 6 (§83) Filter Preset Manager */}
          <div className="pb-3 border-b border-slate-200 dark:border-slate-800/80">
            <FilterPresetManager
              currentStatus={statusFilter}
              currentState={stateFilter}
              currentSearch={searchTerm}
              onApplyPreset={(p) => {
                setStatusFilter(p.status);
                setStateFilter(p.state);
                setSearchTerm(p.search);
                setPage(1);
              }}
              onResetFilters={() => {
                setStatusFilter("");
                setStateFilter("");
                setSearchTerm("");
                setPage(1);
              }}
            />
          </div>

          {/* Filters & Export Bar */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 sm:gap-4 pb-4 border-b border-slate-200 dark:border-slate-800/80">
            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full lg:w-auto">
              {/* Search */}
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search claim, party, city..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setPage(1);
                  }}
                  className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 w-full min-h-[40px]"
                />
              </div>

              {/* Status and State Filters */}
              <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center">
                <div className="flex items-center gap-1.5 w-full">
                  <select
                    value={statusFilter}
                    onChange={(e) => {
                      setStatusFilter(e.target.value);
                      setPage(1);
                    }}
                    className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 w-full min-h-[40px]"
                  >
                    <option value="">All Statuses</option>
                    <option value="NEW">New</option>
                    <option value="SCRAPING_IN_PROGRESS">Scraping In Progress</option>
                    <option value="SCRAPING_COMPLETED">Scraping Completed</option>
                    <option value="MATCH_FOUND">Match Found</option>
                    <option value="MANUAL_REVIEW">Manual Review</option>
                    <option value="NO_MATCH_FOUND">No Match Found</option>
                    <option value="FAILED">Failed</option>
                    <option value="COMPLETED">Completed</option>
                  </select>
                </div>

                <select
                  value={stateFilter}
                  onChange={(e) => {
                    setStateFilter(e.target.value);
                    setPage(1);
                  }}
                  className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 w-full sm:w-auto min-h-[40px]"
                >
                  <option value="">All States</option>
                  <option value="FL">Florida (FL)</option>
                  <option value="TX">Texas (TX)</option>
                </select>
              </div>
            </div>

            {/* Export Actions */}
            <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
              {/* Background Celery Export Modal (§55) */}
              <button
                type="button"
                onClick={() => setIsExportModalOpen(true)}
                className="flex-1 sm:flex-initial px-3.5 py-2 bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 min-h-[40px] cursor-pointer"
                title="Large dataset background export with streaming"
              >
                <Download className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                <span>Background Export</span>
              </button>

              <a
                href={api.getExportUrl({
                  format: "xlsx",
                  status: statusFilter,
                  state: stateFilter,
                  search: searchTerm,
                })}
                download
                className="flex-1 sm:flex-initial px-3.5 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 min-h-[40px]"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
                <span>Export Excel</span>
              </a>

              <a
                href={api.getExportUrl({
                  format: "csv",
                  status: statusFilter,
                  state: stateFilter,
                  search: searchTerm,
                })}
                download
                className="flex-1 sm:flex-initial px-3.5 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 min-h-[40px]"
              >
                <FileText className="w-3.5 h-3.5 text-sky-600" />
                <span>Export CSV</span>
              </a>
            </div>
          </div>

          {/* Floating / Sticky Bulk Action Bar */}
          {selectedIds.length > 0 && (
            <div className="bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs shadow-xs animate-in fade-in">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-full bg-indigo-600 text-white font-bold text-[11px]">
                  {selectedIds.length} Selected
                </span>
                <span className="text-slate-600 dark:text-slate-300">Choose bulk action to execute:</span>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                {/* Bulk Start */}
                <button
                  onClick={handleBulkStart}
                  className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold flex items-center gap-1 cursor-pointer"
                >
                  <Play className="w-3 h-3" />
                  <span>Start Selected</span>
                </button>

                {/* Bulk Retry Failed Only */}
                <button
                  onClick={handleBulkRetryFailed}
                  className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-semibold flex items-center gap-1 cursor-pointer shadow-xs"
                  title="Retry only the failed court portals for selected claims"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Retry Failed Only</span>
                </button>

                {/* Bulk Change Status */}
                <select
                  onChange={(e) => {
                    if (e.target.value) handleBulkStatusChange(e.target.value);
                  }}
                  defaultValue=""
                  className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-800 dark:text-slate-200"
                >
                  <option value="" disabled>Change Status to...</option>
                  <option value="NEW">Set to NEW</option>
                  <option value="COMPLETED">Set to COMPLETED</option>
                  <option value="MANUAL_REVIEW">Set to MANUAL REVIEW</option>
                  <option value="FAILED">Set to FAILED</option>
                </select>

                {/* Export Selected Excel */}
                <a
                  href={api.getExportUrl({ format: "xlsx", claim_ids: selectedIds.join(",") })}
                  download
                  className="px-2.5 py-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-lg font-semibold flex items-center gap-1"
                >
                  <Download className="w-3 h-3" />
                  <span>Export Selected (.xlsx)</span>
                </a>

                {/* Bulk Delete */}
                <button
                  onClick={() => setIsBulkDeleteOpen(true)}
                  className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-semibold flex items-center gap-1 cursor-pointer"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Delete Selected</span>
                </button>

                {/* Clear Selection */}
                <button
                  onClick={() => setSelectedIds([])}
                  className="px-2 py-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* Desktop/Tablet Table (>= md) */}
          <div className="hidden md:block overflow-x-auto w-full">
            <table className="w-full text-left text-xs min-w-[950px]">
              <thead className="text-[11px] text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 uppercase">
                <tr>
                  <th className="py-3 px-3 w-10 text-center">
                    <button
                      onClick={handleSelectAllVisible}
                      className="cursor-pointer text-slate-500 hover:text-indigo-600"
                    >
                      {selectedIds.length === claims.length && claims.length > 0 ? (
                        <CheckSquare className="w-4 h-4 text-indigo-600" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                  </th>
                  <th className="py-3 px-3 cursor-pointer select-none" onClick={() => handleSort("claim_number")}>
                    Claim # {renderSortIcon("claim_number")}
                  </th>
                  <th className="py-3 px-3 cursor-pointer select-none" onClick={() => handleSort("insured_last_name")}>
                    Parties {renderSortIcon("insured_last_name")}
                  </th>
                  <th className="py-3 px-3 cursor-pointer select-none" onClick={() => handleSort("policy_state")}>
                    State {renderSortIcon("policy_state")}
                  </th>
                  <th className="py-3 px-3 cursor-pointer select-none" onClick={() => handleSort("record_status")}>
                    Overall Status {renderSortIcon("record_status")}
                  </th>
                  <th className="py-3 px-3">Florida Bots</th>
                  <th className="py-3 px-3">Texas Bots</th>
                  <th className="py-3 px-3 cursor-pointer select-none" onClick={() => handleSort("total_duration_seconds")}>
                    Duration {renderSortIcon("total_duration_seconds")}
                  </th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {claims.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-slate-400 dark:text-slate-500">
                      No claims found matching current search and filters.
                    </td>
                  </tr>
                ) : (
                  claims.map((claim) => {
                    const flBots = claim.bots.filter((b) => b.name.includes("(FL)"));
                    const txBots = claim.bots.filter((b) => b.name.includes("(TX)"));
                    const isSelected = selectedIds.includes(claim.id);
                    const isExpanded = expandedClaimIds.has(claim.id);

                    return (
                      <React.Fragment key={claim.id}>
                        <tr
                          className={`hover:bg-slate-50 dark:hover:bg-slate-900/60 transition-colors ${
                            isSelected ? "bg-indigo-50/50 dark:bg-indigo-950/20" : ""
                          }`}
                        >
                          {/* Checkbox & Expand Toggle */}
                          <td className="py-3 px-3 text-center">
                            <div className="flex items-center justify-center gap-1">
                              <button
                                type="button"
                                onClick={() => toggleClaimExpansion(claim.id)}
                                title={isExpanded ? "Collapse portal matrix" : "Expand 8-portal matrix"}
                                className="p-1 rounded text-slate-400 hover:text-indigo-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                                ) : (
                                  <ChevronRight className="w-3.5 h-3.5" />
                                )}
                              </button>
                              <button
                                onClick={() => handleToggleSelectRow(claim.id)}
                                className="cursor-pointer text-slate-400 hover:text-indigo-600"
                              >
                                {isSelected ? (
                                  <CheckSquare className="w-4 h-4 text-indigo-600" />
                                ) : (
                                  <Square className="w-4 h-4" />
                                )}
                              </button>
                            </div>
                          </td>

                          {/* Claim # */}
                          <td className="py-3 px-3 font-mono font-medium text-slate-900 dark:text-slate-200">
                            <div className="flex flex-col">
                              <div className="flex items-center gap-1.5">
                                <Link
                                  href={`/claims/${claim.id}`}
                                  className="text-indigo-600 dark:text-indigo-400 hover:underline font-bold"
                                >
                                  {claim.claim_number}
                                </Link>
                                {claim.exposure_number && (
                                  <span className="text-[10px] text-slate-400 font-normal">
                                    (Exp {claim.exposure_number})
                                  </span>
                                )}
                              </div>
                              {claim.primary_key && (
                                <span className="text-[10px] text-slate-400 font-mono">
                                  PK: {claim.primary_key}
                                </span>
                              )}
                            </div>
                          </td>

                          {/* Parties */}
                          <td className="py-3 px-3">
                            <div className="text-slate-800 dark:text-slate-200 font-medium">{claim.insured_name}</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">vs. {claim.claimant_name}</div>
                          </td>

                          {/* State & County */}
                          <td className="py-3 px-3 text-slate-600 dark:text-slate-400">
                            <div>{claim.loss_location_state || claim.policy_state || "N/A"}</div>
                          </td>

                          {/* Overall Status */}
                          <td className="py-3 px-3">
                            <StatusBadge status={claim.record_status} size="sm" />
                          </td>

                          {/* Florida Bots */}
                          <td className="py-3 px-3">
                            <div className="flex gap-1 flex-wrap">
                              {flBots.map((b) => (
                                <span
                                  key={b.name}
                                  title={`${b.name}: ${b.status} (${b.cases_found} cases)`}
                                  className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                                    b.target === "No"
                                      ? "bg-slate-100 dark:bg-slate-900 text-slate-400 dark:text-slate-600"
                                      : b.status === "COMPLETED"
                                      ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800"
                                      : b.status === "IN_PROGRESS"
                                      ? "bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-400 animate-pulse border border-amber-300 dark:border-amber-800"
                                      : b.status === "FAILED"
                                      ? "bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-400 border border-rose-300 dark:border-rose-800"
                                      : "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-400"
                                  }`}
                                >
                                  {b.name.split(" ")[0].slice(0, 3)}
                                </span>
                              ))}
                            </div>
                          </td>

                          {/* Texas Bots */}
                          <td className="py-3 px-3">
                            <div className="flex gap-1 flex-wrap">
                              {txBots.map((b) => (
                                <span
                                  key={b.name}
                                  title={`${b.name}: ${b.status} (${b.cases_found} cases)`}
                                  className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                                    b.target === "No"
                                      ? "bg-slate-100 dark:bg-slate-900 text-slate-400 dark:text-slate-600"
                                      : b.status === "COMPLETED"
                                      ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800"
                                      : b.status === "IN_PROGRESS"
                                      ? "bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-400 animate-pulse border border-amber-300 dark:border-amber-800"
                                      : b.status === "FAILED"
                                      ? "bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-400 border border-rose-300 dark:border-rose-800"
                                      : "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-400"
                                  }`}
                                >
                                  {b.name.split(" ")[0].slice(0, 3)}
                                </span>
                              ))}
                            </div>
                          </td>

                          {/* Duration */}
                          <td className="py-3 px-3 font-mono text-[11px] text-slate-600 dark:text-slate-400">
                            {claim.total_duration_seconds !== null && claim.total_duration_seconds !== undefined ? (
                              <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-bold text-slate-800 dark:text-slate-200">
                                ⏱️ {claim.total_duration_seconds}s
                              </span>
                            ) : claim.action_timings?.total_scraping_seconds ? (
                              <span className="px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
                                ⏱️ {claim.action_timings.total_scraping_seconds}s
                              </span>
                            ) : (
                              <span className="text-slate-400">-</span>
                            )}
                          </td>

                          {/* Row Actions */}
                          <td className="py-3 px-3 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              {/* Start / Retry Automation */}
                              <button
                                onClick={() => handleStartSingle(claim.id, claim.claim_number)}
                                title="Start / Retry RPA Scrapers"
                                className="p-1 rounded text-slate-500 hover:text-emerald-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                              >
                                <Play className="w-3.5 h-3.5" />
                              </button>

                              {/* Edit Claim */}
                              <button
                                onClick={() => {
                                  setEditingClaim(claim);
                                  setFormData({
                                    primary_key: claim.primary_key || "",
                                    claim_number: claim.claim_number,
                                    exposure_number: claim.exposure_number || "1",
                                    insured_first_name: claim.insured_first_name || claim.insured_name.split(" ")[0] || "",
                                    insured_last_name: claim.insured_last_name || claim.insured_name.split(" ").slice(1).join(" ") || "",
                                    claimant_first_name: claim.claimant_first_name || claim.claimant_name.split(" ")[0] || "",
                                    claimant_last_name: claim.claimant_last_name || claim.claimant_name.split(" ").slice(1).join(" ") || "",
                                    driver_first_name: claim.driver_first_name || claim.driver_name?.split(" ")[0] || "",
                                    driver_last_name: claim.driver_last_name || claim.driver_name?.split(" ").slice(1).join(" ") || "",
                                    dol: claim.dol || "",
                                    policy_state: claim.policy_state || "Florida",
                                    loss_location_state: claim.loss_location_state || "Florida",
                                  });
                                  setIsEditOpen(true);
                                }}
                                title="Edit Claim"
                                className="p-1 rounded text-slate-500 hover:text-indigo-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                              </button>

                              {/* Delete Claim */}
                              <button
                                onClick={() => {
                                  setDeletingId(claim.id);
                                  setIsDeleteOpen(true);
                                }}
                                title="Delete Claim"
                                className="p-1 rounded text-slate-500 hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>

                              {/* View 360 Detail */}
                              <Link
                                href={`/claims/${claim.id}`}
                                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-semibold ml-1"
                              >
                                Inspect &rarr;
                              </Link>
                            </div>
                          </td>
                        </tr>

                        {/* Expandable 8-Portal Execution Matrix (§61) */}
                        {isExpanded && (
                          <tr className="bg-slate-50/70 dark:bg-slate-900/60 border-b border-indigo-100 dark:border-indigo-950/60">
                            <td colSpan={9} className="p-3.5 sm:p-5">
                              <div className="bg-white dark:bg-slate-950 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-inner space-y-3">
                                <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-100 dark:border-slate-800 text-xs">
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                                      Claim #{claim.claim_number}
                                    </span>
                                    <span className="text-slate-500 dark:text-slate-400">
                                      — 8-County Portal Execution Matrix & On-Demand Bot Controls
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-2 text-slate-500 text-[11px] font-mono">
                                    <span>Routing: <strong className="text-slate-700 dark:text-slate-300">{claim.policy_state || "FL"} / {claim.loss_location_state || "FL"}</strong></span>
                                    <span>•</span>
                                    <span>Target Portals: {claim.bots.filter((b) => b.target === "Yes").length} / {claim.bots.length}</span>
                                  </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
                                  {claim.bots.map((bot) => {
                                    const botKey = getBotKeyFromName(bot.name);
                                    const isRunningThisBot = runningBotKey === `${claim.id}_${botKey}`;
                                    const isCompleted = bot.status === "COMPLETED";
                                    const isFailed = bot.status === "FAILED";
                                    const isInProgress = bot.status === "IN_PROGRESS";
                                    const isTarget = bot.target === "Yes";

                                    return (
                                      <div
                                        key={bot.name}
                                        className={`p-3 rounded-lg border text-xs flex flex-col justify-between transition-all ${
                                          isCompleted
                                            ? "border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/40 dark:bg-emerald-950/20"
                                            : isFailed
                                            ? "border-rose-200 dark:border-rose-900/50 bg-rose-50/40 dark:bg-rose-950/20"
                                            : isInProgress
                                            ? "border-amber-200 dark:border-amber-900/50 bg-amber-50/40 dark:bg-amber-950/20 animate-pulse"
                                            : "border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/40 text-slate-500"
                                        }`}
                                      >
                                        <div className="space-y-1 mb-2">
                                          <div className="flex items-center justify-between gap-1.5">
                                            <span className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                                              {bot.name}
                                            </span>
                                            {!isTarget && (
                                              <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-200/70 dark:bg-slate-800 text-slate-500 font-mono">
                                                Bypassed
                                              </span>
                                            )}
                                          </div>
                                          <div className="flex items-center justify-between text-[11px]">
                                            <span className="text-slate-500 font-mono">Key: {botKey}</span>
                                            <span
                                              className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                                                isCompleted
                                                  ? "bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300"
                                                  : isFailed
                                                  ? "bg-rose-100 dark:bg-rose-900/60 text-rose-800 dark:text-rose-300"
                                                  : isInProgress
                                                  ? "bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-300"
                                                  : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                                              }`}
                                            >
                                              {bot.status}
                                            </span>
                                          </div>
                                        </div>

                                        <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
                                          <span className="text-[11px] text-slate-500">
                                            Cases: <strong className="text-slate-900 dark:text-slate-100 font-mono">{bot.cases_found}</strong>
                                          </span>
                                          <button
                                            type="button"
                                            onClick={() => handleRunSingleBot(claim.id, botKey, bot.name)}
                                            disabled={isRunningThisBot || isInProgress}
                                            title={`Dispatch ${bot.name} scraper bot`}
                                            className="px-2 py-1 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/70 dark:hover:bg-indigo-900/70 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/80 rounded text-[11px] font-semibold flex items-center gap-1 cursor-pointer transition-colors disabled:opacity-50"
                                          >
                                            {isRunningThisBot ? (
                                              <RefreshCw className="w-3 h-3 animate-spin" />
                                            ) : (
                                              <Zap className="w-3 h-3" />
                                            )}
                                            Run Bot
                                          </button>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Mobile-Friendly Cards List (< md) */}
          <div className="block md:hidden space-y-3 w-full">
            {claims.length === 0 ? (
              <div className="py-8 text-center text-slate-400 dark:text-slate-500 text-xs">
                No claims match your filters.
              </div>
            ) : (
              claims.map((claim) => {
                const isSelected = selectedIds.includes(claim.id);
                const isExpanded = expandedClaimIds.has(claim.id);
                const flBots = claim.bots.filter((b) => b.name.includes("(FL)"));
                const txBots = claim.bots.filter((b) => b.name.includes("(TX)"));
                const activeState = claim.loss_location_state || claim.policy_state || "Florida";

                return (
                  <div
                    key={claim.id}
                    className={cn(
                      "bg-slate-50 dark:bg-slate-900/70 border rounded-xl p-3.5 space-y-2.5 transition-all shadow-xs",
                      isSelected
                        ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 ring-1 ring-indigo-500"
                        : "border-slate-200 dark:border-slate-800"
                    )}
                  >
                    {/* Header: Checkbox + Expand + Claim Number + Exposure + Primary Key + Status */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <button
                          type="button"
                          onClick={() => toggleClaimExpansion(claim.id)}
                          title={isExpanded ? "Collapse portal matrix" : "Expand 8-portal matrix"}
                          className="p-1 text-slate-400 hover:text-indigo-600 cursor-pointer min-h-[36px] min-w-[36px] flex items-center justify-center"
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleToggleSelectRow(claim.id)}
                          className="p-1 text-slate-400 hover:text-indigo-600 cursor-pointer min-h-[36px] min-w-[36px] flex items-center justify-center"
                        >
                          {isSelected ? (
                            <CheckSquare className="w-4 h-4 text-indigo-600" />
                          ) : (
                            <Square className="w-4 h-4" />
                          )}
                        </button>
                        <span className="font-mono font-bold text-xs text-slate-900 dark:text-slate-100">
                          {claim.claim_number}
                        </span>
                        {claim.exposure_number && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                            Exp {claim.exposure_number}
                          </span>
                        )}
                        {claim.primary_key && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-mono">
                            PK {claim.primary_key}
                          </span>
                        )}
                      </div>
                      <StatusBadge status={claim.record_status} size="sm" />
                    </div>

                    {/* Parties Grid */}
                    <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 dark:text-slate-300">
                      <div>
                        <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Insured</span>
                        <span className="font-medium truncate block">{claim.insured_name || "N/A"}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Claimant</span>
                        <span className="font-medium truncate block">{claim.claimant_name || "N/A"}</span>
                      </div>
                    </div>

                    {/* Geography & Fuzzy Match */}
                    <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-200/60 dark:border-slate-800/60">
                      <span>{activeState}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-400">Match:</span>
                        <StatusBadge status={claim.fuzzy_match_status} size="sm" />
                      </div>
                    </div>

                    {/* County Bot Status Badges */}
                    <div className="flex items-center gap-1.5 flex-wrap pt-1">
                      <span className="text-[10px] text-slate-400">Bots:</span>
                      {(activeState === "Florida" ? flBots : txBots).map((b) => (
                        <span
                          key={b.name}
                          className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                            b.status === "COMPLETED"
                              ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400"
                              : b.status === "IN_PROGRESS"
                              ? "bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-400 animate-pulse"
                              : b.status === "FAILED"
                              ? "bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-400"
                              : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                          }`}
                        >
                          {b.name.slice(0, 3)}
                        </span>
                      ))}
                    </div>

                    {/* Expandable 8-Portal Matrix in Mobile Card (§61) */}
                    {isExpanded && (
                      <div className="pt-2 border-t border-slate-200 dark:border-slate-800 space-y-2">
                        <div className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                          8-Portal Execution Status & On-Demand Bot Controls:
                        </div>
                        <div className="grid grid-cols-1 gap-2">
                          {claim.bots.map((bot) => {
                            const botKey = getBotKeyFromName(bot.name);
                            const isRunningThisBot = runningBotKey === `${claim.id}_${botKey}`;
                            return (
                              <div
                                key={bot.name}
                                className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center justify-between gap-2 text-xs"
                              >
                                <div>
                                  <div className="font-semibold text-slate-900 dark:text-slate-100">{bot.name}</div>
                                  <div className="text-[10px] text-slate-500 font-mono">
                                    Status: <span className="font-bold">{bot.status}</span> • Cases: {bot.cases_found}
                                  </div>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => handleRunSingleBot(claim.id, botKey, bot.name)}
                                  disabled={isRunningThisBot || bot.status === "IN_PROGRESS"}
                                  className="px-2.5 py-1 bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded text-[11px] font-semibold flex items-center gap-1 cursor-pointer disabled:opacity-50"
                                >
                                  {isRunningThisBot ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
                                  Run
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Actions Toolbar */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 dark:border-slate-800/60">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleStartSingle(claim.id, claim.claim_number)}
                          title="Start Automation"
                          className="p-2 text-slate-500 hover:text-emerald-600 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-lg min-h-[36px] min-w-[36px] flex items-center justify-center cursor-pointer"
                        >
                          <Play className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            setEditingClaim(claim);
                            setFormData({
                              primary_key: claim.primary_key || "",
                              claim_number: claim.claim_number,
                              exposure_number: claim.exposure_number || "1",
                              insured_first_name: claim.insured_first_name || claim.insured_name.split(" ")[0] || "",
                              insured_last_name: claim.insured_last_name || claim.insured_name.split(" ").slice(1).join(" ") || "",
                              claimant_first_name: claim.claimant_first_name || claim.claimant_name.split(" ")[0] || "",
                              claimant_last_name: claim.claimant_last_name || claim.claimant_name.split(" ").slice(1).join(" ") || "",
                              driver_first_name: claim.driver_first_name || claim.driver_name?.split(" ")[0] || "",
                              driver_last_name: claim.driver_last_name || claim.driver_name?.split(" ").slice(1).join(" ") || "",
                              dol: claim.dol || "",
                              policy_state: claim.policy_state || "Florida",
                              loss_location_state: claim.loss_location_state || "Florida",
                            });
                            setIsEditOpen(true);
                          }}
                          title="Edit Claim"
                          className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-lg min-h-[36px] min-w-[36px] flex items-center justify-center cursor-pointer"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            setDeletingId(claim.id);
                            setIsDeleteOpen(true);
                          }}
                          title="Delete Claim"
                          className="p-2 text-slate-500 hover:text-rose-600 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-lg min-h-[36px] min-w-[36px] flex items-center justify-center cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <Link
                        href={`/claims/${claim.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 font-semibold text-xs rounded-lg min-h-[36px]"
                      >
                        Inspect &rarr;
                      </Link>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Pagination Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-slate-200 dark:border-slate-800/80 text-xs text-slate-600 dark:text-slate-400">
            <div className="flex items-center justify-between sm:justify-start gap-2 w-full sm:w-auto">
              <span>Showing {claims.length > 0 ? (page - 1) * pageSize + 1 : 0} to {Math.min(page * pageSize, total)} of {total} claims</span>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-300 dark:text-slate-700">|</span>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
                    setPage(1);
                  }}
                  className="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded px-2 py-1 text-xs"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={250}>250</option>
                  <option value={500}>500</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-center sm:justify-end gap-2 w-full sm:w-auto">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3.5 py-2 bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-40 border border-slate-200 dark:border-slate-800 rounded-lg transition-all flex items-center gap-1 cursor-pointer min-h-[40px]"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Previous</span>
              </button>
              <span className="font-semibold text-slate-800 dark:text-slate-200 px-2">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-3.5 py-2 bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-40 border border-slate-200 dark:border-slate-800 rounded-lg transition-all flex items-center gap-1 cursor-pointer min-h-[40px]"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* CREATE CLAIM MODAL */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-t-2xl sm:rounded-2xl max-w-lg w-full max-h-[90vh] flex flex-col p-5 sm:p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Plus className="w-4 h-4 text-emerald-500" />
                Create Single Claim Record
              </h3>
              <button onClick={() => setIsCreateOpen(false)} className="text-slate-400 hover:text-slate-600 p-1 min-h-[36px] min-w-[36px] flex items-center justify-center">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs overflow-y-auto flex-1 pr-1 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Primary Key</label>
                  <input
                    type="text"
                    value={formData.primary_key}
                    onChange={(e) => setFormData({ ...formData, primary_key: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
                    placeholder="e.g. CLM-2026-999"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Exposure Number</label>
                  <input
                    type="text"
                    value={formData.exposure_number}
                    onChange={(e) => setFormData({ ...formData, exposure_number: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
                    placeholder="e.g. 1"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                    placeholder="Insured First Name"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Insured Last Name</label>
                  <input
                    type="text"
                    value={formData.insured_last_name}
                    onChange={(e) => setFormData({ ...formData, insured_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                    placeholder="Insured Last Name"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                    placeholder="Claimant First Name"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Claimant Last Name</label>
                  <input
                    type="text"
                    value={formData.claimant_last_name}
                    onChange={(e) => setFormData({ ...formData, claimant_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                    placeholder="Claimant Last Name"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                    placeholder="Driver First Name"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Driver Last Name (Insured Vehicle)</label>
                  <input
                    type="text"
                    value={formData.driver_last_name}
                    onChange={(e) => setFormData({ ...formData, driver_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                    placeholder="Driver Last Name"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">DOL (Date of Loss)</label>
                  <input
                    type="text"
                    placeholder="MM/DD/YYYY"
                    value={formData.dol}
                    onChange={(e) => setFormData({ ...formData, dol: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Policy State</label>
                  <select
                    value={formData.policy_state}
                    onChange={(e) => setFormData({ ...formData, policy_state: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  >
                    <option value="Florida">Florida</option>
                    <option value="Texas">Texas</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Loss Location State</label>
                  <select
                    value={formData.loss_location_state}
                    onChange={(e) => setFormData({ ...formData, loss_location_state: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  >
                    <option value="Florida">Florida</option>
                    <option value="Texas">Texas</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300 font-semibold min-h-[40px]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold cursor-pointer min-h-[40px]"
                >
                  Create Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT CLAIM MODAL */}
      {isEditOpen && editingClaim && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-t-2xl sm:rounded-2xl max-w-lg w-full max-h-[90vh] flex flex-col p-5 sm:p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-indigo-500" />
                Edit Claim: {editingClaim.claim_number}
              </h3>
              <button onClick={() => setIsEditOpen(false)} className="text-slate-400 hover:text-slate-600 p-1 min-h-[36px] min-w-[36px] flex items-center justify-center">
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Exposure Number</label>
                  <input
                    type="text"
                    value={formData.exposure_number}
                    onChange={(e) => setFormData({ ...formData, exposure_number: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Insured Last Name</label>
                  <input
                    type="text"
                    value={formData.insured_last_name}
                    onChange={(e) => setFormData({ ...formData, insured_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Claimant Last Name</label>
                  <input
                    type="text"
                    value={formData.claimant_last_name}
                    onChange={(e) => setFormData({ ...formData, claimant_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
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
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Driver Last Name (Insured Vehicle)</label>
                  <input
                    type="text"
                    value={formData.driver_last_name}
                    onChange={(e) => setFormData({ ...formData, driver_last_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">DOL (Date of Loss)</label>
                  <input
                    type="text"
                    placeholder="MM/DD/YYYY"
                    value={formData.dol}
                    onChange={(e) => setFormData({ ...formData, dol: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 font-mono min-h-[40px]"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Policy State</label>
                  <select
                    value={formData.policy_state}
                    onChange={(e) => setFormData({ ...formData, policy_state: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  >
                    <option value="Florida">Florida</option>
                    <option value="Texas">Texas</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Loss Location State</label>
                  <select
                    value={formData.loss_location_state}
                    onChange={(e) => setFormData({ ...formData, loss_location_state: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 min-h-[40px]"
                  >
                    <option value="Florida">Florida</option>
                    <option value="Texas">Texas</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsEditOpen(false)}
                  className="px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300 font-semibold min-h-[40px]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold cursor-pointer min-h-[40px]"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* SINGLE DELETE CONFIRMATION MODAL */}
      {isDeleteOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-t-2xl sm:rounded-2xl max-w-sm w-full p-5 sm:p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-600">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Delete Claim Record?</h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Are you sure you want to delete this claim? All related scraped court cases and match results will be permanently removed.
            </p>
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                onClick={() => setIsDeleteOpen(false)}
                className="px-3.5 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-xs font-semibold min-h-[40px]"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold cursor-pointer min-h-[40px]"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* BULK DELETE CONFIRMATION MODAL */}
      {isBulkDeleteOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-t-2xl sm:rounded-2xl max-w-sm w-full p-5 sm:p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-600">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Delete {selectedIds.length} Claims?
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              This action will permanently delete all {selectedIds.length} selected claims, including all their scraped court records.
            </p>
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                onClick={() => setIsBulkDeleteOpen(false)}
                className="px-3.5 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-xs font-semibold min-h-[40px]"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkDeleteConfirm}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold cursor-pointer min-h-[40px]"
              >
                Delete Selected
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CLEAN DATABASE CONFIRMATION MODAL */}
      {isCleanOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-t-2xl sm:rounded-2xl max-w-md w-full p-5 sm:p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-600">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Purge Database & Redis Queues?
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              This will completely wipe all claim records, scraped court cases, fuzzy match results, ingestion batches, and purge all pending Celery queues.
              Use this to perform a completely fresh start.
            </p>
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                onClick={() => setIsCleanOpen(false)}
                className="px-3.5 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-xs font-semibold min-h-[40px]"
              >
                Cancel
              </button>
              <button
                onClick={handleCleanDatabase}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold cursor-pointer min-h-[40px]"
              >
                Yes, Purge Everything
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Background Celery Streaming Export Modal (§55) */}
      <AsyncExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        statusFilter={statusFilter}
        stateFilter={stateFilter}
        searchTerm={searchTerm}
        selectedIds={selectedIds}
        totalRecordsCount={total}
      />
    </div>
  );
}
