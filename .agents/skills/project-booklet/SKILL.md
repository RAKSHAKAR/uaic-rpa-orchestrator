---
name: project-booklet
description: >-
  Create and maintain complete, book-length project reference booklets synthesizing all operational and engineering knowledge.
---

# Project Booklet

## 1. Purpose & Overview
Consolidates all architectural blueprints, API catalogs, operational runbooks, database schemas, and court portal scraping guides into a comprehensive, single-volume reference booklet.

---

## 2. When to Use & When NOT to Use

### When to Use
- Preparing client handover documentation packages.
- Synthesizing major platform revisions into an authoritative book-length manual.

### When NOT to Use
- Minor isolated code fixes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- All subsystem guides in `docs/`, `README.md`, `AGENTS.md`, and test verification records.

### Prerequisites
- Complete platform stability.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Booklet Table of Contents Formulation
Organize chapters: 1. Executive Summary, 2. Platform Architecture, 3. Repository Layout, 4. Business Rules & Deduplication, 5. The 8 Court Portals, 6. API Reference, 7. Database Schemas, 8. Operator Manual, 9. Deployment & DevOps, 10. AI Governance & Skills.

### Step 2: Content Synthesis & Chapter Integration
Synthesize detailed subsystem guides into coherent chapters with consistent voice, formatting, and high-resolution diagrams.

### Step 3: Visual Evidence Embedding
Embed verified screenshots and diagrams illustrating every frontend route and scraper workflow.

### Step 4: Cross-Reference Validation
Verify all internal chapter links, code references, and tables of contents.

### Step 5: Publication & Archival
Publish the Master Project Booklet in `README.md` or dedicated `docs/PROJECT_BOOKLET.md`.


---

## 5. Safety Considerations & Guardrails
- Never omit critical operational safeguards or business rules during synthesis.
- Ensure booklet is completely self-contained.

---

## 6. Expected Deliverables & Artifacts
- Comprehensive, book-length Project Reference Booklet.
- Complete chapter index and verified diagram package.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Booklet covers 100% of platform architecture, operations, and business rules.
- [ ] All chapters are thoroughly detailed without missing sections or placeholder text.
- [ ] Embedded diagrams and tables render cleanly.

---

## 8. Error Recovery & Troubleshooting
- If booklet size causes markdown rendering lag, optimize embedded image formats (use WebP or compressed PNG).

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/project-booklet`. | `CUSTOM SKILL` |
| **Cursor** | Select `@project-booklet` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `project-booklet`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `project-booklet` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run project-booklet`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt project-booklet`. | `PROMPT FILE` |
| **Windsurf** | Activate `project-booklet` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `README.md` - Master Architectural Booklet
- `docs/`
