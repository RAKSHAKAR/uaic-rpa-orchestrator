---
name: agent-recovery
description: >-
  Resume execution safely from verified checkpoints following crashes, timeouts, context limits, or interruptions.
---

# Agent Recovery

## 1. Purpose & Overview
Provides deterministic checkpointing and gap-analysis protocols allowing an agent to resume long-running tasks seamlessly following tool timeouts, crashes, or session restarts without re-doing completed work.

---

## 2. When to Use & When NOT to Use

### When to Use
- Resuming a session following an interruption, crash, or context compaction.
- Recovering from Celery worker or Playwright browser automation timeouts.

### When NOT to Use
- Starting a fresh project from scratch.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved Implementation Plan in `docs/`, git commit history, and session transcript.

### Prerequisites
- Documented task checklist with checkpoint markers.

---

## 4. Step-by-Step Execution Procedure

### Step 1: State & Checkpoint Introspection
Inspect git status and recent commits (`git log -n 5`). Determine which files were successfully committed or modified before interruption.

### Step 2: Implementation Plan Re-read
Read the approved implementation plan in `docs/`. Check task checklist to identify the last verified checkpoint.

### Step 3: Gap Analysis & Parity Verification
Execute test suites (`pytest`, `tsc`) on current code to confirm which previous tasks remain green and functional.

### Step 4: Resume Point Identification
Identify the exact first incomplete or unverified task on the checklist.

### Step 5: Seamless Continuation
Resume execution from the identified task without repeating verified steps or losing context.

### Step 6: Checklist State Synchronization
Update plan checklist with current status and proceed toward completion.


---

## 5. Safety Considerations & Guardrails
- Never assume partially modified files are complete; re-verify them before continuing.
- Do NOT skip ahead past incomplete tasks to make up time.

---

## 6. Expected Deliverables & Artifacts
- Interruption Gap Analysis & Recovery Log.
- Resumed execution roadmap leading to completion.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Exact last verified checkpoint is proven with git and test evidence.
- [ ] Execution resumes from the correct sequential task without lost work.
- [ ] Final deliverables achieve 100% of approved plan scope.

---

## 8. Error Recovery & Troubleshooting
- If an interrupted step left partially written corrupted files, revert the uncommitted changes and restart that single step.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/agent-recovery` or follow interruption recovery rule. | `CUSTOM SKILL` |
| **Cursor** | Select `@agent-recovery` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code: 'Resume from the last verified checkpoint.' | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `agent-recovery` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run agent-recovery`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt agent-recovery`. | `PROMPT FILE` |
| **Windsurf** | Activate `agent-recovery` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Interruption Recovery)
- `docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`
