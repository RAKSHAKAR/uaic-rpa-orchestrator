"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { BrandingSettings, ThemePalette } from "../types";
import { api } from "../lib/api";

export const DEFAULT_LIGHT_PALETTE: ThemePalette = {
  primary: "#4f46e5",
  secondary: "#0ea5e9",
  accent: "#6366f1",
  background: "#f8fafc",
  surface: "#ffffff",
  card: "#ffffff",
  header: "#ffffff",
  sidebar: "#ffffff",
  text: "#0f172a",
  text_muted: "#64748b",
  border: "#e2e8f0",
  divider: "#e2e8f0",
  input_background: "#f8fafc",
  input_text: "#0f172a",
  button: "#4f46e5",
  button_text: "#ffffff",
  link: "#4f46e5",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
  info: "#3b82f6",
  focus: "#6366f1",
  hover: "#f1f5f9",
  active: "#e2e8f0",
  selected: "#e0e7ff",
  disabled: "#94a3b8",
};

export const DEFAULT_DARK_PALETTE: ThemePalette = {
  primary: "#6366f1",
  secondary: "#38bdf8",
  accent: "#818cf8",
  background: "#020617",
  surface: "#0f172a",
  card: "#0f172a",
  header: "#020617",
  sidebar: "#020617",
  text: "#f8fafc",
  text_muted: "#94a3b8",
  border: "#1e293b",
  divider: "#1e293b",
  input_background: "#020617",
  input_text: "#f8fafc",
  button: "#4f46e5",
  button_text: "#ffffff",
  link: "#818cf8",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
  info: "#38bdf8",
  focus: "#818cf8",
  hover: "#1e293b",
  active: "#334155",
  selected: "#312e81",
  disabled: "#64748b",
};

export const DEFAULT_BRANDING: BrandingSettings = {
  app_title: "UAIC Orchestrator",
  app_subtitle: "RPA & Match Engine",
  app_logo_url: "/icon.png",
  badge_letter: "U",
  theme_accent: "indigo",
  light_palette: DEFAULT_LIGHT_PALETTE,
  dark_palette: DEFAULT_DARK_PALETTE,
};

export function applyThemeTokens(
  lightPalette: ThemePalette = DEFAULT_LIGHT_PALETTE,
  darkPalette: ThemePalette = DEFAULT_DARK_PALETTE
) {
  if (typeof document === "undefined") return;
  const styleId = "uaic-dynamic-theme-tokens";
  let styleEl = document.getElementById(styleId) as HTMLStyleElement | null;
  if (!styleEl) {
    styleEl = document.createElement("style");
    styleEl.id = styleId;
    document.head.appendChild(styleEl);
  }

  const formatVars = (p: ThemePalette) => `
    --color-primary: ${p.primary};
    --color-secondary: ${p.secondary};
    --color-accent: ${p.accent};
    --color-background: ${p.background};
    --color-surface: ${p.surface};
    --color-card: ${p.card};
    --color-header: ${p.header};
    --color-sidebar: ${p.sidebar};
    --color-text: ${p.text};
    --color-text-muted: ${p.text_muted};
    --color-border: ${p.border};
    --color-divider: ${p.divider};
    --color-input-background: ${p.input_background};
    --color-input-text: ${p.input_text};
    --color-button: ${p.button};
    --color-button-text: ${p.button_text};
    --color-link: ${p.link};
    --color-success: ${p.success};
    --color-warning: ${p.warning};
    --color-error: ${p.error};
    --color-info: ${p.info};
    --color-focus: ${p.focus};
    --color-hover: ${p.hover};
    --color-active: ${p.active};
    --color-selected: ${p.selected};
    --color-disabled: ${p.disabled};
  `;

  styleEl.textContent = `
    :root, [data-theme="light"] {
      ${formatVars(lightPalette)}
    }
    .dark, [data-theme="dark"] {
      ${formatVars(darkPalette)}
    }
  `;
}

interface BrandingContextType {
  branding: BrandingSettings;
  updateBranding: (updates: Partial<BrandingSettings>) => void;
  refreshBranding: () => Promise<void>;
  isLoading: boolean;
}

const BrandingContext = createContext<BrandingContextType>({
  branding: DEFAULT_BRANDING,
  updateBranding: () => {},
  refreshBranding: async () => {},
  isLoading: false,
});

