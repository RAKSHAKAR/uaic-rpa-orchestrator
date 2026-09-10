# COMPLETE SETUP CONSOLE VALIDATION, TESTING & ENTERPRISE DATA CLEANUP

You are working on the **existing UAIC Claim & RPA Orchestrator** solution.

Do NOT treat this as a new implementation.

You must deeply inspect the existing implementation, test every action from **[1] through [9]**, identify all broken/incomplete behavior, fix it, and then retest everything end-to-end.

The goal is not merely to make the menu display correctly.

The goal is:

> **Every action [1]–[9] must be fully functional, production-ready, flexible, safe, enterprise-grade, and actually tested.**

Do not claim an action is working because the command executes successfully. Verify the actual result.

---

# 1. CURRENT OPERATIONS CONSOLE

The current console is:

```text
    _    _         _____ _____    ____           _               _             _
   | |  | |  /\   |_   _/ ____|  / __ \         | |             | |           | |
   | |  | | /  \    | || |      | |  | |_ __ ___| |__   ___  ___| |_ _ __ __ _| |_ ___  _ __
   | |  | |/ /\ \   | || |      | |  | | '__/ __| '_ \ / _ \/ __| __| '__/ _  | __/ _ \| '__|
   | |__| / ____ \ _| || |____| | |__| | | | (__| | | |  __/\__ \ |_| | | (_| | || (_) | |
    \____/_/    \_\_____|_____|  \____/|_|  \___|_| |_|\___||___/\__|_|  \__,_|\__\___|_|


                  Enterprise Operations & Orchestration Console

 Active RPA Engine Mode: [Attended (GUI)]
 Log File: C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\setup.log

=======================================================================

 [1] Start All Application Services (Interactive Launch with Mode Select)
 [2] Stop / Kill All Running Services (Ports 3000, 8000, 5555, Celery)
 [3] Clean Run History, Logs & Scraper Caches
 [4] Install / Update Dependencies (Python venv, Playwright, NPM)
 [5] Purge / Delete All Dependency Folders (.venv, node_modules, .next)
 [6] Configure RPA Execution Mode (Attended GUI vs Unattended Headless)
 [7] Run Full Diagnostics & Test Suite (Pytest, Ruff, TypeScript)
 [8] Docker Stack Deployment (Start/Stop Containerized Stack)
 [9] Live Service Status Monitor (Check listening ports & health)

 [0] Exit Console
```

Do not remove or weaken any of these options.

Improve them where required.

---

# 2. FIRST: FULL EXISTING-SOLUTION AUDIT

Before modifying anything:

1. Inspect the complete setup/operations console implementation.
2. Inspect all PowerShell scripts.
3. Inspect Python backend.
4. Inspect Next.js frontend.
5. Inspect database models and migrations.
6. Inspect Celery configuration.
7. Inspect Redis usage.
8. Inspect queue tables.
9. Inspect scraper result tables.
10. Inspect notification tables.
11. Inspect telemetry tables.
12. Inspect dashboard aggregation/query logic.
13. Inspect logs and cache directories.
14. Inspect Docker configuration.
15. Inspect environment/configuration handling.
16. Inspect test suite.
17. Inspect all cleanup/delete/reset functionality.
18. Inspect all relationships and foreign keys between operational entities.

Do not assume that because a record disappears from one screen, it has actually been deleted.

---

# 3. CRITICAL ISSUE: CLEANUP IS CURRENTLY INCOMPLETE

I am specifically seeing a problem where cleanup appears to delete some records, but data remains elsewhere.

For example:

- Outbound Notification Delivery History still contains data.
- Dashboard still displays old data.
- Other operational/history tables still contain records.
- Scraper-related data can remain.
- Telemetry can remain.
- Queue/history information can remain.
- Cached/generated information can remain.
- Aggregated/statistical information can remain.

This is NOT acceptable.

The cleanup operation must be redesigned as a **complete enterprise data-retention/cleanup engine**.

---

# 4. OPTION [3] MUST BECOME A REAL ENTERPRISE CLEANUP ENGINE

Change:

```text
[3] Clean Run History, Logs & Scraper Caches
```

to a flexible cleanup workflow while preserving the option number.

Recommended display:

```text
[3] Enterprise Data Cleanup & Retention
```

The user must be able to control:

### A. WHAT DATA TO DELETE

Never automatically delete everything.

