---
name: ci-cd-setup
description: >-
  Configure automated quality gates, linting, type-checking, and test pipelines in GitHub Actions.
---

# Ci Cd Setup

## 1. Purpose & Overview
Maintains continuous integration workflows (`.github/workflows/ci.yml`), enforcing automated verification on every push and pull request before code can be merged.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring or updating GitHub Actions CI pipelines.
- Adding automated security scanning, linting, or E2E test jobs to CI.

### When NOT to Use
- Local test execution.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- GitHub Actions workflow files in `.github/workflows/`.

### Prerequisites
- Git repository connected to GitHub.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Workflow Trigger Configuration
Configure triggers: `on: [push, pull_request]` targeting `main` branch.

### Step 2: Matrix & Environment Setup
Set up matrix runner with Python 3.14 and Node 18+ on `ubuntu-latest` or `windows-latest`.

### Step 3: Backend Quality Jobs
Configure steps: Install dependencies, run `ruff check`, execute `pytest` unit & integration test suites.

### Step 4: Frontend Quality Jobs
Configure steps: `npm ci`, run `npx tsc --noEmit`, run `npm run lint`, and test `npm run build`.

### Step 5: Artifact & Report Archival
Upload test coverage reports, failure logs, and lint summaries as workflow artifacts.

### Step 6: Local Workflow Validation
Validate YAML syntax using schema linters or local runner (`act`).


---

## 5. Safety Considerations & Guardrails
- Never put unmasked secrets or production credentials in CI workflow files (use GitHub Repository Secrets).
- Do not allow PRs to merge with failing CI gates.

---

## 6. Expected Deliverables & Artifacts
- Hardened GitHub Actions CI pipeline in `.github/workflows/ci.yml`.
- Verified passing CI run status.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] CI pipeline executes automatically on push and pull requests.
- [ ] Linting, TypeScript compilation, and pytest pass cleanly.
- [ ] Failing tests correctly block PR merging.

---

## 8. Error Recovery & Troubleshooting
- If CI fails due to dependency caching corruption, add cache busting keys to workflow actions.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/ci-cd-setup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@ci-cd-setup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `ci-cd-setup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `ci-cd-setup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run ci-cd-setup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt ci-cd-setup`. | `PROMPT FILE` |
| **Windsurf** | Activate `ci-cd-setup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.github/workflows/ci.yml`
- `Deploy-To-GitHub.ps1`
