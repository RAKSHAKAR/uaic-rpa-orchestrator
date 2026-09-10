# MASTER IMPLEMENTATION PROMPT
## Rebuild and Productionize the Existing UAIC County Court Automation Platform
### Next.js + React + TypeScript + Python + FastAPI + Celery + Redis + Playwright

---

# 1. ROLE

You are acting as a:

- Principal Software Architect
- Senior Full-Stack Engineer
- Senior Python Engineer
- Senior React/Next.js Engineer
- Browser Automation Engineer
- Playwright Automation Engineer
- Distributed Systems Engineer
- Database Architect
- QA Automation Engineer
- DevOps Engineer
- Security Engineer
- UX/UI Engineer

You are working on an **EXISTING application**.

This is NOT a greenfield demo.

This is NOT a request to create mock screens.

This is NOT a request to replace the existing application with a simplified implementation.

Your responsibility is to:

1. Inspect the entire existing source code.
2. Understand what is already implemented.
3. Preserve all working functionality.
4. Identify incomplete/broken functionality.
5. Implement all missing functionality.
6. Reproduce the existing Power Automate business behavior accurately.
7. Improve reliability, observability, UX, performance and maintainability.
8. Test the complete system end-to-end.
9. Do not remove or break existing functionality while adding new functionality.

---

# 2. PRIMARY OBJECTIVE

Convert the existing Power Automate Desktop + Cloud automation behavior into a production-grade:

- Next.js frontend
- React + TypeScript UI
- Python backend
- FastAPI API layer
- Celery worker architecture
- Redis queue/broker
- SQLAlchemy database layer
- Playwright browser automation
- RapidFuzz matching
- Guidewire integration
- Excel/CSV import/export
- Admin operational dashboard

while maintaining **behavioral parity with the existing automation**.

The most important requirement is:

> The input passed to the new application must behave exactly like the input passed to the existing automation, the same websites must be processed under the same conditions, the same fields must be extracted, the same business rules must be applied, and the same output structure must be stored.

Do NOT redesign the business logic merely because a field appears optional or required in a new database schema.

The source automation is the behavioral reference.

---

# 3. FIRST TASK — DEEPLY AUDIT THE EXISTING APPLICATION

Before changing code, inspect the entire repository.

Do NOT immediately start writing new code.

Create an internal implementation inventory containing:

### Frontend

Inspect:

- app routes
- pages
- layouts
- components
- navigation
- tables
- forms
- modals
- dialogs
- settings
- API client
- types
- hooks
- state management
- loading states
- error handling
- responsive behavior
- theme implementation
- existing CRUD
- existing pagination
- existing filters
- existing sorting
- existing bulk operations
- existing export functionality
- existing automation controls

### Backend

Inspect:

- FastAPI application
- routers
- services
- models
- schemas
- database
- migrations
- Celery tasks
- workers
- Redis integration
- browser automation
- scraper implementations
- matching logic
- Guidewire integration
- configuration management
- logging
- exception handling
- tests

### Automation

Inspect:

- all existing Playwright code
- browser launch code
- Chrome profile handling
- extension handling
- CAPTCHA logic
- portal-specific selectors
- navigation logic
- extraction logic
- pagination
- retry logic
- queue processing
- state transitions
- error handling

### Existing Power Automate implementation

Inspect every available Power Automate implementation/version present in the project/reference material.

If multiple versions exist:

1. Compare them.
2. Identify enhancements.
3. Identify regressions.
4. Determine the latest valid implementation.
5. Preserve all valid enhancements.
6. Do not blindly copy obsolete behavior.
7. Do not silently discard behavior that was added in later versions.

Produce an internal comparison before implementation.

---

# 4. DO NOT BREAK EXISTING FUNCTIONALITY

This is mandatory.

Before modifying any existing function:

- understand its callers
- understand its API contract
- understand its database behavior
- understand its UI dependencies
- understand its queue behavior
- understand its tests

Do not:

- delete working APIs
- rename database fields unnecessarily
- remove working settings
- remove existing pages
- replace working components unnecessarily
- change existing behavior just for cleaner code
- introduce breaking API changes
- change data semantics without explicit justification

If refactoring is required, preserve backward compatibility.

---

# 5. TECHNOLOGY BASELINE

Use the existing technology stack wherever practical.

## Frontend

Existing application uses:

- Next.js 14
- React 18
- TypeScript
- Axios
- TanStack React Query
- TanStack React Table
- React Hook Form
- Zod
- Radix UI
- Lucide icons
- Tailwind CSS

These dependencies are already part of the existing application.

Do not unnecessarily replace the frontend stack.

## Backend

Existing requirements include:

- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- Celery
- Redis
- Flower
- SQLAlchemy async
- asyncpg
- Alembic
- pandas
- openpyxl
- RapidFuzz
- Playwright
- Playwright Stealth
- httpx
- pytest
- pytest-asyncio
- pytest-mock
- Ruff

Preserve and use this architecture appropriately.

---

# 6. ARCHITECTURE

Implement a clean separation:

```text
Next.js / React
       |
       | REST API
       v
FastAPI
       |
       +--------------------+
       |                    |
       v                    v
PostgreSQL/DB          Redis
                            |
                            v
                         Celery
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
       Browser Worker   Matching Worker  Integration Worker
             |
             v
        Playwright
             |
             v
      Real Google Chrome
             |
             v
      Chrome Extension
```

The browser automation must run on the machine/environment where Chrome is actually available.

Do NOT pretend browser automation can work inside a normal Vercel serverless function.

If deployment requires a separate browser worker, implement the architecture accordingly.

---

# 7. REAL CHROME REQUIREMENT

This is one of the most important requirements.

The automation MUST launch the installed/default **Google Chrome browser**, not merely bundled Chromium.

Reason:

The AntiCaptcha Chrome extension is expected to operate inside the actual Chrome browser.

The application must:

1. Detect installed Chrome.
2. Resolve the correct Chrome executable.
3. Launch Chrome.
4. Use the configured Chrome profile when configured.
5. Ensure the AntiCaptcha extension is available.
6. Verify the extension is loaded.
7. Only then start portal automation.

Do not silently fall back to Chromium.

If Chrome is unavailable:

- mark the automation environment as unavailable
- show a clear error
- provide diagnostic information
- do not falsely report that automation started successfully

---

# 8. ANTICAPTCHA EXTENSION

There is an AntiCaptcha Chrome extension directory in the project root.

Use it as the local extension source.

The implementation must:

1. Detect whether the extension is already installed/configured.
2. If not installed, load/add the extension from the project-provided extension directory.
3. Use the AntiCaptcha key already configured through Settings.
4. Never hardcode the API key.
5. Never expose the key in browser-side JavaScript.
6. Never print the key into logs.
7. Never commit secrets into source control.

The existing Settings page already contains:

- AntiCaptcha API key
- Chrome profile directory
- Chrome extension directory
- Chrome browser toggle
- browser execution mode
- CAPTCHA retry configuration
- CAPTCHA wait configuration
- page timeout
- reload backoff

Preserve these settings and make them actually drive the backend automation. 

---

# 9. CAPTCHA BEHAVIOR

IMPORTANT:

Do NOT implement a generic CAPTCHA-solving API workflow.

Do NOT attempt to independently solve image CAPTCHA challenges.

The intended behavior is:

```text
Open portal
     ↓
Detect CAPTCHA
     ↓
Click CAPTCHA checkbox/control
     ↓
AntiCaptcha extension handles challenge
     ↓
WAIT
     ↓
Detect successful verification
     ↓
Continue
```

The application should behave like a human operator interacting with the browser.

The automation must:

- locate the CAPTCHA
- click the checkbox/control
- wait for the extension
- wait for verification
- verify that the CAPTCHA/challenge has actually completed
- only then continue

Do NOT immediately click Search/Submit after clicking CAPTCHA.

---

# 10. CAPTCHA TIMEOUT / RETRY

CAPTCHA resolution must be controlled by Settings.

Existing settings already support:

- maximum CAPTCHA attempts
- CAPTCHA resolution wait
- page timeout
- reload backoff

The UI currently allows CAPTCHA attempts to be configured and CAPTCHA wait up to 60 seconds.

Implement the following behavior:

```text
CAPTCHA attempt N
      ↓
Click CAPTCHA
      ↓
Wait for successful verification
      ↓
If success:
    Continue
      ↓
If timeout/failure:
    Refresh browser/page
      ↓
Wait configured reload-backoff
      ↓
Attempt again
```

