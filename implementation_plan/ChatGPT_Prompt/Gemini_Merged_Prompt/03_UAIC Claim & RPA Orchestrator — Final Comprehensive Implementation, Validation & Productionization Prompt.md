# UAIC Claim & RPA Orchestrator
## Final Comprehensive Implementation, Validation, Testing, Repair & Productionization Prompt

> **IMPORTANT:** This is an existing solution. Do **not** rebuild the application from scratch and do **not** replace working functionality unnecessarily.
>
> The primary objective is to inspect the existing implementation, understand the current architecture and behavior, identify everything that is missing, incomplete, broken, incorrectly implemented, non-functional, inconsistent, or not properly tested, and then bring the complete solution into alignment with the requirements below.
>
> Do not mark the work as complete merely because the application builds or the main happy path works. Every applicable requirement below must be implemented, tested, verified, documented, and demonstrated to work correctly.

---

# 1. EXISTING APPLICATION

Application:

**UAIC Claim & RPA Orchestrator**

Base URL:

`http://localhost:3000`

The application already contains functionality for:

- Claim management
- Queue Monitor
- County Court Portal scraping
- RPA automation
- Automation Settings
- Browser/CAPTCHA configuration
- Fuzzy matching
- Exporting
- Audit
- Health monitoring
- Exceptions
- Branding
- Notifications
- Storage and error screenshots
- Portal execution telemetry
- Guidewire-related processing

You must work with the **existing implementation and existing data model**.

Do not unnecessarily change existing database structures, APIs, workflows, routes, or behavior that are already working correctly.

---

# 2. FIRST: COMPLETE EXISTING-SOLUTION AUDIT

Before making changes:

1. Inspect the complete existing solution.
2. Understand the frontend, backend, database, APIs, RPA/browser automation, queues, settings, storage, exports, workflows, tests, skills, flows, README, and other documentation.
3. Identify existing reusable components and services.
4. Identify duplicated components that should reuse a common implementation.
5. Identify existing APIs and workflows before creating new ones.
6. Identify existing test cases and test automation.
7. Identify existing implementation-plan folder structures.
8. Identify all current supported browsers.
9. Identify the current database schema and existing data format for scraped cases.
10. Identify the existing Guidewire integration/conditions.
11. Identify all current County Court Portal configurations.
12. Identify all existing Automation Settings and how they are persisted and consumed.

### Critical rule

Do **not** assume that something works because code exists for it.

Every feature must be tested through the actual application/browser/API/workflow wherever applicable.

---

# 3. GLOBAL UI/UX REQUIREMENTS

Apply the following globally wherever applicable.

## 3.1 Dark and Light Mode

Every page must be properly tested in:

- Light mode
- Dark mode

Verify:

- Page background
- Cards
- Tables
- Forms
- Inputs
- Dropdowns
- Multi-select controls
- Buttons
- Links
- Icons
- Modals
- Popups
- Tooltips
- Charts
- Status indicators
- Export dialogs
- Loading states
- Empty states
- Error states
- Success states
- Hover/focus/active states
- Disabled states
- Scrollbars
- Any dynamically generated content

Nothing should become unreadable, invisible, incorrectly colored, overlapped, or visually broken when switching themes.

---

# 4. GLOBAL RESPONSIVENESS

Every applicable page and component must be fully responsive for:

- Mobile
- Tablet
- Desktop
- Large/big screens

And both:

- Portrait
- Landscape

Verify actual browser rendering, not only CSS source code.

Check:

- Navigation
- Header
- Sidebar
- Cards
- Tables
- Forms
- Filters
- Dropdowns
- Multi-select controls
- Modals
- Popups
- Export controls
- Buttons
- Charts
- Timeline
- Long text
- Loading indicators
- Pagination
- Horizontal/vertical scrolling
- Empty/error states

There must be no:

- Overlapping controls
- Cut-off content
- Broken layouts
- Unusable tables
- Hidden important actions
- Incorrect spacing
- Overflow problems
- Unreadable text

---

# 5. GLOBAL CLICKABLE/ACTIONABLE CONTROL TESTING

Do not test only the functionality specifically mentioned below.

Test **every clickable/actionable object**, including:

- Buttons
- Links
- Cards
- Stat cards
- Tabs
- Dropdowns
- Multi-select controls
- Checkboxes
- Radio buttons
- Switches
- Icons
- Tooltips
- Menus
- Pagination
- Sort controls
- Filter controls
- Export buttons
- Download buttons
- Refresh buttons
- Modal actions
- Close/cross buttons
- Save buttons
- Cancel buttons
- Retry buttons
- Navigation controls
- Search controls
- Form controls
- Workflow controls
- Queue controls

For each control verify:

1. It is visible where required.
2. It is clickable.
3. It performs the correct action.
4. It handles loading correctly.
5. It handles success correctly.
6. It handles failure correctly.
7. It does not produce browser console errors.
8. It does not produce backend errors.
9. It does not cause duplicate requests/actions.
10. It works in both Light and Dark mode.
11. It remains usable responsively.

---

# 6. REUSABLE COMPONENT REQUIREMENT

Not every control must have the same visual design.

Cards, buttons, tables, filters, dialogs, exports, etc. should use designs appropriate to their purpose.

However:

> Do not create separate duplicate implementations of the same functionality for every screen.

Create reusable/global components where appropriate and use those components across all applicable pages.

For example, the background export popup described below must be implemented as a reusable component and reused wherever background exports are supported.

---

# 7. `/audit`

URL:

`http://localhost:3000/audit`

Implement/fix all of the following.

## 7.1 Export

An **Export Excel** option/button must be available at the top of the page.

Export functionality must be properly tested.

## 7.2 Stat Card Filtering

When a user clicks a statistics/stat card:

- The corresponding filter must be applied to the data table.
- The table must refresh correctly.
- The selected filter must be visually understandable.
- The filtering must work with pagination.
- The filtering must work with sorting.

## 7.3 Table Sorting

Sorting must be implemented on table columns.

Do not use an incorrect generic control such as:

`sort:descending`

Use proper column-level sorting consistent with other correctly implemented tables in the application.

