# ATTENDED & UNATTENDED END-TO-END VALIDATION — V4 PARITY, CORRECTION & PRODUCTION READINESS

You must now perform a **complete end-to-end functional validation of the existing UAIC Claim & RPA Orchestrator solution in Attended Mode (visible GUI/browser mode)**.

This is NOT a compile-only test, unit-test-only exercise, mock test, or superficial UI validation.

The objective is to verify that the **entire real automation workflow works correctly from beginning to end**, while matching the functional/business behavior of:

**`UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A`**

However, there is one extremely important rule:

> **V4 is the behavioral baseline, NOT a blind implementation target.**

If you discover that something in V4 is broken, unreliable, hardcoded, slow, insecure, outdated, or logically incorrect, **DO NOT reproduce the defect in the current solution. Fix it in the current solution while preserving the intended business behavior and goal.**

The goal is:

**V4 functional parity + BRD compliance + defect correction + better architecture + better performance + better UX + dynamic configuration + reliable automation.**

---

# 1. SOURCE-OF-TRUTH ANALYSIS

Before testing or modifying anything, inspect and compare BOTH authoritative sources:

### Initial Business Requirement

**`ClaimAutomation_UAIC.pdf`**

This represents the original business requirement and overall business goal.

### Latest Power Automate Implementation

**`UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A`**

This represents the latest evolved implementation containing subsequent changes that were made after the original BRD.

You MUST understand:

```text
Initial BRD
    ↓
Subsequent business/functional changes
    ↓
Power Automate V4
    ↓
Current Application
```

Do not assume that the BRD alone is sufficient.

Do not assume that V4 alone is sufficient.

The final implementation must preserve the **original business goal**, incorporate the valid changes introduced in V4, and correct defects discovered in either source.

---

# 2. THREE-WAY COMPARISON

Create an internal comparison across:

```text
BRD
V4 Power Automate
Current Application
```

For every major requirement determine:

```text
BRD Requirement
V4 Behavior
Current Behavior
Expected Final Behavior
Status
Required Fix
```

Use the following categories:

```text
MATCH
PARTIAL
MISSING
BROKEN
INCORRECT
OUTDATED
V4 DEFECT
ENHANCEMENT REQUIRED
```

Do not mark something as PASS merely because the code exists.

It must work at runtime.

---

# 3. IMPORTANT V4 DEFECT RULE

If V4 contains something such as:

- hardcoded credentials
- hardcoded email
- hardcoded URLs
- incorrect county classification
- incorrect state routing
- disabled failure handling
- incorrect status handling
- broken retry logic
- broken pagination
- unreliable CAPTCHA handling
- race conditions
- duplicate processing
- incorrect fuzzy matching
- incorrect CaseType filtering
- unnecessary fixed waits
- broken error handling
- incorrect queue behavior
- missing telemetry
- incorrect data mapping
- outdated selectors
- browser automation instability
- security problems
- performance problems

you MUST:

1. Identify the defect.
2. Understand the intended business behavior.
3. Fix it in the current solution.
4. Test the corrected behavior.
5. Document the difference between V4 and the corrected implementation.

Do NOT blindly copy known V4 defects.

The correct principle is:

```text
Preserve V4 INTENT
        +
Fix V4 DEFECTS
        +
Improve Architecture
        +
Improve Performance
        +
Improve UX
        =
Final Production Solution
```

---

# 4. ATTENDED MODE IS MANDATORY

Run the actual automation in:

## ATTENDED MODE

The browser/GUI must be visibly available.

You must be able to observe:

```text
Application
    ↓
Queue
    ↓
Chrome Launch
    ↓
County Portal
    ↓
Search
    ↓
CAPTCHA
    ↓
Results
    ↓
Pagination
    ↓
Case Details
    ↓
Extraction
    ↓
Database
    ↓
Fuzzy Match
    ↓
Guidewire
    ↓
Notification
```

Do not replace real browser execution with:

```text
mock browser
mock scraper
fake response
static JSON
simulated CAPTCHA
fake Guidewire response
hardcoded case data
```

unless the specific test is explicitly designed as an isolated automated test.

---

# 5. REAL SYSTEM CHROME

The actual county automation must use the configured **system Google Chrome installation**.

Do NOT silently fall back to:

```text
Playwright bundled Chromium
```

when the production automation requires system Chrome and the Anti-Captcha extension.

Verify:

```text
System Chrome detected
        ↓
Correct executable selected
        ↓
Correct browser profile/context
        ↓
Anti-Captcha extension loaded
        ↓
Browser visibly launches
```

If Chrome fails to launch, fix the root cause.

