---
name: uaic-guidewire-integration
description: >-
  Validate Guidewire Insurance Cloud payload construction, 9-digit '0' prefix, CaseItems array, and delivery retry logic.
---

# Uaic Guidewire Integration

## 1. Purpose & Overview
Manages outbound integration with Guidewire Insurance Cloud, formatting approved match results into the exact JSON payload contract and managing retry delivery with exponential backoff.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pushing matched court cases to Guidewire (`/api/v1/claims/{id}/push-guidewire`).
- Testing Guidewire API connection and payload formatting.

### When NOT to Use
- Internal database querying.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Matched claim record, approved court cases, and Guidewire API credentials.

### Prerequisites
- `GuidewireClient` configured in `app/services/guidewire_client.py`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Claim Number Formatting
Format claim number using `format_claim_number(claim_number)`: if length is 9 digits, prefix with '0' (e.g. `123456789` -> `0123456789`).

### Step 2: Exposure Number & Case Items Construction
Construct `CaseItems` array with objects: `CaseNumber`, `CaseStyle`, `CountyWebsite`, `SuitFiledDate` (normalized MM/DD/YYYY). Set `ExposureNumber: '001'`.

### Step 3: Payload Serialization
Serialize payload matching contract: `{"ClaimNumber": "...", "ExposureNumber": "001", "CaseItems": [...]}`.

### Step 4: Outbound HTTP Delivery
Dispatch POST request via `GuidewireClient` with configured authentication (Bearer, ApiKey, Basic, or OAuth2).

### Step 5: Delivery Response & Audit Logging
Record HTTP status and response body in `GuidewireActivity` table. Update claim status to `PUSH_SUCCEEDED`.

### Step 6: Retry on Transient Failure
If Guidewire returns 5xx or timeout, queue task for retry with exponential backoff; update status to `PUSH_FAILED`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: 9-digit ClaimNumber '0' prefix must ONLY be applied in Guidewire payload; never alter original ClaimNumber in database.
- Mask Guidewire API tokens in audit logs.

---

## 6. Expected Deliverables & Artifacts
- Formatted Guidewire payload delivery.
- Recorded `GuidewireActivity` audit log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Payload strictly adheres to Guidewire JSON contract.
- [ ] 9-digit claim numbers have leading '0' prefix.
- [ ] Successful delivery transitions claim to `PUSH_SUCCEEDED`.

---

## 8. Error Recovery & Troubleshooting
- If Guidewire rejects payload due to schema mismatch, inspect `GuidewireActivity` log and correct serializer.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-guidewire-integration`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-guidewire-integration` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-guidewire-integration`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-guidewire-integration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-guidewire-integration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-guidewire-integration`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-guidewire-integration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 11 (Guidewire Payload Contract)
- `backend/app/services/guidewire_client.py`
