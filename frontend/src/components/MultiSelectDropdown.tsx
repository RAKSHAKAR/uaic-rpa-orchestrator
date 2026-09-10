"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, X, Search } from "lucide-react";

export interface MultiSelectOption {
  value: string;
  label: string;
  count?: number;
}

interface MultiSelectDropdownProps {
  label: string;
  options: MultiSelectOption[];
  selectedValues: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function MultiSelectDropdown({
  label,
  options,
  selectedValues,
  onChange,
  placeholder = "Select options...",
  className = "",
  disabled = false,
}: MultiSelectDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredOptions = options.filter((opt) =>
    opt.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    opt.value.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const isAllSelected = options.length > 0 && selectedValues.length === options.length;

  const toggleOption = (val: string) => {
    if (selectedValues.includes(val)) {
      onChange(selectedValues.filter((v) => v !== val));
    } else {
      onChange([...selectedValues, val]);
    }
  };

  const handleSelectAll = () => {
    if (isAllSelected) {
      onChange([]);
    } else {
      onChange(options.map((opt) => opt.value));
    }
  };

  const handleClearAll = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange([]);
  };

  return (
    <div className={`relative w-full ${className}`} ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-800 dark:text-slate-200 hover:border-slate-300 dark:hover:border-slate-700 focus:outline-hidden focus:border-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer text-left shadow-2xs"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-1.5 truncate flex-1">
          <span className="text-slate-400 dark:text-slate-500 font-medium">{label}:</span>
          {selectedValues.length === 0 ? (
            <span className="text-slate-500 dark:text-slate-400 italic truncate">
              {placeholder}
            </span>
          ) : selectedValues.length === 1 ? (
            <span className="font-semibold text-slate-900 dark:text-slate-100 truncate">
              {options.find((o) => o.value === selectedValues[0])?.label || selectedValues[0]}
            </span>
          ) : isAllSelected ? (
            <span className="px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 font-bold font-mono text-[10px]">
              All ({options.length})
            </span>
          ) : (
            <span className="px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 font-bold font-mono text-[10px]">
              {selectedValues.length} selected
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {selectedValues.length > 0 && (
            <span
              onClick={handleClearAll}
              className="p-0.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded hover:bg-slate-200 dark:hover:bg-slate-800 cursor-pointer"
              title="Clear selections"
            >
              <X className="w-3 h-3" />
            </span>
          )}
          <ChevronDown
            className={`w-3.5 h-3.5 text-slate-400 transition-transform ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full min-w-[200px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl overflow-hidden py-1.5 animate-in fade-in zoom-in-95 duration-100">
          {/* Quick Search */}
          {options.length > 5 && (
            <div className="px-2 pb-1.5 border-b border-slate-100 dark:border-slate-800">
              <div className="relative">
                <Search className="w-3 h-3 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search values..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-7 pr-2 py-1 text-xs bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-md text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-hidden focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {/* Quick Action Bar: Select All / Clear */}
          <div className="flex items-center justify-between px-3 py-1.5 border-b border-slate-100 dark:border-slate-800 text-[11px] font-semibold">
            <button
              type="button"
              onClick={handleSelectAll}
              className="text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer"
            >
              {isAllSelected ? "Deselect All" : "Select All"}
            </button>
            {selectedValues.length > 0 && (
              <button
                type="button"
                onClick={() => onChange([])}
                className="text-slate-400 hover:text-rose-500 cursor-pointer"
              >
                Reset
              </button>
            )}
          </div>

          {/* Options List */}
          <div className="max-h-56 overflow-y-auto py-1">
            {filteredOptions.length === 0 ? (
              <div className="px-3 py-3 text-center text-xs text-slate-400">
                No matching options found
              </div>
            ) : (
              filteredOptions.map((opt) => {
                const isSelected = selectedValues.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => toggleOption(opt.value)}
                    className={`w-full flex items-center justify-between px-3 py-1.5 text-xs text-left cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200 font-medium"
                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/70"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <div
                        className={`w-3.5 h-3.5 rounded border flex items-center justify-center transition-colors ${
                          isSelected
                            ? "bg-indigo-600 border-indigo-600 text-white"
                            : "border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900"
                        }`}
                      >
                        {isSelected && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                      </div>
                      <span className="truncate">{opt.label}</span>
                    </div>

                    {opt.count !== undefined && (
                      <span className="text-[10px] font-mono text-slate-400 ml-2">
                        ({opt.count})
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
