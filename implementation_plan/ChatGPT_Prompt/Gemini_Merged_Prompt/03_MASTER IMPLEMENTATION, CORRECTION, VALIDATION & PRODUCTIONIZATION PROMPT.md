# MASTER IMPLEMENTATION, CORRECTION, VALIDATION & PRODUCTIONIZATION PROMPT
## UAIC Claim & RPA Orchestrator — Complete Existing-System Audit & Finalization

You must now perform a **complete, end-to-end implementation, correction, cleanup, modernization, UI/UX improvement, testing, and production-readiness pass** over the EXISTING UAIC Claim & RPA Orchestrator application.

This instruction supersedes incomplete, truncated, partially implemented, or incorrectly implemented work from previous attempts.

---

# 1. ROLE

Act as a:

- Principal Software Architect
- Senior Full-Stack Engineer
- Senior Python Engineer
- Senior React/Next.js Engineer
- Browser Automation Engineer
- Playwright Engineer
- Power Automate Migration Engineer
- Distributed Systems Engineer
- Celery/Redis Engineer
- Database Architect
- API Architect
- QA Automation Engineer
- DevOps Engineer
- Security Engineer
- Performance Engineer
- UI/UX Engineer

You are working on an **EXISTING application**.

This is NOT greenfield development.

This is NOT a mock/demo implementation.

This is NOT an instruction to replace the application with a simplified version.

---

# 2. ABSOLUTE RULES

## Rule 1 — Enhancement Only

Always work as an enhancement of the existing system.

**DO NOT remove existing functionality merely to simplify implementation.**

Preserve all valid existing:

- frontend functionality
- backend functionality
- APIs
- database behavior
- automation behavior
- queue behavior
- fuzzy matching
- Guidewire integration
- settings
- authentication/configuration
- import/export
- UI functionality

If something is broken, fix it.

If something is incomplete, complete it.

If something is duplicated or obsolete, remove it only after verifying that it is truly unused and that removing it will not affect functionality.

---

## Rule 2 — Inspect Before Changing

Before implementing anything, inspect the actual project.

Audit:

```text
frontend/
backend/
automation/
API routes
database models
services
tasks
Celery configuration
Redis configuration
Playwright configuration
Chrome integration
Anti-Captcha extension integration
settings/configuration
PowerShell scripts
startup scripts
environment configuration
import/export
fuzzy matching
Guidewire integration
all UI routes
all API routes
all scraper files
all tests
```

Do not guess.

Do not create duplicate implementations when an existing implementation already exists.

---

# 3. POWER AUTOMATE V4 IS THE AUTHORITATIVE AUTOMATION BASELINE

A critical correction:

The latest Power Automate implementation that must be analyzed is:

**UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A**

Treat this V4 flow as the **latest authoritative behavioral reference**.

Do NOT use an older V2/V3 flow as the primary reference if V4 is available.

You must deeply inspect V4 and all related subflows/actions.

Build an internal mapping:

```text
Power Automate V4
       ↓
Existing Python implementation
       ↓
Missing behavior
       ↓
Incorrect behavior
       ↓
Required correction
```

Do not claim V4 behavior unless you actually inspected it.

---

# 4. FINAL AUTOMATION GEOGRAPHY — EXACTLY 8 PORTALS

The application must clearly and correctly represent the following automation structure.

## Florida — 3 portals

1. Broward County
2. Hillsborough County
3. Miami-Dade County

## Texas — 5 portals

1. Travis County
2. Dallas County
3. Harris JP
4. Harris County Clerk / CClerk
5. Harris District Clerk

Therefore:

```text
Florida = 3
Texas   = 5
Total   = 8
```

### CRITICAL

**Miami-Dade is Florida.**

It must NEVER be displayed, categorized, routed, or located under Texas.

Do not create confusion by showing:

```text
Texas
 └── Miami
```

This is incorrect.

The UI, backend, automation registry, telemetry, settings, routing, queue, logs and scraper modules must all follow the same geography.

---

# 5. STATE ROUTING

Claims must be automatically routed based on policy/loss-location geography.

Expected behavior:

```text
Policy State == Loss Location State

Florida
    → Broward
    → Hillsborough
    → Miami-Dade

Texas
    → Travis
    → Dallas
    → Harris JP
    → Harris County Clerk
    → Harris District

Other same-state
    → No Florida/Texas scraper

Policy State != Loss Location State
    → All 8 portals
```

