---
name: grill-me
description: >-
  Conduct a structured, interactive interview with the user to resolve critical ambiguities and design trade-offs before making irreversible assumptions.
---

# Grill Me

## 1. Purpose & Overview
Engages the user in targeted, high-signal inquiry to clarify material uncertainties, architectural trade-offs, security boundaries, and edge-case handling before authoring an implementation plan.

---

## 2. When to Use & When NOT to Use

### When to Use
- User request contains underspecified requirements with multiple viable architectures.
- Encountering conflicting business rules between different specifications.
- Consequential design decisions involving database migrations, external integrations, or breaking API changes.

### When NOT to Use
- Trivial questions with self-evident answers already documented in `AGENTS.md` or `README.md`.
- During automated test execution or non-interactive background tasks.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- List of specific, well-articulated ambiguities or design options.
- Context on trade-offs (pros, cons, risks, effort) for each option.

### Prerequisites
- Thorough review of existing documentation to ensure the answer is not already documented.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Ambiguity Clustering
Group open questions into logical themes: Architecture, Data Model, User Experience, External Integrations, and Security/Safety.

### Step 2: Option Formulation with Recommendations
For each question, formulate clear options, highlight the recommended approach prefixed with '(Recommended)', and explain trade-offs.

### Step 3: Interactive Interview Presentation
Present questions concisely using the `ask_question` tool or structured interactive prompts. Avoid overwhelming the user with more than 3-4 questions at once.

### Step 4: User Decision Ingestion & Confirmation
Record user choices, confirm consensus, and extract explicit constraints.

### Step 5: Decision Archival
Archive finalized decisions into the session context and cross-reference them in the upcoming Implementation Plan.


---

## 5. Safety Considerations & Guardrails
- Do NOT ask open-ended or trivial questions that can be answered by reading the codebase.
- Do NOT proceed with speculative assumptions if the user has not confirmed critical architectural directions.

---

## 6. Expected Deliverables & Artifacts
- Interview Findings & Decision Log summarizing confirmed requirements.
- Updated assumptions list ready for inclusion in the Implementation Plan.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All material ambiguities identified during discovery are resolved by explicit user decisions.
- [ ] Every question presented included an explicit recommendation and trade-off summary.
- [ ] Confirmed decisions are recorded in project documentation or session artifacts.

---

## 8. Error Recovery & Troubleshooting
- If the user is unsure of a technical decision, provide a sensible default based on existing project conventions (`AGENTS.md`).
- If user choices contradict existing safety rules, explain the constraint and seek consensus.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke native slash command `/grill-me` or ask the agent to interview you on requirements. | `CUSTOM SKILL` |
| **Cursor** | Select `@grill-me` rule in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code: 'Interview me using the grill-me protocol before designing.' | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `grill-me` workflow in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run grill-me`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt grill-me`. | `PROMPT FILE` |
| **Windsurf** | Activate `grill-me` workflow in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Do / Must Not Do)
- `docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`
