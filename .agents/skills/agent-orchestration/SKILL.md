---
name: agent-orchestration
description: >-
  Coordinate multi-agent workflows, specialist roles, interface contracts, and cross-agent communication channels.
---

# Agent Orchestration

## 1. Purpose & Overview
Coordinates complex, multi-agent software engineering workstreams, establishing clean division of labor between specialized agents (e.g. Research, Architecture, Implementation, QA) while managing communication and shared state.

---

## 2. When to Use & When NOT to Use

### When to Use
- Orchestrating complex, multi-faceted engineering projects across specialized agents.
- Managing independent research or verification streams concurrently.

### When NOT to Use
- Simple single-file edits.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Project objective, decoupled workstream definitions, and subagent tool grants.

### Prerequisites
- Agent framework supporting subagent delegation (`invoke_subagent`, `send_message`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Role & Responsibility Partitioning
Define specialist agent roles: Lead Architect (governance/planning), Scraper Specialist (Playwright/Chrome), API Specialist (FastAPI/DB), Frontend Specialist (Next.js/UI), and QA Specialist (pytest/verification).

### Step 2: Interface Contract Freezing
Establish frozen interface contracts (Pydantic schemas, TypeScript types, database schemas) before launching agents.

### Step 3: Subagent Lifecycle Management
Launch specialist subagents using `invoke_subagent` with explicit task prompts, required deliverables, and appropriate workspace modes (`inherit`, `branch`).

### Step 4: Message Routing & Synchronization
Monitor subagent completion messages. Route intermediate findings between subagents via `send_message`.

### Step 5: Convergence & Integration Pass
Integrate subagent deliverables sequentially, resolve interface discrepancies, and execute full-stack regression tests.

### Step 6: Audit & Teardown
Terminate finished subagents via `manage_subagents` and archive logs.


---

## 5. Safety Considerations & Guardrails
- Never allow two subagents to modify the same file concurrently.
- Ensure the Lead Agent maintains ultimate governance authority and verifies all subagent deliverables.

---

## 6. Expected Deliverables & Artifacts
- Multi-Agent Orchestration Log.
- Integrated, tested software deliverables.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Each subagent operates within strictly defined file and tool boundaries.
- [ ] All subagent deliverables integrate cleanly without merge conflicts.
- [ ] Full regression test suite passes.

---

## 8. Error Recovery & Troubleshooting
- If a subagent fails or times out, inspect subagent task logs, kill the stuck agent, and re-launch with refined prompt.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/agent-orchestration` or slash command `/teamwork`. | `CUSTOM SKILL` |
| **Cursor** | Coordinate via separate Cursor chat windows. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Use Claude Code subagents with clear roles. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `agent-orchestration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run agent-orchestration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt agent-orchestration`. | `PROMPT FILE` |
| **Windsurf** | Activate `agent-orchestration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8
- `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`