If the configured number of retries is exhausted:

- mark that portal execution as failed
- capture diagnostic information
- continue with other portals when appropriate
- do NOT crash the complete claim/job unnecessarily

Important:

The user specifically requires recovery when AntiCaptcha becomes stuck.

Therefore:

> If CAPTCHA does not successfully complete within the configured timeout, refresh the affected page/browser context and restart the CAPTCHA flow.

Do not leave a worker indefinitely waiting.

---

# 11. CAPTCHA SUCCESS DETECTION

Do not treat:

```text
checkbox clicked
```

as:

```text
CAPTCHA solved
```

Those are different states.

Implement portal-specific success detection where possible.

Examples:

- CAPTCHA checkbox state
- challenge iframe disappearance
- verified indicator
- token/state change
- Search button becoming usable
- CAPTCHA container disappearing
- known DOM state after verification

Use multiple indicators when required.

Do not rely solely on fixed sleep.

Fixed waits may be used as fallback, but state-based waiting must be preferred.

---

# 12. BROWSER SESSION STRATEGY

Do NOT open all 8 websites for every record.

Determine required websites from the record's routing rules.

If processing a Florida record:

Open all enabled/required Florida websites in tabs within ONE Chrome session.

Example:

```text
Chrome
 ├── Broward tab
 ├── Hillsborough tab
 └── Miami-Dade tab
```

For Texas:

```text
Chrome
 ├── Travis tab
 ├── Dallas tab
 ├── Harris JP tab
 ├── Harris District Clerk tab
 └── Harris County Clerk tab
```

For a record requiring all sites:

```text
Chrome
 ├── Broward
 ├── Hillsborough
 ├── Miami
 ├── Travis
 ├── Dallas
 ├── Harris JP
 ├── Harris District
 └── Harris Clerk
```

Use the same browser session.

Switch between tabs.

Do not repeatedly close/reopen Chrome between websites.

Only close the browser after all required website tasks for that processing session are complete.

---

# 13. HUMAN-LIKE BROWSER AUTOMATION

The browser automation must perform real UI interactions.

It must:

- navigate to pages
- click controls
- fill fields
- select tabs
- wait for page transitions
- detect page state
- click CAPTCHA
- wait for CAPTCHA completion
- click Search
- wait for results
- read results
- open detail pages where required
- return to search
- navigate pagination
- continue processing

Do not replace portal automation with direct HTTP requests unless the existing portal behavior explicitly permits it.

Do not scrape hidden APIs merely to avoid browser interaction.

The objective is behavioral parity with the existing Power Automate browser automation.

---

# 14. INPUT DATA CONTRACT

The automation input must preserve the existing business input model.

Important fields include:

- Claim Number
- Claimant First Name
- Claimant Last Name
- DOL
- Driver First Name
- Driver Last Name
- Exposure Number
- Garaging City
- Garaging State
- Insured First Name
- Insured Last Name
- Loss Location City
- Loss Location County
- Loss Location State
- Policy State
- Primary Key
- Log ID

Do not discard fields simply because the new application considers them optional.

---

# 15. EXCEL IMPORT

Preserve Excel ingestion behavior.

Support:

- XLSX upload
- CSV upload
- Excel table/worksheet import
- validation
- preview
- duplicate detection
- import progress
- import result
- failed row reporting
- retry failed rows

Use openpyxl/pandas where appropriate.

The current backend already includes pandas and openpyxl.

Imported records must retain the original values accurately.

---

# 16. DOL DATE CONVERSION

Preserve the existing Excel DOL behavior.

Excel serial dates must be converted correctly using the equivalent Excel date base behavior.

The existing automation converts the Excel serial date using:

```text
1899-12-30
```

and stores the formatted value as:

```text
MM/dd/yyyy
```

If DOL is blank/null:

```text
store blank/null
```

Do not introduce timezone-related date shifts.

---

# 17. STATE ROUTING LOGIC

Preserve the existing business logic exactly.

Compare:

```text
Policy State
vs
Loss Location State
```

## If Policy State == Loss Location State

### Florida

If:

```text
Policy State = Florida
```

run:

```text
Broward
Hillsborough
Miami-Dade
```

### Texas

If:

```text
Policy State = Texas
```

run:

```text
Harris County Clerk
Dallas
Harris JP
Harris District Clerk
Travis
```

## If Policy State != Loss Location State

Run ALL configured/enabled websites:

```text
Broward
Hillsborough
Miami-Dade
Harris County Clerk
Dallas
Harris JP
Harris District Clerk
Travis
```

This routing behavior must not be changed merely because another routing strategy appears cleaner.

---

# 18. WEBSITE REGISTRY

The application must have a centralized portal registry.

Each portal must contain:

```text
portal_key
display_name
state
county
base_url
enabled
search_url
authentication_required
captcha_required
pagination_supported
uses_dol
uses_case_detail_page
output_schema
selectors
timeouts
retry_policy
```

The portal registry must be configurable from Settings.

Current configured portals:

## Florida

### Broward County Clerk

```text
https://www.browardclerk.org/Web2
```

### Hillsborough County Clerk

```text
https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab
```

### Miami-Dade County Clerk

```text
https://www2.miamidadeclerk.gov/ocs
```

## Texas

### Travis County

```text
https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29
```

### Dallas County

```text
https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29
```

### Harris County JP

```text
https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29
```

### Harris County District Clerk

```text
https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx
```

### Harris County Clerk

Use the configured URL from Settings.

Do not hardcode signed query-string values into source code.

---

# 19. BROWARD AUTOMATION

Implement the actual existing behavior.

URL:

```text
https://www.browardclerk.org/Web2
```

Flow:

```text
Launch Chrome
↓
Navigate to Broward
↓
Case Search
↓
Party Name
↓
Fill First Name
↓
Fill Last Name
↓
Fill Filing Date On/After
↓
CAPTCHA
↓
Click CAPTCHA
↓
Wait for AntiCaptcha verification
↓
Confirm verification success
↓
Click Search
↓
Wait for results
↓
Extract results
↓
Process pagination
↓
Store output
```

Existing field identifiers include:

```text
firstName
lastName
filingDateOnOrAfterP
```

Result fields:

```text
CaseNumber
CaseStyle
FilingDate
CaseStatus
CaseType
```

Broward has explicit pagination.

Therefore:

```text
Page 1
↓
Extract
↓
Check Next Page
↓
If available:
    Click Next
    Wait
    Extract
    Repeat
↓
Finish
```

Do not stop after page 1.

---

# 20. HILLSBOROUGH AUTOMATION

URL:

```text
https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab
```

Flow:

```text
Party / Business Name
↓
First Name
↓
Last Name
↓
DOL
↓
Search
↓
Wait
↓
Detect No Match
↓
Detect data availability
↓
Extract results
```

Known input fields:

```text
spFirstName
spLastName
spDateFiledAfter
```

Output:

```text
Case Number
Case Style
Filing Date
Case Status
Case Type
```

Handle:

```text
No match
No data available in table
Valid results
```

Do not invent pagination if the actual portal does not expose it.

---

# 21. MIAMI-DADE AUTOMATION

URL:

```text
https://www2.miamidadeclerk.gov/ocs
```

Flow:

```text
Navigate
↓
Check login state
↓
If login required:
    authenticate using securely configured credentials
↓
Party Name
↓
First Name
↓
Last Name
↓
DOL
↓
Convert date to MM-dd-yyyy where required
↓
filingDateFrom
↓
CAPTCHA if present/enabled
↓
Wait for verification
↓
Search
↓
Wait for results
↓
Extract results
```

Output:

```text
Case Style
Case Number
Filing Date
Case Status
Case Type
```

Skip rows where Case Number is blank.

Credentials must NEVER be hardcoded.

The existing implementation exposed credential fields in Settings, so retain that capability but store secrets securely.

---

# 22. DALLAS AUTOMATION

URL:

```text
https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29
```

Search:

```text
Smart / Party Search
```

Use:

```text
LastName,FirstName
```

CAPTCHA:

```text
Detect
↓
Click
↓
Wait
↓
Verify
↓
Retry up to configured limit
```

Important:

Dallas does NOT use DOL as part of the actual search.

Do not add DOL merely because another portal uses it.

Submit through the actual page/JS behavior required by the portal.

Results:

For each row:

```text
Open case
↓
Extract:
    Case Style
    Case Number
    Filing Date
    Case Status
    Case Type
↓
Close detail tab
↓
Return to results
```

