import React from "react";
import { RecordStatus, FuzzyMatchStatus, BotStatus } from "../types";
import { cn } from "../lib/utils";

interface StatusBadgeProps {
  status: RecordStatus | FuzzyMatchStatus | BotStatus | string;
  className?: string;
  size?: "sm" | "md";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className,
  size = "md",
}) => {
  const sizeClasses =
    size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs";

  let colorClasses = "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700";
  let label = status;

  switch (status) {
    case "NEW":
      colorClasses = "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-400 border-sky-200 dark:border-sky-800/60";
      label = "New";
      break;
    case "SCRAPING_IN_PROGRESS":
    case "IN_PROGRESS":
      colorClasses = "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/60 animate-pulse";
      label = "In Progress";
      break;
    case "SCRAPING_COMPLETED":
      colorClasses = "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800/60";
      label = "Scraped";
      break;
    case "MATCH_FOUND":
    case "APPROVED":
    case "COMPLETED":
      colorClasses = "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/60";
      label = status === "MATCH_FOUND" ? "Match Found" : status === "APPROVED" ? "Approved" : "Completed";
      break;
    case "NO_MATCH_FOUND":
      colorClasses = "bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700";
      label = "No Match";
      break;
    case "MANUAL_REVIEW":
    case "PENDING_REVIEW":
      colorClasses = "bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800/60 ring-1 ring-purple-400/30";
      label = "Under Review";
      break;
    case "FAILED":
    case "REJECTED":
      colorClasses = "bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800/60";
      label = status === "FAILED" ? "Failed" : "Rejected";
      break;
    case "READY":
      colorClasses = "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60 font-semibold";
      label = "Ready";
      break;
    case "STANDBY":
    case "NOT_TRIGGERED":
      colorClasses = "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700";
      label = "Standby";
      break;
    default:
      label = String(status);
  }

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full border shadow-xs transition-colors",
        sizeClasses,
        colorClasses,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-80" />
      {label}
    </span>
  );
};
