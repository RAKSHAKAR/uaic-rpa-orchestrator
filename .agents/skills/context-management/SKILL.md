---
name: context-management
description: >-
  Preserve critical architectural decisions, business rules, and constraints across long-running tasks while pruning transient dumps.
---

# Context Management

## 1. Purpose & Overview
Curates conversational and token context during long-running tasks, pruning transient verbose terminal outputs while ensuring critical architectural decisions, invariants, and file paths are permanently retained.

---

## 2. When to Use & When NOT to Use

### When to Use
- During long multi-turn sessions where context window limits approach.
- Responding to `/compact` slash command.
- Archiving large research dumps into permanent documentation in `docs/`.

### When NOT to Use
- Short 1-2 turn conversations.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Current conversational state, active task checklist, and project rule files.

### Prerequisites
- Knowledge of progressive disclosure and artifact storage.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Transient Dump Identification
Identify bulky transient content (raw compiler outputs, large terminal dumps, multi-page logs) in context.

### Step 2: Critical Invariant Extraction
Extract and preserve essential invariants: Implementation ID, active approved plan path, verified test counts, and pending task list.

### Step 3: External File Archival
Offload bulky logs, research findings, or diagnostic dumps into persistent files in `docs/` or `scripts/`.

### Step 4: Context Summarization & Compaction
Synthesize conversation context into a high-signal state brief retaining key decisions, assumptions, and next steps.

### Step 5: Prompt Continuity Check
Confirm that following compaction, the agent can continue executing the active plan without loss of direction.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never discard approved implementation plan details, non-negotiable rules, or user constraints during compaction.
- Ensure file paths to all relevant documents are preserved.

---

## 6. Expected Deliverables & Artifacts
- Compacted context brief.
- Persistent documentation files in `docs/` capturing offloaded data.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Token footprint is significantly reduced.
- [ ] All critical decisions, constraints, and pending tasks are preserved.
- [ ] Agent continues execution with full continuity.

---

## 8. Error Recovery & Troubleshooting
- If context compaction loses a critical detail, re-read the approved implementation plan from `docs/`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke native slash command `/compact` or `/context-management`. | `CUSTOM SKILL` |
| **Cursor** | Summarize context in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Use Claude Code `/compact`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `context-management` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run context-management`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt context-management`. | `PROMPT FILE` |
| **Windsurf** | Activate `context-management` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8
- `docs/`
