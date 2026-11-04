---
name: technical-documentation
description: >-
  Author comprehensive subsystem guides, architectural deep-dives, and technical specifications in docs/.
---

# Technical Documentation

## 1. Purpose & Overview
Creates clear, rigorous technical reference manuals detailing subsystem architectures, operational runbooks, and protocol specifications.

---

## 2. When to Use & When NOT to Use

### When to Use
- Documenting a major subsystem (e.g. Proxy Network, Task Queue, Storage & Exports).
- Authoring technical specifications for newly implemented features.

### When NOT to Use
- Writing quick inline code comments.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Subsystem implementation details, architecture diagrams, and operational procedures.

### Prerequisites
- Complete code-level understanding of the target subsystem.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Structure & Scope Definition
Define document scope in `docs/<SUBSYSTEM>_GUIDE.md`. Establish sections: Overview, Architecture, Data Contracts, Configuration, Error Recovery, and Verification.

### Step 2: Diagram Generation
Create Mermaid diagrams visualizing data flow, state transitions, or component interactions.

### Step 3: Code Snippet & Contract Embedding
Embed concrete, copy-pasteable code examples, API requests, and configuration JSON schemas.

### Step 4: Operational Runbook Procedures
Detail step-by-step procedures for operators: troubleshooting, clearing queues, rotating proxies, or repairing stuck claims.

### Step 5: Review & Linkage
Cross-reference new guide in `README.md` and `AGENTS.md`.


---

## 5. Safety Considerations & Guardrails
- Save all long-form technical guides in `docs/` (never loose in the root directory).
- Mask all credentials, passwords, and API keys in documentation examples.

---

## 6. Expected Deliverables & Artifacts
- Authoritative Subsystem Guide in `docs/`.
- Mermaid architectural diagrams and operational runbooks.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Guide provides complete, standalone reference for the subsystem.
- [ ] All commands and code snippets are accurate and tested.
- [ ] Document is linked from `README.md` table of contents.

---

## 8. Error Recovery & Troubleshooting
- If technical details diverge from implementation, review code AST and update documentation to match reality.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/technical-documentation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@technical-documentation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `technical-documentation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `technical-documentation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run technical-documentation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt technical-documentation`. | `PROMPT FILE` |
| **Windsurf** | Activate `technical-documentation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`
- `docs/COURT_PORTALS_GUIDE.md`
