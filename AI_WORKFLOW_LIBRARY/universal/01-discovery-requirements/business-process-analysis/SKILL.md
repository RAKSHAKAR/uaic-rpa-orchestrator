---
name: business-process-analysis
description: >-
  Map actors, business rules, lifecycle process states, handoffs, exception conditions, and outcomes into structured workflows.
---

# Business Process Analysis

## 1. Purpose & Overview
Formalizes complex domain workflows (such as insurance claims processing, legal court discovery, deduplication cascades, and carrier integrations) into comprehensive state diagrams and transition matrices.

---

## 2. When to Use & When NOT to Use

### When to Use
- Designing or refactoring core business lifecycle engines (e.g. claim ingestion, batch queue processing).
- Aligning frontend UI state displays with backend database state machines.
- Auditing legal or insurance compliance handoffs.

### When NOT to Use
- Low-level infrastructure configuration (Docker, CI/CD, linting).
- Generic utility functions that do not affect business lifecycle states.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Domain specifications, state enumeration files (`app/models/claim.py`), and operational guides (`docs/STAGE_AND_STATUS_DEFINITIONS.md`).

### Prerequisites
- Domain understanding of business entities and their terminal vs. transient states.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Actor & Role Identification
Catalogue all system actors (Human Operator, Admin, Celery Scraper Worker, Guidewire Client, Scheduler).

### Step 2: State Machine Extraction
Extract all valid entity states, transient processing stages, failure statuses, and terminal states from database models and enums.

### Step 3: State Transition Mapping
Document allowed transitions, triggering events, required preconditions, and state mutation functions.

### Step 4: Exception & Retry Modeling
Map exception handling paths: CAPTCHA resolution timeout, portal network retry, dead-letter queue routing, and manual review escalation.

### Step 5: Visual Workflow & State Diagram Generation
Generate Mermaid state diagrams (`stateDiagram-v2`) visualizing the end-to-end lifecycle and decision branches.


---

## 5. Safety Considerations & Guardrails
- Never define invalid or orphaned states where entities can become permanently stuck without recovery.
- Preserve strict state transition invariants (e.g. claims cannot jump from `NEW` directly to `PUSHED` without matching).

---

## 6. Expected Deliverables & Artifacts
- Business Process & State Machine Specification.
- Mermaid State Diagram illustrating all valid transitions and exception paths.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Every state in `RecordStatusEnum`, `BotStatusEnum`, and `StageEnum` is mapped with incoming/outgoing transitions.
- [ ] Retry limits, backoff periods, and human escalation triggers are explicitly documented.
- [ ] Terminal states (Complete, Push Succeeded, Fatal Error) are verified as immutable without operator intervention.

---

## 8. Error Recovery & Troubleshooting
- If state transition inconsistencies are detected in code, trace transitions in Celery task runners (`app/tasks/queue_runner.py`).
- Cross-reference `docs/STAGE_AND_STATUS_DEFINITIONS.md` as the authoritative single source of state truth.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/business-process-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@business-process-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `business-process-analysis` workflow. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `business-process-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run business-process-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt business-process-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `business-process-analysis` rule in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/STAGE_AND_STATUS_DEFINITIONS.md` - Authoritative Stage & Status Definitions Manual
- `backend/app/models/claim.py` - Core Domain Enums
