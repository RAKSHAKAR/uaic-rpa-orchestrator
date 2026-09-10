"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type Theme = "dark" | "light";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  isMounted: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [theme, setThemeState] = useState<Theme>("dark");
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("uaic_theme") as Theme | null;
    const initialTheme: Theme = saved === "light" || saved === "dark" ? saved : "dark";
    setThemeState(initialTheme);
    document.documentElement.classList.remove("light", "dark");
    document.documentElement.classList.add(initialTheme);
    document.documentElement.setAttribute("data-theme", initialTheme);
    setIsMounted(true);

    // Suppress third-party / Edge DevTools injected VM script errors (e.g. reportAllChanges startTime race condition)
    const handleWindowError = (event: ErrorEvent) => {
      const msg = event?.message || "";
      const filename = event?.filename || "";
      if (
        msg.includes("startTime") ||
        msg.includes("reportAllChanges") ||
        (filename.startsWith("VM") && msg.includes("Cannot read properties of undefined"))
      ) {
        event.preventDefault?.();
        event.stopImmediatePropagation?.();
        return true;
      }
    };

    window.addEventListener("error", handleWindowError, true);
    return () => {
      window.removeEventListener("error", handleWindowError, true);
    };
  }, []);

  const setTheme = (t: Theme) => {
    setThemeState(t);
    if (typeof window !== "undefined") {
      localStorage.setItem("uaic_theme", t);
      document.documentElement.classList.remove("light", "dark");
      document.documentElement.classList.add(t);
      document.documentElement.setAttribute("data-theme", t);
    }
  };

  const toggleTheme = () => {
    setThemeState((prev) => {
      const next: Theme = prev === "dark" ? "light" : "dark";
      if (typeof window !== "undefined") {
        localStorage.setItem("uaic_theme", next);
        document.documentElement.classList.remove("light", "dark");
        document.documentElement.classList.add(next);
        document.documentElement.setAttribute("data-theme", next);
      }
      return next;
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme, isMounted }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    return {
      theme: "dark",
      toggleTheme: () => {},
      setTheme: () => {},
      isMounted: false,
    };
  }
  return context;
};
