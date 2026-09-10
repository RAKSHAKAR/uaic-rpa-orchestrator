# MASTER PROMPT
# UAIC ORCHESTRATOR — ENTERPRISE SETUP CONSOLE
# COMPLETE OPTIONS 1–9 + MAILDEV + CELERY/REDIS + BROWSER RUNTIME + RPA CONCURRENCY
# VALIDATION, REPAIR, TESTING, CLEANUP & PRODUCTIONIZATION

You are working on the EXISTING:

**UAIC Claim & RPA Orchestrator**

This is NOT a greenfield implementation.

This is NOT a request to create a demo.

This is NOT a request to rewrite the application blindly.

Your responsibility is to:

> INSPECT → UNDERSTAND → CORRECT → ENHANCE → INTEGRATE → TEST → VALIDATE → PRODUCTIONIZE

the existing Setup Console and all services/features that it controls.

The final result must be an enterprise-grade, reliable, safe, configurable, observable and fully tested local operations/orchestration console.

---

# 1. NON-NEGOTIABLE PRINCIPLES

## 1.1 Existing Application

The application already contains working functionality.

Therefore:

- Preserve all valid existing functionality.
- Do not remove features merely to simplify implementation.
- Do not replace working business logic without a technical reason.
- Do not break existing APIs.
- Do not break database models.
- Do not break the RPA engine.
- Do not break county scrapers.
- Do not break Guidewire integration.
- Do not break notification/email functionality.
- Do not break dashboard functionality.
- Do not break exports.
- Do not break settings.
- Do not break Attended mode.
- Do not break Unattended mode.
- Do not break Docker support.
- Do not break Celery/Redis.
- Do not break MailDev.

However:

> DO NOT BLINDLY PRESERVE BROKEN BEHAVIOR.

If existing behavior is technically incorrect, incomplete, unsafe, slow or inconsistent:

1. identify the defect;
2. determine the intended behavior;
3. implement the correct behavior;
4. preserve the business objective;
5. test the correction;
6. regression-test everything affected.

The objective is a fully working enterprise solution, not historical code preservation.

---

# 2. CURRENT SETUP CONSOLE

The Setup Console currently provides:

```text
[1] Start All Application Services
[2] Stop / Kill All Running Services
[3] Enterprise Data Cleanup & Retention
[4] Install / Update Dependencies
[5] Purge / Delete Dependency Folders
[6] Configure RPA Execution Mode
[7] Full Diagnostics & Test Suite
[8] Docker Stack Deployment
[9] Live Service Status Monitor

[M] Open MailDev Web Inspector

[0] Exit Console
```

Do not remove or renumber these options.

Improve their implementation.

Every option must actually perform the operation it claims to perform.

---

# 3. FIRST STEP — COMPLETE EXISTING-SOLUTION AUDIT

Before modifying code, perform a complete audit.

Inspect:

## Setup / PowerShell

- setup-local.ps1
- all PowerShell scripts called by it
- helper scripts
- process-management scripts
- startup scripts
- shutdown scripts
- dependency scripts
- diagnostics scripts
- Docker scripts
- cleanup scripts
- browser setup scripts
- RPA configuration scripts

## Backend

Inspect:

- Python version
- Python virtual environment
- FastAPI
- Celery
- Celery Beat
- Redis
- SQLAlchemy
- database connection
- configuration management
- queue management
- RPA orchestration
- browser factory
- browser configuration
- scraper execution
- notifications
- email
- MailDev integration
- telemetry
- health endpoints
- logging
- error handling
- retry mechanisms

## Frontend

Inspect:

- Next.js
- React
- TypeScript
- Settings UI
- Browser Automation Engine UI
- RPA configuration UI
- concurrency settings
- service status UI
- dashboard
- notification settings
- email settings
- theme
- responsive behavior

## Infrastructure

Inspect:

- Redis
- PostgreSQL
- Celery
- Celery Beat
- Flower/monitoring
- MailDev
- Docker
- ports
- health checks
- environment variables
- filesystem
- logs

## RPA

Inspect:

- browser runtime
- Chromium
- Google Chrome
- Microsoft Edge
- Anti-Captcha extension
- extension path
- Attended mode
- Unattended mode
- browser launch code
- all 8 county scrapers
- queue orchestration
- claim concurrency
- scraper concurrency

## Data

Inspect:

- Claims
- Claim execution data
- Work Queue
- Scraped Court Cases
- Fuzzy Match
- Guidewire Activity
- Notifications
- Notification Delivery History
- Telemetry
- Bot Execution History
- Dashboard metrics
- Logs
- Exports
- caches
- temporary files
- Redis runtime data

## Tests

Inspect:

- Pytest
- Ruff
- TypeScript
- ESLint
- frontend build
- backend startup tests
- integration tests
- RPA tests
- browser tests
- setup tests
- Docker tests

---

# 4. CREATE ONE AUTHORITATIVE SERVICE REGISTRY

Do NOT maintain separate hardcoded service definitions throughout multiple scripts.

Create or repair one authoritative service registry.

Each service definition should contain, where applicable:

```text
Service ID
Display Name
Category
Process Name
PID
Port
Protocol
Startup Command
Working Directory
Environment
Health Endpoint
Health Check
Dependencies
Shutdown Strategy
Restart Strategy
Docker Service Name
Required / Optional
Local / Docker
Log Location
Owner
```

At minimum audit:

```text
Frontend
Backend
Celery Worker
Celery Beat
Redis
PostgreSQL
MailDev Web
MailDev SMTP
Flower / Monitoring
RPA Engine
Browser Runtime
Anti-Captcha Extension
Docker
```

Do not assume this is the complete list.

Add any additional real application service discovered during the audit.

---

# 5. SERVICE DEPENDENCY GRAPH

Build the actual dependency graph.

A likely model is:

```text
PostgreSQL
     │
Redis
     │
     ├──────────────┐
     │              │
FastAPI          Celery Worker
     │              │
     │           Celery Beat
     │              │
     │        RPA Orchestrator
     │              │
     │       Browser Factory
     │              │
     │      County Scrapers
     │
Frontend
     │
MailDev / Notification Services
```

Do not blindly use this diagram.

Determine the real dependency graph from the application.

Startup and shutdown must respect dependencies.

---

# 6. OPTION [1] — START ALL APPLICATION SERVICES

Option [1] must start the complete application environment.

It must NOT merely open several terminals and assume success.

Required behavior:

1. Detect existing service state.
2. Detect port conflicts.
3. Detect whether a service is already healthy.
4. Reuse healthy existing services.
5. Start missing services.
6. Wait for readiness.
7. Verify process.
8. Verify PID where applicable.
9. Verify port.
10. Verify health endpoint.
11. Verify actual application response.
12. Record startup result.
13. Continue safely when an optional service fails.
14. Clearly report mandatory-service failures.

---

# 7. STARTUP MODES

Option [1] must allow:

```text
[1] Attended GUI
[2] Unattended Headless
```

The selected mode must actually propagate to:

