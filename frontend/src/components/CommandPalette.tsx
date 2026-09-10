"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  PlusCircle,
  Upload,
  Download,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Activity,
  X,
  FileSpreadsheet,
  CornerDownLeft,
  LayoutDashboard,
  ShieldAlert,
  Palette,
  ScrollText,
} from "lucide-react";
import { api } from "../lib/api";

interface CommandItem {
  id: string;
  title: string;
  description: string;
  category: "Navigation" | "Queue & Automation" | "Data & Records";
  icon: React.ElementType;
  shortcut?: string;
  action: () => void | Promise<void>;
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  const commands: CommandItem[] = [
    // Navigation
    {
      id: "nav-records",
      title: "Search Records",
      description: "Jump to Claims Dashboard and filter records",
      category: "Navigation",
      icon: LayoutDashboard,
      shortcut: "G D",
      action: () => {
        router.push("/");
        setIsOpen(false);
      },
    },
    {
      id: "nav-health",
      title: "Open System Health",
      description: "Inspect live health of API, Redis, Celery, Chrome, & 8 Portals",
      category: "Navigation",
      icon: Activity,
      shortcut: "G H",
      action: () => {
        router.push("/health");
        setIsOpen(false);
      },
    },
    {
      id: "nav-audit",
      title: "Open Audit Trail",
      description: "Inspect solution-wide immutable audit trail, operator actions, & data lineage",
      category: "Navigation",
      icon: ScrollText,
      shortcut: "G A",
      action: () => {
        router.push("/audit");
        setIsOpen(false);
      },
    },
    {
      id: "nav-settings",
      title: "Open Settings",
      description: "Manage Portals, CAPTCHA, Browser, Matching, & Guidewire",
      category: "Navigation",
      icon: Settings,
      shortcut: "G S",
      action: () => {
        router.push("/settings");
        setIsOpen(false);
      },
    },
    {
      id: "nav-branding",
      title: "Open Brand & Identity",
      description: "Customize solution title, subtitle, logo icon, and monogram",
      category: "Navigation",
      icon: Palette,
      shortcut: "G B",
      action: () => {
        router.push("/branding");
        setIsOpen(false);
      },
    },
    {
      id: "nav-monitor",
      title: "Open Queue Monitor",
      description: "Real-time task queue monitor and worker diagnostics",
      category: "Navigation",
      icon: Play,
      shortcut: "G M",
      action: () => {
        router.push("/monitor");
        setIsOpen(false);
      },
    },
    {
      id: "nav-exceptions",
      title: "Open Exceptions & Fuzzy Review",
      description: "Review borderline and pending fuzzy match candidates",
      category: "Navigation",
      icon: ShieldAlert,
      shortcut: "G E",
      action: () => {
        router.push("/exceptions");
        setIsOpen(false);
      },
    },

    // Queue & Automation
    {
      id: "queue-start",
      title: "Start Queue",
      description: "Begin sequential processing of all pending claims",
      category: "Queue & Automation",
      icon: Play,
      action: async () => {
        try {
          await api.startAllQueue();
        } catch (e) {
          console.error("Queue start error:", e);
        }
        router.push("/monitor");
        setIsOpen(false);
      },
    },
    {
      id: "queue-pause",
      title: "Pause Queue",
      description: "Halt automatic progression of the queue runner",
      category: "Queue & Automation",
      icon: Pause,
      action: async () => {
        try {
          await api.pauseQueue();
        } catch (e) {
          console.error("Queue pause error:", e);
        }
        setIsOpen(false);
      },
    },
    {
      id: "queue-retry",
      title: "Retry Failed Records",
      description: "Re-queue all claims with FAILED or stuck status",
      category: "Queue & Automation",
      icon: RotateCcw,
      action: async () => {
        try {
          await api.retriggerClaims();
        } catch (e) {
          console.error("Retry failed error:", e);
        }
        router.push("/monitor");
        setIsOpen(false);
      },
    },

    // Data & Records
    {
      id: "data-create",
      title: "Create Record",
      description: "Manually input a new claim record with routing targets",
      category: "Data & Records",
      icon: PlusCircle,
      action: () => {
        router.push("/monitor?action=create");
        setIsOpen(false);
      },
    },
    {
      id: "data-import-excel",
      title: "Import Excel / XLSX",
      description: "Upload Excel spreadsheet with 1899 serial date conversion",
      category: "Data & Records",
      icon: FileSpreadsheet,
      action: () => {
        router.push("/upload");
        setIsOpen(false);
      },
    },
    {
      id: "data-import-csv",
      title: "Import CSV",
      description: "Upload comma-separated values claims file",
      category: "Data & Records",
      icon: Upload,
      action: () => {
        router.push("/upload");
        setIsOpen(false);
      },
    },
    {
      id: "data-export",
      title: "Export Records (Excel / CSV)",
      description: "Download filtered or selected records with portal outputs",
      category: "Data & Records",
      icon: Download,
      action: () => {
        router.push("/monitor?action=export");
        setIsOpen(false);
      },
    },
  ];