Case Style sanitization must preserve existing behavior:

Remove:

```text
/
-
\
|
```

before storing where the legacy behavior requires it.

---

# 23. TRAVIS AUTOMATION

URL:

```text
https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29
```

Search:

```text
Smart Search
```

Input:

```text
LastName,FirstName
```

CAPTCHA:

```text
Click
↓
Wait
↓
Verify
↓
Retry up to configured limit
```

Do not use DOL because the existing Travis search does not use it.

For each result:

```text
Build returned case URL
↓
Open detail in new tab
↓
Extract:
    Case Number
    Case Style
    Filing Date
    Case Status
    Case Type
↓
Close tab
```

---

# 24. HARRIS COUNTY JP AUTOMATION

URL:

```text
https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29
```

Search:

```text
LastName,FirstName
```

CAPTCHA:

```text
Detect
↓
Click
↓
Wait
↓
Verify
↓
Retry
```

Existing behavior allows up to 4 CAPTCHA retries.

However, the retry count must now come from Settings.

Pagination MUST be supported.

For each page:

```text
Extract result
↓
Open case detail
↓
Extract:
    Case Number
    Case Style
    Filing Date
    Case Status
↓
Return
↓
Next page
```

Output does NOT contain CaseType.

Do NOT invent CaseType.

---

# 25. HARRIS DISTRICT CLERK AUTOMATION

URL:

```text
https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx
```

Flow:

```text
Search Our Records and Documents
↓
Party Inquiry
↓
Party Name
↓
LastName,FirstName
↓
DOL
↓
Filed Date Range
↓
Party Search
↓
Extract results
```

Output:

```text
Case Number
Case Style
Filing Date
Case Status
Case Type
```

Case Status extraction must preserve the existing legacy text-cleaning behavior where status is derived from result data.

Do not assume there is always a clean dedicated CaseStatus DOM field.

---

# 26. HARRIS COUNTY CLERK AUTOMATION

Use the configured County Clerk WebSearch URL.

Search fields:

```text
First Name
Last Name
File Date From
```

Existing identifiers include:

```text
ctl00_ContentPlaceHolder1_txtFirstName
ctl00_ContentPlaceHolder1_txtLastName
```

Extract:

```text
Case Number
Filing Date
Case Style
Case Status
```

There is NO CaseType in the legacy output.

Do not invent one.

---

# 27. EXACT OUTPUT CONTRACT

The result schema must preserve portal-specific output.

## Broward

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "...",
  "CaseType": "..."
}
```

## Hillsborough

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "...",
  "CaseType": "..."
}
```

## Miami

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "...",
  "CaseType": "..."
}
```

## Dallas

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "...",
  "CaseType": "..."
}
```

## Travis

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "...",
  "CaseType": "..."
}
```

## Harris JP

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "..."
}
```

## Harris District

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "FilingDate": "...",
  "CaseStatus": "...",
  "CaseType": "..."
}
```

## Harris County Clerk

```json
{
  "CaseNumber": "...",
  "FilingDate": "...",
  "CaseStyle": "...",
  "CaseStatus": "..."
}
```

The absence of CaseType on Harris JP and Harris County Clerk is intentional.

---

# 28. DATABASE STORAGE

Preserve separate portal JSON outputs.

Florida:

```text
fl_jsonbody_broward
fl_jsonbody_hillsborough
fl_jsonbody_miami
```

Texas:

```text
te_jsonbody_cclerk
te_jsonbody_dallas
te_jsonbody_harris
te_jsonbody_hcdistrict
te_jsonbody_travis
```

Also preserve per-portal bot status.

---

# 29. STATUS MODEL

Implement the legacy status semantics.

## Portal status

```text
In Progress
Completed
Failed
No Match Found
```

## Record status

```text
New Record Added
Web Scrapping in Progress
Web Scrapping Completed
Positive Match Found
Positive Match Not Found
Completed
```

Use stable enum values internally.

Never store arbitrary UI labels as the only source of truth.

---

# 30. QUEUE SYSTEM

Use Celery + Redis.

The current backend already includes these dependencies.

Implement:

```text
New Record
↓
Queue
↓
Worker claims record
↓
Browser processing
↓
Portal outputs
↓
Fuzzy matching
↓
Guidewire
↓
Completed
```

Queue behavior must be reliable and observable.

---

# 31. SEQUENTIAL PROCESSING

Default record processing must preserve the existing sequential behavior.

One work item:

```text
Claim
↓
Required websites
↓
Complete all websites
↓
Fuzzy matching
↓
Guidewire
↓
Complete
```

Do not start another record before the current record has completed unless a configurable concurrency mode explicitly allows it.

Within a record, required portals may share one browser session and multiple tabs.

---

# 32. MANUAL QUEUE CONTROLS

The UI MUST provide:

- Start Queue
- Pause Queue
- Resume Queue
- Stop Queue
- Start Selected
- Retry Selected
- Retry Failed
- Cancel Selected
- Clear Completed
- Refresh Queue
- View Job
- View Logs
- View Browser Status

Every queue action must actually invoke backend operations.

Do not build visual-only buttons.

---

# 33. AUTOMATIC QUEUE PROCESSING

The system must automatically process queued items one by one.

Example:

```text
Queue:
1
2
3
4
5

Worker:
Process 1
↓
Complete
↓
Process 2
↓
Complete
↓
Process 3
...
```

If item 2 fails:

```text
Record 2 = Failed
↓
Capture error
↓
Apply retry policy
↓
Continue according to configured queue policy
```

Do not stop the entire queue because one record fails.

---

# 34. RETRY FAILED RECORDS

Implement configurable retry policies.

Settings should control:

- maximum task retries
- retry delay
- CAPTCHA retries
- page reload delay
- browser restart policy
- portal retry policy

The current Settings page already includes queue retry controls. Preserve them and connect them to real Celery behavior.

---

# 35. FUZZY MATCHING

Use RapidFuzz.

The legacy matching sequence is:

```text
Claimant First + Last
        ↓
Case Style
        ↓
threshold 0.6

if no match:

Insured First + Last
        ↓
Case Style
        ↓
threshold 0.6

if no match:

Driver First + Last
        ↓
Case Style
        ↓
threshold 0.6
```

Preserve this order.

Do not randomly reorder candidates.

---

# 36. CASE STYLE CLEANING

Clean CaseStyle before matching.

Preserve existing cleaning behavior:

- CRLF
- LF
- non-breaking spaces
- parentheses
- duplicate spaces
- trim

Also preserve configured noise-word cleaning.

The Settings page already supports configurable party-name cleanup/noise patterns.

---

# 37. MINIMUM FILING DATE

Default fuzzy matching rule:

```text
FilingDate >= 2010-01-01
```

However:

Make this configurable through Settings.

Do not hardcode it throughout the codebase.

---

# 38. ALLOWED CASE STATUS

Preserve the existing allowed status list:

```text
ACTIVE
REOPENED ACTIVE
OPEN
REOPEN
EXTENDED
HEARING SCHEDULED
NONSUIT
OPEN / MISSING FILE DOCUMENTS
RE-OPENED
RESTORED
TRANSFERRED
READY DOCKET
ACTIVE – CIVIL
IN TRIAL
PC1: ACTIVE CASE ON DOCKET
```

IMPORTANT:

The legacy implementation uses substring matching.

Before changing this to exact matching, understand the existing behavior and provide a compatibility option.

The improved implementation should avoid false positives such as:

```text
OPEN
```

accidentally matching:

```text
REOPEN
```

unless legacy compatibility explicitly requires it.

Make matching mode configurable if necessary.

---

# 39. ALLOWED CASE TYPES

Preserve the legacy list:

```text
CIVIL ACTION CENTRAL
COUNTY CIVIL CENTRAL
COUNTY CIVIL NORTH
COUNTY CIVIL SOUTH
COUNTY CIVIL WEST
CIRCUIT CIVIL
COUNTY CIVIL
SMALL CLAIMS
SUMMARY PROCEDURE
COUNTY COURTS – CIVIL
DISTRICT COURTS – CIVIL
OTHER CIVIL
BILL OF REVIEW
BREACH OF CONTRACT
CONSTRUCTION DAMAGES
DAMAGES – AUTO
DAMAGES – OTHER
DECLARATORY JUDGMENT
DTPA – DECEPTIVE TRADE PRACTICE
INSURANCE
INSURANCE POLICY
INSURANCE POLICY – HURRICANE
OTHER PROPERTY
PERSONAL INJURY – AUTO
```

IMPORTANT:

Audit the old condition carefully.

The existing implementation contains an empty-string `contains` condition that effectively bypasses CaseType filtering in one branch.

Do NOT reproduce that bug blindly.

Instead:

1. Preserve expected valid business behavior.
2. Make CaseType filtering configurable.
3. Log which rule was applied.
4. Provide compatibility mode if legacy output must be reproduced exactly.

---

# 40. FUZZY MATCH OUTPUT

Positive matches should contain:

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "CountyWebsite": "...",
  "SuitFiledDate": "..."
}
```

