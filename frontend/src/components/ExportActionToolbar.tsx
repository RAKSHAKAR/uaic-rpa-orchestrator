"use client";

import React from "react";
import {
  FileSpreadsheet,
  FileText,
  FileCode,
  FileType,
  Layers,
  Loader2,
} from "lucide-react";

export interface ExportActionToolbarProps {
  onExport?: (format: "xlsx" | "csv" | "json" | "pdf") => void | Promise<void>;
  onExportXlsx?: () => void | Promise<void>;
  onExportCsv?: () => void | Promise<void>;
  onExportJson?: () => void | Promise<void>;
  onExportPdf?: () => void | Promise<void>;
  onOpenAsyncModal?: () => void;
  showPdf?: boolean;
  showAsyncButton?: boolean;
  isExporting?: boolean;
  activeFormat?: "xlsx" | "csv" | "json" | "pdf" | "async" | null;
  disabled?: boolean;
  className?: string;
  compact?: boolean;
  label?: string;
}

export function ExportActionToolbar({
  onExport,
  onExportXlsx,
  onExportCsv,
  onExportJson,
  onExportPdf,
  onOpenAsyncModal,
  showPdf = true,
  showAsyncButton = true,
  isExporting = false,
  activeFormat = null,
  disabled = false,
  className = "",
  compact = false,
  label = "Export",
}: ExportActionToolbarProps) {
  const btnBaseClass = compact
    ? "px-2.5 py-1.5 text-xs font-medium rounded-lg inline-flex items-center gap-1.5 transition-all shadow-xs cursor-pointer"
    : "px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg inline-flex items-center gap-2 transition-all shadow-xs cursor-pointer";

  const handleXlsx = onExportXlsx || (onExport ? () => onExport("xlsx") : undefined);
  const handleCsv = onExportCsv || (onExport ? () => onExport("csv") : undefined);
  const handleJson = onExportJson || (onExport ? () => onExport("json") : undefined);
  const handlePdf = (showPdf && (onExportPdf || (onExport ? () => onExport("pdf") : undefined))) || undefined;

  return (
    <div className={`flex flex-wrap items-center gap-1.5 sm:gap-2 ${className}`}>
      {label && (
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 mr-1 hidden sm:inline">
          {label}:
        </span>
      )}

      {/* Quick Excel Export */}
      {handleXlsx && (
        <button
          type="button"
          onClick={handleXlsx}
          disabled={disabled || isExporting}
          title="Download formatted Excel spreadsheet (.xlsx)"
          className={`${btnBaseClass} bg-emerald-50 text-emerald-700 border border-emerald-200/80 hover:bg-emerald-100 hover:border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60 dark:hover:bg-emerald-900/50 disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isExporting && activeFormat === "xlsx" ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          )}
          <span>Excel</span>
        </button>
      )}

      {/* Quick CSV Export */}
      {handleCsv && (
        <button
          type="button"
          onClick={handleCsv}
          disabled={disabled || isExporting}
          title="Download standard comma-separated values (.csv)"
          className={`${btnBaseClass} bg-sky-50 text-sky-700 border border-sky-200/80 hover:bg-sky-100 hover:border-sky-300 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800/60 dark:hover:bg-sky-900/50 disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isExporting && activeFormat === "csv" ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FileText className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
          )}
          <span>CSV</span>
        </button>
      )}

      {/* Quick JSON Export */}
      {handleJson && (
        <button
          type="button"
          onClick={handleJson}
          disabled={disabled || isExporting}
          title="Download complete structured raw JSON (.json)"
          className={`${btnBaseClass} bg-amber-50 text-amber-700 border border-amber-200/80 hover:bg-amber-100 hover:border-amber-300 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60 dark:hover:bg-amber-900/50 disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isExporting && activeFormat === "json" ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FileCode className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
          )}
          <span>JSON</span>
        </button>
      )}

      {/* Quick PDF Export */}
      {handlePdf && (
        <button
          type="button"
          onClick={handlePdf}
          disabled={disabled || isExporting}
          title="Download printable enterprise PDF dossier (.pdf)"
          className={`${btnBaseClass} bg-rose-50 text-rose-700 border border-rose-200/80 hover:bg-rose-100 hover:border-rose-300 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800/60 dark:hover:bg-rose-900/50 disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isExporting && activeFormat === "pdf" ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FileType className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />
          )}
          <span>PDF</span>
        </button>
      )}

      {/* Background Async Export Modal Trigger */}
      {showAsyncButton && onOpenAsyncModal && (
        <button
          type="button"
          onClick={onOpenAsyncModal}
          disabled={disabled || isExporting}
          title="Configure background asynchronous batch export with live progress tracking"
          className={`${btnBaseClass} bg-indigo-50 text-indigo-700 border border-indigo-200/80 hover:bg-indigo-100 hover:border-indigo-300 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800/60 dark:hover:bg-indigo-900/50 disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <Layers className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
          <span>Background Export</span>
        </button>
      )}
    </div>
  );
}
