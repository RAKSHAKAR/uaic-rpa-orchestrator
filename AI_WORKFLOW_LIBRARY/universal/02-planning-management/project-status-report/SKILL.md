---
name: project-status-report
description: >-
  Produce concise, high-signal project status reports detailing progress, blockers, active risks, and next steps for stakeholders.
---

# Project Status Report

## 1. Purpose & Overview
Generates executive and engineering status summaries communicating progress against plan, milestone achievements, test pass metrics, and active blockers.

---

## 2. When to Use & When NOT to Use

### When to Use
- Completing a development cycle or milestone.
- Providing daily or weekly stakeholder progress updates.
- Reporting major roadblocks or unexpected discoveries.

### When NOT to Use
- Internal atomic code commit messages.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Current task progress, test results, git log, and blocker notes.

### Prerequisites
- Verified test suite execution data.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Executive Summary Formulation
Summarize high-level progress in 2-3 concise sentences.

### Step 2: Key Achievements Cataloguing
List completed milestones and implemented features with bulleted highlights.

### Step 3: Metric & Test Evidence Summary
Report quantifiable metrics: test pass rates (e.g. 556/556 passing), code coverage, lint status, and build time.

### Step 4: Blockers & Active Risks
Highlight unresolved technical blockers, external API dependencies, or timeline risks with proposed remediations.

### Step 5: Next Steps & Upcoming Milestones
Detail immediate priorities and next actionable deliverables for the upcoming cycle.


---

## 5. Safety Considerations & Guardrails
- Always report test failures and blockers transparently; never conceal technical debt.
- Do not include speculative delivery dates without confidence ranges.

---

## 6. Expected Deliverables & Artifacts
- Project Status Report Document (`docs/YYYY-MM-DD_project_status_report.md`).
- Executive Summary briefing.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Report clearly distinguishes Completed, In Progress, and Blocked work packages.
- [ ] Test pass rates and build status are quantified with concrete numbers.
- [ ] Next steps are explicitly enumerated with owners and target timeframes.

---

## 8. Error Recovery & Troubleshooting
- If metrics cannot be gathered, run `pytest` and `tsc` immediately to establish live status.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/project-status-report`. | `CUSTOM SKILL` |
| **Cursor** | Select `@project-status-report` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `project-status-report`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `project-status-report` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run project-status-report`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt project-status-report`. | `PROMPT FILE` |
| **Windsurf** | Activate `project-status-report` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/WALKTHROUGH.md`
- `AGENTS.md` - Section 8