Test:

- Ascending
- Descending
- Multiple data types where applicable
- Pagination interaction

## 7.4 Filters

Applicable filters must support multi-select.

Verify that:

- Multiple values can be selected.
- Selected values are correctly applied.
- Filters can be cleared.
- Filters work with stat-card filtering.
- Filters work with sorting.
- Filters work with pagination.

## 7.5 Other Requirements

Verify:

- Dark mode
- Light mode
- Full responsive behavior
- Portrait
- Landscape
- All clickable/actionable controls
- Performance

Update documentation, Skills, flows, and test cases.

---

# 8. `/` DASHBOARD

URL:

`http://localhost:3000/`

## Requirements

1. Improve the dashboard.
2. Connect dashboard statistics/data to real application data.
3. Do not use fake/static values where actual data is available.
4. Ensure dashboard statistics reflect actual system state.
5. Ensure cards use the established dashboard design.
6. Verify all interactions.
7. Verify dark/light mode.
8. Verify complete responsiveness.
9. Verify all clickable/actionable controls.
10. Test performance and optimize any delays or unnecessary API/database operations.
11. Update documentation.
12. Create/register appropriate E2E test cases.

---

# 9. `/monitor`

URL:

`http://localhost:3000/monitor`

## 9.1 Statistic Cards

The statistic cards must use the same established visual language/design as the Dashboard.

Do not create a completely separate card style unnecessarily.

## 9.2 JSON Export

JSON export must be available and functional.

Verify that it produces the expected complete data.

## 9.3 Background Export Component

The existing background export popup is a good implementation and must be converted into a reusable component.

The reusable component should support quick-download buttons for:

- Excel
- CSV
- JSON

Use this reusable component on all applicable pages where background export functionality is available/required.

## 9.4 Auto Queue

**Auto Queue must be enabled by default.**

Verify that the default state is persisted and correctly respected by the workflow.

## 9.5 Other Requirements

Test:

- Dark mode
- Light mode
- Mobile
- Tablet
- Desktop
- Large screen
- Portrait
- Landscape
- All clickable/actionable controls
- Export functionality
- Queue functionality
- Performance

Update documentation, Skills, flows, and test cases.

---

# 10. CLAIM DETAIL PAGE

URL:

`http://localhost:3000/claims/e835ebcc-569d-46ce-9871-0f1a2dd195ad`

This page requires particularly thorough validation.

---

## 10.1 Telemetry Audit Popup

The Telemetry Audit popup must display **all stages** of the workflow.

For every applicable stage:

- Show the stage.
- Show its status.
- Show relevant telemetry information.
- Provide the respective screenshot when available.
- Allow the respective screenshot to be downloaded.

The screenshot storage/deletion/cleanup configuration must **not** be hardcoded here.

It must be controlled from:

**Automation Settings → Storage & Error Screenshots**

The storage cleanup/delete behavior must follow the configured policy.

It must work with:

- Local Server Storage
- Any currently supported service storage provider

Do not assume only local storage exists.

---

# 11. VIEW STAGES

Currently, clicking **View Stages** does nothing.

Fix this.

When clicked, it must perform the intended action and display the appropriate stage information.

Test:

- Normal workflow
- Completed workflow
- Failed workflow
- Partial workflow
- Empty/no-stage state
- Loading state
- Error state

---

# 12. TOP EXPORT OPTIONS — CLAIM DETAIL

The top export options must support:

### PDF

Currently working well.

Do not break it.

### Excel

Must contain all information/data that JSON contains, wherever the data can be represented in Excel.

### CSV

Must contain all available information represented by JSON in a sensible CSV-compatible structure.

### JSON

Currently working well.

Do not break it.

After modifications, compare:

- JSON
- Excel
- CSV

and verify that important/available data is not silently omitted.

---

# 13. CONCURRENT MULTI-PORTAL SCRAPING TIMELINE

There is currently UI overlap.

Fix the layout so the timeline is fully responsive according to the global responsive requirements.

Test on:

- Mobile portrait
- Mobile landscape
- Tablet portrait
- Tablet landscape
- Desktop
- Large screen

---

# 14. COUNTY COURT PORTAL SCRAPER EXECUTION STATUS

The statistic cards under:

**County Court Portal Scraper Execution Status (8 Bots)**

must use the same established dashboard card design/language.

Do not unnecessarily create a separate card implementation.

---

# 15. SCRAPED PUBLIC COURT CASES

Section:

**Scraped Public Court Cases (12 of 12)**

## 15.1 Filing Date

The Filing Date is currently not being captured correctly.

Investigate the complete data-extraction pipeline:

- Portal
- Browser automation
- DOM extraction
- Parsing
- Transformation
- API
- Database persistence
- UI display

Fix the root cause.

## 15.2 Capture All Available Columns

Do not capture only the columns explicitly listed in this prompt.

Capture **all available columns/data presented by the applicable court portal**.

If an additional column is discovered during portal execution:

- Capture it.
- Preserve it.
- Save it using the existing/current database data format.
- Make it available to existing APIs/workflows where applicable.
- Ensure it remains compatible with Guidewire processing.

Do not arbitrarily discard available case information.

## 15.3 Pagination

All available result pages must be processed.

“All” means all available items, not only the first page.

---

# 16. REMOVE `sort:descending`

The existing:

`sort:descending`

control is not working correctly.

Remove it.

Use proper column sorting in the table, consistent with correctly implemented tables elsewhere in the solution.

---

# 17. MULTI-SELECT FILTERS

All applicable filters on the claim detail page must support multi-select.

---

# 18. CLAIM AUDIT EVENTS

The claim currently says:

> No audit events recorded yet for this claim.

This is incorrect because the claim has received cases and performed multiple activities.

Investigate why audit events are not being recorded/displayed.

Verify the complete lifecycle:

1. Activity starts.
2. Activity executes.
3. Relevant event is generated.
4. Event is persisted.
5. Event is associated with the correct claim.
6. Event appears in the audit UI.
7. Event contains useful details.
8. Events remain available after page refresh.

Do not simply populate fake audit events.

Fix the actual audit-event recording mechanism.

---

