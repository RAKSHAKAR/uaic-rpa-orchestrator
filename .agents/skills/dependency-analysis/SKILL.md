---
name: dependency-analysis
description: >-
  Review dependency versions, compatibility, known vulnerabilities, licensing, and maintenance status across all package managers.
---

# Dependency Analysis

## 1. Purpose & Overview
Audits external libraries and runtime dependencies across Python (`requirements.txt`, `.venv`) and JavaScript/TypeScript (`package.json`, `package-lock.json`) to prevent security vulnerabilities, version pinning conflicts, and deprecated API usage.

---

## 2. When to Use & When NOT to Use

### When to Use
- Preparing for dependency upgrades or Python/Node runtime updates.
- Pre-release security and licensing compliance audits.
- Diagnosing mysterious build failures caused by transitive package updates.

### When NOT to Use
- Writing internal domain logic with no external dependency changes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `backend/requirements.txt`, `backend/.venv`, `frontend/package.json`, `frontend/package-lock.json`.

### Prerequisites
- Access to package management CLIs (`pip`, `npm`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Package Descriptor Inventory
Parse `backend/requirements.txt` and `frontend/package.json`. Catalogue direct dependencies, version constraints, and development dependencies.

### Step 2: Python Virtualenv Audit
Check installed Python packages against pinned requirements using `.venv\Scripts\pip list --outdated` (passively). Check compatibility with Python 3.14.7.

### Step 3: Frontend NPM Audit
Inspect npm packages for security advisories using `npm audit` (audit-only, no active fix). Check peer dependency compatibility.

### Step 4: License & Deprecation Review
Verify that all third-party dependencies carry permissible open-source licenses (MIT, Apache 2.0, BSD) and identify deprecated packages.

### Step 5: Dependency Health Report
Produce a prioritized dependency audit report detailing upgrade candidates, critical security patches, and potential breaking changes.


---

## 5. Safety Considerations & Guardrails
- Do NOT run `pip install --upgrade` or `npm audit fix --force` without a planned, verified test pass.
- Strictly respect Python 3.14.7 compatibility constraints across all native wheels.

---

## 6. Expected Deliverables & Artifacts
- Comprehensive Dependency Health & Security Audit Report.
- Recommended dependency upgrade path with risk ratings.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of Python and Node dependencies are inventoried with exact pinned versions.
- [ ] Known vulnerabilities and outdated packages are documented with CVE IDs where applicable.
- [ ] Zero package modifications performed during analysis.

---

## 8. Error Recovery & Troubleshooting
- If npm audit reports high severity vulnerabilities, evaluate whether they impact build-time vs. runtime code.
- If pip packages fail under Python 3.14, search for compatible pre-built wheels or pure-Python alternatives.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/dependency-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@dependency-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `dependency-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `dependency-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run dependency-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt dependency-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `dependency-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/requirements.txt`
- `frontend/package.json`
