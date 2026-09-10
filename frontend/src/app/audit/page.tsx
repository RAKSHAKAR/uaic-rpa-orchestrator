"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  ScrollText,
  Search,
  RefreshCw,
  Eye,
  Copy,
  Check,
  X,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Activity,
  Sliders,
  AlertCircle,
  Clock,
  User,
  Database,
  FileSpreadsheet,
  FileJson,
  ExternalLink,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import { Navbar } from "../../components/Navbar";
import { StatCard } from "../../components/StatCard";
import { MultiSelectDropdown } from "../../components/MultiSelectDropdown";
import { api } from "../../lib/api";
import { AuditLogEntry, AuditLogStats, AuditLogQueryParams } from "../../types";

const ACTION_OPTIONS = [
  { value: "CLAIM_CREATED", label: "Claim Created", count: undefined },
  { value: "CLAIM_UPDATED", label: "Claim Updated", count: undefined },
  { value: "CLAIM_DELETED", label: "Claim Deleted", count: undefined },
  { value: "AUTOMATION_STARTED", label: "Automation Started", count: undefined },
  { value: "AUTOMATION_STOPPED", label: "Automation Stopped", count: undefined },
  { value: "SCRAPING_COMPLETED", label: "Scraping Completed", count: undefined },
  { value: "SCRAPING_FAILED", label: "Scraping Failed", count: undefined },
  { value: "FUZZY_MATCHING_COMPLETED", label: "Fuzzy Completed", count: undefined },
  { value: "GUIDEWIRE_PUSHED", label: "Guidewire Pushed", count: undefined },
  { value: "GUIDEWIRE_PUSH_SUCCESS", label: "Guidewire Push OK", count: undefined },
  { value: "GUIDEWIRE_PUSH_FAILED", label: "Guidewire Push Fail", count: undefined },
  { value: "SINGLE_BOT_TRIGGERED", label: "Single Bot Run", count: undefined },
  { value: "FAILED_PORTALS_RETRIED", label: "Portals Retried", count: undefined },
  { value: "BATCH_IMPORTED", label: "Batch Ingested", count: undefined },
  { value: "MATCH_REVIEWED", label: "Match Reviewed", count: undefined },
  { value: "SETTINGS_UPDATED", label: "Settings Saved", count: undefined },
  { value: "SETTINGS_RESET", label: "Settings Reset", count: undefined },
  { value: "BRANDING_UPDATED", label: "Brand Saved", count: undefined },
  { value: "QUEUE_RETRIGGERED", label: "Queue Retrigger", count: undefined },
  { value: "DATABASE_CLEARED", label: "Database Cleared", count: undefined },
];

const ENTITY_OPTIONS = [
  { value: "CLAIM", label: "Claim" },
  { value: "SETTINGS", label: "Settings" },
  { value: "BRANDING", label: "Branding" },
  { value: "MATCH_PAIR", label: "Match Pair" },
  { value: "QUEUE", label: "Queue" },
  { value: "BATCH", label: "Batch Ingestion" },
  { value: "DATABASE", label: "Database" },
];

