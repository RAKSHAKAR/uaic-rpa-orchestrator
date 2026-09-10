"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  UploadCloud,
  Layers,
  AlertTriangle,
  Sliders,
  Activity,
  Palette,
  ScrollText,
} from "lucide-react";
import { cn } from "../lib/utils";
import { useBranding, BrandBadge } from "./BrandingContext";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Upload & Ingest", href: "/upload", icon: UploadCloud },
  { name: "Queue Monitor", href: "/monitor", icon: Layers },
  { name: "System Health", href: "/health", icon: Activity },
  { name: "Audit Trail", href: "/audit", icon: ScrollText },
  { name: "Exception Review", href: "/exceptions", icon: AlertTriangle },
  { name: "Automation Settings", href: "/settings", icon: Sliders },
  { name: "Brand & Identity", href: "/branding", icon: Palette },
];


export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { branding } = useBranding();

  return (
    <aside className="flex flex-col h-full w-56 lg:w-64 bg-white dark:bg-slate-950 shrink-0 select-none transition-colors">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800/80 gap-3">
          <BrandBadge size="md" />
          <div className="min-w-0 flex-1">
            <h1 className="text-sm font-semibold text-slate-900 dark:text-slate-100 tracking-tight truncate">
              {branding.app_title}
            </h1>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium truncate">
              {branding.app_subtitle}
            </p>
          </div>
        </div>

        {/* Navigation links */}
        <div className="p-3 space-y-1">
          <div className="px-3 py-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Main Navigation
          </div>
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all",
                  isActive
                    ? "bg-indigo-50 dark:bg-indigo-600/15 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30 font-semibold shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900/60"
                )}
              >
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive
                      ? "text-indigo-600 dark:text-indigo-400"
                      : "text-slate-400 dark:text-slate-500"
                  )}
                />
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>
    </aside>
  );
};