Do not simply mark the test as passed because the backend started.

---

# 6. ANTI-CAPTCHA

Verify the actual Anti-Captcha integration in Attended Mode.

The extension path must be dynamically resolved from the project root:

```text
<Project Root>/anticaptcha-plugin_v0.83
```

Do NOT hardcode machine-specific paths such as:

```text
C:\Users\...
```

Verify:

```text
Extension exists
        ↓
Extension loads
        ↓
CAPTCHA is detected
        ↓
CAPTCHA is solved
        ↓
Search continues
```

If a CAPTCHA cannot be solved, verify proper:

```text
retry
timeout
failure status
logging
recovery
```

behavior.

---

# 7. TEST THE COMPLETE REAL WORKFLOW

Do not test isolated screens only.

Execute the real workflow:

```text
REAL CLAIM INPUT
      ↓
REAL DATABASE RECORD
      ↓
REAL QUEUE ITEM
      ↓
REAL QUEUE PROCESSING
      ↓
REAL CHROME
      ↓
REAL COUNTY PORTAL
      ↓
REAL SEARCH
      ↓
REAL CAPTCHA
      ↓
REAL RESULT EXTRACTION
      ↓
REAL PAGINATION
      ↓
REAL DATABASE STORAGE
      ↓
REAL FUZZY MATCH
      ↓
REAL GUIDEWIRE
      ↓
REAL NOTIFICATION
      ↓
REAL FINAL STATUS
```

Every stage must be observed and verified.

---

# 8. ALL 8 COUNTY BOTS MUST BE VALIDATED

Validate every configured scraper.

## Florida

```text
1. Broward
2. Hillsborough
3. Miami-Dade
```

## Texas

```text
4. Travis
5. Dallas
6. Harris JP
7. Harris District
8. Harris County Clerk
```

CRITICAL:

```text
Miami-Dade = Florida
```

Miami-Dade must NEVER appear under Texas.

Verify the UI, backend configuration, routing logic, queue payload, telemetry and scraper status all classify it correctly.

---

# 9. STATE ROUTING MUST MATCH BUSINESS LOGIC

Verify the complete routing matrix.

### Policy State = Loss Location State

If:

```text
Florida
```

then:

```text
Broward = Yes
Hillsborough = Yes
Miami-Dade = Yes
```

If:

```text
Texas
```

then:

```text
Travis = Yes
Dallas = Yes
Harris JP = Yes
Harris District = Yes
Harris County Clerk = Yes
```

### Policy State != Loss Location State

All eight sites must be eligible:

```text
Florida × 3
Texas × 5
```

Verify this using actual queue records and runtime telemetry.

---

# 10. ALL INPUT COLUMNS MUST WORK

Validate every required input field:

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

Verify:

```text
Import
Create
Edit
View
Database
Queue
Scraper
Fuzzy Match
Guidewire
Export
```

No field may disappear during the workflow.

---

# 11. QUEUE VALIDATION

Test both:

### Automatic Queue

```text
Automatic Queue = ON
        ↓
Queue item becomes eligible
        ↓
Worker automatically starts it
        ↓
Next eligible item starts sequentially
```

### Manual Queue

```text
Select item
        ↓
Start manually
        ↓
Processing begins
```

Verify that automatic mode does NOT remain incorrectly:

```text
Automatic queue runner is OFF
```

when it is configured ON.

Verify Celery:

```text
Worker
Beat
Redis
Queues
Task registration
Task execution
```

are actually operational.

---

# 12. ATTENDED MODE MUST SHOW REAL ACTIVITY

When a scraper starts in Attended Mode, the visible Chrome browser should actually:

```text
Launch
Navigate
Load portal
Enter search data
Interact with controls
Handle CAPTCHA
Submit search
Read results
Open case details
Return to results
Continue pagination
```

Do not accept:

```text
Task completed
```

if no actual browser activity occurred.

---

# 13. SCRAPER VALIDATION

For every scraper verify:

```text
Correct URL
Correct selectors
Correct search fields
Correct DOL behavior
Correct name format
Correct submit behavior
Correct CAPTCHA behavior
Correct wait conditions
Correct result detection
Correct case extraction
Correct pagination
Correct case-detail navigation
Correct cleanup
Correct database storage
Correct bot status
```

Compare each implementation against V4.

If V4 uses an inefficient fixed wait, replace it with reliable condition-based waiting where possible.

Do not change business behavior merely to change implementation style.

---

# 14. NO BLIND FIXED WAITS

Do not use unnecessary patterns such as:

```text
sleep(10)
sleep(20)
sleep(40)
sleep(150)
```

when reliable browser conditions are available.

