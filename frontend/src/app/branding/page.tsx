"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import {
  Palette,
  RotateCcw,
  Save,
  Upload,
  CheckCircle2,
  AlertCircle,
  Menu,
  Trash2,
  Sparkles,
  Sun,
  Moon,
  Layers,
  Sliders,
  Check,
  CheckCheck,
  Eye,
} from "lucide-react";
import { api } from "../../lib/api";
import { BrandingSettings, ThemePalette } from "../../types";
import {
  useBranding,
  BrandBadge,
  DEFAULT_BRANDING,
  DEFAULT_LIGHT_PALETTE,
  DEFAULT_DARK_PALETTE,
} from "../../components/BrandingContext";

interface TokenItem {
  key: keyof ThemePalette;
  label: string;
  desc: string;
  cssVar: string;
}

interface TokenCategory {
  title: string;
  desc: string;
  tokens: TokenItem[];
}

const TOKEN_CATEGORIES: TokenCategory[] = [
  {
    title: "Brand & Accent Colors",
    desc: "Primary and secondary colors used for brand focal points, active states, and highlights.",
    tokens: [
      { key: "primary", label: "Primary Accent", desc: "Main brand action color", cssVar: "--color-primary" },
      { key: "secondary", label: "Secondary Accent", desc: "Supporting accent color", cssVar: "--color-secondary" },
      { key: "accent", label: "Highlight Accent", desc: "Tertiary highlight tint", cssVar: "--color-accent" },
    ],
  },
  {
    title: "Surfaces & Layout Structure",
    desc: "Background canvas and container colors across viewports, panels, and sidebars.",
    tokens: [
      { key: "background", label: "Page Background", desc: "Main canvas background", cssVar: "--color-background" },
      { key: "surface", label: "Surface / Panel", desc: "Containers & sections", cssVar: "--color-surface" },
      { key: "card", label: "Card Container", desc: "Dashboard cards & widgets", cssVar: "--color-card" },
      { key: "header", label: "Navbar / Header", desc: "Top navigation bar background", cssVar: "--color-header" },
      { key: "sidebar", label: "Sidebar Menu", desc: "Navigation drawer & sidebar", cssVar: "--color-sidebar" },
    ],
  },
  {
    title: "Typography & Content",
    desc: "Text readability hierarchy for headings, body copy, and subtitles.",
    tokens: [
      { key: "text", label: "Primary Text", desc: "High-contrast reading text", cssVar: "--color-text" },
      { key: "text_muted", label: "Muted Text", desc: "Captions, labels & timestamps", cssVar: "--color-text-muted" },
    ],
  },
  {
    title: "Borders & Structural Dividers",
    desc: "Subtle separation lines between sections, cards, and table rows.",
    tokens: [
      { key: "border", label: "Standard Border", desc: "Card and input bounding borders", cssVar: "--color-border" },
      { key: "divider", label: "Divider Line", desc: "Horizontal separation rules", cssVar: "--color-divider" },
    ],
  },
  {
    title: "Form Inputs & Controls",
    desc: "Input fields, selects, textareas, and search boxes.",
    tokens: [
      { key: "input_background", label: "Input Background", desc: "Field interior background", cssVar: "--color-input-background" },
      { key: "input_text", label: "Input Text", desc: "Typed input characters", cssVar: "--color-input-text" },
    ],
  },
  {
    title: "Buttons & Action Controls",
    desc: "Interactive triggers, primary action buttons, and anchor links.",
    tokens: [
      { key: "button", label: "Button Background", desc: "Primary CTA fill color", cssVar: "--color-button" },
      { key: "button_text", label: "Button Text", desc: "Readable text on button", cssVar: "--color-button-text" },
      { key: "link", label: "Hyperlink Text", desc: "Clickable text and links", cssVar: "--color-link" },
    ],
  },
  {
    title: "Operational Status Indicators",
    desc: "Color semantics for match results, queue processing, and alert toasts.",
    tokens: [
      { key: "success", label: "Success State", desc: "Matched & completed items", cssVar: "--color-success" },
      { key: "warning", label: "Warning State", desc: "Manual review & cautions", cssVar: "--color-warning" },
      { key: "error", label: "Error State", desc: "Failed scrapes & alerts", cssVar: "--color-error" },
      { key: "info", label: "Informational State", desc: "General notices & badges", cssVar: "--color-info" },
    ],
  },
  {
    title: "Interactive Component States",
    desc: "Stateful styles for hover, active click, focus outlines, selected items, and disabled controls.",
    tokens: [
      { key: "focus", label: "Focus Outline", desc: "Keyboard accessibility ring", cssVar: "--color-focus" },
      { key: "hover", label: "Hover Surface", desc: "Cursor hover background", cssVar: "--color-hover" },
      { key: "active", label: "Active Press", desc: "Button down/pressed state", cssVar: "--color-active" },
      { key: "selected", label: "Selected Item", desc: "Checked row or active tab", cssVar: "--color-selected" },
      { key: "disabled", label: "Disabled Control", desc: "Inactive / disabled elements", cssVar: "--color-disabled" },
    ],
  },
];

