---
name: uaic-project-analysis
description: >-
  Analyse the existing UAIC codebase, Celery task queues, database models, and preserve working court automation.
---

# Uaic Project Analysis

## 1. Purpose & Overview
Conducts deep codebase analysis specifically across the UAIC subsystem implementations (scrapers, browser manager, session runner, matcher, queue runner), mapping execution paths and preventing regressions.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to modifying court scrapers or queue scheduling logic.
- Auditing scraper session lifecycle and browser tab recycling.

### When NOT to Use
- Generic web application tasks.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `backend/app/automation/`, `backend/app/tasks/`, `backend/app/models/`.

### Prerequisites
- Completed `uaic-orchestrator-context`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Scraper Architecture Traversal
Inspect `BasePortalScraper` in `backend/app/automation/base.py`. Analyze CAPTCHA wait loop, token checking, and navigation state resets.

### Step 2: Browser & Tab Manager Inspection
Inspect `ChromeSession`, `TabManager`, and `ExtensionManager` in `browser_manager.py`. Verify single-session multi-tab recycling patterns.

### Step 3: State Routing & Party Deduction
Inspect `generate_unique_names_for_claim()` and DualSearch/TripleSearch matrix in `fuzzy_engine.py`.

### Step 4: Celery Task Pipeline Mapping
Trace task dispatch: `ingest_tasks` -> `queue_runner` -> `scraper_tasks` -> `fuzzy_tasks` -> `guidewire` -> `export_tasks`.

### Step 5: Database Storage Verification
Inspect `fl_jsonbody_*` and `te_jsonbody_*` column mappings in `ClaimRecord`.

### Step 6: Analysis Summary Synthesis
Document UAIC subsystem dependencies and critical invariants.


---

## 5. Safety Considerations & Guardrails
- Never hold DB transactions open during browser automation.
- Preserve synchronous Playwright browser automation for AntiCaptcha MV3 extension stability.

---

## 6. Expected Deliverables & Artifacts
- UAIC Subsystem Deep Analysis Report.
- Scraper and queue pipeline flow diagram.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All 8 scraper implementations and queue bindings are mapped with code references.
- [ ] Browser session recycling lifecycle is verified.
- [ ] Zero project files modified during analysis.

---

## 8. Error Recovery & Troubleshooting
- If scraper logic is unclear, cross-reference Robin subflows in `v4_subflows/`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-project-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-project-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-project-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-project-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-project-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-project-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-project-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/session_runner.py`
- `backend/app/services/fuzzy_engine.py`
