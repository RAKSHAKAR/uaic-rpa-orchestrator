---
name: code-documentation
description: >-
  Document non-obvious algorithms, scraper heuristics, fuzzy cascade logic, and API interface contracts.
---

# Code Documentation

## 1. Purpose & Overview
Authors clear, concise, and accurate docstrings, module documentation, and inline comments explaining the *why* behind complex business logic and architectural choices.

---

## 2. When to Use & When NOT to Use

### When to Use
- Writing complex business logic (e.g. RapidFuzz cascade, DOL date conversion).
- Implementing complex Playwright DOM interaction workarounds.
- Authoring public service interfaces and utility libraries.

### When NOT to Use
- Writing redundant comments that merely restate self-explanatory code (e.g., `i += 1  # increment i`).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Source code files needing documentation.
- Business rule context from `AGENTS.md`.

### Prerequisites
- Complete understanding of the underlying business constraints.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Module & Function Docstrings
Add Google-style docstrings to Python functions/classes detailing Args, Returns, Raises, and business rationale.

### Step 2: Complex Heuristic Documentation
Document non-obvious heuristics (e.g. why Date of Loss uses 1899-12-30 base, why 9-digit ClaimNumber gets '0' prefix).

### Step 3: TypeScript Interface Comments
Add JSDoc comments to TypeScript interfaces and API client methods in `frontend/src/`.

### Step 4: Preserve Documentation Integrity
Preserve all pre-existing comments and docstrings unrelated to current edits.

### Step 5: Linter Verification
Run `ruff check` to ensure docstrings adhere to formatting standards.


---

## 5. Safety Considerations & Guardrails
- Never write misleading, stale, or contradictory documentation.
- Preserve existing comments and license headers.

---

## 6. Expected Deliverables & Artifacts
- Fully documented source code with standardized docstrings and JSDoc blocks.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All public classes and functions have meaningful docstrings.
- [ ] Complex business invariants are thoroughly explained with references to `AGENTS.md`.
- [ ] Zero docstring formatting errors reported by linter.

---

## 8. Error Recovery & Troubleshooting
- If docstrings desynchronize from code during refactoring, update docstrings immediately as part of the change.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/code-documentation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@code-documentation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `code-documentation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `code-documentation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run code-documentation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt code-documentation`. | `PROMPT FILE` |
| **Windsurf** | Activate `code-documentation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Critical Business Rules)
- `backend/app/services/fuzzy_engine.py`