```text
Setup Console
      ↓
Configuration
      ↓
Backend
      ↓
Celery Task
      ↓
RPA Orchestrator
      ↓
Browser Factory
      ↓
County Scraper
```

Changing the displayed console text alone is NOT sufficient.

---

# 8. ATTENDED RPA

When Attended mode is selected:

- Browser window must actually appear.
- RPA must control the visible browser.
- Navigation must work.
- DOM interaction must work.
- Anti-Captcha extension must load.
- County portal automation must execute.
- Browser must close cleanly.

Do NOT report Attended success because only a background process started.

---

# 9. UNATTENDED RPA

When Unattended mode is selected:

- automation must run without requiring visible GUI;
- browser runtime must support the configured unattended mode;
- queue execution must work;
- browser automation must work;
- Anti-Captcha behavior must be validated;
- county scrapers must work;
- shutdown/recovery must work.

Do not create separate business logic for Attended and Unattended execution.

Use the same core RPA workflow.

---

# 10. ATTENDED / UNATTENDED PARITY

Mandatory sequence:

```text
Attended
   ↓
Real RPA execution
   ↓
Unattended
   ↓
Same RPA execution
```

Test:

```text
Attended
→ Unattended
→ Attended
→ Unattended
```

There must not be a situation where:

```text
Attended = PASS
Unattended = FAIL
```

or:

```text
Unattended = PASS
Attended = FAIL
```

without an explicitly documented browser/runtime limitation.

If a defect is found, fix it.

---

# 11. OPTION [2] — STOP / KILL ALL SERVICES

Option [2] must stop ALL application-owned services.

At minimum:

```text
Frontend              3000
Backend               8000
Flower/Monitoring     5555
MailDev Web           1080
MailDev SMTP          1025
Redis                 6379
PostgreSQL            5432
Celery Worker
Celery Beat
RPA processes
Browser processes created by UAIC
Other UAIC-owned processes
```

The exact service list must come from the service registry.

---

# 12. SAFE PROCESS TERMINATION

NEVER blindly execute:

```text
taskkill /F /IM python.exe
```

or:

```text
taskkill /F /IM node.exe
```

or another broad process kill.

This can kill unrelated user applications.

Instead:

1. identify the process;
2. verify it belongs to UAIC;
3. verify command line;
4. verify working directory;
5. verify PID;
6. gracefully stop it;
7. wait;
8. verify termination;
9. force terminate only if necessary;
10. verify again.

---

# 13. MAILDEV STOP REQUIREMENT

MailDev MUST be included in Option [2].

After stopping:

```text
Port 1080 = FREE
Port 1025 = FREE
MailDev Web = STOPPED
MailDev SMTP = STOPPED
```

Verify actual process termination.

Do not simply print:

```text
MailDev stopped
```

without verification.

---

# 14. STOP IDEMPOTENCY

Running Option [2] when nothing is running must be safe.

Example:

```text
All UAIC application services are already stopped.
```

Running Option [2] multiple times must not cause errors.

---

# 15. PORT CONFLICT HANDLING

The previous environment experienced:

```text
EADDRINUSE :::3000
```

This MUST be handled properly.

Before startup:

1. check port;
2. identify owner;
3. determine whether it belongs to UAIC;
4. reuse if correct;
5. do NOT kill unrelated process;
6. report conflict;
7. provide recovery.

Apply this to all configured ports:

```text
3000
8000
5555
1080
1025
6379
5432
```

and any additional configured ports.

---

# 16. OPTION [3] — ENTERPRISE DATA CLEANUP & RETENTION

Option [3] must be a real enterprise data-retention system.

Do NOT implement:

```text
delete some files
```

or:

```text
delete visible history
```

The database and every dependent operational surface must be reconciled.

---

# 17. CLEANUP DATA CATEGORIES

Determine the real data model first.

At minimum audit:

```text
1. Claims
2. Claim Automation Data
3. Work Queue Data
4. Scraped Court Case Data
5. Fuzzy Match Data
6. Guidewire Activity Data
7. Outbound Notification Data
8. Notification Delivery History
9. Notification Events
10. Notification Attempts / Retries
11. Stage Execution Telemetry
12. Bot / Scraper Execution History
13. Application Run History
14. Error Records
15. Dashboard / Analytics Data
16. Application Logs
17. Scraper Logs
18. Generated Export Files
19. Temporary Files
20. Caches
21. Redis Runtime Data
22. Other application-generated operational data
```

Do not invent categories that do not exist.

Add actual categories discovered during audit.

---

# 18. MULTI-SELECT CLEANUP

The user must be able to select multiple categories in one operation.

Support:

```text
Select All
Select None
Individual Selection
Multiple Selection
```

---

# 19. TIME-BASED CLEANUP

Support:

```text
Days
Weeks
Months
Years
Current Month
Previous Month
Current Quarter
Previous Quarter
Current Year
Previous Year
Last N Days
Last N Weeks
Last N Months
Last N Years
Before Date
After Date
Custom Date Range
```

---

# 20. CURRENT MONTH MUST BE DYNAMIC

Never hardcode a date.

For example, if current date is September 5, 2026:

```text
Current Month:
09/01/2026 00:00:00
→
current date/time
```

When the month changes, the range must automatically change.

Use the application's configured timezone.

Handle DST correctly where applicable.

---

# 21. CLEANUP DRY RUN

Before deletion, calculate the exact impact.

Display:

```text
Category
Records Found
Files Found
Estimated Size
Date Range
Related Records
Potential Dependencies
```

Dry-run MUST NOT delete anything.

---

# 22. CLEANUP CONFIRMATION

Before destructive execution:

- show selected categories;
- show time range;
- show expected records;
- show expected files;
- show dependencies;
- show warning;
- require explicit confirmation.

Cancellation must result in:

```text
No data deleted.
```

---

# 23. CLEANUP RELATIONSHIP GRAPH

Determine actual relationships.

Example:

```text
Claim
 ├── Claim Automation
 ├── Queue
 ├── Scraped Court Cases
 ├── Fuzzy Match
 ├── Guidewire Activity
 ├── Notifications
 │    ├── Notification Events
 │    ├── Deliveries
 │    ├── Attempts
 │    └── Retry History
 ├── Telemetry
 └── Bot Execution History
```

Use:

- foreign keys;
- relationships;
- cascade rules;
- explicit dependent deletion;
- referential integrity checks.

Never leave orphan records.

---

# 24. NOTIFICATION CLEANUP

If Notification Delivery History is selected:

the actual database records MUST be deleted when eligible.

Verify:

```text
Database
↓
API
↓
Backend
↓
Notification History
↓
Delivery History
↓
Retry History
↓
Dashboard
↓
Frontend
```

Do not accept:

```text
API says deleted
```

while records still exist in the database.

---

# 25. CONFIGURATION PROTECTION

Cleanup MUST NOT accidentally delete:

```text
Application Configuration
User Configuration
RPA Configuration
Browser Configuration
County Configuration
Scraper Configuration
SMTP Configuration
Notification Provider Configuration
Email Configuration
AI Configuration
Authentication Configuration
Secrets
Credentials
Branding
Theme
Subscription Configuration
```

