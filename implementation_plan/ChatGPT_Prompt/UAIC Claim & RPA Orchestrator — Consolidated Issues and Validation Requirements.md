# UAIC Claim & RPA Orchestrator — Consolidated Issues and Validation Requirements

The following issues and requirements have been identified during testing of the existing **UAIC Claim & RPA Orchestrator** solution.

The previous testing appears to be incomplete because several important functions, UI behaviors, integrations, and validations are still missing or not working correctly.

The objective is to systematically verify the entire application, fix all identified issues, identify anything else that is broken or incomplete, and ensure the solution is fully functional, responsive, performant, and consistent across all pages.

---

# 1. Global Requirements — Apply to the Entire Application

The following requirements apply to **all pages, screens, dialogs, tables, forms, components, and controls** throughout the application.

## 1.1 Functional Testing

Test every:

- Button
- Link
- Card
- Dropdown
- Multi-select dropdown
- Checkbox
- Radio button
- Toggle
- Tab
- Search box
- Filter
- Sort control
- Pagination control
- Export control
- Modal
- Drawer
- Tooltip
- Context/action menu
- Form submission
- CRUD operation
- Navigation action
- Background operation
- Queue operation
- Automation action
- Integration action

Do not limit testing only to the issues explicitly listed below.

If additional defects, missing functionality, broken functionality, inconsistent behavior, or incomplete implementation are discovered during testing, fix them as well.

---

## 1.2 Multi-Select Filters

All applicable dropdown filters throughout the application must support **multi-select**.

Users must be able to:

- Select one value
- Select multiple values
- Select all
- Clear all
- Remove individual selections
- See selected values clearly
- Apply the filter
- Reset the filter

Filtering must work correctly with:

- Search
- Sorting
- Pagination
- Cards/statistics
- Other filters

---

## 1.3 Reusable Components

Do not create separate implementations of the same functionality for every page.

Where the same functionality is required, create reusable components and use them throughout the application.

Examples include:

- Statistic cards
- Export controls
- Export progress/background popup
- Multi-select filters
- Data tables
- Pagination
- Search controls
- Sorting controls
- Status indicators
- Confirmation dialogs
- Toast notifications
- Loading states
- Error states

However, **do not force every component to have exactly the same visual design**.

Components should be reusable while still supporting page-specific configuration and appropriate UX.

---

## 1.4 Theme Validation

Test the entire application in:

- Light mode
- Dark mode

Verify:

- Page backgrounds
- Cards
- Tables
- Text
- Borders
- Icons
- Buttons
- Inputs
- Dropdowns
- Modals
- Drawers
- Charts
- Tooltips
- Pagination
- Loading states
- Error states
- Export dialogs
- Navigation
- Header
- Footer/bottom navigation

No text, control, icon, border, or background should become unreadable or visually broken when switching themes.

---

## 1.5 Responsive Design

Test every page in:

### Desktop
- 1920px+
- 1600px
- 1440px
- 1366px
- 1280px

### Tablet
- 1024px
- 900px
- 768px

### Mobile
- 600px
- 480px
- 430px
- 414px
- 390px
- 375px
- 360px

Test both:

- Landscape
- Portrait

Verify:

- No accidental horizontal scrolling
- No overlapping controls
- No clipped content
- No hidden functionality
- Tables remain usable
- Cards reflow correctly
- Forms remain usable
- Modals fit the viewport
- Drawers fit the viewport
- Charts remain readable
- Toolbars adapt correctly
- Pagination remains usable
- Navigation remains usable

Do not simply shrink the desktop UI.

Where appropriate, transform complex desktop tables into mobile-friendly layouts/cards while preserving all functionality.

---

## 1.6 Performance

Test every page for:

- Initial load time
- API response time
- Table rendering
- Filtering
- Sorting
- Pagination
- Search
- Export generation
- Background operations
- Modal opening
- Navigation
- Dashboard loading
- Large datasets

If delays, unnecessary API calls, inefficient rendering, blocking operations, memory issues, or other performance problems are discovered, fix them.

The final UI should feel fast, fluent, and responsive.

---

## 1.7 Documentation and Test Cases

Every implemented change must be reflected in the appropriate project documentation.

