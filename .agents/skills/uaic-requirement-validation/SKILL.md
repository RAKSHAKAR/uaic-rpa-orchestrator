---
name: uaic-requirement-validation
description: >-
  Trace UAIC implementation features against approved business requirements and Power Automate V4 behavioral flows.
---

# Uaic Requirement Validation

## 1. Purpose & Overview
Validates that the modern Python/Next.js orchestrator achieves 100% functional and behavioral parity with the client's legacy Power Automate Desktop V4 robotic process automation bots.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-release qualification of court scrapers or deduplication logic.
- Verifying state routing, DOL dates, or Guidewire payload structures.

### When NOT to Use
- Non-UAIC requirements.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Power Automate V4 Robin flows (`v4_subflows/`), `AGENTS.md` Section 3, and implementation test suites.

### Prerequisites
- Access to annotated V4 subflow documentation (`docs/v4_all_8_subflows_annotated.txt`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: State Routing Parity Audit
Verify policy_state == loss_location_state rules: FL runs 3 portals (Broward, Hillsborough, Miami); TX runs 5 portals (Harris Clerk, Dallas, Harris JP, Harris District, Travis); cross-state runs all 8.

### Step 2: Party Matrix Parity Audit
Verify unique name generation matrix: All same (1/1), Insured=Driver Claimant!= (1/3), Insured=Claimant Driver!= (2/1), Driver=Claimant Insured!= (2/1), All different (2/3).

### Step 3: DOL Date Conversion Parity Audit
Verify Excel serial date conversion base 1899-12-30 produces exact MM/dd/yyyy strings without timezone shifts.

### Step 4: Guidewire 9-Digit Rule Audit
Verify 9-digit ClaimNumber receives leading '0' prefix in Guidewire payload.

### Step 5: Portal Output Schema Parity Audit
Verify 5 fields for 6 portals; strictly 4 fields (NO CaseType) for Harris JP and Harris County Clerk.

### Step 6: Parity Matrix Synthesis
Publish the UAIC Requirements & V4 Parity Matrix in `docs/`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never add CaseType to Harris JP or Harris County Clerk scrapers.
- Never introduce timezone offsets into Date of Loss conversion.

---

## 6. Expected Deliverables & Artifacts
- UAIC Requirements Traceability & V4 Parity Report in `docs/`.
- Automated parity test suite pass log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All 5 core business rules verified with 100% compliance.
- [ ] `backend/tests/test_v4_parity.py` passes all assertions.
- [ ] Guidewire payload matches exact client contract.

---

## 8. Error Recovery & Troubleshooting
- If parity discrepancies are found, update code to match Power Automate V4 behavior (V4 is authoritative).

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-requirement-validation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-requirement-validation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-requirement-validation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-requirement-validation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-requirement-validation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-requirement-validation`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-requirement-validation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Critical Business Rules)
- `backend/tests/test_v4_parity.py`