Prefer:

```text
wait for selector
wait for navigation
wait for network idle where appropriate
wait for result table
wait for CAPTCHA completion
wait for known status
explicit timeout
```

The automation should be:

**fast, stable and fluent**, not artificially slow.

---

# 15. FUZZY MATCH VALIDATION

Validate the complete fuzzy-match pipeline.

Verify:

```text
Completed scraper results
        ↓
Valid JSON
        ↓
Case parsing
        ↓
Case style cleanup
        ↓
Date filtering
        ↓
Status filtering
        ↓
CaseType filtering
        ↓
Claimant matching
        ↓
Insured matching
        ↓
Driver matching
        ↓
Threshold
        ↓
Positive/Negative result
```

Verify that known V4 logical defects are corrected.

For example, do NOT preserve conditions that effectively mean:

```text
"" == ""
```

or:

```text
contains(value, "")
```

if those conditions bypass the intended business filtering.

---

# 16. DUPLICATE CASE HANDLING

Verify that duplicate cases from:

```text
multiple pages
multiple portals
multiple searches
retries
```

do not create incorrect duplicate downstream activities.

Before sending cases to Guidewire, apply appropriate deduplication based on the actual business identity of the case.

Do not alter valid business matches.

---

# 17. GUIDEWIRE VALIDATION

The actual Guidewire integration must be tested.

Verify:

```text
Correct Claim Number
Correct Exposure Number
Correct Case Items
Correct Case Number
Correct Case Style
Correct County
Correct Suit Filed Date
Correct payload
Correct endpoint
Correct response
ActivityID captured
Database updated
Final status updated
```

Do not consider Guidewire successful merely because an HTTP request was constructed.

Verify the real response.

---

# 18. EMAIL / NOTIFICATION VALIDATION

If the previous Power Platform system contains notification/email behavior, validate the complete implementation.

Verify:

```text
Guidewire Success
      ↓
Notification Event
      ↓
Notification Record
      ↓
Celery Queue
      ↓
Email Worker
      ↓
Provider
      ↓
Delivery
      ↓
Notification History
```

The configured notification email/recipient must come from the application's dynamic Settings/configuration system where applicable.

Do not hardcode recipient addresses.

---

# 19. ERROR AND FAILURE TESTING

Do not test only the happy path.

Deliberately test failures such as:

```text
Chrome unavailable
Portal unavailable
CAPTCHA failure
Search timeout
No results
Malformed result
Pagination failure
Case detail failure
Scraper exception
Fuzzy Match failure
Guidewire failure
Email failure
Redis unavailable
Celery worker unavailable
```

Verify each failure produces:

```text
Correct status
Correct error message
Correct telemetry
Correct retry behavior
Correct queue behavior
Correct recovery behavior
```

A failure in one subsystem must not incorrectly mark unrelated successful stages as failed.

---

# 20. RETRY VALIDATION

Verify retry behavior for:

```text
CAPTCHA
Portal/network failures
Scraper failures
Fuzzy Match
Guidewire
Email
Queue processing
```

Retries must be:

```text
bounded
observable
configurable where appropriate
idempotent
```

Do not create infinite duplicate processing.

---

# 21. STATUS VALIDATION

Clearly distinguish:

### Business/Claim Status

from:

### Automation/Execution Status

Do not merge them merely because they look similar.

Verify all required statuses remain functional.

For example, preserve the required scraper/bot execution states such as:

```text
In Progress
Completed
Failed
No Match Found
```

and record/business statuses such as:

```text
New Record Added
Web Scrapping in Progress
Web Scrapping Completed
Positive Match Found
Positive Match Not Found
Completed
```

Use clear UI labels so users understand the difference.

---

# 22. TELEMETRY VALIDATION

The Detailed Stage Execution Telemetry must reflect actual runtime execution.

For every claim verify visibility of:

```text
Queue
Scraper
Fuzzy Match
Guidewire
Notification
Finalization
```

with:

```text
Started
Completed
Failed
Duration
Error
Retry
Correlation ID
```

Telemetry must not report success when the actual browser/process failed.

---

# 23. DATABASE VALIDATION

After a real attended-mode execution, verify the actual database.

Check:

```text
Claim
Queue
Scraper result
Bot status
JSON result
Fuzzy Match status
Guidewire ActivityID
Final matched JSON
Notification
Audit
Telemetry
```

The UI and database must agree.

---

# 24. EXPORT VALIDATION

Validate:

```text
Excel
CSV
JSON
PDF
```

using real claim data.

Open each generated file and verify:

```text
File exists
File is not corrupted
Expected data exists
Columns are correct
Values are correct
Formatting is correct
Theme/design is correct where applicable
```

