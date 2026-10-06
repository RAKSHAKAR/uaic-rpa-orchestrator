# Frontend End-to-End (E2E) Test Suite

Comprehensive Playwright test automation suite covering all primary UI views and workflows of the UAIC Claim & RPA Orchestrator frontend application.

---

## 1. Test Suite Coverage

| Test File | Target Route | Scope |
|---|---|---|
| `tests/dashboard.spec.ts` | `/` | Header, navigation, stats metrics cards, claims table, search filter, action links |
| `tests/settings.spec.ts` | `/settings` | Engine selection (Chromium, Chrome, Edge), Attended vs Headless, portal pings, settings save |
| `tests/health.spec.ts` | `/health` | System posture banner, RPA browser status, 8 core infrastructure cards, 8 court portal pings |
| `tests/monitor.spec.ts` | `/monitor` | Queue monitor cards (Active, Queued, Completed, Failed), queue control actions, active claims table |
| `tests/branding.spec.ts` | `/branding` | Light/Dark theme toggle, 26 semantic color tokens, company logo preview, reset |
| `tests/audit.spec.ts` | `/audit` | Audit trail logs, action filters, payload modal viewer |
| `tests/upload.spec.ts` | `/upload` | File dropzone, sample template download, column mapping interface, preview |

---

## 2. Running Frontend E2E Tests

### Prerequisites
Ensure the frontend development server or production container is running:
- Docker: `http://localhost:3000`
- Or local development server: `cd frontend && npm run dev`

### Execution Commands
```bash
cd e2e/frontend

# Install dependencies (first time only)
npm install

# Run all Playwright tests headlessly
npx playwright test

# Run tests with interactive UI
npx playwright test --ui

# Run tests in headed browser mode
npx playwright test --headed

# View HTML test execution report
npx playwright show-report
```
