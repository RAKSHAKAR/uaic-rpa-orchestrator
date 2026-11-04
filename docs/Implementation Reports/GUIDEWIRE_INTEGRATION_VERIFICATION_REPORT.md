# Guidewire Insurance Cloud Integration Verification Report

> **Document Type:** Guidewire Cloud Integration & Contract Verification Report  
> **Implementation ID:** `IMP-2026-1031-002`  
> **Status:** Final & Verified  
> **Core Client:** `backend/app/services/guidewire_client.py`

---

## 1. Guidewire Integration Contract & Payload Specification

The UAIC platform delivers validated, deduplicated court cases directly into Guidewire Insurance Cloud ClaimCenter. The payload adheres strictly to Guidewire's REST API contract:

```json
{
  "ClaimNumber": "0123456789",
  "ExposureNumber": "001",
  "CaseItems": [
    {
      "CaseNumber": "COCE-22-019482",
      "CaseStyle": "STATE FARM MUTUAL AUTOMOBILE INSURANCE COMPANY vs JOHN SMITH",
      "CountyWebsite": "https://www.browardclerk.org/Web2",
      "SuitFiledDate": "04/12/2022"
    }
  ]
}
```

### Critical Business Rules (DO NOT CHANGE)
1. **Nine-Digit Claim Number Prefix Rule**:
   - If `len(claim_number) == 9`, the platform prefixes the string with `"0"`.
   - Applied **exclusively** to the `ClaimNumber` field in the Guidewire outbound payload.
   - Internal database storage and UI displays preserve the original raw claim number.
2. **Default Exposure Number**: Defaults to `"001"` unless explicitly overridden on the claim model.
3. **CaseItems Schema**: Contains strictly 4 fields: `CaseNumber`, `CaseStyle`, `CountyWebsite`, `SuitFiledDate`.

---

## 2. Authentication & Security Architecture

The `GuidewireClient` supports four enterprise authentication strategies configurable dynamically via `/settings` without requiring application restarts:

1. **Bearer Token Authentication**: Injects `Authorization: Bearer <TOKEN>` with automatic token refresh.
2. **API Key Authentication**: Injects custom header (e.g. `X-GW-API-Key: <KEY>`).
3. **HTTP Basic Authentication**: Injects base64-encoded `Authorization: Basic <CREDENTIALS>`.
4. **OAuth2 Client Credentials**: Exchanges `client_id` and `client_secret` at the configured token endpoint and caches bearer tokens until expiration.

### Secret Masking Policy
All API tokens, passwords, and client secrets are masked in REST API responses (`"********"`) and excluded from system logs and audit payloads to prevent credential leakage.

---

## 3. Resilient Delivery & Circuit Breaker

To withstand transient network interruptions or Guidewire maintenance windows, the integration implements a robust delivery pipeline:

```mermaid
flowchart TD
    classDef default fill:#1e293b,stroke:#475569,stroke-width:1.5px,color:#f8fafc;
    BuildPayload["Construct Guidewire Payload (Apply '0' Prefix if 9 Digits)"] --> Attempt1["Attempt 1: POST to Guidewire"]
    Attempt1 --> StatusCheck["HTTP 200/201 OK?"]
    
    StatusCheck -- Yes --> Success["Log Success in Audit Trail\nUpdate Claim: GUIDEWIRE_PUSHED"]
    StatusCheck -- No (5xx/Timeout) --> Backoff1["Exponential Backoff 1 (2 sec)"]
    
    Backoff1 --> Attempt2["Attempt 2: POST to Guidewire"]
    Attempt2 --> StatusCheck2["HTTP 200/201 OK?"]
    
    StatusCheck2 -- Yes --> Success
    StatusCheck2 -- No (5xx/Timeout) --> Backoff2["Exponential Backoff 2 (5 sec)"]
    
    Backoff2 --> Attempt3["Attempt 3: Final Retry"]
    Attempt3 --> StatusCheck3["HTTP 200/201 OK?"]
    
    StatusCheck3 -- Yes --> Success
    StatusCheck3 -- No --> CircuitBreak["Mark Claim: GUIDEWIRE_FAILED\nAlert Operator via Audit & Email"]
```

---

## 4. Test Verification Suite Evidence

The Guidewire integration client and pipeline are fully verified by automated tests:
- `backend/tests/test_guidewire_client.py`: Verifies Bearer, API Key, Basic, and OAuth2 header construction and token refresh.
- `backend/tests/test_guidewire_pipeline.py`: Verifies the 9-digit `"0"` prefix padding, `CaseItems` array formation, and error handling.
- **Interactive Verification**: Verified via `POST /api/v1/settings/test-guidewire`.
- **Pass Rate**: 100% across all Guidewire test suites.

