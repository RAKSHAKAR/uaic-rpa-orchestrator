"""
Category E: Testing & Quality Assurance
Contains 18 comprehensive skills for test strategies, unit/integration testing,
Playwright browser automation, E2E validation, performance, and security testing.
"""

SKILLS_E = [
    {
        "name": "test-strategy",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Define multi-level testing strategies, scope, test environments, mock fixtures, and exit gates across the pyramid.",
        "purpose": "Establishes a cohesive testing strategy balancing fast unit tests, integrated service tests, and end-to-end browser verification, ensuring high defect detection at minimal CI cost.",
        "when_to_use": [
            "Initiating a new feature stream, subsystem, or platform migration.",
            "Auditing and upgrading project test infrastructure."
        ],
        "when_not_to_use": [
            "Writing a single unit test function."
        ],
        "required_inputs": [
            "System architecture, critical risk paths, and SLA requirements."
        ],
        "prerequisites": [
            "Completed `architecture-analysis`."
        ],
        "procedure": [
            ("Test Pyramid Partitioning", "Allocate testing efforts: 70% Unit Tests (fast, isolated), 20% Integration Tests (database, API, queues), 10% E2E Browser Tests (Playwright user journeys)."),
            ("Environment & Fixture Strategy", "Define test fixtures (`conftest.py`), SQLite in-memory databases, and mock strategies for external services (Guidewire, SMTP)."),
            ("Gate Criteria Formulation", "Establish non-negotiable PR gates: 100% test pass rate, 0 lint errors, and 0 TypeScript errors."),
            ("Flaky Test Prevention Policy", "Establish policies for deterministic tests: fixed clocks, explicit locators, and zero arbitrary sleep statements."),
            ("Test Strategy Document Synthesis", "Publish the formal Test Strategy Document in `docs/`.")
        ],
        "safety": [
            "Never rely exclusively on E2E tests for logic that can be tested in fast unit tests.",
            "Never allow flaky tests to be permanently ignored."
        ],
        "deliverables": [
            "Formal Test Strategy Document in `docs/`.",
            "Test Pyramid Coverage Plan."
        ],
        "acceptance_criteria": [
            "Test levels, tooling, and responsibilities are explicitly defined.",
            "Mocking boundaries for third-party systems are established.",
            "Automated quality gates are documented with exact commands."
        ],
        "error_recovery": [
            "If CI execution times become prohibitive, shift slow integration tests to nightly runs or parallelize."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/test-strategy`.",
            "cursor": "Select `@test-strategy` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `test-strategy`.",
            "codex": "Reference `test-strategy` in Codex context.",
            "gemini": "Invoke via `gemini run test-strategy`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt test-strategy`.",
            "windsurf": "Activate `test-strategy` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 7 (Test Commands)",
            "`backend/tests/conftest.py`"
        ]
    },
    {
        "name": "unit-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Create and run isolated, high-speed unit tests with mocked external dependencies using pytest.",
        "purpose": "Authors focused, deterministic unit tests validating pure business logic, fuzzy matching algorithms, date conversions, and data parsing in sub-millisecond execution times.",
        "when_to_use": [
            "Implementing or modifying business logic functions, algorithms, or utility classes.",
            "Verifying date conversion, string normalization, or search count calculations."
        ],
        "when_not_to_use": [
            "Testing full database persistence or multi-service browser workflows."
        ],
        "required_inputs": [
            "Target function/module to test and specification of expected inputs/outputs."
        ],
        "prerequisites": [
            "Configured pytest test runner in `backend/.venv`."
        ],
        "procedure": [
            ("Test Case Identification", "Enumerate happy path, boundary values, null inputs, invalid formats, and exception cases."),
            ("Mocking & Isolation Setup", "Mock all external dependencies (network, database, filesystem) using `unittest.mock.MagicMock` or `AsyncMock`."),
            ("Test Implementation", "Author pytest functions following Arrange-Act-Assert pattern in `backend/tests/`."),
            ("Parameterized Testing", "Use `@pytest.mark.parametrize` for tabular test matrices (e.g. DualSearch/TripleSearch party combinations)."),
            ("Test Execution & Assertion Verification", "Execute tests using `.venv\\Scripts\\pytest <test_file> -q`. Confirm fast, green execution."),
            ("Coverage Verification", "Verify that target functions achieve 100% branch coverage.")
        ],
        "safety": [
            "Never make live network or database calls in unit tests.",
            "Do not assert on non-deterministic values (e.g. dynamic current time) without time-freezing fixtures."
        ],
        "deliverables": [
            "Unit test file in `backend/tests/` with high assertion density.",
            "Test execution log demonstrating 100% pass rate."
        ],
        "acceptance_criteria": [
            "All unit tests execute in under 100ms per test.",
            "Happy path, edge cases, and exception states are thoroughly asserted.",
            "Test suite passes cleanly with zero warnings or failures."
        ],
        "error_recovery": [
            "If tests fail due to mock leakage, verify mocks are cleanly reset between test runs using fixtures."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/unit-testing`.",
            "cursor": "Select `@unit-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `unit-testing`.",
            "codex": "Reference `unit-testing` in Codex context.",
            "gemini": "Invoke via `gemini run unit-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt unit-testing`.",
            "windsurf": "Activate `unit-testing` in Windsurf."
        },
        "references": [
            "`backend/tests/test_v4_parity.py`",
            "`backend/tests/test_fuzzy_matching.py`"
        ]
    },
    {
        "name": "integration-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Verify interactions across database transactions, FastAPI endpoints, and Celery asynchronous task dispatch.",
        "purpose": "Tests the integration boundaries between application services, verifying that database transactions commit cleanly, foreign keys cascade properly, and async tasks dispatch with correct payload arguments.",
        "when_to_use": [
            "Testing API endpoints that persist data to SQLite or PostgreSQL.",
            "Verifying Celery task dispatch and worker state reconciliation.",
            "Testing Excel/CSV ingestion pipelines end-to-end."
        ],
        "when_not_to_use": [
            "Pure isolated unit logic with zero external interfaces."
        ],
        "required_inputs": [
            "Service interfaces, test database fixtures, and Celery task definitions."
        ],
        "prerequisites": [
            "Configured async SQLAlchemy test session and Redis/memory broker."
        ],
        "procedure": [
            ("Test Fixture Setup", "Initialize isolated test database using `AsyncSessionLocal` fixture with automated rollback after each test."),
            ("API Endpoint Invocation", "Execute requests against FastAPI app using `httpx.AsyncClient` and `ASGITransport`."),
            ("Database State Assertion", "Query the database directly using SQLAlchemy `select()` to verify record creation, state mutation, and timestamps."),
            ("Task Dispatch Verification", "Verify Celery task dispatch using task inspection or eager execution mode (`task_always_eager=True`)."),
            ("Transaction Rollback & Cleanup", "Confirm test database state is cleanly reset, ensuring test independence."),
            ("Test Suite Pass", "Run `pytest tests/test_api.py -q`.")
        ],
        "safety": [
            "NEVER run integration tests against production databases.",
            "Ensure tests do not leave lingering records that corrupt subsequent test runs."
        ],
        "deliverables": [
            "Integration test suite in `backend/tests/`.",
            "Test execution log demonstrating verified database persistence."
        ],
        "acceptance_criteria": [
            "Endpoints return expected HTTP status codes and persist correct data to database.",
            "Database constraints, unique indexes, and foreign keys are verified.",
            "Test database resets cleanly between runs."
        ],
        "error_recovery": [
            "If async transactions stall or deadlock, ensure all `AsyncSession` instances are cleanly closed in test teardown."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/integration-testing`.",
            "cursor": "Select `@integration-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `integration-testing`.",
            "codex": "Reference `integration-testing` in Codex context.",
            "gemini": "Invoke via `gemini run integration-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt integration-testing`.",
            "windsurf": "Activate `integration-testing` in Windsurf."
        },
        "references": [
            "`backend/tests/test_api.py`",
            "`backend/tests/test_async_export.py`"
        ]
    },
    {
        "name": "e2e-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Verify critical end-to-end user journeys using Playwright across frontend UI, backend APIs, and automation bots.",
        "purpose": "Simulates complete end-to-end operator journeys (uploading an Excel claim file, reviewing fuzzy matches, launching attended bots, exporting results) across the full running stack.",
        "when_to_use": [
            "Validating full-stack release candidates.",
            "Verifying multi-screen workflows connecting upload, claims detail, monitor, and settings."
        ],
        "when_not_to_use": [
            "Testing isolated helper functions."
        ],
        "required_inputs": [
            "Running full-stack environment (FastAPI on 8000, Next.js on 3000, Redis on 6379).",
            "Playwright test scripts in `e2e/`."
        ],
        "prerequisites": [
            "Local services started via `setup_local.ps1` or Docker."
        ],
        "procedure": [
            ("Environment Readiness Check", "Verify `/api/v1/health` and `http://localhost:3000` respond with HTTP 200."),
            ("Journey Navigation & Data Entry", "Launch Playwright browser. Navigate to `/upload`, upload test Excel file (`ProdRecords8Bots.xlsx`), and submit."),
            ("State Transition Monitoring", "Verify claims appear on `/` dashboard. Monitor queue status on `/monitor` as Celery processes records."),
            ("Exception Review & Fuzzy Verification", "Navigate to `/exceptions`, verify fuzzy match candidate card, click Approve, and confirm status transition."),
            ("Guidewire Dispatch Verification", "Verify claim reaches `PUSHED` status and Guidewire activity log is populated."),
            ("Artifact & Evidence Recording", "Capture Playwright trace, screenshot, or video recording verifying the journey.")
        ],
        "safety": [
            "Use dedicated test claims and seed fixtures; do not pollute production data.",
            "Clean up generated export files and temporary upload artifacts after test completion."
        ],
        "deliverables": [
            "Playwright E2E test scripts in `e2e/`.",
            "Video recording (.webp) or screenshot (.png) verification artifact in `docs/`."
        ],
        "acceptance_criteria": [
            "Complete user journey succeeds from file upload to Guidewire push without manual intervention.",
            "All assertions on UI elements, status badges, and database state pass.",
            "Visual evidence is captured and documented."
        ],
        "error_recovery": [
            "If Playwright locators time out, inspect browser DOM snapshots to confirm whether element IDs or classes changed."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/e2e-testing`.",
            "cursor": "Select `@e2e-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `e2e-testing`.",
            "codex": "Reference `e2e-testing` in Codex context.",
            "gemini": "Invoke via `gemini run e2e-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt e2e-testing`.",
            "windsurf": "Activate `e2e-testing` in Windsurf."
        },
        "references": [
            "`e2e/backend/`",
            "`docs/WALKTHROUGH.md`"
        ]
    },
    {
        "name": "browser-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Automate and record real browser execution in genuine Google Chrome with AntiCaptcha extensions.",
        "purpose": "Exercises court portal automation in genuine attended Chrome instances, verifying extension loading, CAPTCHA token injection, party name search, and row extraction with video evidence.",
        "when_to_use": [
            "Testing court scraper implementations against Florida and Texas portals.",
            "Validating AntiCaptcha Manifest V3 extension solving and DOM token injection.",
            "Capturing video recordings for client demonstrations."
        ],
        "when_not_to_use": [
            "Headless API unit testing."
        ],
        "required_inputs": [
            "Installed Google Chrome, unpacked `anticaptcha-plugin_v0.83/`, portal URLs, and test party names."
        ],
        "prerequisites": [
            "Synchronous Playwright with `ChromeSession` architecture."
        ],
        "procedure": [
            ("Browser Manager Launch", "Launch Chrome using `SingleSessionBrowserRunner` or `Launch_Attended_Browser.bat` with `--load-extension` flags pointing to `anticaptcha-plugin_v0.83`."),
            ("Extension Readiness Check", "Verify AntiCaptcha extension loads, pinned status, and API key presence via `chrome://extensions` or DOM flags."),
            ("Portal Navigation & Tab Management", "Navigate to portal URL. Switch to target search tab (Party Name) using reliable CSS locators."),
            ("Search Form Interaction", "Fill party Last Name, First Name, and DOL normalized to `MM/dd/yyyy` format."),
            ("CAPTCHA Handling & Token Verification", "Wait for solve tokens (`g-recaptcha-response`, `cf-turnstile-response`). Verify resolution before search submission."),
            ("Result Table Extraction & Verification", "Extract table rows, parse columns matching portal schema, and verify zero glossary rows (`CACE`, `COCE`) are included."),
            ("Video & Screenshot Evidence Capture", "Record browser session into WebP or MP4 artifact and save to `docs/`.")
        ],
        "safety": [
            "CRITICAL: Never use aggressive Chrome process termination (`taskkill /f /im chrome.exe`) while an attended user session is running.",
            "Block speculative form submits when an active, unsolved CAPTCHA challenge is present."
        ],
        "deliverables": [
            "Verified scraper execution logs with extracted case count.",
            "Playwright browser video recording (.webp) in `docs/`."
        ],
        "acceptance_criteria": [
            "Chrome launches with AntiCaptcha extension active and functional.",
            "Portal search executes and parses matching cases into the exact 5-field schema.",
            "Video recording confirms smooth, human-paced browser interaction."
        ],
        "error_recovery": [
            "If portal returns a transient Cloudflare block, implement retry with exponential backoff or proxy rotation."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/browser-testing` or slash command `/browser`.",
            "cursor": "Select `@browser-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `browser-testing`.",
            "codex": "Reference `browser-testing` in Codex context.",
            "gemini": "Invoke via `gemini run browser-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt browser-testing`.",
            "windsurf": "Activate `browser-testing` in Windsurf."
        },
        "references": [
            "`backend/app/automation/base.py`",
            "`backend/app/automation/browser_manager.py`"
        ]
    },
    {
        "name": "ui-ux-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Validate visual consistency, dual-theme rendering, component states, and responsive interactions.",
        "purpose": "Conducts detailed visual and experiential testing across all frontend pages, checking typography alignment, color token fidelity, loading spinners, and empty states.",
        "when_to_use": [
            "Verifying new frontend features or design system token updates.",
            "Pre-release visual quality passes."
        ],
        "when_not_to_use": [
            "Backend server testing."
        ],
        "required_inputs": [
            "Frontend application running locally on port 3000.",
            "Dual-theme color specifications."
        ],
        "prerequisites": [
            "Next.js frontend running and reachable."
        ],
        "procedure": [
            ("Light Mode Visual Walkthrough", "Inspect every page under Light Mode. Verify high-contrast readable text, clean borders, and clear card backgrounds."),
            ("Dark Mode Visual Walkthrough", "Toggle theme to Dark Mode. Confirm zero black-on-black text, readable input fields, and consistent slate/gray elevation."),
            ("State Transitions Inspection", "Trigger loading states (skeleton loaders), empty states (zero search matches), and error banners. Verify visual polish."),
            ("Interactive Controls & Hover Effects", "Test button hover/active states, dropdown menus, modal overlays, and toast notifications."),
            ("Screenshot Evidence Archival", "Capture side-by-side screenshots of key views in both themes and save to `docs/`.")
        ],
        "safety": [
            "Never allow un-themed rogue CSS styles to pass UI verification.",
            "Ensure modal dialogs maintain high-contrast backdrops."
        ],
        "deliverables": [
            "UI/UX Visual Inspection Report.",
            "Dual-theme screenshot comparison artifacts in `docs/`."
        ],
        "acceptance_criteria": [
            "100% of pages render flawlessly in both Light Mode and Dark Mode.",
            "Zero white-on-white or black-on-black contrast violations exist.",
            "All state transitions (loading, empty, error) display appropriate visual feedback."
        ],
        "error_recovery": [
            "If an element displays poor contrast in Dark Mode, adjust Tailwind tokens to use explicit `dark:` modifiers."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/ui-ux-testing`.",
            "cursor": "Select `@ui-ux-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `ui-ux-testing`.",
            "codex": "Reference `ui-ux-testing` in Codex context.",
            "gemini": "Invoke via `gemini run ui-ux-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt ui-ux-testing`.",
            "windsurf": "Activate `ui-ux-testing` in Windsurf."
        },
        "references": [
            "`.agents/skills/theme-system/SKILL.md`",
            "`frontend/src/app/branding/page.tsx`"
        ]
    },
    {
        "name": "api-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Verify REST contracts, payload validation, status codes, query pagination, and error responses via automated tests.",
        "purpose": "Ensures all FastAPI endpoints conform strictly to OpenAPI specifications, validate input bounds, return typed JSON models, and handle error scenarios predictably.",
        "when_to_use": [
            "Adding or modifying REST API endpoints in `app/api/v1/endpoints/`.",
            "Verifying pagination, sorting, and bulk operation endpoints."
        ],
        "when_not_to_use": [
            "Frontend-only styling changes."
        ],
        "required_inputs": [
            "FastAPI endpoint definitions and Pydantic schemas."
        ],
        "prerequisites": [
            "`httpx` async test client and test database fixtures."
        ],
        "procedure": [
            ("Schema & Contract Assertion", "Send valid request bodies and verify response status (200 OK / 201 Created) and JSON structure against Pydantic response models."),
            ("Validation Rejection Testing", "Send malformed JSON, out-of-bounds parameters, and invalid types. Confirm 422 Unprocessable Entity with descriptive error arrays."),
            ("Pagination & Filtering Testing", "Test query parameters (`skip=0&limit=10`, `status=NEW`). Verify returned records match filters and total counts are accurate."),
            ("Not Found & Edge Case Scenarios", "Request non-existent resource IDs (e.g. UUIDs). Verify 404 Not Found is returned."),
            ("Security & Authorization Checks", "Test unauthorized calls to protected endpoints. Confirm 401 or 403 responses."),
            ("Test Suite Pass", "Run `pytest tests/test_api.py -q`.")
        ],
        "safety": [
            "Never test endpoints by making mutating requests to live production environments.",
            "Ensure sensitive customer data is never used in automated test payloads."
        ],
        "deliverables": [
            "Automated API contract test suite in `backend/tests/`.",
            "Test execution log demonstrating 100% pass rate."
        ],
        "acceptance_criteria": [
            "All endpoints return valid JSON matching declared Pydantic schemas.",
            "422 errors provide specific field error locations and messages.",
            "Pagination parameters are strictly validated and enforced."
        ],
        "error_recovery": [
            "If Pydantic serialization fails, check for unhandled SQLAlchemy model relationships or timezone-naive datetimes."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/api-testing`.",
            "cursor": "Select `@api-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `api-testing`.",
            "codex": "Reference `api-testing` in Codex context.",
            "gemini": "Invoke via `gemini run api-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt api-testing`.",
            "windsurf": "Activate `api-testing` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 5 (API Endpoints Summary)",
            "`backend/tests/test_api.py`"
        ]
    },
    {
        "name": "database-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Verify relational constraints, schema migrations, transactional atomicity, and data integrity under concurrent operations.",
        "purpose": "Tests database models and queries to prove that foreign key cascades function safely, unique constraints prevent duplicate records, and transactions roll back cleanly upon errors.",
        "when_to_use": [
            "Adding or modifying SQLAlchemy models in `app/models/`.",
            "Validating database migration scripts (`upgrade()` and `downgrade()`).",
            "Testing soft-delete or enterprise data retention cleanup logic."
        ],
        "when_not_to_use": [
            "Testing pure frontend UI interactions."
        ],
        "required_inputs": [
            "SQLAlchemy models, migration scripts, and test database connection."
        ],
        "prerequisites": [
            "Async SQLite and PostgreSQL test runners."
        ],
        "procedure": [
            ("Constraint & Index Verification", "Test primary keys, unique constraints (e.g. claim number uniqueness), and non-null constraints by asserting database error raises."),
            ("Foreign Key & Cascade Verification", "Verify relationship integrity: deleting a parent record correctly cascades or nullifies related records according to model rules."),
            ("Transaction Atomicity & Rollback", "Simulate exceptions mid-transaction; verify that all intermediate database writes are rolled back cleanly."),
            ("Migration Upgrade/Downgrade Cycle", "Execute migration upgrade and immediate downgrade on a populated test database. Verify zero data corruption."),
            ("Cleanup Service Testing", "Execute enterprise data retention cleanups (`execute_enterprise_cleanup`) and verify targeted tables are pruned accurately."),
            ("Test Suite Pass", "Run `pytest tests/test_database_models.py tests/test_enterprise_cleanup.py -q`.")
        ],
        "safety": [
            "CRITICAL: Never execute destructive database tests on production databases.",
            "Ensure all test transactions execute within isolated test sessions."
        ],
        "deliverables": [
            "Database model and transaction test suite in `backend/tests/`.",
            "Test execution log confirming constraint and migration integrity."
        ],
        "acceptance_criteria": [
            "Constraints prevent duplicate and invalid data insertion.",
            "Transaction rollback guarantees atomic all-or-nothing persistence.",
            "Enterprise cleanup prunes expired records while strictly preserving active claims."
        ],
        "error_recovery": [
            "If database locks occur during test teardown, verify all connections in the pool are cleanly closed."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/database-testing`.",
            "cursor": "Select `@database-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `database-testing`.",
            "codex": "Reference `database-testing` in Codex context.",
            "gemini": "Invoke via `gemini run database-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt database-testing`.",
            "windsurf": "Activate `database-testing` in Windsurf."
        },
        "references": [
            "`backend/tests/test_database_models.py`",
            "`backend/tests/test_enterprise_cleanup.py`"
        ]
    },
    {
        "name": "regression-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Execute comprehensive regression suites to guarantee that existing supported features remain completely functional after changes.",
        "purpose": "Executes full test suites across unit, integration, and E2E suites to detect unintended side-effects or regressions introduced by new features or bug fixes.",
        "when_to_use": [
            "Following ANY code modification before declaring a task complete.",
            "Pre-release qualification passes.",
            "After upgrading dependencies or refactoring core architecture."
        ],
        "when_not_to_use": [
            "Initial exploratory spikes in throwaway scratch files."
        ],
        "required_inputs": [
            "Full repository test suites across backend, frontend, and shell scripts."
        ],
        "prerequisites": [
            "Passing test baseline established prior to changes."
        ],
        "procedure": [
            ("Backend Test Suite Execution", "Run `backend\\.venv\\Scripts\\pytest -q` across all 67 test suites. Confirm all 556 tests pass (with 2 pre-existing skips)."),
            ("Backend E2E Suite Execution", "Run `backend\\.venv\\Scripts\\pytest e2e/backend -o pythonpath=backend -q`. Confirm 17/17 tests pass."),
            ("Frontend TypeScript Compile", "Run `cd frontend && npx tsc --noEmit`. Confirm 0 TypeScript compilation errors."),
            ("Backend Linting Check", "Run `cd backend && .venv\\Scripts\\ruff check app tests`. Confirm 0 errors."),
            ("PowerShell Syntax Check", "Run `powershell -File scripts/check_ps1_syntax.ps1`. Confirm 0 syntax errors across all 13 scripts."),
            ("Regression Pass Log Synthesis", "Document all test execution counts, pass rates, and execution times.")
        ],
        "safety": [
            "CRITICAL: Never declare completion if any pre-existing test begins failing.",
            "Do NOT modify existing test assertions merely to make failing tests pass."
        ],
        "deliverables": [
            "Full Regression Test Execution Report.",
            "Verified green status across all test suites."
        ],
        "acceptance_criteria": [
            "556 backend unit/integration tests pass with 100% success rate.",
            "17 backend E2E tests pass with 100% success rate.",
            "Frontend TypeScript compiles with 0 errors.",
            "PowerShell scripts pass with 0 syntax errors."
        ],
        "error_recovery": [
            "If any regression is detected, immediately diagnose the root cause and resolve it before proceeding."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/regression-testing`.",
            "cursor": "Select `@regression-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `regression-testing`.",
            "codex": "Reference `regression-testing` in Codex context.",
            "gemini": "Invoke via `gemini run regression-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt regression-testing`.",
            "windsurf": "Activate `regression-testing` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 7 (Test Commands)",
            "`scripts/check_ps1_syntax.ps1`"
        ]
    },
    {
        "name": "cross-browser-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Validate application rendering, layouts, and JavaScript execution across Chromium, Firefox, and WebKit browser engines.",
        "purpose": "Ensures the web application functions identically and consistently across all major web browser engines without engine-specific rendering bugs or CSS breakage.",
        "when_to_use": [
            "Pre-release testing of the frontend web application.",
            "Testing advanced CSS layouts, sticky scrollbars, or flexbox containers."
        ],
        "when_not_to_use": [
            "Court portal automation bots (which are strictly pinned to Google Chrome for AntiCaptcha MV3 stability)."
        ],
        "required_inputs": [
            "Next.js frontend application running locally on port 3000.",
            "Playwright browser engines (Chromium, Firefox, WebKit)."
        ],
        "prerequisites": [
            "Playwright browser binaries installed."
        ],
        "procedure": [
            ("Chromium Engine Pass", "Execute Playwright suite against Chromium. Capture baseline rendering and layout measurements."),
            ("Firefox Engine Pass", "Execute suite against Firefox. Check font rendering, form control styles, and CSS grid alignment."),
            ("WebKit Engine Pass", "Execute suite against WebKit (Safari engine). Check date inputs, flexbox alignments, and backdrop blur filters."),
            ("Discrepancy Cataloguing", "Log any layout shifts, font mismatches, or interaction differences between engines."),
            ("CSS Prefix & Fallback Remediation", "Apply standard CSS vendor fallbacks to eliminate cross-browser inconsistencies.")
        ],
        "safety": [
            "Remember that court automation scrapers are strictly Chrome-only; cross-browser testing applies exclusively to the Next.js frontend UI."
        ],
        "deliverables": [
            "Cross-Browser Compatibility Report.",
            "Comparative screenshots across Chromium, Firefox, and WebKit."
        ],
        "acceptance_criteria": [
            "All primary frontend routes render cleanly across Chromium, Firefox, and WebKit.",
            "Zero JavaScript console exceptions thrown in any engine.",
            "Forms, tables, and buttons function identically across all engines."
        ],
        "error_recovery": [
            "If WebKit exhibits CSS flexbox bugs, apply explicit width constraints or Tailwind vendor prefix utilities."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/cross-browser-testing`.",
            "cursor": "Select `@cross-browser-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `cross-browser-testing`.",
            "codex": "Reference `cross-browser-testing` in Codex context.",
            "gemini": "Invoke via `gemini run cross-browser-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt cross-browser-testing`.",
            "windsurf": "Activate `cross-browser-testing` in Windsurf."
        },
        "references": [
            "`frontend/src/app/page.tsx`",
            "`AGENTS.md` - Section 8"
        ]
    },
    {
        "name": "mobile-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Test mobile responsive layouts, touch interactions, drawer navigation, and mobile viewports.",
        "purpose": "Verifies that web applications are intuitive, usable, and performant when operated on mobile devices (e.g. iPhone, Android smartphones) using touch controls.",
        "when_to_use": [
            "Validating responsive UI updates on mobile viewports (375px - 430px).",
            "Testing mobile navigation drawers, touch modals, and scroll containers."
        ],
        "when_not_to_use": [
            "Backend server testing."
        ],
        "required_inputs": [
            "Frontend application running locally on port 3000.",
            "Mobile device emulation viewports."
        ],
        "prerequisites": [
            "Playwright mobile device emulation profiles."
        ],
        "procedure": [
            ("Mobile Viewport Emulation", "Launch Playwright with mobile device profile (e.g. iPhone 14: 390x844, DPR 3.0, mobile touch enabled)."),
            ("Navigation Drawer Interaction", "Open and close mobile navigation drawer (`<Navbar />`). Verify smooth animation, focus trap, and escape key closure."),
            ("Table & Data Grid Touch Scroll", "Verify data tables scroll smoothly horizontally without hijacking vertical page scrolling."),
            ("Touch Target Size Verification", "Inspect buttons, icons, and table action controls. Verify hit targets meet minimum 44x44px touch guidelines."),
            ("Mobile Form Usability", "Test form entry on mobile viewport. Confirm on-screen keyboards do not break layout or obscure submit buttons."),
            ("Mobile Evidence Archival", "Capture mobile screenshots of all primary routes and save to `docs/`.")
        ],
        "safety": [
            "Never allow horizontal body scroll on mobile screens.",
            "Ensure font sizes on mobile inputs are $\\ge 16$px to prevent iOS auto-zoom."
        ],
        "deliverables": [
            "Mobile Usability & Responsiveness Report.",
            "Mobile viewport screenshot artifacts in `docs/`."
        ],
        "acceptance_criteria": [
            "Zero horizontal overflow on 375px and 390px mobile screens.",
            "Mobile drawer navigation operates cleanly with touch and keyboard.",
            "All interactive buttons satisfy 44x44px hit targets."
        ],
        "error_recovery": [
            "If mobile viewports trigger horizontal scroll, locate fixed-width elements and apply `max-w-full overflow-hidden`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/mobile-testing`.",
            "cursor": "Select `@mobile-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `mobile-testing`.",
            "codex": "Reference `mobile-testing` in Codex context.",
            "gemini": "Invoke via `gemini run mobile-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt mobile-testing`.",
            "windsurf": "Activate `mobile-testing` in Windsurf."
        },
        "references": [
            "`frontend/src/components/Navbar.tsx`",
            "`frontend/src/app/page.tsx`"
        ]
    },
    {
        "name": "accessibility-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Execute automated axe-core accessibility checks and verify manual keyboard traversal across all interactive views.",
        "purpose": "Verifies that the application adheres to WCAG 2.1 AA criteria, verifying that assistive technology and keyboard-only operators can navigate and use all system features.",
        "when_to_use": [
            "Quality gates for new UI pages, modals, tables, or form controls.",
            "Pre-release accessibility compliance sign-off."
        ],
        "when_not_to_use": [
            "Backend server testing."
        ],
        "required_inputs": [
            "Frontend application running locally on port 3000.",
            "Axe-core automated testing engine."
        ],
        "prerequisites": [
            "Next.js frontend reachable on port 3000."
        ],
        "procedure": [
            ("Automated Axe-Core Test Pass", "Run automated axe-core accessibility scan against all active routes. Collect violation counts by impact (Critical, Serious, Moderate, Minor)."),
            ("Keyboard Tab Order Traversal", "Tab through every interactive element on each page. Confirm focus moves in logical reading order without jumping."),
            ("Focus Visibility Audit", "Confirm every focused element displays a prominent, high-contrast focus ring (`focus-visible:ring-2`)."),
            ("Modal Dialog Focus Trapping", "Open modals. Confirm focus is trapped within modal and returns to triggering button upon closure with Escape."),
            ("Form Label Association Check", "Verify that every `<input>`, `<select>`, and `<textarea>` has an associated `<label>` with matching ID."),
            ("Accessibility Report Synthesis", "Document scan results and confirm 0 critical/serious violations.")
        ],
        "safety": [
            "Never bypass accessibility failures to meet delivery deadlines.",
            "Ensure color contrast is tested under both Light and Dark themes."
        ],
        "deliverables": [
            "Automated Accessibility Scan Results.",
            "Keyboard Navigation Audit Checklist."
        ],
        "acceptance_criteria": [
            "Zero Critical or Serious violations reported by axe-core.",
            "100% of interactive controls are operable via keyboard alone.",
            "Visible focus indicators present on all focused elements."
        ],
        "error_recovery": [
            "If an element lacks accessible naming, add `aria-label` or visible `<label>` text."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/accessibility-testing`.",
            "cursor": "Select `@accessibility-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `accessibility-testing`.",
            "codex": "Reference `accessibility-testing` in Codex context.",
            "gemini": "Invoke via `gemini run accessibility-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt accessibility-testing`.",
            "windsurf": "Activate `accessibility-testing` in Windsurf."
        },
        "references": [
            "`.agents/skills/theme-system/SKILL.md`",
            "`frontend/src/components/Navbar.tsx`"
        ]
    },
    {
        "name": "performance-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Benchmark endpoint response latency, scraper cycle duration, and batch queue throughput against SLAs.",
        "purpose": "Measures system response times, database query execution durations, and scraper throughput under controlled benchmark conditions, proving SLA compliance.",
        "when_to_use": [
            "Pre-release performance validation.",
            "Benchmarking scraper execution durations across Florida and Texas court portals.",
            "Evaluating API throughput under concurrent request loads."
        ],
        "when_not_to_use": [
            "Testing functional correctness on single unit tests."
        ],
        "required_inputs": [
            "Benchmarking test harness (`scripts/inspect_timing.py`), target endpoints, and performance SLA thresholds."
        ],
        "prerequisites": [
            "Running backend stack with populated test dataset."
        ],
        "procedure": [
            ("API Latency Benchmarking", "Execute 100 consecutive requests to core API endpoints (`/api/v1/claims`, `/api/v1/claims/stats`). Record p50, p95, and p99 latency."),
            ("Scraper Cycle Duration Benchmarking", "Execute automated scraper benchmark across 8 portals using `inspect_timing.py`. Record duration per portal and per party."),
            ("Database Query Execution Time", "Inspect database execution logs. Identify queries exceeding 100ms threshold."),
            ("Fuzzy Matching Cascade Throughput", "Benchmark RapidFuzz matching engine against 1,000 cases. Confirm throughput exceeds 10,000 evaluations/second."),
            ("Performance Report Synthesis", "Publish benchmark findings comparing observed metrics against target SLAs.")
        ],
        "safety": [
            "Do NOT run performance stress tests against live external court portals (respect court server rate limits).",
            "Ensure benchmarks run on isolated test databases to avoid corrupting active operational records."
        ],
        "deliverables": [
            "System Performance Benchmark Report with p50, p95, p99 latency figures.",
            "Scraper timing telemetry summary in `docs/`."
        ],
        "acceptance_criteria": [
            "Core API endpoints respond within p95 < 200ms.",
            "Fuzzy matching cascade evaluates 1,000 cases in < 1 second.",
            "Observed performance satisfies all client SLA targets."
        ],
        "error_recovery": [
            "If endpoints fail latency targets, invoke `performance-optimization` to profile slow database queries."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/performance-testing`.",
            "cursor": "Select `@performance-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `performance-testing`.",
            "codex": "Reference `performance-testing` in Codex context.",
            "gemini": "Invoke via `gemini run performance-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt performance-testing`.",
            "windsurf": "Activate `performance-testing` in Windsurf."
        },
        "references": [
            "`backend/app/scripts/inspect_timing.py`",
            "`backend/app/services/fuzzy_engine.py`"
        ]
    },
    {
        "name": "load-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Simulate concurrent Celery worker loads, high-volume claim uploads, and database connection pool contention.",
        "purpose": "Tests system stability, worker queue processing, and database connection pooling under sustained concurrent load, identifying breaking points and deadlocks.",
        "when_to_use": [
            "Validating system capacity for high-volume batch claim processing (e.g. 500+ claims/day).",
            "Testing Celery worker auto-scaling and Redis queue saturation."
        ],
        "when_not_to_use": [
            "Local unit testing."
        ],
        "required_inputs": [
            "Load testing scripts, simulated batch spreadsheets (`ProdRecords8Bots.xlsx`), and Redis connection."
        ],
        "prerequisites": [
            "Local or staging environment with Redis and multi-worker Celery configuration."
        ],
        "procedure": [
            ("Batch Load Generation", "Queue a batch of 50 simulated claims simultaneously using `scripts/run_100_claim_captcha_test.py`."),
            ("Worker Concurrency & Queue Depth Monitoring", "Monitor Celery worker concurrency, prefetch buffers, and Redis queue depth (`scripts/check_celery_workers.py`)."),
            ("Database Connection Pool Monitoring", "Monitor active and overflow database connections in SQLAlchemy pool during concurrent execution."),
            ("Error & Timeout Rate Tracking", "Track failure rates, database lock timeouts (`OperationalError: database is locked`), and retry triggers."),
            ("Throughput & Recovery Audit", "Verify queue drains to 0 cleanly and workers return to idle state without memory leaks."),
            ("Load Testing Summary", "Document maximum sustainable concurrency and bottleneck thresholds.")
        ],
        "safety": [
            "Never execute load tests against external third-party production APIs (Guidewire, court clerks).",
            "Monitor CPU and memory to prevent complete host system freeze."
        ],
        "deliverables": [
            "Load & Concurrency Test Report.",
            "Queue throughput curves and connection pool metrics."
        ],
        "acceptance_criteria": [
            "System processes concurrent batch without database corruption or unhandled crashes.",
            "Queue drains completely with all claims reaching valid terminal states.",
            "Connection pool recovers cleanly without orphan connections."
        ],
        "error_recovery": [
            "If SQLite database locks occur under high concurrency, recommend migration to PostgreSQL via `sync_sqlite_to_postgres.py`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/load-testing`.",
            "cursor": "Select `@load-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `load-testing`.",
            "codex": "Reference `load-testing` in Codex context.",
            "gemini": "Invoke via `gemini run load-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt load-testing`.",
            "windsurf": "Activate `load-testing` in Windsurf."
        },
        "references": [
            "`scripts/run_100_claim_captcha_test.py`",
            "`scripts/check_celery_workers.py`"
        ]
    },
    {
        "name": "security-testing",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Test authentication boundaries, SQL injection resistance, secret leakage prevention, and CORS policies.",
        "purpose": "Executes active and passive security tests probing API endpoints for injection vulnerabilities, unauthorized access, broken object-level authorization, and secret leakage.",
        "when_to_use": [
            "Pre-release security validation.",
            "Adding file upload or user parameter parsing endpoints.",
            "Testing authentication and authorization controls."
        ],
        "when_not_to_use": [
            "Internal non-networked unit tests."
        ],
        "required_inputs": [
            "Security testing payloads (SQL injection strings, XSS scripts, path traversal strings)."
        ],
        "prerequisites": [
            "FastAPI application running in test mode."
        ],
        "procedure": [
            ("SQL Injection Probing", "Inject SQL metacharacters (`' OR '1'='1`, `'; DROP TABLE;--`) into API search query parameters. Confirm ORM parameterized queries neutralize all attacks."),
            ("Path Traversal & File Upload Probing", "Upload files with malicious filenames (`../../etc/passwd`, `test.exe`). Confirm server sanitizes filenames and restricts upload directories."),
            ("Cross-Site Scripting (XSS) Probing", "Inject HTML/JavaScript payloads (`<script>alert(1)</script>`) into claim names and case styles. Confirm React properly escapes strings on rendering."),
            ("Broken Object-Level Authorization (BOLA)", "Attempt to access, update, or delete claim records using non-owner credentials. Confirm 403 Forbidden is enforced."),
            ("Secret Redaction Verification", "Trigger application errors deliberately. Verify stack traces and response bodies redact database passwords and API tokens."),
            ("Security Test Summary", "Publish findings in a formal Security Verification Report.")
        ],
        "safety": [
            "Never execute security tests against systems you do not own or have explicit authorization to test.",
            "Use benign test payloads that do not damage database integrity."
        ],
        "deliverables": [
            "Automated Security Test Suite.",
            "Security Verification Report confirming zero exploitable vulnerabilities."
        ],
        "acceptance_criteria": [
            "Zero SQL injection, XSS, or path traversal vulnerabilities detected.",
            "Unauthorized requests are consistently rejected.",
            "Zero secrets or sensitive credentials leak into responses or logs."
        ],
        "error_recovery": [
            "If any injection or authorization vulnerability is discovered, halt release immediately and patch the boundary."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/security-testing`.",
            "cursor": "Select `@security-testing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `security-testing`.",
            "codex": "Reference `security-testing` in Codex context.",
            "gemini": "Invoke via `gemini run security-testing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt security-testing`.",
            "windsurf": "Activate `security-testing` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8",
            "`backend/app/core/config.py`"
        ]
    },
    {
        "name": "bug-hunting",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Proactively explore edge cases, invalid inputs, network disconnects, race conditions, and unhandled exceptions.",
        "purpose": "Conducts exploratory, adversarial testing to discover hidden defects, race conditions, and edge-case crashes before they impact production operators.",
        "when_to_use": [
            "Following completion of a major feature implementation.",
            "Testing scrapers against erratic court portal DOM variations.",
            "Testing batch queue processing under unexpected network disconnects."
        ],
        "when_not_to_use": [
            "Routine regression test execution."
        ],
        "required_inputs": [
            "Target application modules, edge-case test data, and fault injection capabilities."
        ],
        "prerequisites": [
            "Fully functioning local environment."
        ],
        "procedure": [
            ("Edge-Case Data Generation", "Generate unusual test inputs: empty strings, extreme Unicode strings (emojis, accents), massive strings (10,000 chars), negative numbers, and leap year dates."),
            ("Fault & Latency Injection", "Simulate network timeouts, slow portal responses, and intermittent Redis disconnects during active scraping."),
            ("Race Condition Probing", "Trigger concurrent duplicate clicks on UI buttons (e.g. clicking 'Start' twice rapidly). Verify idempotency."),
            ("State Desynchronization Probing", "Interrupt Celery worker tasks mid-execution (kill process). Verify auto-recovery reconciles orphan claims upon restart."),
            ("Defect Logging & Reproduction", "For every discovered bug, capture stack trace, steps to reproduce, and author an automated reproduction test in `tests/`.")
        ],
        "safety": [
            "Isolate bug-hunting activities to dedicated test databases.",
            "Do not exhaust host operating system resources."
        ],
        "deliverables": [
            "Exploratory Bug-Hunting Findings Log.",
            "Automated Reproduction Test Cases for discovered defects."
        ],
        "acceptance_criteria": [
            "Edge cases and fault injection scenarios are explored systematically.",
            "All discovered defects are documented with reliable reproduction scripts.",
            "Critical state-corruption or unhandled crash bugs are logged for immediate remediation."
        ],
        "error_recovery": [
            "If a defect leaves the database in a corrupted state, run `scripts/clean_all_data.py` to restore clean state."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/bug-hunting`.",
            "cursor": "Select `@bug-hunting` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `bug-hunting`.",
            "codex": "Reference `bug-hunting` in Codex context.",
            "gemini": "Invoke via `gemini run bug-hunting`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt bug-hunting`.",
            "windsurf": "Activate `bug-hunting` in Windsurf."
        },
        "references": [
            "`backend/tests/test_worker_restart_auto_recovery.py`",
            "`scripts/clean_all_data.py`"
        ]
    },
    {
        "name": "test-coverage-analysis",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Find untested critical business paths, state transitions, and exception handlers; optimize for risk coverage, not mere percentage.",
        "purpose": "Analyzes test execution coverage across critical business modules (fuzzy engine, state machine, Guidewire serializer), identifying blind spots where defects could escape to production.",
        "when_to_use": [
            "Pre-release quality audits.",
            "Auditing legacy modules before refactoring.",
            "Evaluating test suite thoroughness after major feature additions."
        ],
        "when_not_to_use": [
            "Chasing 100% code coverage on trivial boilerplate or auto-generated code."
        ],
        "required_inputs": [
            "`pytest-cov` coverage reports and repository source files."
        ],
        "prerequisites": [
            "`pytest-cov` installed in `backend/.venv`."
        ],
        "procedure": [
            ("Coverage Instrumentation Execution", "Execute backend test suite with coverage: `pytest --cov=app --cov-report=term-missing`."),
            ("Critical Path Coverage Audit", "Inspect coverage specifically on high-risk modules: `fuzzy_engine.py`, `guidewire_client.py`, `queue_runner.py`, and `base.py`."),
            ("Branch & Exception Blind Spot Discovery", "Identify unexecuted exception handlers (e.g. `CaptchaResolutionError`), fallback cascades, and retry branches."),
            ("Targeted Test Authoring", "Write focused unit tests covering the discovered untested branches and edge cases."),
            ("Re-run & Verification", "Re-run coverage instrumentation. Confirm critical business modules achieve $\\ge 90\\%$ branch coverage."),
            ("Coverage Report Synthesis", "Publish the Test Coverage Audit Report in `docs/`.")
        ],
        "safety": [
            "Do NOT write meaningless assertion-free tests merely to inflate coverage percentages.",
            "Focus coverage efforts on high-risk business logic and data persistence."
        ],
        "deliverables": [
            "Test Coverage & Risk Gap Analysis Report.",
            "New targeted unit test cases covering previously untested branches."
        ],
        "acceptance_criteria": [
            "Core business services (`fuzzy_engine`, `guidewire_client`) maintain $\\ge 90\\%$ branch coverage.",
            "All primary exception handling branches are verified by tests.",
            "Total test pass rate remains 100%."
        ],
        "error_recovery": [
            "If certain code branches cannot be triggered in unit tests, refactor to dependency-inject the error condition."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/test-coverage-analysis`.",
            "cursor": "Select `@test-coverage-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `test-coverage-analysis`.",
            "codex": "Reference `test-coverage-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run test-coverage-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt test-coverage-analysis`.",
            "windsurf": "Activate `test-coverage-analysis` in Windsurf."
        },
        "references": [
            "`backend/tests/`",
            "`AGENTS.md` - Section 7"
        ]
    },
    {
        "name": "full-application-validation",
        "category_code": "E",
        "category_name": "Testing & Quality Assurance",
        "description": "Run a risk-based end-to-end acceptance pass across all 8 frontend screens and 8 backend court portal scrapers.",
        "purpose": "Conducts a comprehensive, holistic platform validation pass proving that all 8 frontend screens, 8 court portal bots, Guidewire integration, and export engines operate in complete harmony with documented evidence.",
        "when_to_use": [
            "Final acceptance testing prior to client delivery or release tagging.",
            "Major milestone verification passes."
        ],
        "when_not_to_use": [
            "Incremental micro-task development."
        ],
        "required_inputs": [
            "Running full-stack platform, test spreadsheet (`ProdRecords8Bots.xlsx`), and verification recording harness."
        ],
        "prerequisites": [
            "Local dev stack running via `setup_local.ps1`."
        ],
        "procedure": [
            ("System Health & Ping Verification", "Navigate to `/health`. Verify all 8 platform components and 8 portal ping checks return healthy status."),
            ("8-Portal Scraper Execution Pass", "Trigger claim runs exercising all 8 court bots: Broward, Hillsborough, Miami, Dallas, Travis, Harris JP, Harris District, Harris Clerk."),
            ("Dual-Theme Screen Verification", "Walk through all 8 frontend routes (`/`, `/claims/:id`, `/upload`, `/monitor`, `/health`, `/exceptions`, `/settings`, `/branding`) in both Light and Dark themes."),
            ("Fuzzy Matching & Review Verification", "Verify fuzzy matches cascade correctly (Claimant -> Insured -> Driver) and populate `/exceptions` for human review."),
            ("Guidewire Cloud Integration", "Confirm matched claims format correctly with 9-digit '0' prefix and deliver to Guidewire API."),
            ("Bulk Export Verification", "Export claims to multi-sheet Excel, CSV summary, and telemetry packages. Verify column schema accuracy."),
            ("Full Validation Report & Evidence Archival", "Publish the Full Application Validation Report in `docs/` accompanied by video recordings and screenshots.")
        ],
        "safety": [
            "CRITICAL: Never declare full application validation complete without actual test logs and visual evidence.",
            "Ensure all temporary test artifacts and exports are cleanly archived in `exports/`."
        ],
        "deliverables": [
            "Master Full-Application Validation Report in `docs/`.",
            "Complete evidentiary package (screenshots, recordings, test logs)."
        ],
        "acceptance_criteria": [
            "All 8 court portal scrapers extract valid cases matching schemas.",
            "All 8 frontend routes render without errors in Light and Dark themes.",
            "Guidewire integration and multi-format exports function with 100% success rate."
        ],
        "error_recovery": [
            "If any single portal or screen fails during the full pass, isolate the failure, patch the root cause, and re-run."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/full-application-validation`.",
            "cursor": "Select `@full-application-validation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `full-application-validation`.",
            "codex": "Reference `full-application-validation` in Codex context.",
            "gemini": "Invoke via `gemini run full-application-validation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt full-application-validation`.",
            "windsurf": "Activate `full-application-validation` in Windsurf."
        },
        "references": [
            "`docs/WALKTHROUGH.md`",
            "`docs/CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md`"
        ]
    }
]

