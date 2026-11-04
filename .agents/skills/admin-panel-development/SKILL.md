---
name: admin-panel-development
description: >-
  Implement secure administration workflows, system configuration forms, audit viewers, and bulk operations.
---

# Admin Panel Development

## 1. Purpose & Overview
Provides engineering patterns for administrative consoles (e.g. `/settings`, `/branding`, `/audit`) with elevated privileges, bulk management actions, and tamper-evident audit trails.

---

## 2. When to Use & When NOT to Use

### When to Use
- Building or expanding administrator control panels or robot configuration pages.
- Implementing bulk deletion, bulk retriggering, or system reset functions.

### When NOT to Use
- Standard consumer or read-only user views.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Administrative action definitions, settings schemas, and audit logging endpoints.

### Prerequisites
- Role-based access control or operator authentication.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Tabbed Navigation & Sectioning
Organize administrative controls into tabbed sections (General, Automation, Portals, Email, Proxy, Audit, Branding).

### Step 2: Configuration Form Implementation
Bind controls (toggles, sliders, inputs) to backend `SystemSettings`. Implement save, cancel, and reset-to-defaults actions.

### Step 3: Confirmation Modals for Dangerous Actions
Require explicit typed confirmation modals for destructive operations (e.g. Clean All Records, Clear Redis Queue).

### Step 4: Bulk Action Toolbar
Implement multi-select checkboxes on data grids with bulk start, bulk retry, and bulk export actions.

### Step 5: Audit Logging Integration
Log every administrative setting change and bulk action to `AuditLog` table with timestamp, operator ID, and change diff.

### Step 6: Verification Pass
Test setting persistence across page reloads and backend service restarts.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Always require explicit double-confirmation before executing destructive bulk operations.
- Ensure administrative endpoints verify credentials on the backend, not merely via hidden UI buttons.

---

## 6. Expected Deliverables & Artifacts
- Secure administrative management page with verified settings persistence.
- Audit trail capturing all administrative actions.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Settings changes persist in database and reload accurately across sessions.
- [ ] Dangerous bulk actions require explicit confirmation dialog.
- [ ] All administrative mutations generate immutable audit log records.

---

## 8. Error Recovery & Troubleshooting
- If saving settings fails due to validation errors, display field-specific error highlights and preserve user inputs.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/admin-panel-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@admin-panel-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `admin-panel-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `admin-panel-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run admin-panel-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt admin-panel-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `admin-panel-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/settings/page.tsx`
- `backend/app/api/v1/endpoints/settings.py`
