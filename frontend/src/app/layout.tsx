import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ResponsiveShell } from "../components/ResponsiveShell";
import { ThemeProvider } from "../components/ThemeProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "UAIC Claim & RPA Orchestrator",
  description: "Modern distributed claim ingestion, county court scraping, and fuzzy matching platform",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon.png", type: "image/png", sizes: "32x32" },
    ],
    apple: [
      { url: "/apple-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.className} bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 h-screen overflow-hidden flex w-full antialiased transition-colors duration-200`}
      >
        <ThemeProvider>
          <ResponsiveShell>{children}</ResponsiveShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