unless an explicit, separately supported administrative configuration-reset operation exists.

Operational history and configuration must be clearly separated.

---

# 26. CLEANUP TRANSACTION SAFETY

Where supported:

```text
BEGIN
   Validate
   Calculate
   Delete dependencies
   Delete selected data
   Validate integrity
COMMIT
```

On unrecoverable failure:

```text
ROLLBACK
```

For large datasets:

- batch safely;
- maintain consistency;
- avoid loading everything into memory;
- report progress.

---

# 27. CLEANUP IDEMPOTENCY

Running the same cleanup twice must be safe.

Example:

```text
First:
Claims = 10 deleted

Second:
Claims = 0 deleted
```

The second run must still complete successfully.

---

# 28. DASHBOARD RECONCILIATION

After cleanup:

- invalidate caches;
- refresh API queries;
- refresh dashboard metrics;
- refresh frontend query state;
- recalculate persisted aggregates where applicable;
- invalidate Redis entries;
- verify displayed values against database state.

Never merely hide deleted records from the UI.

---

# 29. CACHE INVALIDATION

Identify actual caches.

At minimum audit:

```text
Redis Cache
API Cache
Frontend Query Cache
Dashboard Cache
Notification Cache
Scraper Cache
Generated Report Cache
```

Invalidate only affected caches.

Do not blindly clear all caches unless technically required.

---

# 30. CLEANUP AUDIT TRAIL

Every cleanup must generate an audit record.

Record:

```text
Cleanup ID
Operator
Start Time
End Time
Categories
Time Scope
Date Range
Records Discovered
Records Deleted
Files Deleted
Cache Entries Invalidated
Warnings
Errors
Rollback Status
Final Status
Correlation ID
```

Statuses:

```text
Preview
Confirmed
Running
Completed
Partially Completed
Failed
Rolled Back
Cancelled
```

The cleanup's own audit record must not be deleted by the cleanup currently executing.

---

# 31. OPTION [4] — INSTALL / UPDATE DEPENDENCIES

Option [4] must install, repair and validate ALL required dependencies.

Target:

```text
Python 3.14.7
Backend
Frontend
Node/NPM
Celery
Redis client
PostgreSQL dependencies
Playwright
RapidFuzz
SQLAlchemy
FastAPI
Uvicorn
Pydantic
Excel/CSV/PDF dependencies
Testing dependencies
Linting dependencies
Build dependencies
```

Use authoritative dependency files.

Do not install packages merely because obsolete code references them.

---

# 32. PYTHON 3.14.7

Python MUST remain:

```text
3.14.7
```

Do not downgrade Python.

Verify:

```text
python --version
```

Verify the actual virtual environment interpreter.

If a dependency is incompatible:

1. identify it;
2. find a compatible version;
3. update/replace safely;
4. test;
5. document.

---

# 33. BROWSER AUTOMATION ENGINE — THREE SUPPORTED BROWSERS

The application currently supports:

```text
Chromium
Google Chrome
Microsoft Edge
```

ALL THREE MUST REMAIN SUPPORTED.

Do not remove any of them.

Do not force Chrome.

Do not force Chromium.

Do not remove Edge.

---

# 34. BROWSER CONFIGURATION

Browser selection must be configuration-driven.

Supported values:

```text
chromium
chrome
edge
```

Architecture:

```text
Settings
   ↓
Browser Automation Engine
   ↓
Selected Browser
   ↓
Central Browser Factory
   ↓
Anti-Captcha Extension
   ↓
RPA Engine
   ↓
County Scraper
```

No county scraper should hardcode a browser.

---

# 35. CENTRAL BROWSER FACTORY

Create or repair one browser factory.

Conceptually:

```text
BrowserRuntime.CHROMIUM
BrowserRuntime.CHROME
BrowserRuntime.EDGE
```

It must resolve:

```text
Executable
Version
Launch Arguments
Profile
User Data Directory
Attended / Unattended
Headless Configuration
Extension Path
Timeout
Download Directory
Proxy
Anti-Captcha Configuration
Browser-Specific Flags
```

---

# 36. CHROMIUM

If Chromium is selected:

- validate required Chromium runtime;
- install it only if actually required;
- do not repeatedly download it;
- validate Playwright compatibility;
- validate launch;
- validate automation;
- validate Anti-Captcha;
- validate shutdown.

---

# 37. GOOGLE CHROME

If Chrome is selected:

- detect installed system Chrome;
- determine executable path;
- determine version;
- validate launch;
- validate automation;
- validate extension;
- validate profile;
- validate Attended;
- validate Unattended where supported.

Do not replace system Chrome with bundled Chromium.

---

# 38. MICROSOFT EDGE

If Edge is selected:

- detect installed Edge;
- determine executable;
- determine version;
- validate launch;
- validate automation;
- validate extension;
- validate profile;
- validate Attended;
- validate Unattended where supported.

Do not remove Edge support.

---

# 39. PLAYWRIGHT VS BROWSER RUNTIME

Do NOT confuse:

```text
Playwright Python package
```

with:

```text
Playwright-managed Chromium browser
```

The application may use Playwright while controlling:

```text
Chromium
Google Chrome
Microsoft Edge
```

Determine the actual requirement.

Do not blindly download Chromium every time.

If Chromium is required, install it.

If Chrome/Edge is selected and Chromium is not required, do not waste time and disk space downloading it.

If Chromium is required for automated tests but not production RPA, clearly separate:

```text
Production RPA Runtime
```

from:

```text
Test Runtime
```

---

# 40. ANTI-CAPTCHA EXTENSION

The extension path must be dynamically resolved.

Use:

```text
<PROJECT_ROOT>/anticaptcha-plugin_v0.83
```

Never use developer-specific absolute paths.

Verify:

- directory exists;
- manifest exists;
- manifest is valid;
- service worker/background configuration;
- required files;
- browser compatibility;
- extension loading;
- runtime integration.

Validate against:

```text
Chromium
Google Chrome
Microsoft Edge
```

---

# 41. REAL BROWSER SMOKE TEST

For each available/configured browser:

```text
Launch
 ↓
Create automation context
 ↓
Load Anti-Captcha
 ↓
Open test page
 ↓
Verify DOM
 ↓
Verify JavaScript
 ↓
Verify extension
 ↓
Navigate
 ↓
Close
```

Do not mark browser support PASS merely because the executable exists.

Statuses should distinguish:

```text
Installed
Detected
Available
Launchable
Automatable
Extension Compatible
Fully Validated
```

---

# 42. FRONTEND DEPENDENCIES

Validate:

```text
Node
NPM
package.json
package-lock
Next.js
React
TypeScript
UI dependencies
Export dependencies
Testing dependencies
Build dependencies
```

Investigate warnings such as:

```text
unrs-resolver@1.12.2 install script blocked
```

Determine:

1. why;
2. whether required;
3. whether it affects runtime;
4. whether it affects build;
5. whether it affects production;
6. whether package update is appropriate.

