---
name: requirement-gap-analysis
description: >-
  Find missing, conflicting, ambiguous, duplicated, or unimplemented requirements between specifications and current codebase reality.
---

# Requirement Gap Analysis

## 1. Purpose & Overview
Compares expected requirements against actual codebase implementation to detect unfulfilled promises, behavioral divergences, dead specifications, or unhandled edge cases before release.

---

## 2. When to Use & When NOT to Use

### When to Use
- Auditing a feature implementation prior to client acceptance testing.
- Comparing modern web orchestration against legacy RPA V4 behavior.
- Evaluating test suite coverage against business requirements.

### When NOT to Use
- Greenfield exploration where no code or specification exists yet.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved Requirements Specification or master booklet (`README.md`).
- Current codebase and test suite results.

### Prerequisites
- Completed `requirement-analysis` and `project-deep-analysis`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Baseline Specification Mapping
Extract all verified requirements from specification documents and project guidelines into an audit checklist.

### Step 2: Codebase & Test Verification Audit
Verify whether each requirement is implemented in source code and backed by automated tests. Check API routes, UI controls, and worker tasks.

### Step 3: Divergence & Conflict Classification
Classify each discrepancy: Missing (not implemented), Incomplete (partially implemented), Conflicting (deviates from spec), or Outdated (spec obsolete).

### Step 4: Impact & Risk Assessment
Assess operational and business risk for each identified gap (e.g. data loss risk, compliance breach, UI failure).

### Step 5: Remediation Plan Formulation
Draft actionable remediation recommendations prioritized by severity (Critical, High, Medium, Low).


---

## 5. Safety Considerations & Guardrails
- Never assume code matches documentation without checking actual source and tests.
- Do not silently delete unfulfilled requirements from documentation.

---

## 6. Expected Deliverables & Artifacts
- Requirement Gap Analysis Report with categorized findings.
- Actionable Remediation Backlog linked to specific file locations.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of specified requirements are audited against actual code implementation.
- [ ] Every gap has an assigned severity, evidence reference, and remediation recommendation.
- [ ] Gaps affecting data integrity or external APIs (Guidewire) are prioritized as Critical.

---

## 8. Error Recovery & Troubleshooting
- If test evidence is inconclusive, write an isolated verification script in `scripts/` to probe live behavior.
- If documentation and code contradict each other, consult `AGENTS.md` and git commit history to determine authoritative intent.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/requirement-gap-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@requirement-gap-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `requirement-gap-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `requirement-gap-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run requirement-gap-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt requirement-gap-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `requirement-gap-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Definition of Done & AI Agent Rules)
- `README.md` - Section on Power Automate V4 Behavioral Parity
