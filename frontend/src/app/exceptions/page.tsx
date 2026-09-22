"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import { StatCard } from "../../components/StatCard";
import { MultiSelectDropdown } from "../../components/MultiSelectDropdown";
import { AsyncExportModal } from "../../components/AsyncExportModal";
import { ExportActionToolbar } from "../../components/ExportActionToolbar";
import { api } from "../../lib/api";
import { MatchPair } from "../../types";
import { formatPercent, formatDate } from "../../lib/utils";
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ExternalLink,
  ShieldCheck,
  User,
  Scale,
  Search,
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  LayoutGrid,
  Table as TableIcon,
  Sparkles,
  X,
  FileSpreadsheet,
  FileJson,
  Activity,
  Layers,
  Download,
  Eye,
  FileText,
} from "lucide-react";

type SortField =
  | "county_name"
  | "case_number"
  | "party_name"
  | "party_type"
  | "similarity_score"
  | "filing_date";

export default function ExceptionReviewPage() {
  const [pendingMatches, setPendingMatches] = useState<MatchPair[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [isExporting, setIsExporting] = useState<string | null>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Match Inspection Modal State
  const [selectedMatch, setSelectedMatch] = useState<MatchPair | null>(null);
  const [reviewNotes, setReviewNotes] = useState("");
  const [reviewerName, setReviewerName] = useState("Claims Adjuster");

  const openInspection = (match: MatchPair) => {
    setSelectedMatch(match);
    setReviewNotes(match.review_notes || "");
    setReviewerName(match.reviewed_by || "Claims Adjuster");
  };

  const highlightMatchTokens = (text: string, query: string) => {
    if (!text || !query) return <span>{text || ""}</span>;
    const queryTokens = query
      .toLowerCase()
      .split(/\s+/)
      .map((t) => t.replace(/[^a-z0-9]/gi, ""))
      .filter((t) => t.length > 1);

    if (queryTokens.length === 0) return <span>{text}</span>;

    const words = text.split(/(\s+|[.,;/-]+)/);

    return (
      <span>
        {words.map((part, idx) => {
          const cleanPart = part.toLowerCase().replace(/[^a-z0-9]/gi, "");
          const isMatched =
            cleanPart.length > 1 &&
            queryTokens.some((qt) => cleanPart.includes(qt) || qt.includes(cleanPart));
          if (isMatched) {
            return (
              <mark
                key={idx}
                className="bg-amber-200 dark:bg-amber-900/60 text-amber-900 dark:text-amber-200 font-bold px-1 rounded-xs"
              >
                {part}
              </mark>
            );
          }
          return <span key={idx}>{part}</span>;
        })}
      </span>
    );
  };

  // View Mode: Table or Cards
  const [viewMode, setViewMode] = useState<"table" | "cards">("table");

  // Filtering State
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCounties, setSelectedCounties] = useState<string[]>([]);
  const [selectedPartyTypes, setSelectedPartyTypes] = useState<string[]>([]);
  const [selectedScoreTiers, setSelectedScoreTiers] = useState<string[]>([]);

  // Sorting State
  const [sortField, setSortField] = useState<SortField>("similarity_score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  const loadPending = async () => {
    setIsLoading(true);
    try {
      const data = await api.getPendingMatches(200);
      setPendingMatches(data || []);
    } catch (e) {
      console.error("Failed to load pending match reviews:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPending();
  }, []);

  const handleDecision = async (
    matchId: string,
    decision: "APPROVED" | "REJECTED",
    notes?: string,
    reviewer: string = "Claims Adjuster"
  ) => {
    setActionInProgress(matchId);
    setFeedback(null);
    try {
      await api.reviewMatchPair(matchId, decision, reviewer, notes);
      setFeedback({
        type: "success",
        msg: `Match pair successfully marked as ${
          decision === "APPROVED" ? "Approved" : "Rejected"
        }${notes ? " with adjuster notes" : ""}.`,
      });
      setPendingMatches((prev) => prev.filter((m) => m.id !== matchId));
      if (selectedMatch?.id === matchId) {
        setSelectedMatch(null);
        setReviewNotes("");
      }
    } catch (err) {
      setFeedback({ type: "error", msg: "Failed to update review decision." });
    } finally {
      setActionInProgress(null);
    }
  };

  // Distinct Counties for Filter
  const availableCounties = useMemo(() => {
    const set = new Set<string>();
    pendingMatches.forEach((m) => {
      if (m.county_name) set.add(m.county_name);
    });
    return Array.from(set).sort();
  }, [pendingMatches]);

  const countyOptions = useMemo(() => {
    return availableCounties.map((c) => ({
      value: c,
      label: c,
      count: pendingMatches.filter((m) => m.county_name === c).length,
    }));
  }, [availableCounties, pendingMatches]);

  const partyTypeOptions = [
    { value: "CLAIMANT", label: "Claimant" },
    { value: "INSURED", label: "Insured" },
    { value: "DRIVER", label: "Driver" },
  ];

  const scoreTierOptions = [
    { value: "HIGH", label: "High Confidence (≥60%)" },
    { value: "BORDERLINE", label: "Borderline (40% - 59%)" },
    { value: "LOW", label: "Low Confidence (<40%)" },
  ];

  // Filtering & Sorting Logic
  const filteredAndSortedMatches = useMemo(() => {
    let result = [...pendingMatches];

    // Search query
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase().trim();
      result = result.filter(
        (m) =>
          (m.case_number || "").toLowerCase().includes(q) ||
          (m.party_name || "").toLowerCase().includes(q) ||
          (m.case_style || "").toLowerCase().includes(q) ||
          (m.county_name || "").toLowerCase().includes(q)
      );
    }

    // County multi-select filter
    if (selectedCounties.length > 0) {
      result = result.filter((m) =>
        selectedCounties.includes(m.county_name || "")
      );
    }

    // Party type multi-select filter
    if (selectedPartyTypes.length > 0) {
      result = result.filter((m) =>
        selectedPartyTypes.includes((m.party_type || "").toUpperCase())
      );
    }

    // Score tiers multi-select filter
    if (selectedScoreTiers.length > 0) {
      result = result.filter((m) => {
        const score = (m.similarity_score || 0) * 100;
        return selectedScoreTiers.some((tier) => {
          if (tier === "HIGH") return score >= 60;
          if (tier === "BORDERLINE") return score >= 40 && score < 60;
          if (tier === "LOW") return score < 40;
          return false;
        });
      });
    }

    // Sorting
    result.sort((a, b) => {
      let valA: any = a[sortField] ?? "";
      let valB: any = b[sortField] ?? "";

      if (sortField === "similarity_score") {
        valA = Number(valA) || 0;
        valB = Number(valB) || 0;
      } else if (sortField === "filing_date") {
        valA = valA ? new Date(valA).getTime() : 0;
        valB = valB ? new Date(valB).getTime() : 0;
      } else {
        valA = String(valA).toLowerCase();
        valB = String(valB).toLowerCase();
      }

      if (valA < valB) return sortOrder === "asc" ? -1 : 1;
      if (valA > valB) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  }, [
    pendingMatches,
    searchTerm,
    selectedCounties,
    selectedPartyTypes,
    selectedScoreTiers,
    sortField,
    sortOrder,
  ]);

  // Metrics computation for StatCards
  const metrics = useMemo(() => {
    let high = 0;
    let borderline = 0;
    let low = 0;
    pendingMatches.forEach((m) => {
      const score = (m.similarity_score || 0) * 100;
      if (score >= 60) high++;
      else if (score >= 40) borderline++;
      else low++;
    });
    return {
      total: pendingMatches.length,
      high,
      borderline,
      low,
    };
  }, [pendingMatches]);

  // Pagination Slicing
  const totalFilteredCount = filteredAndSortedMatches.length;
  const totalPages = Math.max(1, Math.ceil(totalFilteredCount / pageSize));
  const paginatedMatches = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSortedMatches.slice(start, start + pageSize);
  }, [filteredAndSortedMatches, currentPage, pageSize]);

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
    setCurrentPage(1);
  };

  const renderSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3 h-3 text-slate-400 opacity-60 ml-1 inline" />;
    }
    return sortOrder === "asc" ? (
      <ArrowUp className="w-3 h-3 text-indigo-500 ml-1 inline" />
    ) : (
      <ArrowDown className="w-3 h-3 text-indigo-500 ml-1 inline" />
    );
  };

  const clearFilters = () => {
    setSearchTerm("");
    setSelectedCounties([]);
    setSelectedPartyTypes([]);
    setSelectedScoreTiers([]);
    setCurrentPage(1);
  };

  const hasActiveFilters =
    searchTerm !== "" ||
    selectedCounties.length > 0 ||
    selectedPartyTypes.length > 0 ||
    selectedScoreTiers.length > 0;

  // Export handlers
  const handleExport = async (format: "csv" | "json" | "xlsx") => {
    setIsExporting(format);
    const timestamp = new Date().toISOString().slice(0, 10);
    try {
      const blob = await api.exportMatches({ format });
      downloadBlob(blob, `fuzzy_exceptions_${timestamp}.${format}`);
      setFeedback({
        type: "success",
        msg: `Successfully exported fuzzy match exceptions as ${format.toUpperCase()}.`,
      });
    } catch (err) {
      console.warn("Backend export failed, falling back to client-side generation:", err);
      if (format === "json") {
        const blob = new Blob([JSON.stringify(filteredAndSortedMatches, null, 2)], {
          type: "application/json",
        });
        downloadBlob(blob, `fuzzy_exceptions_${timestamp}.json`);
      } else {
        const headers = [
          "ID",
          "County",
          "Case Number",
          "Case Style",
          "Party Type",
          "Party Name",
          "Similarity Score",
          "Threshold Applied",
          "Filing Date",
          "Review Status",
        ];
        const rows = filteredAndSortedMatches.map((m) => [
          m.id,
          m.county_name || "",
          m.case_number || "",
          `"${(m.case_style || "").replace(/"/g, '""')}"`,
          m.party_type || "",
          `"${(m.party_name || "").replace(/"/g, '""')}"`,
          ((m.similarity_score || 0) * 100).toFixed(1) + "%",
          ((m.threshold_applied || 0) * 100).toFixed(1) + "%",
          m.filing_date || "",
          m.review_status || "PENDING",
        ]);

        const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
        const blob = new Blob([csvContent], {
          type: format === "xlsx" ? "application/vnd.ms-excel;charset=utf-8;" : "text/csv;charset=utf-8;",
        });
        downloadBlob(blob, `fuzzy_exceptions_${timestamp}.${format}`);
      }
    } finally {
      setIsExporting(null);
    }
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden">
      <Navbar onRefresh={loadPending} isRefreshing={isLoading} />

      <main className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors">
        {/* Title Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-purple-500" />
                Fuzzy Match Exception Review
              </h2>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-purple-50 dark:bg-purple-950/80 text-purple-600 dark:text-purple-400 border border-purple-200 dark:border-purple-800">
                Adjuster Resolution
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Review and manually resolve candidate match pairs with borderline confidence scores.
            </p>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
            {/* View Mode Toggle */}
            <div className="flex items-center bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5">
              <button
                onClick={() => setViewMode("table")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                  viewMode === "table"
                    ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs"
                    : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                }`}
              >
                <TableIcon className="w-3.5 h-3.5" />
                Table
              </button>
              <button
                onClick={() => setViewMode("cards")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                  viewMode === "cards"
                    ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs"
                    : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                }`}
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                Cards
              </button>
            </div>

            {/* Reusable Universal Export Toolbar */}
            <ExportActionToolbar
              label="Export"
              onExport={(fmt) => handleExport(fmt as any)}
              onOpenAsyncModal={() => setIsExportModalOpen(true)}
              isExporting={Boolean(isExporting)}
              showPdf={false}
              showAsyncButton={true}
              compact={true}
            />

            <div className="text-xs text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800/60 px-3 py-1.5 rounded-lg font-medium shadow-xs w-fit">
              {pendingMatches.length} Items Awaiting Review
            </div>
          </div>
        </div>

        {/* Feedback Alert */}
        {feedback && (
          <div
            className={`w-full max-w-full overflow-hidden p-3.5 rounded-xl border text-xs flex items-center justify-between gap-2 shadow-xs ${
              feedback.type === "success"
                ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300"
                : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/60 text-rose-800 dark:text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {feedback.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
              )}
              <span className="min-w-0 break-words flex-1">{feedback.msg}</span>
            </div>
            <button
              onClick={() => setFeedback(null)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 shrink-0 p-1 cursor-pointer transition-colors"
              title="Dismiss"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Metric StatCards Strip (matching Dashboard design language & clickable) */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
          <StatCard
            label="Total Pending"
            value={metrics.total}
            subtext="Needs review"
            icon={Layers}
            gradient="purple"
            selected={!hasActiveFilters}
            onClick={clearFilters}
          />

          <StatCard
            label="High Confidence"
            value={metrics.high}
            subtext="Score ≥ 60%"
            icon={CheckCircle2}
            gradient="emerald"
            selected={selectedScoreTiers.includes("HIGH") && selectedScoreTiers.length === 1}
            onClick={() => {
              setSelectedScoreTiers((prev) =>
                prev.length === 1 && prev[0] === "HIGH" ? [] : ["HIGH"]
              );
              setCurrentPage(1);
            }}
          />

          <StatCard
            label="Borderline"
            value={metrics.borderline}
            subtext="Score 40% - 59%"
            icon={AlertTriangle}
            gradient="amber"
            selected={selectedScoreTiers.includes("BORDERLINE") && selectedScoreTiers.length === 1}
            onClick={() => {
              setSelectedScoreTiers((prev) =>
                prev.length === 1 && prev[0] === "BORDERLINE" ? [] : ["BORDERLINE"]
              );
              setCurrentPage(1);
            }}
          />

          <StatCard
            label="Low Confidence"
            value={metrics.low}
            subtext="Score < 40%"
            icon={XCircle}
            gradient="rose"
            selected={selectedScoreTiers.includes("LOW") && selectedScoreTiers.length === 1}
            onClick={() => {
              setSelectedScoreTiers((prev) =>
                prev.length === 1 && prev[0] === "LOW" ? [] : ["LOW"]
              );
              setCurrentPage(1);
            }}
          />
        </div>

        {/* Filter Controls with Universal MultiSelectDropdowns */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs space-y-3">
          <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search case #, party name, case style, or county..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-9 pr-8 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden focus:border-purple-500 transition-colors"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm("")}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* County Multi-Select */}
            <div className="w-full sm:w-56">
              <MultiSelectDropdown
                label="Counties"
                options={countyOptions}
                selectedValues={selectedCounties}
                onChange={(values) => {
                  setSelectedCounties(values);
                  setCurrentPage(1);
                }}
                placeholder="All Counties"
              />
            </div>

            {/* Party Type Multi-Select */}
            <div className="w-full sm:w-48">
              <MultiSelectDropdown
                label="Party Types"
                options={partyTypeOptions}
                selectedValues={selectedPartyTypes}
                onChange={(values) => {
                  setSelectedPartyTypes(values);
                  setCurrentPage(1);
                }}
                placeholder="All Parties"
              />
            </div>

            {/* Score Tier Multi-Select */}
            <div className="w-full sm:w-52">
              <MultiSelectDropdown
                label="Score Tiers"
                options={scoreTierOptions}
                selectedValues={selectedScoreTiers}
                onChange={(values) => {
                  setSelectedScoreTiers(values);
                  setCurrentPage(1);
                }}
                placeholder="All Score Ranges"
              />
            </div>

            {/* Clear Filters Button */}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 px-3 py-2 text-xs font-semibold text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30 rounded-lg transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3 h-3" />
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Content View: Table or Cards */}
        <div className="space-y-4">
          {viewMode === "table" ? (
            /* Table View */
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xs overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                      <th
                        onClick={() => toggleSort("county_name")}
                        className="py-3 px-4 cursor-pointer hover:text-purple-600 transition-colors select-none"
                      >
                        County / Portal {renderSortIcon("county_name")}
                      </th>
                      <th
                        onClick={() => toggleSort("party_name")}
                        className="py-3 px-4 cursor-pointer hover:text-purple-600 transition-colors select-none"
                      >
                        Party Evaluated {renderSortIcon("party_name")}
                      </th>
                      <th
                        onClick={() => toggleSort("party_type")}
                        className="py-3 px-4 cursor-pointer hover:text-purple-600 transition-colors select-none"
                      >
                        Role {renderSortIcon("party_type")}
                      </th>
                      <th
                        onClick={() => toggleSort("case_number")}
                        className="py-3 px-4 cursor-pointer hover:text-purple-600 transition-colors select-none"
                      >
                        Scraped Case Style / No. {renderSortIcon("case_number")}
                      </th>
                      <th
                        onClick={() => toggleSort("similarity_score")}
                        className="py-3 px-4 cursor-pointer hover:text-purple-600 transition-colors select-none"
                      >
                        Confidence {renderSortIcon("similarity_score")}
                      </th>
                      <th
                        onClick={() => toggleSort("filing_date")}
                        className="py-3 px-4 cursor-pointer hover:text-purple-600 transition-colors select-none"
                      >
                        Filing Date {renderSortIcon("filing_date")}
                      </th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-850">
                    {isLoading ? (
                      <tr>
                        <td colSpan={7} className="py-12 text-center text-slate-400">
                          Loading pending exceptions...
                        </td>
                      </tr>
                    ) : paginatedMatches.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="py-12 text-center text-slate-400">
                          {hasActiveFilters
                            ? "No exception reviews match your filters."
                            : "No pending exceptions. All candidate match pairs are resolved!"}
                        </td>
                      </tr>
                    ) : (
                      paginatedMatches.map((match) => {
                        const score = (match.similarity_score || 0) * 100;
                        const isHigh = score >= 60;
                        const isBorderline = score >= 40 && score < 60;
                        return (
                          <tr
                            key={match.id}
                            onClick={() => openInspection(match)}
                            className="hover:bg-slate-50/90 dark:hover:bg-slate-800/60 transition-colors cursor-pointer group"
                            title="Click to inspect full claim and court case details"
                          >
                            <td className="py-3 px-4 whitespace-nowrap">
                              <span className="font-semibold text-slate-800 dark:text-slate-200">
                                {match.county_name || "Unknown"}
                              </span>
                            </td>
                            <td className="py-3 px-4 whitespace-nowrap">
                              <div className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                                <span>{match.party_name}</span>
                                <span className="opacity-0 group-hover:opacity-100 transition-opacity text-indigo-500">
                                  <Eye className="w-3.5 h-3.5" />
                                </span>
                              </div>
                            </td>
                            <td className="py-3 px-4 whitespace-nowrap">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                                {match.party_type}
                              </span>
                            </td>
                            <td className="py-3 px-4 max-w-xs md:max-w-md">
                              <div className="font-mono text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                                {match.case_number}
                              </div>
                              <p className="text-slate-500 dark:text-slate-400 text-xs truncate" title={match.case_style}>
                                {match.case_style}
                              </p>
                            </td>
                            <td className="py-3 px-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <div className="w-16 bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                                  <div
                                    className={`h-full rounded-full ${
                                      isHigh
                                        ? "bg-emerald-500"
                                        : isBorderline
                                        ? "bg-amber-500"
                                        : "bg-rose-500"
                                    }`}
                                    style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
                                  />
                                </div>
                                <span
                                  className={`font-mono font-bold text-xs ${
                                    isHigh
                                      ? "text-emerald-600 dark:text-emerald-400"
                                      : isBorderline
                                      ? "text-amber-600 dark:text-amber-400"
                                      : "text-rose-600 dark:text-rose-400"
                                  }`}
                                >
                                  {score.toFixed(1)}%
                                </span>
                              </div>
                            </td>
                            <td className="py-3 px-4 whitespace-nowrap font-mono text-slate-600 dark:text-slate-400">
                              {match.filing_date || "N/A"}
                            </td>
                            <td className="py-3 px-4 whitespace-nowrap text-right" onClick={(e) => e.stopPropagation()}>
                              <div className="flex items-center justify-end gap-1.5">
                                <button
                                  onClick={() => openInspection(match)}
                                  className="px-2.5 py-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 rounded-md transition-colors cursor-pointer flex items-center gap-1 border border-indigo-200 dark:border-indigo-800/50"
                                  title="Inspect full match evidence, claim details, and adjuster resolution notes"
                                >
                                  <Eye className="w-3.5 h-3.5" />
                                  <span>Inspect</span>
                                </button>
                                <button
                                  onClick={() => handleDecision(match.id, "REJECTED")}
                                  disabled={actionInProgress === match.id}
                                  className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-md transition-colors cursor-pointer disabled:opacity-50"
                                >
                                  Reject
                                </button>
                                <button
                                  onClick={() => handleDecision(match.id, "APPROVED")}
                                  disabled={actionInProgress === match.id}
                                  className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-md shadow-2xs transition-all cursor-pointer disabled:opacity-50"
                                >
                                  Approve
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            /* Cards View */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {isLoading ? (
                <div className="col-span-2 py-12 text-center text-slate-400">
                  Loading pending exceptions...
                </div>
              ) : paginatedMatches.length === 0 ? (
                <div className="col-span-2 py-12 text-center text-slate-400">
                  {hasActiveFilters
                    ? "No exception reviews match your filters."
                    : "No pending exceptions. All candidate match pairs are resolved!"}
                </div>
              ) : (
                paginatedMatches.map((match) => {
                  const score = (match.similarity_score || 0) * 100;
                  const isHigh = score >= 60;
                  const isBorderline = score >= 40 && score < 60;
                  return (
                    <div
                      key={match.id}
                      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4"
                    >
                      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                        <div>
                          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                            {match.county_name || "Unknown County"}
                          </span>
                          <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 font-mono">
                            {match.case_number}
                          </h4>
                        </div>
                        <div className="text-right">
                          <span
                            className={`font-mono text-sm font-bold ${
                              isHigh
                                ? "text-emerald-600 dark:text-emerald-400"
                                : isBorderline
                                ? "text-amber-600 dark:text-amber-400"
                                : "text-rose-600 dark:text-rose-400"
                            }`}
                          >
                            {score.toFixed(1)}% Match
                          </span>
                          <span className="block text-[10px] text-slate-400">
                            Threshold: {((match.threshold_applied || 0) * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>

                      <div className="space-y-2 text-xs">
                        <div>
                          <span className="text-slate-400 block text-[10px] uppercase font-bold">Party Evaluated</span>
                          <span className="font-semibold text-slate-800 dark:text-slate-200">
                            {match.party_name} ({match.party_type})
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px] uppercase font-bold">Case Style</span>
                          <p className="text-slate-600 dark:text-slate-300 line-clamp-2">
                            {match.case_style}
                          </p>
                        </div>
                        {match.filing_date && (
                          <div>
                            <span className="text-slate-400 block text-[10px] uppercase font-bold">Filing Date</span>
                            <span className="font-mono text-slate-700 dark:text-slate-300">
                              {match.filing_date}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                        <button
                          onClick={() => openInspection(match)}
                          className="px-3 py-1.5 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 rounded-lg transition-colors cursor-pointer flex items-center gap-1.5 border border-indigo-200 dark:border-indigo-800/50"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Inspect Details</span>
                        </button>
                        <div className="flex items-center gap-1.5">
                          <button
                            onClick={() => handleDecision(match.id, "REJECTED")}
                            disabled={actionInProgress === match.id}
                            className="px-3 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleDecision(match.id, "APPROVED")}
                            disabled={actionInProgress === match.id}
                            className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-2xs transition-all cursor-pointer disabled:opacity-50"
                          >
                            Approve Match
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* Pagination Controls */}
          {pendingMatches.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs text-slate-500 dark:text-slate-400">
              <div className="flex items-center gap-2">
                <span>Rows per page:</span>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
                    setCurrentPage(1);
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
                  Showing {totalFilteredCount === 0 ? 0 : (currentPage - 1) * pageSize + 1} to{" "}
                  {Math.min(currentPage * pageSize, totalFilteredCount)} of {totalFilteredCount} exceptions
                </span>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <span className="px-2.5 py-1 font-mono text-xs font-semibold text-slate-800 dark:text-slate-200">
                  Page {currentPage} of {totalPages}
                </span>

                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                  aria-label="Next page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Reusable High-Volume Background Dataset Export Modal */}
        <AsyncExportModal
          isOpen={isExportModalOpen}
          onClose={() => setIsExportModalOpen(false)}
          searchTerm={searchTerm}
          totalRecordsCount={totalFilteredCount}
        />

        {/* Candidate Match Inspection & Adjuster Resolution Modal */}
        {selectedMatch && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200"
            onClick={() => setSelectedMatch(null)}
          >
            <div
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden text-slate-900 dark:text-slate-100"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-purple-100 dark:bg-purple-950/50 text-purple-600 dark:text-purple-400">
                    <Scale className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                        Candidate Match Inspection & Resolution
                      </h3>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300">
                        {selectedMatch.county_name || "Court Portal"}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                      Match Evaluation ID: {selectedMatch.id}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {/* Similarity Badge */}
                  <div className="text-right">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-slate-500">Confidence:</span>
                      <span
                        className={`font-mono text-sm font-black px-2 py-0.5 rounded-md ${
                          (selectedMatch.similarity_score || 0) >= 0.6
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400"
                            : (selectedMatch.similarity_score || 0) >= 0.4
                            ? "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400"
                            : "bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400"
                        }`}
                      >
                        {((selectedMatch.similarity_score || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-400">
                      Threshold: {((selectedMatch.threshold_applied || 0.6) * 100).toFixed(0)}%
                    </span>
                  </div>

                  <button
                    onClick={() => setSelectedMatch(null)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                    aria-label="Close modal"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Modal Body */}
              <div className="p-6 overflow-y-auto space-y-6">
                {/* Side-by-Side Dual Pane Comparison Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Left Pane: Insurance Claim Master */}
                  <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-indigo-500" />
                        Insurance Claim Master
                      </span>
                      {selectedMatch.claim_id && (
                        <Link
                          href={`/claims/${selectedMatch.claim_id}`}
                          target="_blank"
                          className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                        >
                          View Claim <ExternalLink className="w-3 h-3" />
                        </Link>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Claim Number</span>
                        <span className="font-mono font-bold text-slate-900 dark:text-slate-100">
                          {selectedMatch.claim_number || selectedMatch.claim_id?.substring(0, 8) || "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Exposure #</span>
                        <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">
                          {selectedMatch.exposure_number || "001"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Date of Loss (DOL)</span>
                        <span className="font-mono text-slate-700 dark:text-slate-300">
                          {selectedMatch.dol || "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Jurisdiction</span>
                        <span className="text-slate-700 dark:text-slate-300">
                          Policy: <strong className="font-mono">{selectedMatch.policy_state || "FL"}</strong> | Loss:{" "}
                          <strong className="font-mono">{selectedMatch.loss_location_state || "FL"}</strong>
                        </span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-200 dark:border-slate-800/80 space-y-1.5 text-xs">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Claim Parties</span>
                      <div className="flex items-center justify-between p-1.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800">
                        <span className="text-slate-500 text-[11px]">Insured:</span>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          {selectedMatch.insured_name || "N/A"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-1.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800">
                        <span className="text-slate-500 text-[11px]">Claimant:</span>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          {selectedMatch.claimant_name || "N/A"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-1.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800">
                        <span className="text-slate-500 text-[11px]">Driver:</span>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          {selectedMatch.driver_name || "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Right Pane: Discovered Public Court Docket */}
                  <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                        <Scale className="w-3.5 h-3.5 text-purple-500" />
                        Discovered Court Docket
                      </span>
                      {selectedMatch.county_website ? (
                        <a
                          href={selectedMatch.county_website}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] font-semibold text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1"
                        >
                          Court Portal <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-[10px] text-slate-400">Portal Online</span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Docket / Case #</span>
                        <span className="font-mono font-bold text-purple-600 dark:text-purple-400">
                          {selectedMatch.case_number || "Unknown"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Filing Date</span>
                        <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                          {selectedMatch.filing_date || "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Case Status</span>
                        <span className="font-semibold text-slate-700 dark:text-slate-300">
                          {selectedMatch.case_status || "Active / Open"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Case Type</span>
                        <span className="text-slate-700 dark:text-slate-300 truncate block" title={selectedMatch.case_type || "N/A"}>
                          {selectedMatch.case_type || "Civil / Auto Negligence"}
                        </span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-200 dark:border-slate-800/80 space-y-1 text-xs">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Full Case Style</span>
                      <p className="p-2.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 text-slate-800 dark:text-slate-200 font-medium text-xs leading-relaxed max-h-24 overflow-y-auto">
                        {selectedMatch.case_style}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Matching Engine Evidence & Token Highlight Box */}
                <div className="p-4 rounded-xl bg-purple-50/50 dark:bg-purple-950/20 border border-purple-200/60 dark:border-purple-800/50 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-purple-800 dark:text-purple-300 flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                      Matching Engine Evidence & Token Overlap
                    </span>
                    <span className="text-[11px] font-mono text-purple-700 dark:text-purple-400">
                      Algorithm: RapidFuzz partial_ratio
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                    <div className="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-purple-100 dark:border-purple-900/40">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Party Evaluated</span>
                      <span className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                        {selectedMatch.party_name}
                      </span>
                      <span className="block text-[10px] text-purple-600 dark:text-purple-400 font-semibold mt-0.5">
                        Role: {selectedMatch.party_type}
                      </span>
                    </div>

                    <div className="md:col-span-2 p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-purple-100 dark:border-purple-900/40">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">
                        Token Overlap in Docket Case Style
                      </span>
                      <div className="text-xs text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">
                        {highlightMatchTokens(selectedMatch.case_style, selectedMatch.party_name)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-purple-100 dark:border-purple-900/40 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="text-slate-500 dark:text-slate-400">Match Classification:</span>
                      {(selectedMatch.similarity_score || 0) >= 0.6 ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                          Strong Match (≥60%) — Recommended for Guidewire Sync
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                          Borderline Match (40%–59%) — Adjuster Discretion Required
                        </span>
                      )}
                    </div>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                      Filing Date Filter: Compliant (&gt;= 2010)
                    </span>
                  </div>
                </div>

                {/* Adjuster Resolution & Justification Notes Box */}
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-indigo-500" />
                      Adjuster Legal Justification & Decision Notes
                    </label>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">Reviewer:</span>
                      <input
                        type="text"
                        value={reviewerName}
                        onChange={(e) => setReviewerName(e.target.value)}
                        className="text-xs px-2.5 py-1 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 font-medium"
                        placeholder="Claims Adjuster"
                      />
                    </div>
                  </div>

                  <textarea
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    rows={3}
                    className="w-full text-xs p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-purple-500 placeholder:text-slate-400"
                    placeholder="Enter adjuster justification, DOB/VIN cross-check observations, or reasons for approval/rejection (saved to Audit Log & Guidewire payload)..."
                  />
                </div>
              </div>

              {/* Modal Footer Actions */}
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50">
                <button
                  onClick={() => setSelectedMatch(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                >
                  Cancel & Close
                </button>

                <div className="flex items-center gap-2.5">
                  <button
                    onClick={() => handleDecision(selectedMatch.id, "REJECTED", reviewNotes, reviewerName)}
                    disabled={actionInProgress === selectedMatch.id}
                    className="px-4 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 rounded-lg transition-colors cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Reject Match</span>
                  </button>

                  <button
                    onClick={() => handleDecision(selectedMatch.id, "APPROVED", reviewNotes, reviewerName)}
                    disabled={actionInProgress === selectedMatch.id}
                    className="px-5 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-sm transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve Match & Sync Guidewire</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