Cross-state claims must dispatch all 8 portals concurrently according to the V4 behavior.

Do not hardcode incorrect routing.

Routing must be centralized and reused by:

- queue
- orchestrator
- scraper registry
- UI
- telemetry
- status
- reporting

---

# 6. SCRAPER FILE STRUCTURE

Verify the backend automation structure.

It must contain implementations for all 8 required portals.

Expected conceptual organization:

```text
automation/
    florida/
        broward.py
        hillsborough.py
        miami_dade.py

    texas/
        travis.py
        dallas.py
        harris_jp.py
        harris_clerk.py
        harris_district.py
```

The exact filenames may follow the existing project's conventions, but the functionality must exist.

Do NOT create a Texas scraper for Miami.

Do NOT leave old duplicate Miami implementations in Texas.

Do NOT leave obsolete/unused scraper files that create ambiguity.

Before deleting files, prove they are unused.

---

# 7. CLEANUP OF OBSOLETE CODE

Perform a complete repository cleanup.

Find:

- obsolete Python versions
- old Python source files
- duplicate scraper files
- obsolete JavaScript/TypeScript files
- unused components
- unused API routes
- abandoned implementations
- duplicate configuration
- dead code
- old automation modules
- temporary files
- generated artifacts
- obsolete `.pyc`
- `__pycache__`
- old compiled Python artifacts
- stale build output

If Python 3.14.7 is now the official target, remove obsolete generated artifacts from older Python versions.

For example, files such as:

```text
broward.cpython-313.pyc
```

must not remain as stale runtime artifacts if they are no longer required.

However:

**Do not blindly delete files.**

First verify references/imports/runtime usage.

Then clean the repository safely.

Final repository should contain only the active implementation and required generated/build files.

---

# 8. PYTHON 3.14.7

The backend must officially target:

**Python 3.14.7**

Verify:

```powershell
python --version
python -c "import sys; print(sys.version)"
py --version
python -m pip --version
```

The active virtual environment must use Python 3.14.7.

Do not silently fall back to older Python.

Modernize:

- dependencies
- type hints
- async code where appropriate
- FastAPI
- Pydantic
- SQLAlchemy
- Celery compatibility
- Redis client
- Playwright integration
- HTTP clients
- logging
- configuration
- testing

Do not mass-upgrade dependencies blindly.

Use versions that are actually compatible with Python 3.14.7.

---

# 9. GOOGLE CHROME — MANDATORY

The automation must use the **normal system-installed Google Chrome**.

Do NOT use Playwright's bundled Chromium for the real county automation.

This is especially important because the Anti-Captcha extension must be tested in the same Chrome environment used by the automation.

The actual browser flow must be:

```text
System Google Chrome
        ↓
Anti-Captcha extension
        ↓
County website
        ↓
CAPTCHA interaction
        ↓
Search
        ↓
Extraction
```

Do NOT make the actual automation depend on:

```text
Playwright bundled Chromium
```

Installing Playwright Chromium dependencies must not cause the system to use Chromium for this automation.

If Playwright dependencies are required for package/runtime support, that is acceptable, but the actual county browser automation must explicitly launch the detected system Google Chrome.

Verify the executable path dynamically.

Do not hardcode one user's machine path.

---

# 10. ANTICAPTCHA EXTENSION

The Anti-Captcha extension is located inside the project root.

The current development path may look like:

```text
C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\anticaptcha-plugin_v0.83
```

BUT THIS PATH MUST NOT BE HARDCODED.

The root folder may change.

Resolve the project root dynamically and locate:

```text
<PROJECT_ROOT>/anticaptcha-plugin_v0.83
```

The implementation must work if the project is moved to another directory.

Validate:

- extension exists
- extension files are complete
- extension can be loaded by system Chrome
- configured Anti-Captcha key is retrieved from the application's Settings/configuration
- no API key is hardcoded
- browser starts with the extension
- extension is actually available to the running Chrome instance

---

# 11. CAPTCHA BEHAVIOR

Follow the actual V4 behavior.

Where CAPTCHA is required:

1. Open the county portal.
2. Fill required search fields.
3. Click the CAPTCHA checkbox/control.
4. Allow Anti-Captcha extension to solve it.
5. Wait for actual verification.
6. Continue only after successful verification.
7. If CAPTCHA does not solve within the configured timeout:
   - refresh/restart the search flow
   - retry according to configured retry policy
