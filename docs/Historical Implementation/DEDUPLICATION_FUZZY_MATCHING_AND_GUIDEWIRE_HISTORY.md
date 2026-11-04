# Historical Implementation: Deduplication, Fuzzy Matching & Guidewire Cloud

> **Subsystem:** RapidFuzz Matching Engine & Guidewire Cloud Integration  
> **Historical Scope:** October 2026 Engineering Sprints  
> **Status:** Fully Remediated, Benchmarked & Verified  

---

## 1. RapidFuzz 3-Tier Deduplication Cascade

The matching engine deduplicates extracted court records against claim parties using a 3-tier cascade:
```
1. Claimant (First + Last Name) -> CaseStyle
2. If no match: Insured (First + Last Name) -> CaseStyle
3. If no match: Driver (First + Last Name) -> CaseStyle
```

### Key Milestones:
- **Algorithm**: `rapidfuzz.fuzz.partial_ratio` normalized to `[0.0, 1.0]`.
- **Match Threshold**: Configurable via `SystemSettings.fuzzy_match_threshold` (default: `0.60`).
- **Filing Date Filter**: Case filing date must be `>= 2010-01-01` (configurable in settings).
- **Party Disambiguation Matrix**: Evaluates DualSearch vs TripleSearch count based on name identity equality across Claimant, Insured, and Driver.
- **Unique Names Extraction**: Generates deduplicated lists of search targets across all 3 party columns.

---

## 2. Guidewire Insurance Cloud Integration

### Key Milestones:
- **Payload Contract**:
  ```json
  {
    "ClaimNumber": "0123456789",
    "ExposureNumber": "001",
    "CaseItems": [
      {
        "CaseNumber": "COCE-22-019482",
        "CaseStyle": "STATE FARM vs JOHN SMITH",
        "CountyWebsite": "https://www.browardclerk.org/Web2",
        "SuitFiledDate": "04/12/2022"
      }
    ]
  }
  ```
- **9-Digit Claim Number Rule**: If `len(claim_number) == 9`, prepend `"0"` (e.g. `123456789` -> `0123456789`). Applied only to Guidewire JSON payload.
- **DOL Base Date Normalization**: Serial dates parsed from Excel files use base `1899-12-30`, formatted as `MM/dd/yyyy` without timezone drift.
- **Authentication Resilience**: Supports API Key, Bearer Token, Basic Auth, and OAuth2 Client Credentials with automatic token refresh.
- **Retry Logic**: Exponential backoff retry (3 attempts) on network errors (HTTP 502/503/504).

