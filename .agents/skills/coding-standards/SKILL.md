---
name: coding-standards
description: >-
  Enforce repository-specific formatting, naming, linting, and quality conventions across all source code.
---

# Coding Standards

## 1. Purpose & Overview
Maintains strict code hygiene and stylistic consistency across Python, TypeScript, and PowerShell files, enforcing automated linting and formatting gates.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-commit quality verification on any modified or newly created files.
- Resolving linting failures or formatting discrepancies.

### When NOT to Use
- Running destructive formatting across unchanged legacy files.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Modified source files, `ruff.toml`, `cspell.json`, and TypeScript configuration.

### Prerequisites
- Configured linters in local virtual environment.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Python Linting & Formatting Check
Run `ruff check app tests` in `backend/`. Verify zero syntax or style errors.

### Step 2: TypeScript Type Check
Run `npx tsc --noEmit` in `frontend/`. Verify zero type errors.

### Step 3: PowerShell Syntax Check
Run `powershell -File scripts/check_ps1_syntax.ps1`. Verify zero syntax errors.

### Step 4: Spelling & Dictionary Check
Verify new symbols and variables against `cspell.json` dictionary.

### Step 5: Automated Fix Application
Apply safe automated formatting fixes (`ruff check --fix`) where appropriate.

### Step 6: Final Clean Baseline Verification
Confirm all linters report 0 errors.


---

## 5. Safety Considerations & Guardrails
- Never bypass or disable linter rules merely to silence warnings.
- Avoid massive whitespace reformatting on untouched legacy files.

---

## 6. Expected Deliverables & Artifacts
- 100% compliant source code matching repository standards.
- Zero linter and type-checker error baseline.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Python `ruff check` passes with 0 errors.
- [ ] Frontend `tsc --noEmit` passes with 0 errors.
- [ ] PowerShell syntax check passes with 0 errors.

---

## 8. Error Recovery & Troubleshooting
- If a linter rule conflicts with project conventions, adjust `ruff.toml` with documented justification.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/coding-standards`. | `CUSTOM SKILL` |
| **Cursor** | Select `@coding-standards` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `coding-standards`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `coding-standards` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run coding-standards`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt coding-standards`. | `PROMPT FILE` |
| **Windsurf** | Activate `coding-standards` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 7 (Test Commands)
- `ruff.toml`