Also:

1. Create/update proper test cases.
2. Register the test cases in the solution's testing documentation/framework.
3. Include functional, UI, responsive, integration, performance, and regression test cases.
4. Execute the test cases.
5. Record the results.
6. Keep them available for future regression testing.

---

# 2. Home / Dashboard

**URL:** `http://localhost:3000/`

## Requirements

1. Improve the Dashboard UI and UX.
2. Connect the Dashboard to **real application data**.
3. Ensure statistics and charts represent actual backend/application data.
4. Ensure dashboard data updates correctly after underlying records change.
5. Ensure charts and statistics are meaningful and useful.
6. Test all Dashboard controls and navigation.
7. Test Light and Dark mode.
8. Test Desktop, Tablet, Mobile, Landscape, and Portrait modes.
9. Test performance and optimize where required.
10. Perform complete functional and regression testing.

---

# 3. Audit Page

**URL:** `http://localhost:3000/audit`

There are currently several issues with the Audit page.

## Requirements

1. Add/ensure the **Excel Export** button is available in the top export area.
2. Ensure export functionality is actually working.
3. Statistic cards must be clickable.
4. Clicking a statistic card must correctly filter the data table.
5. Table column sorting must work.
6. Sorting must be available directly from the table columns.
7. Add multi-select filters.
8. Filters must work correctly together with sorting and pagination.
9. Ensure all applicable columns support appropriate filtering/sorting.
10. Test Light and Dark mode.
11. Test all responsive breakpoints and orientations.
12. Test every clickable/actionable control.
13. Test performance.
14. Update documentation and test cases.
15. Perform complete end-to-end and regression testing.

---

# 4. Exceptions Page

**URL:** `http://localhost:3000/exceptions`

## Requirements

1. Add the required Export functionality.
2. Add multi-select filter dropdowns.
3. Ensure filters actually work.
4. Ensure sorting and pagination work where applicable.
5. Test Light and Dark mode.
6. Test Desktop, Tablet, Mobile, Landscape, and Portrait.
7. Test every clickable/actionable control.
8. Test performance and optimize where necessary.
9. Update documentation.
10. Register and execute test cases.
11. Perform complete end-to-end and regression testing.

---

# 5. Monitor Page

**URL:** `http://localhost:3000/monitor`

## Requirements

### 5.1 Statistic Cards

The statistic cards on the Monitor page currently do not have the same design language as the Dashboard.

Make the Monitor statistic cards consistent with the application's global Dashboard statistic-card design system.

Use a reusable component rather than creating another independent implementation.

---

### 5.2 Export Functionality

The Monitor page currently has a good **background export popup** and separate quick-download buttons for Excel and CSV.

This component is useful and should become a reusable application-wide export component.

Requirements:

- Add JSON export.
- Preserve the existing background export popup UX.
- Preserve separate quick-download buttons for:
  - Excel
  - CSV
  - JSON
- Convert the export popup/controls into a reusable component.
- Reuse this component on every page where export functionality is applicable.

---

### 5.3 Auto Queue

**Auto Queue must be enabled by default.**

Verify that:

- The default configuration is enabled.
- The UI correctly displays the enabled state.
- The backend respects the setting.
- Celery/queue processing actually advances automatically.
- Queue items are processed sequentially as intended.
- The setting remains synchronized between frontend and backend.

---

### 5.4 Additional Validation

Test:

- All buttons
- All links
- All cards
- Filters
- Sorting
- Pagination
- Export functionality
- Auto Queue
- Background operations
- Light/Dark mode
- Responsive behavior
- Performance

Update documentation and test cases and perform complete end-to-end testing.

---

# 6. Claim Detail Page

**URL:** `http://localhost:3000/claims/e835ebcc-569d-46ce-9871-0f1a2dd195ad`

This page requires a comprehensive functional and UI review.

---

## 6.1 Telemetry Audit Popup

When opening the **Telemetry Audit** popup:

1. All execution stages for the claim must be displayed.
2. Every applicable stage must be represented.
3. Each stage must show its relevant execution information.
4. Where screenshots exist, the corresponding screenshot must be downloadable.
5. Screenshot storage and cleanup policies must not be hardcoded to this page.

