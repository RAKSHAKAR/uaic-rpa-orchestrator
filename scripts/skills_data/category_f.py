"""
Category F: Debugging & Problem Resolution
Contains 13 comprehensive skills for root-cause diagnosis, application debugging,
fixing build/runtime/console/terminal/database/UI errors, and automated bug fixing.
"""

SKILLS_F = [
    {
        "name": "diagnose-issue",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Collect symptoms, logs, stack traces, and environment state before touching or changing any code.",
        "purpose": "Enforces a disciplined diagnostic phase prior to bug fixing, preventing guesswork and avoiding superficial patches that mask underlying systemic defects.",
        "when_to_use": [
            "Responding to any bug report, unexpected test failure, or system error.",
            "Diagnosing mysterious scraper timeouts or portal navigation failures."
        ],
        "when_not_to_use": [
            "Implementing pre-diagnosed and approved changes."
        ],
        "required_inputs": [
            "Error messages, stack traces, terminal output, reproduction steps, or user symptom descriptions."
        ],
        "prerequisites": [
            "Read-only access to application logs (`logs/`, `AuditLog`) and error screenshots (`backend/screenshots/`)."
        ],
        "procedure": [
            ("Symptom & Environment Collection", "Gather exact error strings, HTTP status codes, timestamp, operating system, and active configuration."),
            ("Log & Stack Trace Extraction", "Inspect application logs (`backend/orchestrator.db`, terminal stdout/stderr, browser console). Extract full traceback."),
            ("State & Database Inspection", "Query the database to inspect the exact state of affected records at the moment of failure."),
            ("Error Screenshot & DOM Review", "If a browser automation failure occurred, inspect the corresponding screenshot in `backend/screenshots/` and DOM dump."),
            ("Hypothesis Generation & Evidence Testing", "Formulate candidate hypotheses. Test each hypothesis against concrete evidence to isolate root cause."),
            ("Diagnosis Report Synthesis", "Publish a concise Diagnosis Report detailing proven root cause, affected files, and recommended remediation.")
        ],
        "safety": [
            "CRITICAL: Do NOT edit or modify source code during the diagnosis phase.",
            "Do NOT speculate on root cause without verifiable log or trace evidence."
        ],
        "deliverables": [
            "Root-Cause Diagnosis Report in `docs/` or session artifact.",
            "Extracted stack trace and evidence log."
        ],
        "acceptance_criteria": [
            "Exact root cause is identified with concrete code line references.",
            "Evidence (stack trace, error screenshot, or database dump) corroborates the finding.",
            "Zero source code files modified during diagnosis."
        ],
        "error_recovery": [
            "If logs are insufficient, author an isolated non-destructive probe script in `scripts/` to gather additional telemetry."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/diagnose-issue`.",
            "cursor": "Select `@diagnose-issue` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `diagnose-issue`.",
            "codex": "Reference `diagnose-issue` in Codex context.",
            "gemini": "Invoke via `gemini run diagnose-issue`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt diagnose-issue`.",
            "windsurf": "Activate `diagnose-issue` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Diagnose Before Fixing)",
            "`backend/app/models/error_screenshot.py`"
        ]
    },
    {
        "name": "debug-application",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Trace a defect methodically through frontend React components, FastAPI APIs, and Celery worker runtimes.",
        "purpose": "Traces defect lifecycles across process boundaries, identifying where data contracts break down between frontend UI, backend routers, Celery task payloads, and external APIs.",
        "when_to_use": [
            "Debugging multi-tier bugs where the failure symptom manifests far from the root cause.",
            "Tracing claim state transitions that stall or desynchronize."
        ],
        "when_not_to_use": [
            "Straightforward local compiler or syntax errors."
        ],
        "required_inputs": [
            "Reproduction claim ID or user journey steps.",
            "Access to running services and log streams."
        ],
        "prerequisites": [
            "Local services running in debug mode."
        ],
        "procedure": [
            ("Client-Side State Tracing", "Trace user action from React click handler through `lib/api.ts` Axios call. Inspect outgoing network payload in DevTools."),
            ("API Endpoint Ingestion Tracing", "Inspect incoming FastAPI handler parameters and Pydantic validation parsing in `app/api/v1/endpoints/`."),
            ("Celery Task Dispatch Inspection", "Inspect task argument serialization and message publishing to Redis queue in `app/tasks/queue_runner.py`."),
            ("Worker Execution & Scraper Tracing", "Trace Celery worker task execution, Playwright page lifecycle, and database persistence."),
            ("Response Roundtrip & UI State Mutation", "Inspect backend response serialization and frontend state update (`useState`, React Query)."),
            ("Bug Location Isolation", "Pinpoint exact file, function, and line where execution diverged from expected behavior.")
        ],
        "safety": [
            "Do NOT insert permanent debugging `print()` statements into production code; clean up all debug probes.",
            "Never expose sensitive credentials during debugging."
        ],
        "deliverables": [
            "Execution Trace Map documenting exact divergence point.",
            "Targeted fix recommendation."
        ],
        "acceptance_criteria": [
            "Execution path is traced step-by-step from UI trigger to terminal state.",
            "Exact location and mechanism of data corruption or failure is proven.",
            "Minimal, non-breaking fix proposed."
        ],
        "error_recovery": [
            "If async concurrency obscures debugging, reproduce the failure in an isolated synchronous test script."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/debug-application`.",
            "cursor": "Select `@debug-application` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `debug-application`.",
            "codex": "Reference `debug-application` in Codex context.",
            "gemini": "Invoke via `gemini run debug-application`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt debug-application`.",
            "windsurf": "Activate `debug-application` in Windsurf."
        },
        "references": [
            "`backend/app/tasks/queue_runner.py`",
            "`frontend/src/lib/api.ts`"
        ]
    },
    {
        "name": "fix-build-errors",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Resolve TypeScript compilation failures (tsc), Next.js build errors, and package resolution bugs.",
        "purpose": "Systematically diagnoses and resolves TypeScript type errors, Next.js page generation failures, and bundler resolution issues to restore a clean build baseline.",
        "when_to_use": [
            "`npx tsc --noEmit` fails with type errors.",
            "`npm run build` fails during static page optimization or bundling.",
            "Upgraded frontend packages introduce broken types."
        ],
        "when_not_to_use": [
            "Backend Python exceptions (use `fix-runtime-errors`)."
        ],
        "required_inputs": [
            "`tsc` compiler error output, error file paths, and line numbers."
        ],
        "prerequisites": [
            "Node.js and npm installed in `frontend/`."
        ],
        "procedure": [
            ("Compiler Error Extraction", "Run `npx tsc --noEmit` in `frontend/`. Parse error codes (`TS2322`, `TS2339`), file locations, and offending line numbers."),
            ("Type Discrepancy Diagnosis", "Compare expected type vs actual type. Determine whether interface in `types/index.ts` is outdated or component is passing incorrect props."),
            ("Type Contract Correction", "Update type definitions in `types/index.ts` to reflect valid API contracts, or correct component prop passing."),
            ("SSR & Dynamic Import Resolution", "If build fails on SSR window/document access, wrap browser-only code in `useEffect` or dynamic `ssr: false` import."),
            ("Compiler Re-verification", "Rerun `npx tsc --noEmit`. Verify 0 errors."),
            ("Production Build Pass", "Run `npm run build` to confirm all static and dynamic routes generate cleanly.")
        ],
        "safety": [
            "NEVER use `// @ts-ignore` or `any` type casts merely to bypass compiler checks.",
            "Ensure type fixes preserve backward compatibility with backend API schemas."
        ],
        "deliverables": [
            "Corrected TypeScript source files and interface contracts.",
            "Clean compiler output with 0 errors."
        ],
        "acceptance_criteria": [
            "`cd frontend && npx tsc --noEmit` exits with code 0.",
            "`cd frontend && npm run build` completes successfully.",
            "Zero `@ts-ignore` suppressions introduced."
        ],
        "error_recovery": [
            "If Next.js cache becomes corrupted (`.next/`), purge `.next` directory and rebuild."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-build-errors`.",
            "cursor": "Select `@fix-build-errors` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-build-errors`.",
            "codex": "Reference `fix-build-errors` in Codex context.",
            "gemini": "Invoke via `gemini run fix-build-errors`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-build-errors`.",
            "windsurf": "Activate `fix-build-errors` in Windsurf."
        },
        "references": [
            "`frontend/src/types/index.ts`",
            "`frontend/tsconfig.json`"
        ]
    },
    {
        "name": "fix-runtime-errors",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Resolve Python runtime exceptions, unhandled crashes, async deadlocks, and worker task failures.",
        "purpose": "Diagnoses and fixes runtime exceptions (`AttributeError`, `KeyError`, `ValueError`, `TypeError`) and async task failures in backend services and Celery workers.",
        "when_to_use": [
            "FastAPI returns HTTP 500 Internal Server Error.",
            "Celery tasks crash with unhandled tracebacks.",
            "Scrapers encounter unexpected DOM structure changes."
        ],
        "when_not_to_use": [
            "Frontend-only CSS or visual styling issues."
        ],
        "required_inputs": [
            "Exception traceback, error log, input arguments, and reproduction conditions."
        ],
        "prerequisites": [
            "Backend Python virtual environment."
        ],
        "procedure": [
            ("Traceback Analysis", "Analyze the complete Python traceback. Identify the exact file, function, line, and exception class."),
            ("Input State & Null Safety Check", "Inspect variables at point of failure. Check for `None` values, missing dictionary keys, or mismatched datatypes."),
            ("Defensive Guard & Fallback Implementation", "Implement defensive checks (e.g. `dict.get()`, null checks, try/except blocks) with sensible defaults."),
            ("Reproduction Test Authoring", "Write an automated unit test reproducing the exact input conditions that triggered the crash."),
            ("Regression Verification", "Execute `pytest` across all test suites to confirm the fix works and breaks zero adjacent logic."),
            ("Lint Check", "Run `ruff check app tests` to verify clean code formatting.")
        ],
        "safety": [
            "Never use bare `except:` blocks that swallow keyboard interrupts or system exits.",
            "Ensure fixes preserve core business rules (e.g. 1899-12-30 date conversion, 9-digit ClaimNumber prefix)."
        ],
        "deliverables": [
            "Patched Python source files with robust error handling.",
            "Automated regression test verifying the fix."
        ],
        "acceptance_criteria": [
            "Runtime exception no longer occurs under reproduction inputs.",
            "New regression test passes cleanly.",
            "All 556 backend tests continue passing."
        ],
        "error_recovery": [
            "If an async deadlock occurs in SQLAlchemy, ensure database sessions are cleanly closed with async context managers."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-runtime-errors`.",
            "cursor": "Select `@fix-runtime-errors` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-runtime-errors`.",
            "codex": "Reference `fix-runtime-errors` in Codex context.",
            "gemini": "Invoke via `gemini run fix-runtime-errors`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-runtime-errors`.",
            "windsurf": "Activate `fix-runtime-errors` in Windsurf."
        },
        "references": [
            "`backend/app/main.py`",
            "`backend/app/tasks/scraper_tasks.py`"
        ]
    },
    {
        "name": "fix-console-errors",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Inspect and resolve browser Developer Console errors, unhandled promise rejections, React warnings, and CORS failures.",
        "purpose": "Eliminates browser Developer Console errors and warnings, ensuring seamless client-side execution, zero unhandled promise rejections, and pristine user experience.",
        "when_to_use": [
            "Browser DevTools shows red console errors or unhandled promise rejections.",
            "React emits hydration mismatch warnings or duplicate key warnings.",
            "API calls fail with CORS (Cross-Origin Resource Sharing) errors."
        ],
        "when_not_to_use": [
            "Headless backend CLI tasks."
        ],
        "required_inputs": [
            "Browser console logs, network request details, and affected component JSX."
        ],
        "prerequisites": [
            "Running frontend and backend stack."
        ],
        "procedure": [
            ("Console Log Extraction", "Extract exact console error strings, stack traces, and network failure status codes from browser DevTools."),
            ("React Warning Diagnosis", "Diagnose React warnings: unique `key` prop missing in lists, hydration differences between server/client, or controlled/uncontrolled input switching."),
            ("CORS & Network Resolution", "If API calls fail with CORS errors, verify FastAPI `CORSMiddleware` configuration (`allow_origins`, `allow_credentials`) in `backend/app/main.py`."),
            ("Promise Rejection Handling", "Wrap all asynchronous Axios/Fetch promises in `try/catch` blocks or `.catch()` handlers with user-facing toast alerts."),
            ("Clean Console Verification", "Navigate through the application with browser DevTools open. Confirm 0 console errors and 0 warnings are emitted.")
        ],
        "safety": [
            "Never set `allow_origins=['*']` with `allow_credentials=True` in production CORS configurations.",
            "Do not suppress console errors using monkey-patched `console.error = () => {}`."
        ],
        "deliverables": [
            "Cleaned frontend components and CORS configuration.",
            "DevTools console screenshot demonstrating 0 errors."
        ],
        "acceptance_criteria": [
            "Browser console remains completely clean (0 errors, 0 warnings) across all primary user workflows.",
            "All asynchronous network requests handle failure gracefully.",
            "React hydration completes without SSR mismatch warnings."
        ],
        "error_recovery": [
            "If hydration warnings persist on date formatting, use client-only rendering wrappers or `suppressHydrationWarning`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-console-errors`.",
            "cursor": "Select `@fix-console-errors` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-console-errors`.",
            "codex": "Reference `fix-console-errors` in Codex context.",
            "gemini": "Invoke via `gemini run fix-console-errors`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-console-errors`.",
            "windsurf": "Activate `fix-console-errors` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (No Error Left Behind)",
            "`backend/app/main.py` - CORS Configuration"
        ]
    },
    {
        "name": "fix-terminal-errors",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Resolve command execution failures, process startup crashes, port collisions, and virtual environment path errors.",
        "purpose": "Diagnoses and fixes terminal startup failures, port collisions (e.g. 8000, 3000, 6379), path resolution defects, and PowerShell script syntax errors.",
        "when_to_use": [
            "`setup_local.ps1` or background processes fail to launch.",
            "Port collision errors (`Errno 10048`, `Address already in use`).",
            "Python module not found errors due to virtualenv desynchronization."
        ],
        "when_not_to_use": [
            "Browser UI layout defects."
        ],
        "required_inputs": [
            "Terminal command string, error output, and exit code."
        ],
        "prerequisites": [
            "PowerShell execution privileges."
        ],
        "procedure": [
            ("Process & Port Collision Inspection", "Identify colliding ports (8000, 3000, 6379) using `Get-NetTCPConnection` or `scripts/check_python_procs.ps1`."),
            ("Zombie Process Termination", "Terminate orphan Python, Node, or Celery processes holding the ports using clean process IDs via `scripts/clean_stale_workers.py`."),
            ("Virtualenv Path Validation", "Verify Python interpreter points to `backend\\.venv\\Scripts\\python.exe` and has required modules in `sys.path`."),
            ("PowerShell Syntax Audit", "If a `.ps1` script fails, execute `scripts/check_ps1_syntax.ps1` to detect syntax or parameter parsing errors."),
            ("Clean Startup Rerun", "Re-execute the launcher script (`setup_local.ps1`) and verify all services start persistently and report healthy status.")
        ],
        "safety": [
            "CRITICAL: PowerShell launcher (`setup_local.ps1`) must be persistent, interactive, and NEVER auto-close unexpectedly.",
            "Do not kill external processes unrelated to the project."
        ],
        "deliverables": [
            "Patched PowerShell scripts or launcher configurations.",
            "Clean terminal execution log confirming healthy service startup."
        ],
        "acceptance_criteria": [
            "Services bind to expected ports cleanly without collision.",
            "All `.ps1` scripts pass `check_ps1_syntax.ps1` with 0 errors.",
            "Background processes remain healthy and persistent."
        ],
        "error_recovery": [
            "If ports remain locked by Windows kernel, wait 30 seconds for TIME_WAIT socket cleanup or restart host service."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-terminal-errors`.",
            "cursor": "Select `@fix-terminal-errors` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-terminal-errors`.",
            "codex": "Reference `fix-terminal-errors` in Codex context.",
            "gemini": "Invoke via `gemini run fix-terminal-errors`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-terminal-errors`.",
            "windsurf": "Activate `fix-terminal-errors` in Windsurf."
        },
        "references": [
            "`setup_local.ps1`",
            "`scripts/check_ps1_syntax.ps1`"
        ]
    },
    {
        "name": "fix-api-errors",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Diagnose request, response, schema validation, and HTTP 4xx/5xx failures across REST endpoints.",
        "purpose": "Isolates and resolves REST API contract failures, Pydantic serialization bugs, missing query parameters, and unexpected HTTP status codes.",
        "when_to_use": [
            "API endpoints returning 400 Bad Request, 422 Unprocessable Entity, or 500 Server Error.",
            "Frontend Axios requests failing or receiving malformed payloads."
        ],
        "when_not_to_use": [
            "External third-party API integration timeouts (use `fix-integration-issues`)."
        ],
        "required_inputs": [
            "HTTP request URL, method, headers, request body, response status code, and response JSON."
        ],
        "prerequisites": [
            "Access to FastAPI route definitions in `app/api/v1/endpoints/`."
        ],
        "procedure": [
            ("Request Payload Inspection", "Compare incoming request body against Pydantic schema in `app/schemas/`. Check for missing required fields, type mismatches, or invalid formats."),
            ("Endpoint Handler Debugging", "Inspect route logic in `app/api/v1/endpoints/`. Check database queries, foreign key validations, and error raises."),
            ("Pydantic Serialization Check", "Ensure database model objects are correctly converted to Pydantic response models with `from_attributes=True`."),
            ("Status Code Alignment", "Return explicit HTTP status codes: 200 (Success), 201 (Created), 400 (Bad Request), 404 (Not Found), 409 (Conflict), 422 (Validation Error)."),
            ("Automated Regression Test Pass", "Author a test in `tests/test_api.py` asserting the fix."),
            ("Endpoint Verification", "Verify endpoint returns expected JSON using `AsyncClient`.")
        ],
        "safety": [
            "Never expose internal database error details or SQL statements in API error messages.",
            "Ensure API contract fixes do not break existing frontend consumers."
        ],
        "deliverables": [
            "Patched FastAPI endpoint handler or Pydantic schema.",
            "Automated test case in `backend/tests/test_api.py`."
        ],
        "acceptance_criteria": [
            "Endpoint returns expected 2xx response for valid inputs.",
            "Invalid inputs return structured 4xx responses with clear error messages.",
            "Zero 500 Internal Server Errors emitted."
        ],
        "error_recovery": [
            "If Pydantic fails to serialize datetime fields, ensure UTC ISO-8601 formatting is applied."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-api-errors`.",
            "cursor": "Select `@fix-api-errors` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-api-errors`.",
            "codex": "Reference `fix-api-errors` in Codex context.",
            "gemini": "Invoke via `gemini run fix-api-errors`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-api-errors`.",
            "windsurf": "Activate `fix-api-errors` in Windsurf."
        },
        "references": [
            "`backend/app/api/v1/endpoints/claims.py`",
            "`backend/tests/test_api.py`"
        ]
    },
    {
        "name": "fix-database-errors",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Diagnose database locks, connection pool exhaustion, constraint violations, and schema migration errors.",
        "purpose": "Resolves relational database locks (`database is locked`), duplicate key constraint violations, foreign key cascading errors, and transaction rollbacks.",
        "when_to_use": [
            "SQLite throws `OperationalError: database is locked` during concurrent scraper runs.",
            "IntegrityError raised for duplicate unique keys.",
            "Database migrations fail or leave schema in an inconsistent state."
        ],
        "when_not_to_use": [
            "Frontend UI bugs."
        ],
        "required_inputs": [
            "Database error traceback, failed SQL query, and database connection settings."
        ],
        "prerequisites": [
            "SQLAlchemy connection configuration and database inspection tools."
        ],
        "procedure": [
            ("Lock & Concurrency Analysis", "If encountering SQLite locks, inspect connection pooling in `backend/app/core/database.py`. Configure WAL (Write-Ahead Logging) mode and busy timeouts."),
            ("Constraint Violation Inspection", "If encountering `IntegrityError`, identify which unique or foreign key constraint failed. Check input data uniqueness before inserting."),
            ("Transaction Scope Audit", "Verify that `AsyncSession` transactions are kept as short as possible. Never hold a session open across network or scraper calls."),
            ("Migration Repair", "If schema migration is stuck, inspect migration versions, resolve conflicts, and run migration repair script."),
            ("Database Integrity Verification", "Run `PRAGMA integrity_check;` on SQLite or equivalent PostgreSQL validation to confirm zero corruption."),
            ("Regression Test Pass", "Run `pytest tests/test_database_models.py -q`.")
        ],
        "safety": [
            "CRITICAL: Always backup the database file before running low-level repair or migration commands.",
            "Never disable foreign key constraints to bypass validation errors."
        ],
        "deliverables": [
            "Patched database engine configuration or model constraint logic.",
            "Verified database integrity test log."
        ],
        "acceptance_criteria": [
            "Database operations execute without lock timeouts or connection exhaustion.",
            "Constraint violations are prevented via pre-insert validation.",
            "Database integrity check passes with zero corruption."
        ],
        "error_recovery": [
            "If SQLite database file is locked by a dead process, cleanly terminate the lingering process holding the file handle."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-database-errors`.",
            "cursor": "Select `@fix-database-errors` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-database-errors`.",
            "codex": "Reference `fix-database-errors` in Codex context.",
            "gemini": "Invoke via `gemini run fix-database-errors`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-database-errors`.",
            "windsurf": "Activate `fix-database-errors` in Windsurf."
        },
        "references": [
            "`backend/app/core/database.py`",
            "`backend/tests/test_database_models.py`"
        ]
    },
    {
        "name": "fix-ui-issues",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Resolve layout shifts, z-index bugs, modal backdrop traps, contrast defects, and broken responsive viewports.",
        "purpose": "Diagnoses and patches CSS layout defects, broken flex/grid alignments, missing theme tokens, and modal stacking context bugs across Next.js components.",
        "when_to_use": [
            "UI components clip or overflow unexpectedly on smaller screens.",
            "Modals render behind other elements or block page interactions.",
            "Text is unreadable due to missing dark/light theme token pairing."
        ],
        "when_not_to_use": [
            "Backend API logic."
        ],
        "required_inputs": [
            "Affected component file path, visual defect description, and viewport resolution."
        ],
        "prerequisites": [
            "Tailwind CSS configuration and running frontend application."
        ],
        "procedure": [
            ("DOM & CSS Inspection", "Inspect affected element in browser DevTools. Check computed box-sizing, display mode, padding, margin, and z-index values."),
            ("Theme Token Pairing Check", "Verify background and text color utility classes are paired correctly (`bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100`)."),
            ("Z-Index & Stacking Context Fix", "Assign explicit, standardized z-index levels (`z-10` for dropdowns, `z-50` for modals, `z-60` for toasts). Ensure backdrop overlays have `fixed inset-0`."),
            ("Overflow & Responsive Fix", "Replace rigid pixel widths with responsive utilities (`w-full`, `max-w-none`, `overflow-x-auto`)."),
            ("Dual-Mode Visual Verification", "Inspect fix under both Light Mode and Dark Mode across 375px, 768px, and 1920px viewports."),
            ("TypeScript Compile Pass", "Run `cd frontend && npx tsc --noEmit`.")
        ],
        "safety": [
            "Do NOT use arbitrary high z-indexes (e.g. `z-[999999]`); use established design system elevation scales.",
            "Ensure UI fixes do not introduce horizontal scrollbars."
        ],
        "deliverables": [
            "Patched React component JSX/CSS.",
            "Dual-theme screenshot verifying defect resolution."
        ],
        "acceptance_criteria": [
            "Visual defect is completely resolved across desktop, tablet, and mobile.",
            "Renders cleanly with high contrast in both Light Mode and Dark Mode.",
            "`npx tsc --noEmit` passes with 0 errors."
        ],
        "error_recovery": [
            "If Tailwind classes fail to apply, check for specificity collisions with custom CSS."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-ui-issues`.",
            "cursor": "Select `@fix-ui-issues` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-ui-issues`.",
            "codex": "Reference `fix-ui-issues` in Codex context.",
            "gemini": "Invoke via `gemini run fix-ui-issues`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-ui-issues`.",
            "windsurf": "Activate `fix-ui-issues` in Windsurf."
        },
        "references": [
            "`.agents/skills/theme-system/SKILL.md`",
            "`frontend/src/app/branding/page.tsx`"
        ]
    },
    {
        "name": "fix-integration-issues",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Resolve external service failures, Guidewire API contract mismatches, AntiCaptcha timeouts, and portal DOM changes.",
        "purpose": "Diagnoses and fixes integration failures when communicating with external court websites, CAPTCHA solving services, and Guidewire Insurance Cloud APIs.",
        "when_to_use": [
            "Guidewire rejects case delivery payloads with HTTP 400 or 500.",
            "AntiCaptcha extension times out or fails to resolve a challenge.",
            "Court portal alters table markup or input field locators."
        ],
        "when_not_to_use": [
            "Internal unit test failures."
        ],
        "required_inputs": [
            "Failed integration transaction log, error screenshot, external HTTP response, and target portal key."
        ],
        "prerequisites": [
            "Access to external client code in `app/services/` and scrapers in `app/automation/`."
        ],
        "procedure": [
            ("External Response & Screenshot Analysis", "Inspect external API error payload or scraper error screenshot in `backend/screenshots/`."),
            ("Guidewire Contract Verification", "If Guidewire fails, verify payload structure matches exact contract: `ClaimNumber` (9-digit gets '0' prefix), `ExposureNumber`, `CaseItems` array."),
            ("CAPTCHA & DOM Locator Inspection", "If portal fails, inspect live portal DOM. Verify whether element IDs, search tabs, or CAPTCHA types have mutated."),
            ("Client / Scraper Locator Patch", "Update Playwright CSS selectors or API client serializer to match current external interface."),
            ("Isolated Live Test Execution", "Run targeted live test script in `scripts/` (e.g. `test_broward.py` or `scripts/test_export_download_verify.py`) to confirm fix."),
            ("Regression Verification", "Run full pytest suite to ensure portal output schema remains 100% compliant.")
        ],
        "safety": [
            "Never modify portal output schemas (CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType) when fixing locators.",
            "Do NOT add CaseType to Harris JP or Harris County Clerk scrapers."
        ],
        "deliverables": [
            "Patched scraper locator or API client serializer.",
            "Verification execution log confirming successful live interaction."
        ],
        "acceptance_criteria": [
            "External integration completes successfully without unhandled errors.",
            "Extracted records strictly adhere to portal schema.",
            "All scraper unit and parity tests pass."
        ],
        "error_recovery": [
            "If an external portal is temporarily down, implement exponential backoff retry rather than permanent failure."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fix-integration-issues`.",
            "cursor": "Select `@fix-integration-issues` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fix-integration-issues`.",
            "codex": "Reference `fix-integration-issues` in Codex context.",
            "gemini": "Invoke via `gemini run fix-integration-issues`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fix-integration-issues`.",
            "windsurf": "Activate `fix-integration-issues` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Portal Output Schema) & Section 11 (Guidewire Payload Contract)",
            "`backend/app/services/guidewire_client.py`"
        ]
    },
    {
        "name": "root-cause-analysis",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Identify the underlying systemic cause of defects using the 5-Whys methodology rather than masking symptoms with workarounds.",
        "purpose": "Performs exhaustive root-cause analysis on recurring defects, intermittent race conditions, or architecture breakdowns, establishing permanent structural fixes.",
        "when_to_use": [
            "Investigating recurring defects that reappear after superficial fixes.",
            "Conducting post-incident reviews following a production disruption.",
            "Diagnosing complex multi-worker concurrency bugs."
        ],
        "when_not_to_use": [
            "Trivial one-off syntax typos."
        ],
        "required_inputs": [
            "Incident timeline, error logs, git history, and system telemetry."
        ],
        "prerequisites": [
            "Historical log data covering the incident."
        ],
        "procedure": [
            ("Incident Timeline Reconstruction", "Reconstruct chronological timeline of events leading up to the failure with exact timestamps."),
            ("5-Whys Iterative Analysis", "Apply 5-Whys methodology starting from the observable symptom. Drill down through software layers to the systemic root cause."),
            ("Root Cause vs Contributing Factor Segregation", "Distinguish primary root causes (e.g. unindexed query causing lock timeout) from secondary contributing factors (e.g. high load)."),
            ("Permanent Corrective Action Formulation", "Design structural architectural or procedural fixes that make future occurrences impossible."),
            ("Preventive Test Case Definition", "Define automated regression tests specifically engineered to detect the failure condition."),
            ("RCA Document Publication", "Publish the formal Root Cause Analysis Document in `docs/`.")
        ],
        "safety": [
            "Never blame individual operators; focus on systemic software guards, validation gates, and architecture.",
            "Do NOT accept superficial explanations ('network glitch') without investigating why the system did not recover."
        ],
        "deliverables": [
            "Formal Root Cause Analysis (RCA) Document in `docs/`.",
            "Preventive Action Plan and automated regression test."
        ],
        "acceptance_criteria": [
            "Underlying systemic root cause is proven with concrete evidence.",
            "Corrective actions address the core cause, not merely symptoms.",
            "Automated test case prevents regression."
        ],
        "error_recovery": [
            "If evidence is insufficient to reach the 5th Why, design telemetry logging to capture data if the issue recurs."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/root-cause-analysis`.",
            "cursor": "Select `@root-cause-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `root-cause-analysis`.",
            "codex": "Reference `root-cause-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run root-cause-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt root-cause-analysis`.",
            "windsurf": "Activate `root-cause-analysis` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Do / Must Not Do)",
            "`docs/` - Historical Implementation Records"
        ]
    },
    {
        "name": "error-reproduction",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Create a minimal, reliable, automated reproduction test case before attempting to implement any code fix.",
        "purpose": "Constructs minimal, deterministic reproduction scripts that reliably trigger reported bugs in isolation, providing a concrete verification baseline for fixes.",
        "when_to_use": [
            "Prior to modifying code to fix any reported bug or unexpected failure.",
            "Investigating intermittent or hard-to-reproduce edge cases."
        ],
        "when_not_to_use": [
            "When a deterministic failing test already exists in the test suite."
        ],
        "required_inputs": [
            "Bug report symptoms, input parameters, and environment state."
        ],
        "prerequisites": [
            "Access to pytest testing framework or scratch script runner."
        ],
        "procedure": [
            ("Minimal Input Isolation", "Strip away irrelevant inputs. Determine the minimal subset of data that reproduces the defect."),
            ("Reproduction Script Authoring", "Write a minimal, isolated test in `backend/tests/` or scratch script in `scripts/` (e.g. `scripts/diag_claims.py`)."),
            ("Deterministic Failure Verification", "Execute the reproduction script. Verify it fails with the exact reported error and traceback."),
            ("State Isolation Check", "Ensure the test does not depend on uncommitted local data or transient external conditions."),
            ("Baseline Failure Recording", "Record the failing assertion or exception trace as the benchmark for successful fix verification.")
        ],
        "safety": [
            "Do NOT modify application source code until the reproduction test is written and confirmed failing.",
            "Ensure reproduction scripts run against test databases."
        ],
        "deliverables": [
            "Automated Reproduction Test Case in `backend/tests/`.",
            "Baseline failure execution log."
        ],
        "acceptance_criteria": [
            "Reproduction test fails reliably with 100% determinism under pre-fix code.",
            "Test contains zero extraneous dependencies or bloated setup logic.",
            "Test passes cleanly once the fix is applied."
        ],
        "error_recovery": [
            "If a defect cannot be reproduced locally, check for differences in environment variables, Python versions, or database fixtures."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/error-reproduction`.",
            "cursor": "Select `@error-reproduction` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `error-reproduction`.",
            "codex": "Reference `error-reproduction` in Codex context.",
            "gemini": "Invoke via `gemini run error-reproduction`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt error-reproduction`.",
            "windsurf": "Activate `error-reproduction` in Windsurf."
        },
        "references": [
            "`backend/tests/`",
            "`scripts/`"
        ]
    },
    {
        "name": "automated-bug-fixing",
        "category_code": "F",
        "category_name": "Debugging & Problem Resolution",
        "description": "Implement bounded, surgical bug fixes and execute full regression test suites proving complete resolution.",
        "purpose": "Guides the surgical implementation of bug fixes, ensuring fixes address root causes with minimal blast radius and are verified by both the reproduction test and the full regression suite.",
        "when_to_use": [
            "Implementing a fix following successful diagnosis and reproduction test authoring.",
            "Resolving localized defects across API handlers, services, or UI components."
        ],
        "when_not_to_use": [
            "Attempting to fix bugs before diagnosing root cause or authoring a reproduction test."
        ],
        "required_inputs": [
            "Confirmed root cause, failing reproduction test, and target source files."
        ],
        "prerequisites": [
            "Completed `diagnose-issue` and `error-reproduction`."
        ],
        "procedure": [
            ("Failing Test Baseline Confirmation", "Run the reproduction test to confirm it currently fails: `pytest <repro_test> -q`."),
            ("Surgical Fix Implementation", "Apply minimal, focused code modifications resolving the underlying defect. Avoid unrelated refactoring."),
            ("Reproduction Test Pass Verification", "Rerun the reproduction test. Confirm it now passes cleanly: `pytest <repro_test> -q`."),
            ("Full Regression Test Suite Pass", "Run the entire backend test suite: `pytest -q`. Confirm 556/556 tests pass with 0 regressions."),
            ("Frontend & Linting Pass", "Run `npx tsc --noEmit` and `ruff check app tests`."),
            ("Fix Summary & Verification Documentation", "Document the bug fix, root cause, changed lines, and passing test evidence in `docs/`.")
        ],
        "safety": [
            "Never introduce broad, speculative refactoring in a bug fix task.",
            "Never bypass regression tests before declaring the bug fixed."
        ],
        "deliverables": [
            "Surgically patched source code files.",
            "Passing reproduction test and full regression test log."
        ],
        "acceptance_criteria": [
            "Reproduction test transitions from Red (Failing) to Green (Passing).",
            "Full regression suite passes with 100% success rate.",
            "Zero new linting or type-checking errors introduced."
        ],
        "error_recovery": [
            "If the fix causes regressions in adjacent test suites, revert the fix and re-analyze the blast radius."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/automated-bug-fixing`.",
            "cursor": "Select `@automated-bug-fixing` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `automated-bug-fixing`.",
            "codex": "Reference `automated-bug-fixing` in Codex context.",
            "gemini": "Invoke via `gemini run automated-bug-fixing`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt automated-bug-fixing`.",
            "windsurf": "Activate `automated-bug-fixing` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Definition of Done)",
            "`docs/` - Historical Fix Plans"
        ]
    }
]