# 19. BOTTOM EXPORT CASES

Under:

**Scraped Public Court Cases (12 of 12)**

## PDF

Currently working.

**Remove PDF from this section.**

## Excel

Currently working well.

Reuse the same correct implementation/logic for the top Excel export.

Do not maintain two different Excel export implementations unnecessarily.

## CSV

CSV must contain all available data, similar in completeness to JSON.

Think carefully about how nested/multi-value data can be represented in a single CSV while keeping the output usable.

## JSON

Currently working well.

Do not break it.

---

# 20. BACKGROUND EXPORT

Implement the reusable background export popup/component from:

`http://localhost:3000/monitor`

Use it on the claim detail page.

It must provide quick-download options for:

- Excel
- CSV
- JSON

The component must be reusable across all other applicable pages.

---

# 21. `/health`

URL:

`http://localhost:3000/health`

## Requirements

1. Auto Refresh must be **ON by default**.
2. Verify actual automatic refresh behavior.
3. Verify the UI in Light mode.
4. Verify the UI in Dark mode.
5. Verify complete responsiveness.
6. Test all clickable/actionable controls.
7. Test all health functionality.
8. Test performance.
9. Fix unnecessary delays.
10. Update documentation.
11. Register E2E tests.

---

# 22. `/exceptions`

URL:

`http://localhost:3000/exceptions`

## Requirements

1. Export functionality must be available.
2. Applicable filters must support multi-select.
3. Test export data for completeness.
4. Test Light mode.
5. Test Dark mode.
6. Test mobile/tablet/desktop/large screen.
7. Test portrait/landscape.
8. Test all clickable/actionable controls.
9. Test performance.
10. Update documentation.
11. Register E2E test cases.

---

# 23. `/settings`

URL:

`http://localhost:3000/settings`

Thoroughly test every tab and every setting.

---

## 23.1 Browser & CAPTCHA

Default values:

### CAPTCHA Resolution Wait

`120 seconds`

### Max Retry & Refresh Attempts

`2`

### Portal Navigation Timeout

`60 seconds`

### Page Reload Backoff Delay

The current meaning is unclear.

Do not blindly remove or change it.

First understand how this setting is currently used in the solution and align it appropriately with the intended retry/refresh behavior described in this prompt.

The behavior must be clear and documented.

### Parallel RPA Concurrency

Maximum/default selected value must be:

**10x**

Do not add support for additional browsers beyond the browsers already supported by the existing solution.

---

# 24. EMAIL & NOTIFICATION TAB

## 24.1 CC/BCC

The UI currently displays:

- No CC recipients configured
- No BCC recipients configured

Investigate why these appear.

Determine whether this represents an incorrect configuration, incorrect UI state, missing data, or intended behavior.

Fix it appropriately.

Do not simply hide the message without fixing the underlying problem.

---

## 24.2 Render Preview

There is a:

**Render Preview**

button.

There is also:

**Live Preview**

which already provides a useful preview.

Determine whether Render Preview provides any unique value.

If it is redundant and provides no meaningful functionality, remove it.

Do not keep duplicate functionality merely for the sake of having two buttons.

---

## 24.3 Live Synchronized Render Preview

The:

**Live Synchronized Render Preview**

section must only be visible after the user clicks:

**Live Preview**

It should not occupy unnecessary space when Live Preview has not been requested.

---

## 24.4 Outbound Notification Delivery History

This section must actually work.

Currently it displays:

> No notification records found in history yet. Use the "Send Test Email" console above or trigger a claim automation run to record deliveries.

Verify the complete lifecycle:

1. Send test email.
2. Trigger notification.
3. Record delivery.
4. Persist delivery history.
5. Display delivery history.
6. Display status.
7. Display relevant timestamps/details.
8. Handle failure.
9. Refresh/reload and confirm history remains available.

Do not fake records.

---

# 25. CELERY WORKER QUEUES & FAILURE ALERTS

The user is not familiar with this technology.

Do not remove or arbitrarily redesign the functionality.

Inspect the existing implementation and determine:

- Why it exists.
- What it controls.
- How it affects the application.
- Whether it is currently required.
- Whether it is correctly implemented.
- Whether the configuration is actually used.

Make the implementation appropriate to the existing architecture.

Ensure the UI is understandable enough for an administrator without requiring knowledge of Celery internals.

Document the purpose in the README/Skills/documentation.

---

# 26. SETTINGS TAB TESTING

Every Settings tab must be tested completely.

Test:

- Loading
- Saving
- Updating
- Reset/default behavior where applicable
- Validation
- Error handling
- Persistence
- Actual runtime usage
- API integration
- UI state
- Dark mode
- Light mode
- Responsive behavior

Do not accept settings that appear configurable but are not actually used by the workflow.

---

# 27. `/branding`

URL:

`http://localhost:3000/branding`

Test every tab and every function.

Verify:

- Save
- Update
- Preview
- Configuration persistence
- Actual application usage
- Dark mode
- Light mode
- Responsiveness
- Portrait
- Landscape
- All clickable/actionable controls
- Error handling
- Loading states
- Performance

Update documentation and tests.

---

# 28. GLOBAL DROPDOWN REQUIREMENT

Where a dropdown represents a filter or selection that logically supports multiple values:

**Multi-select must be supported.**

Do not add multi-select blindly to controls where only one value is logically valid.

The implementation must respect the purpose of each field.

---

# 29. GUIDEWIRE SEND CONDITION

Determine exactly:

1. What condition causes records to be sent to Guidewire.
2. Which records qualify.
3. Which records do not qualify.
4. Why a record is currently not being sent automatically.
5. Whether automatic sending is intended based on the existing workflow.
6. What configuration or status is required before sending.
7. Whether failures are recorded.

If the current behavior does not match the intended workflow, fix it.

Do not send records automatically without respecting the correct business condition.

The exact condition must be documented.

---

# 30. COUNTY COURT PORTAL NAVIGATION

When executing portal scraping:

**Always begin navigation from the configured Home URL of each County Court Portal.**

Do not directly jump into deep search URLs unless the portal workflow itself redirects there as part of the normal interaction.