The system must first ask the user what type(s) of data should be deleted.

Provide selectable categories.

At minimum support:

```text
[1] Claim / Claim Automation Data
[2] Work Queue Data
[3] Scraped Court Case Data
[4] Fuzzy Match / Matching Data
[5] Guidewire Activity / Integration Data
[6] Outbound Notification Data
[7] Notification Delivery History
[8] Stage Execution Telemetry
[9] Bot / Scraper Execution History
[10] Dashboard / Analytics Data
[11] Application Run History
[12] Application Logs
[13] Scraper Logs
[14] Temporary Files / Caches
[15] Generated Export Files
[16] Redis / Temporary Runtime Data
[17] All Operational Data
[18] All Supported Data Categories
```

The exact list must be generated from the actual application's data model.

Do NOT invent categories that do not exist.

If additional operational data stores are discovered during the audit, include them.

---

# 5. MULTI-SELECT DATA CATEGORIES

The user must be able to select multiple categories in one operation.

For example:

```text
Select data to delete:

[X] Claim / Claim Automation Data
[X] Work Queue Data
[X] Scraped Court Case Data
[X] Fuzzy Match Data
[X] Guidewire Activity Data
[X] Notification Data
[X] Notification Delivery History
[X] Execution Telemetry
[X] Bot Execution History
[X] Dashboard / Analytics Data
[X] Application Logs
[X] Scraper Logs
[X] Temporary Files / Caches
[ ] Generated Exports
```

The user must also have:

```text
[A] Select All
[N] Select None
```

Therefore the user can perform **all cleanup operations in one go**.

---

# 6. TIME-BASED CLEANUP IS MANDATORY

The cleanup must NOT simply mean:

```text
delete everything
```

The user must provide the desired retention/deletion period.

Support flexible time units.

At minimum:

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
Custom Date Range
Before Specific Date
After Specific Date
```

Examples:

```text
Delete data older than:
3 months
```

or:

```text
Delete data older than:
6 months
```

or:

```text
Delete data from:
01/01/2026
to:
03/31/2026
```

or:

```text
Delete data from the current month only:
09/01/2026 → 09/05/2026
```

---

# 7. IMPORTANT: "CURRENT MONTH" MUST BE SUPPORTED

The user specifically requires cleanup based on the **current month**.

Implement explicit support for:

```text
Current Month
```

The system must dynamically determine the current calendar month.

Do NOT hardcode September 2026.

For example:

If the current date is:

```text
September 5, 2026
```

then:

```text
Current Month =
September 1, 2026 00:00:00
through
September 5, 2026/current time
```

When the application runs in another month, the range must automatically change.

Timezone must be configurable and must use the application's configured timezone.

---

# 8. EXAMPLE USER EXPERIENCE

Option [3] should behave approximately like:

```text
=======================================================================
                 ENTERPRISE DATA CLEANUP
=======================================================================

Select Data Categories:

 [1] Claim / Claim Automation Data
 [2] Work Queue Data
 [3] Scraped Court Case Data
 [4] Fuzzy Match Data
 [5] Guidewire Activity Data
 [6] Outbound Notification Data
 [7] Notification Delivery History
 [8] Stage Execution Telemetry
 [9] Bot / Scraper Execution History
[10] Dashboard / Analytics Data
[11] Application Run History
[12] Application Logs
[13] Scraper Logs
[14] Temporary Files / Caches
[15] Generated Export Files
[16] Redis Runtime Data
[17] All Operational Data

Enter selection(s):
> 1,2,3,6,7,8,9,10

=======================================================================

Select Time Scope:

 [1] Current Month
 [2] Previous Month
 [3] Last N Days
 [4] Last N Weeks
 [5] Last N Months
 [6] Last N Years
 [7] Custom Date Range
 [8] Before Specific Date

Enter selection:
> 1

=======================================================================

Current Month:
09/01/2026 00:00:00
through
09/05/2026 19:09:00

=======================================================================
```

Then show a **dry-run preview** before deleting anything.

---

# 9. MANDATORY DRY-RUN PREVIEW

Before deletion, calculate exactly what will be affected.

Example:

```text
=======================================================================
                    CLEANUP PREVIEW
=======================================================================

Time Range:
09/01/2026 00:00:00
09/05/2026 19:09:00

Selected Data:

Claims                         12
Work Queue Items               18
Scraped Court Cases            64
Fuzzy Match Records            64
Guidewire Activities            8
Outbound Notifications         25
Notification Deliveries        25
Execution Telemetry           182
Bot Execution History          48
Dashboard Metrics              91
Application Logs              143
Scraper Logs                   88
Temporary Cache Files          37

Total database records:       769
Total files:                  268

=======================================================================

WARNING:
This operation will permanently delete the selected data.

Continue?

[Y] Yes
[N] No
```

Never delete before confirmation.

---

# 10. CLEANUP MUST BE RELATIONSHIP-AWARE

This is critical.

Do not simply delete parent records and leave child/orphan records behind.

Analyze the complete data relationship graph.

For example:

```text
Claim
 ├── Claim Automation
 ├── Work Queue
 ├── Scraped Court Cases
 ├── Fuzzy Match
 ├── Guidewire Activity
 ├── Notifications
 │    └── Notification Delivery History
 ├── Execution Telemetry
 ├── Bot Execution History
 └── Dashboard/Analytics records
```

If a selected parent entity is deleted, determine what dependent data must also be removed according to the application's data-retention rules.

Use:

- Foreign keys.
- Cascade rules where appropriate.
- Explicit dependency deletion where required.
- Referential integrity checks.
- Transactional deletion.

Never leave orphan records.

---

# 11. DASHBOARD DATA MUST BE HANDLED CORRECTLY

The current problem where the Dashboard still displays old data must be fixed.

Determine whether dashboard information is:

1. Persisted database data.
2. Materialized/aggregated data.
3. Cached data.
4. Calculated dynamically.
5. Redis-backed.
6. Frontend cached.
7. API cached.

Implement the correct cleanup/invalidation mechanism.

After cleanup:

- refresh Dashboard API data;
- invalidate applicable caches;
- invalidate Redis cache entries;
- invalidate frontend query caches where applicable;
- recalculate materialized aggregates where applicable.

The Dashboard must reflect the actual remaining database state.

Do NOT simply hide records from the Dashboard.

---

# 12. OUTBOUND NOTIFICATION DELIVERY HISTORY MUST BE CLEANED

This is a mandatory acceptance requirement.

If:

```text
Notification Delivery History
```

is selected and records fall inside the requested cleanup range, those records must actually be removed.

Verify:

```text
Database
API
Backend queries
Frontend table
Dashboard metrics
Notification history
Related notification records
```

After cleanup, refresh the application and verify the records are gone.

Do not accept:

```text
deleted from one API endpoint
```

as proof.

---

# 13. NOTIFICATION CLEANUP MUST BE RELATIONSHIP-AWARE

Inspect all notification entities, including but not limited to:

- Notification records.
- Notification templates if they are runtime-generated.
- Notification events.
- Notification deliveries.
- Delivery attempts.
- Delivery history.
- Failed deliveries.
- Retry records.
- Email records.
- SMS records.
- WhatsApp records.
- In-app notification records.
- Webhook notification records.

Do NOT delete configuration/templates that are supposed to be permanent configuration unless the user explicitly selects them.

Separate:

```text
Configuration
```

from:

```text
Operational History
```

---

# 14. CONFIGURATION MUST NEVER BE ACCIDENTALLY DELETED

The cleanup operation must never accidentally remove:

- System configuration.
- User configuration.
- AI provider configuration.
- SMTP configuration.
- Notification provider configuration.
- RPA configuration.
- County configuration.
- Scraper configuration.
- Application secrets.
- Authentication configuration.
- Subscription configuration.
- Branding/theme configuration.

unless the user explicitly selects a supported configuration category.

Operational cleanup must remain safe.

---

# 15. CLEANUP TRANSACTION SAFETY

Database cleanup must be implemented safely.

Where supported:

```text
BEGIN TRANSACTION
    validate
    calculate affected records
    delete dependencies
    delete selected records
    validate referential integrity
COMMIT
```

If an unrecoverable error occurs:

```text
ROLLBACK
```

Do not leave half-deleted data.

For very large datasets, implement controlled batching while maintaining consistency.

---

# 16. CLEANUP MUST BE IDEMPOTENT

Running the same cleanup twice must not cause errors.

Example:

First run:

```text
Deleted:
Claims = 10
Notifications = 20
Telemetry = 100
```

Second identical run:

```text
Deleted:
Claims = 0
Notifications = 0
Telemetry = 0
```

It must complete successfully.

---

# 17. CLEANUP RESULT REPORT

After completion, display:

```text
=======================================================================
                  CLEANUP COMPLETED
