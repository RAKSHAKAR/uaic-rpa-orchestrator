---
name: full-application-validation
description: >-
  Run a risk-based end-to-end acceptance pass across all 8 frontend screens and 8 backend court portal scrapers.
---

# Full Application Validation

## 1. Purpose & Overview
Conducts a comprehensive, holistic platform validation pass proving that all 8 frontend screens, 8 court portal bots, Guidewire integration, and export engines operate in complete harmony with documented evidence.

---

## 2. When to Use & When NOT to Use

### When to Use
- Final acceptance testing prior to client delivery or release tagging.
- Major milestone verification passes.

### When NOT to Use
- Incremental micro-task development.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Running full-stack platform, test spreadsheet (`ProdRecords8Bots.xlsx`), and verification recording harness.

### Prerequisites
- Local dev stack running via `setup_local.ps1`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: System Health & Ping Verification
Navigate to `/health`. Verify all 8 platform components and 8 portal ping checks return healthy status.

### Step 2: 8-Portal Scraper Execution Pass
Trigger claim runs exercising all 8 court bots: Broward, Hillsborough, Miami, Dallas, Travis, Harris JP, Harris District, Harris Clerk.

### Step 3: Dual-Theme Screen Verification
Walk through all 8 frontend routes (`/`, `/claims/:id`, `/upload`, `/monitor`, `/health`, `/exceptions`, `/settings`, `/branding`) in both Light and Dark themes.

### Step 4: Fuzzy Matching & Review Verification
Verify fuzzy matches cascade correctly (Claimant -> Insured -> Driver) and populate `/exceptions` for human review.

### Step 5: Guidewire Cloud Integration
Confirm matched claims format correctly with 9-digit '0' prefix and deliver to Guidewire API.

### Step 6: Bulk Export Verification
Export claims to multi-sheet Excel, CSV summary, and telemetry packages. Verify column schema accuracy.

### Step 7: Full Validation Report & Evidence Archival
Publish the Full Application Validation Report in `docs/` accompanied by video recordings and screenshots.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never declare full application validation complete without actual test logs and visual evidence.
- Ensure all temporary test artifacts and exports are cleanly archived in `exports/`.

---

## 6. Expected Deliverables & Artifacts
- Master Full-Application Validation Report in `docs/`.
- Complete evidentiary package (screenshots, recordings, test logs).

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All 8 court portal scrapers extract valid cases matching schemas.
- [ ] All 8 frontend routes render without errors in Light and Dark themes.
- [ ] Guidewire integration and multi-format exports function with 100% success rate.

---

## 8. Error Recovery & Troubleshooting
- If any single portal or screen fails during the full pass, isolate the failure, patch the root cause, and re-run.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/full-application-validation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@full-application-validation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `full-application-validation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `full-application-validation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run full-application-validation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt full-application-validation`. | `PROMPT FILE` |
| **Windsurf** | Activate `full-application-validation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/WALKTHROUGH.md`
- `docs/CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md`