8. Never pretend CAPTCHA succeeded merely because a timeout elapsed.

CAPTCHA timeout and retries must come from Settings.

Do not hardcode secrets or operational values.

---

# 12. SETTINGS PAGE IS THE CENTRAL CONFIGURATION SOURCE

The complete system must be aligned with:

```text
http://localhost:3000/settings
```

The Settings page must be the source of truth for configurable behavior.

Review all existing settings and make sure they are actually consumed by the backend.

Configuration should cover where applicable:

- Chrome executable
- Anti-Captcha API key
- CAPTCHA timeout
- CAPTCHA retry count
- browser timeout
- navigation timeout
- search timeout
- retry interval
- queue settings
- concurrency
- worker settings
- automation mode
- attended/unattended mode
- Guidewire configuration
- fuzzy-match configuration
- API endpoints
- database configuration
- Redis configuration
- notification settings

Do not create one setting in the UI and hardcode a different value in Python.

There must be one consistent configuration flow:

```text
Settings UI
    ↓
Persistent configuration
    ↓
Backend configuration service
    ↓
Automation / Queue / API
```

---

# 13. INPUT FILE COLUMNS

The uploaded claim file contains these columns:

```text
Primary Key
Insured First Name
Insured Last Name
DOL
Driver First Name (Insured Vehicle)
Driver Last Name (Insured Vehicle)
Policy State
Claim Number
Loss Location State
Exposure Number
Claimant First Name
Claimant Last Name
```

The system must preserve all of them.

The Create/Edit claim form must NOT display only a subset.

The form must support all required imported fields.

Verify:

```text
Excel/CSV
   ↓
Parser
   ↓
Validation
   ↓
Database
   ↓
Create/Edit Form
   ↓
Queue
   ↓
Automation
```

No imported field may silently disappear.

---

# 14. CLAIM CRUD

Claim management must support:

- Create
- Read
- Update
- Delete
- View details
- Search
- Filter
- Sort
- Pagination
- Bulk selection
- Bulk delete
- Bulk status change
- Retry/reprocess
- Export

Forms must be fully responsive.

Validation must be consistent between frontend and backend.

---

# 15. CLAIM DETAIL PAGE

The page:

```text
/claims/[claim-id]
```

must work reliably.

Fix cases where:

```text
GET /api/v1/claims/<id>
```

returns `404` for a claim that should exist.

Do not hide the problem with frontend fallback/mock data.

Trace:

```text
Frontend route
   ↓
API request
   ↓
FastAPI route
   ↓
Service
   ↓
Database query
```

Fix the real cause.

Also verify that invalid IDs correctly return 404.

---

# 16. CELERY WORKER

The Celery worker must not merely start successfully.

It must actually process tasks.

Verify all required tasks:

```text
orchestrate_court_scrapers_task
evaluate_fuzzy_matches_task
notify_guidewire_task
parse_and_ingest_file_task
advance_auto_queue_task
retrigger_failed_cases_task
```

Verify queues:

```text
default
ingest
scrapers
matcher
notifications
```

Test:

```text
Task submitted
   ↓
Redis
   ↓
Celery worker
   ↓
Task received
   ↓
Task executes
   ↓
Database updated
   ↓
Next task
```

---

# 17. CELERY INSPECTOR WARNINGS

Investigate warnings such as:

```text
Inspect method registered failed
Inspect method scheduled failed
Inspect method conf failed
Inspect method revoked failed
Inspect method active failed
Inspect method reserved failed
Inspect method stats failed
Inspect method active_queues failed
```

Do not simply ignore them.

Determine whether they are:

- Flower configuration issues
- worker event issues
- Celery version compatibility issues
- Windows process limitations
- broker connectivity issues
- worker configuration issues
- inspection timeout issues

Then fix or correctly configure the monitoring stack.

If an inspection limitation is inherent to the selected Windows execution model, document it and provide a reliable alternative monitoring mechanism.

The system must still provide accurate operational status through the application's own backend APIs.

---

# 18. CELERY BEAT

Celery Beat must be verified end-to-end.

It must:

1. Start.
2. Load the schedule.
3. Connect to Redis.
4. Emit due tasks.
5. Worker receives them.
6. Task executes.
7. Result/status is persisted.

The following must actually work:

```text
advance-auto-queue-periodic
```

Do not consider:

```text
beat: Starting...
```

as proof of success.

Test the complete chain.

---

# 19. AUTOMATIC QUEUE PROCESSING

The previous logs showed:

```text
Automatic queue runner is OFF.
Halting sequential queue advancement.
```

This is not acceptable if automatic processing is expected to be enabled.

Verify the Settings/UI configuration.

If Auto Queue is ON:

```text
Queue Item 1
   ↓
Process
   ↓
Complete
   ↓
Queue Item 2
   ↓
Process
   ↓
Complete
   ↓
Queue Item 3
```

must happen automatically.

There must also be a manual option to:

- Start
- Pause
- Resume
- Retry
- Cancel
- Process individual queue item

Do not start all queue items simultaneously unless V4 explicitly requires it.

Sequential queue behavior must be preserved.

---

# 20. ATTENDED MODE

If attended mode is enabled, the user must actually see the browser automation occurring.

Verify:

```text
Attended = ON
      ↓
System Chrome launches
      ↓
Anti-Captcha extension available
      ↓
County portal opens
      ↓
Search executes
      ↓
CAPTCHA handled
      ↓
Results extracted
```

Do not report the automation as running when no browser is launched and no actual automation occurs.

Provide clear UI status:

```text
Starting Chrome
Launching Broward
Waiting for CAPTCHA
Searching
Extracting results
Completed
```

---

# 21. BROWSER LIFECYCLE

Do not launch eight separate Chrome instances unnecessarily.

Follow the intended automation architecture.

For a Florida claim:

```text
One Chrome session
    ├── Broward
    ├── Hillsborough
    └── Miami-Dade
```

For a Texas claim:

```text
One Chrome session
    ├── Travis
    ├── Dallas
    ├── Harris JP
    ├── Harris Clerk
    └── Harris District
```

For a cross-state claim:

```text
All 8 portals
```

Keep the browser/session available for the required operations and close it cleanly afterward.

---

# 22. EIGHT SCRAPERS MUST BE FUNCTIONAL

Every portal scraper must be implemented and tested against its actual behavior.

Do not stop after implementing Florida.

Verify:

### Florida

- Broward
- Hillsborough
- Miami-Dade

### Texas

- Travis
- Dallas
- Harris JP
- Harris County Clerk
- Harris District

Each scraper must support:

- navigation
- correct search fields
- DOL handling where applicable
- CAPTCHA where applicable
- result detection
- extraction
- pagination where required
- case detail navigation where required
- error handling
- retry handling
- database persistence

---

# 23. SCRAPED DATA MODEL

Preserve the fields actually produced by V4.

Where applicable:

```text
Case Number
Case Style
Filing Date
Case Status
Case Type
```

Do not invent fields.

Do not silently discard fields.

For portals where V4 does not provide Case Type, preserve that behavior rather than fabricating data.

---

# 24. FUZZY MATCHING

Verify that the fuzzy matching implementation follows V4.

Audit:

- claimant name
- insured name
- driver name
- Case Style
- threshold
- date filtering
- Case Status filtering
- Case Type filtering
- retry behavior
- result handling

Do not accidentally retain known bugs such as an always-true condition equivalent to:

```text
contains(actualCaseType, "")
```

unless V4 explicitly requires it.

Do not use loose substring matching when exact/normalized status matching is required.

Avoid shared mutable arrays with uncontrolled concurrent writes.

Results must be deterministic.

---

# 25. GUIDEWIRE INTEGRATION

Guidewire is a critical downstream dependency.

Maintain the existing expected payload contract.

The flow must be:

```text
Scraped Data
   ↓
Fuzzy Match
   ↓
Positive Match
   ↓
Guidewire Payload Mapper
   ↓
Guidewire API
   ↓
Activity ID
   ↓
Database
```

Do not use the UI model as the Guidewire payload model.

Verify:

- ClaimNumber
- ExposureNumber
- CaseItems
- CaseNumber
- CaseStyle
- CountyWebsite
- SuitFiledDate
- ActivityID
- final payload storage
- final status

Any existing Claim Number formatting rule must remain unchanged unless V4 explicitly changes it.

Never expose credentials/secrets in frontend code or logs.

---

# 26. SCRAPED PUBLIC COURT CASES UI

Redesign:

**Scraped Public Court Cases (12)**