The intent is to execute the portal flow as defined below and maintain the configured portal Home URLs.

Run each County Court Portal at least once and record the result.

After successful validation:

1. Update the configured portal URL where required.
2. Save the correct Home URL.
3. Perform the portal connection test.
4. Verify that the connection test succeeds.

---

# 31. PAGINATION UI

The current maximum UI pagination size is:

`100`

Increase the maximum UI page size to:

**500 records**

Do not unnecessarily load 500 records from the backend when the user has not selected that page size.

Use appropriate pagination/query behavior.

---

# 32. REMOVE UNNECESSARY FORM FIELDS

Remove the following fields from:

- New Form
- Edit Form
- Data Ingestion Column Mapping
- Excel Import Column Mapping

Fields:

- Loss Location City
- Loss Location County
- Garaging City
- Garaging State

Verify that these fields are no longer unintentionally required by:

- Validation
- API
- Import
- Database mapping
- UI
- Workflows

Do not break existing valid data processing.

---

# 33. DEFAULT COUNTY COURT PORTAL URLs

Update the default URLs exactly as follows.

| Portal | Current | Required Default |
|---|---|---|
| Broward | `https://www.browardclerk.org/Web2/` | `https://www.browardclerk.org/` |
| Hillsborough | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | `https://hover.hillsclerk.com/` |
| Miami-Dade | `https://www2.miamidadeclerk.gov/ocs` | `https://www2.miamidadeclerk.gov/ocs` |
| Travis | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | `https://odysseyweb.traviscountytx.gov/Portal/` |
| Dallas | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` |
| Harris JP | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` |
| CClerk | `https://www.cclerk.hctx.net/Applications/WebSearch/` | `https://www.cclerk.hctx.net/Applications/WebSearch/` |
| HCDistrict | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | `https://www.hcdistrictclerk.com/` |

Do not unnecessarily change URLs that are already identical.

---

# 34. AUTOMATION SETTINGS — ANTI-CAPTCHA EXTENSION

Create a separate workflow/process for installing and testing the Anti-Captcha extension through Automation Settings.

Requirements:

1. Support only browsers currently supported by the existing solution.
2. **Do not add any additional browser.**
3. All extension settings must be configurable.
4. The current configuration may be used as the default configuration.
5. Configuration must be persisted.
6. Configuration must be used by the actual automation workflow.
7. Provide a way to test the configuration.
8. Show meaningful success/failure information.

The extension must be handled as an authorized integration/configuration component of the automation system.

---

# 35. INITIAL CLAIM DATA

The system receives records manually or through Excel/CSV upload.

The starting data includes:

- Primary Key
- Claim Number — Required
- Exposure Number
- Insured First Name
- Insured Last Name
- Claimant First Name
- Claimant Last Name
- Driver First Name (Insured Vehicle)
- Driver Last Name (Insured Vehicle)
- DOL — Excel serial date or MM/DD/YYYY
- Policy State
- Loss Location State

Do not break the existing import/create-record functionality.

---

# 36. FUZZY MATCH API #1 — UNIQUE NAMES

Create/implement an API that returns the list of unique names from the following columns of uploaded/created records:

- `Insured First Name`
- `Insured Last Name`
- `Driver First Name (Insured Vehicle)`
- `Driver Last Name (Insured Vehicle)`
- `Claimant First Name`
- `Claimant Last Name`

The API must:

- Use actual database records.
- Return unique values.
- Handle duplicates correctly.
- Handle blank/null values correctly.
- Be testable from Automation Settings.
- Return a real response.
- Be documented.

---

# 37. FUZZY MATCH API #2 — PREVIOUS SOLUTION

There is an earlier implementation at:

`.\PowerAutomateSolutions\fuzzy-match-api\`

Use it as the reference.

Implement the same API behavior in the current solution.

Do not unnecessarily change its expected contract.

---

# 38. EXISTING FUZZY MATCH APIs

The current solution already has:

### Pending Matches

`GET /api/v1/matches/pending?limit=50`

### Review Match

`POST /api/v1/matches/{match_pair_id}/review`

Do not break these APIs.

Provide a very small but complete explanation of:

- What it does
- Why it exists
- How it works
- Input
- Output
- When it is used

The explanation should be understandable without requiring deep knowledge of fuzzy matching.

---

# 39. API CONFIGURATION & TESTING

All relevant API configuration must be configurable and testable from:

**Automation Settings**

The UI should provide functionality similar to API documentation/testing tools.

The user must be able to:

1. Configure the API.
2. Save configuration.
3. Test the API.
4. Receive the real response.
5. See success/failure.
6. Understand configuration errors.

Use the current exact configuration from the existing solution as the default configuration.

Do not invent fake API responses for successful tests.

---

# 40. API TEST SCENARIOS

Provide realistic test parameters covering:

### Positive scenarios

- Exact match
- Strong fuzzy match
- Different casing
- Minor spelling difference
- Formatting differences
- Common name variation

### Negative scenarios

- Clearly different names
- Empty name
- Missing required data
- Invalid parameter
- Duplicate input
- No matching result

Provide sample parameters in the Automation Settings testing UI/documentation.

---

# 41. WORKFLOW ENTRY GATE

This is critical.

The remaining automation workflows must **not start** unless all prerequisite configuration and services are:

- Configured
- Activated
- Available
- Working
- Validated

This includes the relevant:

- Browser configuration
- Anti-Captcha installation and configuration
- API configuration
- Fuzzy-match APIs
- Storage configuration
- Required authentication
- Other prerequisites required by the workflow

---

# 42. ENTRY-GATE FAILURE POPUP

The entry point for starting the workflow is the Queue Monitor page, including:

- Document upload
- Create-record workflow

If prerequisites are missing, inactive, invalid, or not working:

**Do not start the workflow.**

Instead, show a clear popup explaining:

1. What prerequisite is missing.
2. Why it is required.
3. Where to configure it.
4. What must be tested/activated.
5. What the user should do next.

Do not show a generic:

> Something went wrong.

The message must be actionable.

---

# 43. FLORIDA WORKFLOW

Portals:

- Broward
- Hillsborough
- Miami-Dade

---

## 43.1 Browser

Launch the browser selected/configured in:

**Automation Settings**

Do not introduce additional browsers.

---

## 43.2 Open Florida Portals

Open all three Florida portals in browser tabs in one browser session:

- Broward
- Hillsborough
- Miami-Dade

Navigate between the tabs according to the workflow below.

---

# 44. BROWARD WORKFLOW

Home:

`https://www.browardclerk.org/`