Do not add random fields to the legacy payload unless required by the application.

---

# 41. GUIDEWIRE INTEGRATION

Preserve the existing Guidewire integration.

Payload:

```json
{
  "ClaimNumber": "...",
  "ExposureNumber": "...",
  "CaseItems": []
}
```

Each CaseItem:

```json
{
  "CaseNumber": "...",
  "CaseStyle": "...",
  "CountyWebsite": "...",
  "SuitFiledDate": "..."
}
```

---

# 42. CLAIM NUMBER RULE

Preserve:

```text
If ClaimNumber length == 9:
    prefix "0"
else:
    leave unchanged
```

Do not apply this rule to other fields.

---

# 43. GUIDEWIRE RESPONSE

Guidewire is expected to return:

```text
ActivityID
```

Store it.

Also store:

- final payload
- response status
- response body
- timestamp
- duration
- error details if failed

---

# 44. GUIDEWIRE SETTINGS

The existing Settings page already provides:

- endpoint URL
- authentication type
- API key/token
- client ID
- client secret
- mock mode
- timeout
- live tester

Preserve all of this.

Support:

```text
Bearer
ApiKey
Basic
OAuth2
None
```

Do not expose credentials in frontend logs.

---

# 45. GUIDEWIRE TEST CONSOLE

Keep the existing live Guidewire tester.

It must support:

- custom JSON payload
- send/test
- status
- latency
- response body
- copy response
- clear response
- error diagnostics

The current implementation already supports custom payload editing and response inspection.

Do not remove this functionality.

---

# 46. SETTINGS ARCHITECTURE

There must be ONE authoritative Settings system.

The existing Settings page has these logical groups:

```text
Guidewire API
County Court Portals
Browser & CAPTCHA
RapidFuzz & Filters
Task Queue & Alerts
```

Preserve this structure.

Settings must be persisted in the backend/database.

Workers must read the latest effective configuration.

Avoid requiring application restart for settings that can safely be hot-reloaded.

---

# 47. SETTINGS VALIDATION

Every setting must have:

- type validation
- min/max validation
- sensible default
- help text
- error message
- audit trail
- save state
- reset-default capability

The existing Settings UI already supports Save All Configuration and Reset Defaults. Preserve this.

---

# 48. SETTINGS SECURITY

Secrets must:

- never be returned unnecessarily to frontend
- be masked
- support show/hide
- be encrypted at rest where practical
- never appear in logs
- never appear in error messages
- never appear in Git
- never be hardcoded

The frontend should receive:

```text
configured: true
masked_value: "********"
```

rather than the actual secret unless absolutely required.

---

# 49. ADMIN DASHBOARD

Build/complete a professional operational dashboard.

Display:

### Queue

- Pending
- Running
- Completed
- Failed
- Retry
- Cancelled

### Records

- Total
- New
- In Progress
- Completed
- Match Found
- No Match
- Failed

### Portals

For each portal:

- Enabled/Disabled
- Healthy/Unhealthy
- Last execution
- Last successful execution
- Last failure
- Average duration
- Success rate

### CAPTCHA

- Attempts
- Success
- Failure
- Average resolution time
- Current browser status

### Guidewire

- Requests
- Success
- Failure
- Average latency
- Last Activity ID

---

# 50. RECORD MANAGEMENT PAGE

Create a complete record management experience.

Table must support:

- server-side pagination
- page size
- first/last page
- next/previous
- jump to page
- sorting
- multi-column sorting if useful
- global search
- column filtering
- advanced filters
- status filter
- state filter
- portal filter
- date filter
- claim number filter
- match status filter

---

# 51. BULK OPERATIONS

Implement:

- Select All
- Select Current Page
- Deselect All
- Bulk Delete
- Bulk Retry
- Bulk Start
- Bulk Cancel
- Bulk Change Status
- Bulk Export

Require confirmation for destructive operations.

Show:

```text
Selected: X records
```

---

# 52. CRUD

Records must support:

### Create

- manual record creation
- Excel import
- CSV import

### Read

- list
- details
- portal outputs
- fuzzy matches
- Guidewire result
- execution logs

### Update

- editable input fields
- retry state
- status where permitted
- metadata

### Delete

- single delete
- bulk delete

Use soft delete where appropriate.

Do not physically delete records required for audit.

---

# 53. RECORD DETAILS PAGE / MODAL

Create a detailed record view.

Sections:

```text
Record Information
Input Data
Routing
Portal Execution
Portal Results
Fuzzy Matching
Guidewire
Execution Timeline
Errors
Logs
Raw JSON
```

Use tabs/drawers/modals where appropriate.

---

# 54. PORTAL RESULT VIEW

For every portal show:

```text
Portal
Status
Started
Completed
Duration
Search Input
CAPTCHA Status
Result Count
Raw Result JSON
Error
```

Allow copying JSON.

Allow downloading portal result.

---

# 55. EXPORT

Implement:

## Excel

Export:

- current filtered records
- selected records
- all records
- portal results
- fuzzy matches
- Guidewire results

Use `.xlsx`.

## CSV

Same export options.

Exports must respect:

- current filters
- sorting
- selected rows
- selected columns where supported

For large datasets:

```text
Create export job
↓
Background processing
↓
Progress
↓
Download
```

Do not load millions of rows into browser memory.

---

# 56. IMPORT EXPERIENCE

Create a professional import workflow:

```text
Upload
↓
Parse
↓
Preview
↓
Column Mapping
↓
Validation
↓
Duplicate Check
↓
Import
↓
Progress
↓
Summary
```

Show:

```text
Total Rows
Valid
Invalid
Duplicates
Imported
Failed
```

Allow downloading failed rows.

---

# 57. PAGINATION

Every large dataset must support server-side pagination.

Never retrieve the entire database unnecessarily.

API should support:

```text
page
page_size
sort
filters
search
```

Return:

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 1000,
  "total_pages": 40
}
```

---

# 58. LAZY LOADING

Implement lazy loading where appropriate.

Examples:

- record details
- portal JSON
- logs
- execution timeline
- large result sets

Do not load huge JSON payloads on initial table rendering.

---

# 59. LOADING STATES

Every asynchronous operation must have a real loading state.

Examples:

- table skeleton
- card skeleton
- button spinner
- modal loading
- export progress
- import progress
- queue progress
- portal execution progress
- CAPTCHA waiting indicator

Never show a frozen interface.

---

# 60. REAL-TIME JOB STATUS

Use polling, Server-Sent Events or WebSockets where appropriate.

The user should be able to see:

```text
Claim ABC123
├── Broward       Completed
├── Hillsborough  Running
├── Miami         Pending
└── Guidewire     Pending
```

Update automatically.

Do not require manual browser refresh.

---

# 61. EXECUTION MONITOR

Create a live execution screen.

Show:

```text
Current Claim
Current Portal
Browser
Current Tab
CAPTCHA
Search
Results
Pagination
Fuzzy Match
Guidewire
```

Example:

```text
Processing Claim 001234567

✓ Broward completed — 12 cases
✓ Hillsborough completed — 4 cases
⏳ Miami-Dade — CAPTCHA verification
○ Texas portals — pending
○ Fuzzy Match — pending
○ Guidewire — pending
```

---

# 62. BROWSER STATUS

Show:

```text
Chrome Installed
Chrome Path
Chrome Version
Profile
Extension Detected
Extension Version
AntiCaptcha Configured
Browser Running
Current Session
Open Tabs
```

Provide diagnostics.

---

# 63. PORTAL HEALTH CHECK

Preserve existing Ping Portal functionality.

The current Settings page supports:

- portal URL
- enable/disable
- Ping Portal
- open portal
- duration
- error detail

Keep and improve it.

Health checks must not be confused with actual scraper execution.

---

# 64. ERROR HANDLING

Every automation layer must have structured exceptions.

Example:

```text
BrowserLaunchError
ExtensionLoadError
PortalNavigationError
CaptchaTimeoutError
CaptchaVerificationError
PortalSearchError
PortalNoMatch
PortalExtractionError
PaginationError
DatabaseError
QueueError
FuzzyMatchError
GuidewireError
```

Store structured errors.

---

# 65. ERROR SCREENSHOTS

When a portal fails:

Capture:

- screenshot
- current URL
- page title
- portal
- claim
- timestamp
- exception
- retry number

Do NOT capture secrets unnecessarily.

Allow operators to inspect screenshots from the UI.

---

# 66. FAILED RECORD RECOVERY

Implement automated recovery.

Example:

```text
Failure
↓
Capture diagnostics
↓
Retry if allowed
↓
If retries exhausted:
    Failed