=======================================================================

Cleanup ID:
<UUID>

Started:
09/05/2026 19:10:01

Completed:
09/05/2026 19:10:08

Time Scope:
Current Month

Date Range:
09/01/2026 → 09/05/2026

Records Deleted:

Claims                         12
Work Queue Items               18
Scraped Court Cases            64
Fuzzy Match Records            64
Guidewire Activities            8
Outbound Notifications         25
Notification Deliveries        25
Execution Telemetry           182
Bot Execution History          48
Dashboard Metrics              91

Files Deleted:
268

Redis/Caches Invalidated:
Yes

Referential Integrity:
PASS

Dashboard Reconciliation:
PASS

Notification History Reconciliation:
PASS

Overall:
SUCCESS
=======================================================================
```

Persist an audit record for the cleanup itself.

The cleanup audit record must NOT be deleted by the cleanup operation currently executing.

---

# 18. CLEANUP AUDIT HISTORY

Create/maintain an enterprise cleanup audit trail.

Record:

- Cleanup ID.
- User/operator.
- Start time.
- End time.
- Requested categories.
- Time range.
- Records discovered.
- Records deleted.
- Files deleted.
- Cache entries invalidated.
- Errors.
- Warnings.
- Rollback status.
- Final status.
- Correlation ID.

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

Provide enough information to troubleshoot exactly what happened.

---

# 19. OPTION [1] — START ALL SERVICES

Test this completely.

Verify:

- frontend starts;
- backend starts;
- Redis starts/available;
- Celery worker starts;
- Celery Beat starts where configured;
- monitoring service starts;
- required ports are available;
- health endpoints return healthy;
- no duplicate processes are accidentally created;
- logs are written correctly;
- startup failures are reported clearly.

Test both:

```text
Attended GUI
Unattended Headless
```

where applicable.

---

# 20. OPTION [2] — STOP / KILL ALL SERVICES

Test:

```text
Port 3000
Port 8000
Port 5555
Celery
Redis-dependent workers
Beat
Monitoring
```

Verify that processes are actually terminated.

Do not only kill processes by a brittle process-name assumption.

After stopping:

```text
3000 = free
8000 = free
5555 = free
Celery worker = stopped
Beat = stopped
```

Then verify Option [1] can start everything again.

---

# 21. OPTION [4] — INSTALL / UPDATE DEPENDENCIES

Test the complete process.

Must support:

- Python 3.14.7.
- Virtual environment.
- Backend dependencies.
- Frontend dependencies.
- NPM dependencies.
- Playwright requirements where actually required.
- System Google Chrome requirement for attended/unattended browser automation.

IMPORTANT:

Do NOT blindly install bundled Playwright Chromium if the production automation requires **system Google Chrome**.

Verify dependency installation is:

- repeatable;
- idempotent;
- version-aware;
- error-aware;
- logged.

---

# 22. OPTION [5] — PURGE DEPENDENCY FOLDERS

Test:

```text
.venv
node_modules
.next
```

and any other generated dependency/build folders discovered during audit.

Do not delete:

- source code;
- configuration;
- database;
- user data;
- secrets;
- required extensions;
- Anti-Captcha extension;
- automation assets;
- Power Automate reference artifacts.

Before deleting, display exactly what will be removed.

Then verify Option [4] can rebuild the environment successfully.

---

# 23. OPTION [6] — RPA EXECUTION MODE

Fully test:

```text
Attended (GUI)
Unattended (Headless)
```

Attended mode must visibly launch and control the actual browser.

Use the configured **system Google Chrome**.

Do not silently fall back to bundled Chromium.

Verify:

```text
Mode selected
↓
Configuration persisted
↓
Worker reads configuration
↓
Scraper receives configuration
↓
Browser launches correctly
↓
Automation executes correctly
```

Then repeat the same workflow in unattended mode.

Attended success must not introduce assumptions that break unattended execution.

---

# 24. OPTION [7] — FULL DIAGNOSTICS

Test all diagnostics.

At minimum:

```text
Python
Python 3.14.7
Node/NPM
TypeScript
Ruff
Pytest
Database
Redis
Celery
Celery Beat
Frontend
Backend
Environment
Google Chrome
Anti-Captcha extension
Filesystem
Ports
Docker
Configuration
```

Diagnostics must distinguish:

```text
PASS
WARN
FAIL
SKIPPED
NOT CONFIGURED
```

Do not report a false PASS.

---

# 25. OPTION [8] — DOCKER STACK

Test both:

```text
Start
Stop
Restart
Status
```

Verify:

- containers start;
- health checks work;
- dependencies connect;
- application services communicate;
- ports are correct;
- data persistence works;
- shutdown is clean.

Do not allow Docker configuration to silently conflict with local development configuration.

---

# 26. OPTION [9] — LIVE SERVICE STATUS MONITOR

The monitor must show real status.

At minimum:

```text
Frontend
Backend
Redis
Celery Worker
Celery Beat
Monitoring
Database
Docker
RPA Engine
Chrome
```

Show:

```text
RUNNING
STOPPED
DEGRADED
FAILED
UNKNOWN
```

Include:

- PID where applicable;
- port;
- health endpoint;
- uptime;
- last heartbeat;
- worker state;
- queue state;
- RPA mode.

Do not show RUNNING merely because a process exists.

Perform actual health checks.

---

# 27. TEST ALL OPTIONS IN COMBINATION

Do not test options only individually.

Test realistic sequences:

### Scenario A

```text
[2] Stop
↓
[1] Start
↓
[9] Monitor
↓
[7] Diagnostics
```

### Scenario B

```text
[5] Purge
↓
[4] Install
↓
[7] Diagnostics
↓
[1] Start
```

### Scenario C

```text
[6] Attended
↓
[1] Start
↓
Run automation
↓
[9] Monitor
```

### Scenario D

```text
[6] Unattended
↓
[1] Start
↓
Run automation
↓
[9] Monitor
```

### Scenario E

```text
[3] Cleanup
↓
Dashboard
↓
Notification History
↓
Queue
↓
Scraped Cases
↓
Telemetry
```

Verify that all affected data is actually gone.

---

# 28. CLEANUP TEST MATRIX

Mandatory tests:

| Test | Data Selection | Time Range | Expected |
|---|---|---|---|
| C01 | One category | Current Month | Only matching data removed |
| C02 | Multiple categories | Current Month | All selected data removed |
| C03 | All categories | Current Month | All eligible operational data removed |
| C04 | One category | Last 1 Month | Correct date filtering |
| C05 | One category | Last 3 Months | Correct date filtering |
| C06 | Multiple categories | Last 6 Months | Correct date filtering |
| C07 | Custom date range | Custom | Exact range respected |
| C08 | Before date | Custom | Correct boundary |
| C09 | After date | Custom | Correct boundary |
| C10 | No matching data | Any | Safe zero-result operation |
| C11 | Repeat cleanup | Same range | Idempotent |
| C12 | Cancel | Any | No deletion |
| C13 | Invalid input | Any | Validation error |
| C14 | Partial failure | Any | Transaction/recovery behavior |
| C15 | Large dataset | Any | Batched/performance-safe |
| C16 | Dashboard | Any | Metrics reconciled |
| C17 | Notification History | Any | Data actually removed |
| C18 | Telemetry | Any | Data actually removed |
| C19 | Queue | Any | Data actually removed |
| C20 | Scraped cases | Any | Data actually removed |

---

# 29. BOUNDARY TESTING

Test exact date boundaries.

For example:

```text
Start = 09/01/2026 00:00:00
End   = 09/05/2026 23:59:59.999
```

Verify:

- record exactly at start;
- record exactly at end;
- record one millisecond before;
- record one millisecond after.

Timezone and DST behavior must be tested where applicable.

---

# 30. DO NOT USE FRONTEND-ONLY DELETION

A major requirement:

Do NOT solve cleanup by:

```text
filtering the UI
```

or:

```text
removing rows from frontend state
```

The database must actually be changed.

Then APIs must return the correct data.

Then frontend must display the correct data.

---

# 31. CACHE INVALIDATION

After cleanup, identify and invalidate:

- Redis cache.
- API cache.
- frontend query cache.
- dashboard cache.
- notification cache.
- scraper cache.
- generated reports where applicable.

Do not use a blanket:

```text
clear everything
```

unless explicitly required.

Invalidate only what is appropriate.

---

# 32. PERFORMANCE REQUIREMENT

Cleanup must be fast and fluent.

Do not load millions of records into Python memory simply to delete them.

Prefer:

- database-side filtering;
- indexed timestamp columns;
- batch deletes;
- efficient queries;
- proper transactions;
- asynchronous execution for large cleanup jobs.

The UI must remain responsive.

For long-running cleanup:

```text
Queued
→ Running
→ Progress
→ Completed
```

Provide progress where practical.

---

# 33. RESPONSIVE UI

If cleanup is also available from the web/admin UI, it must work on:

- Desktop.
- Laptop.
- Tablet.
- Mobile.

No horizontal overflow.

Selection controls must remain usable.

The preview must remain readable.

Confirmation must be clear.

Do not sacrifice functionality on mobile.

---

# 34. SECURITY

Cleanup is destructive.

Therefore:

- require proper authorization;
- restrict to authorized administrators;
- record the operator;
- audit every cleanup;
- require confirmation;
- validate all inputs server-side;
- prevent unauthorized arbitrary SQL;
- never expose secrets;
- prevent path traversal for file deletion;
- never allow deletion outside approved directories;
- protect configuration data.

Do not implement deletion using unsafe raw user-generated SQL.

---

# 35. AUTOMATED TESTING

Add automated tests for the entire cleanup engine.

At minimum:

### Unit tests

- date parsing;
- month calculation;
- time-period calculation;
- category selection;
- validation;
- dependency resolution;
- deletion planning;
- dry-run calculation.

### Integration tests

- database deletion;
- cascade/dependency deletion;
- notification cleanup;
- telemetry cleanup;
- dashboard reconciliation;
- cache invalidation.

### End-to-end tests

- console [3];
- user selection;
- confirmation;
- deletion;
- UI refresh;
- dashboard verification;
- notification history verification.

Also test options [1]–[9].

---

# 36. REAL BROWSER TESTING

Do not rely only on automated unit tests.

Actually operate the application.

Verify:

```text
Console
↓
Frontend
↓
Backend
↓
Database
↓
Redis
↓
Celery
↓
RPA engine
↓
Chrome
↓
Scrapers
↓
Notifications
↓
Dashboard
```

where applicable.

---

# 37. NO FALSE SUCCESS

The following are NOT acceptable:

```text
Command returned exit code 0
```

as the only evidence.

Also unacceptable:

```text
API returned 200
```

without verifying actual data.

Also unacceptable:

```text
Frontend shows zero records
```

without checking the database.

Also unacceptable:

```text
Cleanup completed
```

while old records remain in another operational table.

---

# 38. FINAL CLEANUP RECONCILIATION

After every cleanup test, perform a reconciliation.

For every selected category:

```text
Expected records deleted
=
Actual records deleted
```

Then verify all dependent views.

Example:

```text
Database                  PASS
API                       PASS
Dashboard                 PASS
Notification History      PASS
Queue                     PASS
Scraped Cases             PASS
Telemetry                 PASS
Bot History               PASS
Exports                   PASS
Cache                     PASS
```

If any selected data remains within the requested range, the cleanup test is FAIL.

---

# 39. DO NOT BLINDLY PRESERVE BROKEN BEHAVIOR

The existing implementation may contain defects.

If you discover:

- incorrect cleanup;
- incomplete deletion;
- stale dashboard metrics;
- orphan records;
- broken dependencies;
- wrong date calculations;
- unsafe deletion;
- broken service startup;
- incorrect service status;
- broken attended mode;
- broken unattended mode;

FIX them.

Do not say:

> "This was how the old implementation worked."

The objective is a **fully working enterprise solution**, not blind preservation of defects.

---

# 40. PRESERVE VALID EXISTING FUNCTIONALITY

While fixing these issues:

- do not remove valid functionality;
- do not break existing APIs;
- do not break the RPA workflow;
- do not break the 8 county scrapers;
- do not break Guidewire;
- do not break notification functionality;
- do not break dashboards;
- do not break authentication;
- do not break settings;
- do not break exports;
- do not break attended mode;
- do not break unattended mode.

Enhance safely.

---

# 41. FINAL ACCEPTANCE TEST

The implementation is NOT complete until all of these pass:

```text
[1] Start Services                 PASS
[2] Stop Services                  PASS
[3] Enterprise Cleanup             PASS
[4] Dependency Installation        PASS
[5] Dependency Purge               PASS
[6] RPA Mode Configuration          PASS
[7] Diagnostics                    PASS
[8] Docker Stack                   PASS
[9] Live Monitoring                PASS
```

And:

```text
Cleanup by category                PASS
Cleanup by current month           PASS
Cleanup by days                    PASS
Cleanup by weeks                   PASS
Cleanup by months                  PASS
Cleanup by years                   PASS
Custom date range                  PASS
Multiple categories                PASS
Select All                         PASS
Select None                        PASS
Dry Run                            PASS
Confirmation                       PASS
Cancellation                       PASS
Dashboard reconciliation           PASS
Notification reconciliation        PASS
Telemetry reconciliation           PASS
Queue reconciliation               PASS
Scraper reconciliation             PASS
Cache invalidation                 PASS
Audit trail                        PASS
Idempotency                        PASS
Error handling                     PASS
Rollback                           PASS
Large dataset handling             PASS
Attended mode                      PASS
Unattended mode                    PASS
```

---

# 42. REQUIRED FINAL REPORT

At the end, provide a report containing:

## A. Issues Found

```text
Issue ID
Component
Problem
Root Cause
Fix
Test
Result
```

## B. Option Validation

```text
Option | Tested | Result | Evidence
1      | YES    | PASS   | ...
2      | YES    | PASS   | ...
...
9      | YES    | PASS   | ...
```

## C. Cleanup Validation

Show every cleanup category tested.

## D. Data Reconciliation

Show:

```text
Before
Selected
Eligible
Deleted
Remaining
Expected Remaining
Mismatch
```

## E. Dashboard Validation

Explicitly prove dashboard values were reconciled after cleanup.

## F. Notification Validation

Explicitly prove:

```text
Outbound Notification History
Delivery History
Notification Events
Retry/Attempt History
```

were correctly handled.

## G. Service Validation

Show:

```text
Frontend
Backend
Redis
Celery
Beat
Monitoring
Docker
RPA
Chrome
```

## H. Test Evidence

Provide:

- commands executed;
- tests executed;
- important logs;
- database verification;
- API verification;
- browser verification;
- cleanup IDs/correlation IDs;
- screenshots where useful.

---

# 43. FINAL DEFINITION OF DONE

This task is complete ONLY when:

1. Options [1]–[9] actually work.
2. Every option has been tested.
3. Option [3] supports user-selected data categories.
4. Multiple categories can be selected in one operation.
5. User can select all categories in one operation.
6. User controls the time period.
7. Current Month is dynamically supported.
8. Days/weeks/months/years are supported.
9. Custom date ranges are supported.
10. Dry-run preview is provided.
11. Confirmation is required.
12. Cancellation works.
13. Database records are actually deleted.
14. Related records are handled correctly.
15. No orphan records remain.
16. Dashboard data is reconciled.
17. Outbound Notification Delivery History is reconciled.
18. Queue data is reconciled.
19. Scraped court data is reconciled.
20. Fuzzy-match data is reconciled.
21. Guidewire activity data is reconciled.
22. Execution telemetry is reconciled.
23. Bot execution history is reconciled.
24. Logs and caches are handled correctly.
25. Redis/cache invalidation works.
26. Cleanup is idempotent.
27. Cleanup is audited.
28. Errors are handled safely.
29. Transactions/rollback work where applicable.
30. Large datasets are handled efficiently.
31. Attended GUI mode works.
32. Unattended mode works.
33. Switching between modes works.
34. All existing valid functionality remains intact.
35. Automated tests pass.
36. Real browser testing passes.
37. No stale records remain after cleanup within the requested scope.
38. No false-positive PASS status is reported.

---

# FINAL PRINCIPLE

Do not implement this as a simple:

```text
"delete some history files"
```

operation.

Implement it as an:

> **Enterprise Data Retention, Cleanup, Reconciliation & Operational Maintenance System**

The user must have complete but safe control over:

```text
WHAT to delete
+
WHEN to delete it
+
PREVIEW what will be deleted
+
CONFIRM the operation
+
EXECUTE safely
+
RECONCILE every affected system
+
AUDIT what happened
```

And most importantly:

> **If the user deletes selected operational data for a specified period, that data must actually disappear from every applicable database table, API response, dashboard aggregation, notification history, queue/history view, telemetry view, scraper result view, cache, and other dependent operational surface.**

Do not declare success until this has been verified end-to-end.