1. Open the Broward tab.
2. Wait for the page to fully load.
3. If it does not load correctly, refresh.
4. Click **Case Search**.
5. Verify the page loads.
6. Verify **Party Name** is selected.
7. If not selected, select it.
8. Fill:
   - Last Name
   - First Name
   - Date From
9. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA-resolution mechanism.
10. Wait for CAPTCHA resolution.
11. Verify the CAPTCHA completion state.
12. CAPTCHA visual indicators may change; do not rely on a fixed color/design.
13. If CAPTCHA verification fails:
    - Refresh the page.
    - Repeat the required steps.
14. If a **Session timeout warning** appears:
    - Click **Continue session**.
15. If the session is allowed to expire and the site returns to Home:
    - Restart from the appropriate workflow step.
16. CAPTCHA Resolution Wait is configured as:
    - `120 seconds`
17. This is the maximum CAPTCHA-resolution wait.
18. It does not mean the complete workflow should stop automatically after exactly 120 seconds.
19. If CAPTCHA is not resolved within the configured period:
    - Perform a hard refresh.
    - Retry according to:
      `Max Retry & Refresh Attempts = 2`
20. Once CAPTCHA is successfully resolved, immediately click **Search**.
21. Wait for the result page.
22. Verify whether results exist.
23. If results exist, extract all available information.
24. At minimum, capture:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Any other available columns
25. Capture all pagination.
26. Save the results in the existing/current database format.
27. Do not lose columns that were not explicitly listed in this prompt.
28. Ensure compatibility with existing APIs and Guidewire processing.
29. Return to Case Search and keep the browser tab available.
30. Move to the Hillsborough tab.

---

# 45. HILLSBOROUGH WORKFLOW

Home:

`https://hover.hillsclerk.com/`

1. Open Hillsborough tab.
2. Wait for page to fully load.
3. Refresh if required.
4. Click **Party or Business Name**.
5. Verify **Search by Party or Business Name** is selected.
6. If not, select it.
7. Fill:
   - First Name
   - Last Name
   - On or After
8. Click **Search**.
9. Wait for results.
10. If results exist, capture all available columns.
11. At minimum capture:
    - Case Number
    - Case Style
    - Case Type
    - Filled
    - Case Status
    - Citation
    - Any additional available columns
12. Capture all paginated data.
13. Save using the current database format.
14. Handle **YOUR SEARCH CRITERIA** popup if it appears.
15. Close/cross the popup.
16. Return to the appropriate starting state.
17. Keep the tab open.
18. Move to the Miami-Dade tab.

---

# 46. MIAMI-DADE WORKFLOW

Home:

`https://www2.miamidadeclerk.gov/ocs`

1. Open Miami-Dade tab.
2. Wait for the page to fully load.
3. Refresh if required.

### Login

Only perform login if the account is not already logged in.

1. Click **Register/Login**.
2. Wait for page load.
3. Enter:
   - User ID / Email
   - Password
4. Retrieve credentials from Automation Settings.
5. Click **LOGIN**.
6. Wait for page load.

### Browser Save Password Popup

A browser-generated **Save your password** popup may appear.

Handle it appropriately if it appears.

Do not depend on it appearing every time.

### Search

1. Ensure the page is:

`https://www2.miamidadeclerk.gov/ocs`

2. Click **Party Name**.
3. Click **Refresh**.
4. Fill:
   - First Name
   - Last Name
   - Filing Date Range From
5. Click **Search**.
6. Wait for results.
7. Ensure **Table View** is enabled.
8. If not enabled, enable it.
9. Extract all available data.
10. At minimum capture:
    - Local Case Number
    - State Case Number
    - Section
    - Case Type
    - Filing Date
    - Case Status
    - Any additional available columns
11. Capture all pagination.
12. Save in the existing/current database format.
13. Handle **YOUR SEARCH CRITERIA** popup if it appears.
14. Close/cross the popup.
15. Return to the appropriate search state.
16. After completion, close all Florida tabs/browser as required.

---

# 47. FLORIDA UNIQUE-NAME PROCESSING

The Florida workflow must process the unique names returned by the unique-name API.

Important:

**One unique name at a time.**

For each unique name:

1. Obtain one unique name from the API.
2. Launch/open the required Florida browser tabs.
3. Search that same name across:
   - Broward
   - Hillsborough
   - Miami-Dade
4. Complete all applicable processing for that name.
5. Save all results.
6. Close the browser completely.
7. Move to the next unique name.
8. Repeat until all unique names have been processed.

Do not process multiple unique names simultaneously within the same logical search workflow.

After Florida processing is complete, the next Queue item may belong to another state.

The workflow must determine the next queue item's applicable state/workflow.

---

# 48. TEXAS WORKFLOW

Portals:

- Travis
- Dallas
- Harris JP
- CClerk
- HCDistrict

---

# 49. TRAVIS WORKFLOW

Home:

`https://odysseyweb.traviscountytx.gov/Portal/`

1. Launch the configured/default browser.
2. Open the Travis tab.
3. Wait for page load.
4. Refresh if necessary.
5. Click **Smart Search**.
6. Verify the page loads.
7. Enter the search value in the Search Input Text box.
8. If CAPTCHA solving has not started automatically, initiate the available mechanism.
9. Wait for CAPTCHA resolution.
10. Verify completion.
11. If CAPTCHA verification fails:
    - Refresh.
    - Repeat from the appropriate step.
12. If **Session timeout warning** appears:
    - Click **Continue session**.
13. If session expires:
    - Restart from the required navigation point.
14. Use:
    - CAPTCHA Resolution Wait = `120`
    - Max Retry & Refresh Attempts = `2`
