---
name: managing-python-dependencies
description: >-
  Enforce Python 3.14.7 virtual environment isolation, avoid global pip modifications, and maintain dependency consistency.
---

# Managing Python Dependencies

## 1. Purpose & Overview
Ensures proper Python dependency management within the dedicated `backend/.venv` virtual environment, strictly prohibiting global `pip install` modifications.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding, upgrading, or modifying Python packages in `backend/`.
- Before executing Python scripts via the terminal to ensure the correct virtual environment is active.

### When NOT to Use
- Frontend npm package management.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `backend/requirements.txt`, target package name, and Python 3.14.7 virtualenv.

### Prerequisites
- Active `backend/.venv` virtual environment.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Virtualenv Active Check
Verify virtualenv: execute `.venv\Scripts\python.exe -c 'import sys; print(sys.executable)'`.

### Step 2: Target Package Specification
Add package with exact pinned version to `backend/requirements.txt`.

### Step 3: Virtualenv Installation
Install package strictly into virtual environment: `.venv\Scripts\pip.exe install -r requirements.txt`.

### Step 4: Conflict & Compatibility Audit
Verify package installs clean C-extension wheels compatible with Python 3.14.7 on Windows.

### Step 5: Test Verification
Execute `pytest` to confirm newly installed package causes zero dependency regressions.

### Step 6: Lockfile Consistency
Ensure `requirements.txt` remains the single authoritative source of Python dependencies.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: NEVER run global `pip install` on the host machine.
- Always pin exact versions to prevent breaking transitive updates.

---

## 6. Expected Deliverables & Artifacts
- Updated `backend/requirements.txt`.
- Isolated virtual environment with verified packages.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All packages installed strictly within `backend/.venv`.
- [ ] Python 3.14.7 compatibility verified.
- [ ] All backend tests pass cleanly.

---

## 8. Error Recovery & Troubleshooting
- If a package fails to install on Python 3.14, search for compatible pre-built wheels or pure-Python alternatives.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/managing-python-dependencies`. | `CUSTOM SKILL` |
| **Cursor** | Select `@managing-python-dependencies` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `managing-python-dependencies`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `managing-python-dependencies` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run managing-python-dependencies`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt managing-python-dependencies`. | `PROMPT FILE` |
| **Windsurf** | Activate `managing-python-dependencies` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/requirements.txt`
- `AGENTS.md` - Section 8