Storage/screenshot cleanup configuration must be available under:

**Automation Settings → Storage & Error Screenshots**

The settings must allow configuration of:

- Storage provider
- Retention policy
- Cleanup policy
- Update/change policy

The configured policy must actually control cleanup/deletion of connected storage.

It must work with:

- Local storage
- Configured external/service storage providers

---

## 6.2 View Stages

Currently, clicking **View Stages** does not appear to do anything.

Fix this.

The button must open the correct stage/telemetry view and display the relevant execution information.

Test it with:

- Successful claims
- Failed claims
- Claims with multiple stages
- Claims with scraper execution
- Claims with no available stage data

---

# 7. Claim Detail — Top Export Options

The top export section currently provides:

### PDF
Working correctly.

**Keep the existing working PDF behavior.**

### Excel
Currently does not contain all the information available in JSON.

Fix Excel export so that it contains the complete required claim information.

### CSV
Currently does not contain all the information available in JSON.

Fix CSV export so that the complete available data can be represented correctly.

### JSON
Currently working correctly and contains the complete information.

**Preserve the existing JSON behavior.**

The goal is that the export formats represent the same underlying information as completely as their formats allow.

---

# 8. Concurrent Multi-Portal Scraping Timeline

There is UI overlap in the **Concurrent Multi-Portal Scraping Timeline**.

Fix the layout so that it is fully responsive and follows the application's responsive design requirements.

Verify it on:

- Large desktop
- Desktop
- Tablet
- Mobile
- Landscape
- Portrait

No overlapping or clipped content should remain.

---

# 9. County Court Portal Scraper Execution Status — 8 Bots

The statistic cards immediately below the **County Court Portal Scraper Execution Status (8 Bots)** section do not currently match the Dashboard design.

Requirements:

1. Use the reusable statistic-card component.
2. Make the design consistent with the Dashboard.
3. Preserve appropriate page-specific information.
4. Ensure all 8 county scraper statuses are represented correctly.
5. Verify the underlying data is real and accurate.

---

# 10. Scraped Public Court Cases

In the **Scraped Public Court Cases (12 of 12)** section:

## 10.1 Missing Filing Date

The Filing Date is not being captured correctly.

Investigate the complete extraction pipeline:

**County Portal → Scraper → Parsed Data → Backend → Database → API → UI → Export**

Determine where the value is being lost.

Fix the root cause.

Do not simply add a frontend fallback.

All available required case information must be captured correctly.

---

## 10.2 Sorting

The current **Sort: Descending** button is not working correctly.

Remove this standalone sort-direction control.

Implement sorting directly on the table columns, consistent with the other tables in the application.

Users must be able to:

- Sort ascending
- Sort descending
- Understand the active sort column
- Change the sort column
- Maintain sorting while filtering/paginating where applicable

---

## 10.3 Filters

All applicable filters must support multi-select.

Ensure filters work correctly with:

- Multiple selections
- Sorting
- Pagination
- Search
- Case data

---

# 11. Audit Events on Claim Detail

The page currently shows:

> "No audit events recorded yet for this claim."

This is unexpected when the claim has already received 12 cases and multiple automation activities have occurred.

Investigate why audit events are not being recorded.

Trace the complete lifecycle:

**Claim Created → Queue → Automation → County Scrapers → Case Extraction → Fuzzy Matching → Guidewire → Notifications → Status Changes → Audit Events**

Determine which events should be recorded and ensure they are actually persisted and displayed.

Do not simply hide the "No audit events" message.

---

# 12. Claim Detail — Bottom Export Cases

Under **Scraped Public Court Cases (12 of 12)**:

### PDF

The PDF currently works well.

Remove the PDF export option from this section because PDF is already available in the top export options.

### Excel

The Excel export currently works well.

Use the same successful implementation to improve the **top Excel export** so that it contains the complete information.

### CSV

The CSV currently does not contain all information represented in JSON.

Design an appropriate CSV representation that can contain the complete available case information as effectively as CSV allows.

If the data is nested or structured, use a clear, consistent representation rather than silently dropping fields.

### JSON

JSON is working correctly.

Preserve the existing behavior.

---

# 13. Reusable Background Export Component

