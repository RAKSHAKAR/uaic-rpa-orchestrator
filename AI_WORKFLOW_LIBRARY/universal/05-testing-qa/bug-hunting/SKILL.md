---
name: bug-hunting
description: >-
  Proactively explore edge cases, invalid inputs, network disconnects, race conditions, and unhandled exceptions.
---

# Bug Hunting

## 1. Purpose & Overview
Conducts exploratory, adversarial testing to discover hidden defects, race conditions, and edge-case crashes before they impact production operators.

---

## 2. When to Use & When NOT to Use

### When to Use
- Following completion of a major feature implementation.
- Testing scrapers against erratic court portal DOM variations.
- Testing batch queue processing under unexpected network disconnects.

### When NOT to Use
- Routine regression test execution.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target application modules, edge-case test data, and fault injection capabilities.

### Prerequisites
- Fully functioning local environment.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Edge-Case Data Generation
Generate unusual test inputs: empty strings, extreme Unicode strings (emojis, accents), massive strings (10,000 chars), negative numbers, and leap year dates.

### Step 2: Fault & Latency Injection
Simulate network timeouts, slow portal responses, and intermittent Redis disconnects during active scraping.

### Step 3: Race Condition Probing
Trigger concurrent duplicate clicks on UI buttons (e.g. clicking 'Start' twice rapidly). Verify idempotency.

### Step 4: State Desynchronization Probing
Interrupt Celery worker tasks mid-execution (kill process). Verify auto-recovery reconciles orphan claims upon restart.

### Step 5: Defect Logging & Reproduction
For every discovered bug, capture stack trace, steps to reproduce, and author an automated reproduction test in `tests/`.


---

## 5. Safety Considerations & Guardrails
- Isolate bug-hunting activities to dedicated test databases.
- Do not exhaust host operating system resources.

---

## 6. Expected Deliverables & Artifacts
- Exploratory Bug-Hunting Findings Log.
- Automated Reproduction Test Cases for discovered defects.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Edge cases and fault injection scenarios are explored systematically.
- [ ] All discovered defects are documented with reliable reproduction scripts.
- [ ] Critical state-corruption or unhandled crash bugs are logged for immediate remediation.

---

## 8. Error Recovery & Troubleshooting
- If a defect leaves the database in a corrupted state, run `scripts/clean_all_data.py` to restore clean state.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/bug-hunting`. | `CUSTOM SKILL` |
| **Cursor** | Select `@bug-hunting` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `bug-hunting`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `bug-hunting` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run bug-hunting`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt bug-hunting`. | `PROMPT FILE` |
| **Windsurf** | Activate `bug-hunting` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/test_worker_restart_auto_recovery.py`
- `scripts/clean_all_data.py`
