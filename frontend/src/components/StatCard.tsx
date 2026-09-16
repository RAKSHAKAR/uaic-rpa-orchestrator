"use client";

import React from "react";

export interface StatCardProps {
  title?: string;
  label?: string;
  value: string | number;
  subtitle?: string;
  subtext?: string;
  icon: React.ComponentType<{ className?: string }>;
  colorGradient?: string;
  gradient?: string;
  color?: string;
  badgeColor?: string;
  onClick?: () => void;
  isSelected?: boolean;
  selected?: boolean;
  badge?: string;
  className?: string;
}

const COLOR_TOKEN_MAP: Record<string, string> = {
  emerald: "from-emerald-500/20 to-teal-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800",
  green: "from-emerald-500/20 to-teal-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800",
  rose: "from-rose-500/20 to-red-500/20 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-800",
  red: "from-rose-500/20 to-red-500/20 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-800",
  amber: "from-amber-500/20 to-orange-500/20 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800",
  yellow: "from-amber-500/20 to-yellow-500/20 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800",
  orange: "from-amber-500/20 to-orange-500/20 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-800",
  sky: "from-sky-500/20 to-blue-500/20 text-sky-600 dark:text-sky-400 border-sky-200 dark:border-sky-800",
  cyan: "from-cyan-500/20 to-blue-500/20 text-cyan-600 dark:text-cyan-400 border-cyan-200 dark:border-cyan-800",
  blue: "from-blue-500/20 to-indigo-500/20 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800",
  purple: "from-purple-500/20 to-pink-500/20 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800",
  indigo: "from-indigo-500/20 to-purple-500/20 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800",
};

export function StatCard({
  title,
  label,
  value,
  subtitle,
  subtext,
  icon: Icon,
  colorGradient,
  gradient,
  color,
  badgeColor,
  onClick,
  isSelected,
  selected,
  badge,
  className = "",
}: StatCardProps) {
  const isClickable = !!onClick;
  const displayTitle = title || label || "";
  const displaySubtitle = subtitle || subtext;
  const isSelectedCard = isSelected ?? selected ?? false;

  const rawToken = gradient || colorGradient || color || "indigo";
  const resolvedGradient =
    COLOR_TOKEN_MAP[rawToken.toLowerCase()] ||
    (rawToken.includes("from-")
      ? `${rawToken} border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400`
      : COLOR_TOKEN_MAP.indigo);

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-slate-900/60 border rounded-xl p-3.5 sm:p-4 flex flex-col justify-between space-y-2.5 shadow-xs transition-all ${
        isSelectedCard
          ? "border-indigo-500 ring-2 ring-indigo-500/20 bg-indigo-50/20 dark:bg-indigo-950/30"
          : "border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700"
      } ${
        isClickable ? "cursor-pointer hover:shadow-md hover:-translate-y-0.5" : ""
      } ${className}`}
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 truncate">
          {displayTitle}
        </span>
        <div
          className={`w-7 h-7 rounded-lg bg-gradient-to-br ${resolvedGradient} border flex items-center justify-center shrink-0`}
        >
          <Icon className="w-3.5 h-3.5" />
        </div>
      </div>

      <div className="space-y-0.5">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight font-mono">
            {value}
          </span>
          {badge && (
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-mono">
              {badge}
            </span>
          )}
        </div>
        {displaySubtitle && (
          <p className="text-[10px] text-slate-400 dark:text-slate-500 font-medium truncate">
            {displaySubtitle}
          </p>
        )}
      </div>
    </div>
  );
}
