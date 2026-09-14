"use client";

import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import {
  UploadCloud,
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Calendar,
  HardDrive,
  Layers,
  Bot,
  X,
  FileText,
  Table,
  Check,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  RefreshCw,
  ShieldCheck,
  AlertTriangle,
  Download,
  Copy,
  Info,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import Link from "next/link";
import { api } from "../lib/api";
import {
  IngestionBatch,
  FilePreviewData,
  FileValidationResult,
  TargetFieldDefinition,
  ColumnMappingRecommendation,
  ValidationIssue,
} from "../types";

interface FileUploaderProps {
  onSuccess?: (batch: IngestionBatch) => void;
}

type WizardStep = 1 | 2 | 3 | 4 | 5;

export const FileUploader: React.FC<FileUploaderProps> = ({ onSuccess }) => {
  const [step, setStep] = useState<WizardStep>(1);
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<FilePreviewData | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // Step 2: Column Mapping state
  const [mapping, setMapping] = useState<Record<string, string | null>>({});

  // Step 3: Validation state
  const [duplicateStrategy, setDuplicateStrategy] = useState<"SKIP" | "OVERWRITE" | "IMPORT_ALL">("SKIP");
  const [validationResult, setValidationResult] = useState<FileValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [showAllIssues, setShowAllIssues] = useState(false);

  // Step 4 & 5: Ingestion Progress and Summary
  const [isUploading, setIsUploading] = useState(false);
  const [activeBatch, setActiveBatch] = useState<IngestionBatch | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load preview and auto-initialize mappings
  const loadPreview = async (selectedFile: File) => {
    setIsPreviewLoading(true);
    setPreviewData(null);
    setError(null);
    try {
      const data = await api.previewFile(selectedFile);
      setPreviewData(data);

      // Auto-populate mapping from backend recommendations
      const initialMapping: Record<string, string | null> = {};
      if (data.mapping_recommendations && data.mapping_recommendations.length > 0) {
        data.mapping_recommendations.forEach((rec) => {
          initialMapping[rec.target_key] = rec.source_column;
        });
      } else if (data.target_fields) {
        data.target_fields.forEach((tf) => {
          const matched = data.detected_columns.find(
            (c) => c.toLowerCase() === tf.label.toLowerCase() || c.toLowerCase() === tf.key.toLowerCase()
          );
          initialMapping[tf.key] = matched || null;
        });
      }
      setMapping(initialMapping);
      setStep(2); // Automatically advance to Column Mapping step
    } catch (err: any) {
      console.error("Preview failed:", err);
      setError(err?.response?.data?.detail || "Could not analyze spreadsheet schema. Please check the file format.");
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0];
      setFile(selected);
      loadPreview(selected);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const selected = acceptedFiles[0];
      setFile(selected);
      loadPreview(selected);
    }
  }, []);

  // Expose global helper for automated testing and browser subagent flows
  useEffect(() => {
    if (typeof window !== "undefined") {
      (window as any).__selectClaimFile = (selectedFile: File) => {
        setFile(selectedFile);
        loadPreview(selectedFile);
      };
    }
    return () => {
      if (typeof window !== "undefined") {
        delete (window as any).__selectClaimFile;
      }
    };
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
      "text/csv": [".csv"],
    },
    maxFiles: 1,
  });

  // Handle remapping a target field
  const handleMappingChange = (targetKey: string, sourceCol: string) => {
    setMapping((prev) => ({
      ...prev,
      [targetKey]: sourceCol === "__NONE__" ? null : sourceCol,
    }));
  };

  // Reset mappings to auto-detected defaults
  const handleResetToAutoDetected = () => {
    if (!previewData?.mapping_recommendations) return;
    const autoMapping: Record<string, string | null> = {};
    previewData.mapping_recommendations.forEach((rec) => {
      autoMapping[rec.target_key] = rec.source_column;
    });
    setMapping(autoMapping);
  };

  // Clear all mappings
  const handleClearAllMappings = () => {
    if (!previewData?.target_fields) return;
    const cleared: Record<string, string | null> = {};
    previewData.target_fields.forEach((tf) => {
      cleared[tf.key] = null;
    });
    setMapping(cleared);
  };

  // Validate mapping and perform duplicate check
  const handleValidateMapping = async (strategyOverride?: "SKIP" | "OVERWRITE" | "IMPORT_ALL") => {
    if (!file) return;
    const strategy = strategyOverride || duplicateStrategy;
    setIsValidating(true);
    setError(null);
    try {
      const result = await api.validateFileMapping(file, mapping, strategy);
      setValidationResult(result);
      setStep(3); // Advance to Validation & Duplicate Inspection step
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Validation failed. Please verify column mappings.");
    } finally {
      setIsValidating(false);
    }
  };

  // Change duplicate strategy in Step 3 and re-validate seamlessly
  const handleStrategyChange = (newStrategy: "SKIP" | "OVERWRITE" | "IMPORT_ALL") => {
    setDuplicateStrategy(newStrategy);
    handleValidateMapping(newStrategy);
  };

  // Start Ingestion
  const handleStartIngestion = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    setStep(4);

    try {
      const batch = await api.uploadFileWithMapping(file, mapping, duplicateStrategy);
      setActiveBatch(batch);
      if (onSuccess) {
        onSuccess(batch);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to start file ingestion.");
      setStep(3); // Return to validation on immediate failure
      setIsUploading(false);
    }
  };

  // Poll batch status during Step 4
  useEffect(() => {
    if (step !== 4 || !activeBatch?.id) return;

    const interval = setInterval(async () => {
      try {
        const latest = await api.getBatchStatus(activeBatch.id);
        setActiveBatch(latest);
        if (latest.status === "COMPLETED" || latest.status === "FAILED") {
          clearInterval(interval);
          setIsUploading(false);
          setStep(5); // Advance to Summary step
        }
      } catch (err) {
        console.warn("Polling batch failed:", err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [step, activeBatch?.id]);

  // Full reset
  const handleResetAll = () => {
    setStep(1);
    setFile(null);
    setPreviewData(null);
    setMapping({});
    setValidationResult(null);
    setActiveBatch(null);
    setError(null);
  };

  const isClaimNumberMapped = Boolean(mapping["claim_number"]);

  return (
    <div className="space-y-6 w-full">
      {/* 5-STEP WIZARD PROGRESS STEPPER */}
      <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-3 sm:p-4">
        <div className="flex items-center justify-between gap-2 sm:gap-4 overflow-x-auto pb-1 text-xs">
          {/* Step 1 */}
          <div className={`flex items-center gap-2 whitespace-nowrap ${step === 1 ? "text-indigo-600 dark:text-indigo-400 font-bold" : step > 1 ? "text-emerald-600 dark:text-emerald-400 font-medium" : "text-slate-400"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 ${step === 1 ? "bg-indigo-600 text-white" : step > 1 ? "bg-emerald-500 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-500"}`}>
              {step > 1 ? "✓" : "1"}
            </span>
            <span>1. Upload File</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">→</span>

          {/* Step 2 */}
          <div className={`flex items-center gap-2 whitespace-nowrap ${step === 2 ? "text-indigo-600 dark:text-indigo-400 font-bold" : step > 2 ? "text-emerald-600 dark:text-emerald-400 font-medium" : "text-slate-400"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 ${step === 2 ? "bg-indigo-600 text-white" : step > 2 ? "bg-emerald-500 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-500"}`}>
              {step > 2 ? "✓" : "2"}
            </span>
            <span>2. Column Mapping</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">→</span>

          {/* Step 3 */}
          <div className={`flex items-center gap-2 whitespace-nowrap ${step === 3 ? "text-indigo-600 dark:text-indigo-400 font-bold" : step > 3 ? "text-emerald-600 dark:text-emerald-400 font-medium" : "text-slate-400"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 ${step === 3 ? "bg-indigo-600 text-white" : step > 3 ? "bg-emerald-500 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-500"}`}>
              {step > 3 ? "✓" : "3"}
            </span>
            <span>3. Validation &amp; Duplicates</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">→</span>

          {/* Step 4 */}
          <div className={`flex items-center gap-2 whitespace-nowrap ${step === 4 ? "text-indigo-600 dark:text-indigo-400 font-bold" : step > 4 ? "text-emerald-600 dark:text-emerald-400 font-medium" : "text-slate-400"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 ${step === 4 ? "bg-indigo-600 text-white animate-pulse" : step > 4 ? "bg-emerald-500 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-500"}`}>
              {step > 4 ? "✓" : "4"}
            </span>
            <span>4. Ingestion</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">→</span>

          {/* Step 5 */}
          <div className={`flex items-center gap-2 whitespace-nowrap ${step === 5 ? "text-emerald-600 dark:text-emerald-400 font-bold" : "text-slate-400"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 ${step === 5 ? "bg-emerald-500 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-500"}`}>
              5
            </span>
            <span>5. Summary</span>
          </div>
        </div>
      </div>

      {/* ERROR ALERT */}
      {error && (
        <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 rounded-xl p-4 text-rose-800 dark:text-rose-300 flex items-start gap-3 text-xs">
          <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold text-rose-900 dark:text-rose-200">Error</p>
            <p className="text-rose-700 dark:text-rose-400/90">{error}</p>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* STEP 1: FILE DROPZONE & UPLOAD                                            */}
      {/* ========================================================================= */}
      {step === 1 && (
        <div className="space-y-4">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all cursor-pointer ${
              isDragActive
                ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/20"
                : "border-slate-300 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30"
            }`}
          >
            <input {...getInputProps({ onChange: handleFileInput })} id="claim-file-input" />
            <div className="flex flex-col items-center justify-center space-y-3">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shadow-inner">
                <UploadCloud className="w-8 h-8" />
              </div>
              <div className="space-y-1">
                <p className="text-base font-semibold text-slate-800 dark:text-slate-200">
                  {isDragActive ? "Drop spreadsheet here" : "Drag & drop claim spreadsheet here, or click to browse"}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Supports Excel (.xlsx, .xls) and CSV (.csv). Headers can vary; you can customize column mapping in the next step.
                </p>
              </div>
            </div>
          </div>

          {isPreviewLoading && (
            <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 flex flex-col items-center justify-center space-y-3 text-center shadow-xs">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  Analyzing Spreadsheet Schema &amp; Columns...
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Inspecting headers and running RapidFuzz column match algorithm.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* STEP 2: COLUMN MAPPING INTERFACE                                          */}
      {/* ========================================================================= */}
      {step === 2 && previewData && (
        <div className="space-y-6">
          {/* File Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">{previewData.filename}</h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                    {previewData.file_type}
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {previewData.filesize_formatted} • {previewData.total_records} total rows • {previewData.detected_columns.length} columns detected
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleResetToAutoDetected}
                className="px-3 py-1.5 text-xs font-semibold text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-950/40 flex items-center gap-1.5 transition-colors"
                title="Re-run auto-detection algorithm"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Auto-Detect All
              </button>
              <button
                onClick={handleClearAllMappings}
                className="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Clear All
              </button>
              <button
                onClick={handleResetAll}
                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg border border-slate-200 dark:border-slate-800 transition-colors"
                title="Cancel & Choose another file"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Missing Claim Number Warning */}
          {!isClaimNumberMapped && (
            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800/80 rounded-xl p-3 flex items-start gap-2.5 text-xs text-amber-800 dark:text-amber-300">
              <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong>Claim Number is required:</strong> Please select the spreadsheet column that contains the Claim Number before proceeding.
              </div>
            </div>
          )}

          {/* Column Mapping Table */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 font-semibold text-[11px]">
                    <th className="p-3 w-1/4">UAIC Target Schema Field</th>
                    <th className="p-3 w-1/3">Mapped Spreadsheet Column</th>
                    <th className="p-3 w-28 text-center">Match Status</th>
                    <th className="p-3">Sample Column Values</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {(previewData.target_fields || []).map((tf) => {
                    const currentMapped = mapping[tf.key] || null;
                    const rec = previewData.mapping_recommendations?.find((r) => r.target_key === tf.key);
                    const isExact = rec?.source_column === currentMapped && rec?.confidence === "EXACT";
                    const isFuzzy = rec?.source_column === currentMapped && (rec?.confidence === "HIGH_FUZZY" || rec?.confidence === "LOW_FUZZY");
                    const samples = currentMapped && previewData.column_samples ? previewData.column_samples[currentMapped] || [] : [];

                    return (
                      <tr key={tf.key} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                        <td className="p-3">
                          <div className="flex items-center gap-1.5 font-medium text-slate-900 dark:text-slate-100">
                            {tf.label}
                            {tf.required && (
                              <span className="text-rose-500 font-bold" title="Required field">*</span>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-400">{tf.description}</div>
                        </td>

                        <td className="p-3">
                          <select
                            value={currentMapped || "__NONE__"}
                            onChange={(e) => handleMappingChange(tf.key, e.target.value)}
                            className={`w-full text-xs font-mono rounded-lg border py-1.5 px-2 bg-white dark:bg-slate-900 transition-colors focus:ring-2 focus:ring-indigo-500 ${
                              tf.required && !currentMapped
                                ? "border-rose-400 dark:border-rose-600 text-rose-600"
                                : "border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200"
                            }`}
                          >
                            <option value="__NONE__">-- Do not map / Skip --</option>
                            {previewData.detected_columns.map((col) => (
                              <option key={col} value={col}>
                                {col}
                              </option>
                            ))}
                          </select>
                        </td>

                        <td className="p-3 text-center">
                          {currentMapped ? (
                            isExact ? (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60">
                                Exact Match
                              </span>
                            ) : isFuzzy ? (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-400 border border-sky-200 dark:border-sky-800/60">
                                Auto-Matched
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800/60">
                                User-Mapped
                              </span>
                            )
                          ) : (
                            <span className="inline-flex items-center text-[10px] text-slate-400 font-medium">
                              {tf.required ? (
                                <span className="text-rose-500 font-bold">Unmapped *</span>
                              ) : (
                                "Skipped"
                              )}
                            </span>
                          )}
                        </td>

                        <td className="p-3">
                          {samples.length > 0 ? (
                            <div className="flex items-center gap-1 flex-wrap">
                              {samples.map((s, sIdx) => (
                                <span
                                  key={sIdx}
                                  className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 max-w-[150px] truncate"
                                  title={s}
                                >
                                  {s}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-[11px] text-slate-400 italic">No samples</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Step 2 Action Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-slate-200 dark:border-slate-800/80">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Upload
            </button>

            <button
              onClick={() => handleValidateMapping()}
              disabled={!isClaimNumberMapped || isValidating}
              className="flex items-center justify-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
            >
              {isValidating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Validating &amp; Checking Duplicates...
                </>
              ) : (
                <>
                  Validate &amp; Check Duplicates
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* STEP 3: VALIDATION & DUPLICATE INSPECTION                                  */}
      {/* ========================================================================= */}
      {step === 3 && validationResult && (
        <div className="space-y-6">
          {/* 5 KPI Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div className="bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-slate-500 dark:text-slate-400">Total Rows</span>
              <div className="text-lg font-extrabold text-slate-900 dark:text-slate-100">
                {validationResult.total_rows}
              </div>
            </div>

            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-emerald-700 dark:text-emerald-400 font-medium">Valid to Ingest</span>
              <div className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                {validationResult.valid_rows}
              </div>
            </div>

            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-amber-700 dark:text-amber-400 font-medium">Duplicates</span>
              <div className="text-lg font-extrabold text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                <Copy className="w-4 h-4" />
                {validationResult.duplicate_rows}
              </div>
            </div>

            <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-rose-700 dark:text-rose-400 font-medium">Invalid Rows</span>
              <div className="text-lg font-extrabold text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4" />
                {validationResult.invalid_rows}
              </div>
            </div>

            <div className="col-span-2 sm:col-span-1 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-indigo-700 dark:text-indigo-400 font-medium">Est. Bot Runs</span>
              <div className="text-lg font-extrabold text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5">
                <Bot className="w-4 h-4" />
                ~{validationResult.estimated_bot_runs}
              </div>
            </div>
          </div>

          {/* DUPLICATE RESOLUTION STRATEGY SELECTOR */}
          <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-500" />
                <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                  Duplicate Resolution Strategy
                </h4>
              </div>
              <span className="text-[11px] text-slate-400">Enforced during ingestion</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <label
                className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                  duplicateStrategy === "SKIP"
                    ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 text-indigo-950 dark:text-indigo-200"
                    : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <input
                  type="radio"
                  name="dup_strategy"
                  value="SKIP"
                  checked={duplicateStrategy === "SKIP"}
                  onChange={() => handleStrategyChange("SKIP")}
                  className="mt-0.5 text-indigo-600 focus:ring-indigo-500"
                />
                <div className="space-y-0.5">
                  <div className="text-xs font-bold">Skip Duplicates (Recommended)</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">
                    Skip existing claim numbers and record them in the failed rows download.
                  </div>
                </div>
              </label>

              <label
                className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                  duplicateStrategy === "OVERWRITE"
                    ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 text-indigo-950 dark:text-indigo-200"
                    : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <input
                  type="radio"
                  name="dup_strategy"
                  value="OVERWRITE"
                  checked={duplicateStrategy === "OVERWRITE"}
                  onChange={() => handleStrategyChange("OVERWRITE")}
                  className="mt-0.5 text-indigo-600 focus:ring-indigo-500"
                />
                <div className="space-y-0.5">
                  <div className="text-xs font-bold">Update Existing Records</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">
                    Update existing claim records with newly provided demographic data.
                  </div>
                </div>
              </label>

              <label
                className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                  duplicateStrategy === "IMPORT_ALL"
                    ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 text-indigo-950 dark:text-indigo-200"
                    : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <input
                  type="radio"
                  name="dup_strategy"
                  value="IMPORT_ALL"
                  checked={duplicateStrategy === "IMPORT_ALL"}
                  onChange={() => handleStrategyChange("IMPORT_ALL")}
                  className="mt-0.5 text-indigo-600 focus:ring-indigo-500"
                />
                <div className="space-y-0.5">
                  <div className="text-xs font-bold">Import All Rows</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">
                    Import every row into queue without duplicate checks.
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* VALIDATION ISSUES LIST (if any) */}
          {validationResult.issues.length > 0 && (
            <div className="bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/60 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-amber-900 dark:text-amber-300">
                  <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                  Validation Issues &amp; Duplicate Warnings ({validationResult.issues.length} rows flagged)
                </div>
                <button
                  onClick={() => setShowAllIssues(!showAllIssues)}
                  className="text-xs text-amber-700 dark:text-amber-400 hover:underline flex items-center gap-1 font-medium cursor-pointer"
                >
                  {showAllIssues ? "Collapse" : "Expand Details"}
                  {showAllIssues ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              </div>

              {showAllIssues && (
                <div className="border border-amber-200/80 dark:border-amber-800/40 rounded-lg overflow-hidden max-h-56 overflow-y-auto">
                  <table className="w-full text-left text-xs bg-white dark:bg-slate-900">
                    <thead className="bg-amber-50 dark:bg-amber-950/60 border-b border-amber-200 dark:border-amber-800 text-[11px] text-amber-900 dark:text-amber-300 font-semibold sticky top-0">
                      <tr>
                        <th className="p-2 w-16">Row #</th>
                        <th className="p-2 w-32">Claim Number</th>
                        <th className="p-2 w-32">Issue Type</th>
                        <th className="p-2">Explanation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {validationResult.issues.map((issue, iIdx) => (
                        <tr key={iIdx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                          <td className="p-2 font-mono text-[11px] text-slate-500">{issue.row_number}</td>
                          <td className="p-2 font-mono font-bold text-slate-800 dark:text-slate-200">
                            {issue.claim_number || "-"}
                          </td>
                          <td className="p-2">
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                issue.issue_type === "INVALID"
                                  ? "bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400"
                                  : "bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400"
                              }`}
                            >
                              {issue.issue_type.replace(/_/g, " ")}
                            </span>
                          </td>
                          <td className="p-2 text-slate-600 dark:text-slate-400 text-[11px]">{issue.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* RECORDS PREVIEW TABLE */}
          {validationResult.preview_records.length > 0 && (
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Data Preview (First {validationResult.preview_records.length} records to be injected)
                </span>
                <span className="text-[11px] text-slate-400">
                  Mapped schema verification
                </span>
              </div>

              <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold text-[11px]">
                        <th className="p-3 w-12 text-center">#</th>
                        <th className="p-3">Claim Number</th>
                        <th className="p-3">Insured Party</th>
                        <th className="p-3">Claimant Party</th>
                        <th className="p-3">Date of Loss</th>
                        <th className="p-3">Policy State</th>
                        <th className="p-3">Loss Location</th>
                        <th className="p-3">Target RPA Bots</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                      {validationResult.preview_records.map((rec) => (
                        <tr key={rec.row_number} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                          <td className="p-3 text-center text-slate-400 font-mono text-[11px]">{rec.row_number}</td>
                          <td className="p-3 font-mono font-bold text-indigo-600 dark:text-indigo-400">{rec.claim_number}</td>
                          <td className="p-3 text-slate-800 dark:text-slate-200">{rec.insured_name || "-"}</td>
                          <td className="p-3 text-slate-600 dark:text-slate-400">{rec.claimant_name || "-"}</td>
                          <td className="p-3 font-mono text-slate-600 dark:text-slate-400">{rec.dol || "-"}</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                              {rec.policy_state || "Florida"}
                            </span>
                          </td>
                          <td className="p-3 text-slate-500 text-[11px]">{rec.loss_location || "-"}</td>
                          <td className="p-3">
                            <div className="flex items-center gap-1 flex-wrap">
                              {rec.target_bots.map((b, bIdx) => (
                                <span
                                  key={bIdx}
                                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                                    b.startsWith("Fl")
                                      ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50"
                                      : "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-400 border border-sky-200 dark:border-sky-800/50"
                                  }`}
                                >
                                  {b.replace("FL: ", "").replace("TX: ", "")}
                                </span>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Action Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-slate-200 dark:border-slate-800/80">
            <button
              onClick={() => setStep(2)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Column Mapping
            </button>

            <button
              onClick={handleStartIngestion}
              disabled={validationResult.valid_rows === 0 || isUploading}
              className="flex items-center justify-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              Start Ingestion ({validationResult.valid_rows} Valid Claims)
            </button>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* STEP 4: LIVE INGESTION PROGRESS                                           */}
      {/* ========================================================================= */}
      {step === 4 && (
        <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 space-y-6 text-center shadow-xs">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>

          <div className="space-y-2 max-w-md mx-auto">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Ingesting Claims &amp; Orchestrating Celery Workers...
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Normalizing dates, applying custom column mapping, and dispatching court scraper tasks.
            </p>
          </div>

          {activeBatch && (
            <div className="max-w-md mx-auto space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                <span>Batch ID: {activeBatch.id.substring(0, 8)}...</span>
                <span>Status: {activeBatch.status}</span>
              </div>
              <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-full animate-pulse w-3/4 transition-all"></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* STEP 5: SUMMARY REPORT & FAILED ROWS DOWNLOAD                              */}
      {/* ========================================================================= */}
      {step === 5 && activeBatch && (
        <div className="space-y-6">
          {/* Success / Completion Banner */}
          <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-2xl p-6 text-emerald-800 dark:text-emerald-300 space-y-3">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <div>
                <h3 className="text-base font-bold text-emerald-900 dark:text-emerald-200">
                  Spreadsheet Ingestion Complete!
                </h3>
                <p className="text-xs text-emerald-700 dark:text-emerald-400/90">
                  Batch ID: <span className="font-mono font-bold">{activeBatch.id}</span> • {activeBatch.filename}
                </p>
              </div>
            </div>
          </div>

          {/* Final Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div className="bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-slate-500">Total Rows</span>
              <div className="text-lg font-bold text-slate-900 dark:text-slate-100">
                {activeBatch.total_records}
              </div>
            </div>

            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-emerald-700 dark:text-emerald-400 font-medium">Ingested</span>
              <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                {activeBatch.processed_records}
              </div>
            </div>

            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-amber-700 dark:text-amber-400 font-medium">Duplicates</span>
              <div className="text-lg font-bold text-amber-600 dark:text-amber-400">
                {activeBatch.duplicate_records || 0}
              </div>
            </div>

            <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-rose-700 dark:text-rose-400 font-medium">Invalid Rows</span>
              <div className="text-lg font-bold text-rose-600 dark:text-rose-400">
                {activeBatch.invalid_records || 0}
              </div>
            </div>

            <div className="col-span-2 sm:col-span-1 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/70 rounded-xl p-3 space-y-1">
              <span className="text-xs text-slate-500">Failed Records</span>
              <div className="text-lg font-bold text-slate-900 dark:text-slate-100">
                {activeBatch.failed_records || 0}
              </div>
            </div>
          </div>

          {/* FAILED ROWS DOWNLOAD CARD (If any rows failed or skipped) */}
          {((activeBatch.failed_records || 0) > 0 || (activeBatch.invalid_records || 0) > 0 || (activeBatch.duplicate_records || 0) > 0) && (
            <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs font-bold text-amber-900 dark:text-amber-300">
                  <Download className="w-4 h-4 text-amber-600" />
                  Failed &amp; Skipped Rows Available for Download
                </div>
                <p className="text-[11px] text-amber-700 dark:text-amber-400/90">
                  Download a complete CSV detailing every row number, claim number, and error reason for easy review and correction.
                </p>
              </div>

              <a
                href={api.getFailedRowsDownloadUrl(activeBatch.id)}
                download={`failed_rows_${activeBatch.id.substring(0, 8)}.csv`}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold rounded-lg flex items-center justify-center gap-2 shadow-xs transition-colors shrink-0"
              >
                <Download className="w-4 h-4" />
                Download Failed Rows (.csv)
              </a>
            </div>
          )}

          {/* Action Navigation Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-slate-200 dark:border-slate-800/80">
            <button
              onClick={handleResetAll}
              className="px-4 py-2.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors shadow-xs"
            >
              <Upload className="w-3.5 h-3.5" />
              Import Another Spreadsheet
            </button>

            <div className="flex items-center gap-3">
              <Link
                href="/monitor"
                className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-1.5 transition-all"
              >
                View Queue Monitor
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                href="/"
                className="px-4 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded-xl border border-slate-300 dark:border-slate-700 transition-all"
              >
                Claims Dashboard
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


