---
name: uaic-eight-portal-validation
description: >-
  Run portal-specific and cross-portal automated test harnesses exercising all 8 Florida and Texas scrapers.
---

# Uaic Eight Portal Validation

## 1. Purpose & Overview
Executes automated portal validation suites across Broward, Hillsborough, Miami, Dallas, Travis, Harris JP, Harris District, and Harris County Clerk, proving navigation, search, and extraction fidelity.

---

## 2. When to Use & When NOT to Use

### When to Use
- Testing court scraper modifications or portal DOM fixes.
- Pre-release qualification of court automation fleet.

### When NOT to Use
- Frontend UI testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Portal scrapers in `backend/app/automation/` and portal test suites in `backend/tests/`.

### Prerequisites
- Network connectivity to court portals or mock portal server.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Florida Suite Execution
Run tests for Florida portals: `pytest tests/test_broward_portal.py tests/test_hillsborough_portal.py tests/test_miami_portal.py -q`.

### Step 2: Texas Suite Execution
Run tests for Texas portals: `pytest tests/test_dallas_portal.py tests/test_travis_portal.py tests/test_harris_jp_portal.py tests/test_harris_district_portal.py tests/test_harris_clerk_portal.py -q`.

### Step 3: Schema Compliance Audit
Assert that all 8 portal test runs emit cases matching their exact required field schema.

### Step 4: Cross-State Routing Verification
Test cross-state claim (FL policy, TX loss) and confirm all 8 scrapers are scheduled.

### Step 5: Validation Report Synthesis
Compile results into an 8-Portal Automation Health Matrix.


---

## 5. Safety Considerations & Guardrails
- Do NOT run high-frequency automated loops against live court portals (respect court servers).
- Use mocked HTML fixtures for high-volume automated CI runs.

---

## 6. Expected Deliverables & Artifacts
- 8-Portal Validation Test Report in `docs/`.
- Automated test execution logs confirming 100% pass rate.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All 8 portal scrapers pass their unit and workflow test suites.
- [ ] Harris JP and Harris Clerk emit strictly 4 fields (no CaseType).
- [ ] Remaining 6 portals emit exactly 5 fields.

---

## 8. Error Recovery & Troubleshooting
- If any single portal fails, isolate the test and inspect portal-specific locators.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-eight-portal-validation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-eight-portal-validation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-eight-portal-validation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-eight-portal-validation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-eight-portal-validation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-eight-portal-validation`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-eight-portal-validation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/COURT_PORTALS_GUIDE.md`
- `backend/tests/test_broward_portal.py`
