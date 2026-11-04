# UAIC Testing Standards

> **Purpose:** Testing patterns, conventions, and quality gates for the UAIC project.
> **Last Updated:** 2026-11-03 (`IMP-2026-1103-002`)

---

## 1. Test Suite Structure

```
backend/
├── tests/                     ← Unit + integration tests (85+ modules, 562+ tests)
│   ├── conftest.py            ← Fixtures, test DB setup, mocks
│   ├── test_<feature>.py      ← Feature-specific test modules
│   └── e2e/                   ← E2E test suites
│       ├── test_e2e_attended_scraping.py
│       └── test_e2e_unattended_scraping.py
e2e/
└── backend/                   ← Mirrored E2E test assets
    └── (Playwright E2E tests)
```

---

## 2. Test Naming Convention

```python
# Format: test_<feature>_<scenario>
def test_fuzzy_engine_claimant_match_above_threshold():
def test_fuzzy_engine_no_match_below_threshold():
def test_guidewire_payload_nine_digit_claim_prefix():
def test_scraper_captcha_waf_session_redispatch():
def test_claims_api_bulk_delete_returns_204():
```

**Module naming:**
```
test_<feature_area>.py              # e.g., test_fuzzy_engine.py
test_<feature_area>_<detail>.py     # e.g., test_fuzzy_engine_enhanced.py
test_imp_<IMP-ID>.py               # e.g., test_imp_2026_1031_003.py (implementation-specific)
```

---

## 3. Fixture Conventions (conftest.py)

### Standard Fixtures

```python
# Database fixtures
@pytest.fixture
async def db_session():
    """Async test DB session (in-memory SQLite)"""

@pytest.fixture
def sample_claim():
    """Minimal valid claim dict for testing"""

@pytest.fixture
def cross_state_claim():
    """Claim with policy_state != loss_location_state (all 8 portals)"""

# Mock fixtures
@pytest.fixture
def mock_celery_task(mocker):
    """Prevent actual Celery task dispatch in unit tests"""

@pytest.fixture
def mock_browser(mocker):
    """Prevent actual Playwright browser launch"""

@pytest.fixture
def mock_guidewire(mocker):
    """Mock Guidewire HTTP responses"""
```

---

## 4. Mock Strategy

### What to Mock in Unit Tests
| Component | Mock with | Reason |
|---|---|---|
| Browser (Playwright) | `pytest-mock` + `AsyncMock` | Slow, requires Chrome |
| Celery tasks | `mocker.patch("app.tasks.*.delay")` | Async, requires Redis |
| Guidewire API | `httpx.AsyncMock` or `responses` | External service |
| SMTP email | `mocker.patch("app.services.email_service.*")` | External service |
| Redis | `fakeredis` or mock | Requires running Redis |
| Settings service | `mocker.patch("get_system_settings_async")` | DB dependency |

### What NOT to Mock in Integration Tests
- Database (use real in-memory SQLite via aiosqlite)
- Excel parsing (use real test files)
- Fuzzy matching logic (always test real RapidFuzz behavior)
- Business rule calculations (state routing, claim prefix, DOL dates)

---

## 5. Test Categories & When to Use

| Category | When | Framework | Speed |
|---|---|---|---|
| **Unit tests** | Isolated function/method logic | pytest | Fast (ms) |
| **Integration tests** | Multiple components together (API + DB) | pytest + httpx AsyncClient | Medium (1-5s) |
| **E2E tests** | Full user workflows via actual browser | Playwright | Slow (30-120s) |
| **Regression tests** | After every bug fix | pytest (existing suite) | Varies |

**Decision rule:**
- Pure business logic (fuzzy engine, DOL date, claim prefix) → Unit test
- API endpoint behavior → Integration test with test client
- Browser automation behavior → E2E test only (never mock Playwright in E2E)
- UI rendering → Manual verification + browser screenshots

---

## 6. pytest Configuration

```toml
# From pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**Running specific test subsets:**
```powershell
# Run full suite
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests -q

# Run specific module
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests/test_fuzzy_engine.py -v

# Run by keyword
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests -k "guidewire" -v

# Run with coverage
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests --cov=app --cov-report=term-missing -q

