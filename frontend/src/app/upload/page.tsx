"use client";

import React, { useState } from "react";
import { Navbar } from "../../components/Navbar";
import { FileUploader } from "../../components/FileUploader";
import { IngestionBatch } from "../../types";
import { FileSpreadsheet, CheckCircle2, ShieldCheck, ArrowRight, Download, FileText } from "lucide-react";
import Link from "next/link";

export default function UploadPage() {
  const [lastBatch, setLastBatch] = useState<IngestionBatch | null>(null);

  return (
    <div className="flex-1 flex flex-col w-full">
      <Navbar />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none flex-1 transition-colors">
        {/* Title Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Data Ingestion & Excel Import
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Upload claims spreadsheet to trigger automated Celery parsing, schema validation, and county bot routing.
            </p>
          </div>
        </div>

        {/* Uploader Card */}
        <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
          <FileUploader onSuccess={(batch) => setLastBatch(batch)} />

        </div>

        {/* Architecture & Format Reference */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
          <div className="bg-white dark:bg-slate-900/30 border border-slate-200 dark:border-slate-800/80 rounded-xl p-6 space-y-3 shadow-xs transition-colors">
            <div className="flex items-center gap-2 text-slate-900 dark:text-slate-200 font-semibold text-xs">
              <FileSpreadsheet className="w-4 h-4 text-indigo-500" />
              Supported Columns & Formatting
            </div>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
              The ingestion engine automatically maps and validates the following fields:
            </p>
            <ul className="text-[11px] text-slate-600 dark:text-slate-400 space-y-1 list-disc list-inside font-mono">
              <li>Primary Key</li>
              <li>Claim Number (Required)</li>
              <li>Exposure Number</li>
              <li>Insured First & Last Name</li>
              <li>Claimant First & Last Name</li>
              <li>Driver First & Last Name (Insured Vehicle)</li>
              <li>DOL (Excel serial date or MM/DD/YYYY)</li>
              <li>Policy State &amp; Loss Location State</li>
            </ul>
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center gap-3">
              <span className="text-[11px] text-slate-500">Download Template:</span>
              <a
                href="/sample_claims.xlsx"
                download="sample_claims.xlsx"
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-medium"
              >
                <Download className="w-3 h-3" /> Excel (.xlsx)
              </a>
              <a
                href="/sample_claims.csv"
                download="sample_claims.csv"
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-medium"
              >
                <FileText className="w-3 h-3" /> CSV (.csv)
              </a>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900/30 border border-slate-200 dark:border-slate-800/80 rounded-xl p-6 space-y-3 shadow-xs transition-colors">
            <div className="flex items-center gap-2 text-slate-900 dark:text-slate-200 font-semibold text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              State Routing & RPA Dispatch
            </div>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
              Claims are automatically routed to county scrapers based on policy geography:
            </p>
            <div className="text-[11px] text-slate-600 dark:text-slate-400 space-y-1.5">
              <div>
                <strong className="text-slate-800 dark:text-slate-300">Florida:</strong> Broward, Hillsborough, Miami-Dade
              </div>
              <div>
                <strong className="text-slate-800 dark:text-slate-300">Texas:</strong> Travis, Dallas, Harris JP, CClerk, HCDistrict
              </div>
              <div>
                <strong className="text-slate-800 dark:text-slate-300">Cross-State:</strong> All 8 portals dispatched concurrently
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
