---
name: learn
description: >-
  Convert confirmed user corrections, preferences, and architectural rules into permanent project governance guidelines.
---

# Learn

## 1. Purpose & Overview
Persists confirmed user corrections, architectural mandates, and preference decisions into permanent project rules (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`), preventing repeated mistakes across sessions.

---

## 2. When to Use & When NOT to Use

### When to Use
- User explicitly corrects an agent mistake or establishes a new project rule.
- Responding to `/learn` slash command.
- Following successful resolution of a complex architectural decision.

### When NOT to Use
- Transient session-specific instructions.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- User correction text, confirmed rule, and target rule files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`).

### Prerequisites
- Explicit user confirmation of the rule.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Correction & Rule Analysis
Analyze the user correction. Extract the underlying rule and scope of applicability.

### Step 2: Rule Formulation
Draft a concise, unambiguous rule statement with explicit DO and DON'T examples.

### Step 3: Permanent Rule File Update
Add the rule to `AGENTS.md` (Section 8), `GEMINI.md`, `CLAUDE.md`, and `.cursorrules`.

### Step 4: Deduplication & Conflict Check
Ensure the new rule does not contradict existing governance guidelines.

### Step 5: User Confirmation
Confirm to the user that the lesson has been codified into permanent project memory.


---

## 5. Safety Considerations & Guardrails
- Never encode rules that violate core safety invariants (data loss prevention, security).
- Keep global rule files concise; place lengthy procedures into dedicated skills.

---

## 6. Expected Deliverables & Artifacts
- Updated rule files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.cursorrules`).
- Confirmation summary to the user.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Confirmed rule is persisted across all primary AI rule files.
- [ ] Rule phrasing is unambiguous, testable, and actionable.
- [ ] No conflicting rules exist in project memory.

---

## 8. Error Recovery & Troubleshooting
- If user refines or withdraws a rule later, update rule files immediately to reflect the revised directive.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke native slash command `/learn` or ask agent to learn this rule. | `CUSTOM SKILL` |
| **Cursor** | Select `@learn` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code: 'Update CLAUDE.md with this confirmed lesson.' | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `learn` workflow in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run learn`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt learn`. | `PROMPT FILE` |
| **Windsurf** | Activate `learn` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Do / Must Not Do)
- `CLAUDE.md`
- `GEMINI.md`