↓
Continue queue
```

Also provide:

```text
Retry
Retry from failed portal
Retry entire record
```

Do not unnecessarily repeat already successful portal work.

---

# 67. IDEMPOTENCY

A job must be safe to retry.

Do not create duplicate Guidewire activities because of a worker restart.

Use idempotency keys such as:

```text
record_id + execution_id
```

and appropriate Guidewire/request identifiers.

Before creating a new activity:

- determine whether one already exists for this execution
- avoid accidental duplicates

---

# 68. TRANSACTION SAFETY

Do not keep a database transaction open during a 2-minute browser operation.

Use:

```text
Claim job
Commit
Browser operation
Persist portal result
Commit
Next portal
```

Do not hold database connections unnecessarily.

---

# 69. CONCURRENCY

Use concurrency carefully.

Default:

```text
Record concurrency = 1
```

Portal execution within a single record can use tabs in one browser.

Do not create uncontrolled parallel browser instances.

The legacy fuzzy implementation used high concurrency in one area; do not reproduce unsafe shared mutable state.

All shared arrays/state must be isolated per job.

---

# 70. FUZZY MATCHING CONCURRENCY SAFETY

Do not use a shared mutable global array across concurrent workers.

Each job must have:

```text
local candidate list
local match result
local execution context
```

Persist results transactionally.

Ordering must be deterministic where business logic requires it.

---

# 71. API DESIGN

Use clean REST APIs.

Examples:

```text
GET    /api/records
POST   /api/records
GET    /api/records/{id}
PATCH  /api/records/{id}
DELETE /api/records/{id}

POST   /api/records/import
POST   /api/records/export

POST   /api/records/{id}/start
POST   /api/records/{id}/retry
POST   /api/records/{id}/cancel

POST   /api/queue/start
POST   /api/queue/pause
POST   /api/queue/resume
POST   /api/queue/stop

GET    /api/jobs
GET    /api/jobs/{id}
GET    /api/jobs/{id}/logs

GET    /api/settings
PUT    /api/settings
POST   /api/settings/reset

