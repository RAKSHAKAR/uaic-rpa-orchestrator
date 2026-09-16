"use client";

import React, { useState, useEffect } from "react";
import {
  FileSpreadsheet,
  FileText,
  FileCode,
  Download,
  Loader2,
  CheckCircle2,
  AlertCircle,
  X,
  Clock,
  HardDrive,
} from "lucide-react";
import { api } from "../lib/api";

interface AsyncExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  statusFilter?: string;
  stateFilter?: string;
  searchTerm?: string;
  selectedIds?: string[];
  totalRecordsCount?: number;
}

export function AsyncExportModal({
  isOpen,
  onClose,
  statusFilter,
  stateFilter,
  searchTerm,
  selectedIds,
  totalRecordsCount,
}: AsyncExportModalProps) {
  const [format, setFormat] = useState<"xlsx" | "csv" | "json">("xlsx");
  const [isProcessing, setIsProcessing] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progressPercent, setProgressPercent] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [completedResult, setCompletedResult] = useState<{
    filename: string;
    totalRows: number;
    fileSize: number;
    downloadUrl: string;
  } | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) {
      setIsProcessing(false);
      setTaskId(null);
      setProgressPercent(0);
      setStatusMessage("");
      setCompletedResult(null);
      setErrorMessage(null);
    }
  }, [isOpen]);

  // Polling loop when taskId is active
  useEffect(() => {
    if (!taskId || !isProcessing) return;

    const interval = setInterval(async () => {
      try {
        const res = await api.getAsyncExportStatus(taskId);
        if (res.status === "PROGRESS") {
          setProgressPercent(res.percent || 45);
          setStatusMessage(res.message || "Generating export dataset...");
        } else if (res.status === "SUCCESS") {
          setProgressPercent(100);
          setIsProcessing(false);
          const r = res.result || {};
          const fname = r.filename || `claims_export.${format}`;
          const downloadUrl = r.download_url || api.getAsyncExportDownloadUrl(fname);
          setCompletedResult({
            filename: fname,
            totalRows: r.total_rows ?? (selectedIds?.length || totalRecordsCount || 0),
            fileSize: r.file_size ?? 0,
            downloadUrl,
          });

          // Trigger automatic browser download
          const link = document.createElement("a");
          link.href = downloadUrl;
          link.setAttribute("download", fname);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          clearInterval(interval);
        } else if (res.status === "FAILURE") {
          setIsProcessing(false);
          setErrorMessage(res.error || "Background export job failed.");
          clearInterval(interval);
        }
      } catch (err: any) {
        setIsProcessing(false);
        setErrorMessage(err.message || "Failed to retrieve export task status.");
        clearInterval(interval);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [taskId, isProcessing, format, selectedIds, totalRecordsCount]);

  if (!isOpen) return null;

  const handleStartExport = async () => {
    setIsProcessing(true);
    setErrorMessage(null);
    setProgressPercent(10);
    setStatusMessage("Queueing background export task in Celery...");

    try {
      const res = await api.triggerAsyncExport({
        format,
        status: statusFilter || undefined,
        state: stateFilter || undefined,
        search: searchTerm || undefined,
        claim_ids: selectedIds && selectedIds.length > 0 ? selectedIds : undefined,
      });

      setTaskId(res.task_id);
    } catch (err: any) {
      setIsProcessing(false);
      setErrorMessage(err.response?.data?.detail || "Failed to trigger background export.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-lg w-full shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/40">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/60">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base">
                Export Claims Dataset
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                High-volume streaming export via background worker
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5">
          {/* Scope indicator */}
          <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 rounded-xl p-3 text-xs text-slate-600 dark:text-slate-300 flex items-center justify-between">
            <div>
              <span className="font-semibold text-slate-900 dark:text-white">Export Scope: </span>
              {selectedIds && selectedIds.length > 0 ? (
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                  {selectedIds.length} Selected Claims
                </span>
              ) : (
                <span>
                  Filtered Dataset{" "}
                  {totalRecordsCount !== undefined ? `(${totalRecordsCount} Total Claims)` : ""}
                </span>
              )}
            </div>
            {(statusFilter || stateFilter || searchTerm) && (
              <span className="text-[10px] bg-slate-200 dark:bg-slate-700 px-2 py-0.5 rounded-full">
                Active Filters Applied
              </span>
            )}
          </div>

          {!completedResult && !isProcessing && (
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                Select Output Format
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setFormat("xlsx")}
                  className={`p-3.5 rounded-xl border text-center flex flex-col items-center gap-1.5 transition-all cursor-pointer ${
                    format === "xlsx"
                      ? "border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 ring-2 ring-emerald-500/20"
                      : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400"
                  }`}
                >
                  <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
                  <span className="font-bold text-xs">Excel (.xlsx)</span>
                  <span className="text-[10px] text-slate-400">Formatted tables</span>
                </button>

                <button
                  type="button"
                  onClick={() => setFormat("csv")}
                  className={`p-3.5 rounded-xl border text-center flex flex-col items-center gap-1.5 transition-all cursor-pointer ${
                    format === "csv"
                      ? "border-sky-500 bg-sky-50/50 dark:bg-sky-950/30 text-sky-700 dark:text-sky-300 ring-2 ring-sky-500/20"
                      : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400"
                  }`}
                >
                  <FileText className="w-5 h-5 text-sky-600" />
                  <span className="font-bold text-xs">CSV (.csv)</span>
                  <span className="text-[10px] text-slate-400">Standard tabular</span>
                </button>

                <button
                  type="button"
                  onClick={() => setFormat("json")}
                  className={`p-3.5 rounded-xl border text-center flex flex-col items-center gap-1.5 transition-all cursor-pointer ${
                    format === "json"
                      ? "border-amber-500 bg-amber-50/50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-300 ring-2 ring-amber-500/20"
                      : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400"
                  }`}
                >
                  <FileCode className="w-5 h-5 text-amber-600" />
                  <span className="font-bold text-xs">JSON (.json)</span>
                  <span className="text-[10px] text-slate-400">Raw structures</span>
                </button>
              </div>
            </div>
          )}

          {/* Progress State */}
          {isProcessing && (
            <div className="space-y-4 py-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-300 font-medium flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                  {statusMessage}
                </span>
                <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                  {progressPercent}%
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400 text-center">
                The file will download automatically once processing completes.
              </p>
            </div>
          )}

          {/* Completed State */}
          {completedResult && (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/80 rounded-xl p-4 text-xs space-y-3">
              <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Export generated successfully!</span>
              </div>
              <div className="text-slate-600 dark:text-slate-300 space-y-1 text-[11px]">
                <div>
                  <span className="text-slate-400">Filename: </span>
                  <span className="font-mono font-medium">{completedResult.filename}</span>
                </div>
                <div>
                  <span className="text-slate-400">Total Rows: </span>
                  <span className="font-medium">{completedResult.totalRows} records</span>
                </div>
                {completedResult.fileSize > 0 && (
                  <div>
                    <span className="text-slate-400">File Size: </span>
                    <span className="font-medium">
                      {(completedResult.fileSize / 1024).toFixed(1)} KB
                    </span>
                  </div>
                )}
              </div>
              <div className="pt-2">
                <a
                  href={completedResult.downloadUrl}
                  download={completedResult.filename}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-xs transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download File Again</span>
                </a>
              </div>
            </div>
          )}

          {/* Error State */}
          {errorMessage && (
            <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-xl p-3.5 text-xs text-rose-800 dark:text-rose-300 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 flex items-center justify-end gap-2.5">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-white rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            {completedResult ? "Close" : "Cancel"}
          </button>
          {!completedResult && (
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleStartExport}
              className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg shadow-sm flex items-center gap-1.5 transition-all cursor-pointer"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Download className="w-3.5 h-3.5" />
                  <span>Start Background Export</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