Implement the background export popup currently used on:

`http://localhost:3000/monitor`

as a reusable application-wide component.

It should support:

- Excel
- CSV
- JSON
- Background export processing
- Progress/status
- Success state
- Failure state
- Download action
- Quick download buttons
- Multiple simultaneous exports where appropriate

Reuse it throughout pages where export functionality is applicable.

---

# 14. Guidewire Automation

Investigate and clearly determine:

1. What is the exact condition for sending a record/case to Guidewire?
2. Which status/state triggers the Guidewire submission?
3. Which records qualify?
4. Which records are rejected and why?
5. Is Guidewire submission automatic or manual?
6. Why are qualifying records currently not being sent automatically?
7. Is the issue in:
   - Matching
   - Status transition
   - Queue processing
   - Celery
   - Configuration
   - API call
   - Retry handling
   - Validation
   - Background task
   - Database state
   - Another component?

Fix the actual root cause.

The final behavior must be clearly documented and visible through appropriate telemetry/audit information.

---

# 15. Health Page

**URL:** `http://localhost:3000/health`

## Requirements

1. Auto Refresh must be enabled by default.
2. Verify Auto Refresh actually refreshes the health information.
3. Verify the refresh interval is configurable where appropriate.
4. Test all health indicators.
5. Test all clickable/actionable controls.
6. Test Light and Dark mode.
7. Test all responsive breakpoints and orientations.
8. Test performance.
9. Update documentation and test cases.
10. Perform complete end-to-end and regression testing.

---

# 16. Settings Page

**URL:** `http://localhost:3000/settings`

The Settings page requires a complete functional review.

---

## 16.1 Default Settings — Browser & CAPTCHA

Set and verify the following defaults:

### CAPTCHA Resolution Wait

**120 seconds**

### Max Retry & Refresh Attempts

**2**

### Portal Navigation Timeout

**60 seconds**

### Page Reload Backoff Delay

The current purpose/behavior of this setting is unclear.

Do not blindly retain an unclear setting.

Investigate:

1. What this setting currently controls.
2. Where it is used.
3. Whether it is required by the automation architecture.
4. What the appropriate default should be.
5. Whether it should be renamed or better explained.
6. Whether it can be optimized for faster automation without reducing reliability.

Then implement the appropriate solution and document it.

---

# 17. Settings — Email & Notification

## 17.1 CC/BCC

The UI currently displays:

- No CC recipients configured
- No BCC recipients configured

Investigate why these are displayed.

If CC/BCC are not required by the current business requirements, do not present confusing empty-state information unnecessarily.

If they are required, provide proper configuration.

The behavior must be consistent with the notification architecture.

---

## 17.2 Render Preview

There are currently two preview concepts:

- Render Preview
- Live Preview

The Live Preview functionality already provides a useful preview.

Determine whether **Render Preview** provides any unique value.

If it is redundant, remove it.

Do not maintain duplicate functionality without a clear purpose.

---

## 17.3 Live Synchronized Render Preview

The **Live Synchronized Render Preview** section should only become visible after the user clicks **Live Preview**.

It should not occupy unnecessary space when preview mode is inactive.

---

## 17.4 Outbound Notification Delivery History

The UI currently shows:

> "No notification records found in history yet. Use the "Send Test Email" console above or trigger a claim automation run to record deliveries."

Verify that this functionality actually works.

Test:

- Send Test Email
- Successful email delivery
- Failed email delivery
- Claim-triggered notification
- Retry
- Multiple recipients
- Notification status
- Timestamp
- Provider information
- Error details
- Search
- Filter
- Sorting
- Pagination

Delivery history must contain actual persisted notification records.

Do not implement a UI-only history.

---

# 18. Settings — Celery Worker Queues & Failure Alerts

The purpose and configuration of this tab is not clear from a user perspective.

Review the complete implementation and improve it as necessary.

The system should provide an understandable and useful administration experience for:

- Celery workers
- Queues
- Worker health
- Queue health
- Failure alerts
- Retry behavior
- Background task status
- Configuration

Do not expose unnecessary technical complexity to users.

However, do not remove important operational capabilities.

Ensure that the configuration actually affects the backend behavior.

---