POST   /api/guidewire/test
POST   /api/portals/{portal}/ping
POST   /api/portals/{portal}/test
```

Adapt to existing API structure rather than blindly creating duplicates.

---

# 72. DATABASE

Use SQLAlchemy consistently.

Create normalized entities where appropriate:

```text
records
portal_executions
portal_results
fuzzy_matches
guidewire_transactions
jobs
job_logs
settings
audit_logs
exports
imports
```

Do not duplicate huge JSON unnecessarily.

Store raw JSON where needed for audit and exact-output parity.

---

# 73. AUDIT LOG

Record:

- who imported data
- who edited records
- who started automation
- who retried
- who deleted
- who changed settings
- who changed portal configuration
- Guidewire tests
- browser actions at appropriate granularity
- failures

Do not log sensitive credentials.

---

# 74. LOGGING

Use structured logging.

Every job log should include:

```text
execution_id
record_id
claim_number
portal
worker
timestamp
event
level
duration
error_code
```

Example:

```text
INFO
execution=abc
record=123
portal=broward
event=search_completed
result_count=12
duration=18.2s
```

---

# 75. FRONTEND RESPONSIVENESS

The entire application must be fully responsive.

Support:

- mobile
- tablet
- laptop
- desktop
- ultrawide screens

The application must use the full available width of the active screen.

Do not unnecessarily constrain the application to a narrow centered container.

Avoid:

```text
max-width: 1200px
```

when it causes unused screen space.

Use responsive layouts.

---

# 76. MOBILE NAVIGATION

On mobile:

- provide fixed/sticky bottom navigation
- preserve access to primary modules
- provide hamburger/menu where needed
- avoid horizontal overflow
- make buttons touch-friendly

Tables should transform appropriately into:

- horizontally scrollable tables
- responsive cards
- condensed row views

depending on the screen.

---

# 77. MOBILE UX

On mobile:

- filters should open in a drawer
- bulk actions should be in an action bar
- forms should stack
- modals should become bottom sheets/full-screen where appropriate
- JSON viewers should scroll horizontally
- buttons should remain usable
- pagination must remain accessible

---

# 78. DESKTOP UX

On desktop:

- use full width
- dense professional data tables
- sticky headers where appropriate
- resizable columns where useful
- command actions
- keyboard shortcuts
- detail drawers
- contextual actions

---

# 79. UI QUALITY

Do not stop at functional UI.

Implement:

- consistent spacing
- typography hierarchy
- professional cards
- badges
- status indicators
- skeletons
- tooltips
- confirmation dialogs
- empty states
- error states
- success states
- hover states
- focus states
- keyboard navigation

Do not add decorative UI that does not improve usability.

---

# 80. THEME

Preserve existing theme support.

Everything must work correctly in:

- Light
- Dark

Do not allow text to disappear when switching themes.

Verify:

- tables
- inputs
- selects
- modals
- dialogs
- tooltips
- pagination
- loaders
- badges
- navigation
- JSON viewers

---

# 81. ACCESSIBILITY

Implement:

- semantic HTML
- keyboard navigation
- focus states
- ARIA labels
- accessible dialogs
- accessible tables
- sufficient contrast
- screen-reader friendly status updates

---

# 82. SEARCH

Global search should support:

- claim number
- primary key
- claimant
- insured
- driver
- state
- status
- portal
- case number

Use debouncing.

Search should be server-side for large datasets.

---

# 83. ADVANCED FILTERS

Provide filters for:

```text
State
Policy State
Loss Location State
Status
Portal
Portal Status
Match Status
Guidewire Status
Created Date
Processed Date
DOL
Claim Number
Exposure Number
```

Allow:

```text
Apply
Clear
Save Filter
```

where useful.

---

# 84. SORTING

Support sorting on relevant columns.

Examples:

```text
Claim Number
DOL
Created Date
Updated Date
Status
State
Portal Count
Match Count
Execution Duration
```

Sorting must be server-side for large datasets.

---

# 85. MODALS / POPUPS

Use professional modal/dialog components for:

- Create
- Edit
- Delete confirmation
- Bulk delete
- Retry confirmation
- Start automation
- Import
- Export
- Guidewire test
- Portal test
- Record details
- Error details

Do not use browser `alert()` except as a last-resort fallback.

---

# 86. TOASTS

Use non-blocking toast notifications for:

- Save successful
- Import completed
- Export ready
- Queue started
- Queue paused
- Retry started
- Delete successful
- API failure

Critical destructive actions still require confirmation dialogs.

---

# 87. EXPORT COLUMN DESIGN

Allow export to contain:

### Input

```text
Claim Number
Exposure Number
Claimant
Insured
Driver
DOL
Policy State
Loss Location State
Loss Location County
Garaging State
Garaging City
```

### Execution

```text
Record Status
Execution Status
Created
Started
Completed
Duration
```

### Portal

```text
Broward
Hillsborough
Miami
Dallas
Travis
Harris JP
Harris District
Harris Clerk
```

### Matching

```text
Match Status
Matched Case Number
Matched Case Style
County Website
Suit Filed Date
```

### Guidewire

```text
Activity ID
Guidewire Status
```

---

# 88. NO-MATCH HANDLING

If a portal finds no cases:

Store:

```text
status = No Match Found
json = appropriate empty/legacy-compatible output
```

Do not treat no-match as a technical failure.

Similarly:

```text
No CAPTCHA
```

must not be treated as:

```text
CAPTCHA failure
```

---

# 89. PORTAL FAILURE VS BUSINESS NO-MATCH

These are distinct:

```text
No Match Found
```

means:

> Portal worked and returned no matching cases.

```text
Failed
```

means:

> Portal automation could not successfully complete.

Never mix them.

---

# 90. BROWSER FAILURE VS PORTAL FAILURE

If Chrome crashes:

```text
Browser failure
```

If Broward fails while other tabs work:

```text
Portal failure
```

Do not mark every portal failed merely because one portal encountered an error.

---

# 91. RECOVERY FROM BROWSER CRASH

Implement:

```text
Detect browser crash
↓
Capture state
↓
Restart Chrome
↓
Reload required tabs
↓
Resume failed portal
```

Do not automatically restart completed portal work unless necessary.

---

# 92. CONFIGURATION HOT RELOAD

When Settings are saved:

- persist settings
- invalidate worker configuration cache
- ensure future jobs use new settings
- do not require manual restart unless technically unavoidable

The existing UI claims that settings apply to workers/scrapers/Guidewire. Make this statement truthful.

---

# 93. TESTING

Testing is mandatory.

Create:

## Unit tests

For:

- state routing
- DOL conversion
- Claim Number normalization
- CaseStyle cleaning
- status filtering
- CaseType filtering
- fuzzy matching
- payload generation
- settings validation

## Integration tests

For:

- database
- FastAPI
- Celery
- Redis
- Guidewire mock
- import/export

## Browser tests

Use Playwright.

Test:

- Chrome launch
- portal navigation
- form filling
- CAPTCHA detection
- CAPTCHA waiting
- result extraction
- pagination
- portal failure recovery

Where real CAPTCHA cannot be used in CI:

- use deterministic test fixtures/mocks
- never disable CAPTCHA logic in production code just to make tests pass

---

# 94. END-TO-END TEST

Create an end-to-end test representing:

```text
Excel Upload
↓
Record Creation
↓
State Routing
↓
Queue
↓
Chrome Launch
↓
Portal Tabs
↓
Search
↓
CAPTCHA
↓
Results
↓
Pagination
↓
Database
↓
Fuzzy Matching
↓
Guidewire
↓
Final Completion
```

Validate the exact final stored data.

---

# 95. TEST DATA

Create representative test records for:

### Florida

- same insured/driver/claimant
- insured = driver
- insured = claimant
- driver = claimant
- all three different

### Texas

Same combinations.

### Cross-state

```text
Policy State = Florida
Loss Location State = Texas
```

Must process all configured portals.

### Same-state unsupported

```text
Policy State = another state
Loss Location State = same state
```

Must preserve the legacy behavior.

---

# 96. IMPORTANT SEARCH COUNT LOGIC

Preserve the legacy search optimization logic.

Existing behavior derives search counts based on equality of:

```text
Insured
Driver
Claimant
```

Conceptually:

### All same

```text
DualSearch = 1
TripleSearch = 1
```

### Insured = Driver, Claimant different

```text
DualSearch = 1
TripleSearch = 3
```

### Insured = Claimant, Driver different

```text
DualSearch = 2
TripleSearch = 1
```

### Driver = Claimant, Insured different

```text
DualSearch = 2
TripleSearch = 1
```

### All different

```text
DualSearch = 2
TripleSearch = 3
```

Preserve this behavior unless the latest valid Power Automate implementation explicitly changes it.

---

# 97. NAME COMPARISON

Audit the legacy comparison behavior carefully.

The old logic compares first and last names independently.

Do not accidentally change:

```text
same person
```

into:

```text
different person
```

because only one name component changed.

Write explicit tests for:

- same first + same last
- different first + same last
- same first + different last
- different first + different last

---

# 98. POWER AUTOMATE PARITY MATRIX

Create a technical parity matrix:

| Capability | Legacy | New | Test |
|---|---|---|---|
| Excel import | Yes | Yes | Pass |
| State routing | Yes | Yes | Pass |
| Work queue | Yes | Yes | Pass |
| Chrome | Yes | Yes | Pass |
| AntiCaptcha | Yes | Yes | Pass |
| Broward | Yes | Yes | Pass |
| Hillsborough | Yes | Yes | Pass |
| Miami | Yes | Yes | Pass |
| Dallas | Yes | Yes | Pass |
| Travis | Yes | Yes | Pass |
| Harris JP | Yes | Yes | Pass |
| Harris District | Yes | Yes | Pass |
| Harris Clerk | Yes | Yes | Pass |
| Pagination | Portal-specific | Same | Pass |
| Fuzzy Match | Yes | Yes | Pass |
| Guidewire | Yes | Yes | Pass |
| Retry | Yes | Yes | Pass |
| Failure recovery | Yes | Improved | Pass |

Do not mark anything Pass without actual testing.

---

# 99. DO NOT COPY LEGACY BUGS BLINDLY

The goal is:

```text
Functional parity
+
Bug fixes
+
Reliability improvements
+
Security improvements
+
Better UX
```

Do not reproduce known defects such as:

- hardcoded credentials
- disabled failure updates
- disabled screenshots
- unsafe concurrency
- broken filtering
- inconsistent endpoint environments
- obsolete test endpoints
- accidental empty-string filters

But do not remove valid business behavior.

---

# 100. ENVIRONMENT CONFIGURATION

All environment-specific values must be configurable.

Examples:

```text
DATABASE_URL
REDIS_URL
GUIDEWIRE_URL
GUIDEWIRE credentials
ANTICAPTCHA key
CHROME_PATH
CHROME_PROFILE
EXTENSION_PATH
FUZZY_MATCH_URL
```

Never hardcode production URLs/secrets into frontend source.

---

# 101. DEVELOPMENT MODE

Provide:

```text
Mock Guidewire
Mock CAPTCHA
Mock Portal
Test Browser
Test Queue
```

where technically necessary.

But clearly distinguish:

```text
MOCK
```

from:

```text
REAL
```

Never accidentally send production Guidewire traffic during automated tests.

---

# 102. PRODUCTION MODE

Production must:

- use real Chrome
- use real configured portal URLs
- use real configured CAPTCHA extension
- use real configured Guidewire endpoint
- persist all execution data
- record failures
- support recovery
- support monitoring

---

# 103. SECURITY

Implement:

- secret masking
- encryption at rest where practical
- secure cookies/token handling
- CSRF protection where applicable
- input validation
- URL validation
- SSRF protection for configurable URLs
- command injection protection
- safe browser path validation
- restricted filesystem access
- audit logging
- least privilege

Do not allow arbitrary filesystem paths or commands from an untrusted frontend.

---

# 104. CHROME SECURITY

Never execute arbitrary user-provided Chrome command-line arguments.

Whitelist supported options.

Validate:

```text
Chrome executable
profile directory
extension directory
```

before launching.

---

# 105. PERFORMANCE

Optimize:

- database queries
- indexes
- pagination
- JSON storage
- Celery jobs
- browser reuse
- API caching where safe
- frontend rendering
- table virtualization if needed

Do not optimize by removing required browser waits or state verification.

---

# 106. DATABASE INDEXES

Index:

```text
claim_number
primary_key
status
policy_state
loss_location_state
created_at
updated_at
dol
execution_status
guidewire_status
```

Add indexes based on actual query patterns.

---

# 107. OBSERVABILITY

Provide:

- health endpoint
- readiness endpoint
- worker health
- Redis health
- database health
- browser health
- portal health
- Guidewire health

Dashboard should expose operational status.

---

# 108. CELERY/FLOWER

Keep Flower support for worker monitoring.

Expose:

- active workers
- pending jobs
- running jobs
- failed jobs
- retrying jobs

Do not rely exclusively on Flower; application-level job tracking is required.

---

# 109. DEPLOYMENT

Support:

### Local Windows

Because real Chrome + extension is required.

### Docker

Provide appropriate browser-worker architecture.

### VPS

Support persistent browser worker.

Do not claim that real GUI Chrome + extension can run identically inside every serverless environment.

The architecture must clearly separate:

```text
Web Application
API
Database
Redis
Worker
Browser Worker
```

when required.

---

# 110. FRONTEND BUILD QUALITY

Before completion run:

```text
npm install
npm run lint
npm run build
```

Fix all:

- TypeScript errors
- JSX errors
- ESLint errors
- hydration issues
- invalid imports
- missing components
- broken routes
- console errors

Do not leave known console errors.

---

# 111. BACKEND QUALITY

Run:

```text
pytest
pytest -q
ruff check
```

Fix all failures.

Ensure:

- no unhandled async errors
- no leaked DB connections
- no leaked browser contexts
- no leaked Celery tasks
- no hanging requests

---

# 112. BROWSER CLEANUP

Always use safe cleanup:

```python
try:
    ...
finally:
    ...