The current minimal card presentation is not acceptable.

Do not show only:

```text
Case
County
Portal Link
Case Style
```

Instead, use an enterprise-grade grouped table.

Group by:

```text
Portal Link / County Portal
```

Example:

```text
Broward County Clerk — Florida
Portal: [Open Portal]

Cases Found: 4

| Case Number | Case Style | Filing Date | Case Status | Case Type |
|-------------|------------|-------------|-------------|-----------|
```

All relevant V4 fields must be displayed.

---

# 27. SCRAPED CASE TABLE FEATURES

All required table functionality must exist:

- Search
- Filter
- Sorting
- Pagination
- Page size
- Lazy loading/efficient rendering
- Grouping
- Expand/collapse
- Case details
- Raw JSON
- Copy case number
- Open portal
- Match information
- Processing information

Filters should include where applicable:

- County
- State
- Portal
- Case Number
- Case Style
- Filing Date
- Case Status
- Case Type
- Match Status

---

# 28. ALL TABULAR DATA IN THE ENTIRE SOLUTION

This requirement is global.

Every significant table in the application must support, where applicable:

- Sorting
- Filtering
- Pagination
- Search
- Column visibility
- Responsive behavior
- Loading state
- Empty state
- Error state
- Bulk selection/actions where meaningful

This includes:

- Claims
- Queue
- Scraped cases
- Bot execution status
- Telemetry
- logs
- activities
- Guidewire submissions
- imports
- exports
- settings tables
- users/configuration tables
- audit tables

Do not implement these features only on one page.

---

# 29. STATUS MODEL — REMOVE USER CONFUSION

There are currently two statuses that are confusing.

Do not arbitrarily delete backend statuses because they are technically required.

Instead, audit all statuses and clearly distinguish:

### Business/Claim Status

What is happening to the claim overall.

### Automation/Execution Status

What is happening to the current automation run.

If both are required internally, present them clearly in the UI with meaningful labels and context.

Do not display two ambiguous badges both called simply:

```text
Status
```

Use terminology such as:

```text
Claim Status
Automation Status
```

only after verifying the actual semantics.

The backend status values must remain compatible with the existing workflow.

---

# 30. DETAILED STAGE EXECUTION TELEMETRY

Enhance the telemetry section where useful.

It should clearly show:

```text
Stage
Portal
Started
Completed
Duration
Status
Attempt
Records
Error
Screenshot/diagnostic reference where available
```

Useful stages may include:

```text
Queue
Browser Startup
Portal Navigation
CAPTCHA
Search
Result Extraction
Pagination
Database Save
Fuzzy Match
Guidewire Submission
Completion
```

Do not create fake telemetry.

Telemetry must reflect real execution.

---

# 31. COUNTY COURT PORTAL SCRAPER EXECUTION STATUS — 8 BOTS

This section must clearly show all eight bots.

Group them:

### Florida

- Broward
- Hillsborough
- Miami-Dade

### Texas

- Travis
- Dallas
- Harris JP
- Harris Clerk
- Harris District

For each:

- Status
- Started
- Completed
- Duration
- Attempt
- Cases Found
- Match Result
- Error
- Retry
- Open portal/action if appropriate

Do not display Miami under Texas.

---

# 32. DASHBOARD

Rename:

```text
Overview
```

to:

```text
Dashboard
```

The dashboard should be operationally useful.

Enhance it with real data-driven visualizations such as:

- Claims processed
- Claims pending
- Claims failed
- Positive matches
- No matches
- Guidewire submissions
- Portal success rate
- Processing duration
- Queue depth
- Florida vs Texas distribution
- scraper performance
- daily/weekly trends

Charts must use real backend data.

Do not create fake/random chart values.

Dashboard tables should also support filtering/sorting/pagination where applicable.

---

# 33. EXPORTS — CLAIM DETAIL PAGE

For:

```text
/claims/[claim-id]
```

provide:

- Export Excel
- Export CSV
- Export PDF
- Export JSON

These must export actual claim data.

Do not create placeholder downloads.

---

# 34. PDF EXPORT — STRICT REQUIREMENTS

PDF export must:

- generate a valid PDF
- open successfully
- download directly as `.pdf`
- preserve the current theme/design as closely as practical
- contain the entire relevant page
- exclude:
  - application header
  - footer
  - navigation/sidebar
  - interactive-only controls where appropriate