const LIGHT_PRESETS = [
  {
    name: "Classic Enterprise (Default)",
    desc: "Clean slate-50 background with royal indigo accents",
    palette: DEFAULT_LIGHT_PALETTE,
  },
  {
    name: "Crisp Azure",
    desc: "Modern corporate blue with high-legibility slate surfaces",
    palette: {
      ...DEFAULT_LIGHT_PALETTE,
      primary: "#2563eb",
      secondary: "#0284c7",
      accent: "#3b82f6",
      background: "#f0f4f8",
      surface: "#ffffff",
      card: "#ffffff",
      button: "#2563eb",
      link: "#2563eb",
      focus: "#3b82f6",
      selected: "#dbeafe",
    },
  },
  {
    name: "Emerald Pro",
    desc: "Fresh financial green with crisp zinc-50 surfaces",
    palette: {
      ...DEFAULT_LIGHT_PALETTE,
      primary: "#059669",
      secondary: "#0d9488",
      accent: "#10b981",
      background: "#f4f4f5",
      surface: "#ffffff",
      card: "#ffffff",
      button: "#059669",
      link: "#059669",
      focus: "#10b981",
      selected: "#d1fae5",
    },
  },
  {
    name: "Warm Sand",
    desc: "Warm neutral stone canvas with rich amber highlights",
    palette: {
      ...DEFAULT_LIGHT_PALETTE,
      primary: "#d97706",
      secondary: "#ea580c",
      accent: "#f59e0b",
      background: "#fafaf9",
      surface: "#ffffff",
      card: "#ffffff",
      button: "#d97706",
      link: "#d97706",
      focus: "#f59e0b",
      selected: "#fef3c7",
    },
  },
];

const DARK_PRESETS = [
  {
    name: "Obsidian Slate (Default)",
    desc: "Deep slate-950 backdrop with vibrant indigo illumination",
    palette: DEFAULT_DARK_PALETTE,
  },
  {
    name: "Midnight Navy",
    desc: "Ultra-deep navy background with cyan & sky blue neon accents",
    palette: {
      ...DEFAULT_DARK_PALETTE,
      primary: "#38bdf8",
      secondary: "#06b6d4",
      accent: "#60a5fa",
      background: "#030712",
      surface: "#0b1329",
      card: "#0b1329",
      header: "#030712",
      sidebar: "#030712",
      border: "#1e294b",
      divider: "#1e294b",
      input_background: "#030712",
      button: "#0284c7",
      link: "#38bdf8",
      focus: "#38bdf8",
      selected: "#1e3a8a",
    },
  },
  {
    name: "Cyber Emerald",
    desc: "Tactical terminal dark with neon emerald and mint accents",
    palette: {
      ...DEFAULT_DARK_PALETTE,
      primary: "#10b981",
      secondary: "#34d399",
      accent: "#6ee7b7",
      background: "#020617",
      surface: "#04201b",
      card: "#04201b",
      header: "#020617",
      sidebar: "#020617",
      border: "#064e3b",
      divider: "#064e3b",
      input_background: "#020617",
      button: "#059669",
      link: "#34d399",
      focus: "#10b981",
      selected: "#064e3b",
    },
  },
  {
    name: "High Contrast Pro",
    desc: "Pitch black OLED background with vivid violet accents",
    palette: {
      ...DEFAULT_DARK_PALETTE,
      primary: "#8b5cf6",
      secondary: "#a855f7",
      accent: "#c084fc",
      background: "#000000",
      surface: "#0a0a0a",
      card: "#0a0a0a",
      header: "#000000",
      sidebar: "#000000",
      border: "#27272a",
      divider: "#27272a",
      input_background: "#000000",
      text: "#ffffff",
      button: "#7c3aed",
      link: "#a78bfa",
      focus: "#8b5cf6",
      selected: "#4c1d95",
    },
  },
];

