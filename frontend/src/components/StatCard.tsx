"use client";

import React from "react";

export interface AnimatedNumberProps {
  value: string | number;
  duration?: number;
  className?: string;
}

export function AnimatedNumber({
  value,
  duration = 800,
  className = "",
}: AnimatedNumberProps) {
  const [displayValue, setDisplayValue] = React.useState<string | number>(value);
  const [hasMounted, setHasMounted] = React.useState(false);
  const prevNumRef = React.useRef<number | null>(null);

  React.useEffect(() => {
    setHasMounted(true);
  }, []);

  React.useEffect(() => {
    if (!hasMounted) return;

    let num: number;
    let decimals = 0;
    let prefix = "";
    let suffix = "";

    if (typeof value === "number") {
      num = value;
      decimals = Number.isInteger(value) ? 0 : 2;
    } else {
      const str = String(value).trim();
      const match = str.match(/^([^0-9.-]*)([0-9]+(?:\.[0-9]+)?)(.*)$/);
      if (!match) {
        setDisplayValue(value);
        return;
      }
      prefix = match[1] || "";
      const numStr = match[2];
      suffix = match[3] || "";
      num = parseFloat(numStr);
      if (isNaN(num)) {
        setDisplayValue(value);
        return;
      }
      decimals = numStr.includes(".") ? numStr.split(".")[1].length : 0;
    }

    const startNum = prevNumRef.current !== null ? prevNumRef.current : 0;
    prevNumRef.current = num;

    if (startNum === num) {
      const formatted = `${prefix}${num.toFixed(decimals)}${suffix}`;
      setDisplayValue(formatted);
      return;
    }

    let startTimestamp: number | null = null;
    let animId: number;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // Cubic ease-out curve for natural deceleration
      const ease = 1 - Math.pow(1 - progress, 3);
      const currentVal = startNum + (num - startNum) * ease;
      const formatted = `${prefix}${currentVal.toFixed(decimals)}${suffix}`;
      setDisplayValue(formatted);

      if (progress < 1) {
        animId = requestAnimationFrame(step);
      } else {
        setDisplayValue(`${prefix}${num.toFixed(decimals)}${suffix}`);
      }
    };

    animId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animId);
  }, [value, duration, hasMounted]);

  return <span className={className}>{displayValue}</span>;
}

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
  emerald: "from-emerald-500/20 to-teal-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800 shadow-emerald-500/10",
  green: "from-emerald-500/20 to-teal-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800 shadow-emerald-500/10",
  rose: "from-rose-500/20 to-red-500/20 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-800 shadow-rose-500/10",
  red: "from-rose-500/20 to-red-500/20 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-800 shadow-rose-500/10",
  amber: "from-amber-500/20 to-orange-500/20 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800 shadow-amber-500/10",
  yellow: "from-amber-500/20 to-yellow-500/20 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800 shadow-amber-500/10",
  orange: "from-amber-500/20 to-orange-500/20 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-800 shadow-orange-500/10",
  sky: "from-sky-500/20 to-blue-500/20 text-sky-600 dark:text-sky-400 border-sky-200 dark:border-sky-800 shadow-sky-500/10",
  cyan: "from-cyan-500/20 to-blue-500/20 text-cyan-600 dark:text-cyan-400 border-cyan-200 dark:border-cyan-800 shadow-cyan-500/10",
  blue: "from-blue-500/20 to-indigo-500/20 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800 shadow-blue-500/10",
  purple: "from-purple-500/20 to-pink-500/20 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800 shadow-purple-500/10",
  indigo: "from-indigo-500/20 to-purple-500/20 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800 shadow-indigo-500/10",
};

function StatCardComponent({
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
      ? `${rawToken} border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 shadow-indigo-500/10`
      : COLOR_TOKEN_MAP.indigo);

  return (
    <div
      onClick={onClick}
      className={`group bg-white dark:bg-slate-900/60 border rounded-xl p-3.5 sm:p-4 flex flex-col justify-between space-y-2.5 shadow-xs transition-all duration-300 ease-out ${
        isSelectedCard
          ? "border-indigo-500 ring-2 ring-indigo-500/20 bg-indigo-50/20 dark:bg-indigo-950/30 shadow-md shadow-indigo-500/10"
          : "border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-md"
      } ${
        isClickable ? "cursor-pointer hover:-translate-y-1 hover:shadow-lg" : ""
      } ${className}`}
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 truncate group-hover:text-slate-700 dark:group-hover:text-slate-200 transition-colors">
          {displayTitle}
        </span>
        <div
          className={`w-7 h-7 rounded-lg bg-gradient-to-br ${resolvedGradient} border flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform duration-300`}
        >
          <Icon className="w-3.5 h-3.5" />
        </div>
      </div>

      <div className="space-y-0.5">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight font-mono">
            <AnimatedNumber value={value} />
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

export const StatCard = React.memo(StatCardComponent);