export const BrandingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [branding, setBranding] = useState<BrandingSettings>(DEFAULT_BRANDING);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshBranding = useCallback(async () => {
    try {
      const data = await api.getSettings();
      if (data?.branding) {
        const light = data.branding.light_palette
          ? { ...DEFAULT_LIGHT_PALETTE, ...data.branding.light_palette }
          : DEFAULT_LIGHT_PALETTE;
        const dark = data.branding.dark_palette
          ? { ...DEFAULT_DARK_PALETTE, ...data.branding.dark_palette }
          : DEFAULT_DARK_PALETTE;

        const merged: BrandingSettings = {
          app_title: data.branding.app_title || DEFAULT_BRANDING.app_title,
          app_subtitle: data.branding.app_subtitle || DEFAULT_BRANDING.app_subtitle,
          app_logo_url: data.branding.app_logo_url || DEFAULT_BRANDING.app_logo_url,
          badge_letter: data.branding.badge_letter || DEFAULT_BRANDING.badge_letter,
          theme_accent: data.branding.theme_accent || DEFAULT_BRANDING.theme_accent,
          light_palette: light,
          dark_palette: dark,
        };
        setBranding(merged);
        applyThemeTokens(light, dark);
      } else {
        applyThemeTokens(DEFAULT_LIGHT_PALETTE, DEFAULT_DARK_PALETTE);
      }
    } catch {
      applyThemeTokens(DEFAULT_LIGHT_PALETTE, DEFAULT_DARK_PALETTE);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshBranding();
  }, [refreshBranding]);

  const updateBranding = useCallback((updates: Partial<BrandingSettings>) => {
    setBranding((prev) => {
      const next = { ...prev, ...updates };
      if (typeof document !== "undefined" && next.app_title) {
        document.title = `${next.app_title} — ${next.app_subtitle}`;
      }
      applyThemeTokens(
        next.light_palette || DEFAULT_LIGHT_PALETTE,
        next.dark_palette || DEFAULT_DARK_PALETTE
      );
      return next;
    });
  }, []);

  // Sync document title on mount & change
  useEffect(() => {
    if (typeof document !== "undefined" && branding.app_title) {
      document.title = `${branding.app_title} — ${branding.app_subtitle}`;
    }
  }, [branding.app_title, branding.app_subtitle]);

  return (
    <BrandingContext.Provider
      value={{
        branding,
        updateBranding,
        refreshBranding,
        isLoading,
      }}
    >
      {children}
    </BrandingContext.Provider>
  );
};

export const useBranding = () => useContext(BrandingContext);

/**
 * Reusable BrandBadge component that displays the configured logo image asset
 * (e.g. /icon.png from favicon.ico creation) with graceful fallback to badge letter.
 */
export const BrandBadge: React.FC<{
  size?: "sm" | "md" | "lg";
  className?: string;
}> = ({ size = "md", className = "" }) => {
  const { branding } = useBranding();
  const [imgError, setImgError] = useState(false);

  // Reset error state if the logo URL changes
  useEffect(() => {
    setImgError(false);
  }, [branding.app_logo_url]);

  const dimensionClasses = {
    sm: "w-7 h-7 rounded-lg text-xs",
    md: "w-8 h-8 rounded-lg text-sm",
    lg: "w-10 h-10 rounded-xl text-base",
  }[size];

  const iconDimension = {
    sm: "w-5 h-5",
    md: "w-6 h-6",
    lg: "w-7 h-7",
  }[size];

  return (
    <div
      className={`relative bg-gradient-to-br from-indigo-500 to-sky-500 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20 shrink-0 overflow-hidden select-none transition-all ${dimensionClasses} ${className}`}
      title={branding.app_title}
      aria-label={`${branding.app_title} brand icon`}
    >
      {!imgError && branding.app_logo_url ? (
        /* eslint-disable-next-line @next/next/no-img-element */
        <img
          src={branding.app_logo_url}
          alt={branding.app_title}
          className={`${iconDimension} object-contain transition-transform duration-200 group-hover:scale-105`}
          onError={() => setImgError(true)}
        />
      ) : (
        <span>{branding.badge_letter || "U"}</span>
      )}
    </div>
  );
};