export default function BrandingPage() {
  const { branding: contextBranding, updateBranding, refreshBranding } = useBranding();
  const [branding, setBranding] = useState<BrandingSettings>(contextBranding || DEFAULT_BRANDING);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  // Tab State: "brand" | "theme" (default to "brand" per UX spec)
  const [activeTab, setActiveTab] = useState<"brand" | "theme">("brand");

  // Palette Mode in Theme Tab: "light" | "dark"
  const [paletteMode, setPaletteMode] = useState<"light" | "dark">("light");

  // Logo upload state
  const [isDraggingLogo, setIsDraggingLogo] = useState<boolean>(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState<boolean>(false);
  const [logoUploadError, setLogoUploadError] = useState<string | null>(null);
  const [logoUploadSuccess, setLogoUploadSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadBranding();
  }, []);

  const loadBranding = async () => {
    setIsLoading(true);
    try {
      const data = await api.getBrandingSettings();
      if (data) {
        const merged: BrandingSettings = {
          app_title: data.app_title || DEFAULT_BRANDING.app_title,
          app_subtitle: data.app_subtitle || DEFAULT_BRANDING.app_subtitle,
          app_logo_url: data.app_logo_url || DEFAULT_BRANDING.app_logo_url,
          badge_letter: data.badge_letter || DEFAULT_BRANDING.badge_letter,
          theme_accent: data.theme_accent || DEFAULT_BRANDING.theme_accent,
          light_palette: data.light_palette ? { ...DEFAULT_LIGHT_PALETTE, ...data.light_palette } : DEFAULT_LIGHT_PALETTE,
          dark_palette: data.dark_palette ? { ...DEFAULT_DARK_PALETTE, ...data.dark_palette } : DEFAULT_DARK_PALETTE,
        };
        setBranding(merged);
      } else {
        setBranding(DEFAULT_BRANDING);
      }
    } catch {
      setBranding(DEFAULT_BRANDING);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogoFileUpload = async (file: File) => {
    setLogoUploadError(null);
    setLogoUploadSuccess(null);

    const validTypes = [
      "image/png",
      "image/x-icon",
      "image/vnd.microsoft.icon",
      "image/svg+xml",
      "image/jpeg",
      "image/webp",
    ];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    const validExts = [".png", ".ico", ".svg", ".jpg", ".jpeg", ".webp"];

    if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
      setLogoUploadError("Please upload a valid image file (.png, .ico, .svg, .jpg, .webp)");
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setLogoUploadError("File size exceeds 2 MB limit.");
      return;
    }

    const localPreviewUrl = URL.createObjectURL(file);
    const stagedBranding = {
      ...branding,
      app_logo_url: localPreviewUrl,
    };
    setBranding(stagedBranding);
    updateBranding(stagedBranding);

    setIsUploadingLogo(true);
    try {
      const res = await api.uploadBrandLogo(file);
      if (res.success && res.url) {
        const finalBranding = {
          ...branding,
          app_logo_url: res.url,
        };
        setBranding(finalBranding);
        updateBranding(finalBranding);
        setLogoUploadSuccess(
          `Logo '${res.filename}' uploaded and active in preview! Click 'Save Configuration' to persist permanently.`
        );
      } else {
        setLogoUploadError(res.message || "Failed to upload logo.");
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Upload failed.";
      setLogoUploadError(`Upload error: ${msg}`);
    } finally {
      setIsUploadingLogo(false);
    }
  };

  const updatePaletteColor = (mode: "light" | "dark", key: keyof ThemePalette, value: string) => {
    const targetKey = mode === "light" ? "light_palette" : "dark_palette";
    const defaultPal = mode === "light" ? DEFAULT_LIGHT_PALETTE : DEFAULT_DARK_PALETTE;
    const currentPal = branding[targetKey] || defaultPal;

    const updatedPal = {
      ...currentPal,
      [key]: value,
    };

    const updatedBranding = {
      ...branding,
      [targetKey]: updatedPal,
    };

    setBranding(updatedBranding);
    updateBranding(updatedBranding);
  };

  const applyPreset = (mode: "light" | "dark", presetPalette: ThemePalette) => {
    const targetKey = mode === "light" ? "light_palette" : "dark_palette";
    const updatedBranding = {
      ...branding,
      [targetKey]: presetPalette,
    };
    setBranding(updatedBranding);
    updateBranding(updatedBranding);
  };

  const handleResetSinglePalette = (mode: "light" | "dark") => {
    const def = mode === "light" ? DEFAULT_LIGHT_PALETTE : DEFAULT_DARK_PALETTE;
    applyPreset(mode, def);
    setFeedback({
      type: "success",
      msg: `${mode === "light" ? "Light" : "Dark"} theme palette reset to default in preview. Click 'Save Configuration' to persist.`,
    });
  };

  const handleResetAllThemeDefaults = () => {
    const updatedBranding = {
      ...branding,
      light_palette: DEFAULT_LIGHT_PALETTE,
      dark_palette: DEFAULT_DARK_PALETTE,
    };
    setBranding(updatedBranding);
    updateBranding(updatedBranding);
    setFeedback({
      type: "success",
      msg: "Both Light and Dark theme palettes reset to factory defaults in preview. Click 'Save Configuration' to persist.",
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    setFeedback(null);
    try {
      const payload: BrandingSettings = {
        app_title: branding.app_title || DEFAULT_BRANDING.app_title,
        app_subtitle: branding.app_subtitle || DEFAULT_BRANDING.app_subtitle,
        app_logo_url: branding.app_logo_url || DEFAULT_BRANDING.app_logo_url,
        badge_letter: branding.badge_letter || DEFAULT_BRANDING.badge_letter,
        theme_accent: branding.theme_accent || DEFAULT_BRANDING.theme_accent,
        light_palette: branding.light_palette || DEFAULT_LIGHT_PALETTE,
        dark_palette: branding.dark_palette || DEFAULT_DARK_PALETTE,
      };

      const updated = await api.updateBrandingSettings(payload);
      setBranding(updated);
      updateBranding(updated);
      await refreshBranding();
      setLogoUploadSuccess(null);
      setFeedback({
        type: "success",
        msg: "Brand, Identity & Dual-Theme palettes successfully saved and applied to entire application.",
      });
    } catch (err: any) {
      setFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Failed to save brand settings.",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetAllDefaults = async () => {
    setIsResetting(true);
    setFeedback(null);
    try {
      const def = await api.resetBrandingSettings();
      const finalDef = def || DEFAULT_BRANDING;
      setBranding(finalDef);
      updateBranding(finalDef);
      setLogoUploadSuccess(null);
      setLogoUploadError(null);
      setFeedback({
        type: "success",
        msg: "Brand, identity, and theme palettes restored to system defaults.",
      });
    } catch {
      setBranding(DEFAULT_BRANDING);
      updateBranding(DEFAULT_BRANDING);
      setFeedback({
        type: "success",
        msg: "Brand & theme restored to system defaults in preview. Click 'Save Configuration' to persist.",
      });
    } finally {
      setIsResetting(false);
    }
  };

  const activePalette = paletteMode === "light"
    ? branding.light_palette || DEFAULT_LIGHT_PALETTE
    : branding.dark_palette || DEFAULT_DARK_PALETTE;

  const lightPal = branding.light_palette || DEFAULT_LIGHT_PALETTE;
  const darkPal = branding.dark_palette || DEFAULT_DARK_PALETTE;

  return (
    <div className="flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden">
      <Navbar onRefresh={loadBranding} isRefreshing={isLoading} />

      <main className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
              <Palette className="w-5 h-5 text-indigo-500" />
              <span>Brand & Theme Management Console</span>
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Authoritative single source of truth for application identity, official logos, and independent Light & Dark theme color tokens.
            </p>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap sm:flex-nowrap w-full sm:w-auto">
            <button
              type="button"
              onClick={handleResetAllDefaults}
              disabled={isResetting || isLoading}
              className="px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 shadow-xs min-h-[40px]"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
              <span>Reset All Defaults</span>
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving || isLoading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 min-h-[40px]"
            >
              <Save className={`w-3.5 h-3.5 ${isSaving ? "animate-spin" : ""}`} />
              <span>{isSaving ? "Saving..." : "Save Configuration"}</span>
            </button>
          </div>
        </div>

        {/* Status / Feedback Banner */}
        {feedback && (
          <div
            className={`p-3.5 rounded-xl border flex items-center gap-3 text-xs font-medium animate-fadeIn ${
              feedback.type === "success"
                ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/80 text-emerald-800 dark:text-emerald-300"
                : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/80 text-rose-800 dark:text-rose-300"
            }`}
          >
            {feedback.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
            )}
            <span>{feedback.msg}</span>
          </div>
        )}

        {/* Live Solution-Wide Brand & Dual-Mode Theme Preview */}
        <div className="bg-gradient-to-r from-indigo-900/10 via-sky-900/10 to-transparent dark:from-indigo-950/40 dark:via-sky-950/30 border border-indigo-200/80 dark:border-indigo-800/60 rounded-2xl p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-500" />
                <span>Live Dual-Mode Solution Preview</span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Real-time preview demonstrating side-by-side contrast and appearance in both Light Mode and Dark Mode.
              </p>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 text-[11px] font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Real-time Dynamic Sync Active</span>
            </div>
          </div>

          {/* Dual Mocks: Light vs Dark comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
            {/* 1. Light Mode Mock */}
            <div
              className="rounded-xl p-4 space-y-3 border transition-all"
              style={{
                backgroundColor: lightPal.background,
                borderColor: lightPal.border,
                color: lightPal.text,
              }}
            >
              <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: lightPal.divider }}>
                <div className="flex items-center gap-1.5 text-xs font-bold" style={{ color: lightPal.primary }}>
                  <Sun className="w-3.5 h-3.5" />
                  <span>Light Mode Mockup</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded font-medium" style={{ backgroundColor: lightPal.surface, color: lightPal.text_muted, border: `1px solid ${lightPal.border}` }}>
                  Active Light Palette
                </span>
              </div>

              {/* Mock Header & Card */}
              <div className="rounded-lg p-3 space-y-2.5 border" style={{ backgroundColor: lightPal.surface, borderColor: lightPal.border }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <BrandBadge size="sm" />
                    <div>
                      <div className="text-xs font-semibold" style={{ color: lightPal.text }}>
                        {branding.app_title}
                      </div>
                      <div className="text-[10px]" style={{ color: lightPal.text_muted }}>
                        {branding.app_subtitle}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="px-2.5 py-1 rounded text-[11px] font-semibold transition cursor-pointer"
                    style={{ backgroundColor: lightPal.button, color: lightPal.button_text }}
                  >
                    Button CTA
                  </button>
                </div>

                {/* Mock table snippet */}
                <div className="pt-2 border-t text-[11px] space-y-1.5" style={{ borderColor: lightPal.divider }}>
                  <div className="flex justify-between items-center p-1.5 rounded" style={{ backgroundColor: lightPal.hover }}>
                    <span style={{ color: lightPal.text }}>CLM-FL-2026-001</span>
                    <span className="px-1.5 py-0.2 rounded text-[10px] font-medium" style={{ backgroundColor: lightPal.selected, color: lightPal.primary }}>
                      Matched
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* 2. Dark Mode Mock */}
            <div
              className="rounded-xl p-4 space-y-3 border transition-all"
              style={{
                backgroundColor: darkPal.background,
                borderColor: darkPal.border,
                color: darkPal.text,
              }}
            >
              <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: darkPal.divider }}>
                <div className="flex items-center gap-1.5 text-xs font-bold" style={{ color: darkPal.primary }}>
                  <Moon className="w-3.5 h-3.5" />
                  <span>Dark Mode Mockup</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded font-medium" style={{ backgroundColor: darkPal.surface, color: darkPal.text_muted, border: `1px solid ${darkPal.border}` }}>
                  Active Dark Palette
                </span>
              </div>

              {/* Mock Header & Card */}
              <div className="rounded-lg p-3 space-y-2.5 border" style={{ backgroundColor: darkPal.surface, borderColor: darkPal.border }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <BrandBadge size="sm" />
                    <div>
                      <div className="text-xs font-semibold" style={{ color: darkPal.text }}>
                        {branding.app_title}
                      </div>
                      <div className="text-[10px]" style={{ color: darkPal.text_muted }}>
                        {branding.app_subtitle}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="px-2.5 py-1 rounded text-[11px] font-semibold transition cursor-pointer"
                    style={{ backgroundColor: darkPal.button, color: darkPal.button_text }}
                  >
                    Button CTA
                  </button>
                </div>

                {/* Mock table snippet */}
                <div className="pt-2 border-t text-[11px] space-y-1.5" style={{ borderColor: darkPal.divider }}>
                  <div className="flex justify-between items-center p-1.5 rounded" style={{ backgroundColor: darkPal.hover }}>
                    <span style={{ color: darkPal.text }}>CLM-TX-2026-088</span>
                    <span className="px-1.5 py-0.2 rounded text-[10px] font-medium" style={{ backgroundColor: darkPal.selected, color: darkPal.primary }}>
                      Matched
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Primary Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800">
          <button
            type="button"
            onClick={() => setActiveTab("brand")}
            className={`px-4 py-3 text-xs font-bold transition-all border-b-2 flex items-center gap-2 cursor-pointer ${
              activeTab === "brand"
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/40 dark:bg-indigo-950/20"
                : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Brand & Identity</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("theme")}
            className={`px-4 py-3 text-xs font-bold transition-all border-b-2 flex items-center gap-2 cursor-pointer ${
              activeTab === "theme"
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/40 dark:bg-indigo-950/20"
                : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
            }`}
          >
            <Palette className="w-4 h-4" />
            <span>Theme & Colors</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-mono">
              26 Tokens
            </span>
          </button>
        </div>

        {/* TAB 1: Brand & Identity */}
        {activeTab === "brand" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors animate-fadeIn">
            <div className="border-b border-slate-200 dark:border-slate-800/80 pb-3 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-500" />
                  <span>Application Brand & Identity Attributes</span>
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  Customize the title, subtitle, favicon logo asset, and fallback monogram badge.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Application Title */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Application Title / Brand Name
                </label>
                <input
                  type="text"
                  value={branding.app_title ?? DEFAULT_BRANDING.app_title}
                  onChange={(e) => {
                    const updated = { ...branding, app_title: e.target.value };
                    setBranding(updated);
                    updateBranding(updated);
                  }}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  placeholder="UAIC Orchestrator"
                />
                <p className="text-[10px] text-slate-500">Displayed in sidebar header, page document titles, and notifications.</p>
              </div>

              {/* Application Subtitle */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Application Subtitle / Tagline
                </label>
                <input
                  type="text"
                  value={branding.app_subtitle ?? DEFAULT_BRANDING.app_subtitle}
                  onChange={(e) => {
                    const updated = { ...branding, app_subtitle: e.target.value };
                    setBranding(updated);
                    updateBranding(updated);
                  }}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  placeholder="RPA & Match Engine"
                />
                <p className="text-[10px] text-slate-500">Subtitle displayed under application title in sidebar and headers.</p>
              </div>

              {/* Fallback Badge Letter */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Fallback Badge Letter / Monogram
                </label>
                <input
                  type="text"
                  maxLength={3}
                  value={branding.badge_letter ?? DEFAULT_BRANDING.badge_letter}
                  onChange={(e) => {
                    const updated = { ...branding, badge_letter: e.target.value.toUpperCase() };
                    setBranding(updated);
                    updateBranding(updated);
                  }}
                  className="w-24 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono text-center uppercase"
                  placeholder="U"
                />
                <p className="text-[10px] text-slate-500">Monogram letter rendered when logo image is unavailable.</p>
              </div>

              {/* Brand Logo URL */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Brand Logo / Favicon Asset URL
                </label>
                <input
                  type="text"
                  value={branding.app_logo_url ?? DEFAULT_BRANDING.app_logo_url}
                  onChange={(e) => {
                    const updated = { ...branding, app_logo_url: e.target.value };
                    setBranding(updated);
                    updateBranding(updated);
                  }}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg pl-3 pr-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                  placeholder="/icon.png"
                />
                <p className="text-[10px] text-slate-500">
                  Relative path or URL pointing to your PNG, ICO, or SVG icon.
                </p>
              </div>

              {/* Custom Brand Logo / Icon File Upload */}
              <div className="md:col-span-2 space-y-2 pt-2 border-t border-slate-200 dark:border-slate-800/60">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                      Upload Custom Logo or Favicon Image
                    </label>
                    <p className="text-[11px] text-slate-500">
                      Upload a PNG, SVG, ICO, JPG, or WEBP image (max 2 MB). Live preview applies immediately.
                    </p>
                  </div>
                  {branding.app_logo_url && branding.app_logo_url !== DEFAULT_BRANDING.app_logo_url && (
                    <button
                      type="button"
                      onClick={() => {
                        const resetBranding = {
                          ...branding,
                          app_logo_url: DEFAULT_BRANDING.app_logo_url,
                        };
                        setBranding(resetBranding);
                        updateBranding(resetBranding);
                        setLogoUploadSuccess(null);
                        setLogoUploadError(null);
                      }}
                      className="text-[11px] text-slate-400 hover:text-rose-500 flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-3 h-3" />
                      Reset to Default Icon
                    </button>
                  )}
                </div>

                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDraggingLogo(true);
                  }}
                  onDragLeave={(e) => {
                    e.preventDefault();
                    setIsDraggingLogo(false);
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    setIsDraggingLogo(false);
                    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                      handleLogoFileUpload(e.dataTransfer.files[0]);
                    }
                  }}
                  className={`relative border-2 border-dashed rounded-xl p-4 transition-all flex flex-col items-center justify-center gap-2.5 text-center cursor-pointer ${
                    isDraggingLogo
                      ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 scale-[1.005]"
                      : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30"
                  }`}
                >
                  <input
                    type="file"
                    id="brand-logo-file-input"
                    accept=".png,.ico,.svg,.jpg,.jpeg,.webp,image/*"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleLogoFileUpload(e.target.files[0]);
                      }
                    }}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isUploadingLogo}
                  />

                  <div className="w-10 h-10 rounded-full bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                    {isUploadingLogo ? (
                      <RotateCcw className="w-5 h-5 animate-spin" />
                    ) : (
                      <Upload className="w-5 h-5" />
                    )}
                  </div>

                  <div className="space-y-0.5">
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                      {isUploadingLogo ? "Uploading logo..." : "Click to browse or drag and drop your logo"}
                    </p>
                    <p className="text-[10px] text-slate-400">PNG, ICO, SVG, JPG, or WEBP (Max: 2 MB)</p>
                  </div>
                </div>

                {logoUploadError && (
                  <div className="text-xs text-rose-500 flex items-center gap-1.5 pt-1">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>{logoUploadError}</span>
                  </div>
                )}
                {logoUploadSuccess && (
                  <div className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 pt-1 font-medium bg-emerald-50 dark:bg-emerald-950/30 p-2 rounded-lg border border-emerald-200 dark:border-emerald-800/60">
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    <span>{logoUploadSuccess}</span>
                  </div>
                )}
              </div>

              {/* Built-in Official Icon Presets */}
              <div className="md:col-span-2 pt-2 border-t border-slate-200 dark:border-slate-800/60 space-y-2">
                <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block">
                  Built-in Official Icon Presets:
                </label>
                <div className="flex flex-wrap gap-2.5">
                  {[
                    {
                      label: "Standard Branded Shield (/icon.png)",
                      url: "/icon.png",
                      desc: "Optimized 32x32 UI icon matching favicon",
                    },
                    {
                      label: "High-Res Retina Shield (/apple-icon.png)",
                      url: "/apple-icon.png",
                      desc: "High-DPI 180x180 retina asset",
                    },
                    {
                      label: "Multi-Size ICO Container (/favicon.ico)",
                      url: "/favicon.ico",
                      desc: "Direct browser favicon ICO container",
                    },
                  ].map((preset) => {
                    const isSelected =
                      (branding.app_logo_url ?? DEFAULT_BRANDING.app_logo_url) === preset.url;
                    return (
                      <button
                        key={preset.url}
                        type="button"
                        onClick={() => {
                          const updated = {
                            ...branding,
                            app_logo_url: preset.url,
                          };
                          setBranding(updated);
                          updateBranding(updated);
                        }}
                        className={`px-3 py-2 rounded-xl text-xs font-medium border text-left transition-all flex items-center gap-2.5 cursor-pointer ${
                          isSelected
                            ? "bg-indigo-50 dark:bg-indigo-950/50 border-indigo-500 text-indigo-700 dark:text-indigo-300 shadow-xs ring-1 ring-indigo-500/20"
                            : "bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700"
                        }`}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={preset.url}
                          alt="preset preview"
                          className="w-5 h-5 object-contain rounded bg-slate-900 p-0.5"
                        />
                        <div>
                          <div className="font-semibold text-[11px]">{preset.label}</div>
                          <div className="text-[10px] text-slate-400">{preset.desc}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Theme & Colors */}
        {activeTab === "theme" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors animate-fadeIn">
            {/* Theme Tab Header & Mode Switcher */}
            <div className="border-b border-slate-200 dark:border-slate-800/80 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200 flex items-center gap-2">
                  <Palette className="w-4 h-4 text-indigo-500" />
                  <span>Dual-Theme Design Token Engine</span>
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  Configure independent semantic color tokens for Light Mode and Dark Mode. Changes preview in real-time.
                </p>
              </div>

              {/* Mode Toggle Pills: Light Mode vs Dark Mode */}
              <div className="inline-flex items-center p-1 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 self-start sm:self-auto">
                <button
                  type="button"
                  onClick={() => setPaletteMode("light")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                    paletteMode === "light"
                      ? "bg-white text-indigo-600 shadow-xs dark:bg-slate-900 dark:text-amber-400"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                  }`}
                >
                  <Sun className="w-3.5 h-3.5 text-amber-500" />
                  <span>Light Mode Palette</span>
                </button>
                <button
                  type="button"
                  onClick={() => setPaletteMode("dark")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                    paletteMode === "dark"
                      ? "bg-slate-900 text-indigo-300 shadow-xs dark:bg-indigo-600 dark:text-white"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                  }`}
                >
                  <Moon className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Dark Mode Palette</span>
                </button>
              </div>
            </div>

            {/* Curated Theme Presets for Active Mode */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Sliders className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Curated {paletteMode === "light" ? "Light" : "Dark"} Mode Presets:</span>
                </label>
                <button
                  type="button"
                  onClick={() => handleResetSinglePalette(paletteMode)}
                  className="text-[11px] text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 flex items-center gap-1 cursor-pointer transition-colors"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Reset {paletteMode === "light" ? "Light" : "Dark"} Palette Defaults</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {(paletteMode === "light" ? LIGHT_PRESETS : DARK_PRESETS).map((preset) => {
                  return (
                    <button
                      key={preset.name}
                      type="button"
                      onClick={() => applyPreset(paletteMode, preset.palette)}
                      className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 hover:border-indigo-400 dark:hover:border-indigo-600 text-left transition-all cursor-pointer space-y-2 group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {preset.name}
                        </span>
                        <span
                          className="w-3 h-3 rounded-full border border-black/10"
                          style={{ backgroundColor: preset.palette.primary }}
                        />
                      </div>
                      <p className="text-[10px] text-slate-400 line-clamp-2">
                        {preset.desc}
                      </p>
                      <div className="flex items-center gap-1.5 pt-1">
                        <span className="w-4 h-4 rounded-md border" style={{ backgroundColor: preset.palette.background, borderColor: preset.palette.border }} title="Background" />
                        <span className="w-4 h-4 rounded-md border" style={{ backgroundColor: preset.palette.surface, borderColor: preset.palette.border }} title="Surface" />
                        <span className="w-4 h-4 rounded-md" style={{ backgroundColor: preset.palette.primary }} title="Primary" />
                        <span className="w-4 h-4 rounded-md" style={{ backgroundColor: preset.palette.secondary }} title="Secondary" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Categorized 26 Semantic Design Tokens */}
            <div className="space-y-6 pt-2">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Semantic Token Configuration ({paletteMode === "light" ? "Light Mode" : "Dark Mode"})
                </h4>
                <span className="text-[11px] font-mono text-slate-400">26 Tokens Configurable</span>
              </div>

              <div className="space-y-6">
                {TOKEN_CATEGORIES.map((category) => (
                  <div
                    key={category.title}
                    className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 space-y-3.5"
                  >
                    <div>
                      <h5 className="text-xs font-bold text-slate-900 dark:text-slate-200">
                        {category.title}
                      </h5>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        {category.desc}
                      </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                      {category.tokens.map((token) => {
                        const currentColor = activePalette[token.key] || "#000000";
                        return (
                          <div
                            key={token.key}
                            className="bg-white dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-2 shadow-2xs"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="min-w-0">
                                <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block truncate">
                                  {token.label}
                                </span>
                                <span className="text-[10px] text-slate-400 block truncate" title={token.desc}>
                                  {token.desc}
                                </span>
                              </div>
                              <span className="text-[9px] font-mono text-slate-400 px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 shrink-0">
                                {token.cssVar}
                              </span>
                            </div>

                            {/* Color Picker + Hex Input */}
                            <div className="flex items-center gap-2 pt-1">
                              {/* Native color picker button */}
                              <div className="relative w-8 h-8 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden shrink-0 shadow-2xs cursor-pointer">
                                <input
                                  type="color"
                                  value={currentColor}
                                  onChange={(e) => updatePaletteColor(paletteMode, token.key, e.target.value)}
                                  className="absolute -inset-2 w-12 h-12 cursor-pointer opacity-0"
                                  aria-label={`Select color for ${token.label}`}
                                />
                                <div
                                  className="w-full h-full rounded-lg"
                                  style={{ backgroundColor: currentColor }}
                                />
                              </div>

                              {/* Hex Input */}
                              <input
                                type="text"
                                value={currentColor}
                                onChange={(e) => {
                                  const val = e.target.value;
                                  updatePaletteColor(paletteMode, token.key, val);
                                }}
                                className="flex-1 min-w-0 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1 text-xs font-mono text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 uppercase"
                                placeholder="#000000"
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Bottom Persistent Action Bar */}
        <div className="p-4 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/60 text-xs text-indigo-900 dark:text-indigo-200 flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
            <span>
              All branding and theme tokens update live in your current session and are permanently saved to the server upon clicking <strong>Save Configuration</strong>.
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleResetAllDefaults}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 transition shrink-0 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>Reset Defaults</span>
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-xs transition shrink-0 cursor-pointer disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save Configuration"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
