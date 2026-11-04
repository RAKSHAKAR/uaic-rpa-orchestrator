---
name: architecture-decision-record
description: >-
  Record significant architecture decisions, rationale, context, consequences, and evaluated alternatives in immutable ADRs.
---

# Architecture Decision Record

## 1. Purpose & Overview
Maintains an immutable historical record of major technical decisions, preserving architectural context and preventing future regressions or circular debates.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adopting or retiring a core technology, framework, database, or library.
- Choosing an architectural style (e.g. monolithic FastAPI + Celery vs microservices).
- Establishing significant technical conventions (e.g., synchronous Playwright for AntiCaptcha stability).

### When NOT to Use
- Routine implementation choices that follow established conventions.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Context of the decision, evaluated options, trade-offs, and final consensus.

### Prerequisites
- Completed `technical-feasibility` or team consensus.

---

## 4. Step-by-Step Execution Procedure

### Step 1: ADR Numbering & Titling
Assign sequential ID: `ADR-NNN: <Short Decision Title>`. Status: Proposed, Accepted, Deprecated, or Superseded.

### Step 2: Context Statement Formulation
Describe the engineering context, business drivers, constraints, and forces at play.

### Step 3: Decision Statement
State clearly: 'We will ...' with unambiguous commitment to the chosen architecture.

### Step 4: Consequences & Trade-Offs
Detail positive consequences, negative trade-offs, risks, and follow-up maintenance overhead.

### Step 5: Alternatives Considered
Document rejected alternatives with explicit reasons for rejection.

### Step 6: Archival & Linkage
Save to `docs/adr/` or `docs/` and cross-reference in `README.md`.


---

## 5. Safety Considerations & Guardrails
- Never overwrite an existing ADR; create a new ADR that explicitly supersedes the older one.
- Ensure ADRs reflect verified reality, not aspirational theories.

---

## 6. Expected Deliverables & Artifacts
- Formal Architecture Decision Record (`docs/ADR-NNN_<title>.md`).
- Updated ADR Index in project documentation.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] ADR adheres to standard Michael Nygard format (Title, Status, Context, Decision, Consequences, Alternatives).
- [ ] Both positive and negative consequences are objectively documented.
- [ ] Cross-referenced in repository documentation.

---

## 8. Error Recovery & Troubleshooting
- If an approved ADR proves unworkable in practice, author a new superseding ADR documenting lessons learned.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/architecture-decision-record`. | `CUSTOM SKILL` |
| **Cursor** | Select `@architecture-decision-record` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `architecture-decision-record`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `architecture-decision-record` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run architecture-decision-record`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt architecture-decision-record`. | `PROMPT FILE` |
| **Windsurf** | Activate `architecture-decision-record` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 1 (Project Identity) & Section 3 (Critical Business Rules)
- `README.md`
