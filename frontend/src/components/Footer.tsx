"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, ShieldCheck, Cpu, HardDrive, ExternalLink } from "lucide-react";
import { api } from "../lib/api";

export const Footer: React.FC = () => {
  const [workerCount, setWorkerCount] = useState<number>(1);
  const [isHealthy, setIsHealthy] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    const checkQueue = async () => {
      try {
        const data = await api.getQueueStatus();
        if (isMounted && data) {
          setWorkerCount(data.workers_online || 1);
          setIsHealthy(true);
        }
      } catch {
        if (isMounted) {
          setIsHealthy(false);
        }
      }
    };
    checkQueue();
    const interval = setInterval(checkQueue, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <footer className="no-print w-full mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950/90 text-slate-600 dark:text-slate-400 text-xs transition-colors">
      <div className="w-full px-4 sm:px-6 md:px-8 py-4 sm:py-5">
        <div className="flex flex-col md:flex-row items-center justify-between gap-3 sm:gap-4 text-center sm:text-left">
          {/* Left: Branding & Status Pill */}
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0" />
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                Engine Status:
              </span>
              <span className="inline-flex items-center gap-1 font-mono text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-bold">
                <Activity className="w-3 h-3 text-emerald-500 shrink-0" />
                {isHealthy ? "ONLINE & READY" : "DEGRADED"}
              </span>
            </div>

            <div className="hidden sm:flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 border-l border-slate-200 dark:border-slate-800 pl-3">
              <span className="flex items-center gap-1">
                <Cpu className="w-3 h-3 text-indigo-500 shrink-0" />
                <span>Celery Workers:</span>
                <strong className="font-mono text-slate-700 dark:text-slate-300">
                  {workerCount} Active
                </strong>
              </span>
              <span className="text-slate-300 dark:text-slate-700">•</span>
              <span className="flex items-center gap-1">
                <HardDrive className="w-3 h-3 text-sky-500 shrink-0" />
                <span>County Bots:</span>
                <strong className="font-mono text-slate-700 dark:text-slate-300">
                  8 Registered
                </strong>
              </span>
              <span className="text-slate-300 dark:text-slate-700">•</span>
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-teal-500 shrink-0" />
                <span>Attended Mode:</span>
                <strong className="font-mono text-emerald-600 dark:text-emerald-400">
                  Real Chrome
                </strong>
              </span>
            </div>
          </div>

          {/* Right: Quick Links & Version Info */}
          <div className="flex flex-wrap items-center justify-center sm:justify-end gap-3 sm:gap-4 text-[11px] text-slate-500 dark:text-slate-400">
            <Link
              href="/monitor"
              className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              Queue Monitor
            </Link>
            <Link
              href="/settings"
              className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              Automation Settings
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="hidden sm:flex items-center gap-1 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              API Docs
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
            <span className="border-l border-slate-200 dark:border-slate-800 pl-3 font-mono text-[10px]">
              v1.0.0 (Python 3.14.7)
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