Do not simply suppress warnings.

---

# 43. OPTION [5] — PURGE / DELETE DEPENDENCY FOLDERS

Option [5] may remove only generated dependency/build directories.

At minimum audit:

```text
backend/.venv
node_modules
.next
```

and any other verified generated directories.

Never delete:

```text
Source Code
Database
User Data
Configuration
.env
Secrets
Credentials
RPA Configuration
County Configuration
Scraper Code
Anti-Captcha Extension
Automation Assets
Documentation
Tests
Power Automate Reference Artifacts
```

---

# 44. OPTION [5] PRECONDITION

Before purge:

1. detect running services;
2. stop affected services;
3. verify no process uses target folder;
4. show deletion plan;
5. request confirmation;
6. delete only approved generated folders;
7. verify deletion;
8. verify source remains intact.

Then test:

```text
[5] Purge
 ↓
[4] Install
 ↓
[7] Diagnostics
 ↓
[1] Start
 ↓
[9] Status
```

---

# 45. OPTION [6] — CONFIGURE RPA EXECUTION MODE

Support:

```text
Attended GUI
Unattended Headless
```

The selected mode must be persisted and consumed by the actual backend.

Do not create multiple conflicting sources of truth.

Flow:

```text
Option [6]
 ↓
Persist Configuration
 ↓
Backend Reads Configuration
 ↓
Celery Reads Configuration
 ↓
RPA Orchestrator
 ↓
Browser Factory
 ↓
County Scraper
```

---

# 46. BROWSER + MODE CONFIGURATION MATRIX

The system must support combinations such as:

```text
Chromium + Attended
Chromium + Unattended

Chrome + Attended
Chrome + Unattended

Edge + Attended
Edge + Unattended
```

Where a specific technical limitation exists, detect it and report it accurately.

Never silently switch to another browser.

Never silently switch execution mode.

---

# 47. PARALLEL RPA CONCURRENCY

The application contains:

> Parallel RPA Concurrency / Concurrent Scraper Worker Fleet

with:

```text
1 – 10 Parallel Claims
```

This setting must be fully functional.

The value:

```text
10
```

means:

> Maximum 10 claims may be actively processed concurrently.

It does NOT automatically mean:

```text
10 Celery Workers
```

---

# 48. CRITICAL CELERY WORKER VS CLAIM CONCURRENCY DISTINCTION

These are different concepts.

Example:

```text
Celery Workers = 1
```

means:

```text
One Celery worker instance
```

while:

```text
RPA Concurrency = 10
```

means:

```text
Maximum 10 simultaneous claim executions
```

ONLY if the underlying Celery execution architecture genuinely supports it.

The system must NEVER display:

```text
10x Parallel Claims
```

as if it is effective when the underlying runtime can only execute one task at a time.

---

# 49. CELERY EXECUTION CAPACITY

Inspect the actual:

```text
Worker Count
Pool
Concurrency
Queues
Prefetch
Task Routing
Task Acknowledgement
Task Execution
```

Pay special attention to configurations such as:

```text
Pool: solo
Concurrency: 12
```

Do NOT assume:

```text
solo + concurrency=12
```

automatically means 12 simultaneously executing RPA tasks.

Determine the actual effective capacity.

If the current architecture prevents the configured RPA concurrency from working, FIX the architecture.

---

# 50. EFFECTIVE RPA CONCURRENCY

Expose:

```text
Configured RPA Concurrency
Actual Celery Capacity
Actual Scraper Capacity
Active Claims
Available Claim Slots
Queued Claims
```

Example:

```text
Configured RPA Capacity: 10
Celery Effective Capacity: 10
Active Claims: 7
Available Slots: 3
Queued Claims: 23
```

If the real capacity is only 1:

```text
Configured RPA Capacity: 10
Effective Capacity: 1
Status: DEGRADED
Reason: Celery execution pool currently supports one active task
```

Do NOT falsely display:

```text
10/10 Running
```

unless ten claims are genuinely executing.

---

# 51. CLAIM CONCURRENCY SEMANTICS

Example:

```text
50 queued claims
RPA concurrency = 10
```

Expected:

```text
Running:
Claim 1
Claim 2
Claim 3
Claim 4
Claim 5
Claim 6
Claim 7
Claim 8
Claim 9
Claim 10

Waiting:
Claim 11 → Claim 50
```

When Claim 4 finishes:

```text
Claim 11
```

should occupy the available slot.

Maintain:

```text
MAX 10 ACTIVE CLAIMS
```

until the queue is exhausted.

---

# 52. FAILURE ISOLATION

If:

```text
Claim 3 = FAILED
```

the other nine running claims must continue.

Then the freed slot should be available to the next queued claim.

A single failed claim must not stop the entire queue unless the failure is classified as a global infrastructure failure.

---

# 53. COUNTY SCRAPER CONCURRENCY

Do not confuse:

```text
Claim Concurrency
```

with:

```text
County Scraper Concurrency
```

One claim may require multiple county portals.

Therefore inspect whether each claim executes:

```text
Sequentially
```

or:

```text
Parallel
```

at scraper level.

Prevent uncontrolled browser explosion.

For example:

```text
10 Claims
×
8 Scrapers
=
Potentially very high browser activity
```

Do not automatically create 80 browser instances unless the architecture intentionally supports and has been capacity-tested for it.

Implement controlled concurrency.

---

# 54. RESOURCE PROTECTION

At high concurrency monitor:

```text
CPU
Memory
Disk
Browser Processes
Browser Contexts
Redis
PostgreSQL
Celery
Queue Latency
Network
CAPTCHA failures
Portal timeouts
Portal errors
Guidewire latency
Email latency
```

Concurrency 10 must be treated as a maximum, not automatically the safest production setting.

---

# 55. CONCURRENCY TESTING

Test progressively:

```text
1
2
3
5
8
10
```

For each level record:

```text
Claims/hour
Average Duration
CPU
Memory
Browser Count
Redis Latency
DB Connections
Queue Latency
Scraper Failures
CAPTCHA Failures
Timeouts
Retries
Guidewire Failures
Email Failures
Success Rate
```

Determine the real safe maximum.

---

# 56. AUTOMATIC QUEUE PROCESSING

Previous runtime logs showed:

```text
Automatic queue runner is OFF.
Halting sequential queue advancement.
```

This MUST be investigated and fixed.

Verify:

```text
Redis
 ↓
Celery Worker
 ↓
Celery Beat
 ↓
Queue
 ↓
Task
 ↓
RPA
 ↓
Database
```

The application must correctly honor its configured Auto Queue setting.

If Auto Queue is intended to be enabled:

- enable it;
- persist configuration;
- verify Beat scheduling;
- verify worker receives task;
- verify task executes;
- verify queue advances;
- verify next claim starts.

---

# 57. OPTION [7] — FULL DIAGNOSTICS

Option [7] must run comprehensive diagnostics.

Do not only run:

```text
Pytest
Ruff
TypeScript
```

