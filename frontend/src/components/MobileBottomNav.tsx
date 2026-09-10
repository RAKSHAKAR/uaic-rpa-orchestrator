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
} from "lucide-react";
import { cn } from "../lib/utils";

const mobileDestinations = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Upload", href: "/upload", icon: UploadCloud },
  { name: "Queue", href: "/monitor", icon: Layers },
  { name: "Exceptions", href: "/exceptions", icon: AlertTriangle },
  { name: "Settings", href: "/settings", icon: Sliders },
];

export const MobileBottomNav: React.FC = () => {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Mobile Navigation Bar"
      className="fixed bottom-0 inset-x-0 z-40 md:hidden bg-white/95 dark:bg-slate-950/95 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800/90 shadow-lg shadow-black/10 transition-colors"
      style={{ paddingBottom: "max(0.35rem, env(safe-area-inset-bottom, 0px))" }}
    >
      <div className="grid grid-cols-5 items-center w-full px-1">
        {mobileDestinations.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex flex-col items-center justify-center py-2 px-1 min-h-[52px] rounded-lg transition-all select-none",
                isActive
                  ? "text-indigo-600 dark:text-indigo-400 font-semibold"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 active:scale-95"
              )}
            >
              <div className="relative">
                <Icon
                  className={cn(
                    "w-5 h-5 transition-transform",
                    isActive && "scale-110"
                  )}
                />
                {isActive && (
                  <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
                )}
              </div>
              <span className="text-[10px] mt-1 tracking-tight truncate max-w-full">
                {item.name}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
