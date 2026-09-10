"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Server,
  Database,
  Cpu,
  Globe,
  Chrome,
  ShieldCheck,
  Send,
  HardDrive,
  ExternalLink,
  Zap,
  ArrowUpRight,
  Clock,
  Radio,
  Play,
} from "lucide-react";
import { Navbar } from "../../components/Navbar";
import { api } from "../../lib/api";
import { SystemHealthData, HealthStatus, PortalPingResponse, BrowserTestResponse } from "../../types";

export default function OperationalHealthPage() {
  const [healthData, setHealthData] = useState<SystemHealthData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);
  const [autoRefreshInterval, setAutoRefreshInterval] = useState<number>(15); // Default 15s (§62)
  const [pingStates, setPingStates] = useState<Record<string, { loading: boolean; result?: PortalPingResponse }>>({});

  // RPA Browser & Automation Health Panel State (§62)
  const [isTestingBrowser, setIsTestingBrowser] = useState(false);
  const [testingMode, setTestingMode] = useState<"attended" | "headless" | null>(null);
  const [browserTestResult, setBrowserTestResult] = useState<BrowserTestResponse | null>(null);

  const fetchHealth = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getDetailedHealth();
      setHealthData(data);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Health check error:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  // Auto-refresh interval
  useEffect(() => {
    if (autoRefreshInterval <= 0) return;
    const timer = setInterval(() => {
      fetchHealth();
    }, autoRefreshInterval * 1000);
    return () => clearInterval(timer);
  }, [autoRefreshInterval, fetchHealth]);

  const handlePingPortal = async (portalKey: string) => {
    setPingStates((prev) => ({
      ...prev,
      [portalKey]: { loading: true },
    }));

    try {
      const res = await api.pingPortal(portalKey);
      setPingStates((prev) => ({
        ...prev,
        [portalKey]: { loading: false, result: res },
      }));
    } catch (err: any) {
      setPingStates((prev) => ({
        ...prev,
        [portalKey]: {
          loading: false,
          result: {
            portal_key: portalKey,
            portal_name: portalKey,
            url: "",
            reachable: false,
            status_code: 500,
            latency_ms: 0,
            status: "critical",
            error: err?.message || "Failed to reach portal ping endpoint",
          },
        },
      }));
    }
  };

  const handleLaunchBrowserTest = async (headless: boolean) => {
    setIsTestingBrowser(true);
    setTestingMode(headless ? "headless" : "attended");
    setBrowserTestResult(null);
    try {
      const res = await api.testBrowserLaunch({
        headless,
        browser_engine: "chromium",
        test_url: "https://example.com",
        timeout_seconds: 25,
      });
      setBrowserTestResult(res);
    } catch (err: any) {
      setBrowserTestResult({
        success: false,
        mode: headless ? "Headless (Background)" : "Attended (Visible GUI)",
        headless,
        chrome_found: false,
        extension_found: false,
        duration_ms: 0,
        message: err?.response?.data?.detail || "Browser launch test failed.",
        error_detail: String(err),
      });
    } finally {
      setIsTestingBrowser(false);
    }
  };

  const getStatusBadge = (status: HealthStatus) => {
    switch (status) {
      case "healthy":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
            <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
          </span>
        );
      case "warning":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-300 dark:border-amber-800">
            <AlertTriangle className="w-3.5 h-3.5" /> Warning
          </span>
        );
      case "critical":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-300 dark:border-rose-800">
            <XCircle className="w-3.5 h-3.5" /> Critical
          </span>
        );
      default:
        return null;
    }
  };

  const getComponentIcon = (key: string) => {
    switch (key) {
      case "api":
        return Server;
      case "database":
        return Database;
      case "redis":
        return Zap;
      case "celery":
        return Cpu;
      case "chrome":
        return Chrome;
      case "anticaptcha":
        return ShieldCheck;
      case "guidewire":
        return Send;
      case "storage":
        return HardDrive;
      default:
        return Radio;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col">
      <Navbar />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none flex-1 transition-colors">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-blue-600 text-white shadow-lg shadow-blue-500/20">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Operational System Health
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                  Real-time telemetry and diagnostics across API, Database, Redis, Celery, Chrome, AntiCaptcha, Guidewire, & 8 Portals.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Auto Refresh selector */}
            <div className="flex items-center space-x-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-2 rounded-lg shadow-sm">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-500 dark:text-slate-400">Auto Refresh:</span>
              <select
                value={autoRefreshInterval}
                onChange={(e) => setAutoRefreshInterval(Number(e.target.value))}
                className="bg-transparent font-medium text-slate-700 dark:text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value={0}>Off</option>
                <option value={5}>Every 5s</option>
                <option value={15}>Every 15s</option>
                <option value={30}>Every 30s</option>
              </select>
            </div>

            {/* Manual Refresh button */}
            <button
              onClick={fetchHealth}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Global Status Banner */}
        {healthData && (
          <div
            className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
              healthData.status === "healthy"
                ? "bg-emerald-50/70 border-emerald-200 dark:bg-emerald-950/20 dark:border-emerald-900/50"
                : healthData.status === "warning"
                ? "bg-amber-50/70 border-amber-200 dark:bg-amber-950/20 dark:border-amber-900/50"
                : "bg-rose-50/70 border-rose-200 dark:bg-rose-950/20 dark:border-rose-900/50"
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`p-2 rounded-lg ${
                  healthData.status === "healthy"
                    ? "bg-emerald-500 text-white"
                    : healthData.status === "warning"
                    ? "bg-amber-500 text-white"
                    : "bg-rose-500 text-white"
                }`}
              >
                {healthData.status === "healthy" ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : healthData.status === "warning" ? (
                  <AlertTriangle className="w-5 h-5" />
                ) : (
                  <XCircle className="w-5 h-5" />
                )}
              </div>
              <div>
                <h2 className="text-base font-semibold text-slate-900 dark:text-white capitalize">
                  Overall System Posture: {healthData.status}
                </h2>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                  Environment: <span className="font-medium uppercase">{healthData.environment}</span> • Version:{" "}
                  <span className="font-mono">{healthData.version}</span> • Last checked:{" "}
                  {lastRefreshed ? lastRefreshed.toLocaleTimeString() : "Just now"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {getStatusBadge(healthData.status)}
            </div>
          </div>
        )}

        {/* Dedicated RPA Browser & Automation Health Panel (§62) */}
        <section className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Chrome className="w-5 h-5 text-indigo-500" />
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                RPA Browser & Automation Health Panel
              </h2>
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300">
                §62 Live Diagnostic Console
              </span>
            </div>
            <Link
              href="/settings"
              className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
            >
              Configure in Automation Settings <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xs space-y-6">
            {/* Top Stat Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 space-y-1">
                <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Configured Browser Engine
                </span>
                <div className="flex items-center gap-2 text-slate-900 dark:text-slate-100 font-bold text-sm">
                  <Chrome className="w-4 h-4 text-indigo-500" />
                  <span>Google Chrome / Chromium</span>
                </div>
                <p className="text-[10px] text-slate-400 font-mono">
                  Engine: {healthData?.components?.chrome?.details?.execution_mode || "Attended GUI & Headless"}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 space-y-1">
                <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Executable Detection
                </span>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold ${
                      healthData?.components?.chrome?.details?.detected
                        ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                        : "bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300"
                    }`}
                  >
                    {healthData?.components?.chrome?.details?.detected ? "DETECTED" : "NOT FOUND"}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate" title={String(healthData?.components?.chrome?.details?.executable_path || "")}>
                  {String(healthData?.components?.chrome?.details?.executable_path || "Auto-detected")}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 space-y-1">
                <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  AntiCaptcha Extension (v0.83)
                </span>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold ${
                      healthData?.components?.anticaptcha?.details?.extension_detected
                        ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                        : "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300"
                    }`}
                  >
                    {healthData?.components?.anticaptcha?.details?.extension_detected ? "LOADED & VERIFIED" : "PENDING"}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                  API Key: {healthData?.components?.anticaptcha?.details?.api_key_configured ? "Configured ✓" : "Missing key"}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 space-y-1">
                <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Interactive Test Controls
                </span>
                <div className="flex items-center gap-2 pt-1 flex-wrap">
                  <button
                    type="button"
                    onClick={() => handleLaunchBrowserTest(false)}
                    disabled={isTestingBrowser}
                    className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors disabled:opacity-50"
                  >
                    {isTestingBrowser && testingMode === "attended" ? (
                      <RefreshCw className="w-3 h-3 animate-spin" />
                    ) : (
                      <Play className="w-3 h-3" />
                    )}
                    Visible GUI Test
                  </button>
                  <button
                    type="button"
                    onClick={() => handleLaunchBrowserTest(true)}
                    disabled={isTestingBrowser}
                    className="px-2.5 py-1 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 rounded text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors disabled:opacity-50"
                  >
                    {isTestingBrowser && testingMode === "headless" ? (
                      <RefreshCw className="w-3 h-3 animate-spin" />
                    ) : (
                      <Zap className="w-3 h-3" />
                    )}
                    Headless
                  </button>
                </div>
              </div>
            </div>

            {/* Live Test Results Console Display */}
            {browserTestResult && (
              <div
                className={`p-4 rounded-xl border text-xs space-y-2.5 transition-all ${
                  browserTestResult.success
                    ? "bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800/80"
                    : "bg-rose-50/50 dark:bg-rose-950/20 border-rose-300 dark:border-rose-800/80"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {browserTestResult.success ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-600" />
                    )}
                    <span className="font-bold text-slate-900 dark:text-slate-100">
                      Browser Verification Result ({browserTestResult.mode})
                    </span>
                    <span className="font-mono text-slate-500">
                      {browserTestResult.duration_ms}ms
                    </span>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                      browserTestResult.success
                        ? "bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300"
                        : "bg-rose-100 dark:bg-rose-900/60 text-rose-800 dark:text-rose-300"
                    }`}
                  >
                    {browserTestResult.success ? "VERIFIED SUCCESS" : "FAILED"}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono text-[11px] text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-200/60 dark:border-slate-800/60">
                  <div>
                    Extension Loaded: <strong className="text-slate-800 dark:text-slate-200">{browserTestResult.extension_loaded ? "Yes (Active)" : "No"}</strong>
                  </div>
                  <div>
                    Service Worker: <strong className="text-slate-800 dark:text-slate-200">{browserTestResult.service_worker_active ? "Running" : "Inactive"}</strong>
                  </div>
                  <div>
                    Page Title: <strong className="text-slate-800 dark:text-slate-200 truncate">{browserTestResult.page_title || "-"}</strong>
                  </div>
                </div>

                {browserTestResult.message && (
                  <div className="text-[11px] text-slate-700 dark:text-slate-300">
                    {browserTestResult.message}
                  </div>
                )}
                {browserTestResult.error_detail && (
                  <div className="p-2 rounded bg-rose-100/70 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 font-mono text-[10px] whitespace-pre-wrap">
                    {browserTestResult.error_detail}
                  </div>
                )}
              </div>
            )}
          </div>
        </section>

        {/* Section 1: Core System Architecture Components */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <Server className="w-5 h-5 text-blue-600" />
              Core Infrastructure Stack
            </h2>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              8 Core Modules Monitored
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {healthData &&
              Object.entries(healthData.components).map(([key, comp]) => {
                const Icon = getComponentIcon(key);
                return (
                  <div
                    key={key}
                    className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2 mb-3">
                        <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200">
                          <Icon className="w-5 h-5" />
                        </div>
                        {getStatusBadge(comp.status)}
                      </div>

                      <h3 className="font-semibold text-slate-900 dark:text-white text-base">
                        {comp.name}
                      </h3>

                      {comp.latency_ms !== undefined && (
                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-1">
                          <Zap className="w-3.5 h-3.5 text-amber-500" /> Latency:{" "}
                          <span className="font-mono font-medium text-slate-700 dark:text-slate-200">
                            {comp.latency_ms} ms
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-xs text-slate-600 dark:text-slate-400 space-y-1 font-mono">
                      {Object.entries(comp.details).slice(0, 3).map(([k, v]) => (
                        <div key={k} className="flex justify-between truncate">
                          <span className="text-slate-400 capitalize">{k.replace(/_/g, " ")}:</span>
                          <span className="font-medium text-slate-800 dark:text-slate-200 truncate ml-2">
                            {String(v)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
          </div>
        </section>

        {/* Section 2: 8 County Court Scraper Portals */}
        <section className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-600" />
                County Court Clerk Portals (8 Portals)
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Live reachability, HTTP latency test, and target automation configuration.
              </p>
            </div>

            <Link
              href="/settings"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
            >
              Configure Portals in Settings <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {healthData &&
              Object.entries(healthData.portals).map(([key, portal]) => {
                const pingState = pingStates[key];
                return (
                  <div
                    key={key}
                    className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {portal.state}
                        </span>
                        {portal.enabled ? (
                          <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> Enabled
                          </span>
                        ) : (
                          <span className="text-[11px] font-semibold text-slate-400">
                            Disabled
                          </span>
                        )}
                      </div>

                      <h3 className="font-semibold text-slate-900 dark:text-white text-base truncate" title={portal.name}>
                        {portal.name}
                      </h3>

                      <a
                        href={portal.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 mt-1 truncate"
                        title={portal.url}
                      >
                        <span className="truncate">{portal.url}</span>
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>

                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {portal.has_dol && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium">
                            DOL Search
                          </span>
                        )}
                        {portal.has_casetype ? (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 font-medium">
                            CaseType
                          </span>
                        ) : (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 font-medium">
                            No CaseType
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                      {pingState?.result ? (
                        <div className="mb-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 text-xs space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">HTTP Status:</span>
                            <span
                              className={`font-semibold font-mono ${
                                pingState.result.reachable ? "text-emerald-600" : "text-rose-600"
                              }`}
                            >
                              {pingState.result.status_code || "ERR"}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">Latency:</span>
                            <span className="font-mono text-slate-700 dark:text-slate-300">
                              {pingState.result.latency_ms} ms
                            </span>
                          </div>
                          {pingState.result.error && (
                            <p className="text-[11px] text-rose-500 truncate" title={pingState.result.error}>
                              {pingState.result.error}
                            </p>
                          )}
                        </div>
                      ) : null}

                      <button
                        onClick={() => handlePingPortal(key)}
                        disabled={pingState?.loading}
                        className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-colors disabled:opacity-50"
                      >
                        <RefreshCw className={`w-3.5 h-3.5 ${pingState?.loading ? "animate-spin" : ""}`} />
                        {pingState?.loading ? "Pinging..." : "Ping Portal"}
                      </button>
                    </div>
                  </div>
                );
              })}
          </div>
        </section>
      </main>
    </div>
  );
}