```

Close:

- pages when no longer needed
- browser context
- browser only after required session completion

But do NOT close the browser between portal tabs when the same claim is still being processed.

---

# 113. PORTAL SELECTOR ARCHITECTURE

Do not scatter selectors throughout the application.

Use portal-specific classes/configuration:

```text
BrowardScraper
HillsboroughScraper
MiamiScraper
DallasScraper
TravisScraper
HarrisJPScraper
HarrisDistrictScraper
HarrisClerkScraper
```

Shared base:

```text
BasePortalScraper
```

Shared capabilities:

```text
navigate()
click()
fill()
wait()
handle_captcha()
extract()
paginate()
recover()
```

Portal-specific behavior stays inside the portal implementation.

---

# 114. SELECTOR RESILIENCE

Prefer:

1. stable IDs
2. names
3. labels
4. semantic selectors
5. role selectors
6. CSS
7. XPath only where necessary

Avoid fragile selectors based solely on DOM position.

Provide fallback selectors.

---

# 115. PORTAL VERSION CHANGES

A portal can change.

Implement:

- selector diagnostics
- portal health test
- scraper version
- extraction validation
- failure screenshots
- clear error messages

If expected fields disappear:

```text
Portal schema changed
```

should be reported instead of silently storing empty results.

---

# 116. DATA VALIDATION

Before storing portal results:

Validate:

```text
CaseNumber
CaseStyle
FilingDate
CaseStatus
CaseType
```

according to that portal's actual output contract.

Do not reject valid records merely because a portal legitimately omits CaseType.

---

# 117. EXACT JSON PRESERVATION

The raw portal JSON must remain available.

Do not normalize away fields that were actually returned.

Store:

```text
raw_json
normalized_json
```

where useful.

The UI should allow viewing raw JSON.

---

# 118. EXECUTION TIMELINE

Each record should have an event timeline:

```text
Record Created
Queue Added
Worker Started
Browser Started
Portal Started
CAPTCHA Started
CAPTCHA Completed
Search Started
Search Completed
Extraction Completed
Pagination Completed
Portal Completed
Fuzzy Match Started
Fuzzy Match Completed
Guidewire Started
Guidewire Completed
Record Completed
```

This is extremely important for debugging.

---

# 119. UI QUEUE TABLE

Columns should include:

```text
Select
Claim Number
Claimant
Insured
Driver
Policy State
Loss State
Status
Current Portal
Progress
Attempts
Match
Guidewire
Created
Actions
```

Use badges.

---

# 120. PROGRESS

For each record calculate:

```text
completed_portals / required_portals
```

Example:

```text
2 / 3 portals completed
```

Display progress bar.

---

# 121. ACTION MENU

Each record should have:

```text
View
Edit
Start
Retry
Retry Failed Portal
Cancel
Delete
Export
View Logs
View JSON
```

Actions must be permission-aware.

---

# 122. BULK ACTION BAR

When selected:

```text
8 selected

Start
Retry
Cancel
Change Status
Export
Delete
```

Use confirmation for destructive actions.

---

# 123. EMPTY STATES

Every page needs a meaningful empty state.

Examples:

```text
No records found
No failed jobs
No portal results
No matches
No logs
No exports
No imports
```

Provide useful next action.

---

# 124. ERROR STATES

Every API page must handle:

```text
loading
success
empty
error
retry
```

This follows standard API UX expectations and is also consistent with the project's existing frontend architecture. 

---

# 125. NO FAKE DATA

Do not use hardcoded fake records in production screens.

Mock data is allowed only in:

```text
development
storybook
automated tests
```

Clearly label it.

---

# 126. NO PLACEHOLDER BUTTONS

Every button must work.

Do not implement:

```text
Coming Soon
TODO
Not Implemented
```

for required functionality.

---

# 127. NO SILENT FAILURES

If something fails:

- display it
- log it
- persist it where relevant
- allow retry
- provide diagnostics

Never silently swallow exceptions.

---

# 128. EXISTING SETTINGS PAGE

Do not replace the existing Settings page unnecessarily.

Enhance it.

It currently contains:

### Guidewire

- endpoint
- authentication
- credentials
- mock mode
- timeout
- test payload
- response inspector

### Portals

- 8 portal configurations
- enable/disable
- URL
- Ping
- open portal
- Miami credentials

### Browser/CAPTCHA

- CAPTCHA attempts
- CAPTCHA wait
- page timeout
- reload backoff
- user agent
- Chrome toggle
- extension path
- API key
- Chrome profile
- browser mode

### Matcher

- minimum filing date
- noise words
- matching configuration

### Queue

- max retries
- retry delay
- batch size
- notification email

These existing capabilities must continue working. 

---

# 129. SETTINGS UX IMPROVEMENTS

You may improve the Settings page with:

- grouped cards
- inline validation
- reset individual setting
- reset section
- save indicator
- unsaved changes warning
- last saved timestamp
- configuration health
- test buttons
- masked secrets
- copy-safe controls
- mobile-friendly tabs
- sticky save bar

Do not remove existing settings.

---

# 130. CONFIGURATION HEALTH

Add:

```text
Chrome ✓
AntiCaptcha ✓
Redis ✓
Database ✓
Guidewire ✓
Broward ✓
Hillsborough ✓
Miami ✓
Dallas ✓
Travis ✓
Harris JP ✓
Harris District ✓
Harris Clerk ✓
```

Use actual health checks.

---

# 131. IMPORTANT: LATEST POWER AUTOMATE VERSION

When inspecting the supplied/reference automation:

- inspect all available versions
- compare V2/V3/V4 or any later versions if present
- identify which version contains the latest business behavior
- incorporate valid enhancements

Do NOT assume the oldest version is authoritative.

If a newer version exists, use it as the primary behavioral reference.

If versions conflict:

```text
latest validated business behavior wins
```

unless an earlier behavior is explicitly required for compatibility.

---

# 132. LEGACY LIMITATIONS TO AUDIT

During implementation, explicitly inspect whether the following legacy issues still exist:

1. Hardcoded portal credentials.
2. Different fuzzy-match API environments.
3. Different Guidewire environments.
4. Disabled failure-status updates.
5. Disabled error screenshots.
6. Incomplete error recovery.
7. CaseType filter bypass.
8. Substring status matching.
9. Missing pagination on some portals.
10. CAPTCHA success detection relying too heavily on waits.
11. Fixed sleeps.
12. Unsafe shared concurrency.
13. Duplicate activity risk.
14. Missing portal-specific validation.
15. Inconsistent environment configuration.

Fix these where appropriate without changing intended business behavior.

---

# 133. LEGACY VS IMPROVED BEHAVIOR

For every improvement, document:

```text
Legacy behavior
New behavior
Why changed
Compatibility impact
Test coverage
```

Example:

```text
Legacy:
Hardcoded Miami credentials

New:
Encrypted settings-backed credentials

Reason:
Security