# 19. Settings — Complete Validation

Verify **every Settings tab**.

For every tab:

1. Every field must work.
2. Every save/update operation must work.
3. Values must persist.
4. Backend behavior must use the configured values.
5. Refreshing the page must preserve the configuration.
6. Related automation behavior must reflect changes.
7. Validation must work.
8. Error handling must work.
9. Success feedback must work.
10. Configuration changes must be auditable where appropriate.

---

# 20. Branding Page

**URL:** `http://localhost:3000/branding`

Verify every tab and every functionality.

Requirements:

1. All fields work.
2. Save/update functionality works.
3. Branding changes persist.
4. Branding changes are reflected throughout the application where applicable.
5. Light/Dark mode works correctly.
6. Responsive behavior works correctly.
7. All clickable/actionable controls work.
8. Performance is acceptable.
9. Documentation is updated.
10. Test cases are registered and executed.

---

# 21. County Court Portal Execution — Mandatory Real Validation

This is a critical requirement.

When executing/testing the County Court Portal automation, do not directly navigate to deep search URLs without first validating the real portal navigation flow.

For **each of the 8 County Court Portals**:

1. Start from the configured portal **home page**.
2. Navigate through the portal as an actual user would.
3. Navigate to the appropriate search functionality.
4. Enter the required search information.
5. Handle the portal's CAPTCHA appropriately.
6. Execute the search.
7. Find and extract the available case information.
8. Complete pagination where applicable.
9. Save the extracted data.
10. Record execution telemetry.
11. Record success/failure information.
12. Verify the scraper result.
13. Perform this validation for **all 8 portals**.

This is important because different county portals use different CAPTCHA and bot-detection mechanisms.

The automation should behave as much like a real user as technically and legally appropriate, including starting from the portal home page and following the actual navigation flow.

---

# 22. County Portal URL Validation

After successfully testing each county portal:

1. Verify the portal URL.
2. Update the configured URL if the existing URL is outdated or incorrect.
3. Store the URL through the application's configuration/settings mechanism.
4. Do not hardcode URLs unnecessarily.
5. Run the portal connection test.
6. Confirm the connection test succeeds.
7. Record the result.
8. Ensure the scraper uses the validated configuration.

This must be completed for all 8 county portals.

---

# 23. Pagination Limit

The current UI allows a maximum of only **100 records**.

Increase the maximum selectable/displayable page size to:

**500 records**

The pagination component should support appropriate page sizes up to 500 while maintaining performance.

Verify that:

- 500 records can be displayed when available.
- Sorting works with 500 records.
- Filtering works with 500 records.
- Selection works with 500 records.
- Export works correctly.
- The UI remains responsive.

---

# 24. Overall End-to-End Validation

After implementing all corrections, do not stop after checking individual pages.

Perform a complete end-to-end test of the application.

Validate the complete workflow:

**Dashboard → Claims → Queue → Automation → County Court Portals → Case Extraction → Scraped Cases → Fuzzy Matching → Guidewire → Notifications → Audit → Monitor → Health → Settings → Exports**

Verify that data and statuses remain consistent throughout the entire workflow.

---

# 25. Regression Testing

After fixing one issue, verify that the change has not broken another feature.

In particular, validate:

- Dashboard
- Claims
- Audit
- Exceptions
- Monitor
- Health
- Settings
- Branding
- County scrapers
- Queue processing
- Auto Queue
- Guidewire
- Notifications
- Telemetry
- Exports
- Theme
- Responsive layouts
- Pagination
- Filters
- Sorting

Do not consider an issue resolved if fixing it causes regressions elsewhere.

---

# 26. Final Expected Outcome

The final application must be:

- Fully functional
- Fully tested
- Responsive
- Fast
- Consistent
- Maintainable
- Configurable
- Reusable
- Production-ready

Most importantly, do not limit the work to the issues explicitly listed above.

Use the listed issues as the **minimum known defect list**.

During testing, identify and fix additional defects, incomplete functionality, broken integrations, inconsistent UI/UX, performance problems, data issues, configuration issues, and regression issues that are discovered.

Every change must be:

**Implemented → Tested → Validated → Documented → Registered as a test case → Regression tested.**