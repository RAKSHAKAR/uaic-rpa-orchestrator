---
name: e2e-testing
description: >-
  Verify critical end-to-end user journeys using Playwright across frontend UI, backend APIs, and automation bots.
---

# E2E Testing

## 1. Purpose & Overview
Simulates complete end-to-end operator journeys (uploading an Excel claim file, reviewing fuzzy matches, launching attended bots, exporting results) across the full running stack.

---

## 2. When to Use & When NOT to Use

### When to Use
- Validating full-stack release candidates.
- Verifying multi-screen workflows connecting upload, claims detail, monitor, and settings.

### When NOT to Use
- Testing isolated helper functions.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Running full-stack environment (FastAPI on 8000, Next.js on 3000, Redis on 6379).
- Playwright test scripts in `e2e/`.

### Prerequisites
- Local services started via `setup_local.ps1` or Docker.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Environment Readiness Check
Verify `/api/v1/health` and `http://localhost:3000` respond with HTTP 200.

### Step 2: Journey Navigation & Data Entry
Launch Playwright browser. Navigate to `/upload`, upload test Excel file (`ProdRecords8Bots.xlsx`), and submit.

### Step 3: State Transition Monitoring
Verify claims appear on `/` dashboard. Monitor queue status on `/monitor` as Celery processes records.

### Step 4: Exception Review & Fuzzy Verification
Navigate to `/exceptions`, verify fuzzy match candidate card, click Approve, and confirm status transition.

### Step 5: Guidewire Dispatch Verification
Verify claim reaches `PUSHED` status and Guidewire activity log is populated.

### Step 6: Artifact & Evidence Recording
Capture Playwright trace, screenshot, or video recording verifying the journey.


---

## 5. Safety Considerations & Guardrails
- Use dedicated test claims and seed fixtures; do not pollute production data.
- Clean up generated export files and temporary upload artifacts after test completion.

---

## 6. Expected Deliverables & Artifacts
- Playwright E2E test scripts in `e2e/`.
- Video recording (.webp) or screenshot (.png) verification artifact in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Complete user journey succeeds from file upload to Guidewire push without manual intervention.
- [ ] All assertions on UI elements, status badges, and database state pass.
- [ ] Visual evidence is captured and documented.

---

## 8. Error Recovery & Troubleshooting
- If Playwright locators time out, inspect browser DOM snapshots to confirm whether element IDs or classes changed.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/e2e-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@e2e-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `e2e-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `e2e-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run e2e-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt e2e-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `e2e-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `e2e/backend/`
- `docs/WALKTHROUGH.md`
