# E2E Tests

End-to-end and browser automation tests for the UAIC Claim & RPA Orchestrator.

## Structure

`
e2e/
├── backend/    ← Backend E2E browser automation tests (Python/Playwright)
├── frontend/   ← Frontend E2E tests (placeholder — see README inside)
└── README.md
`

## Backend E2E Tests

Located in `e2e/backend/` (mirrored from `backend/tests/e2e/`):

| File | Description |
|------|-------------|
| `test_e2e_attended_scraping.py` | Attended (visible GUI) browser automation tests |
| `test_e2e_unattended_scraping.py` | Unattended (headless) browser automation tests |

### Running Backend E2E Tests

`ash
cd backend
.venv\Scripts\pytest tests/e2e/ -m e2e --tb=short -v
`

## Backend Unit Tests

All 556 backend unit/integration tests live in `backend/tests/` and are run via:

`ash
cd backend
.venv\Scripts\pytest --tb=short -q
`

## Markers

- `@pytest.mark.e2e` — End-to-end tests (require real browser + running backend)
- `@pytest.mark.unattended` — Unattended headless automation tests

> **Note:** E2E tests require a running backend, Redis, and configured Chrome with AntiCaptcha extension.