For PDF:

```text
Header excluded
Footer excluded
Navigation excluded
Main page content included
Correct theme
Correct layout
Valid PDF
```

Do not mark export as successful merely because a download started.

---

# 25. RESPONSIVE UI VALIDATION

Test the entire application at:

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

Verify:

```text
No accidental horizontal scrolling
No clipped controls
No overlapping controls
No hidden functionality
Tables remain usable
Filters remain usable
Pagination remains usable
Modals remain usable
Forms remain usable
Queue controls remain usable
Settings remain usable
Mobile navigation remains usable
```

Do not simply shrink desktop layouts.

Use appropriate responsive transformations where required.

---

# 26. THEME VALIDATION

Test:

```text
Light Mode
Dark Mode
```

Verify the entire application:

```text
Dashboard
Claims
Claim Detail
Queue
Scrapers
Fuzzy Match
Guidewire
Settings
Tables
Forms
Dialogs
Dropdowns
Pagination
Charts
Notifications
Telemetry
Exports
```

No page or control may remain partially styled in the wrong theme.

---

# 27. PERFORMANCE VALIDATION

The final system must be:

**fast, fluent and responsive.**

Measure and improve:

```text
Page load
Claim detail load
Queue refresh
Database queries
Scraper startup
Portal navigation
Result extraction
Fuzzy matching
Guidewire
Notification
Dashboard
Exports
```

Do not solve performance problems by removing functionality.

Use:

```text
async processing
efficient database queries
pagination
lazy loading
caching where appropriate
condition-based browser waits
connection reuse
Celery
Redis
```

where appropriate.

---

# 28. UNATTENDED MODE REQUIREMENT — CRITICAL

This is mandatory.

> **Everything that successfully works in Attended Mode must also work in Unattended Mode.**

Attended Mode is NOT allowed to hide automation dependencies that will fail in unattended execution.

After successful Attended Mode validation, execute the same scenarios in:

## UNATTENDED MODE

Verify:

```text
No visible user interaction required
No manual CAPTCHA intervention required unless explicitly designed
No reliance on mouse position
No reliance on screen coordinates
No reliance on focused window
No reliance on manually opened tabs
No reliance on user clipboard
No reliance on user-entered values
No reliance on active desktop state
No reliance on browser already being open
```

The automation must programmatically control the required browser/application.

---

# 29. ATTENDED → UNATTENDED PARITY TEST

For every major scenario create:

```text
Scenario
Attended Result
Unattended Result
Differences
Root Cause
Fix
Retest Result
```

Examples:

```text
Florida routing
Texas routing
Broward search
Hillsborough search
Miami-Dade search
Dallas search
Travis search
Harris JP search
Harris District search
Harris County Clerk search
Pagination
Fuzzy Match
Guidewire
Notification
Failure recovery
Queue retry
```

Expected:

```text
Attended = PASS
Unattended = PASS
```

Any difference must be investigated and fixed.

---

# 30. NO "WORKS ON MY MACHINE" ACCEPTANCE

Do not consider the solution production-ready if it works only when:

```text
Chrome is already open
A user is logged in manually
A specific window is focused
A developer has manually configured something
A hardcoded path exists
A specific local username exists
A specific machine environment exists
A developer clicks something manually
```

All required configuration must come from the application's supported configuration mechanism.

---

# 31. AUTOMATION SELF-RECOVERY

Where appropriate, verify recovery from:

```text
browser crash
tab crash
portal timeout
network interruption
CAPTCHA timeout
worker restart
task retry
temporary Redis failure
temporary external API failure
```

The system should recover safely without corrupting claim state or generating duplicate Guidewire activities.

---

# 32. DO NOT SACRIFICE FUNCTIONALITY FOR CLEANUP

You may remove:

```text
unused code
dead files
obsolete implementations
unused imports
old artifacts
.pyc files
temporary files
```

ONLY after verifying they are genuinely unused.

Do NOT remove anything that is still required by:

```text
scrapers
Celery
API
frontend
tests
startup scripts
browser automation
Anti-Captcha
Guidewire
exports
settings
```

Cleanup must never become a regression.

---

# 33. FINAL REGRESSION TEST

After all fixes, execute a complete regression cycle.

Verify:

```text
Application startup
Backend
Frontend
Database
Redis
Celery Worker
Celery Beat
Queue
Automatic processing
Manual processing
All 8 scrapers
Fuzzy Match
Guidewire
Notifications
Telemetry
Dashboard
Settings
Exports
Light/Dark themes
Responsive layouts
Attended mode
Unattended mode
```

