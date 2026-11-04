---
name: documentation-sync
description: >-
  Audit and synchronize documentation across README.md, docs/, and AGENTS.md automatically following code modifications.
---

# Documentation Sync

## 1. Purpose & Overview
Guarantees that project documentation never desynchronizes from codebase reality, updating API catalogs, schemas, endpoints, and test commands whenever code changes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Following ANY implementation task that touches APIs, routes, models, or configuration.
- Pre-release documentation synchronization passes.

### When NOT to Use
- Pure documentation edits.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- List of modified code files, new endpoints, and existing documentation.

### Prerequisites
- Passing test suite baseline.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Code Diff Review
Inspect all modified files in git working tree. Identify new routes, modified models, new settings, or changed scripts.

### Step 2: README.md Synchronization
Update `README.md` tables, directory tree, and test metrics to reflect changes.

### Step 3: AGENTS.md Synchronization
Update `AGENTS.md` API endpoints summary (Section 5) and frontend routes (Section 6).

### Step 4: Subsystem Guide Updates
Update corresponding guides in `docs/` (e.g. `COURT_PORTALS_GUIDE.md` for scraper changes).

### Step 5: Verification Pass
Verify all updated markdown files render cleanly without broken links or formatting defects.


---

## 5. Safety Considerations & Guardrails
- Never delete existing documentation sections during a sync pass.
- Ensure all documented commands and file paths are verified against reality.

---

## 6. Expected Deliverables & Artifacts
- Fully synchronized `README.md`, `AGENTS.md`, and subsystem guides in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of newly added endpoints, routes, and scripts are documented.
- [ ] Test pass rates and suite counts reflect current reality.
- [ ] Zero documentation drift exists between code and docs.

---

## 8. Error Recovery & Troubleshooting
- If git diff shows accidental documentation deletions, restore deleted blocks from git history.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/documentation-sync`. | `CUSTOM SKILL` |
| **Cursor** | Select `@documentation-sync` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `documentation-sync`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `documentation-sync` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run documentation-sync`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt documentation-sync`. | `PROMPT FILE` |
| **Windsurf** | Activate `documentation-sync` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `README.md`
- `AGENTS.md`
