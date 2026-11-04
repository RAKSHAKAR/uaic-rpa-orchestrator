---
name: readme-generation
description: >-
  Maintain and enhance the authoritative single-source README.md master booklet without losing existing operational details.
---

# Readme Generation

## 1. Purpose & Overview
Governs the maintenance and continuous synchronization of `README.md`, ensuring it serves as an exhaustive, single-source booklet covering architecture, directory layout, business rules, API endpoints, setup, and testing.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding new API endpoints, scripts, environment variables, or frontend routes.
- Updating repository directory layout or test command documentation.

### When NOT to Use
- Replacing a comprehensive README with a simplified summary (STRICTLY PROHIBITED).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Current `README.md` (136+ KB), recent code changes, and new features.

### Prerequisites
- Thorough review of existing `README.md` structure to preserve all sections.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Existing Content Audit
Read existing `README.md` fully. Identify all existing sections: Identity, Architecture, Directory Tree, Business Rules, API Table, UI Routes, Test Suite, Power Automate Parity.

### Step 2: Change Integration
Insert new information into the exact matching section without deleting or condensing surrounding details.

### Step 3: Directory Tree Synchronization
Update ASCII directory tree representation to reflect newly added directories or files.

### Step 4: API & Route Table Updates
Add new API endpoints and Next.js frontend routes to their respective tables.

### Step 5: Test Command & Pass Rate Update
Update test suite statistics (e.g. 556 passing tests across 67 suites).

### Step 6: Formatting & Link Verification
Verify all markdown tables, code blocks, and internal anchor links render cleanly.


---

## 5. Safety Considerations & Guardrails
- CRITICAL NON-NEGOTIABLE: NEVER replace a comprehensive `README.md` with a simplified or abbreviated version.
- Preserve all existing historical context, Power Automate V4 behavioral mappings, and business rules.

---

## 6. Expected Deliverables & Artifacts
- Synchronized, comprehensive `README.md` master booklet.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `README.md` remains an exhaustive, book-length reference document.
- [ ] All new endpoints, routes, scripts, and skills are accurately documented.
- [ ] Zero pre-existing sections or operational guides are lost.

---

## 8. Error Recovery & Troubleshooting
- If `README.md` is accidentally truncated, immediately restore from git and re-apply changes incrementally.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/readme-generation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@readme-generation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `readme-generation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `readme-generation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run readme-generation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt readme-generation`. | `PROMPT FILE` |
| **Windsurf** | Activate `readme-generation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `README.md` - Master Architectural Booklet
- `AGENTS.md` - Section 8 (MUST DO: Maintain README.md)
