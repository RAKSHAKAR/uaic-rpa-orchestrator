---
name: subagent-delegation
description: >-
  Delegate bounded, well-specified tasks to independent subagents with explicit inputs, tools, and acceptance criteria.
---

# Subagent Delegation

## 1. Purpose & Overview
Enables primary coding agents to delegate isolated, time-consuming tasks (e.g. codebase research, log auditing, documentation drafting) to subagents, preserving primary context window and focus.

---

## 2. When to Use & When NOT to Use

### When to Use
- Performing broad codebase searches or documentation surveys that would clutter primary context.
- Executing isolated test passes or independent script generation.

### When NOT to Use
- Architectural decision-making or critical governance approvals.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Task description, explicit inputs, allowed tool scope, and expected deliverables.

### Prerequisites
- `invoke_subagent` tool availability.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Task Boundary Definition
Scope delegated task to a single, well-defined objective with unambiguous inputs and outputs.

### Step 2: Tool & Workspace Mode Selection
Select subagent type (`research` for read-only codebase search, `self` for full tools). Choose workspace mode (`inherit` or `branch`).

### Step 3: Structured Prompt Formulation
Draft actionable subagent prompt detailing: Role, Background Context, Specific Steps, Prohibited Actions, and Deliverable Format.

### Step 4: Subagent Launch
Invoke subagent via `invoke_subagent`. Capture returned `conversationId`.

### Step 5: Reactive Wakeup & Result Ingestion
Allow background execution. Upon subagent message arrival, ingest findings into primary task context.

### Step 6: Deliverable Verification
Verify subagent output against acceptance criteria before incorporating into primary plan.


---

## 5. Safety Considerations & Guardrails
- Never delegate tasks that require unconfirmed destructive operations.
- Do NOT poll subagent status in a tight loop; rely on reactive wakeup.

---

## 6. Expected Deliverables & Artifacts
- Subagent execution result and verified deliverable.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Subagent prompt is specific, actionable, and bounded.
- [ ] Subagent returns all requested deliverables without errors.
- [ ] Primary context remains clean and uncluttered.

---

## 8. Error Recovery & Troubleshooting
- If subagent produces incomplete output, send clarifying message via `send_message`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via `invoke_subagent` or `/subagent-delegation`. | `CUSTOM SKILL` |
| **Cursor** | Delegate via secondary Cursor composer. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Use Claude Code `/subagent` if supported. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `subagent-delegation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run subagent-delegation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt subagent-delegation`. | `PROMPT FILE` |
| **Windsurf** | Activate `subagent-delegation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- Antigravity Subagent System Documentation
- `AGENTS.md` - Section 8