Also validate:

```text
Python
Python 3.14.7
Node
NPM
Frontend
Backend
Database
Redis
Celery
Celery Beat
Flower
MailDev Web
MailDev SMTP
Docker
Ports
Environment
Configuration
Browser Runtime
Anti-Captcha
RPA Mode
RPA Concurrency
Queue
All 8 Scrapers
Filesystem
Exports
Email
Notifications
```

---

# 58. DIAGNOSTIC STATUS MODEL

Every check must return one of:

```text
PASS
WARN
FAIL
SKIPPED
NOT CONFIGURED
DEGRADED
UNKNOWN
```

Do not convert warnings into PASS.

Do not convert failures into WARN merely to make the result look better.

---

# 59. PYTEST UNRAISABLE EXCEPTION WARNING

The previous environment showed:

```text
PytestUnraisableExceptionWarning
Exception ignored while calling deallocator
_proactor_events.py
ValueError: I/O operation on closed pipe
```

Investigate the root cause.

Determine whether related to:

```text
Playwright
Asyncio
Windows Proactor
Browser lifecycle
Test fixtures
Unclosed transport
Pipe cleanup
Process cleanup
Dependency
```

If application/test related:

FIX IT.

If genuinely third-party and unavoidable:

- document it;
- prove no resource leak;
- explain impact;
- identify mitigation.

Do not simply say:

```text
All tests passed
```

while ignoring meaningful warnings.

---

# 60. CELERY DIAGNOSTICS

Option [7] must verify:

```text
Worker registered
Worker heartbeat
Worker responsiveness
Pool
Concurrency
Queues
Task registration
Task execution
Redis connection
Celery Beat
Scheduled tasks
Reserved tasks
Active tasks
Failed tasks
```

Previous inspector failures such as:

```text
registered failed
scheduled failed
conf failed
revoked failed
active failed
reserved failed
stats failed
active_queues failed
```

must be investigated.

Do not hide them.

---

# 61. REAL CELERY TEST TASK

Diagnostics must execute a controlled real test task.

Flow:

```text
Submit Diagnostic Task
 ↓
Redis
 ↓
Celery Worker
 ↓
Task Executes
 ↓
Result Returned
 ↓
Result Verified
```

A worker process existing is NOT sufficient.

---

# 62. OPTION [8] — DOCKER STACK

Option [8] must support:

```text
Start
Stop
Restart
Status
```

Inspect actual Docker Compose.

Verify:

```text
Containers
Networks
Volumes
Ports
Environment
Health Checks
Restart Policies
Database
Redis
Backend
Frontend
Worker
Beat
MailDev
Monitoring
```

---

# 63. DOCKER VS LOCAL MODE

Clearly distinguish:

```text
LOCAL / POWERSHELL MODE
```

from:

```text
DOCKER MODE
```

Never unintentionally run:

```text
Local Redis
+
Docker Redis
```

on the same configured port.

Same for:

```text
PostgreSQL
Backend
Frontend
Celery
MailDev
Flower
```

Provide conflict detection and clear recovery.

---

# 64. OPTION [9] — LIVE SERVICE STATUS MONITOR

Option [9] must be significantly more capable than:

```text
[RUNNING] Service (Port)
```

The current status output may show:

```text
[RUNNING] Frontend Web Application (Port 3000)
[RUNNING] FastAPI Backend & API (Port 8000)
[RUNNING] Celery Flower Monitor (Port 5555)
[RUNNING] MailDev Web Inspector (Port 1080)
[RUNNING] MailDev SMTP Server (Port 1025)
[RUNNING] Redis Queue Broker (Port 6379)
[RUNNING] PostgreSQL Database (Port 5432)
```

This is useful but NOT sufficient.

---

# 65. OPTION [9] SERVICE STATUS MODEL

For every service show:

```text
Service
Process
PID
Port
Protocol
Configured
Expected
Running
Healthy
Response Time
Uptime
Last Heartbeat
Last Error
Dependency Status
```

Use:

```text
RUNNING
HEALTHY
DEGRADED
STOPPED
FAILED
UNKNOWN
NOT CONFIGURED
```

---

# 66. OPTION [9] MUST VERIFY ACTUAL HEALTH

Do not report:

```text
RUNNING
```

because a process exists.

Do not report:

```text
RUNNING
```

because a port is open.

For HTTP:

```text
Connect
 ↓
Call Health Endpoint
 ↓
Validate Response
 ↓
Validate Application
```

For Redis:

```text
Ping
 ↓
Validate Response
```

For PostgreSQL:

```text
Connect
 ↓
Execute lightweight query
 ↓
Validate
```

For Celery:

```text
Worker Heartbeat
 ↓
Worker Registration
 ↓
Queue
 ↓
Diagnostic Task
```

For MailDev:

```text
HTTP/API
SMTP
```

must both be validated.

---

# 67. OPTION [9] CELERY WORKER DISPLAY

Do NOT only show:

```text
Celery Workers: 1 Active
```

Display:

```text
Celery Workers
------------------------------------------------
Worker Instances:       1
Online:                 1
Offline:                0

Worker:
  Name:                 <actual worker>
  PID:                  <PID>
  Pool:                 <actual>
  Concurrency:          <actual>
  Heartbeat:            HEALTHY
  Registered Tasks:     <count>
  Active Tasks:         <count>
  Reserved Tasks:       <count>
  Scheduled Tasks:      <count>
```

---

# 68. OPTION [9] RPA FLEET STATUS

Display separately:

```text
RPA Fleet
------------------------------------------------
Configured Capacity:       10
Effective Capacity:        10
Active Claims:              7
Available Slots:             3
Queued Claims:              23
```

If actual capacity differs:

```text
Configured Capacity:       10
Effective Capacity:         1
Status:                DEGRADED
Reason:
Celery execution pool cannot currently execute
the configured number of parallel claim tasks.
```

This is mandatory.

---

# 69. OPTION [9] SCRAPER FLEET

Display:

```text
Florida
  Broward
  Hillsborough
  Miami-Dade

Texas
  Travis
  Dallas
  Harris JP
  Harris District
  Harris County Clerk
```

Required:

```text
Florida = 3
Texas   = 5
Total   = 8
```

Miami-Dade MUST ALWAYS be Florida.

Never classify Miami-Dade as Texas.

---

# 70. OPTION [9] BROWSER STATUS

Display:

```text
Browser Automation Engine
------------------------------------------------
Selected Browser: Chrome
Mode: Attended
Executable: <path>
Version: <version>
Anti-Captcha: HEALTHY
Extension: HEALTHY
Launch Test: PASS
Automation Test: PASS
```

Also show availability of:

```text
Chromium
Google Chrome
Microsoft Edge
```

without incorrectly implying all three must be selected simultaneously.

---

# 71. OPTION [9] MAILDEV STATUS

Display:

```text
MailDev
------------------------------------------------
Web Inspector:     HEALTHY
HTTP Port:         1080
SMTP Server:       HEALTHY
SMTP Port:         1025
Email Test:        PASS
```