- preserve tables and sections
- handle multiple pages
- not truncate content
- not produce corrupt PDFs

The PDF should represent the complete claim details content, not merely the currently visible viewport.

Test both:

- light theme
- dark theme

where supported.

---

# 35. EXPORT VALIDATION

Do not merely generate export files.

Actually validate them.

For:

```text
Excel
CSV
JSON
PDF
```

perform:

```text
Generate
   ↓
Open/read/parse
   ↓
Validate structure
   ↓
Validate data
   ↓
Confirm file integrity
```

The PDF must be opened and confirmed valid.

Excel must be readable.

CSV must parse correctly.

JSON must be valid JSON.

Do not claim export functionality works until files have actually been validated.

---

# 36. THEME SYSTEM

Theme changer must work globally.

Verify:

- Light
- Dark
- system/default if supported

Changing theme must not:

- break layout
- hide text
- make controls unreadable
- produce inconsistent top-bar backgrounds
- create page-specific theme differences
- break tables
- break modals
- break charts
- break forms
- break exports

The top bar/header background must be consistent with the application's design system.

Do not fix one page while breaking another.

---

# 37. GLOBAL DESIGN SYSTEM

All pages must share consistent:

- typography
- spacing
- cards
- borders
- shadows
- colors
- buttons
- tables
- forms
- modals
- drawers
- status badges
- header
- navigation
- theme behavior

Do not create page-specific styling that visually conflicts with the rest of the application.

---

# 38. FULL RESPONSIVENESS

The entire application must be responsive.

Required testing sizes include:

```text
1920
1600
1440
1366
1280
1024
900
768
600
480
430
414
390
375
360
```

There must be:

- no accidental horizontal overflow
- no clipped content
- no unusable tables
- no fixed-width forms
- no broken modals
- no overflowing charts
- no inaccessible controls

---

# 39. MOBILE UX

Mobile is not just a scaled desktop UI.

Provide a purpose-built mobile experience.

Mobile must include:

- responsive header
- mobile navigation
- fixed bottom/footer navigation
- touch-friendly controls
- responsive cards
- responsive forms
- responsive modals/drawers
- mobile-friendly tables transformed into cards where appropriate

Do not remove important functionality simply because the device is small.

---

# 40. FULL VIEWPORT UTILIZATION

The active application should use the full available screen.

Avoid unnecessary:

```css
max-width: 1200px;
```

or other fixed-width layouts that create large empty areas.

Desktop:

```text
Full-width enterprise workspace
```

Tablet:

```text
Adaptive workspace
```

Mobile:

```text
Purpose-built touch experience
```

---

# 41. PERFORMANCE

The application is currently reported as slow.

Profile before optimizing.

Investigate:

- unnecessary API requests
- duplicate API calls
- N+1 database queries
- inefficient ORM queries
- large payloads
- repeated renders
- unnecessary React state updates
- oversized JSON
- unoptimized tables
- unnecessary polling
- browser startup
- scraper waits
- Celery queue delays
- Redis communication
- database indexes
- frontend bundle size

Use:

- pagination
- lazy loading
- caching where appropriate
- memoization where appropriate
- database indexes
- efficient queries
- connection pooling
- event-driven status updates where appropriate

Do not sacrifice automation reliability for micro-optimizations.

---

# 42. STARTUP SCRIPTS

Both setup scripts must actually work.

Test:

```text
setup.ps1
setup-local.ps1
```

Fix errors such as:

```text
error 2147942632 (0x800700e8)
```

when launching:

```text
powershell.exe
-NoExit
-ExecutionPolicy Bypass
...
activate.ps1
uvicorn ...
```

Do not merely suppress the error.

Make startup robust.

Verify:

- backend
- frontend
- Redis
- Celery worker
- Celery Beat
- monitoring
- required dependencies

start correctly.

---

# 43. PORT MANAGEMENT

The frontend previously failed with:

```text
EADDRINUSE
port 3000 already in use
```

Handle this properly.

Before starting:

- detect whether the port is already occupied
- determine whether it belongs to the application's existing process
- reuse/terminate stale application process safely
- avoid killing unrelated processes
- start the application on the configured port

Do not hide port conflicts.

---

# 44. HEALTH CHECKS

Implement or verify health endpoints for:

```text
Application
Database
Redis
Celery
Queue
Chrome
Anti-Captcha
Guidewire
Fuzzy Match API
```

