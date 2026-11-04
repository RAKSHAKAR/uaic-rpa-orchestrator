---
name: diagnose-issue
description: >-
  Collect symptoms, logs, stack traces, and environment state before touching or changing any code.
---

# Diagnose Issue

## 1. Purpose & Overview
Enforces a disciplined diagnostic phase prior to bug fixing, preventing guesswork and avoiding superficial patches that mask underlying systemic defects.

---

## 2. When to Use & When NOT to Use

### When to Use
- Responding to any bug report, unexpected test failure, or system error.
- Diagnosing mysterious scraper timeouts or portal navigation failures.

### When NOT to Use
- Implementing pre-diagnosed and approved changes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Error messages, stack traces, terminal output, reproduction steps, or user symptom descriptions.

### Prerequisites
- Read-only access to application logs (`logs/`, `AuditLog`) and error screenshots (`backend/screenshots/`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Symptom & Environment Collection
Gather exact error strings, HTTP status codes, timestamp, operating system, and active configuration.

### Step 2: Log & Stack Trace Extraction
Inspect application logs (`backend/orchestrator.db`, terminal stdout/stderr, browser console). Extract full traceback.

### Step 3: State & Database Inspection
Query the database to inspect the exact state of affected records at the moment of failure.

### Step 4: Error Screenshot & DOM Review
If a browser automation failure occurred, inspect the corresponding screenshot in `backend/screenshots/` and DOM dump.

### Step 5: Hypothesis Generation & Evidence Testing
Formulate candidate hypotheses. Test each hypothesis against concrete evidence to isolate root cause.

### Step 6: Diagnosis Report Synthesis
Publish a concise Diagnosis Report detailing proven root cause, affected files, and recommended remediation.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Do NOT edit or modify source code during the diagnosis phase.
- Do NOT speculate on root cause without verifiable log or trace evidence.

---

## 6. Expected Deliverables & Artifacts
- Root-Cause Diagnosis Report in `docs/` or session artifact.
- Extracted stack trace and evidence log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Exact root cause is identified with concrete code line references.
- [ ] Evidence (stack trace, error screenshot, or database dump) corroborates the finding.
- [ ] Zero source code files modified during diagnosis.

---

## 8. Error Recovery & Troubleshooting
- If logs are insufficient, author an isolated non-destructive probe script in `scripts/` to gather additional telemetry.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/diagnose-issue`. | `CUSTOM SKILL` |
| **Cursor** | Select `@diagnose-issue` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `diagnose-issue`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `diagnose-issue` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run diagnose-issue`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt diagnose-issue`. | `PROMPT FILE` |
| **Windsurf** | Activate `diagnose-issue` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Diagnose Before Fixing)
- `backend/app/models/error_screenshot.py`
