"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  X,
  LayoutDashboard,
  UploadCloud,
  Layers,
  AlertTriangle,
  Sliders,
  Activity,
  FileSpreadsheet,
  Palette,
  ScrollText,
  Sun,
  Moon,
} from "lucide-react";
import { cn } from "../lib/utils";
import { useBranding, BrandBadge } from "./BrandingContext";
import { useTheme } from "./ThemeProvider";

interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Upload & Ingest", href: "/upload", icon: UploadCloud },
  { name: "Queue Monitor", href: "/monitor", icon: Layers },
  { name: "System Health", href: "/health", icon: Activity },
  { name: "Audit Trail", href: "/audit", icon: ScrollText },
  { name: "Exception Review", href: "/exceptions", icon: AlertTriangle },
  { name: "Automation Settings", href: "/settings", icon: Sliders },
  { name: "Brand & Identity", href: "/branding", icon: Palette },
];


export const MobileDrawer: React.FC<MobileDrawerProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();
  const { branding } = useBranding();
  const { theme, setTheme } = useTheme();

  // Close drawer on escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 md:hidden flex">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-over Content */}
      <div className="relative w-4/5 max-w-xs h-full bg-white dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between shadow-2xl z-10 animate-in slide-in-from-left duration-200">
        <div>
          {/* Header */}
          <div className="h-16 flex items-center justify-between px-5 border-b border-slate-200 dark:border-slate-800/80">
            <div className="flex items-center gap-2.5 min-w-0">
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
            <button
              onClick={onClose}
              aria-label="Close navigation menu"
              className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-900 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <div className="px-3 py-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              Navigation
            </div>
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all",
                    isActive
                      ? "bg-indigo-50 dark:bg-indigo-600/15 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30 font-semibold"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900/60"
                  )}
                >
                  <Icon
                    className={cn(
                      "w-4 h-4",
                      isActive
                        ? "text-indigo-600 dark:text-indigo-400"
                        : "text-slate-400 dark:text-slate-500"
                    )}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Theme Switcher & Engine Status & Footer */}
        <div className="mt-auto shrink-0 p-4 border-t border-slate-200 dark:border-slate-800/80 space-y-3">
          {/* Dual Theme Switcher */}
          <div className="flex items-center justify-between p-1 bg-slate-100 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
            <button
              type="button"
              onClick={() => setTheme("light")}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer",
                theme === "light"
                  ? "bg-white text-indigo-600 shadow-xs dark:bg-slate-800 dark:text-amber-400"
                  : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
              )}
            >
              <Sun className="w-3.5 h-3.5 text-amber-500" />
              <span>Light</span>
            </button>
            <button
              type="button"
              onClick={() => setTheme("dark")}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer",
                theme === "dark"
                  ? "bg-slate-900 text-indigo-400 shadow-xs dark:bg-indigo-600 dark:text-white"
                  : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
              )}
            >
              <Moon className="w-3.5 h-3.5 text-indigo-400" />
              <span>Dark</span>
            </button>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900/80 rounded-xl p-3 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-600 dark:text-slate-400 font-medium flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-500" />
                Engine Status
              </span>
              <span className="inline-flex items-center text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
                Active
              </span>
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 space-y-0.5 font-mono">
              <div className="flex justify-between">
                <span>Celery Workers</span>
                <span className="text-slate-700 dark:text-slate-300">4 Online</span>
              </div>
              <div className="flex justify-between">
                <span>County Bots</span>
                <span className="text-slate-700 dark:text-slate-300">8 Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
