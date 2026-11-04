---
name: root-cause-analysis
description: >-
  Identify the underlying systemic cause of defects using the 5-Whys methodology rather than masking symptoms with workarounds.
---

# Root Cause Analysis

## 1. Purpose & Overview
Performs exhaustive root-cause analysis on recurring defects, intermittent race conditions, or architecture breakdowns, establishing permanent structural fixes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Investigating recurring defects that reappear after superficial fixes.
- Conducting post-incident reviews following a production disruption.
- Diagnosing complex multi-worker concurrency bugs.

### When NOT to Use
- Trivial one-off syntax typos.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Incident timeline, error logs, git history, and system telemetry.

### Prerequisites
- Historical log data covering the incident.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Incident Timeline Reconstruction
Reconstruct chronological timeline of events leading up to the failure with exact timestamps.

### Step 2: 5-Whys Iterative Analysis
Apply 5-Whys methodology starting from the observable symptom. Drill down through software layers to the systemic root cause.

### Step 3: Root Cause vs Contributing Factor Segregation
Distinguish primary root causes (e.g. unindexed query causing lock timeout) from secondary contributing factors (e.g. high load).

### Step 4: Permanent Corrective Action Formulation
Design structural architectural or procedural fixes that make future occurrences impossible.

### Step 5: Preventive Test Case Definition
Define automated regression tests specifically engineered to detect the failure condition.

### Step 6: RCA Document Publication
Publish the formal Root Cause Analysis Document in `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never blame individual operators; focus on systemic software guards, validation gates, and architecture.
- Do NOT accept superficial explanations ('network glitch') without investigating why the system did not recover.

---

## 6. Expected Deliverables & Artifacts
- Formal Root Cause Analysis (RCA) Document in `docs/`.
- Preventive Action Plan and automated regression test.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Underlying systemic root cause is proven with concrete evidence.
- [ ] Corrective actions address the core cause, not merely symptoms.
- [ ] Automated test case prevents regression.

---

## 8. Error Recovery & Troubleshooting
- If evidence is insufficient to reach the 5th Why, design telemetry logging to capture data if the issue recurs.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/root-cause-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@root-cause-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `root-cause-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `root-cause-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run root-cause-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt root-cause-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `root-cause-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Do / Must Not Do)
- `docs/` - Historical Implementation Records