const STATUS_OPTIONS = [
  { value: "SUCCESS", label: "Success" },
  { value: "FAILED", label: "Failed" },
  { value: "ERROR", label: "Error" },
];

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [stats, setStats] = useState<AuditLogStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  // Filters and Query Params
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedActions, setSelectedActions] = useState<string[]>([]);
  const [selectedEntityTypes, setSelectedEntityTypes] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);

  // Sorting state
  const [sortBy, setSortBy] = useState<string>("timestamp");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  // Modal inspection state
  const [inspectedLog, setInspectedLog] = useState<AuditLogEntry | null>(null);
  const [copiedPayload, setCopiedPayload] = useState(false);

  // Export states
  const [isExporting, setIsExporting] = useState<string | null>(null);
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load audit logs
  const fetchAuditLogs = useCallback(async () => {
    try {
      const params: AuditLogQueryParams = {
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_dir: sortDir,
      };
      if (debouncedSearch.trim()) params.search = debouncedSearch.trim();
      if (selectedActions.length > 0) params.action = selectedActions.join(",");
      if (selectedEntityTypes.length > 0) params.entity_type = selectedEntityTypes.join(",");
      if (selectedStatuses.length > 0) params.status = selectedStatuses.join(",");

      const res = await api.getAuditLogs(params);
      setLogs(res.items || []);
      setTotalCount(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err: any) {
      console.error("Failed to load audit logs:", err);
      setNotification({
        type: "error",
        message: "Failed to load audit trail records from server.",
      });
    }
  }, [page, pageSize, sortBy, sortDir, debouncedSearch, selectedActions, selectedEntityTypes, selectedStatuses]);

  // Load audit statistics
  const fetchAuditStats = useCallback(async () => {
    try {
      const res = await api.getAuditLogStats();
      setStats(res);
    } catch (err) {
      console.error("Failed to load audit stats:", err);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    setIsRefreshing(true);
    await Promise.all([fetchAuditLogs(), fetchAuditStats()]);
    setIsRefreshing(false);
  }, [fetchAuditLogs, fetchAuditStats]);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([fetchAuditLogs(), fetchAuditStats()]).finally(() => {
      setIsLoading(false);
    });
  }, [fetchAuditLogs, fetchAuditStats]);

  // Handle column header sorting
  const handleSort = (columnKey: string) => {
    if (sortBy === columnKey) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(columnKey);
      setSortDir("desc");
    }
    setPage(1);
  };

  // Export handler
  const handleExport = async (format: "csv" | "json" | "xlsx") => {
    setIsExporting(format);
    try {
      const params: AuditLogQueryParams & { format: "csv" | "json" | "xlsx" } = {
        format,
        sort_by: sortBy,
        sort_dir: sortDir,
      };
      if (debouncedSearch.trim()) params.search = debouncedSearch.trim();
      if (selectedActions.length > 0) params.action = selectedActions.join(",");
      if (selectedEntityTypes.length > 0) params.entity_type = selectedEntityTypes.join(",");
      if (selectedStatuses.length > 0) params.status = selectedStatuses.join(",");

      const blob = await api.exportAuditLogs(params);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `audit_trail_export_${new Date().toISOString().slice(0, 10)}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setNotification({
        type: "success",
        message: `Successfully exported audit logs as ${format.toUpperCase()}.`,
      });
    } catch (err: any) {
      console.error("Audit export failed:", err);
      setNotification({
        type: "error",
        message: `Failed to export audit logs as ${format.toUpperCase()}.`,
      });
    } finally {
      setIsExporting(null);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPayload(true);
    setTimeout(() => setCopiedPayload(false), 2000);
  };

  // Format timestamp helper
  const formatTimestamp = (ts: string) => {
    try {
      const date = new Date(ts);
      return {
        dateStr: date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        timeStr: date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        relative: getRelativeTime(date),
      };
    } catch {
      return { dateStr: ts, timeStr: "", relative: "" };
    }
  };

  const getRelativeTime = (date: Date) => {
    const diffSeconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    if (diffSeconds < 60) return "just now";
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m ago`;
    if (diffSeconds < 86400) return `${Math.floor(diffSeconds / 3600)}h ago`;
    return `${Math.floor(diffSeconds / 86400)}d ago`;
  };

  // Action badge color styling
  const getActionBadgeClass = (action: string) => {
    const act = action.toUpperCase();
    if (act.includes("FAIL") || act.includes("DELETE") || act.includes("ERROR")) {
      return "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400 border-rose-200 dark:border-rose-800/60";
    }
    if (act.includes("SETTING") || act.includes("BRAND")) {
      return "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200 dark:border-amber-800/60";
    }
    if (act.includes("QUEUE") || act.includes("AUTO")) {
      return "bg-cyan-50 text-cyan-700 dark:bg-cyan-950/40 dark:text-cyan-400 border-cyan-200 dark:border-cyan-800/60";
    }
    if (act.includes("MATCH")) {
      return "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/60";
    }
    if (act.includes("INGEST") || act.includes("IMPORT") || act.includes("BATCH")) {
      return "bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-400 border-purple-200 dark:border-purple-800/60";
    }
    if (act.includes("GUIDEWIRE")) {
      return "bg-teal-50 text-teal-700 dark:bg-teal-950/40 dark:text-teal-400 border-teal-200 dark:border-teal-800/60";
    }
    return "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800/60";
  };

  const renderSortIndicator = (columnKey: string) => {
    if (sortBy !== columnKey) {
      return <ArrowUpDown className="w-3 h-3 opacity-40 group-hover:opacity-100 transition-opacity" />;
    }
    return sortDir === "asc" ? (
      <ArrowUp className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
    ) : (
      <ArrowDown className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
    );
  };

  const hasActiveFilters =
    Boolean(searchQuery) ||
    selectedActions.length > 0 ||
    selectedEntityTypes.length > 0 ||
    selectedStatuses.length > 0;

  const resetAllFilters = () => {
    setSearchQuery("");
    setSelectedActions([]);
    setSelectedEntityTypes([]);
    setSelectedStatuses([]);
    setPage(1);
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors">
      <Navbar onRefresh={refreshAll} isRefreshing={isRefreshing} />

      <main className="w-full max-w-none flex-1 p-4 sm:p-6 md:p-8 space-y-6">
        {/* Notification Banner */}
        {notification && (
          <div
            className={`p-4 rounded-xl flex items-center justify-between text-xs font-medium border shadow-xs transition-all ${
              notification.type === "success"
                ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"
            }`}
          >
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="p-1 hover:opacity-75 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                <ScrollText className="w-3.5 h-3.5" />
                Audit Trail & Compliance Ledger (§73)
              </span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                <ShieldCheck className="w-3 h-3" /> Zero Leakage Verified
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 tracking-tight">
              Audit Logs & Provenance Console
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Immutable chronological record of user operations, RPA bot triggers, system configurations, and Guidewire dispatches.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={refreshAll}
              disabled={isRefreshing}
              className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 shadow-2xs flex items-center gap-2 cursor-pointer transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-indigo-500" : ""}`} />
              <span>Refresh</span>
            </button>

            <button
              onClick={() => handleExport("xlsx")}
              disabled={isExporting !== null}
              className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-white dark:bg-slate-800 border border-emerald-300 dark:border-emerald-700/60 hover:bg-emerald-50 dark:hover:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 shadow-2xs flex items-center gap-2 cursor-pointer transition-all disabled:opacity-50"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>{isExporting === "xlsx" ? "Exporting..." : "Export Excel"}</span>
            </button>

            <button
              onClick={() => handleExport("csv")}
              disabled={isExporting !== null}
              className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 shadow-2xs flex items-center gap-2 cursor-pointer transition-all disabled:opacity-50"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-slate-500" />
              <span>{isExporting === "csv" ? "Exporting..." : "Export CSV"}</span>
            </button>

            <button
              onClick={() => handleExport("json")}
              disabled={isExporting !== null}
              className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-xs flex items-center gap-2 cursor-pointer transition-all disabled:opacity-50"
            >
              <FileJson className="w-3.5 h-3.5" />
              <span>{isExporting === "json" ? "Exporting..." : "Export JSON"}</span>
            </button>
          </div>
        </div>

        {/* Reusable Stat Cards Strip (matching Dashboard design language & clickable) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          <StatCard
            label="Total Events"
            value={stats ? stats.total_events : "-"}
            subtext="All logged operations"
            icon={ScrollText}
            gradient="indigo"
            selected={!hasActiveFilters}
            onClick={resetAllFilters}
          />

          <StatCard
            label="Today's Activity"
            value={stats ? stats.total_today : "-"}
            subtext="Past 24 hours"
            icon={Clock}
            gradient="cyan"
          />

          <StatCard
            label="Claim Ops"
            value={stats ? stats.total_claims_ops : "-"}
            subtext="Create/Edit/Push/Delete"
            icon={Database}
            gradient="blue"
            selected={selectedEntityTypes.includes("CLAIM") && selectedEntityTypes.length === 1}
            onClick={() => {
              setSelectedEntityTypes((prev) =>
                prev.length === 1 && prev[0] === "CLAIM" ? [] : ["CLAIM"]
              );
              setPage(1);
            }}
          />

          <StatCard
            label="Config Changes"
            value={stats ? stats.total_settings_ops : "-"}
            subtext="Settings & Brand edits"
            icon={Sliders}
            gradient="amber"
            selected={selectedEntityTypes.includes("SETTINGS") && selectedEntityTypes.length === 1}
            onClick={() => {
              setSelectedEntityTypes((prev) =>
                prev.length === 1 && prev[0] === "SETTINGS" ? [] : ["SETTINGS"]
              );
              setPage(1);
            }}
          />

          <StatCard
            label="Match Reviews"
            value={stats ? stats.total_match_reviews : "-"}
            subtext="Approvals / Rejections"
            icon={Activity}
            gradient="emerald"
            selected={selectedEntityTypes.includes("MATCH_PAIR") && selectedEntityTypes.length === 1}
            onClick={() => {
              setSelectedEntityTypes((prev) =>
                prev.length === 1 && prev[0] === "MATCH_PAIR" ? [] : ["MATCH_PAIR"]
              );
              setPage(1);
            }}
          />

          <StatCard
            label="Failures"
            value={stats ? stats.total_failures : "-"}
            subtext="Errors / Abort events"
            icon={AlertCircle}
            gradient="rose"
            selected={selectedStatuses.includes("FAILED") && selectedStatuses.length === 1}
            onClick={() => {
              setSelectedStatuses((prev) =>
                prev.length === 1 && prev[0] === "FAILED" ? [] : ["FAILED"]
              );
              setPage(1);
            }}
          />
        </div>

        {/* Filter & Search Bar with Universal MultiSelect Dropdowns */}
        <div className="bg-white dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-3">
          <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search descriptions, claim numbers, user IDs, or IPs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-8 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Actions Multi-Select */}
            <div className="w-full sm:w-56">
              <MultiSelectDropdown
                label="Actions"
                options={ACTION_OPTIONS}
                selectedValues={selectedActions}
                onChange={(values) => {
                  setSelectedActions(values);
                  setPage(1);
                }}
                placeholder="All Actions"
              />
            </div>

            {/* Entity Types Multi-Select */}
            <div className="w-full sm:w-48">
              <MultiSelectDropdown
                label="Entities"
                options={ENTITY_OPTIONS}
                selectedValues={selectedEntityTypes}
                onChange={(values) => {
                  setSelectedEntityTypes(values);
                  setPage(1);
                }}
                placeholder="All Entities"
              />
            </div>

            {/* Statuses Multi-Select */}
            <div className="w-full sm:w-44">
              <MultiSelectDropdown
                label="Statuses"
                options={STATUS_OPTIONS}
                selectedValues={selectedStatuses}
                onChange={(values) => {
                  setSelectedStatuses(values);
                  setPage(1);
                }}
                placeholder="All Statuses"
              />
            </div>

            {/* Reset Button */}
            {hasActiveFilters && (
              <button
                onClick={resetAllFilters}
                className="px-3 py-2 text-xs font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 whitespace-nowrap cursor-pointer transition-colors"
              >
                Reset Filters
              </button>
            )}
          </div>
        </div>

        {/* Audit Log Table Container with Clickable Sorting Column Headers */}
        <div className="bg-white dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[11px] font-semibold">
                  <th
                    onClick={() => handleSort("timestamp")}
                    className="py-3 px-4 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Timestamp</span>
                      {renderSortIndicator("timestamp")}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("action")}
                    className="py-3 px-4 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Action</span>
                      {renderSortIndicator("action")}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("entity_type")}
                    className="py-3 px-4 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Entity / Target</span>
                      {renderSortIndicator("entity_type")}
                    </div>
                  </th>
                  <th className="py-3 px-4">Description</th>
                  <th
                    onClick={() => handleSort("user_id")}
                    className="py-3 px-4 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Operator</span>
                      {renderSortIndicator("user_id")}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("status")}
                    className="py-3 px-4 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Status</span>
                      {renderSortIndicator("status")}
                    </div>
                  </th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-850">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400 dark:text-slate-500">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <RefreshCw className="w-6 h-6 animate-spin text-indigo-500" />
                        <span>Loading audit trail records...</span>
                      </div>
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400 dark:text-slate-500">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <ScrollText className="w-8 h-8 text-slate-300 dark:text-slate-600" />
                        <span className="font-semibold text-slate-700 dark:text-slate-300">No audit records found</span>
                        <span className="text-xs">Adjust your search criteria or refresh the ledger.</span>
                      </div>
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => {
                    const ts = formatTimestamp(log.timestamp);
                    const isFailed = log.status === "FAILED" || log.status === "ERROR";
                    return (
                      <tr
                        key={log.id}
                        className="hover:bg-slate-50/70 dark:hover:bg-slate-900/50 transition-colors"
                      >
                        {/* Timestamp */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="flex flex-col">
                            <span className="font-semibold text-slate-900 dark:text-slate-100">
                              {ts.dateStr}
                            </span>
                            <div className="flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                              <span>{ts.timeStr}</span>
                              <span className="text-slate-300 dark:text-slate-600">•</span>
                              <span className="italic">{ts.relative}</span>
                            </div>
                          </div>
                        </td>

                        {/* Action Badge */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold border ${getActionBadgeClass(
                              log.action
                            )}`}
                          >
                            {log.action}
                          </span>
                        </td>

                        {/* Entity / Target */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="flex flex-col">
                            <span className="font-semibold text-slate-800 dark:text-slate-200">
                              {log.entity_type}
                            </span>
                            {log.claim_number ? (
                              <Link
                                href={`/claims/${log.entity_id || ""}`}
                                className="inline-flex items-center gap-1 text-[11px] font-mono font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
                              >
                                <span>Claim #{log.claim_number}</span>
                                <ExternalLink className="w-2.5 h-2.5" />
                              </Link>
                            ) : log.entity_id ? (
                              <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono truncate max-w-[120px]">
                                ID: {log.entity_id.slice(0, 8)}...
                              </span>
                            ) : (
                              <span className="text-[11px] text-slate-400 dark:text-slate-500 font-mono">
                                System
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Description */}
                        <td className="py-3 px-4 max-w-xs md:max-w-md">
                          <p className="text-slate-700 dark:text-slate-300 truncate" title={log.description}>
                            {log.description}
                          </p>
                        </td>

                        {/* Operator */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="flex items-center gap-1.5">
                            <div className="w-5 h-5 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-600 dark:text-slate-400">
                              <User className="w-3 h-3" />
                            </div>
                            <div className="flex flex-col">
                              <span className="font-medium text-slate-800 dark:text-slate-200">
                                {log.user_id}
                              </span>
                              <span className="text-[10px] text-slate-400 truncate max-w-[110px]">
                                {log.user_email}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase border ${
                              isFailed
                                ? "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400 border-rose-200 dark:border-rose-800"
                                : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800"
                            }`}
                          >
                            <span
                              className={`w-1.5 h-1.5 rounded-full ${
                                isFailed ? "bg-rose-500" : "bg-emerald-500"
                              }`}
                            />
                            {log.status}
                          </span>
                        </td>

                        {/* Details / Action */}
                        <td className="py-3 px-4 whitespace-nowrap text-right">
                          <button
                            onClick={() => setInspectedLog(log)}
                            className="px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 flex items-center gap-1 ml-auto cursor-pointer transition-colors shadow-2xs"
                          >
                            <Eye className="w-3 h-3 text-indigo-500" />
                            <span>Inspect</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Toolbar with 250 & 500 options */}
          {!isLoading && logs.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
              <div className="flex items-center gap-2">
                <span>Rows per page:</span>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
                    setPage(1);
                  }}
                  className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-md px-2 py-1 text-slate-700 dark:text-slate-300 focus:outline-none cursor-pointer"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={250}>250</option>
                  <option value={500}>500</option>
                </select>
                <span>
                  Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, totalCount)} of {totalCount} records
                </span>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <span className="px-3 py-1 font-mono text-xs font-semibold text-slate-800 dark:text-slate-200">
                  Page {page} of {totalPages}
                </span>

                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                  aria-label="Next page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Inspector Modal */}
      {inspectedLog && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <ScrollText className="w-5 h-5 text-indigo-500" />
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Audit Entry Provenance Inspector
                </h3>
              </div>
              <button
                onClick={() => setInspectedLog(null)}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content Summary */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Action</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                  {inspectedLog.action}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Status</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                  {inspectedLog.status}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Timestamp</span>
                <span className="font-mono text-slate-800 dark:text-slate-200">
                  {formatTimestamp(inspectedLog.timestamp).dateStr}{" "}
                  {formatTimestamp(inspectedLog.timestamp).timeStr}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Operator ID</span>
                <span className="font-mono text-slate-800 dark:text-slate-200 truncate block">
                  {inspectedLog.user_id}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Operator Email</span>
                <span className="font-mono text-slate-800 dark:text-slate-200 truncate block">
                  {inspectedLog.user_email}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">IP Address</span>
                <span className="font-mono text-slate-800 dark:text-slate-200 truncate block">
                  {inspectedLog.ip_address || "Internal/Worker"}
                </span>
              </div>
            </div>

            {/* Description Card */}
            <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 text-xs">
              <span className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Description</span>
              <p className="font-medium text-slate-800 dark:text-slate-200">
                {inspectedLog.description}
              </p>
            </div>

            {/* User Agent */}
            {inspectedLog.user_agent && (
              <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono truncate">
                <span className="font-bold">Client:</span> {inspectedLog.user_agent}
              </div>
            )}

            {/* Payload JSON */}
            <div className="flex-1 overflow-hidden flex flex-col space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-indigo-500" />
                  Audit Payload & Parameters (Zero Credential Leakage Verified)
                </span>
                <button
                  onClick={() => copyToClipboard(JSON.stringify(inspectedLog, null, 2))}
                  className="px-2.5 py-1 text-[11px] font-medium rounded-md bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-300 flex items-center gap-1 cursor-pointer transition-colors"
                >
                  {copiedPayload ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-500" />
                      <span className="text-emerald-600 font-semibold">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>Copy Full Event</span>
                    </>
                  )}
                </button>
              </div>

              <pre className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-indigo-600 dark:text-indigo-400 overflow-y-auto max-h-72">
                {JSON.stringify(inspectedLog.details || {}, null, 2)}
              </pre>
            </div>

            {/* Footer */}
            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <span className="font-mono text-[10px] text-slate-400">
                Log ID: {inspectedLog.id}
              </span>
              <button
                onClick={() => setInspectedLog(null)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg cursor-pointer transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
