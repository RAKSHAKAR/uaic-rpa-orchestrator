"use client";

import React, { useState, useEffect } from "react";
import {
  Bookmark,
  Plus,
  Trash2,
  Check,
  RotateCcw,
  Sparkles,
  X,
} from "lucide-react";

export interface FilterPreset {
  id: string;
  name: string;
  isSystem?: boolean;
  status?: string;
  state?: string;
  search?: string;
}

interface FilterPresetManagerProps {
  currentStatus: string;
  currentState: string;
  currentSearch: string;
  onApplyPreset: (preset: { status: string; state: string; search: string }) => void;
  onResetFilters: () => void;
}

const SYSTEM_PRESETS: FilterPreset[] = [
  { id: "sys-all", name: "All Claims", isSystem: true, status: "", state: "", search: "" },
  { id: "sys-review", name: "Needs Review", isSystem: true, status: "MANUAL_REVIEW" },
  { id: "sys-failed", name: "Failed Portals", isSystem: true, status: "FAILED" },
  { id: "sys-in-progress", name: "In Progress", isSystem: true, status: "SCRAPING_IN_PROGRESS" },
  { id: "sys-matched", name: "Match Found", isSystem: true, status: "MATCH_FOUND" },
  { id: "sys-fl", name: "Florida (FL)", isSystem: true, state: "FL" },
  { id: "sys-tx", name: "Texas (TX)", isSystem: true, state: "TX" },
];

const STORAGE_KEY = "uaic_filter_presets_v1";

export function FilterPresetManager({
  currentStatus,
  currentState,
  currentSearch,
  onApplyPreset,
  onResetFilters,
}: FilterPresetManagerProps) {
  const [customPresets, setCustomPresets] = useState<FilterPreset[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newPresetName, setNewPresetName] = useState("");
  const [activePresetId, setActivePresetId] = useState<string | null>(null);

  // Load custom presets from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setCustomPresets(JSON.parse(stored));
      }
    } catch {
      // ignore
    }
  }, []);

  // Sync active preset ID
  useEffect(() => {
    const allPresets = [...SYSTEM_PRESETS, ...customPresets];
    const match = allPresets.find(
      (p) =>
        (p.status ?? "") === currentStatus &&
        (p.state ?? "") === currentState &&
        (p.search ?? "") === currentSearch
    );
    setActivePresetId(match ? match.id : null);
  }, [currentStatus, currentState, currentSearch, customPresets]);

  const saveCustomPreset = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPresetName.trim()) return;

    const newPreset: FilterPreset = {
      id: `custom-${Date.now()}`,
      name: newPresetName.trim(),
      status: currentStatus,
      state: currentState,
      search: currentSearch,
    };

    const updated = [...customPresets, newPreset];
    setCustomPresets(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch {
      // ignore
    }

    setNewPresetName("");
    setIsModalOpen(false);
    setActivePresetId(newPreset.id);
  };

  const deleteCustomPreset = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = customPresets.filter((p) => p.id !== id);
    setCustomPresets(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch {
      // ignore
    }
    if (activePresetId === id) setActivePresetId(null);
  };

  const hasActiveFilter = Boolean(currentStatus || currentState || currentSearch);

  return (
    <div className="flex flex-wrap items-center gap-1.5 py-1 text-xs w-full">
      <div className="flex items-center gap-1 text-slate-400 dark:text-slate-500 font-semibold mr-1 shrink-0">
        <Bookmark className="w-3.5 h-3.5 text-indigo-500" />
        <span className="text-[11px] uppercase tracking-wider">Presets:</span>
      </div>

      {/* Preset Chips */}
      <div className="flex items-center gap-1.5 flex-wrap flex-1">
        {SYSTEM_PRESETS.map((p) => {
          const isActive = activePresetId === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onApplyPreset({ status: p.status || "", state: p.state || "", search: p.search || "" })}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1 cursor-pointer ${
                isActive
                  ? "bg-indigo-600 text-white shadow-xs font-semibold"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200/80 dark:border-slate-700/80"
              }`}
            >
              {isActive && <Check className="w-3 h-3 text-white" />}
              <span>{p.name}</span>
            </button>
          );
        })}

        {/* Custom Presets */}
        {customPresets.map((p) => {
          const isActive = activePresetId === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onApplyPreset({ status: p.status || "", state: p.state || "", search: p.search || "" })}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer ${
                isActive
                  ? "bg-amber-600 text-white shadow-xs font-semibold"
                  : "bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900/60 border border-amber-200 dark:border-amber-800"
              }`}
            >
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span>{p.name}</span>
              <span
                onClick={(e) => deleteCustomPreset(p.id, e)}
                className="hover:text-rose-500 p-0.5 rounded cursor-pointer transition-colors"
                title="Delete preset"
              >
                <Trash2 className="w-2.5 h-2.5" />
              </span>
            </button>
          );
        })}

        {/* Save Current Preset Button */}
        {hasActiveFilter && (
          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="px-2 py-1 bg-white dark:bg-slate-900 border border-dashed border-indigo-300 dark:border-indigo-700 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
            title="Save current filters as named preset"
          >
            <Plus className="w-3 h-3" />
            <span>Save View</span>
          </button>
        )}

        {/* Reset / Clear Button */}
        {hasActiveFilter && (
          <button
            type="button"
            onClick={onResetFilters}
            className="px-2 py-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs flex items-center gap-1 transition-colors cursor-pointer"
            title="Clear all active filters"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Save Preset Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-sm w-full p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-1.5">
                <Bookmark className="w-4 h-4 text-indigo-600" />
                Save Filter Preset (§83)
              </h4>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={saveCustomPreset} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Preset Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Dallas Pending Review"
                  value={newPresetName}
                  onChange={(e) => setNewPresetName(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden focus:border-indigo-500"
                  autoFocus
                />
              </div>

              <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg text-[11px] text-slate-600 dark:text-slate-400 space-y-0.5">
                <div className="font-semibold text-slate-700 dark:text-slate-300">Saved criteria:</div>
                {currentStatus && <div>Status: <span className="font-mono">{currentStatus}</span></div>}
                {currentState && <div>State: <span className="font-mono">{currentState}</span></div>}
                {currentSearch && <div>Search: <span className="font-mono">{currentSearch}</span></div>}
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg shadow-sm"
                >
                  Save Preset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
