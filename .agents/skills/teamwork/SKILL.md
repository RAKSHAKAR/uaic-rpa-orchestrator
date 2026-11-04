---
name: teamwork
description: >-
  Coordinate multi-agent and parallel workstreams with clear ownership boundaries, interface contracts, and serialized file modifications.
---

# Teamwork

## 1. Purpose & Overview
Orchestrates concurrent agent execution (e.g. Frontend Agent, Backend Agent, Testing Agent) while preventing file overwrite collisions, race conditions, and merge conflicts.

---

## 2. When to Use & When NOT to Use

### When to Use
- Dividing large multi-service tasks across independent AI subagents.
- Running parallel research, linting, or testing alongside active implementation.
- Responding to `/teamwork` slash command.

### When NOT to Use
- Single-agent sequential tasks or tasks editing the same shared files.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved project scope partitioned into independent, decoupled domains.

### Prerequisites
- Tool support for subagent invocation (`invoke_subagent`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Domain Boundary Partitioning
Partition work into strictly disjoint domains (e.g. Agent A: `backend/app/api/`, Agent B: `frontend/src/app/`, Agent C: `tests/`).

### Step 2: Interface Contract Freezing
Freeze TypeScript types, REST endpoint paths, and database schemas before launching parallel subagents.

### Step 3: Subagent Launch & Role Assignment
Launch subagents with dedicated prompts, specific role titles ('Backend Architect', 'Frontend Developer'), and isolated workspace modes.

### Step 4: Inter-Agent Communication & Synchronization
Monitor subagent completion messages. Coordinate integration handoffs sequentially.

### Step 5: Integration Validation & Synthesis
Execute full-stack integration tests (`pytest`, `tsc`) to verify combined output.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never allow two parallel agents to modify the same file concurrently.
- Do NOT run parallel agents without frozen interface contracts.

---

## 6. Expected Deliverables & Artifacts
- Multi-Agent Coordination Plan.
- Consolidated Integration Test Report.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All subagents operate on strictly non-overlapping file sets.
- [ ] Interface contracts are respected across all subagent deliverables.
- [ ] Combined code passes all integration test suites without regressions.

---

## 8. Error Recovery & Troubleshooting
- If subagents generate conflicting code, serialize modifications and resolve interface discrepancies immediately.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke native slash command `/teamwork` or use `invoke_subagent`. | `CUSTOM SKILL` |
| **Cursor** | Coordinate via separate Cursor chat sessions. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Use Claude Code subagents with explicit file boundaries. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `teamwork` in Codex multi-agent context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run teamwork`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt teamwork`. | `PROMPT FILE` |
| **Windsurf** | Activate `teamwork` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Do / Must Not Do)
