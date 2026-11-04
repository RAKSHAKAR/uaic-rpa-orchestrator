---
name: dependency-cleanup
description: >-
  Remove or replace unused, deprecated, or vulnerable dependencies safely across Python and Node ecosystems.
---

# Dependency Cleanup

## 1. Purpose & Overview
Audits and purges unused third-party packages from `requirements.txt` and `package.json`, reducing bundle sizes, installation times, and attack surfaces.

---

## 2. When to Use & When NOT to Use

### When to Use
- Following refactoring where external libraries were replaced with native code.
- Resolving security advisories for unmaintained dependencies.

### When NOT to Use
- Removing dependencies without verifying transitive usage.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Dependency candidate list, `requirements.txt`, `package.json`.

### Prerequisites
- Working virtual environment and clean package lockfiles.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Import Scanning
Scan all Python files for `import <pkg>` and frontend files for `from '<pkg>'`. Confirm zero active imports.

### Step 2: Package Descriptors Update
Remove package entry from `backend/requirements.txt` or run `npm uninstall <pkg>` in `frontend/`.

### Step 3: Lockfile Regeneration
Regenerate lockfiles cleanly without extraneous modifications.

### Step 4: Clean Environment Build & Test Pass
Run fresh test execution to verify no transitive runtime crashes occur.

### Step 5: Cleanup Summary
Document removed packages and package size savings.


---

## 5. Safety Considerations & Guardrails
- Never remove core runtime packages (FastAPI, Celery, SQLAlchemy, Playwright, RapidFuzz, Next.js).
- Verify dependencies are not loaded dynamically or utilized exclusively in test fixtures.

---

## 6. Expected Deliverables & Artifacts
- Updated `requirements.txt` and `package.json`.
- Verification test report confirming full platform stability.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Removed packages have zero active imports in the repository.
- [ ] `pytest` and `npm run build` pass cleanly after removal.
- [ ] Lockfiles are consistent and free of corruption.

---

## 8. Error Recovery & Troubleshooting
- If uninstallation causes missing module errors during runtime, restore the dependency and check dynamic usage.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/dependency-cleanup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@dependency-cleanup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `dependency-cleanup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `dependency-cleanup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run dependency-cleanup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt dependency-cleanup`. | `PROMPT FILE` |
| **Windsurf** | Activate `dependency-cleanup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/requirements.txt`
- `frontend/package.json`
