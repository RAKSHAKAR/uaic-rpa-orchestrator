# Backend End-to-End (E2E) Test Suite

Comprehensive backend integration and end-to-end automation test suite for the UAIC Claim & RPA Orchestrator.

---

## 1. Test Suite Coverage

| Test File | Scope |
|---|---|
| `test_e2e_portal_pings.py` | Validates live reachability & streaming latency across all 8 Florida and Texas court portals |
| `test_e2e_browser_engine.py` | Validates Playwright bundled Chromium discovery, Google Chrome discovery, and AntiCaptcha directory resolution |
| `test_e2e_health_detailed.py` | Validates `/api/v1/health/detailed` full 8-module core stack and 8-portal registry |
| `test_e2e_attended_scraping.py` | Full flow attended scraping orchestration |
| `test_e2e_unattended_scraping.py` | Full flow background unattended scraping orchestration |

---

## 2. Running Backend E2E Tests

From the repository root:
```bash
# Run all backend E2E tests
backend\.venv\Scripts\pytest e2e/backend -v

# Run with short tracebacks
backend\.venv\Scripts\pytest e2e/backend --tb=short -q
```