The UI should distinguish:

```text
UP
DEGRADED
DOWN
NOT CONFIGURED
```

Do not display "UP" simply because a process exists.

---

# 45. ERROR HANDLING

Every important operation must provide:

- user-friendly error
- backend log
- correlation/request ID where appropriate
- retry information
- recoverable/non-recoverable classification

Never swallow exceptions silently.

Never display misleading success messages.

---

# 46. DATABASE INTEGRITY

Verify:

- migrations
- schema
- foreign keys
- indexes
- uniqueness
- status values
- JSON fields
- timestamps
- transaction boundaries

Do not recreate the database just to make tests pass.

Do not delete real data unless explicitly required.

---

# 47. SECURITY

Verify:

- no credentials in source code
- no API keys in frontend
- no passwords in logs
- secure settings storage
- safe file uploads
- validation
- path traversal protection
- command execution safety
- secure browser configuration
- protected API endpoints

Existing sensitive credentials must be migrated to secure configuration.

---

# 48. TESTING STRATEGY

Do not stop at compilation.

Perform:

### Static validation

- TypeScript
- Python
- lint
- imports
- dependency checks

### Backend

- API tests
- database tests
- queue tests
- task tests
- fuzzy-match tests

### Frontend

- route tests
- component tests
- interaction tests

### Browser

Use the actual browser to test:

- login/navigation where applicable
- dashboard
- claims
- create/edit
- queue
- scraper execution
- settings
- exports
- theme
- responsive layouts

### Automation

Test real:

```text
Chrome
Anti-Captcha extension
County portal
Search
CAPTCHA
Extraction
Database
Fuzzy match
Guidewire
```

where environment/configuration allows.

---

# 49. END-TO-END TEST

The ultimate test is:

```text
REAL INPUT
   ↓
REAL FILE IMPORT
   ↓
REAL DATABASE RECORD
   ↓
REAL QUEUE ITEM
   ↓
REAL AUTOMATIC/MANUAL START
   ↓
REAL SYSTEM GOOGLE CHROME
   ↓
REAL ANTICAPTCHA EXTENSION
   ↓
REAL CAPTCHA
   ↓
REAL COUNTY PORTAL
   ↓
REAL SEARCH
   ↓
REAL RESULT EXTRACTION
   ↓
REAL PAGINATION
   ↓
REAL DATABASE STORAGE
   ↓
REAL FUZZY MATCH
   ↓
REAL POSITIVE/NEGATIVE RESULT
   ↓
REAL GUIDEWIRE REQUEST
   ↓
REAL ACTIVITY ID
   ↓
REAL FINAL STATUS
```

Every stage must be observable and verifiable.

---

# 50. CURRENT_PROBLEMS

Whenever `@[current_problems]` is available, treat it as an active defect list.

Do not ignore it.

For every current problem:

1. Reproduce it.
2. Identify root cause.
3. Fix it.
4. Test it.
5. Verify no regression.
6. Clear it only after the problem is genuinely resolved.

Do not simply mark problems as completed because code was changed.

---

# 51. DO NOT CREATE NEW PROBLEMS WHILE FIXING OLD ONES

This is extremely important.

Previous changes have repeatedly caused regressions such as:

- fixing one page and breaking another
- moving Engine Status into navigation
- changing top-bar colors
- breaking theme
- breaking APIs
- breaking queue execution
- incorrect county categorization
- wrong scraper files
- missing form fields
- broken PDF
- broken startup scripts
- port conflicts

Therefore, after every major change:

```text
Implement
   ↓
Regression Test
   ↓
Browser Test
   ↓
API Test
   ↓
Automation Test
```

Do not modify unrelated working functionality unnecessarily.

---

# 52. NO MOCKS FOR PRODUCTION FUNCTIONALITY

Do not use:

- fake scraper results
- fake queue processing
- fake Guidewire success
- fake health status
- fake charts
- fake telemetry
- fake export data

Mocks are acceptable only inside automated unit/integration tests where explicitly appropriate.

The actual application must use real data.

---

# 53. FINAL SOURCE CLEANUP

After implementation:

- remove unused files
- remove obsolete scrapers
- remove stale Python artifacts
- remove dead imports
- remove duplicate components
- remove unused routes
- remove debug code
- remove hardcoded credentials
- remove hardcoded local absolute paths
- remove unnecessary Chromium dependency from the actual automation path
- retain only required production code

