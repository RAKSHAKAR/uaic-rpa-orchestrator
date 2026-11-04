---
name: final-delivery-audit
description: >-
  Conduct comprehensive pre-handover verification: automated test evidence, documentation sync, limitation logs, and rollback instructions.
---

# Final Delivery Audit

## 1. Purpose & Overview
Governs the final delivery audit of an engineering task or release, ensuring that all acceptance criteria are met, test suites pass with 100% success rate, documentation is synchronized, and known limitations are transparently reported.

---

## 2. When to Use & When NOT to Use

### When to Use
- Concluding any substantial engineering implementation task.
- Preparing the final delivery report for the user.

### When NOT to Use
- Mid-flight execution of intermediate work packages.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved implementation plan, all test outputs (`pytest`, `tsc`, `ps1`), git diff, and updated documentation.

### Prerequisites
- All code changes implemented and tested.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Acceptance Criteria Audit
Compare final codebase against every single requirement in the approved plan. Confirm 100% completion.

### Step 2: Full Test Suite Verification
Run full test suite: `pytest -q`, `tsc --noEmit`, `check_ps1_syntax.ps1`, `ruff check`. Confirm 0 errors.

### Step 3: Documentation Synchronization Audit
Verify `README.md`, `AGENTS.md`, and relevant subsystem guides reflect all newly added components.

### Step 4: Known Limitations & Gaps Cataloguing
Document any deliberate scope boundaries, environment-specific limitations, or future recommendations.

### Step 5: Rollback Instructions Verification
Provide explicit, copy-pasteable rollback instructions in the final report.

### Step 6: Final Delivery Report Generation
Publish comprehensive Final Delivery Report summarizing accomplishments, test evidence, and handover instructions.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never claim completion without actual automated test evidence.
- Always report limitations honestly; never conceal unverified paths.

---

## 6. Expected Deliverables & Artifacts
- Comprehensive Final Delivery Report in conversation output and `docs/`.
- Verified green test suite logs.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All planned deliverables are confirmed complete with evidence.
- [ ] 100% of test suites pass cleanly.
- [ ] Documentation is fully synchronized and rollback instructions provided.

---

## 8. Error Recovery & Troubleshooting
- If any requirement is found incomplete during final audit, resume implementation before declaring completion.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/final-delivery-audit`. | `CUSTOM SKILL` |
| **Cursor** | Select `@final-delivery-audit` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `final-delivery-audit`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `final-delivery-audit` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run final-delivery-audit`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt final-delivery-audit`. | `PROMPT FILE` |
| **Windsurf** | Activate `final-delivery-audit` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Definition of Done)
- `docs/WALKTHROUGH.md`
