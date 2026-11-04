# Historical Implementation: Frontend Dashboard, UI & Settings System

> **Subsystem:** Next.js 14 App Router, Design Tokens & Settings Persistence  
> **Historical Scope:** October 2026 Engineering Sprints  
> **Status:** Fully Remediated, Benchmarked & Verified  

---

## 1. Next.js 14 Frontend Architecture

Built on Next.js 14 with App Router, TypeScript, and Tailwind CSS:
- `/` — Main Fleet Management Dashboard with interactive stat cards, multi-filter claim grid, and bulk action bar.
- `/claims/[id]` — Claim Detail View with portal tabs, case match cards, and audit timeline.
- `/upload` — Excel/CSV File Ingestion with real-time column mapping preview.
- `/monitor` — Real-time Queue Monitor with worker status, CPU/RAM telemetry, and pause/resume controls.
- `/health` — System Health dashboard displaying status for 8 system components and 8 county portals.
- `/exceptions` — Fuzzy Match Review page for approving or rejecting borderline matches.
- `/settings` — Robot & Automation Configuration forms.
- `/branding` — Centralized brand management and semantic color tokens.
- `/audit` — Audit log trail with JSON payload viewer.
- `/notifications` — Email notification log and live template studio.

---

## 2. Key Remediations & Technical Milestones

### 2.1 Dual Theme System Governance
- Enforced strict Light and Dark mode design tokens with zero OS-level auto-detection (`theme-system` skill).
- The Branding console serves as the single source of truth for 26 semantic color design tokens.

### 2.2 Full-Width Enterprise Layouts
- Removed restrictive max-width containers (`max-w-4xl`, `max-w-6xl`) across all routes in favor of `w-full max-w-none flex-1` enterprise responsive layouts.
- Integrated unified `<Navbar />` with breadcrumb navigation and live system status indicators.

### 2.3 Settings DB Persistence & Secrets Masking
- All robot settings persist in SQLite database via `settings_service.py`.
- Workers read settings dynamically via `get_system_settings_async()`.
- Sensitive credentials (AntiCaptcha key, Guidewire API token, SMTP password) are masked (`********`) in all REST responses and audit logs.

