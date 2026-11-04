---
name: execution-tracking
description: >-
  Track ongoing implementation tasks against the approved plan and update progress with verifiable automated evidence.
---

# Execution Tracking

## 1. Purpose & Overview
Provides continuous visibility into implementation progress, ensuring every completed task is backed by actual test evidence and preventing drift from the approved plan.

---

## 2. When to Use & When NOT to Use

### When to Use
- During active execution of multi-step implementation plans.
- Following completion of individual work packages or checkpoints.

### When NOT to Use
- Initial planning phase before work has commenced.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved Implementation Plan and task checklist.
- Automated test run outputs and verification artifacts.

### Prerequisites
- Active execution of approved implementation plan.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Task Progress Inspection
Check current state against the task checklist. Verify which tasks are Pending, In Progress, or Complete.

### Step 2: Evidence Verification Audit
For completed tasks, inspect test outputs (`pytest` logs, `tsc` exits, browser recordings) to confirm genuine completion.

### Step 3: Checklist State Mutation
Update task checkboxes (`[x]`) and timestamp verified milestones.

### Step 4: Deviation & Blocker Detection
Identify any unexpected scope additions, test failures, or performance regressions.

### Step 5: Progress Snapshot Generation
Publish a concise Execution Tracking Snapshot detailing completed tasks, active task, and next steps.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never mark a task as completed without verified automated evidence.
- Do NOT silently bypass failing tests; log them as blockers.

---

## 6. Expected Deliverables & Artifacts
- Updated Task Progress Checklist.
- Execution Progress Summary with test verification logs.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Every completed task is accompanied by verifiable terminal or test evidence.
- [ ] Discrepancies between plan and actual implementation are documented.
- [ ] Remaining tasks and blockers are clearly identified.

---

## 8. Error Recovery & Troubleshooting
- If an execution blocker halts progress, invoke `diagnose-issue` and document the roadblock.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/execution-tracking`. | `CUSTOM SKILL` |
| **Cursor** | Select `@execution-tracking` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `execution-tracking`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `execution-tracking` in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run execution-tracking`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt execution-tracking`. | `PROMPT FILE` |
| **Windsurf** | Activate `execution-tracking` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`
