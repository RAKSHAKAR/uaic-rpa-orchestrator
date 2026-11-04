---
name: fix-integration-issues
description: >-
  Resolve external service failures, Guidewire API contract mismatches, AntiCaptcha timeouts, and portal DOM changes.
---

# Fix Integration Issues

## 1. Purpose & Overview
Diagnoses and fixes integration failures when communicating with external court websites, CAPTCHA solving services, and Guidewire Insurance Cloud APIs.

---

## 2. When to Use & When NOT to Use

### When to Use
- Guidewire rejects case delivery payloads with HTTP 400 or 500.
- AntiCaptcha extension times out or fails to resolve a challenge.
- Court portal alters table markup or input field locators.

### When NOT to Use
- Internal unit test failures.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Failed integration transaction log, error screenshot, external HTTP response, and target portal key.

### Prerequisites
- Access to external client code in `app/services/` and scrapers in `app/automation/`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: External Response & Screenshot Analysis
Inspect external API error payload or scraper error screenshot in `backend/screenshots/`.

### Step 2: Guidewire Contract Verification
If Guidewire fails, verify payload structure matches exact contract: `ClaimNumber` (9-digit gets '0' prefix), `ExposureNumber`, `CaseItems` array.

### Step 3: CAPTCHA & DOM Locator Inspection
If portal fails, inspect live portal DOM. Verify whether element IDs, search tabs, or CAPTCHA types have mutated.

### Step 4: Client / Scraper Locator Patch
Update Playwright CSS selectors or API client serializer to match current external interface.

### Step 5: Isolated Live Test Execution
Run targeted live test script in `scripts/` (e.g. `test_broward.py` or `scripts/test_export_download_verify.py`) to confirm fix.

### Step 6: Regression Verification
Run full pytest suite to ensure portal output schema remains 100% compliant.


---

## 5. Safety Considerations & Guardrails
- Never modify portal output schemas (CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType) when fixing locators.
- Do NOT add CaseType to Harris JP or Harris County Clerk scrapers.

---

## 6. Expected Deliverables & Artifacts
- Patched scraper locator or API client serializer.
- Verification execution log confirming successful live interaction.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] External integration completes successfully without unhandled errors.
- [ ] Extracted records strictly adhere to portal schema.
- [ ] All scraper unit and parity tests pass.

---

## 8. Error Recovery & Troubleshooting
- If an external portal is temporarily down, implement exponential backoff retry rather than permanent failure.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-integration-issues`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-integration-issues` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-integration-issues`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-integration-issues` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-integration-issues`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-integration-issues`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-integration-issues` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Portal Output Schema) & Section 11 (Guidewire Payload Contract)
- `backend/app/services/guidewire_client.py`
