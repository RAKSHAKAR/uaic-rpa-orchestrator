---
name: dashboard-development
description: >-
  Build functional, real-time operational dashboards with responsive stat cards, filter bars, telemetry grids, and charts.
---

# Dashboard Development

## 1. Purpose & Overview
Guides the creation of high-density executive and operational dashboards that present real-time system metrics, queue depths, throughput charts, and searchable data grids.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring or enhancing main application dashboards (`/`, `/monitor`, `/health`).
- Adding operational stat cards, throughput charts, or batch telemetry views.

### When NOT to Use
- Backend scraper tasks with no UI representation.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Metric definitions, aggregate API endpoints (`/api/v1/claims/stats`), and filter dimensions.

### Prerequisites
- FastAPI stats endpoints and Next.js page routing.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Dashboard Grid Scaffolding
Establish full-width container (`w-full max-w-none flex-1`). Create responsive stat card grid (`grid-cols-2 md:grid-cols-4 lg:grid-cols-8`).

### Step 2: Metric Stat Cards Implementation
Implement clickable stat cards displaying title, count, trend indicator, and active filter state.

### Step 3: Filter Bar & Search Controls
Implement debounced text search, dropdown status filters, date range pickers, and clear-all actions.

### Step 4: Data Grid & Table Integration
Render paginated data table with sortable column headers, status badges, and action buttons.

### Step 5: Real-Time Telemetry & Polling
Implement automatic periodic refresh (e.g. 10s poll) with visual pause toggle for live queue monitoring.

### Step 6: Loading & Empty States
Provide clean skeleton loaders during fetch and helpful empty state illustrations when zero records match filters.


---

## 5. Safety Considerations & Guardrails
- Never allow rapid polling intervals (< 2s) that overload the backend or SQLite database locks.
- Ensure dashboard filters update URL query parameters for shareability.

---

## 6. Expected Deliverables & Artifacts
- Operational dashboard page with interactive stat cards, filters, and data grid.
- Verified responsive layout across desktop and mobile screens.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Stat cards accurately reflect backend database counts.
- [ ] Filtering data table dynamically updates view without full page reloads.
- [ ] Auto-refresh functions reliably without causing memory leaks or UI jitter.

---

## 8. Error Recovery & Troubleshooting
- If polling fails due to network disconnect, back off polling interval and display a discreet reconnecting banner.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/dashboard-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@dashboard-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `dashboard-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `dashboard-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run dashboard-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt dashboard-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `dashboard-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/page.tsx` - Main Claims Dashboard
- `frontend/src/app/monitor/page.tsx` - Queue Monitor Dashboard
