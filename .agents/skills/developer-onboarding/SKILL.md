---
name: developer-onboarding
description: >-
  Create a practical, streamlined onboarding path for new developers with prerequisites and initial verification tests.
---

# Developer Onboarding

## 1. Purpose & Overview
Provides a comprehensive, friction-free onboarding guide enabling new software engineers to clone the repository, install dependencies, launch services, and run their first green test pass within 15 minutes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Onboarding new team members or AI coding agents.
- Re-verifying workstation setup prerequisites after major dependency upgrades.

### When NOT to Use
- Advanced production operations.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Workstation prerequisites (Python 3.14.7, Node.js 18+, Redis, Git, Chrome) and repo setup commands.

### Prerequisites
- Working local development environment.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Prerequisites Checklist
Enumerate required tooling with download links and exact verified versions: Python 3.14.7, Node 18+, Git, Redis for Windows, Google Chrome.

### Step 2: Step-by-Step Repository Setup
Provide ordered shell commands: clone repository, run virtualenv setup, install pip requirements, install npm packages, and install Playwright Chromium.

### Step 3: First Green Test Pass
Instruct developer to run `backend\.venv\Scripts\pytest -q` to confirm all 556 tests pass out of the box.

### Step 4: Local Service Launch
Instruct developer to execute `setup_local.ps1` and verify UI opens at `http://localhost:3000`.

### Step 5: Key Architectural Pointers
Highlight critical files to read first: `AGENTS.md`, `README.md`, `backend/app/main.py`, and `frontend/src/app/page.tsx`.

### Step 6: Publish Onboarding Manual
Publish in `docs/DEVELOPMENT_WORKFLOW.md`.


---

## 5. Safety Considerations & Guardrails
- Ensure onboarding steps do not require administrator privileges where avoidable.
- Never instruct developers to edit `.env` with live production secrets.

---

## 6. Expected Deliverables & Artifacts
- Streamlined Developer Onboarding Guide in `docs/DEVELOPMENT_WORKFLOW.md`.
- Prerequisite verification script.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] A new developer can set up and run the full stack within 15 minutes.
- [ ] First test pass executes cleanly with 556 passing tests.
- [ ] Core architectural rules and conventions are clearly communicated.

---

## 8. Error Recovery & Troubleshooting
- If new developers encounter Windows execution policy blocks, include `-ExecutionPolicy Bypass` in launcher instructions.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/developer-onboarding`. | `CUSTOM SKILL` |
| **Cursor** | Select `@developer-onboarding` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `developer-onboarding`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `developer-onboarding` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run developer-onboarding`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt developer-onboarding`. | `PROMPT FILE` |
| **Windsurf** | Activate `developer-onboarding` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/DEVELOPMENT_WORKFLOW.md`
- `AGENTS.md` - Section 2 (Repository Layout)
