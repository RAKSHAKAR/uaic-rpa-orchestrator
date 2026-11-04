---
name: parallel-execution
description: >-
  Run independent verification, linting, or research tasks concurrently while strictly serializing shared file modifications.
---

# Parallel Execution

## 1. Purpose & Overview
Maximizes engineering throughput by executing non-conflicting background tasks (e.g. running pytest while compiling frontend TypeScript) in parallel while preventing file write collisions.

---

## 2. When to Use & When NOT to Use

### When to Use
- Running multiple independent test suites or linters simultaneously.
- Conducting multi-source codebase research across decoupled modules.

### When NOT to Use
- Modifying the same files or shared database records concurrently.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- List of independent, non-conflicting tasks.

### Prerequisites
- Background task execution capabilities (`run_command` with async support).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Independence & Conflict Analysis
Verify tasks have zero shared mutable state, touch disjoint file sets, and do not compete for the same network ports.

### Step 2: Concurrent Task Launch
Launch independent tasks concurrently (e.g. Task A: `pytest`, Task B: `tsc --noEmit`).

### Step 3: Background Task Monitoring
Allow tasks to run in background. Rely on reactive completion notifications.

### Step 4: Serialized File Write Handoff
If tasks generate file updates, serialize file writes sequentially: apply Task A changes, verify, then apply Task B changes.

### Step 5: Consolidated Result Synthesis
Combine outputs and report unified completion status.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never run concurrent tasks that modify the same source file.
- Do NOT run concurrent scraper tests against the same court portal to avoid IP blocking.

---

## 6. Expected Deliverables & Artifacts
- Consolidated results from parallel task executions.
- Reduced total execution duration.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All parallel tasks execute without port collisions or file locks.
- [ ] Combined results are synthesized accurately.
- [ ] Total execution time is significantly lower than sequential execution.

---

## 8. Error Recovery & Troubleshooting
- If parallel tasks collide on database access, serialize their execution immediately.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/parallel-execution`. | `CUSTOM SKILL` |
| **Cursor** | Run concurrent terminal processes in Cursor. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Execute background tasks in Claude Code. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `parallel-execution` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run parallel-execution`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt parallel-execution`. | `PROMPT FILE` |
| **Windsurf** | Activate `parallel-execution` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Do / Must Not Do)