Compatibility:
No business behavior change
```

---

# 134. AUTOMATION DEBUG MODE

Add an optional debug mode.

When enabled:

- slower execution
- detailed logs
- screenshots
- DOM diagnostics
- selector diagnostics
- portal step timeline

When disabled:

- normal production execution
- minimal logs
- no unnecessary screenshots

---

# 135. MANUAL PORTAL TEST

Settings should allow:

```text
Test Portal
```

The test should:

1. Launch Chrome.
2. Open portal.
3. Validate navigation.
4. Detect required controls.
5. Optionally perform a safe test action where possible.
6. Report health.

Do not execute destructive searches with fake data against production portals unless explicitly intended.

---

# 136. RECORD TEST MODE

Allow operators to select a record and run:

```text
Test Automation
```

Show live steps.

This should be useful for debugging selectors and CAPTCHA behavior.

---

# 137. BROWSER SESSION UI

Show:

```text
Session ID
Chrome PID
Profile
Extension
Open Tabs
Current Tab
Started
Duration
```

Allow:

```text
Stop Browser Session
```

with confirmation.

---

# 138. DATA RETENTION

Provide configurable retention policies for:

- logs
- screenshots
- raw JSON
- job history
- exports

Do not automatically delete business records without explicit policy.

---

# 139. BACKGROUND CLEANUP

Implement scheduled cleanup for:

- expired temporary exports
- old screenshots
- old debug logs
- abandoned jobs

Never delete audit records accidentally.

---

# 140. HEALTH / MONITORING PAGE

Create an operational health page showing:

```text
API
Database
Redis
Celery
Chrome
AntiCaptcha
Guidewire
8 portals
Storage
```

with:

```text
Healthy
Warning
Critical
```

---

# 141. RESPONSIVE TABLE REQUIREMENT

Desktop:

```text
Full data table
```

Tablet:

```text
Condensed table
```

Mobile:

```text
Card/list representation
```

Do not make users horizontally scroll the entire application just to access actions.

---

# 142. COMMAND PALETTE

Add:

```text
Ctrl + K
```

for global actions.

Actions:

```text
Search Records
Create Record
Import Excel
Import CSV
Export
Start Queue
Pause Queue
Retry Failed
Open Settings
Open Health
```

---

# 143. KEYBOARD ACCESSIBILITY

Support:

```text
Ctrl + K
Esc
Enter
Tab
Shift + Tab
```

where appropriate.

---

# 144. CONFIRMATION BEFORE DESTRUCTIVE OPERATIONS

Require confirmation for:

- delete
- bulk delete
- cancel job
- stop queue
- reset settings
- reset all configuration

---

# 145. DATA CONSISTENCY

Never let the frontend show:

```text
Completed
```

while backend says:

```text
Running
```

Use server state as source of truth.

---

# 146. CACHE INVALIDATION

After:

- create
- update
- delete
- start
- retry
- cancel
- import

invalidate/update React Query caches correctly.

Do not require full-page refresh.

---

# 147. FRONTEND API ERROR HANDLING

Handle:

```text
400
401
403
404
409
422
429
500
502
503
504
```

with useful user messages.

Never display raw Python stack traces to normal users.

---

# 148. RATE LIMITING

Protect:

- manual start
- retry
- bulk retry
- exports
- imports
- Guidewire tests
- portal tests

from accidental repeated clicks.

Disable buttons while requests are executing.

---

# 149. DOUBLE-SUBMISSION PROTECTION

Every mutation must be idempotent or protected from duplicate clicks.

Example:

User clicks:

```text
Start
Start
Start
```

should not create three jobs.

---

# 150. PROGRESSIVE ENHANCEMENT

The application must remain usable if:

- WebSocket unavailable
- live status stream unavailable
- one portal unavailable
- Guidewire unavailable

Show degraded state rather than crashing.

---

# 151. FINAL VALIDATION

Before declaring completion:

## Frontend

```text
npm run lint
npm run build
```

## Backend

```text
pytest
ruff check
```

## Browser

Run real browser tests.

## Queue

Process multiple records.

## CAPTCHA

Test timeout/retry behavior.

## Import

Test Excel and CSV.

## Export

Test Excel and CSV.

## CRUD

Test create/read/update/delete.

## Bulk

Test selection/bulk actions.

## Pagination

Test page navigation.

## Sorting

Test all relevant columns.

## Filtering

Test combinations.

## Mobile

Test:

```text
375px
390px
768px
1024px
1440px
1920px+
```

---

# 152. REAL BROWSER ACCEPTANCE TEST

At least one real acceptance test must execute:

```text
Launch actual Google Chrome
↓
Load configured extension
↓
Open actual portal
↓
Navigate like human
↓
Fill real fields
↓
Click CAPTCHA
↓
Wait for AntiCaptcha
↓
Detect success
↓
Submit
↓
Read result
↓
Persist result
```

Do not claim this is tested if only mocked browser tests were executed.

---

# 153. NO SHORTCUTS

Do NOT:

- replace browser automation with requests
- skip CAPTCHA waiting
- skip pagination
- hardcode outputs
- create fake success states
- hardcode test data
- hardcode Guidewire response
- hardcode portal results
- bypass queue
- mark jobs completed without actual execution
- silently ignore failures

---

# 154. IMPLEMENTATION ORDER

Work in this order:

## Phase 1

Audit existing source.

## Phase 2

Audit Power Automate versions.

## Phase 3

Create parity matrix.

## Phase 4

Fix architecture/data model.

## Phase 5

Complete browser/Chrome/extension infrastructure.

## Phase 6

Implement portal automation.

## Phase 7

Implement queue orchestration.

## Phase 8

Implement fuzzy matching.

## Phase 9

Implement Guidewire.

## Phase 10

Complete CRUD/data management.

## Phase 11

Import/export.

## Phase 12

Dashboard/monitoring.

## Phase 13

Responsive/mobile UX.

## Phase 14

Testing.

## Phase 15

Real browser acceptance.

## Phase 16

Production hardening.

---

# 155. DO NOT STOP AFTER ONE PHASE

Do not return after saying:

```text
Architecture completed.
```

Continue until the application is actually functional.

Do not leave partially implemented modules.

---

# 156. CODE QUALITY

Follow:

- SOLID
- DRY
- typed APIs
- dependency injection where appropriate
- service boundaries
- reusable components
- reusable hooks
- repository/service patterns where appropriate
- clear exception hierarchy
- meaningful names
- no unnecessary abstraction

Avoid overengineering.

---

# 157. DOCUMENTATION

Create/update:

```text
README
Architecture documentation
Setup documentation
Chrome setup
AntiCaptcha setup
Environment variables
Database setup
Redis setup
Celery setup
Browser worker setup
Testing instructions
Production deployment
Troubleshooting
Portal troubleshooting
Guidewire troubleshooting
```

---

# 158. OPERATOR DOCUMENTATION

Document:

```text
How to import records
How to start queue
How to retry
How CAPTCHA works
How Chrome extension works
How to configure portals
How to configure Guidewire
How to diagnose failures
How to export results
How to interpret statuses
```

---

# 159. FINAL ACCEPTANCE CRITERIA

The implementation is complete ONLY when all of the following are true:

### Application

- [ ] Existing application still works.
- [ ] No broken existing routes.
- [ ] No broken existing APIs.
- [ ] No TypeScript errors.
- [ ] No console errors.
- [ ] No backend startup errors.

### Browser

- [ ] Real Chrome launches.
- [ ] Extension loads.
- [ ] Configured profile works.
- [ ] CAPTCHA click works.
- [ ] CAPTCHA wait works.
- [ ] CAPTCHA timeout works.
- [ ] CAPTCHA refresh/retry works.

### Portals

- [ ] Broward works.
- [ ] Hillsborough works.
- [ ] Miami works.
- [ ] Dallas works.
- [ ] Travis works.
- [ ] Harris JP works.
- [ ] Harris District works.
- [ ] Harris Clerk works.

### Data

- [ ] Excel import.
- [ ] CSV import.
- [ ] CRUD.
- [ ] Pagination.
- [ ] Sorting.
- [ ] Filtering.
- [ ] Bulk actions.
- [ ] Excel export.
- [ ] CSV export.

### Automation

- [ ] Queue.
- [ ] Sequential processing.
- [ ] Manual start.
- [ ] Automatic processing.
- [ ] Retry.
- [ ] Browser reuse.
- [ ] Portal tabs.
- [ ] Portal-specific outputs.
- [ ] Fuzzy matching.
- [ ] Guidewire.
- [ ] Failure recovery.

### UX

- [ ] Desktop.
- [ ] Tablet.
- [ ] Mobile.
- [ ] Bottom mobile navigation.
- [ ] Dark mode.
- [ ] Light mode.
- [ ] Loaders.
- [ ] Empty states.
- [ ] Error states.
- [ ] Confirmation dialogs.
- [ ] Toasts.
- [ ] Responsive tables.

### Security

- [ ] No hardcoded secrets.
- [ ] Credentials secured.
- [ ] API keys protected.
- [ ] Logs sanitized.
- [ ] Browser paths validated.

---

# 160. FINAL RULE

The most important rule of this entire implementation is:

> DO NOT BUILD A SIMPLIFIED VERSION OF THE AUTOMATION.

Build the actual production implementation.

The application must behave like the existing Power Automate solution from an input/output perspective while improving:

```text
Reliability
Security
Observability
Maintainability
Performance
Error recovery
UX
Responsiveness
Testing
Administration
```

The legacy automation is the behavioral baseline.

The existing React/Next.js + Python application is the implementation baseline.

The final application must combine both correctly.

Before finishing, perform a complete source-code audit, implementation audit, browser audit, API audit, database audit, UI/UX audit and end-to-end test.

Do not declare success based only on compilation.

The final definition of done is:

```text
REAL INPUT
   ↓
REAL QUEUE
   ↓
REAL CHROME
   ↓
REAL EXTENSION
   ↓
REAL CAPTCHA INTERACTION
   ↓
REAL PORTAL NAVIGATION
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
REAL GUIDEWIRE REQUEST
   ↓
REAL FINAL STATUS
```

Everything above must work end-to-end.