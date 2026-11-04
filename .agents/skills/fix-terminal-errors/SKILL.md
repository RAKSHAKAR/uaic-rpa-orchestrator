---
name: fix-terminal-errors
description: >-
  Resolve command execution failures, process startup crashes, port collisions, and virtual environment path errors.
---

# Fix Terminal Errors

## 1. Purpose & Overview
Diagnoses and fixes terminal startup failures, port collisions (e.g. 8000, 3000, 6379), path resolution defects, and PowerShell script syntax errors.

---

## 2. When to Use & When NOT to Use

### When to Use
- `setup_local.ps1` or background processes fail to launch.
- Port collision errors (`Errno 10048`, `Address already in use`).
- Python module not found errors due to virtualenv desynchronization.

### When NOT to Use
- Browser UI layout defects.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Terminal command string, error output, and exit code.

### Prerequisites
- PowerShell execution privileges.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Process & Port Collision Inspection
Identify colliding ports (8000, 3000, 6379) using `Get-NetTCPConnection` or `scripts/check_python_procs.ps1`.

### Step 2: Zombie Process Termination
Terminate orphan Python, Node, or Celery processes holding the ports using clean process IDs via `scripts/clean_stale_workers.py`.

### Step 3: Virtualenv Path Validation
Verify Python interpreter points to `backend\.venv\Scripts\python.exe` and has required modules in `sys.path`.

### Step 4: PowerShell Syntax Audit
If a `.ps1` script fails, execute `scripts/check_ps1_syntax.ps1` to detect syntax or parameter parsing errors.

### Step 5: Clean Startup Rerun
Re-execute the launcher script (`setup_local.ps1`) and verify all services start persistently and report healthy status.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: PowerShell launcher (`setup_local.ps1`) must be persistent, interactive, and NEVER auto-close unexpectedly.
- Do not kill external processes unrelated to the project.

---

## 6. Expected Deliverables & Artifacts
- Patched PowerShell scripts or launcher configurations.
- Clean terminal execution log confirming healthy service startup.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Services bind to expected ports cleanly without collision.
- [ ] All `.ps1` scripts pass `check_ps1_syntax.ps1` with 0 errors.
- [ ] Background processes remain healthy and persistent.

---

## 8. Error Recovery & Troubleshooting
- If ports remain locked by Windows kernel, wait 30 seconds for TIME_WAIT socket cleanup or restart host service.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-terminal-errors`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-terminal-errors` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-terminal-errors`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-terminal-errors` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-terminal-errors`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-terminal-errors`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-terminal-errors` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `setup_local.ps1`
- `scripts/check_ps1_syntax.ps1`
