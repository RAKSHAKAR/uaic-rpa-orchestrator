---
name: duplicate-code-detection
description: >-
  Identify duplicated logic, copy-pasted helper functions, repetitive UI patterns, and redundant scraper routines.
---

# Duplicate Code Detection

## 1. Purpose & Overview
Detects structural duplication across Python scrapers, API endpoints, and React components, recommending clean abstractions to reduce maintenance overhead and bug propagation.

---

## 2. When to Use & When NOT to Use

### When to Use
- Auditing scraper implementations across the 8 court portals.
- Standardizing error handling or date formatting logic across services.
- Refactoring repetitive UI form components or stat cards.

### When NOT to Use
- Accidental syntactic similarity across completely unrelated business domains.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target directories (`backend/app/automation/`, `frontend/src/components/`).

### Prerequisites
- Understanding of DRY (Don't Repeat Yourself) principles and when duplication is preferable to wrong abstraction.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Static Similarity Scanning
Scan codebase for duplicated blocks: date formatting, table parsing, CAPTCHA wait loops, and API error formatting.

### Step 2: Duplication Classification
Classify duplication: Exact Duplication (identical code), Semantic Duplication (same logic, different variable names), or Incidental Duplication.

### Step 3: Consolidation Proposal
Design a shared abstraction (e.g. `BasePortalScraper` helper method or shared React hook).

### Step 4: Impact & Blast Radius Check
Verify which callers will be affected by consolidating the duplicated routines.

### Step 5: Consolidation & Regression Verification
Extract shared routine, update callers, and execute automated test suites.


---

## 5. Safety Considerations & Guardrails
- Do NOT force artificial abstractions onto portals with subtle DOM differences.
- Ensure portal-specific output schemas (e.g. no `CaseType` for Harris JP/Clerk) remain strictly preserved.

---

## 6. Expected Deliverables & Artifacts
- Duplication Audit Report detailing redundant patterns.
- Consolidated shared helper modules with comprehensive test coverage.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Identified duplicated code blocks are replaced with a single shared function.
- [ ] All affected modules pass their unit tests without behavior changes.
- [ ] Portal output schemas remain 100% compliant with specifications.

---

## 8. Error Recovery & Troubleshooting
- If a shared abstraction causes regressions in one specific scraper, decouple that scraper with an override method.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/duplicate-code-detection`. | `CUSTOM SKILL` |
| **Cursor** | Select `@duplicate-code-detection` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `duplicate-code-detection`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `duplicate-code-detection` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run duplicate-code-detection`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt duplicate-code-detection`. | `PROMPT FILE` |
| **Windsurf** | Activate `duplicate-code-detection` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/base.py`
- `AGENTS.md` - Section 3 (Portal Output Schema)