15. If CAPTCHA is not resolved within the configured period, hard refresh and retry according to the configured retry limit.
16. Once resolved, immediately click **Submit**.
17. Wait for results.
18. Extract all available data.
19. At minimum:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - All additional available columns
20. Extract all pagination.
21. Save using the existing database format.
22. Return to Travis start/search state.
23. Keep the tab open.
24. Move to Dallas.

---

# 50. DALLAS WORKFLOW

Home:

`https://courtsportal.dallascounty.org/DALLASPROD/Home/`

Follow the same overall CAPTCHA/session/retry principles as Travis.

1. Open Dallas tab.
2. Wait for page load.
3. Refresh if needed.
4. Click **Smart Search**.
5. Verify page loads.
6. Enter Search Input.
7. Handle CAPTCHA if required.
8. Apply:
   - CAPTCHA wait = `120`
   - Max retry/refresh = `2`
9. Handle session timeout using **Continue session**.
10. Click **Submit** once CAPTCHA is successfully resolved.
11. Wait for results.
12. Extract all columns.
13. At minimum:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Additional available columns
14. Extract all pagination.
15. Save using existing database format.
16. Return to appropriate starting state.
17. Keep tab open.
18. Move to Harris JP.

---

# 51. HARRIS JP WORKFLOW

Home:

`https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`

1. Open Harris JP tab.
2. Wait for page load.
3. Refresh if needed.
4. Click **Smart Search**.
5. Verify page loads.
6. Enter Search Input.
7. Handle CAPTCHA where required.
8. Apply:
   - CAPTCHA wait = `120`
   - Max retry/refresh = `2`
9. Handle session timeout.
10. Click **Submit** after successful CAPTCHA resolution.
11. Wait for results.
12. Extract all columns.
13. At minimum:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Additional available columns
14. Extract all pagination.
15. Save in current database format.
16. Return to the appropriate starting state.
17. Keep tab available.
18. Continue to CClerk.

---

# 52. CCLERK WORKFLOW

Home:

`https://www.cclerk.hctx.net/Applications/WebSearch/`

1. Open CClerk tab.
2. Wait for page load.
3. Refresh if needed.
4. Navigate to:

**COURTS → County Civil**

5. Verify the correct page loads.
6. Fill:
   - Last Name
   - First Name
   - File Date (From)
7. Click **Search**.
8. Wait for results.
9. If results exist, extract all available columns.
10. At minimum:
    - Case Number
    - Case Style
    - Case Type
    - Filled
    - Case Status
    - Citation
    - Additional available columns
11. Extract all pagination.
12. Save using current database format.
13. Handle **YOUR SEARCH CRITERIA** popup if displayed.
14. Close/cross the popup.
15. Return to appropriate starting state.
16. Keep tab open.
17. Move to HCDistrict.

---

# 53. HCDISTRICT WORKFLOW

Home:

`https://www.hcdistrictclerk.com/`

1. Open HCDistrict tab.
2. Wait for page load.
3. Refresh if required.
4. Click **Search Our Records**.
5. Verify the correct page loads.
6. Fill:
   - Last Name
   - First Name
   - File Date (From)
7. Click **Search**.
8. Wait for results.
9. Extract all available columns.
10. At minimum:
    - Case Number
    - Case Style
    - Case Type
    - Filled
    - Case Status
    - Citation
    - Additional available columns
11. Extract all pagination.
12. Save using current database format.
13. Handle **YOUR SEARCH CRITERIA** popup if displayed.
14. Close/cross the popup.
15. Return to appropriate starting state.
16. After completion, close all tabs and the browser.

---

# 54. TEXAS UNIQUE-NAME PROCESSING

Process unique names returned by the unique-name API.

For each unique name:

1. Take exactly one unique name.
2. Launch configured/default browser.
3. Open required Texas portal tabs.
4. Process the same unique name across all applicable Texas portals:
   - Travis
   - Dallas
   - Harris JP
   - CClerk
   - HCDistrict
5. Extract all results and pagination.
6. Persist all available data.
7. Close browser completely.
8. Start next unique name.
9. Continue until all unique names are completed.

Do not process multiple unique names simultaneously within the same logical search operation.

---

# 55. CROSS-STATE WORKFLOW

Cross-State workflow includes all 8 portals.

### Florida

1. Broward
2. Hillsborough
3. Miami-Dade

### Texas

4. Travis
5. Dallas
6. Harris JP
7. CClerk
8. HCDistrict

Process:

1. Launch the browser configured in Automation Settings.
2. Perform the Florida workflow.
3. Perform the Texas workflow.
4. Open all applicable portals in browser tabs as required.
5. Navigate between tabs according to the defined workflow.
6. Process one unique name at a time.
7. Complete all applicable portals for that unique name.
8. Save all results.
9. Close all tabs.
10. Close the browser.
11. Move to the next unique name.
12. Continue until all unique names are completed.

---

# 56. UNIQUE-NAME WORKFLOW RULE

This is mandatory.

The unique-name API must be called/used before launching the browser tabs for the search workflow.

The workflow must process:

**One unique name → all applicable portals → finish → next unique name**

Example:

`Unique Name #1`
→ all applicable Florida/Texas portals
→ complete
→ close browser

then:

`Unique Name #2`
→ all applicable portals
→ complete
→ close browser

Continue until complete.

---

# 57. QUEUE PROCESSING

After completing one queue item:

1. Close the browser completely.
2. Retrieve/process the next queue item.
3. Determine its applicable state/workflow.
4. Execute the correct workflow.
5. Do not assume that the next queue item belongs to the same state as the previous queue item.

---

# 58. ERROR SCREENSHOT CAPTURE

At any point during the portal workflow, if an error or stopper prevents the workflow from proceeding:

When:

**Error Screenshot Capture on Portal Scraper Failure = Enabled**

and:

**Local Server Storage = Selected**

then:

### Screenshot

Save the screenshot under:

`.\backend\screenshots`

Use:

- Unique identity
- Meaningful folder hierarchy
- Relationship to claim/queue/workflow/portal where applicable

The folder structure must make it easy for developers to locate the screenshot and for the application to display it later.

---

# 59. ERROR LOGGING