Everything must work together.

---

# 34. REQUIRED EVIDENCE

Do not provide a statement such as:

> "Testing completed successfully."

unless actual evidence exists.

Produce evidence for:

### Source Comparison

```text
BRD
V4
Current Application
```

### Runtime Testing

```text
Claim ID
Queue ID
Scraper
Execution ID
Guidewire ActivityID
Notification ID
```

### Browser Testing

Record:

```text
Browser launched
Portal URL
Search executed
CAPTCHA handled
Results found
Case opened
Data extracted
```

### Database Evidence

Show the relevant persisted results.

### Failure Evidence

Show at least one deliberately tested failure and recovery path.

### Unattended Evidence

Show that the same critical workflow completed without manual interaction.

---

# 35. FINAL ACCEPTANCE MATRIX

Create a final matrix:

| Area | BRD | V4 | Current Before Fix | Current After Fix | Attended | Unattended | Evidence |
|---|---|---|---|---|---|---|---|
| Input | | | | | | | |
| Queue | | | | | | | |
| Florida Routing | | | | | | | |
| Texas Routing | | | | | | | |
| Broward | | | | | | | |
| Hillsborough | | | | | | | |
| Miami-Dade | | | | | | | |
| Dallas | | | | | | | |
| Travis | | | | | | | |
| Harris JP | | | | | | | |
| Harris District | | | | | | | |
| Harris Clerk | | | | | | | |
| CAPTCHA | | | | | | | |
| Pagination | | | | | | | |
| Fuzzy Match | | | | | | | |
| Guidewire | | | | | | | |
| Notification | | | | | | | |
| Telemetry | | | | | | | |
| Exports | | | | | | | |
| Settings | | | | | | | |
| Responsive UI | | | | | | | |
| Theme | | | | | | | |
| Performance | | | | | | | |

---

# 36. FINAL REPORT MUST IDENTIFY V4 DEFECTS

Create a section:

## V4 Issues Discovered

For each issue:

```text
V4 Behavior:
Why It Is Incorrect/Problematic:
Business Intent:
Current Solution Fix:
Test Performed:
Final Result:
```

This is important because the objective is NOT to reproduce broken V4 behavior.

---

# 37. FINAL REPORT MUST IDENTIFY ENHANCEMENTS

Create a separate section:

## Improvements Beyond V4

Include improvements such as:

```text
Performance
Reliability
Dynamic configuration
Error handling
Retry
Observability
Security
Responsive UX
Accessibility
Maintainability
Unattended execution
```

Clearly distinguish these from mandatory V4 parity.

---

# 38. FINAL DEFINITION OF DONE

The task is complete ONLY when:

- BRD has been inspected.
- V4 has been inspected.
- Current implementation has been inspected.
- BRD vs V4 vs current implementation has been compared.
- All intended V4 behavior is implemented.
- Known V4 defects have been corrected rather than copied.
- All 8 county scrapers work.
- Miami-Dade is correctly classified as Florida.
- Florida/Texas routing is correct.
- Real system Chrome works.
- Anti-Captcha works.
- Real browser automation works.
- Queue works automatically.
- Manual queue works.
- Scraping works.
- Pagination works where required.
- Fuzzy Match works.
- Guidewire works.
- Notification/email works.
- Database persistence works.
- Statuses are correct.
- Telemetry is correct.
- Exports work and files are validated.
- Settings work as the central configuration source.
- Light mode works.
- Dark mode works.
- Responsive UI works.
- Performance is acceptable.
- Error handling works.
- Retry works.
- No critical regression exists.
- Attended Mode passes.
- **Unattended Mode passes.**
- The same business workflow succeeds in both execution modes.

---

# FINAL PRINCIPLE

The required outcome is NOT:

```text
"Make the current application look like V4."
```

It is:

```text
BRD Business Goal
        +
Valid V4 Functional Evolution
        +
V4 Defect Correction
        +
Current Application Enhancement
        +
Real Attended Execution
        +
Real Unattended Execution
        +
Performance
        +
Reliability
        +
Security
        +
Excellent UI/UX
        =
FULLY WORKING PRODUCTION-READY UAIC SOLUTION
```

**Do not stop at code inspection.**

**Do not stop at compilation.**

**Do not stop at unit tests.**

**Do not stop at mocked browser tests.**

**Do not stop when Attended Mode works.**

The final acceptance requires:

> **The complete real workflow must work in Attended Mode with visible GUI, and the same complete workflow must also work correctly in Unattended Mode without requiring manual intervention.**

If any part fails, investigate the root cause, fix it, retest it, and continue until the complete workflow is stable.