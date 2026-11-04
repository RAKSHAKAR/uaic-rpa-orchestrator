---
name: uaic-data-validation
description: >-
  Validate extracted court case schemas, column boundaries, date normalizations, and noise word filtering.
---

# Uaic Data Validation

## 1. Purpose & Overview
Ensures all court records scraped from Florida and Texas portals strictly conform to the exact 5-field schema (or 4-field for Harris JP/Clerk) and contain zero corrupted rows or static glossary prefixes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Validating extracted cases before persisting to `ScrapedCourtCase` table.
- Testing Excel and CSV import data mapping.

### When NOT to Use
- Frontend UI rendering.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Extracted raw case dictionaries and source portal key.

### Prerequisites
- Knowledge of portal output schemas in `AGENTS.md` Section 3.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Field Presence Validation
For Broward, Hillsborough, Miami, Dallas, Travis, Harris District: confirm exactly 5 fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`). For Harris JP & Harris Clerk: confirm exactly 4 fields (strictly NO `CaseType`).

### Step 2: Static Glossary Filtering
Reject static glossary prefix rows (e.g. `CACE`, `COCE`, `CC`, `DC`) that contain no digits.

### Step 3: Filing Date Normalization
Normalize filing date string to strict `MM/DD/YYYY` format. Filter out invalid dates.

### Step 4: Case Style Trimming
Strip leading/trailing whitespace and normalize internal spaces in `CaseStyle`.

### Step 5: Schema Integrity Assertion
Assert dictionary keys match expected portal schema exactly before database insert.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: NEVER add `CaseType` to Harris JP or Harris County Clerk records.
- Do NOT persist duplicate case numbers for the same claim and portal.

---

## 6. Expected Deliverables & Artifacts
- Validated, sanitized court case records.
- Data validation audit log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All persisted cases conform strictly to target portal schema.
- [ ] Zero static glossary rows exist in database.
- [ ] All filing dates are normalized to `MM/DD/YYYY`.

---

## 8. Error Recovery & Troubleshooting
- If a portal scraper emits missing keys, fix the extraction parsing loop in the respective scraper module.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-data-validation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-data-validation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-data-validation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-data-validation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-data-validation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-data-validation`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-data-validation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Portal Output Schema)
- `backend/app/models/court_case.py`