---

# 72. OPTION [9] REDIS STATUS

Display:

```text
Redis
------------------------------------------------
Port:              6379
Connection:        HEALTHY
Ping:              PASS
Latency:           <ms>
Queues:            <count>
```

---

# 73. OPTION [9] DATABASE STATUS

Display:

```text
PostgreSQL
------------------------------------------------
Port:              5432
Connection:        HEALTHY
Query Test:        PASS
Latency:           <ms>
```

---

# 74. OPTION [M] — MAILDEV

Option [M] must:

1. detect MailDev;
2. verify HTTP 1080;
3. verify SMTP 1025;
4. open the browser only if available;
5. otherwise provide a useful error;
6. optionally offer to start MailDev;
7. verify MailDev after startup.

URL:

```text
http://localhost:1080
```

---

# 75. EMAIL TESTING

The current application has a notification email setting.

Verify the complete chain:

```text
Settings
 ↓
Notification Email
 ↓
Backend Configuration
 ↓
Notification Engine
 ↓
Celery
 ↓
SMTP
 ↓
MailDev
 ↓
Email Visible in MailDev
```

The configured recipient must actually be used.

Do not only save the value in the frontend.

---

# 76. EMAIL CONFIGURATION VALIDATION

Verify:

- recipient;
- SMTP host;
- SMTP port;
- sender;
- provider;
- enabled/disabled state;
- notification rules;
- template;
- retry;
- failure handling.

Never log:

```text
Password
SMTP Secret
API Key
Token
Credential
```

---

# 77. EMAIL FAILURE ISOLATION

Email failure must not automatically fail unrelated claim processing.

Example:

```text
Claim Processing = SUCCESS
Email = FAILED
```

must be represented separately.

Implement appropriate retry and notification status.

---

# 78. LOGGING

Every Setup Console operation must generate structured logs.

Capture:

```text
Timestamp
Operation
Service
Command
PID
Port
Exit Code
Duration
Result
Error
Warning
Recovery Action
Correlation ID
```

Never log:

```text
Passwords
Tokens
Secrets
API Keys
Credentials
CAPTCHA secrets
Guidewire credentials
SMTP credentials
```

---

# 79. PROCESS TRACKING

Where possible maintain:

```text
PID
Command Line
Working Directory
Process Owner
Service Identity
Start Time
```

This information must be used for safe lifecycle management.

---

# 80. STARTUP FAILURE HANDLING

If:

```text
Redis = PASS
Backend = PASS
Worker = FAIL
Frontend = PASS
MailDev = FAIL
```

show exactly that.

Do NOT display:

```text
All services started successfully.
```

Allowed states:

```text
STARTED
FAILED
SKIPPED
ALREADY RUNNING
UNHEALTHY
DEGRADED
```

---

# 81. STARTUP RECOVERY

If a mandatory service fails:

1. capture error;
2. identify root cause;
3. attempt safe recovery;
4. retry if appropriate;
5. verify;
6. report final status.

Do not enter infinite restart loops.

---

# 82. SETUP CONSOLE UX

The console must provide:

- clear menu;
- clear status;
- progress;
- error details;
- confirmation;
- cancellation;
- Ctrl+C handling;
- invalid input handling;
- repeated execution handling;
- return-to-menu behavior;
- no false success;
- no unexplained failures.

---

# 83. OPTION COMBINATION TESTING

Do not test only individual options.

Test:

## Sequence A — Clean Startup

```text
[2] Stop
→ [9] Status
→ [4] Install
→ [7] Diagnostics
→ [1] Start
→ [9] Status
→ [M] MailDev
```

## Sequence B — Clean Rebuild

```text
[2] Stop
→ [5] Purge
→ [4] Install
→ [7] Diagnostics
→ [1] Start
→ [9] Status
```

## Sequence C — Attended

```text
[6] Attended
→ [1] Start
→ Run real RPA
→ [9] Monitor
→ [2] Stop
```

## Sequence D — Unattended

```text
[6] Unattended
→ [1] Start
→ Run real RPA
→ [9] Monitor
→ [2] Stop
```

## Sequence E — MailDev

```text
[1] Start
→ [9] Verify MailDev
→ [M]
→ Send Test Email
→ Verify Email
→ [2] Stop
→ [9] Verify 1080/1025 free
```

## Sequence F — Docker

```text
[2] Stop Local
→ [8] Docker Start
→ [9] Verify
→ [8] Docker Stop
→ [9] Verify
```

## Sequence G — Cleanup

```text
[3] Dry Run
→ Review
→ Cancel
→ [3] Dry Run
→ Confirm
→ Execute
→ Reconcile
```

---

# 84. CONCURRENCY TEST SEQUENCES

Test:

```text
Concurrency 1
→ real queue
→ verify 1 active claim
```

Then:

```text
Concurrency 2
→ verify maximum 2 active claims
```

Then:

```text
Concurrency 5
```

Then:

```text
Concurrency 10
```

At each level verify actual execution, not configuration only.

---

# 85. CLEANUP TEST MATRIX

Mandatory:

| Test | Selection | Time Scope | Expected |
|---|---|---|---|
| C01 | One category | Current Month | Only selected data deleted |
| C02 | Multiple categories | Current Month | All selected deleted |
| C03 | All operational | Current Month | All eligible operational data deleted |
| C04 | One category | Last 1 Month | Correct filtering |
| C05 | One category | Last 3 Months | Correct filtering |
| C06 | Multiple | Last 6 Months | Correct filtering |
| C07 | Custom range | Custom | Exact range |
| C08 | Before date | Date | Correct boundary |
| C09 | After date | Date | Correct boundary |
| C10 | No matching | Any | Safe zero result |
| C11 | Repeat | Same range | Idempotent |
| C12 | Cancel | Any | Nothing deleted |
| C13 | Invalid | Any | Validation |
| C14 | Partial failure | Any | Safe rollback/recovery |
| C15 | Large data | Any | Batched/performance safe |
| C16 | Dashboard | Any | Reconciled |
| C17 | Notification History | Any | Actually deleted |
| C18 | Telemetry | Any | Actually deleted |
| C19 | Queue | Any | Actually deleted |
| C20 | Scraped Cases | Any | Actually deleted |

---

# 86. DATE BOUNDARY TESTING

Test:

```text
Start
End
One unit before
One unit after
```

Example:

```text
Start = 09/01/2026 00:00:00
End   = 09/05/2026 23:59:59.999
```

Verify records exactly on both boundaries.

Test timezone and DST where applicable.

---

# 87. PERFORMANCE

Do not load millions of records into Python memory.

Prefer:

```text
Database-side filtering
Indexed timestamps
Batch deletion
Efficient queries
Transactions
Asynchronous long-running jobs
Progress tracking
```

For long operations:

```text
QUEUED
 ↓
RUNNING
 ↓
PROGRESS
 ↓
COMPLETED
```

---

# 88. SECURITY

All destructive operations require authorization.

Protect against:

- unauthorized cleanup;
- arbitrary SQL;
- path traversal;
- deletion outside approved directories;
- credential exposure;
- unsafe process killing;
- secret logging.

Never use unsafe raw SQL constructed directly from user input.

---

# 89. AUTOMATED TESTING

Create/repair automated tests for:

## Setup

- menu;
- option parsing;
- service registry;
- startup;
- shutdown;
- status;
- process tracking;
- ports;
- recovery.

## Dependencies

- Python;
- NPM;
- Playwright;
- browser detection;
- browser factory;
- Anti-Captcha.

## Celery

- worker;
- Beat;
- Redis;
- queues;
- task execution;
- concurrency.

## Cleanup

- category selection;
- multi-select;
- current month;
- date ranges;
- dry-run;
- confirmation;
- cancellation;
- deletion;
- relationships;
- rollback;
- idempotency;
- reconciliation.

## Docker

- start;
- stop;
- restart;
- status;
- conflicts.

## MailDev

- startup;
- shutdown;
- HTTP;
- SMTP;
- email delivery.

---

# 90. REAL-WORLD VALIDATION

Unit tests are NOT enough.

Actually execute the Setup Console.

Run:

```text
[1]
[2]
[3]
[4]
[5]
[6]
[7]
[8]
[9]
[M]
[0]
```

Verify the real-world outcome.

---

# 91. NO FALSE SUCCESS

These are NOT sufficient evidence:

```text
PowerShell exit code 0
```

```text
Process exists
```

```text
Port is open
```

```text
API returned 200
```

```text
Frontend displays zero rows
```

```text
Pytest passed
```

Each must be followed by actual behavioral validation where applicable.

---

# 92. FULL RPA VALIDATION

The final test must validate:

```text
Real Claim
 ↓
Real Queue
 ↓
Real Redis
 ↓
Real Celery
 ↓
Real RPA Orchestrator
 ↓
Real Browser
 ↓
Real Anti-Captcha
 ↓
Real County Portal
 ↓
Real Search
 ↓
Real Result Extraction
 ↓
Real Pagination
 ↓
Real Database Storage
 ↓
Real Fuzzy Match
 ↓
Real Guidewire
 ↓
Real Notification
 ↓
Real Final Status
```

No compile-only acceptance.

---

# 93. EIGHT COUNTY SCRAPER VALIDATION

Exactly:

## Florida — 3

```text
1. Broward
2. Hillsborough
3. Miami-Dade
```

## Texas — 5

```text
4. Travis
5. Dallas
6. Harris JP
7. Harris District
8. Harris County Clerk
```

Total:

```text
8
```

Miami-Dade MUST remain Florida.

---

# 94. BROWSER MATRIX FOR RPA

For the configured browser test:

```text
Chromium
Google Chrome
Microsoft Edge
```

where installed/configured.

For each:

```text
Browser Detection
 ↓
Launch
 ↓
Anti-Captcha
 ↓
Attended
 ↓
Unattended
 ↓
County Navigation
 ↓
Extraction
 ↓
Clean Shutdown
```

Do not silently fall back to another browser.

---

# 95. REGRESSION REQUIREMENT

After modifying Setup Console, rerun:

```text
Backend Tests
Frontend Tests
TypeScript
Ruff
ESLint
Build
Database Tests
Redis Tests
Celery Tests
RPA Tests
Browser Tests
Email Tests
Export Tests
Docker Tests
Setup Tests
```

Also test existing application functionality.

---

# 96. COMPLETE ENVIRONMENT RECOVERY TEST

Perform:

```text
[2] Stop
 ↓
[5] Purge Dependencies
 ↓
[4] Install Dependencies
 ↓
[7] Diagnostics
 ↓
[1] Start
 ↓
[9] Status
 ↓
Real RPA
```

The system must recover successfully.

---

# 97. DESTRUCTION / RECREATION TEST

Where safe and appropriate, validate that generated runtime state can be removed and recreated without losing:

```text
Source
Configuration
Database
Secrets
RPA settings
Browser configuration
Anti-Captcha extension
Documentation
Tests
```

---

# 98. FINAL SERVICE STATUS REPORT

The final Option [9] output should be significantly more informative than:

```text
[RUNNING] Frontend
[RUNNING] Backend
[RUNNING] Flower
[RUNNING] MailDev
[RUNNING] Redis
[RUNNING] PostgreSQL
```

It should expose enough information to answer:

```text
Is the service running?
Is it healthy?
Is the correct process running?
Is the correct port being used?
Is the dependency healthy?
Is Celery actually working?
Is the queue working?
Can RPA execute?
How many claims can actually run?
Which browser is selected?
Is Anti-Captcha working?
Is MailDev working?
```

---

# 99. FINAL VALIDATION MATRIX

Produce:

| Component | Tested | Real Execution | Passed | Recovery Tested | Evidence |
|---|---:|---:|---:|---:|---|
| [1] Start | | | | | |
| [2] Stop | | | | | |
| [3] Cleanup | | | | | |
| [4] Dependencies | | | | | |
| [5] Purge | | | | | |
| [6] RPA Mode | | | | | |
| [7] Diagnostics | | | | | |
| [8] Docker | | | | | |
| [9] Status | | | | | |
| [M] MailDev | | | | | |
| Celery Worker | | | | | |
| Celery Beat | | | | | |
| Redis | | | | | |
| PostgreSQL | | | | | |
| Browser Engine | | | | | |
| Anti-Captcha | | | | | |
| RPA Concurrency | | | | | |
| 8 County Scrapers | | | | | |
| Email | | | | | |

---

# 100. REQUIRED FINAL REPORT

At the end provide:

## A. Root Causes

```text
Issue ID
Component
Problem
Root Cause
Impact
Fix
Validation
Result
```

## B. Files Changed

List:

```text
File
Purpose
Change
Reason
```

## C. Setup Console Results

```text
[1] PASS/FAIL
[2] PASS/FAIL
[3] PASS/FAIL
[4] PASS/FAIL
[5] PASS/FAIL
[6] PASS/FAIL
[7] PASS/FAIL
[8] PASS/FAIL
[9] PASS/FAIL
[M] PASS/FAIL
```

## D. Service Results

```text
Frontend
Backend
Celery Worker
Celery Beat
Redis
PostgreSQL
Flower
MailDev Web
MailDev SMTP
RPA Engine
Browser
Anti-Captcha
```

## E. Browser Results

```text
Chromium
Google Chrome
Microsoft Edge
```

For each:

```text
Detected
Version
Executable
Launch
Automation
Extension
Attended
Unattended
Final
```

## F. Celery Results

Show:

```text
Worker Instances
Pool
Concurrency
Queues
Heartbeat
Active Tasks
Reserved Tasks
Scheduled Tasks
Diagnostic Task
Effective Capacity
```

## G. RPA Concurrency Results

Show:

```text
Configured
Actual Effective
1x
2x
3x
5x
8x
10x
```

with performance metrics.

## H. Cleanup Results

Show:

```text
Category
Selected
Eligible
Deleted
Remaining
Expected Remaining
Mismatch
```

