import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercent(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

export function formatDate(dateString?: string): string {
  if (!dateString || dateString.trim() === "" || dateString.toLowerCase() === "n/a" || dateString === "-") return "-";
  try {
    // Check regex match for MM/DD/YYYY or DD/MM/YYYY or MM-DD-YYYY
    const usMatch = dateString.match(/(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})/);
    if (usMatch) {
      let p1 = parseInt(usMatch[1], 10);
      let p2 = parseInt(usMatch[2], 10);
      if (p1 > 12 && p2 <= 12) {
        // DD/MM/YYYY format
        const temp = p1;
        p1 = p2;
        p2 = temp;
      }
      const m = p1 - 1;
      const d = p2;
      let y = parseInt(usMatch[3], 10);
      if (y < 100) y += y < 50 ? 2000 : 1900;
      const dateObj = new Date(y, m, d);
      return dateObj.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
    }
    // Check ISO format YYYY-MM-DD
    const isoMatch = dateString.match(/(\d{4})[/-](\d{1,2})[/-](\d{1,2})/);
    if (isoMatch) {
      const y = parseInt(isoMatch[1], 10);
      const m = parseInt(isoMatch[2], 10) - 1;
      const d = parseInt(isoMatch[3], 10);
      const dateObj = new Date(y, m, d);
      return dateObj.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
    }
    const d = new Date(dateString);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
    }
    return dateString;
  } catch {
    return dateString;
  }
}
