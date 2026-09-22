import React from "react";
import Link from "next/link";
import { Search, RefreshCw, Sun, Moon, Menu, Activity } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { useNavigation } from "./NavigationContext";
import { BrandBadge } from "./BrandingContext";

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  onMenuToggle?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onRefresh,
  isRefreshing,
  onMenuToggle,
}) => {
  const { theme, toggleTheme } = useTheme();
  const { toggleDrawer } = useNavigation();

  const handleMenuClick = onMenuToggle || toggleDrawer;

  const triggerCommandPalette = () => {
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", ctrlKey: true }));
  };

  return (
    <header className="no-print h-16 w-full border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 sm:px-6 md:px-8 flex items-center justify-between z-20 shrink-0 overflow-x-hidden transition-colors">
      {/* Left: Mobile Menu Trigger & Brand + Responsive Search */}
      <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0 mr-3">
        {/* Mobile Hamburger Menu (visible on mobile < md) */}
        <button
          type="button"
          onClick={handleMenuClick}
          aria-label="Open navigation menu"
          className="flex md:hidden p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 rounded-lg min-h-[44px] min-w-[44px] items-center justify-center transition-colors cursor-pointer shrink-0"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Mobile mini brand icon */}
        <div className="flex md:hidden shrink-0">
          <BrandBadge size="sm" />
        </div>

        {/* Fluid Responsive Search Bar / Command Palette Trigger */}
        <div
          onClick={triggerCommandPalette}
          className="relative flex-1 max-w-sm sm:max-w-md min-w-0 cursor-pointer group"
          title="Search claims or run commands (Ctrl+K)"
        >
          <Search className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none group-hover:text-blue-500 transition-colors" />
          <input
            type="text"
            readOnly
            placeholder="Search claims or run commands..."
            className="w-full bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-lg pl-9 pr-14 py-2 text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none group-hover:border-blue-500/50 transition-colors cursor-pointer"
          />
          <kbd className="hidden sm:inline-flex items-center absolute right-2.5 top-1/2 -translate-y-1/2 px-1.5 py-0.5 text-[10px] font-mono font-medium text-slate-400 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded shadow-xs pointer-events-none">
            Ctrl K
          </kbd>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
        {/* Quick Command Palette Button for touch/mobile */}
        <button
          onClick={triggerCommandPalette}
          aria-label="Open command palette"
          className="sm:hidden p-2 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 rounded-lg transition-colors cursor-pointer"
          title="Commands (Ctrl+K)"
        >
          <Search className="w-4 h-4" />
        </button>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="p-2 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-600 dark:text-slate-300 rounded-lg transition-colors cursor-pointer"
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-slate-700" />
          )}
        </button>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium rounded-lg transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-indigo-500" : ""}`}
            />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        )}

        <div className="h-4 w-px bg-slate-200 dark:border-slate-800 hidden sm:block" />

        {/* System Health link */}
        <Link
          href="/health"
          className="hidden md:flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
          title="Inspect Operational System Health"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <Activity className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
          <span className="text-xs text-slate-700 dark:text-slate-300 font-medium">System Health</span>
        </Link>
      </div>
    </header>
  );
};

