---
name: uaic-orchestrator-context
description: >-
  Load the approved UAIC Claim & RPA Orchestrator context, architectural constraints, business rules, and test commands.
---

# Uaic Orchestrator Context

## 1. Purpose & Overview
Provides the essential mental model and architectural invariants for working in the UAIC repository, detailing the 8 Florida/Texas court scrapers, RapidFuzz deduplication cascade, Guidewire integration, and strict directory layout rules.

---

## 2. When to Use & When NOT to Use

### When to Use
- Before making ANY code or architectural change to the UAIC Orchestrator repository.
- Understanding business rules (state routing, DOL 1899-12-30 base date, 9-digit ClaimNumber '0' prefix).

### When NOT to Use
- Generic non-UAIC repositories.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `AGENTS.md` and `README.md` master booklet.

### Prerequisites
- Repository access.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Core Architecture Inspection
Review stack: Next.js 14 App Router, Python 3.14.7 FastAPI, Celery 5.4, Redis, SQLAlchemy 2.0 async, Playwright Chromium, RapidFuzz.

### Step 2: Critical Business Rules Ingestion
Memorize non-negotiable rules: FL/TX state routing logic, DOL date conversion (1899-12-30 base, strict MM/dd/yyyy), 9-digit ClaimNumber gets '0' prefix, RapidFuzz partial_ratio cascade (Claimant -> Insured -> Driver, threshold=0.60), and exact portal output schemas.

### Step 3: Protected Directories Audit
Verify protected directories (`anticaptcha-plugin_v0.83`, `.agents`) remain untouched.

### Step 4: Pre-Change Verification Baseline
Run `pytest -q`, `ruff check app tests`, `tsc --noEmit`, and `check_ps1_syntax.ps1`.

### Step 5: Context Archival
Apply context to all upcoming implementation planning.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never alter business rules (state routing, DOL base date, 9-digit prefix, fuzzy cascade threshold).
- Never create stray files in root; utility scripts must go to `scripts/`.

---

## 6. Expected Deliverables & Artifacts
- Verified operational context.
- Baseline health check report.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Agent demonstrates complete understanding of business rules and repository layout.
- [ ] Protected directories remain intact.
- [ ] Pre-flight tests pass cleanly.

---

## 8. Error Recovery & Troubleshooting
- If in doubt on any architectural convention, consult `AGENTS.md` as the authoritative source.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-orchestrator-context` or load `.agents/skills/uaic-context/SKILL.md`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-orchestrator-context` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-orchestrator-context`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Discovered via `AGENTS.md` in OpenAI Codex. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-orchestrator-context`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-orchestrator-context`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-orchestrator-context` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 1-4 (Project Identity & Rules)
- `.agents/skills/uaic-context/SKILL.md`
