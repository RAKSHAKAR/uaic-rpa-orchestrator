---
name: uaic-fuzzy-matching
description: >-
  Verify RapidFuzz partial_ratio matching cascade (Claimant -> Insured -> Driver) and 0.60 threshold.
---

# Uaic Fuzzy Matching

## 1. Purpose & Overview
Governs the deduplication and fuzzy match engine (`fuzzy_engine.py`), executing the strict 3-tier cascade and filtering cases by minimum filing date (>= 2010-01-01).

---

## 2. When to Use & When NOT to Use

### When to Use
- Executing or verifying the fuzzy matching deduplication cascade.
- Reviewing fuzzy match candidate scores on `/exceptions` page.

### When NOT to Use
- Raw scraper DOM automation.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Extracted court cases and claim party names (Claimant, Insured, Driver).

### Prerequisites
- RapidFuzz library installed in `backend/.venv`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Case Style Cleaning & Normalization
Strip noise words ('ET AL', 'VS', 'A MINOR', 'INDIVIDUALLY') using `clean_case_style()`.

### Step 2: Filing Date Filtering
Filter out cases filed before minimum filing date (default `>= 2010-01-01`).

### Step 3: Tier 1: Claimant Cascade Evaluation
Evaluate Claimant (first + last) against CaseStyle using `fuzz.partial_ratio()`. If score $\ge 0.60$, match confirmed as CLAIMANT.

### Step 4: Tier 2: Insured Cascade Fallback
If Claimant score < 0.60, evaluate Insured against CaseStyle. If score $\ge 0.60$, match confirmed as INSURED.

### Step 5: Tier 3: Driver Cascade Fallback
If Insured score < 0.60, evaluate Driver against CaseStyle. If score $\ge 0.60$, match confirmed as DRIVER.

### Step 6: Match Result Persistence
Save match result to `MatchResult` table with score, matched party type, and matched party name. Populate `/exceptions` review list.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never alter the cascade order: Claimant MUST be evaluated before Insured, and Insured before Driver.
- Never lower threshold below 0.60 without explicit user authorization.

---

## 6. Expected Deliverables & Artifacts
- Matched court cases linked to claim with confidence scores.
- Populated `/exceptions` human review list.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Cascade strictly evaluates Claimant -> Insured -> Driver.
- [ ] Scores $\ge 0.60$ generate valid `MatchResult` records.
- [ ] Cases filed before 2010-01-01 are filtered out.

---

## 8. Error Recovery & Troubleshooting
- If ambiguous matches occur, route claim to `REVIEW_PENDING` status for human operator approval.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-fuzzy-matching`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-fuzzy-matching` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-fuzzy-matching`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-fuzzy-matching` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-fuzzy-matching`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-fuzzy-matching`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-fuzzy-matching` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Fuzzy Match Cascade)
- `backend/app/services/fuzzy_engine.py`