Do not remove anything without verifying its usage.

---

# 54. FINAL BROWSER AUDIT

Use the browser to inspect the entire application.

Check:

- Dashboard
- Claims
- Claim Detail
- Scraped Cases
- Queue
- Telemetry
- 8-Bot Status
- Settings
- Imports
- Exports
- Theme
- Responsive layouts

Test:

```text
Desktop
Tablet
Mobile
```

Test:

- sorting
- filtering
- pagination
- CRUD
- bulk actions
- dialogs
- drawers
- exports
- theme switching
- queue start/stop
- automation
- status updates

Fix every issue found.

Then repeat the audit.

---

# 55. FINAL DEFINITION OF DONE

Do NOT report:

```text
Completed
```

just because:

- code compiles
- server starts
- Celery starts
- Beat starts
- a page renders
- API returns 200 for one claim
- a scraper file exists

The system is complete only when the actual functionality has been verified.

Final checklist:

```text
[ ] Power Automate V4 analyzed
[ ] V4 behavior mapped
[ ] 3 Florida scrapers verified
[ ] 5 Texas scrapers verified
[ ] Miami-Dade correctly categorized as Florida
[ ] Cross-state routing verified
[ ] System Google Chrome verified
[ ] Anti-Captcha extension dynamically located
[ ] Anti-Captcha works in system Chrome
[ ] Python 3.14.7 verified
[ ] Old Python artifacts removed
[ ] Setup scripts work
[ ] Redis works
[ ] Celery worker works
[ ] Celery Beat works
[ ] Monitoring/inspection works or limitation documented
[ ] Automatic queue works
[ ] Manual queue works
[ ] Attended mode visibly launches Chrome
[ ] Claim CRUD complete
[ ] All import columns available
[ ] Claim API 404 issue resolved
[ ] All 8 scrapers functional
[ ] Scraped case data matches V4
[ ] Fuzzy matching verified
[ ] Guidewire payload verified
[ ] Guidewire response verified
[ ] Scraped Cases UI redesigned
[ ] Portal grouping works
[ ] Search works
[ ] Filters work
[ ] Sorting works
[ ] Pagination works
[ ] All major tables have sorting/filter/pagination
[ ] Telemetry enhanced
[ ] 8-bot status enhanced
[ ] Dashboard renamed from Overview
[ ] Dashboard charts use real data
[ ] Excel export works
[ ] CSV export works
[ ] JSON export works
[ ] PDF export works
[ ] PDF opens successfully
[ ] PDF excludes navigation/header/footer
[ ] PDF preserves page design/theme
[ ] Export files were actually validated
[ ] Theme changer works
[ ] Global theme consistency verified
[ ] Full responsive UI implemented
[ ] Mobile bottom navigation works
[ ] No horizontal overflow
[ ] Full viewport utilized
[ ] Performance issues investigated/fixed
[ ] No hardcoded secrets
[ ] No hardcoded project-root paths
[ ] No unwanted/unused files
[ ] No regression introduced
[ ] Browser QA completed
[ ] End-to-end automation tested
```

---

# 56. FINAL EXECUTION INSTRUCTION

Do not give me a long explanation of what you *intend* to do.

Actually work on the existing application.

Use this execution cycle:

```text
INSPECT
   ↓
COMPARE WITH V4
   ↓
IDENTIFY GAPS
   ↓
IMPLEMENT
   ↓
RUN
   ↓
TEST
   ↓
BROWSER VERIFY
   ↓
FIX
   ↓
REGRESSION TEST
   ↓
CLEANUP
   ↓
FINAL VERIFY
```

If you discover a conflict between an older instruction and the latest verified **Power Automate V4 behavior**, use **V4 as the authoritative automation baseline**, while preserving existing application functionality wherever it is not in conflict.

If a requirement is already correctly implemented, **do not rewrite it unnecessarily**. Verify it and preserve it.

If a requirement is partially implemented, finish it.

If it is incorrectly implemented, correct it.

If obsolete code exists, remove it only after proving it is unused.

**Do not sacrifice functionality, UI, UX, data integrity, automation reliability, or Guidewire compatibility while performing cleanup or modernization.**

The final application must be a **real, working, production-grade UAIC Claim & RPA Orchestrator**, not a collection of screens that merely appears complete.