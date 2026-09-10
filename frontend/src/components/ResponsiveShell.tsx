"use client";

import React from "react";
import { Sidebar } from "./Sidebar";
import { MobileBottomNav } from "./MobileBottomNav";
import { MobileDrawer } from "./MobileDrawer";
import { NavigationProvider, useNavigation } from "./NavigationContext";

import { Footer } from "./Footer";
import { CommandPalette } from "./CommandPalette";
import { BrandingProvider } from "./BrandingContext";

const ShellInner: React.FC<{ children: React.ReactNode }> = ({ children }) => {

  const { isDrawerOpen, closeDrawer } = useNavigation();
  const [isPdfExport, setIsPdfExport] = React.useState(false);

  React.useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      setIsPdfExport(params.get("pdf_export") === "true");
    }
  }, []);

  if (isPdfExport) {
    return (
      <div className="flex w-full min-h-screen bg-slate-950 text-slate-100 p-0 m-0">
        <div className="flex-1 flex flex-col w-full min-w-0 p-0 m-0">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full min-h-screen relative overflow-x-clip bg-slate-50 dark:bg-slate-950 transition-colors">
      {/* Top area: Sidebar + Main Content */}
      <div className="flex-1 flex w-full min-w-0 relative">
        {/* Desktop & Tablet Sidebar */}
        <div className="no-print hidden md:flex shrink-0 w-56 lg:w-64 relative border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
          <div className="sticky top-0 h-screen w-56 lg:w-64 overflow-y-auto">
            <Sidebar />
          </div>
        </div>

        {/* Slide-over Mobile Drawer for Phone Viewports */}
        <div className="no-print">
          <MobileDrawer isOpen={isDrawerOpen} onClose={closeDrawer} />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col w-full min-w-0 pb-6 md:pb-0">
          {children}
        </div>
      </div>

      {/* Full Active Screen Width Footer with Mobile Bottom Nav Clearance */}
      <div className="w-full shrink-0 z-20 pb-[calc(4.75rem+env(safe-area-inset-bottom,0px))] md:pb-0">
        <Footer />
      </div>

      {/* Dedicated Fixed Mobile Footer Navigation */}
      <div className="no-print">
        <MobileBottomNav />
      </div>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette />
    </div>
  );
};


export const ResponsiveShell: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <NavigationProvider>
      <BrandingProvider>
        <ShellInner>{children}</ShellInner>
      </BrandingProvider>
    </NavigationProvider>
  );
};