## I. Notification Results

Show:

```text
Notification
Delivery
Retry
MailDev
SMTP
Recipient
Template
Final Result
```

Do not expose secrets.

## J. Test Results

Include:

```text
Pytest
Ruff
TypeScript
ESLint
Build
Integration
Celery
Redis
Database
Docker
Browser
RPA
Email
Cleanup
Setup
```

## K. Warnings

Every remaining warning must be explained.

Never hide warnings.

---

# 101. EVIDENCE REQUIREMENT

Provide actual evidence:

```text
Console Output
Logs
Process IDs
Ports
Health Responses
Celery Worker Evidence
Redis Evidence
Database Evidence
Browser Evidence
Anti-Captcha Evidence
Queue Evidence
RPA Evidence
Email Evidence
MailDev Evidence
Cleanup Evidence
Screenshots where useful
```

For real RPA testing, provide evidence that the browser actually launched and automation actually executed.

---

# 102. FINAL DEFINITION OF DONE

The implementation is complete ONLY when:

### Setup Console

- [ ] [1] works
- [ ] [2] works
- [ ] [3] works
- [ ] [4] works
- [ ] [5] works
- [ ] [6] works
- [ ] [7] works
- [ ] [8] works
- [ ] [9] works
- [ ] [M] works

### Services

- [ ] Frontend
- [ ] Backend
- [ ] Redis
- [ ] PostgreSQL
- [ ] Celery Worker
- [ ] Celery Beat
- [ ] Flower
- [ ] MailDev Web
- [ ] MailDev SMTP

### Browser

- [ ] Chromium supported
- [ ] Google Chrome supported
- [ ] Microsoft Edge supported
- [ ] Browser selection is configuration-driven
- [ ] Central browser factory works
- [ ] Anti-Captcha works
- [ ] Dynamic extension path works

### RPA

- [ ] Attended works
- [ ] Unattended works
- [ ] Mode switching works
- [ ] 8 scrapers work
- [ ] Florida = 3
- [ ] Texas = 5
- [ ] Miami-Dade = Florida
- [ ] Queue processing works
- [ ] Auto Queue works
- [ ] Manual queue works
- [ ] Claim failure isolation works

### Celery

- [ ] Worker is genuinely connected
- [ ] Beat is genuinely connected
- [ ] Redis is healthy
- [ ] Queues are healthy
- [ ] Diagnostic task executes
- [ ] Actual effective concurrency is known
- [ ] Configured concurrency is not falsely represented

### Parallel RPA

- [ ] 1x tested
- [ ] 2x tested
- [ ] 3x tested
- [ ] 5x tested
- [ ] 8x tested
- [ ] 10x tested
- [ ] Actual parallel claim count verified
- [ ] Resource utilization measured
- [ ] No uncontrolled browser explosion

### Cleanup

- [ ] Multiple categories
- [ ] Select All
- [ ] Select None
- [ ] Current Month
- [ ] Days
- [ ] Weeks
- [ ] Months
- [ ] Years
- [ ] Custom range
- [ ] Before date
- [ ] After date
- [ ] Dry-run
- [ ] Confirmation
- [ ] Cancellation
- [ ] Referential integrity
- [ ] Rollback
- [ ] Idempotency
- [ ] Dashboard reconciliation
- [ ] Notification reconciliation
- [ ] Queue reconciliation
- [ ] Scraper reconciliation
- [ ] Telemetry reconciliation
- [ ] Cache invalidation
- [ ] Audit history

### Dependencies

- [ ] Python 3.14.7
- [ ] Backend dependencies
- [ ] Frontend dependencies
- [ ] NPM dependencies
- [ ] Browser dependencies
- [ ] No unnecessary browser installation
- [ ] No repeated unnecessary installation
- [ ] Installation warnings investigated
- [ ] Safe purge/rebuild

### Diagnostics

- [ ] No false PASS
- [ ] Meaningful warnings
- [ ] Meaningful failures
- [ ] Real Celery task test
- [ ] Real browser test
- [ ] Real MailDev test
- [ ] Real database test
- [ ] Real Redis test

### Docker

- [ ] Start
- [ ] Stop
- [ ] Restart
- [ ] Status
- [ ] Health
- [ ] Persistence
- [ ] Local/Docker conflict prevention

---

# 103. ABSOLUTE NO-FALSE-PASS RULE

NEVER report:

```text
SUCCESS
```

just because:

```text
PowerShell command exited 0
```

NEVER report:

```text
Celery Healthy
```

because a Python process exists.

NEVER report:

```text
RPA Concurrency 10
```

because the setting contains the value 10.

NEVER report:

```text
Browser Supported
```

because an executable exists.

NEVER report:

```text
MailDev Healthy
```

because port 1080 is open.

NEVER report:

```text
Cleanup Completed
```

while eligible records remain.

NEVER report:

```text
All Tests Passed
```

while meaningful warnings/failures remain unexplained.

---

# 104. FINAL ENGINEERING RULE

The objective is NOT:

```text
Make the Setup Console look correct.
```

The objective is:

```text
Make the Setup Console actually control
and validate the complete UAIC application.
```

The final architecture must provide:

```text
                    SETUP CONSOLE
                         │
       ┌─────────────────┼──────────────────┐
       │                 │                  │
    Services          RPA Engine         Data
       │                 │                  │
       ▼                 ▼                  ▼
Frontend              Browser            Database
Backend               Anti-Captcha       Cleanup
Redis                 Scrapers            Reconciliation
PostgreSQL             Queue              Audit
Celery                 Fuzzy Match
Beat                   Guidewire
MailDev                Notifications
Flower
Docker
```

The complete RPA execution path must be:

```text
INPUT
 ↓
QUEUE
 ↓
REDIS
 ↓
CELERY
 ↓
RPA ORCHESTRATOR
 ↓
CONFIGURED BROWSER
 ↓
ANTI-CAPTCHA
 ↓
COUNTY PORTAL
 ↓
SEARCH
 ↓
EXTRACTION
 ↓
DATABASE
 ↓
FUZZY MATCH
 ↓
GUIDEWIRE
 ↓
NOTIFICATION
 ↓
FINAL STATUS
```

The complete Setup Console lifecycle must be:

```text
INSTALL
 ↓
CONFIGURE
 ↓
START
 ↓
VERIFY
 ↓
EXECUTE
 ↓
MONITOR
 ↓
RECOVER
 ↓
STOP
 ↓
CLEANUP
 ↓
REBUILD
 ↓
VERIFY AGAIN
```

Do not stop after implementation.

If a test fails:

```text
Find Root Cause
 ↓
Fix
 ↓
Retest
 ↓
Regression Test
 ↓
Repeat
```

Continue until the complete system is genuinely functional.

> **The final acceptance criterion is real-world behavior, not code existence, command success, process existence, open ports, API status codes, or test counts.**
>
> **Every supported option, service, browser, queue, concurrency level, cleanup operation, notification path and RPA workflow must be actually executed and verified before being reported as PASS.**