  // Filter commands by query
  const filteredCommands = commands.filter((cmd) => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    return (
      cmd.title.toLowerCase().includes(q) ||
      cmd.description.toLowerCase().includes(q) ||
      cmd.category.toLowerCase().includes(q)
    );
  });

  // Global keydown listener for Ctrl+K, Cmd+K, Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape" && isOpen) {
        e.preventDefault();
        setIsOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Keyboard navigation within palette
  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (filteredCommands.length || 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % (filteredCommands.length || 1));
    } else if (e.key === "Enter" && filteredCommands[selectedIndex]) {
      e.preventDefault();
      filteredCommands[selectedIndex].action();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh] animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Bar */}
        <div className="relative flex items-center border-b border-slate-200 dark:border-slate-800 px-4 py-3">
          <Search className="w-5 h-5 text-slate-400 mr-3 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or search action (e.g. Health, Queue, Export)..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleInputKeyDown}
            className="w-full bg-transparent text-slate-900 dark:text-slate-100 placeholder-slate-400 text-base focus:outline-none"
          />
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ml-2"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Command Items List */}
        <div className="overflow-y-auto p-2 space-y-1 divide-y divide-slate-100 dark:divide-slate-800/60">
          {filteredCommands.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              No actions found matching <span className="font-semibold text-slate-600 dark:text-slate-300">&ldquo;{query}&rdquo;</span>
            </div>
          ) : (

            filteredCommands.map((cmd, index) => {
              const Icon = cmd.icon;
              const isSelected = index === selectedIndex;
              return (
                <div
                  key={cmd.id}
                  onClick={() => cmd.action()}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                    isSelected
                      ? "bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300"
                      : "text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <div
                      className={`p-2 rounded-md shrink-0 ${
                        isSelected
                          ? "bg-blue-100 dark:bg-blue-900/60 text-blue-600 dark:text-blue-300"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <div className="font-medium text-sm text-slate-900 dark:text-slate-100 truncate">
                        {cmd.title}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                        {cmd.description}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0 ml-3">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                      {cmd.category}
                    </span>
                    {isSelected && (
                      <CornerDownLeft className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info & keyboard shortcuts */}
        <div className="flex items-center justify-between px-4 py-2 bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center space-x-3">
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono text-[10px] text-slate-700 dark:text-slate-300">↑</kbd>{" "}
              <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono text-[10px] text-slate-700 dark:text-slate-300">↓</kbd> to navigate
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono text-[10px] text-slate-700 dark:text-slate-300">↵</kbd> to select
            </span>
          </div>
          <div>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono text-[10px] text-slate-700 dark:text-slate-300">ESC</kbd> to close
          </div>
        </div>
      </div>
    </div>
  );
}
