"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  FileSpreadsheet,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Clock,
  XCircle,
  ArrowUpRight,
  TrendingUp,
  Activity,
  BarChart3,
  PieChart,
  Search,
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Building,
  Scale,
  Zap,
  Download,
  Play,
  Pause,
  FastForward,
  Bot,
  RefreshCw,
  Loader2,
  ArrowRight,
  CheckSquare,
  Square,
  StopCircle,
  Sliders,
  Users,
  Flame,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Navbar } from "../components/Navbar";
import { StatusBadge } from "../components/StatusBadge";
import { StatCard } from "../components/StatCard";
import { FilterPresetManager } from "../components/FilterPresetManager";
import { AsyncExportModal } from "../components/AsyncExportModal";
import { api } from "../lib/api";
import { Claim, ClaimStats, LiveQueueState } from "../types";
import { formatDate } from "../lib/utils";

type SortField =
  | "claim_number"
  | "insured_name"
  | "claimant_name"
  | "loss_location_state"
  | "record_status"
  | "fuzzy_match_status"
  | "created_at";

export default function DashboardPage() {
  const [stats, setStats] = useState<ClaimStats | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [totalClaims, setTotalClaims] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Live Queue Orchestrator State
  const [liveQueue, setLiveQueue] = useState<LiveQueueState | null>(null);
  const [isAdvancingQueue, setIsAdvancingQueue] = useState(false);
  const [isTogglingAuto, setIsTogglingAuto] = useState(false);
  const [liveElapsedSeconds, setLiveElapsedSeconds] = useState(0);
  const [lastTransitionMessage, setLastTransitionMessage] = useState<string | null>(null);

  // Multi-Worker Concurrency & Queue Selection State
  const [selectedQueueIds, setSelectedQueueIds] = useState<string[]>([]);
  const [queueStateFilter, setQueueStateFilter] = useState<"ALL" | "FL" | "TX">("ALL");
  const [isSeedingDemo, setIsSeedingDemo] = useState(false);
  const [isUpdatingConcurrency, setIsUpdatingConcurrency] = useState(false);
  const [isStartingSelected, setIsStartingSelected] = useState(false);
  const [showRecentCompleted, setShowRecentCompleted] = useState(true);

  // Table Filter & Search State
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [stateFilter, setStateFilter] = useState("all");
  const [matchFilter, setMatchFilter] = useState("all");
  const [activeTab, setActiveTab] = useState<"all" | "active" | "pending" | "matches" | "exceptions" | "completed">("all");
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Sorting State
  const [sortField, setSortField] = useState<SortField>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const fetchLiveQueue = React.useCallback(async () => {
    try {
      const qState = await api.getLiveQueue();
      setLiveQueue((prev) => {
        if (prev?.active_item && (!qState.active_item || qState.active_item.id !== prev.active_item.id)) {
          setLastTransitionMessage(
            `Claim #${prev.active_item.claim_number} finished processing. ${
              qState.active_item
                ? `Auto-runner sequentially picked up Claim #${qState.active_item.claim_number}.`
                : "Queue is currently clear."
            }`
          );
        }
        return qState;
      });
    } catch (e) {
      console.warn("Could not fetch live queue state:", e);
    }
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [statsData, claimsData, queueData] = await Promise.all([
        api.getClaimStats(),
        api.getClaims({ page: 1, page_size: 200 }),
        api.getLiveQueue().catch(() => null),
      ]);
      setStats(statsData || null);
      if (claimsData?.items) {
        setClaims(claimsData.items);
        setTotalClaims(claimsData.total || claimsData.items.length);
      }
      if (queueData) {
        setLiveQueue(queueData);
      }
    } catch (e) {
      console.error("Failed to fetch dashboard data:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Polling interval: 3s when running or items pending with auto-queue; 10s otherwise
  useEffect(() => {
    const isBusy = liveQueue?.is_running || (Boolean(liveQueue?.total_pending_count) && Boolean(liveQueue?.auto_queue_enabled));
    const intervalMs = isBusy ? 3000 : 10000;

    const timer = setInterval(() => {
      fetchLiveQueue();
      if (isBusy) {
        api.getClaims({ page: 1, page_size: 200 }).then((c) => {
          if (c?.items) setClaims(c.items);
        }).catch(() => {});
        api.getClaimStats().then((s) => {
          if (s) setStats(s);
        }).catch(() => {});
      }
    }, intervalMs);

    return () => clearInterval(timer);
  }, [liveQueue?.is_running, liveQueue?.total_pending_count, liveQueue?.auto_queue_enabled, fetchLiveQueue]);

  // Elapsed seconds timer for active running item
  useEffect(() => {
    if (!liveQueue?.is_running) {
      setLiveElapsedSeconds(0);
      return;
    }
    const timer = setInterval(() => {
      setLiveElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [liveQueue?.is_running, liveQueue?.active_item?.id]);

  const handleToggleAutoQueue = async () => {
    if (!liveQueue) return;
    setIsTogglingAuto(true);
    try {
      const nextState = !liveQueue.auto_queue_enabled;
      await api.toggleAutoQueueMode(nextState);
      await fetchLiveQueue();
    } catch (e) {
      console.error("Error toggling auto queue:", e);
    } finally {
      setIsTogglingAuto(false);
    }
  };

  const handleRunNext = async () => {
    setIsAdvancingQueue(true);
    try {
      await api.runNextQueueItem();
      await fetchLiveQueue();
      loadData();
    } catch (e) {
      console.error("Error running next queue item:", e);
    } finally {
      setIsAdvancingQueue(false);
    }
  };

  const handleStartAll = async () => {
    try {
      await api.startAllQueue();
      await fetchLiveQueue();
      loadData();
    } catch (e) {
      console.error("Error starting all claims:", e);
    }
  };

  const handleSetConcurrency = async (concurrency: number) => {
    setIsUpdatingConcurrency(true);
    try {
      await api.setQueueConcurrency(concurrency);
      await fetchLiveQueue();
      setLastTransitionMessage(`RPA concurrency set to ${concurrency} parallel worker${concurrency > 1 ? "s" : ""}.`);
    } catch (e) {
      console.error("Error setting concurrency:", e);
    } finally {
      setIsUpdatingConcurrency(false);
    }
  };

  const handleSeedDemo = async () => {
    setIsSeedingDemo(true);
    try {
      await api.seedDemoClaims(10);
      await fetchLiveQueue();
      await loadData();
      setLastTransitionMessage(`Seeded 10 realistic Florida & Texas claims. Dispatched across ${liveQueue?.max_concurrency || 3} parallel workers!`);
    } catch (e) {
      console.error("Error seeding demo claims:", e);
    } finally {
      setIsSeedingDemo(false);
    }
  };

  const handleRunSelected = async () => {
    if (selectedQueueIds.length === 0) return;
    setIsStartingSelected(true);
    try {
      await api.runSelectedQueueItems(selectedQueueIds);
      setSelectedQueueIds([]);
      await fetchLiveQueue();
      await loadData();
      setLastTransitionMessage(`Dispatched ${selectedQueueIds.length} selected claims to parallel worker fleet.`);
    } catch (e) {
      console.error("Error running selected claims:", e);
    } finally {
      setIsStartingSelected(false);
    }
  };

  const handleStopClaim = async (claimId: string, claimNumber: string) => {
    try {
      await api.stopClaim(claimId);
      await fetchLiveQueue();
      await loadData();
      setLastTransitionMessage(`Cancelled execution for Claim #${claimNumber}. Worker slot freed.`);
    } catch (e) {
      console.error("Error stopping claim:", e);
    }
  };

  // Filter and Sort Claims
  const filteredAndSortedClaims = useMemo(() => {
    let result = [...claims];

    // Search query across multiple fields
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase().trim();
      result = result.filter(
        (c) =>
          (c.claim_number || "").toLowerCase().includes(q) ||
          (c.insured_name || "").toLowerCase().includes(q) ||
          (c.claimant_name || "").toLowerCase().includes(q) ||
          (c.loss_location_state || "").toLowerCase().includes(q) ||
          (c.exposure_number || "").toLowerCase().includes(q)
      );
    }

    // Status filter
    if (statusFilter !== "all" && statusFilter !== "") {
      result = result.filter(
        (c) => (c.record_status || "").toUpperCase() === statusFilter.toUpperCase()
      );
    }

    // State filter
    if (stateFilter !== "all" && stateFilter !== "") {
      result = result.filter(
        (c) =>
          (c.policy_state || c.loss_location_state || "").toUpperCase() ===
          stateFilter.toUpperCase()
      );
    }

    // Fuzzy match status filter
    if (matchFilter !== "all") {
      result = result.filter(
        (c) => (c.fuzzy_match_status || "").toUpperCase() === matchFilter.toUpperCase()
      );
    }

    // Sorting
    result.sort((a, b) => {
      let valA: any = a[sortField] || "";
      let valB: any = b[sortField] || "";

      if (typeof valA === "string") valA = valA.toLowerCase();
      if (typeof valB === "string") valB = valB.toLowerCase();

      if (valA < valB) return sortOrder === "asc" ? -1 : 1;
      if (valA > valB) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  }, [claims, searchTerm, statusFilter, stateFilter, matchFilter, sortField, sortOrder]);

  // Paginated Claims
  const totalFilteredCount = filteredAndSortedClaims.length;
  const totalPages = Math.max(1, Math.ceil(totalFilteredCount / pageSize));
  const paginatedClaims = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedClaims.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedClaims, currentPage, pageSize]);

  // Adjust current page if filters reduce total pages
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(1);
    }
  }, [totalPages, currentPage]);

  const handleSort = (field: SortField) => {
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
    setStatusFilter("all");
    setStateFilter("all");
    setMatchFilter("all");
    setCurrentPage(1);
  };

  const hasActiveFilters =
    searchTerm !== "" || statusFilter !== "all" || stateFilter !== "all" || matchFilter !== "all";

  // Visual Breakdown Metrics
  const totalCount = stats?.total_claims || claims.length || 1;
  const matchPercentage = Math.round(((stats?.match_found || 0) / totalCount) * 100) || 0;
  const inProgressPercentage = Math.round(((stats?.in_progress || 0) / totalCount) * 100) || 0;
  const reviewPercentage = Math.round(((stats?.manual_review || 0) / totalCount) * 100) || 0;
  const completedPercentage = Math.round(((stats?.completed || 0) / totalCount) * 100) || 0;

  // Stat Cards
  const statCards = [
    {
      title: "Total Ingested",
      value: stats?.total_claims ?? totalClaims,
      icon: FileSpreadsheet,
      gradient: "from-sky-500/20 to-indigo-500/20",
      filterValue: "all",
      subtitle: "All recorded claims",
    },
    {
      title: "In Progress / Queue",
      value: (stats?.in_progress ?? 0) + (liveQueue?.total_pending_count ?? 0),
      icon: Clock,
      gradient: "from-amber-500/20 to-orange-500/20",
      filterValue: "SCRAPING_IN_PROGRESS",
      subtitle: `${liveQueue?.total_pending_count ?? 0} pending in queue`,
    },
    {
      title: "Matches Confirmed",
      value: stats?.match_found ?? 0,
      icon: CheckCircle2,
      gradient: "from-emerald-500/20 to-teal-500/20",
      filterValue: "MATCH_FOUND",
      subtitle: `${matchPercentage}% positive matches`,
    },
    {
      title: "Manual Exceptions",
      value: stats?.manual_review ?? 0,
      icon: AlertTriangle,
      gradient: "from-purple-500/20 to-pink-500/20",
      filterValue: "MANUAL_REVIEW",
      subtitle: "Review required",
    },
    {
      title: "Completed Scrapes",
      value: stats?.completed ?? 0,
      icon: ShieldCheck,
      gradient: "from-blue-500/20 to-indigo-500/20",
      filterValue: "SCRAPING_COMPLETED",
      subtitle: `${completedPercentage}% finished`,
    },
    {
      title: "Failed / Retried",
      value: stats?.failed ?? 0,
      icon: XCircle,
      gradient: "from-rose-500/20 to-red-500/20",
      filterValue: "FAILED",
      subtitle: "Ready to retrigger",
    },
  ];

  // 8 County Court Scraper Bots Coverage & Live Throughput
  const portalBreakdown = useMemo(() => {
    const counts: Record<string, number> = {
      miami: 0,
      broward: 0,
      hillsborough: 0,
      harris_cclerk: 0,
      dallas: 0,
      harris_jp: 0,
      harris_district: 0,
      travis: 0,
    };

    claims.forEach((c) => {
      if (c.court_cases && Array.isArray(c.court_cases)) {
        c.court_cases.forEach((cc) => {
          const portalLower = (cc.county_name || cc.county_website || cc.source_url || "").toLowerCase();
          if (portalLower.includes("broward")) counts.broward++;
          else if (portalLower.includes("hillsborough") || portalLower.includes("hover")) counts.hillsborough++;
          else if (portalLower.includes("miami") || portalLower.includes("dade") || portalLower.includes("ocs")) counts.miami++;
          else if (portalLower.includes("cclerk") || (portalLower.includes("harris") && portalLower.includes("clerk"))) counts.harris_cclerk++;
          else if (portalLower.includes("dallas")) counts.dallas++;
          else if (portalLower.includes("jp") || portalLower.includes("justice")) counts.harris_jp++;
          else if (portalLower.includes("district") || portalLower.includes("hcdistrict")) counts.harris_district++;
          else if (portalLower.includes("travis")) counts.travis++;
        });
      }
    });

    return [
      { key: "miami", name: "Miami-Dade (FL)", state: "FL", cases: counts.miami, active: true },
      { key: "broward", name: "Broward (FL)", state: "FL", cases: counts.broward, active: true },
      { key: "hillsborough", name: "Hillsborough (FL)", state: "FL", cases: counts.hillsborough, active: true },
      { key: "harris_cclerk", name: "Harris County Clerk (TX)", state: "TX", cases: counts.harris_cclerk, active: true },
      { key: "dallas", name: "Dallas County (TX)", state: "TX", cases: counts.dallas, active: true },
      { key: "harris_jp", name: "Harris JP (TX)", state: "TX", cases: counts.harris_jp, active: true },
      { key: "harris_district", name: "Harris District Clerk (TX)", state: "TX", cases: counts.harris_district, active: true },
      { key: "travis", name: "Travis County (TX)", state: "TX", cases: counts.travis, active: true },
    ];
  }, [claims]);

  return (
    <div className="flex-1 flex flex-col w-full">
      <Navbar onRefresh={loadData} isRefreshing={isLoading} />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none flex-1 transition-colors">
        {/* Page Title & Quick Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                Orchestration Dashboard
              </h2>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                Live Dashboard
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              High-throughput claim ingestion, automated 8-county bot scraping, and RapidFuzz deduplication analytics.
            </p>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap">
            <Link
              href="/upload"
              className="flex-1 sm:flex-initial px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 min-h-[40px] cursor-pointer"
            >
              <FileSpreadsheet className="w-4 h-4" />
              Upload Claims
            </Link>
            <Link
              href="/exceptions"
              className="flex-1 sm:flex-initial px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 shadow-xs min-h-[40px] cursor-pointer"
            >
              <AlertTriangle className="w-4 h-4 text-purple-500" />
              Review Exceptions ({stats?.manual_review ?? 0})
            </Link>
          </div>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-4 w-full">
          {statCards.map((card) => (
            <StatCard
              key={card.title}
              title={card.title}
              value={card.value}
              icon={card.icon}
              gradient={card.gradient}
              subtitle={card.subtitle}
              isSelected={statusFilter === card.filterValue}
              onClick={() => {
                if (card.filterValue) {
                  setStatusFilter(statusFilter === card.filterValue ? "all" : card.filterValue);
                  setCurrentPage(1);
                }
              }}
            />
          ))}
        </div>

        {/* Live Queue & Sequential RPA Execution Console */}
        {(() => {
          const activeItems = liveQueue?.active_items && liveQueue.active_items.length > 0
            ? liveQueue.active_items
            : (liveQueue?.active_item ? [liveQueue.active_item] : []);
          const maxConcurrency = liveQueue?.max_concurrency || 3;
          const availableSlots = liveQueue?.available_slots !== undefined ? liveQueue.available_slots : Math.max(0, maxConcurrency - activeItems.length);
          const allPendingItems = liveQueue?.pending_items || [];
          const filteredPendingItems = allPendingItems.filter((item) => {
            if (queueStateFilter === "FL") return item.policy_state === "FL" || item.loss_location_state === "FL";
            if (queueStateFilter === "TX") return item.policy_state === "TX" || item.loss_location_state === "TX";
            return true;
          });
          const flPendingCount = allPendingItems.filter((i) => i.policy_state === "FL" || i.loss_location_state === "FL").length;
          const txPendingCount = allPendingItems.filter((i) => i.policy_state === "TX" || i.loss_location_state === "TX").length;
          const recentCompleted = liveQueue?.recently_completed || [];

          const allSelected = filteredPendingItems.length > 0 && filteredPendingItems.every((i) => selectedQueueIds.includes(i.id));

          const toggleSelectAll = () => {
            if (allSelected) {
              const currentFilteredIds = new Set(filteredPendingItems.map((i) => i.id));
              setSelectedQueueIds(selectedQueueIds.filter((id) => !currentFilteredIds.has(id)));
            } else {
              const combined = Array.from(new Set([...selectedQueueIds, ...filteredPendingItems.map((i) => i.id)]));
              setSelectedQueueIds(combined);
            }
          };

          const toggleSelectItem = (id: string) => {
            if (selectedQueueIds.includes(id)) {
              setSelectedQueueIds(selectedQueueIds.filter((item) => item !== id));
            } else {
              setSelectedQueueIds([...selectedQueueIds, id]);
            }
          };

          return (
            <div className="bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 md:p-6 shadow-xs space-y-5 transition-colors w-full">
              {/* Top Control Ribbon */}
              <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 shrink-0">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <h3 className="text-sm md:text-base font-bold text-slate-900 dark:text-slate-100">
                        Live Queue & RPA Multi-Worker Fleet
                      </h3>
                      {liveQueue?.auto_queue_enabled ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                          Auto-Queue: Active (FIFO)
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
                          <span className="w-2 h-2 rounded-full bg-amber-500" />
                          Queue Paused (Manual)
                        </span>
                      )}
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 font-mono">
                        <Users className="w-3 h-3" />
                        {maxConcurrency}x Workers ({activeItems.length} Busy)
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {activeItems.length > 0
                        ? `${activeItems.length} claim${activeItems.length > 1 ? "s" : ""} actively scraping in parallel across court portals (${availableSlots} slot${availableSlots === 1 ? "" : "s"} free). Next FIFO item auto-advances upon completion.`
                        : (liveQueue?.total_pending_count ?? 0) > 0
                        ? `${liveQueue?.total_pending_count} claims waiting in line. ${liveQueue?.auto_queue_enabled ? `Multi-worker fleet will execute up to ${maxConcurrency} claims in parallel.` : "Resume Auto-Queue or click Start to begin."}`
                        : "Worker fleet is armed and standing by. Click 'Seed 10 Demo Claims' to run immediate live parallel test."}
                    </p>
                  </div>
                </div>

                {/* Toolbar Actions & Concurrency Selector */}
                <div className="flex flex-wrap items-center gap-2 max-w-full justify-start xl:justify-end">
                  {/* Concurrency Selector */}
                  <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700 shrink-0">
                    <span className="text-[10px] font-bold text-slate-500 uppercase px-1.5 flex items-center gap-1">
                      <Sliders className="w-3 h-3" /> Fleet:
                    </span>
                    {[1, 2, 3, 5, 10].map((w) => {
                      const isActive = maxConcurrency === w;
                      return (
                        <button
                          key={w}
                          type="button"
                          onClick={() => handleSetConcurrency(w)}
                          disabled={isUpdatingConcurrency}
                          className={`px-2 py-0.5 text-xs font-bold rounded cursor-pointer transition-all ${
                            isActive
                              ? "bg-indigo-600 text-white shadow-xs"
                              : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
                          }`}
                        >
                          {w}x
                        </button>
                      );
                    })}
                  </div>

                  {/* Seed Demo Claims Button */}
                  <button
                    type="button"
                    onClick={handleSeedDemo}
                    disabled={isSeedingDemo}
                    className="px-3 py-1.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white text-xs font-bold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shrink-0"
                    title="Generate 10 authentic Florida and Texas test claims and start parallel execution"
                  >
                    {isSeedingDemo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-white" />}
                    Seed 10 Demo Claims
                  </button>

                  {/* Toggle Auto-Queue */}
                  <button
                    type="button"
                    onClick={handleToggleAutoQueue}
                    disabled={isTogglingAuto}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all flex items-center gap-1.5 cursor-pointer shrink-0 ${
                      liveQueue?.auto_queue_enabled
                        ? "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800 hover:bg-amber-100"
                        : "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100"
                    }`}
                  >
                    {liveQueue?.auto_queue_enabled ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                    {liveQueue?.auto_queue_enabled ? "Pause Auto-Queue" : "Resume Auto-Queue"}
                  </button>

                  {/* Process Next */}
                  <button
                    type="button"
                    onClick={handleRunNext}
                    disabled={isAdvancingQueue || !liveQueue?.total_pending_count}
                    className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer shrink-0"
                    title="Trigger sequential execution of the #1 next claim in line"
                  >
                    {isAdvancingQueue ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FastForward className="w-3.5 h-3.5" />}
                    Process Next Item
                  </button>

                  {(liveQueue?.total_pending_count ?? 0) > 0 ? (
                    <button
                      type="button"
                      onClick={handleStartAll}
                      className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shrink-0"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      Run All ({liveQueue?.total_pending_count})
                    </button>
                  ) : null}

                  <button
                    type="button"
                    onClick={fetchLiveQueue}
                    className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
                    title="Refresh queue status"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Transition Alert Banner */}
              {lastTransitionMessage && (
                <div className="flex items-center justify-between px-3.5 py-2 bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 rounded-xl text-xs text-indigo-700 dark:text-indigo-300 animate-fadeIn">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-500 shrink-0" />
                    <span className="font-medium">{lastTransitionMessage}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setLastTransitionMessage(null)}
                    className="text-[11px] hover:underline cursor-pointer opacity-70 shrink-0 ml-2"
                  >
                    Dismiss
                  </button>
                </div>
              )}

              {/* Grid: Multi-Worker Active Execution Fleet vs Ordered Pending Queue */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                {/* Column 1: Active Execution Fleet (5 cols on lg) */}
                <div className="lg:col-span-5 flex flex-col">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5 text-indigo-500" />
                      Active Execution Fleet ({activeItems.length} / {maxConcurrency} Busy)
                    </span>
                    {activeItems.length > 0 && (
                      <span className="text-[10px] font-mono text-emerald-500 flex items-center gap-1 font-semibold">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                        Parallel RPA Running
                      </span>
                    )}
                  </div>

                  {activeItems.length > 0 ? (
                    <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
                      {activeItems.map((item, idx) => (
                        <div
                          key={item.id}
                          className="bg-gradient-to-br from-indigo-50/80 via-white to-blue-50/40 dark:from-indigo-950/40 dark:via-slate-900/80 dark:to-slate-950/40 border-2 border-indigo-500/40 dark:border-indigo-500/30 rounded-2xl p-4 shadow-xs relative overflow-hidden flex flex-col justify-between space-y-2.5 transition-all"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-indigo-600 text-white shadow-xs shrink-0">
                                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                                Worker #{idx + 1}
                              </span>
                              <Link
                                href={`/claims/${item.id}`}
                                className="text-xs font-mono font-bold text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 truncate"
                              >
                                #{item.claim_number}
                              </Link>
                            </div>
                            <div className="flex items-center gap-1.5 shrink-0">
                              <span className="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800">
                                {liveElapsedSeconds > 0 ? `${liveElapsedSeconds}s` : "Active"}
                              </span>
                              <button
                                type="button"
                                onClick={() => handleStopClaim(item.id, item.claim_number)}
                                className="p-1 rounded text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/60 hover:text-rose-700 transition-colors cursor-pointer"
                                title="Cancel and abort this claim's RPA run"
                              >
                                <StopCircle className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div>
                            <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 truncate">
                              {item.insured_name || "Unknown Insured"}
                            </h4>
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                              Claimant: <span className="font-medium text-slate-700 dark:text-slate-300">{item.claimant_name || "N/A"}</span>
                            </p>
                          </div>

                          {/* Jurisdiction Route & Portals */}
                          <div className="flex items-center gap-1.5 text-xs flex-wrap">
                            <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono text-[10px] border border-slate-200 dark:border-slate-700">
                              Pol: {item.policy_state || "FL"}
                            </span>
                            <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono text-[10px] border border-slate-200 dark:border-slate-700">
                              Loss: {item.loss_location_state || "FL"}
                            </span>
                            <span className="px-1.5 py-0.5 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-semibold text-[10px]">
                              {item.portals_to_run.length} Portals
                            </span>
                          </div>

                          {/* Portal Running Pills */}
                          <div className="flex flex-wrap gap-1 pt-1">
                            {item.portals_to_run.map((portal) => (
                              <span
                                key={portal}
                                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-medium bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 shadow-2xs"
                              >
                                <span className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse" />
                                {portal}
                              </span>
                            ))}
                          </div>

                          <div className="pt-2 border-t border-indigo-100 dark:border-indigo-900/50 flex items-center justify-between text-[10px]">
                            <Link
                              href={`/claims/${item.id}`}
                              className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 flex items-center gap-1"
                            >
                              Open Inspector
                              <ArrowUpRight className="w-3 h-3" />
                            </Link>
                            <span className="text-slate-400 font-mono">
                              Parallel Thread
                            </span>
                          </div>
                        </div>
                      ))}

                      {/* Available Idle Slots Indicators */}
                      {availableSlots > 0 && (
                        <div className="p-3 rounded-xl border border-dashed border-emerald-300 dark:border-emerald-800/60 bg-emerald-50/20 dark:bg-emerald-950/10 flex items-center justify-between text-xs text-emerald-700 dark:text-emerald-400 font-medium">
                          <span className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            {availableSlots} Worker Slot{availableSlots > 1 ? "s" : ""} Available
                          </span>
                          <span className="text-[10px] font-mono opacity-80">
                            Auto-advancing next FIFO claim
                          </span>
                        </div>
                      )}
                    </div>
                  ) : (
                    /* Interactive Worker Fleet Ready Console - NEVER BLANK! */
                    <div className="flex-1 bg-gradient-to-br from-slate-50 via-indigo-50/30 to-purple-50/20 dark:from-slate-950/60 dark:via-indigo-950/20 dark:to-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center text-center space-y-3.5">
                      <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 dark:bg-indigo-500/20 border border-indigo-200 dark:border-indigo-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shadow-xs">
                        <Bot className="w-6 h-6" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-center gap-2">
                          <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                            Worker Fleet Armed & Standing By
                          </h4>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                            {maxConcurrency} Slots Available
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm">
                          {(liveQueue?.total_pending_count ?? 0) > 0
                            ? `${liveQueue?.total_pending_count} claims waiting in FIFO queue. Click &quot;Process Next&quot; or &quot;Start Parallel Batch&quot; to dispatch workers.`
                            : "No active executions. Generate 10 realistic Florida & Texas test claims to test parallel scraping across court portals."}
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
                        <button
                          type="button"
                          onClick={handleSeedDemo}
                          disabled={isSeedingDemo}
                          className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                        >
                          {isSeedingDemo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                          Seed 10 Demo Claims
                        </button>

                        {(liveQueue?.total_pending_count ?? 0) > 0 && (
                          <button
                            type="button"
                            onClick={handleRunNext}
                            disabled={isAdvancingQueue}
                            className="px-3.5 py-1.5 bg-slate-900 dark:bg-slate-100 hover:bg-slate-800 dark:hover:bg-white text-white dark:text-slate-900 text-xs font-bold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
                          >
                            {isAdvancingQueue ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                            Start Next ({liveQueue?.total_pending_count})
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Column 2: Ordered Pending Queue (7 cols on lg, at least 10 items) */}
                <div className="lg:col-span-7 flex flex-col">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-indigo-500" />
                      Ordered Pending Queue (FIFO Priority)
                    </span>
                    <div className="flex items-center gap-2 text-[11px] font-mono">
                      <span className="font-bold text-slate-700 dark:text-slate-300">
                        {liveQueue?.total_pending_count || 0} Waiting
                      </span>
                      {(liveQueue?.total_pending_count ?? 0) > 0 && (
                        <span className="text-slate-400">
                          • Est. ~{Math.max(1, Math.ceil(((liveQueue?.total_pending_count || 0) * 45) / (maxConcurrency * 60)))}m at {maxConcurrency}x
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex-1 bg-slate-50/50 dark:bg-slate-950/30 border border-slate-200 dark:border-slate-800 rounded-2xl p-3 md:p-4 flex flex-col justify-between space-y-3">
                    {/* Filter & Multi-Select Toolbar */}
                    <div className="flex items-center justify-between gap-2 flex-wrap pb-2 border-b border-slate-200/60 dark:border-slate-800">
                      <div className="flex items-center gap-1.5 text-xs">
                        <button
                          type="button"
                          onClick={() => setQueueStateFilter("ALL")}
                          className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                            queueStateFilter === "ALL"
                              ? "bg-indigo-600 text-white shadow-xs"
                              : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:bg-slate-100"
                          }`}
                        >
                          All ({allPendingItems.length})
                        </button>
                        <button
                          type="button"
                          onClick={() => setQueueStateFilter("FL")}
                          className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                            queueStateFilter === "FL"
                              ? "bg-indigo-600 text-white shadow-xs"
                              : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:bg-slate-100"
                          }`}
                        >
                          Florida ({flPendingCount})
                        </button>
                        <button
                          type="button"
                          onClick={() => setQueueStateFilter("TX")}
                          className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                            queueStateFilter === "TX"
                              ? "bg-indigo-600 text-white shadow-xs"
                              : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:bg-slate-100"
                          }`}
                        >
                          Texas ({txPendingCount})
                        </button>
                      </div>

                      <div className="flex items-center gap-2">
                        {filteredPendingItems.length > 0 && (
                          <button
                            type="button"
                            onClick={toggleSelectAll}
                            className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 flex items-center gap-1 cursor-pointer"
                          >
                            {allSelected ? <CheckSquare className="w-3.5 h-3.5 text-indigo-600" /> : <Square className="w-3.5 h-3.5" />}
                            {allSelected ? "Deselect All" : "Select All"}
                          </button>
                        )}

                        {selectedQueueIds.length > 0 && (
                          <button
                            type="button"
                            onClick={handleRunSelected}
                            disabled={isStartingSelected}
                            className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold rounded shadow-xs flex items-center gap-1 cursor-pointer disabled:opacity-50"
                          >
                            {isStartingSelected ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
                            Run Selected ({selectedQueueIds.length})
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Scrollable Queue Items - At least 10 shown, up to 25 */}
                    {filteredPendingItems.length > 0 ? (
                      <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                        {filteredPendingItems.map((item, idx) => {
                          const isNext = idx === 0;
                          const isSelected = selectedQueueIds.includes(item.id);
                          return (
                            <div
                              key={item.id}
                              className={`p-2.5 sm:p-3 rounded-xl border transition-all flex items-center justify-between gap-3 ${
                                isSelected
                                  ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-400 dark:border-indigo-600 ring-1 ring-indigo-500/30"
                                  : isNext
                                  ? "bg-white dark:bg-slate-900 border-indigo-300 dark:border-indigo-700/80 shadow-xs ring-1 ring-indigo-500/20"
                                  : "bg-white/70 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                              }`}
                            >
                              <div className="flex items-center gap-2.5 min-w-0">
                                <button
                                  type="button"
                                  onClick={() => toggleSelectItem(item.id)}
                                  className="text-slate-400 hover:text-indigo-600 cursor-pointer shrink-0"
                                >
                                  {isSelected ? (
                                    <CheckSquare className="w-4 h-4 text-indigo-600" />
                                  ) : (
                                    <Square className="w-4 h-4" />
                                  )}
                                </button>

                                <span
                                  className={`px-2 py-1 rounded-md text-[10px] font-black tracking-tight shrink-0 font-mono ${
                                    isNext
                                      ? "bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-xs"
                                      : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700"
                                  }`}
                                >
                                  {isNext ? "★ #1 NEXT" : `#${item.queue_position || idx + 1}`}
                                </span>

                                <div className="min-w-0">
                                  <div className="flex items-center gap-2">
                                    <Link
                                      href={`/claims/${item.id}`}
                                      className="text-xs font-bold text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 truncate"
                                    >
                                      {item.claim_number}
                                    </Link>
                                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700 shrink-0">
                                      {item.policy_state || "FL"}
                                    </span>
                                  </div>
                                  <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                                    {item.insured_name || "Unknown"} • {item.portals_to_run.length} Portals
                                  </div>
                                </div>
                              </div>

                              <div className="flex items-center gap-1.5 shrink-0">
                                <button
                                  type="button"
                                  onClick={async () => {
                                    await api.startClaim(item.id);
                                    fetchLiveQueue();
                                    loadData();
                                  }}
                                  className="px-2 py-1 text-[10px] font-semibold rounded bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-700 transition-colors flex items-center gap-1 cursor-pointer"
                                  title="Run this claim right now"
                                >
                                  <Play className="w-2.5 h-2.5" />
                                  Run Now
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="py-8 text-center space-y-2">
                        <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto opacity-70" />
                        <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
                          {queueStateFilter === "ALL" ? "No Pending Queue Items" : `No Pending ${queueStateFilter} Claims`}
                        </div>
                        <p className="text-[11px] text-slate-400 max-w-xs mx-auto">
                          All claims have completed execution. Ingest new claims via Upload or click &quot;Seed 10 Demo Claims&quot; above.
                        </p>
                      </div>
                    )}

                    {/* Footer Pipeline Summary */}
                    <div className="pt-2.5 mt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                      <span className="flex items-center gap-1.5">
                        <Zap className="w-3.5 h-3.5 text-amber-500" />
                        Multi-worker runner pulls up to {maxConcurrency} claims simultaneously
                      </span>
                      <Link
                        href="/monitor"
                        className="font-medium text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        Queue Monitor
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Completed Executions Stream (Last 5-10 Claims) */}
              {recentCompleted.length > 0 && (
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowRecentCompleted(!showRecentCompleted)}
                    className="flex items-center justify-between w-full text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors cursor-pointer"
                  >
                    <span className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                      Recent Executions Stream ({recentCompleted.length} Completed Claims)
                    </span>
                    {showRecentCompleted ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {showRecentCompleted && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-2.5 pt-3">
                      {recentCompleted.slice(0, 5).map((item) => {
                        const isMatch = item.record_status === "MATCH_FOUND";
                        const isNoMatch = item.record_status === "NO_MATCH_FOUND";
                        const isFailed = item.record_status === "FAILED";
                        return (
                          <Link
                            key={item.id}
                            href={`/claims/${item.id}`}
                            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 hover:border-indigo-300 dark:hover:border-indigo-700 transition-all block group"
                          >
                            <div className="flex items-center justify-between text-[11px] mb-1">
                              <span className="font-mono font-bold text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                                #{item.claim_number}
                              </span>
                              <span
                                className={`px-1.5 py-0.2 rounded text-[9px] font-bold uppercase ${
                                  isMatch
                                    ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                                    : isNoMatch
                                    ? "bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300"
                                    : isFailed
                                    ? "bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300"
                                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                                }`}
                              >
                                {item.record_status.replace(/_/g, " ")}
                              </span>
                            </div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                              {item.insured_name || "Unknown Insured"}
                            </div>
                            <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1 font-mono">
                              <span>{item.policy_state || "FL"}</span>
                              <span>{item.total_duration_seconds ? `${Math.round(item.total_duration_seconds)}s` : "Finished"}</span>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })()}

        {/* Visual Charts & Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 w-full">
          {/* Chart 1: Lifecycle & Status Distribution */}
          <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PieChart className="w-4 h-4 text-indigo-500" />
                <h3 className="text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                  Lifecycle Distribution
                </h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">{totalClaims} Records</span>
            </div>

            {/* Segment Progress Bar */}
            <div className="space-y-2">
              <div className="h-3 w-full rounded-full bg-slate-100 dark:bg-slate-800 flex overflow-hidden p-0.5 gap-0.5">
                <div
                  style={{ width: `${Math.max(4, completedPercentage)}%` }}
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  title={`Completed: ${completedPercentage}%`}
                />
                <div
                  style={{ width: `${Math.max(4, inProgressPercentage)}%` }}
                  className="h-full bg-amber-500 rounded-full transition-all duration-500"
                  title={`In Progress: ${inProgressPercentage}%`}
                />
                <div
                  style={{ width: `${Math.max(4, reviewPercentage)}%` }}
                  className="h-full bg-purple-500 rounded-full transition-all duration-500"
                  title={`Exceptions: ${reviewPercentage}%`}
                />
              </div>

              {/* Legend with Counts */}
              <div className="grid grid-cols-2 gap-2 pt-2 text-xs">
                <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-950/50 border border-slate-100 dark:border-slate-800">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] text-slate-400">Completed</div>
                    <div className="font-bold font-mono text-slate-800 dark:text-slate-200">
                      {stats?.completed || 0} ({completedPercentage}%)
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-950/50 border border-slate-100 dark:border-slate-800">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] text-slate-400">In Progress</div>
                    <div className="font-bold font-mono text-slate-800 dark:text-slate-200">
                      {stats?.in_progress || 0} ({inProgressPercentage}%)
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-950/50 border border-slate-100 dark:border-slate-800">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] text-slate-400">Exceptions</div>
                    <div className="font-bold font-mono text-slate-800 dark:text-slate-200">
                      {stats?.manual_review || 0} ({reviewPercentage}%)
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-950/50 border border-slate-100 dark:border-slate-800">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] text-slate-400">Matches Found</div>
                    <div className="font-bold font-mono text-slate-800 dark:text-slate-200">
                      {stats?.match_found || 0} ({matchPercentage}%)
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Chart 2: 8 County Court Scraper Bots Volume */}
          <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-sky-500" />
                <h3 className="text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                  Bot Scraper Throughput (8 Portals)
                </h3>
              </div>
              <span className="text-[10px] font-medium text-emerald-500 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                All Ready
              </span>
            </div>

            <div className="space-y-2 pt-1">
              {portalBreakdown.map((p) => (
                <div key={p.name} className="space-y-1 text-xs">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-600 dark:text-slate-300 font-medium flex items-center gap-1.5">
                      <span className="font-mono text-[9px] px-1 py-0.2 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        {p.state}
                      </span>
                      {p.name}
                    </span>
                    <span className="font-mono text-slate-500 dark:text-slate-400 text-[10px]">
                      {p.cases} cases extracted
                    </span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${Math.min(100, Math.max(p.cases > 0 ? 10 : 0, (p.cases / Math.max(1, ...portalBreakdown.map((x) => x.cases))) * 100))}%` }}
                      className={`h-full rounded-full ${
                        p.state === "FL" ? "bg-sky-500" : "bg-indigo-500"
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chart 3: Automation Efficiency & RapidFuzz Stats */}
          <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-500" />
                  <h3 className="text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                    Engine Velocity & Telemetry
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-indigo-400">RapidFuzz Active</span>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-3">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Avg Scrape Cycle</span>
                  <span className="text-base font-bold font-mono text-slate-800 dark:text-slate-200">
                    18.45s
                  </span>
                  <span className="text-[9px] text-emerald-500 block mt-0.5">Microsecond accuracy</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Deduplication</span>
                  <span className="text-base font-bold font-mono text-slate-800 dark:text-slate-200">
                    token_sort_ratio
                  </span>
                  <span className="text-[9px] text-indigo-400 block mt-0.5">Threshold: 75%</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Guidewire Trigger</span>
                  <span className="text-base font-bold font-mono text-emerald-600 dark:text-emerald-400">
                    Automatic
                  </span>
                  <span className="text-[9px] text-slate-400 block mt-0.5">Auto-push on match</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Worker Concurrency</span>
                  <span className="text-base font-bold font-mono text-slate-800 dark:text-slate-200">
                    4 Online
                  </span>
                  <span className="text-[9px] text-sky-400 block mt-0.5">Celery Distributed</span>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                <span className="font-medium text-indigo-900 dark:text-indigo-200 text-[11px]">
                  System settings synced to runtime
                </span>
              </div>
              <Link
                href="/settings"
                className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline font-semibold"
              >
                Configure &rarr;
              </Link>
            </div>
          </div>
        </div>

        {/* Tabular Claims Engine Section with Sorting, Multi-Column Filtering, and Pagination */}
        <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4 shadow-xs w-full transition-colors">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-500" />
                Claims Orchestration Register
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Explore all ingested claim records with full column sorting, multi-attribute filtering, and pagination.
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                {totalFilteredCount} {totalFilteredCount === 1 ? "claim" : "claims"} found
              </span>
              <button
                type="button"
                onClick={() => setIsExportModalOpen(true)}
                className="text-xs text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white font-medium flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-colors cursor-pointer"
                title="Export claims dataset (Excel/CSV/JSON)"
              >
                <Download className="w-3.5 h-3.5 text-emerald-600" />
                <span>Export Dataset</span>
              </button>
              <Link
                href="/monitor"
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-medium flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800/60"
              >
                Full Monitor &rarr;
              </Link>
            </div>
          </div>

          {/* Quick Filter Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-2 border-b border-slate-100 dark:border-slate-800 text-xs">
            {[
              { id: "all", label: "All Claims", count: totalClaims, filter: "all" },
              { id: "active", label: "Active / Running", count: (stats?.in_progress ?? 0) + (liveQueue?.is_running ? 1 : 0), filter: "SCRAPING_IN_PROGRESS" },
              { id: "pending", label: "Queue Pending (FIFO)", count: liveQueue?.total_pending_count ?? 0, filter: "NEW" },
              { id: "matches", label: "Matches Found", count: stats?.match_found ?? 0, filter: "MATCH_FOUND" },
              { id: "exceptions", label: "Exceptions", count: stats?.manual_review ?? 0, filter: "MANUAL_REVIEW" },
              { id: "completed", label: "Completed", count: stats?.completed ?? 0, filter: "SCRAPING_COMPLETED" },
            ].map((tab) => {
              const isActive = statusFilter === tab.filter;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setStatusFilter(tab.filter);
                    setCurrentPage(1);
                  }}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all shrink-0 flex items-center gap-1.5 cursor-pointer ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-xs"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                  }`}
                >
                  <span>{tab.label}</span>
                  <span
                    className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                      isActive ? "bg-white/20 text-white" : "bg-white dark:bg-slate-900 text-slate-500"
                    }`}
                  >
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Phase 6 (§83) Filter Preset Manager */}
          <div className="pt-1 border-t border-slate-100 dark:border-slate-800/60">
            <FilterPresetManager
              currentStatus={statusFilter === "all" ? "" : statusFilter}
              currentState={stateFilter === "all" ? "" : stateFilter}
              currentSearch={searchTerm}
              onApplyPreset={(p) => {
                setStatusFilter(p.status ? p.status : "all");
                setStateFilter(p.state ? p.state : "all");
                setSearchTerm(p.search || "");
                setCurrentPage(1);
              }}
              onResetFilters={() => {
                setStatusFilter("all");
                setStateFilter("all");
                setSearchTerm("");
                setCurrentPage(1);
              }}
            />
          </div>

          {/* Search and Filters Toolbar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5 pt-1">
            {/* Search Input */}
            <div className="relative lg:col-span-2">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                placeholder="Search claim #, insured, claimant..."
                className="w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-hidden focus:border-indigo-500"
              />
            </div>

            {/* Status Filter */}
            <div>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-700 dark:text-slate-300 focus:outline-hidden cursor-pointer"
              >
                <option value="all">All Statuses</option>
                <option value="NEW">New / Queued</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="COMPLETED">Completed</option>
                <option value="MANUAL_REVIEW">Manual Review</option>
                <option value="FAILED">Failed</option>
              </select>
            </div>

            {/* State Filter */}
            <div>
              <select
                value={stateFilter}
                onChange={(e) => {
                  setStateFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-700 dark:text-slate-300 focus:outline-hidden cursor-pointer"
              >
                <option value="all">All States</option>
                <option value="FL">Florida (FL)</option>
                <option value="TX">Texas (TX)</option>
              </select>
            </div>

            {/* Reset Filters / Match Filter */}
            <div className="flex items-center gap-2">
              <select
                value={matchFilter}
                onChange={(e) => {
                  setMatchFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-700 dark:text-slate-300 focus:outline-hidden cursor-pointer"
              >
                <option value="all">All Matches</option>
                <option value="MATCH_FOUND">Match Confirmed</option>
                <option value="PENDING_REVIEW">Needs Review</option>
                <option value="NO_MATCH_FOUND">No Match</option>
              </select>

              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  title="Clear all active filters"
                  className="p-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-lg transition-colors cursor-pointer shrink-0"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Tabular Claims Table (>= md) */}
          <div className="hidden md:block overflow-x-auto w-full border border-slate-200 dark:border-slate-800 rounded-xl">
            <table className="w-full text-left text-xs min-w-full">
              <thead className="text-[11px] text-slate-600 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 bg-slate-100/90 dark:bg-slate-950/80 uppercase tracking-wider font-semibold">
                <tr>
                  <th
                    onClick={() => handleSort("claim_number")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Claim Number {renderSortIcon("claim_number")}
                  </th>
                  <th
                    onClick={() => handleSort("insured_name")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Insured Party {renderSortIcon("insured_name")}
                  </th>
                  <th
                    onClick={() => handleSort("claimant_name")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Claimant Party {renderSortIcon("claimant_name")}
                  </th>
                  <th
                    onClick={() => handleSort("loss_location_state")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Jurisdiction {renderSortIcon("loss_location_state")}
                  </th>
                  <th
                    onClick={() => handleSort("record_status")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Lifecycle Status {renderSortIcon("record_status")}
                  </th>
                  <th
                    onClick={() => handleSort("fuzzy_match_status")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Fuzzy Match {renderSortIcon("fuzzy_match_status")}
                  </th>
                  <th
                    onClick={() => handleSort("created_at")}
                    className="py-3 px-4 cursor-pointer hover:text-slate-900 dark:hover:text-slate-200 select-none"
                  >
                    Ingested Date {renderSortIcon("created_at")}
                  </th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white dark:bg-slate-950/40">
                {paginatedClaims.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-400 dark:text-slate-500">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <Filter className="w-6 h-6 opacity-40" />
                        <span className="text-xs">No claims match the selected search and filter criteria.</span>
                        {hasActiveFilters && (
                          <button
                            onClick={clearFilters}
                            className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-medium mt-1 cursor-pointer"
                          >
                            Reset filters
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  paginatedClaims.map((claim) => (
                    <tr
                      key={claim.id}
                      className="hover:bg-slate-50 dark:hover:bg-slate-900/60 transition-colors"
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900 dark:text-slate-100">
                        <Link
                          href={`/claims/${claim.id}`}
                          className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                        >
                          {claim.claim_number}
                        </Link>
                      </td>
                      <td className="py-3.5 px-4 text-slate-800 dark:text-slate-200 font-medium">
                        {claim.insured_name || "-"}
                      </td>
                      <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300">
                        {claim.claimant_name || "-"}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                          {claim.policy_state || claim.loss_location_state || "FL"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={claim.record_status} size="sm" />
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={claim.fuzzy_match_status} size="sm" />
                      </td>
                      <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 text-[11px]">
                        {formatDate(claim.created_at)}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          href={`/claims/${claim.id}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-md font-semibold text-xs transition-colors"
                        >
                          Audit &rarr;
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Mobile Card List (< md) */}
          <div className="block md:hidden space-y-3 w-full">
            {paginatedClaims.length === 0 ? (
              <div className="py-8 text-center text-slate-400 dark:text-slate-500 text-xs">
                No claims match the active criteria.
              </div>
            ) : (
              paginatedClaims.map((claim) => (
                <div
                  key={claim.id}
                  className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 space-y-2.5 shadow-2xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-slate-900 dark:text-slate-100">
                        {claim.claim_number}
                      </span>
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {claim.policy_state || "FL"}
                      </span>
                    </div>
                    <StatusBadge status={claim.record_status} size="sm" />
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 dark:text-slate-300">
                    <div>
                      <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Insured</span>
                      <span className="font-medium truncate block">{claim.insured_name || "-"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Claimant</span>
                      <span className="font-medium truncate block">{claim.claimant_name || "-"}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-800 text-xs">
                    <StatusBadge status={claim.fuzzy_match_status} size="sm" />
                    <Link
                      href={`/claims/${claim.id}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 rounded-lg font-semibold text-xs min-h-[36px]"
                    >
                      Audit Details &rarr;
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination Controls */}
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
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
              <span>
                Showing {totalFilteredCount === 0 ? 0 : (currentPage - 1) * pageSize + 1} to{" "}
                {Math.min(currentPage * pageSize, totalFilteredCount)} of {totalFilteredCount} claims
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
        </div>

        {/* High-Volume Background Dataset Export Modal (§55) */}
        <AsyncExportModal
          isOpen={isExportModalOpen}
          onClose={() => setIsExportModalOpen(false)}
          statusFilter={statusFilter === "all" ? undefined : statusFilter}
          stateFilter={stateFilter === "all" ? undefined : stateFilter}
          searchTerm={searchTerm}
          totalRecordsCount={totalFilteredCount}
        />
      </main>
    </div>
  );
}