For every relevant failure:

Save detailed logs under:

`.\backend\logs`

Use:

- Unique identity
- Meaningful folder hierarchy
- Matching identifiers with the screenshot
- Claim/queue/workflow/portal context where applicable

The logs and screenshots must be easy to correlate.

For example:

`Screenshot ID X`

must be traceable to:

`Log ID X`

or an equivalent common correlation identifier.

---

# 60. STORAGE PROVIDER RULE

When:

- Error Screenshot Capture is enabled
- Local Server Storage is selected

store screenshots/logs using the configured local paths.

If another supported storage provider is selected:

- Store the files using that provider.
- Follow the provider's configured path/location.
- Maintain the same logical folder hierarchy.
- Maintain unique IDs.
- Maintain screenshot/log correlation.
- Make the data available to the application where required.

Do not implement behavior that works only for local storage.

---

# 61. DOCUMENTATION & SKILLS

After every relevant implementation change:

Update:

- Skills
- Workflows/flows
- README.md
- Relevant technical documentation
- API documentation
- Configuration documentation
- Testing documentation
- Implementation documentation

The documentation must describe:

- What was implemented
- Why it exists
- How it works
- How it is configured
- How it is tested
- Important defaults
- Important dependencies
- Important paths
- Important workflows

---

# 62. TECHNOLOGY DOCUMENTATION

For every technology/framework/library/service that is actually used:

Document briefly:

### What

What it is.

### Why

Why it is used in this solution.

### How

How it is used.

Where appropriate, include the official documentation URL.

Do not document technologies that are not actually used.

---

# 63. TEST CASE REGISTRATION

Create and register proper test cases for all implemented/fixed functionality.

Test cases must cover, where applicable:

- Positive scenarios
- Negative scenarios
- Validation
- Error handling
- Empty states
- Loading states
- Retry behavior
- Pagination
- Sorting
- Filtering
- Multi-select
- Export
- Dark mode
- Light mode
- Responsiveness
- Portrait
- Landscape
- API configuration
- API failures
- Browser automation
- CAPTCHA failures
- Session timeout
- Portal failures
- Storage failures
- Notification failures
- Queue failures
- Guidewire conditions
- Entry-gate failures

These test cases must be retained for future regression testing.

---

# 64. E2E TESTING

Perform complete end-to-end testing.

Do not stop at unit/component tests.

Where applicable, test the actual application through the browser.

The E2E process should cover:

1. Application startup.
2. Login/authentication if applicable.
3. Queue Monitor.
4. Record/document creation.
5. Automation Settings.
6. API configuration.
7. Browser configuration.
8. CAPTCHA configuration.
9. Workflow entry gate.
10. Florida workflow.
11. Texas workflow.
12. Cross-State workflow.
13. Case scraping.
14. Data persistence.
15. Audit events.
16. Telemetry.
17. Exports.
18. Notifications.
19. Health.
20. Exceptions.
21. Branding.
22. Cleanup/storage.
23. Error handling.

---

# 65. PERFORMANCE TESTING

Performance must be tested on all relevant pages and workflows.

Check for:

- Slow page loads
- Slow APIs
- Excessive database queries
- Duplicate requests
- Unnecessary re-renders
- Large payloads
- Slow exports
- Slow table rendering
- Slow pagination
- Memory leaks
- Browser automation delays
- Queue delays
- Unnecessary polling
- Excessive concurrency
- Long-running processes

Fix genuine performance problems.

Do not optimize by removing required functionality.

The application should feel responsive and fast while retaining correct behavior.

---

# 66. BROWSER CONSOLE / TERMINAL / BUILD VALIDATION

Before declaring completion, verify:

- No browser console errors
- No unhandled browser exceptions
- No React errors
- No TypeScript errors
- No lint errors where applicable
- No build errors
- No backend startup errors
- No API runtime errors
- No database errors
- No queue/runtime errors
- No failing automated tests that are related to the changes

Do not ignore warnings/errors simply because the main page renders.

---

# 67. DATA INTEGRITY

When scraping cases:

- Never silently discard available fields.
- Never overwrite valid existing data incorrectly.
- Preserve the current database format.
- Preserve compatibility with existing APIs.
- Preserve compatibility with Guidewire processing.
- Ensure Filing Date is captured.
- Ensure pagination is completely processed.
- Ensure duplicate handling is correct.
- Ensure the same case is not unintentionally inserted repeatedly.

---

# 68. NO FAKE SUCCESS

Do not:

- Fake API responses.
- Fake audit events.
- Fake notification history.
- Fake scraping results.
- Fake export data.
- Fake health status.
- Fake successful connection tests.
- Hardcode success messages when the operation actually failed.

A test is successful only when the actual functionality works.

---

# 69. DO NOT BREAK WORKING FUNCTIONALITY

When modifying an existing feature:

1. Test the current behavior first.
2. Understand why it works.
3. Make the smallest appropriate change.
4. Re-test the existing behavior.
5. Add regression coverage.
6. Verify dependent workflows.

Do not replace a working implementation merely because a different implementation appears cleaner.

---

# 70. REUSE EXISTING IMPLEMENTATIONS

Before creating anything new:

Search the existing codebase for:

- Existing export logic
- Existing Excel export
- Existing CSV export
- Existing JSON export
- Existing PDF export
- Existing background export
- Existing card components
- Existing table components
- Existing filter components
- Existing multi-select components
- Existing modal components
- Existing telemetry components
- Existing screenshot handling
- Existing logging
- Existing storage services
- Existing browser automation
- Existing CAPTCHA integration
- Existing fuzzy-match APIs
- Existing notification services
- Existing audit event services
- Existing queue services

Reuse and improve existing functionality wherever appropriate.

---

# 71. IMPLEMENTATION ORDER

Follow this order to reduce the chance of breaking the system.

## Phase 1 — Inspect

Inspect the complete solution and establish the current state.

## Phase 2 — Fix Foundation

Fix:

- Settings
- Configuration
- Storage
- APIs
- Reusable components
- Entry gate
- Logging
- Screenshot handling

## Phase 3 — Fix Data

Fix:

- Claim fields
- Import mapping
- Unique-name API
- Fuzzy matching
- Scraped data model
- Filing Date
- All-column extraction
- Pagination

## Phase 4 — Fix Automation

Implement/fix:

- Anti-Captcha configuration
- Browser configuration
- Florida
- Texas
- Cross-State
- Queue processing
- Retry/session behavior
- Storage/error capture

## Phase 5 — Fix UI

Fix:

- Dashboard
- Audit
- Monitor
- Claim detail
- Health
- Exceptions
- Settings
- Branding

## Phase 6 — Exports

Validate:

- Excel
- CSV
- JSON
- PDF where required
- Background export

## Phase 7 — Audit/Notifications/Guidewire

Validate:

- Audit events
- Notification history
- Guidewire sending condition

## Phase 8 — Testing

Run:

- Unit tests
- Integration tests
- API tests
- E2E tests
- Browser tests
- Responsive tests
- Dark/light tests
- Performance tests

## Phase 9 — Documentation

Update:

- Skills
- Flows
- README
- API documentation
- Configuration documentation
- Test documentation
- Implementation documentation

## Phase 10 — Final Regression

Run the complete solution from beginning to end again.

---

# 72. TEST OUTPUT FOLDER STRUCTURE

Maintain the existing implementation-plan folder hierarchy.

The solution already has:

- `Images` folder for images/screenshots
- `Recording` folder for recordings

Continue maintaining an organized hierarchy for:

- Screenshots
- Images
- Recordings
- Logs
- Test outputs
- Reports
- Evidence
- Other development artifacts

Do not randomly place files in unrelated folders.

The structure must allow developers to easily identify which:

- Test
- Workflow
- Claim
- Portal
- Error
- Screenshot
- Recording
- Log

belongs together.

---

# 73. FINAL VALIDATION CHECKLIST

Do not declare the task complete until all of the following have been verified.

### Application

- [ ] Application starts correctly.
- [ ] No startup errors.
- [ ] No browser console errors.
- [ ] No build/type/lint errors.
- [ ] Existing functionality remains intact.

### Dashboard

- [ ] Real data.
- [ ] Correct cards.
- [ ] Dark mode.
- [ ] Light mode.
- [ ] Responsive.
- [ ] All controls tested.
- [ ] Performance tested.

### Audit

- [ ] Excel export.
- [ ] Stat-card filters.
- [ ] Column sorting.
- [ ] Multi-select filters.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] All controls tested.

### Monitor

- [ ] Dashboard-style cards.
- [ ] JSON export.
- [ ] Background export component.
- [ ] Excel quick download.
- [ ] CSV quick download.
- [ ] JSON quick download.
- [ ] Auto Queue ON by default.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] Performance.

### Claim Detail

- [ ] Telemetry stages.
- [ ] Screenshot downloads.
- [ ] View Stages works.
- [ ] Top PDF works.
- [ ] Top Excel complete.
- [ ] Top CSV complete.
- [ ] Top JSON works.
- [ ] Timeline responsive.
- [ ] Dashboard-style scraper cards.
- [ ] Filing Date captured.
- [ ] All available columns captured.
- [ ] All pagination captured.
- [ ] Column sorting.
- [ ] Multi-select filters.
- [ ] Audit events recorded.
- [ ] Bottom PDF removed.
- [ ] Bottom Excel reused.
- [ ] Bottom CSV complete.
- [ ] Bottom JSON works.
- [ ] Background export works.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] Performance.

### Health

- [ ] Auto Refresh ON.
- [ ] Actual refresh works.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] All controls tested.
- [ ] Performance.

### Exceptions

- [ ] Export.
- [ ] Multi-select.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] All controls tested.
- [ ] Performance.

### Settings

- [ ] CAPTCHA wait = 120.
- [ ] Retry/refresh = 2.
- [ ] Navigation timeout = 60.
- [ ] Page reload backoff correctly handled.
- [ ] Parallel RPA concurrency = 10x maximum.
- [ ] CC/BCC issue investigated/fixed.
- [ ] Render Preview appropriately handled.
- [ ] Live Preview behavior correct.
- [ ] Notification history works.
- [ ] Celery tab appropriately handled.
- [ ] All tabs tested.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] Performance.

### Branding

- [ ] All tabs tested.
- [ ] All functionality works.
- [ ] Dark/light.
- [ ] Responsive.
- [ ] Performance.

### Automation

- [ ] Anti-Captcha workflow.
- [ ] Only supported browsers.
- [ ] Configurable extension settings.
- [ ] Unique-name API.
- [ ] Existing fuzzy-match APIs preserved.
- [ ] API configuration/testing.
- [ ] Positive/negative test scenarios.
- [ ] Workflow entry gate.
- [ ] Florida.
- [ ] Texas.
- [ ] Cross-State.
- [ ] Queue processing.
- [ ] Error screenshots.
- [ ] Error logs.
- [ ] Storage-provider behavior.

### Data

- [ ] Removed unwanted form fields.
- [ ] Correct portal Home URLs.
- [ ] Filing Date captured.
- [ ] All available columns captured.
- [ ] All pagination captured.
- [ ] Existing database format preserved.
- [ ] Guidewire compatibility maintained.

### Documentation

- [ ] Skills updated.
- [ ] Flows updated.
- [ ] README updated.
- [ ] API documentation updated.
- [ ] Configuration documentation updated.
- [ ] Test cases registered.
- [ ] Test outputs saved correctly.
- [ ] Folder hierarchy maintained.

---

# 74. FINAL COMPLETION RULE

**Do not say "completed", "done", "implemented", or "working" until the functionality has actually been tested.**

If anything remains:

1. Clearly identify it.
2. Explain why it remains.
3. Continue working on it if it can be fixed.
4. Re-test after fixing.
5. Run regression testing again.

If an existing implementation conflicts with these requirements, do not silently choose one.

Investigate the existing behavior, identify the root cause, make the appropriate correction, and document the final behavior.

The final result must be a **fully functional, tested, responsive, documented, maintainable, and production-ready UAIC Claim & RPA Orchestrator**, while preserving existing working functionality and avoiding unnecessary rewrites.