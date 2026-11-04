---
name: project-documentation-analysis
description: >-
  Read existing specifications, operator manuals, and implementation plans; reconcile them with actual repository reality.
---

# Project Documentation Analysis

## 1. Purpose & Overview
Audits existing project documentation (`README.md`, `docs/`, `AGENTS.md`, operator manuals) against the actual codebase to identify stale guides, dead documentation, and missing operational instructions.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to updating `README.md` or writing new subsystem documentation.
- Following major feature implementations or architectural refactoring.
- Onboarding new operators or preparing production handovers.

### When NOT to Use
- Executing code changes that do not touch documented interfaces.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- All markdown files in `docs/` and root documentation (`README.md`, `AGENTS.md`, `DEPLOYMENT.md`).

### Prerequisites
- Access to current codebase to verify documented commands and endpoints.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Documentation Inventory & Indexing
Catalogue all markdown files in root, `docs/`, and `implementation_plan/`. Record document title, date, version, and declared scope.

### Step 2: Command & Endpoint Cross-Verification
Verify documented shell commands, API routes, and script paths against reality. Check if documented endpoints exist in `app/api/v1/endpoints/`.

### Step 3: Configuration & Settings Drift Audit
Compare documented settings keys with `SystemSettings` schema in `app/schemas/settings.py`.

### Step 4: Discrepancy Cataloguing
Log all documentation drift: outdated URLs, obsolete parameters, dead screenshots, or deprecated scripts.

### Step 5: Documentation Synchronization Plan
Formulate a prioritized list of documentation updates required to bring docs into 100% alignment with code.


---

## 5. Safety Considerations & Guardrails
- NEVER replace comprehensive project booklets (`README.md`) with simplified summaries.
- Preserve historical implementation records in `docs/` for auditability.

---

## 6. Expected Deliverables & Artifacts
- Documentation Drift & Reconciled Audit Report.
- Actionable Documentation Sync Checklist.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All documentation files in `docs/` and root are audited against codebase reality.
- [ ] Every documented API route, shell command, and settings key is verified.
- [ ] Stale or conflicting documentation is catalogued with required corrections.

---

## 8. Error Recovery & Troubleshooting
- If a documented feature appears missing in code, check recent git commits or branch history before marking it dead.
- If contradictory documentation exists, `AGENTS.md` and `README.md` take precedence.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/project-documentation-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@project-documentation-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `project-documentation-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `project-documentation-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run project-documentation-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt project-documentation-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `project-documentation-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `README.md` - Master Architectural Booklet
- `docs/` - Operational Guides & Implementation Records