# Run E2E only
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest e2e/backend -o pythonpath=backend -v
```

---

## 7. Existing Test Module Reference

Key test modules and what they cover:

| Module | Coverage |
|---|---|
| `test_fuzzy_engine.py` | RapidFuzz cascade, threshold, party matching |
| `test_fuzzy_engine_enhanced.py` | Edge cases, unicode, special characters |
| `test_guidewire_client.py` | Auth modes, retry, error handling |
| `test_guidewire_payload_enhanced.py` | Payload construction, 9-digit prefix |
| `test_guidewire_pipeline.py` | End-to-end push pipeline |
| `test_excel_parser.py` | DOL date conversion, column mapping |
| `test_broward_portal.py` | Broward scraper logic |
| `test_dallas_portal.py` | Dallas scraper logic |
| `test_travis_portal.py` | Travis scraper + WAF handling |
| `test_harris_cclerk_portal.py` | Harris Clerk (no CaseType) |
| `test_harris_jp_portal.py` | Harris JP (no CaseType) |
| `test_captcha_waf_session_redispatch.py` | CAPTCHA resolution + cooldown |
| `test_settings_alignment.py` | Settings → runtime parity |
| `test_credentials_security.py` | Secret masking |
| `test_audit_logs.py` | Audit trail completeness |
| `test_email_notifications.py` | Email delivery |
| `test_health_detailed.py` | /health/detailed response |
| `test_api.py` | Full API contract tests |
| `test_database_models.py` | ORM model validation |

---

## 8. Mandatory Quality Gate

Run this complete gate after ANY backend or frontend change:

```powershell
# Step 1: Python lint — MUST be 0 errors
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m ruff check app tests

# Step 2: Backend unit + integration tests — MUST be 0 failures
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests --tb=short -q

# Step 3: E2E backend tests
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest e2e/backend -o pythonpath=backend --tb=short -q

# Step 4: TypeScript type check — MUST be 0 errors
Set-Location d:\scratch\Bot_UAIC\frontend; npx tsc --noEmit

# Step 5: Frontend lint
Set-Location d:\scratch\Bot_UAIC\frontend; npm run lint

# Step 6: PowerShell syntax (if .ps1 changed)
powershell -NoProfile -ExecutionPolicy Bypass -File "d:\scratch\Bot_UAIC\scripts\check_ps1_syntax.ps1"

# Step 7: Docker compose (if docker-compose.yml changed)
docker compose -f d:\scratch\Bot_UAIC\docker-compose.yml config
```

**Required pass rate:** 100% — no failing tests permitted before declaring any task complete.

---

## 9. Test File Placement Rules

| Test Type | Location |
|---|---|
| Unit/integration tests | `backend/tests/test_<feature>.py` |
| E2E backend tests | `backend/tests/e2e/test_e2e_<scenario>.py` AND mirrored to `e2e/backend/` |
| E2E frontend tests | `e2e/frontend/` (Playwright) |
| Scratch/diagnostic scripts | `backend/app/scripts/` or `scripts/` (never in `tests/`) |

---

## 10. Writing Tests for New Features

Template for a new feature test:

```python
"""
Tests for: <feature name>
Coverage: <what business rules/behaviors are tested>
IMP ID: <implementation ID>
"""
import pytest
from httpx import AsyncClient
from app.main import app

pytestmark = pytest.mark.asyncio

class TestFeatureName:
    """Group tests by feature class for readability"""

    async def test_happy_path(self, db_session):
        """Positive case: expected behavior under normal conditions"""
        # Arrange
        ...
        # Act
        ...
        # Assert
        assert result == expected

    async def test_boundary_condition(self, db_session):
        """Edge case at the boundary of valid input"""
        ...

    async def test_error_handling(self, db_session):
        """Negative case: what happens when input is invalid"""
        ...

    async def test_security_constraint(self, db_session):
        """Security case: ensure protected data is not exposed"""
        ...
```

---

## 11. Pre-Existing Test Baseline

| Metric | Value (last verified) |
|---|---|
| Backend test modules | 85+ |
| Backend test count | 562+ (growing) |
| Permitted failures | 0 |
| Permitted skips | 2 (pre-existing baseline — document any additions) |
| Ruff lint errors | 0 |
| TypeScript errors | 0 |
| PS1 syntax errors | 0 |

> [!WARNING]
> **Never delete a failing test to make the suite pass.** If a test is genuinely obsolete, document the reason in a comment and replace it with a valid equivalent.

