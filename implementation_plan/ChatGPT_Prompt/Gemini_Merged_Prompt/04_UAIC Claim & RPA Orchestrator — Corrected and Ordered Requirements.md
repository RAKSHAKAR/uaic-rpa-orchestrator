# UAIC Claim & RPA Orchestrator — Corrected and Ordered Requirements

## 1. `/audit` — Audit Page

**URL:** `http://localhost:3000/audit`

1. Sorting is not currently showing/available on this page. Please add/fix the sorting functionality.
2. When clicking the statistic cards, the corresponding filter is not being applied to the data table. Please fix this so that clicking each applicable stat card correctly filters the table data.
3. Export functionality for Excel and PDF is not currently showing. Please add/fix these export options.
4. Check and verify the complete UI in both Dark Mode and Light Mode.
5. Check and verify responsiveness across all supported device sizes, including:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
6. Test all clickable and actionable elements on the page, including buttons, links, cards, controls, menus, filters, exports, and any other interactive elements that have not yet been tested or were missed.
7. Update all required solution documentation with these changes. Perform complete end-to-end testing with proper documented steps, and make sure the test cases are registered for future testing.
8. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

## 2. `/` — Dashboard/Home Page

**URL:** `http://localhost:3000/`

1. Improve the dashboard and connect it with the actual/real data.
2. Check and verify the complete UI in both Dark Mode and Light Mode.
3. Check and verify responsiveness across all supported device sizes, including:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
4. Test all clickable and actionable elements on the page, including buttons, links, cards, controls, menus, and any other interactive elements that have not yet been tested or were missed.
5. Update all required solution documentation with these changes. Perform complete end-to-end testing with proper documented steps, and make sure the test cases are registered for future testing.
6. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

## 3. `/monitor` — Monitor Page

**URL:** `http://localhost:3000/monitor`

1. The statistic cards on this page do not have the same design as the cards on the Dashboard screen. Please align them with the Dashboard card design.
2. The Export JSON option is not currently showing.
3. The existing background export popup looks good, and the separate Excel and CSV quick-download buttons are also useful. Please make this export popup/download functionality a reusable component and use the same reusable component on all applicable pages where this functionality is required.
4. Auto Queue must be enabled by default.
5. Check and verify the complete UI in both Dark Mode and Light Mode.
6. Check and verify responsiveness across all supported device sizes, including:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
7. Test all clickable and actionable elements on the page, including buttons, links, cards, controls, menus, filters, exports, and any other interactive elements that have not yet been tested or were missed.
8. Update all required solution documentation with these changes. Perform complete end-to-end testing with proper documented steps, and make sure the test cases are registered for future testing.
9. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

# 4. Claim Detail Page

**URL:** `http://localhost:3000/claims/e835ebcc-569d-46ce-9871-0f1a2dd195ad`

## 4.1 Telemetry Audit and Stage Screenshots

1. In the Telemetry Audit popup, all stages must be displayed.
2. The user must be able to download the screenshot corresponding to each respective stage.
3. Storage deletion/cleanup definitions and settings must be available under:

   **Automation Settings → Storage & Error Screenshots**

4. The Storage & Error Screenshots settings must include the required change/update policy.
5. Based on the configured storage settings, deletion/cleanup must work against the connected storage.
6. The storage deletion/cleanup functionality must work with local storage as well as supported service/storage providers.
7. Deletion/Cleanup functionality must have time period selection and other important things like deletion confirmation, other validation, logs generation, etc.


## 4.2 View Stages

1. Nothing happens when clicking **View Stages**. Please fix this functionality so that it works correctly.

## 4.3 Top Export Options

The Top Export Options currently contain:

### PDF
- PDF export is working well and should remain working.

### Excel
- Excel export is not currently showing all the information that is available in the JSON export.
- Please make the Excel export include all available data, equivalent to the information available in the JSON export.

### CSV
- CSV export is not currently showing all the information that is available in the JSON export.
- Make the CSV contain all possible available data in the same CSV output/sheet, using an appropriate structure for representing the complete information.

### JSON
- JSON export is working well and is providing all the information.
- Keep the existing working JSON behavior.

## 4.4 Concurrent Multi-Portal Scraping Timeline

1. The UI is currently overlapping in the **Concurrent Multi-Portal Scraping Timeline** section.
2. Please fix the overlapping issue.
3. The section must be fully responsive according to the responsiveness requirements defined in the existing Skills.

## 4.5 County Court Portal Scraper Execution Status

1. Under the **County Court Portal Scraper Execution Status (8 Bots)** section, the statistic cards do not have the same design as the Dashboard cards.
2. Please align these cards with the Dashboard card design.

## 4.6 Scraped Public Court Cases

1. In the **Scraped Public Court Cases (12 of 12)** section, the Filing Date is not being captured.
2. Please fix the Filing Date capture.
3. Make sure all available data is captured.
4. This includes all available columns, including columns that may not have been explicitly mentioned in these requirements.
5. The captured data must continue to be saved in the existing database format because this data may already be used by existing APIs and may also be sent to the Guidewire API.

## 4.7 Table Sorting

1. The `sort:descending` button is not working correctly.
2. Add a Cases Found column just after the duration column in all data tables across the solution, and use Total Cases Found for the corresponding statistic cards.
3. Remove the `sort:descending` button.
4. Add sorting directly to the table columns, consistent with the sorting implementation used in other applicable places.

## 4.8 Filters

1. All filters must support multi-select functionality.
2. Case Found Filter must be there in all the data table.

## 4.9 Theme and Responsiveness

1. Check and verify the complete UI in both Dark Mode and Light Mode.
2. Check and verify responsiveness across:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation

## 4.10 Audit Events

1. No audit events are currently recorded for this claim.
2. Please investigate why audit events are not being displayed even though 12 cases were received and many activities were performed.
3. Fix the issue so that the appropriate audit events are recorded and displayed.

## 4.11 Bottom Export Cases

Under **Scraped Public Court Cases (12 of 12) → Export Cases**:

### PDF
- PDF export is working well.
- Remove the PDF export option from this section.

### Excel
- The Excel export in this section is working well.
- Use/implement the same working Excel export behavior in the **Top Export Options → Excel** functionality.

### CSV
- The CSV export is not currently showing all available data in the same way as JSON.
- Make the CSV contain all possible available data in the same CSV output/sheet, using an appropriate structure for representing the complete information.

### JSON
- JSON export is working well and provides all the information.
- Keep the existing working JSON behavior.

## 4.12 Background Export Popup

1. Implement the background export popup component currently available on:

   `http://localhost:3000/monitor`

2. Use this as a reusable component on the Claim Detail page.
3. Include the separate quick-download buttons for:
   - Excel
   - CSV
   - JSON
4. The same reusable component should be used wherever this export functionality is applicable.

## 4.13 Remaining Interactive Elements

1. Test all clickable and actionable elements on the page, including buttons, links, cards, controls, menus, filters, exports, tabs, popups, and any other interactive elements that have not yet been tested or were missed.

## 4.14 Documentation, Testing, and Performance

1. Update all required solution documentation with these changes.
2. Perform complete end-to-end testing with proper documented steps.
3. Register the test cases for future testing.
4. Test the page performance.
5. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

# 5. `/health` — Health Page

**URL:** `http://localhost:3000/health`

1. Auto Refresh must be enabled by default.
2. Check and verify the complete UI in both Dark Mode and Light Mode.
3. Check and verify responsiveness across:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
4. Test all clickable and actionable elements, including buttons, links, controls, menus, and any other interactive elements that have not yet been tested or were missed.
5. Update all required solution documentation with these changes.
6. Perform complete end-to-end testing with proper documented steps.
7. Register the test cases for future testing.
8. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

# 6. `/audit` — Additional Audit Requirements

**URL:** `http://localhost:3000/audit`

1. The Export Excel button must be available at the top of the page.
2. Filters must work correctly when clicking the statistic cards.
3. Sorting must be available directly on the table columns.
4. Filter dropdowns must support multi-select.
5. Check and verify the complete UI in both Dark Mode and Light Mode.
6. Check and verify responsiveness across:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
7. Test all clickable and actionable elements, including buttons, links, cards, controls, menus, filters, exports, and any other interactive elements that have not yet been tested or were missed.
8. Update all required solution documentation with these changes.
9. Perform complete end-to-end testing with proper documented steps.
10. Register the test cases for future testing.
11. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

# 7. `/exceptions` — Exceptions Page

**URL:** `http://localhost:3000/exceptions`

1. An Export option must be available.
2. Filter dropdowns must support multi-select.
3. Check and verify the complete UI in both Dark Mode and Light Mode.
4. Check and verify responsiveness across:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
5. Test all clickable and actionable elements, including buttons, links, controls, menus, filters, exports, and any other interactive elements that have not yet been tested or were missed.
6. Update all required solution documentation with these changes.
7. Perform complete end-to-end testing with proper documented steps.
8. Register the test cases for future testing.
9. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.
10. **Data Synchronization & Real Data Connection:** Fix the data discrepancy between the Dashboard and the Exceptions page. If the Dashboard statistic card shows an exception count (e.g., 2 exceptions), the Exceptions page table MUST successfully fetch and display those exact exception records. Ensure the page is fully connected to real application data and that the backend API does not silently hide, drop, or fail to load the exception logs.

---

# 8. `/settings` — Settings Page

**URL:** `http://localhost:3000/settings`

## 8.1 Default Settings

### Browser & Captcha Tab

The following values must be the default settings:

1. **CAPTCHA Resolution Wait (Seconds):** `120`
2. **Max Retry & Refresh Attempts:** `2`
3. **Portal Navigation Timeout (Seconds):** `60`
4. **Page Reload Backoff Delay (Seconds):**
   - I am not currently clear about what this setting means.
   - Please explain its purpose and make the appropriate adjustment based on the requirements already provided.
5. **Parallel RPA Concurrency:** `10x` / maximum value selected.

### Email & Notification Tab

1. **No CC recipients configured** and **No BCC recipients configured** are currently showing.
   - I do not know why these are appearing.
   - Please investigate and fix this.
2. The preview can already be viewed by clicking **Live Preview**, which is working well.
3. If the **Render Preview** button does not provide additional valuable functionality, remove it.
4. The **Live Synchronized Render Preview** section and **HTML Body Template (Responsive Email Layout)** section must be always visible based on the screensize dynamically.
5. The **Outbound Notification Delivery History** section must work properly.
Currently it shows:
   `"No notification records found in history yet. Use the "Send Test Email" console above or trigger a claim automation run to record deliveries."`
   Please investigate and make sure notification delivery history is properly recorded and displayed when notifications are actually sent.

### Celery Worker Queues & Failure Alerts

1. I am not familiar with the technology behind this tab.
2. Please handle this appropriately based on the existing solution and its actual implementation.

## 8.2 Complete Settings Testing

1. Make sure all Settings tabs are fully functional.
2. Test every setting and functionality available in all tabs.
3. Verify that all functionality works correctly.

## 8.3 Theme and Responsiveness

1. Check and verify the complete UI in both Dark Mode and Light Mode.
2. Check and verify responsiveness across:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation

## 8.4 Interactive Elements

1. Test all clickable and actionable elements, including buttons, links, tabs, controls, menus, forms, settings, previews, test actions, and any other interactive elements that have not yet been tested or were missed.

## 8.5 Documentation, Testing, and Performance

1. Update all required solution documentation with these changes.
2. Perform complete end-to-end testing with proper documented steps.
3. Register the test cases for future testing.
4. Test the page performance.
5. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

# 9. `/branding` — Branding Page

**URL:** `http://localhost:3000/branding`

1. Make sure all tabs and their functionality are fully tested and working.
2. Check and verify the complete UI in both Dark Mode and Light Mode.
3. Check and verify responsiveness across:
   - Mobile
   - Tablet
   - Desktop
   - Large/Big Screens
   - Landscape orientation
   - Portrait orientation
4. Test all clickable and actionable elements, including buttons, links, tabs, controls, menus, forms, and any other interactive elements that have not yet been tested or were missed.
5. Update all required solution documentation with these changes.
6. Perform complete end-to-end testing with proper documented steps.
7. Register the test cases for future testing.
8. Test the page performance. If any performance issue, delay, unnecessary loading, or other performance problem is found, fix it and make the page faster.

---

# 10. General Requirements

## 10.1 Multi-Select Dropdowns

1. All applicable dropdowns must support multiple selections.

## 10.2 Reusable Components

1. Not all controls, cards, buttons, etc. should have the same design.
2. Each control type should have an appropriate design.
3. Components should be reusable and shared across applicable pages/screens instead of creating separate duplicate controls for every screen.
4. The reusable component approach should be applied consistently wherever the same functionality is required.

## 10.3 Guidewire Processing

1. Determine the condition under which record(s) are sent to Guidewire.
2. Determine why records are currently not being sent automatically.
3. Fix the automatic sending behavior according to the intended conditions already defined in the solution.
4. It must be suport automatic and manual both kind of processing.

## 10.4 Documentation and Testing

1. Update the required solution documentation with all applicable changes.
2. Perform complete end-to-end testing with proper documented steps.
3. Register the test cases for future testing.

## 10.5 County Court Portal Navigation

1. While executing the workflows, make sure navigation starts from the home page of each County Court Portal.
2. From the portal home page, navigate to the respective search functionality and then perform the required case search.
3. Run all County Court Portals at least once and record the result.
4. After the portals have been successfully tested, update the County Court Portal URLs accordingly.
5. Perform the connection test after updating the URLs.
6. This is important because different County Court Portals may use different CAPTCHA mechanisms and navigation behavior.

## 10.6 Pagination

1. The maximum number of records that can be displayed in the UI through pagination must be `500`.
2. The current maximum is `100`; increase it to `500`.

## 10.7 Global Data Table Columns (Jurisdiction & Bots)
1. **JURISDICTION/BOTS Column:** Add a column strictly named `JURISDICTION` to all applicable data tables across the entire application (e.g., Claims, Queue, Audit, Scraped Cases). The rendered values for this column must explicitly display as `Florida (FL)` or `Texas (TX)` or `Others (OT)`.
2. **State-Specific Bot Columns:** Add columns named `FLORIDA BOTS` and `TEXAS BOTS` to all applicable data tables to display the respective bot execution statuses or assignments.
3. **Sorting & Filtering:** Ensure that the `JURISDICTION`, `FLORIDA`, `OTHERS` and `TEXAS` columns fully support column-level sorting and multi-select filtering.

---

# 11. Form and Data Changes

## 11.1 Remove Fields

Remove the following fields from:

- New Form
- Edit Form
- Data Ingestion Column Mapping
- Excel Import Column Mapping

Fields to remove:

1. `Loss Location City`
2. `Loss Location County`
3. `Garaging City`
4. `Garaging State`

---

# 12. Default County Court Portal URLs

Update the default URLs as follows:

| County Court Portal | Current URL | Required Default URL |
|---|---|---|
| Broward | `https://www.browardclerk.org/Web2/` | `https://www.browardclerk.org/` |
| Hillsborough | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | `https://hover.hillsclerk.com/` |
| Miami-Dade | `https://www2.miamidadeclerk.gov/ocs` | `https://www2.miamidadeclerk.gov/ocs` |
| Travis | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | `https://odysseyweb.traviscountytx.gov/Portal/` |
| Dallas | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` |
| Harris JP | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` |
| CClerk | `https://www.cclerk.hctx.net/Applications/WebSearch/` | `https://www.cclerk.hctx.net/Applications/WebSearch/` |
| HCDistrict | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | `https://www.hcdistrictclerk.com/` |

---

# 13. Automation Settings — Required Workflows and APIs

## 13.1 Anti-Captcha Extension Configuration

Create a separate workflow to install and test the Anti-Captcha extension through the Automation Settings page.

Requirements:

1. Support all browser types that are currently supported by the solution.
2. Do not add any additional browser.
3. All required extension settings must be configurable.
4. The current configuration should be used as the default configuration.
5. The installation and configuration must be testable from Automation Settings.
6. We are creating this seperately then i think while start the data processing our current workflow is checking and validating extention, pls remove from there as it will take load time and move that here, 

---

# 14. Starting Data

The records created manually or uploaded through Excel/CSV contain the following information:

1. Primary Key
2. Claim Number — Required
3. Exposure Number
4. Insured First Name
5. Insured Last Name
6. Claimant First Name
7. Claimant Last Name
8. Driver First Name (Insured Vehicle)
9. Driver Last Name (Insured Vehicle)
10. DOL — Excel serial date or `MM/DD/YYYY`
11. Policy State
12. Loss Location State

---

# 15. Fuzzy Match APIs

Create the following two fuzzy-match APIs.

## 15.1 Unique Names API

Create an API that returns the list of all unique names from the following columns of uploaded/created records:

1. `Insured First Name`
2. `Insured Last Name`
3. `Driver First Name (Insured Vehicle)`
4. `Driver Last Name (Insured Vehicle)`
5. `Claimant First Name`
6. `Claimant Last Name`

## 15.2 Existing Fuzzy Match API

1. The earlier solution already contains a fuzzy-match API under:

   `.\PowerAutomateSolutions\fuzzy-match-api\`

2. Use this implementation as the reference.
3. Implement the same API in the current solution with the same behavior.

## 15.3 Existing APIs

The current solution already implements the following APIs:

### GET

`/api/v1/matches/pending?limit=50`

### POST

`/api/v1/matches/{match_pair_id}/review`

Please explain both APIs in very small but clear detail, covering the possible **What, Why, and How** questions related to them.

---

# 16. API Configuration and Testing Requirements

For all the APIs described above:

1. All API settings must be configurable from the Automation Settings page.
2. The APIs must be testable from the Automation Settings page.
3. The API testing experience should work similarly to API documentation/testing functionality and must return the real response.
4. The current exact configuration from the existing path/configuration should be used as the default configuration.
5. Testing must include different types of positive and negative match scenarios.
6. Provide sample test parameters/data with input and expected output that can be used for testing and must represent realistic scenarios.

---

# 17. Workflow Entry Gate

The remaining workflows described below must only start when all the required prerequisites above are:

- Configured
- Activated
- Valid
- Working correctly

If any prerequisite is not satisfied:

1. The workflow should proceed with condition.
2. The Queue Monitor is the entry point for starting the application/workflow process.
3. When the user starts a workflow by uploading a document or creating a record from the **Queue Monitor** page, display a clear information popup with validation and exeception and impact of run this and even accepting all of these and forfully upload process it then work as per the validation and impact you have said to the user at the time of confirming this.
4. The popup must clearly explain what prerequisite is missing or not working and what needs to be configured/fixed.
5. Make sure all the documents must be created realeted to workflow as well with all workflow diagram(s).

---

# 18. Florida Workflow

## 18.1 Florida Portals

The Florida workflow covers:

1. Broward
2. Hillsborough
3. Miami-Dade

## 18.2 Browser Launch

1. Launch the default browser configured in the Automation Settings page.
2. Open all three Florida sites in browser tabs in parallel.
3. Navigate from one tab to another according to the workflow below.

---

## 18.3 Broward Workflow

**URL:** `https://www.browardclerk.org/`

1. Go to the Broward tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **Case Search**.
5. Verify that the Case Search page loads.
6. Verify that the **Party Name** tab is selected. If it is not selected, select it.
7. Fill in:
   - Last Name
   - First Name
   - Date From
8. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
9. Wait for the CAPTCHA resolution and successful verification.
10. The CAPTCHA tick/check appearance may vary based on the CAPTCHA mechanism and its security behavior.
11. Handle the following exceptions:
    - If CAPTCHA verification fails, refresh the browser page and repeat the required steps from the appropriate point.
    - If a **Session timeout warning** appears, click **Continue session**.
    - If **Continue session** is not selected, the portal may navigate back to the home page. In that case, restart from the appropriate point.
12. The default **CAPTCHA Resolution Wait (Seconds)** is `120`.
13. This value represents the maximum wait time for CAPTCHA resolution.
14. If CAPTCHA is not resolved within the configured time, perform a hard refresh.
15. The hard refresh/retry behavior must follow **Max Retry & Refresh Attempts = 2**.
16. Once CAPTCHA verification is successful, immediately click **Search**.
17. Wait for the results page to load.
18. Check whether results/data are available.
19. If data is available, extract all available information, including:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Any other available columns
20. Extract all paginated result data, including all available items across all result pages.
21. Save the extracted information in the database using the exact existing database format currently used by the solution.
22. The existing data format must be preserved because this data may already be used by existing APIs and may also be sent to the Guidewire API.
23. Click **Case Search** again as required and keep the Broward tab available.
24. Move to the Hillsborough tab and continue with the next workflow.

---

# 19. Hillsborough Workflow

**URL:** `https://hover.hillsclerk.com/`

1. Go to the Hillsborough tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **Party or Business Name**.
5. Verify that the page loads.
6. Verify that **Search by Party or Business Name** is selected. If it is not selected, select it.
7. Fill in:
   - First Name
   - Last Name
   - On or After
8. Click **Search**.
9. Wait for the result page to load.
10. Check whether results/data are available.
11. If data is available, extract all available information, including:
    - Case Number
    - Case Style
    - Case Type
    - Filled
    - Case Status
    - Citation
    - Any other available columns
12. Extract all paginated result data, including all available items across all result pages.
13. Save the extracted information in the existing database format.
14. Make sure all available columns are captured, including columns not explicitly listed above.
15. Preserve the existing database format because the data may be used by existing APIs and may also be sent to the Guidewire API.
16. If the **YOUR SEARCH CRITERIA** popup appears, close it using the Close/Cross action.
17. Return to the appropriate starting point and keep the Hillsborough tab available.
18. Move to the Miami-Dade tab and continue with the next workflow.

---

# 20. Miami-Dade Workflow

**URL:** `https://www2.miamidadeclerk.gov/ocs`

## 20.1 Login

1. Go to the Miami-Dade tab.
2. Wait for the page to fully load.
3. Perform the following login steps only if the account is not already logged in:
   1. Click **Register/Login**.
   2. Wait for the login page to load.
   3. Verify that the page loads correctly.
   4. Enter:
      - User ID / Email
      - Password
   5. Retrieve these credentials from the Automation Settings page.
   6. Click **LOGIN**.
   7. Wait for the page to load.

## 20.2 Browser Password Popup

1. If the browser displays a **Save your password** popup after login, close the popup.
2. The popup may or may not appear, so the workflow must be able to handle both situations.

## 20.3 Search

1. Make sure the page/tab is redirected to:

   `https://www2.miamidadeclerk.gov/ocs`

2. Click **Party Name**.
3. Click **Refresh**.
4. Fill in:
   - First Name
   - Last Name
   - Filing Date Range From
5. Click **Search**.
6. Wait for the result page to load.
7. Verify that **Table View** is enabled. If it is not enabled, enable it.
8. Check whether data/results are available.
9. If data is available, extract all available information, including:
   - Local Case Number
   - State Case Number
   - Section
   - Case Type
   - Filing Date
   - Case Status
   - Any other available columns
10. Extract all paginated result data, including all available items across all result pages.
11. Save the extracted information in the existing database format.
12. Make sure every available column is captured, including columns not explicitly listed above.
13. Preserve the existing database format because this data may be used by existing APIs and may also be sent to the Guidewire API.
14. If the **YOUR SEARCH CRITERIA** popup appears, close it using the Close/Cross action.
15. Return to the appropriate search starting point and keep the tab available as required.
16. After completing the required workflow, close all browser tabs and the browser.

---

# 21. Florida Workflow — Unique Name Processing

1. The Florida workflow must be repeated until all unique names returned by the Unique Names API have been processed.
2. The Unique Names API must be called before launching the browser tabs.
3. Process one unique name at a time.
4. For each unique name, perform the search across all applicable Florida portals:
   - Broward
   - Hillsborough
   - Miami-Dade
5. Only after completing the current unique name across all applicable sites should the next unique name be processed.
6. Continue with the second, third, fourth, etc. unique names returned by the API.
7. After the required Florida processing for one queue item is complete, close the browser completely.
8. Start the next queue item.
9. The next queue item may belong to Florida, Texas, or another applicable workflow, so its state/processing type must determine the next workflow.

---

# 22. Texas Workflow

## 22.1 Texas Portals

The Texas workflow covers:

1. Travis
2. Dallas
3. Harris JP
4. CClerk
5. HCDistrict

## 22.2 Browser Launch

1. Launch the default browser configured in the Automation Settings page.
2. Open all applicable Texas sites in browser tabs in parallel.
3. Navigate from one tab to another according to the workflow below.

---

# 23. Travis Workflow

**URL:** `https://odysseyweb.traviscountytx.gov/Portal/`

1. Go to the Travis tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **Smart Search**.
5. Verify that the page loads.
6. Enter the required value in the **Search Input** text box.
7. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
8. Wait for CAPTCHA resolution and successful verification.
9. Handle CAPTCHA verification failures by refreshing the page and repeating the required steps.
10. Handle **Session timeout warning** by clicking **Continue session** when it appears.
11. Use the configured **CAPTCHA Resolution Wait (Seconds) = 120** as the maximum CAPTCHA wait time.
12. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
13. Wait for the CAPTCHA resolution and successful verification.
14. The CAPTCHA tick/check appearance may vary based on the CAPTCHA mechanism and its security behavior.
15. Handle the following exceptions:
    - If CAPTCHA verification fails, refresh the browser page and repeat the required steps from the appropriate point.
    - If a **Session timeout warning** appears, click **Continue session**.
    - If **Continue session** is not selected, the portal may navigate back to the home page. In that case, restart from the appropriate point.
16. This value represents the maximum wait time for CAPTCHA resolution.
17. If CAPTCHA is not resolved within the configured time, perform a hard refresh.
18. The hard refresh/retry behavior must follow **Max Retry & Refresh Attempts = 2**.
13. Once CAPTCHA verification is successful, immediately click **Submit**.
14. Wait for the results page to load.
15. If results are available, extract all available data, including:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Any other available columns
16. Extract all paginated result data.
17. Save all data using the existing database format.
18. Navigate back to the Travis starting page/search point as required.
19. Keep the Travis tab available and move to the Dallas tab.

---

# 24. Dallas Workflow

**URL:** `https://courtsportal.dallascounty.org/DALLASPROD/Home/`

1. Go to the Dallas tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **Smart Search**.
5. Verify that the page loads.
6. Enter the required value in the **Search Input** text box.
7. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
8. Wait for CAPTCHA resolution and successful verification.
9. Handle CAPTCHA verification failures by refreshing the page and repeating the required steps.
10. Handle **Session timeout warning** by clicking **Continue session** when it appears.
11. Use the configured **CAPTCHA Resolution Wait (Seconds) = 120** as the maximum CAPTCHA wait time.
12. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
13. Wait for the CAPTCHA resolution and successful verification.
14. The CAPTCHA tick/check appearance may vary based on the CAPTCHA mechanism and its security behavior.
15. Handle the following exceptions:
    - If CAPTCHA verification fails, refresh the browser page and repeat the required steps from the appropriate point.
    - If a **Session timeout warning** appears, click **Continue session**.
    - If **Continue session** is not selected, the portal may navigate back to the home page. In that case, restart from the appropriate point.
16. This value represents the maximum wait time for CAPTCHA resolution.
17. If CAPTCHA is not resolved within the configured time, perform a hard refresh.
18. The hard refresh/retry behavior must follow **Max Retry & Refresh Attempts = 2**.
13. Once CAPTCHA verification is successful, immediately click **Submit**.
14. Wait for the results page to load.
15. If results are available, extract all available data, including:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Any other available columns
16. Extract all paginated result data.
17. Save all data using the existing database format.
18. Navigate back to the Dallas starting page/search point as required.
19. Keep the Dallas tab available and move to the Harris JP tab.

---

# 25. Harris JP Workflow

**URL:** `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`

1. Go to the Harris JP tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **Smart Search**.
5. Verify that the page loads.
6. Enter the required value in the **Search Input** text box.
7. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
8. Wait for CAPTCHA resolution and successful verification.
9. Handle CAPTCHA verification failures by refreshing the page and repeating the required steps.
10. Handle **Session timeout warning** by clicking **Continue session** when it appears.
11. Use the configured **CAPTCHA Resolution Wait (Seconds) = 120** as the maximum CAPTCHA wait time.
12. If CAPTCHA solving has not started automatically, initiate the available CAPTCHA resolution process.
13. Wait for the CAPTCHA resolution and successful verification.
14. The CAPTCHA tick/check appearance may vary based on the CAPTCHA mechanism and its security behavior.
15. Handle the following exceptions:
    - If CAPTCHA verification fails, refresh the browser page and repeat the required steps from the appropriate point.
    - If a **Session timeout warning** appears, click **Continue session**.
    - If **Continue session** is not selected, the portal may navigate back to the home page. In that case, restart from the appropriate point.
16. This value represents the maximum wait time for CAPTCHA resolution.
17. If CAPTCHA is not resolved within the configured time, perform a hard refresh.
18. The hard refresh/retry behavior must follow **Max Retry & Refresh Attempts = 2**.
13. Once CAPTCHA verification is successful, immediately click **Submit**.
14. Wait for the results page to load.
15. If results are available, extract all available data, including:
    - Case Number
    - Case Style
    - Case Type
    - Filing Date
    - Case Status
    - Access Level
    - Any other available columns
16. Extract all paginated result data.
17. Save all data using the existing database format.
18. Navigate back to the Harris JP starting page/search point as required.
19. Keep the Harris JP tab available and continue to the CClerk tab.

---

# 26. CClerk Workflow

**URL:** `https://www.cclerk.hctx.net/Applications/WebSearch/`

1. Go to the CClerk tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **COURTS**.
5. Click **County Civil** inside the COURTS submenu.
6. Verify that the required page loads.
7. Fill in:
   - Last Name
   - First Name
   - File Date (From)
8. Click **Search**.
9. Wait for the results page to load.
10. If results are available, extract all available data, including:
    - Case Number
    - Case Style
    - Case Type
    - Filled
    - Case Status
    - Citation
    - Any other available columns
11. Extract all paginated result data.
12. Save all data using the existing database format.
13. Make sure all available columns are captured, including columns not explicitly listed above.
14. If the **YOUR SEARCH CRITERIA** popup appears, close it using the Close/Cross action.
15. Return to the appropriate starting point.
16. Keep the CClerk tab available.
17. Move to the HCDistrict tab.

---

# 27. HCDistrict Workflow

**URL:** `https://www.hcdistrictclerk.com/`

1. Go to the HCDistrict tab.
2. Wait for the page to fully load.
3. If the page does not load correctly, refresh the page and wait again.
4. Click **Search Our Records**.
5. Verify that the required page loads.
6. Fill in:
   - Last Name
   - First Name
   - File Date (From)
7. Click **Search**.
8. Wait for the results page to load.
9. If results are available, extract all available data, including:
    - Case Number
    - Case Style
    - Case Type
    - Filled
    - Case Status
    - Citation
    - Any other available columns
10. Extract all paginated result data.
11. Save all data using the existing database format.
12. Make sure all available columns are captured, including columns not explicitly listed above.
13. If the **YOUR SEARCH CRITERIA** popup appears, close it using the Close/Cross action.
14. Return to the appropriate starting point.
15. Keep the HCDistrict tab available as required.
16. After completing the workflow, close all browser tabs and close the browser completely.

---

# 28. Texas Workflow — Unique Name Processing

1. The Texas workflow must be repeated until all unique names returned by the Unique Names API have been processed.
2. The Unique Names API must be called before launching the browser tabs.
3. Process one unique name at a time.
4. For each unique name, perform the search across all applicable Texas portals:
   - Travis
   - Dallas
   - Harris JP
   - CClerk
   - HCDistrict
5. Only after completing the current unique name across all applicable sites should the next unique name be processed.
6. Continue with the second, third, fourth, etc. unique names returned by the API.
7. After completing the current queue item, close the browser completely.
8. Start the next queue item.
9. The next queue item may belong to Florida, Texas, or another applicable workflow, so its state/processing type must determine the next workflow.

---

# 29. Cross-State Workflow — All 8 Portals

## 29.1 Launch

1. Launch the default browser configured in the Automation Settings page.
2. Perform the complete Florida and Texas activities.
3. Open all 8 County Court Portals in browser tabs in parallel.

The 8 portals are:

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

## 29.2 Processing

1. Once all sites are loaded, follow the defined Florida and Texas workflows.
2. Navigate between the portal tabs according to their respective workflows.
3. Process one unique name at a time across all applicable portals.
4. Continue until all unique names returned by the Unique Names API have been processed.
5. Close all browser tabs and close the browser after completion.

---

# 30. Cross-State Unique Name Processing

1. The Cross-State workflow must be repeated until all unique names returned by the Unique Names API have been processed.
2. Retrieve/process the unique names before launching the browser tabs.
3. Process exactly one unique name at a time.
4. Complete processing for that unique name across all applicable portals.
5. Only after the current unique name is completed should the next unique name be selected.
6. Continue with the second, third, fourth, etc. unique names.
7. Close the browser completely before starting the next queue item.
8. The next queue item may belong to a different state/workflow, so the workflow must proceed according to the queue item's actual state/type.

---

# 31. Error Screenshot and Logging Requirements

## 31.1 Error Capture

At any point during the above workflows, if an error or any other stopper prevents the workflow from continuing as expected:

1. Capture a screenshot of the page where the error/stopper occurred.
2. Save the screenshot under:

   `.\backend\screenshots`

3. Assign a unique identity to the screenshot.
4. Maintain a proper folder hierarchy so that the development team can easily identify and locate screenshots later.
5. The screenshot structure should also allow the application to display/use the screenshots for error investigation, similar to the existing implementation on the Claim Detail page:

   `http://localhost:3000/claims/e835ebcc-569d-46ce-9871-0f1a2dd195ad`

## 31.2 Error Logs

1. Always save detailed logs for the error under:

   `.\backend\logs`

2. Assign a unique identity to the logs.
3. Maintain a folder hierarchy that allows the development team to easily identify and locate the logs.
4. The log structure should allow the logs to be matched with the corresponding screenshot.
5. The logs should also be usable by the application wherever error details are displayed, similar to the existing Claim Detail page implementation.

## 31.3 Storage Configuration Conditions

1. Screenshot and log storage behavior must follow the configured **Error Screenshot Capture on Portal Scraper Failure** setting.
2. When:
   - **Error Screenshot Capture on Portal Scraper Failure = Enabled**
   - **Local Server Storage = Selected**
   
   both conditions being true, save the screenshots and logs under the configured local server locations:

   - `.\backend\screenshots`
   - `.\backend\logs`

3. If Local Server Storage is not selected and another storage provider is configured, store the screenshots/logs under the selected storage provider's configured path.
4. Regardless of the selected storage provider, maintain the same logical folder hierarchy.
5. The hierarchy must allow screenshots and logs to be easily identified and matched for debugging and application display.

---

# 32. Skills, Flows, Documentation, and Testing Records

1. Always update the relevant Skills after making these changes.
2. Update the applicable workflow/flow definitions.
3. Update the README file.
4. Update all other required solution documentation.
5. Create and maintain the correct test cases.
6. Perform the required testing.
7. Save the testing output in the correct location.
8. Maintain the expected testing-output folder hierarchy.
9. The existing `implementation_plan` structure contains:
   - `Images` folder for images
   - `Recording` folder for recordings
10. Continue maintaining the appropriate folder hierarchy so that development teams can easily identify and locate:
    - Screenshots
    - Images
    - Recordings
    - Logs
    - Test outputs
    - Other debugging/testing artifacts
11. No manual test required, Everything must be automated and vedio and screenshot evidence recorded as per abvoe defination(s).

The folder hierarchy must always be maintained consistently for proper development identification, debugging, testing, and future reference.

# 33. Concurrency & Execution Engine Rules

## 33.1 Enforce Parallel RPA Concurrency Limit
1. The backend execution engine MUST dynamically respect the "Parallel RPA Concurrency" setting defined in the Automation Settings UI. 
2. If concurrency is set to 10, the orchestrator (e.g., Celery or Python `asyncio`) must process exactly 10 queue items simultaneously using asynchronous processing (e.g., `asyncio.gather` with a semaphore), rather than a sequential `for` loop.

## 33.2 Strict Visual Concurrency in Attended Mode
1. When "Attended Mode" is enabled and concurrency is set higher than 1, the scraping framework (e.g., Playwright) MUST launch entirely separate, distinct, and visible GUI Browser Instances for each parallel worker. 
2. It must NOT use hidden background contexts or headless tabs. 
3. If concurrency is 10, the user must physically see 10 separate Chrome windows executing simultaneously on their desktop monitor. Ensure secondary workers are not defaulted to headless mode.

## 33.3 Resource-Optimized Concurrency in Unattended Mode
1. When "Unattended Mode" is enabled, the scraping framework MUST execute entirely in the background without rendering a graphical user interface (GUI).
2. The framework (e.g., Playwright) MUST utilize `headless=True` for all browser instances to optimize server CPU and memory allocation.
3. To maximize efficiency when the concurrency setting is high (e.g., 10x), the framework should utilize isolated Browser Contexts (which share a single underlying browser process) rather than launching 10 entirely separate heavy OS-level browser executables, while strictly ensuring data and cookie isolation between contexts.

# 34. Global Performance & UI Loading Architecture

## 34.1 Component-Level Loading States (Skeleton Loaders)
1. **Remove Silent Loading:** Do not rely solely on a single global refresh icon to indicate that data is being fetched or refreshed.
2. **Skeleton UI:** Implement skeleton loaders (pulsing placeholder blocks) for all specific UI components—including Statistic Cards, Data Tables, and Graphs—across the Dashboard and all other pages. 
3. **Visual Feedback:** When a user triggers a refresh (or during the initial page load), the specific components awaiting data must display these skeleton loaders or localized spinners so the user explicitly knows which parts of the page are updating.

## 34.2 Lazy Loading & Code Splitting
1. Implement React lazy loading (e.g., `React.lazy` and `<Suspense>`) for heavy UI components like charts, large tables, and modals to ensure the initial page frame loads instantly.
2. Ensure that non-critical components are loaded asynchronously so they do not block the main UI thread.

## 34.3 Data Fetching & Backend Optimization
1. **API Speed:** Dashboard aggregation queries must be optimized at the backend level. Ensure the database utilizes proper indexing for counting claims, matches, and exceptions so the API responds rapidly.
2. **State Management Optimization:** Utilize modern data-fetching libraries (e.g., TanStack Query / React Query) to cache data, deduplicate requests, and handle background refetching smoothly without locking up the UI.
3. Apply these speed optimizations and rendering improvements not just to the Dashboard, but globally across all pages (`/audit`, `/monitor`, `/exceptions`, `/claims`, etc.).

# 35. Global Interactivity & Event Handling

## 35.1 Dashboard & Global Statistic Cards
1. **Actionable Cards:** All statistic cards on the Dashboard (and across other pages like `/audit`, `/monitor`) MUST be fully clickable and actionable.
2. **Dynamic Filtering:** Clicking a specific statistic card (e.g., "Manual Exceptions", "Completed Scrapes") must immediately apply the corresponding filter to the data table on that page, or navigate the user to the relevant page with the data pre-filtered. 

## 35.2 Global Tables, Sorting, Filters & Pagination
1. **Pagination Controls:** Pagination must be completely functional across all tables. Users must be able to navigate between pages (Next, Previous, First, Last) and dynamically change the number of rows displayed per page (up to the defined maximum of 500).
2. **Fully Wired Controls:** Every single table element—including all multi-select filters, column sorting toggles (ascending/descending), and export buttons (Excel, CSV, PDF, JSON)—MUST be connected to the real backend data state and work perfectly.

## 35.3 Search Bars, Tabs, Modals, and Tooltips
1. **Search Inputs:** Any search bar or query input across the application must correctly filter the respective dataset either in real-time or upon submission.
2. **Tabs and Navigation:** Navigating between tabs (e.g., on the Settings or Branding pages) must instantly render the correct sub-components. 
3. **Modals and Popups:** Opening and closing modals, popups, or side-drawers (like the Export popups or Exception details) must work flawlessly without trapping the user or failing to load data.
4. **No "Dead" UI:** There must be zero "mock" or unresponsive interactive elements. If a button, filter, card, control, or link is visible anywhere in the UI, it must perform its intended function flawlessly.

# 36. Global CAPTCHA Execution & Human-Like Interaction Logic

## 36.1 Dynamic Presence Detection & Sequencing
1. **Check for Existence & Fill Data First:** On every portal search page, the automation must dynamically check if a CAPTCHA widget exists. If it does, the system must emulate a human by filling out all required search data (First Name, Last Name, Dates) *before* attempting to interact with or solve the CAPTCHA.

## 36.2 Proactive Triggering (Anti-Blind Wait)
1. **Monitor Auto-Start:** Once the data is filled, the automation must check if the Anti-Captcha extension has automatically started the solving process. 
2. **Manual Human Trigger:** If the solving process does NOT start automatically within a few seconds, the bot MUST NOT wait blindly. It must act like a human operator and physically simulate a click directly on the CAPTCHA checkbox/widget to manually trigger the extension's solving sequence.

## 36.3 Strict Verification & Submission Enforcement
1. **Strict Submission Gate:** The automation must wait for the definitive "solved/verified" status from the CAPTCHA widget. Under no circumstances should the system click the "Search" or "Submit" button before the CAPTCHA is positively confirmed as fully solved. 
2. **Settings Compliance:** The waiting period must strictly respect the `CAPTCHA Resolution Wait (Seconds)` setting. If the timeout is reached or verification fails, it must utilize the `Max Retry & Refresh Attempts` setting (e.g., performing a hard refresh and starting the sequence over).

## 36.4 Human-Like Resilience Goal
1. **Adaptive Extraction:** The overriding goal of the scraping engine is to think and act like a pure human operator. It must adapt to UI delays, pace interactions naturally, and persistently aim to extract the claims data if it is available, rather than throwing rigid technical exceptions when a simple human interaction (like clicking a stalled checkbox) would solve the problem.

# 37. Batch Ingestion & Idle Queue Management

## 37.1 Batch Upload Tracking (Excel/CSV)
1. **Unique Batch ID:** Whenever a user uploads a bulk Excel or CSV file, the backend MUST generate a unique `Batch ID` (UUID) and record the original `Filename` and `Upload Timestamp`.
2. **Data Tagging:** Every single claim record extracted and created from that file must be securely tagged with this `Batch ID` and `Filename` in the database.
3. **UI Filtering:** All data tables (Queue, Claims, Audit, Exceptions) and Dashboard statistic cards must include a filter for `Batch ID` or `Filename`. This allows the user to easily isolate, track, and export the exact progress and results of a specific uploaded file without mixing it up with manual entries or past uploads.

## 37.2 Queue Depletion & System Idle State
1. **Continuous Listening:** The orchestration engine (e.g., Celery workers) must be designed as a continuous background service. When the pending queue drops to `0` (all search and extraction tasks are completed), the system MUST NOT crash, terminate, or stop the background worker processes.
2. **Graceful Idle State:** Instead, the workers must enter a lightweight "Idle/Listening" state. The UI Dashboard should accurately reflect this state (e.g., showing "0 Pending in Queue" and "Workers Idle - Waiting for Data").
3. **Seamless Resumption:** The moment a new file is uploaded or a new manual record is created, the idle workers must instantly detect the new items in the queue and resume processing automatically without requiring any manual server restarts or service reboots.


# 38. Exception Handling & Retrigger Lifecycle

## 38.1 In-Flight vs. Post-Failure Retries
1. **In-Flight Retries:** During active execution, the automation must strictly use the existing `Max Retry & Refresh Attempts` setting (e.g., 2 attempts) for immediate page reloads if an element fails to load or a CAPTCHA errors out.
2. **Post-Failure State:** If a claim completely fails after exhausting its in-flight retries, the system must immediately capture the error screenshot/log, flag the record as `Failed`, and route it to the Exceptions Queue.

## 38.2 Automated Retrigger Logic
1. **Auto-Retrigger Settings:** The Automation Settings page MUST include an "Auto-Retrigger Failed Claims" toggle and a "Max Global Retries per Claim" numeric input (e.g., default value of 1).
2. **Cool-Down Period:** If auto-retrigger is enabled, the system must wait a configurable cool-down period (e.g., 30 minutes or 24 hours or 1 day or 1 month) before automatically pushing a failed claim back into the active queue. This prevents the bot from spamming a portal that is temporarily down.
3. **Infinite Loop Prevention (Hard Exceptions):** Once a claim hits the "Max Global Retries per Claim" limit, it must be permanently flagged as a "Hard Exception." The system MUST NOT automatically retrigger Hard Exceptions.

## 38.3 Manual UI Retriggering
1. **Bulk & Individual Retriggering:** The Exceptions page and all relevant data tables must include functional "Retrigger" buttons (both for individual rows and a bulk "Retrigger Selected" action). 
2. **State Reset:** When a user manually retriggers a claim, the system must reset the claim's internal retry counter, update its status from `Failed` back to `In Progress/Queue`, and immediately push it to the active execution fleet.

## 38.4 Retry Audit Logging & Diagnostics
1. **Attempt Tracking:** The system MUST log every single retry attempt independently. The logs must clearly identify the current attempt number (e.g., "Attempt 2 of 3") and the specific output, error, or exception thrown during that exact iteration.
2. **Diagnostic Snapshotting:** A full-page screenshot and DOM state log must be captured and saved for *every* failed attempt (both in-flight retries and hard failures), ensuring no diagnostic data is overwritten or lost.
3. **Traceability:** These granular retry logs and screenshots must share a correlation ID linked to the specific claim and batch. This ensures the Exceptions UI can display a complete, chronological timeline of every failure and retry attempt for a given record.

# 39. Storage Retention, Disk Hygiene & Automated Cleanup

## 39.1 Storage & Error Screenshots Settings UI
1. **Retention Period Setting:** Under `Automation Settings → Storage & Error Screenshots`, provide a configurable numeric input: **"Retention Period for Error Screenshots & Diagnostic Logs (Days)"** (default: `180` days).
2. **Auto-Purge Toggle:** Provide an **"Enable Automatic Background Cleanup"** toggle switch (default: `Enabled`).
3. **Storage Target Selection:** Support target switching between Local Disk (`.\backend\screenshots` and `.\backend\logs`) and configured Cloud/External Storage providers.
4. **Manual Trigger Action:** Provide a **"Run Cleanup Now"** button with a confirmation modal showing disk space freed and total files removed.

## 39.2 Backend Automated Purge Mechanism
1. **Scheduled Cleanup Task:** The orchestrator must run a scheduled background worker (e.g., daily Celery Beat / Cron task) that scans diagnostic directories.
2. **Safe Deletion:** The background job must permanently delete screenshots, DOM dumps, and detailed attempt logs whose creation timestamp exceeds the configured retention window (e.g., older than 180 days).
3. **Audit Log Retention:** Core database audit records (metadata, claim status, timestamps, and error summaries) must be preserved for historical reporting; only heavy image files and raw HTML diagnostic logs are purged.
4. **Purge Logging:** The engine must generate an audit record for every cleanup run detailing execution time, number of files purged, and disk space reclaimed.

---

# 40. Portal Outage Alerting & Consecutive Failure Monitoring

## 40.1 Outage Alert Configuration (Settings UI)
1. **Failure Threshold Input:** Under `Automation Settings → Email & Notification Tab` (or `Celery Worker Queues & Failure Alerts`), provide a numeric input: **"Consecutive Portal Failure Threshold"** (default: `5` consecutive failures).
2. **Outage Detection Window:** Provide a configurable timeframe setting: **"Portal Outage Evaluation Window (Minutes)"** (default: `15` minutes).
3. **Alert Recipients:** Include a multi-email recipient field strictly designated for **"Portal Outage & Infrastructure Alerts"**.
4. **Auto-Pause Option:** Provide a toggle switch: **"Auto-Pause Scraping on Portal Outage Detection"** (default: `Enabled`).

## 40.2 Backend Outage Evaluation & Notification Logic
1. **Per-Portal Tracking:** The orchestrator must maintain an isolated consecutive failure counter for each of the 8 county portals independently.
2. **Alert Trigger:** If any single portal records consecutive failures reaching or exceeding the configured threshold within the evaluation window (e.g., 5 consecutive portal timeouts, 500-series HTTP errors, or Cloudflare blocks), the system must flag that portal as `CRITICAL_OUTAGE`.
3. **Instant Email Dispatch:** An immediate high-priority alert email must be dispatched to the configured recipients containing:
   - Specific County Portal Name & URL.
   - Exact failure pattern (e.g., "Portal Unresponsive", "Continuous CAPTCHA Block", or "HTTP 503 Service Unavailable").
   - Timestamp and affected Claim Numbers / Batch IDs.
   - Total consecutive failure count and screenshot link of the latest failure.
4. **Protective Worker Backoff:** If "Auto-Pause" is enabled, the queue runner must temporarily suspend requests directed at the affected portal for a configured quarantine period (e.g., 60 minutes) to prevent IP banning, while allowing workers to continue processing claims across healthy portals.

# 41. Dynamic System Identity & Browser Paths

## 41.1 Dynamic Executable Location Display
1. **Live Path Resolution:** The Automation Settings UI (specifically within the Browser & Captcha Tab) MUST dynamically display the exact physical file path of the browser executable that the automation engine is actively using to run the bots.
2. **No Hardcoding:** Similar to the dynamic Browser User-Agent string display, the "Executable Location" must not be a static or hardcoded string. The frontend must fetch this path directly from the backend automation framework upon loading.
3. **Fallback Accuracy:** If the backend falls back to an internal Playwright Chromium binary because the default system browser is missing, the UI must dynamically update to reflect the actual fallback path being utilized by the active workers.

# 42. Advanced Anti-Bot Evasion & Human Behavior Emulation

## 42.1 Biometric Pacing & Jitter
1. **Randomized Delays:** The bot MUST NOT execute actions (clicking, navigating) at exact, robotic intervals. It must inject randomized "jitter" (e.g., waiting anywhere between 800ms and 2400ms) between page loads and interactions.
2. **Human Keystroke Emulation:** When filling out search inputs (First Name, Last Name), the bot must simulate human typing by adding random delays between keystrokes (e.g., 50ms to 150ms per character), rather than pasting the entire string instantly.
3. **Cursor Emulation (Where Applicable):** When interacting with strict portals, the framework should utilize bezier-curve mouse movements to simulate a human dragging a physical mouse, rather than instantly teleporting the cursor to the "Submit" button.

## 42.2 Browser Fingerprint Masking
1. **Webdriver Obfuscation:** The automation framework MUST utilize stealth plugins (e.g., `playwright-stealth`) to strip the `webdriver=true` flag from the browser environment, preventing county WAFs from instantly detecting the automated session.
2. **Consistent Profiles:** If a specific queue item encounters a CAPTCHA, it must maintain the exact same session, cookies, and browser fingerprint (User-Agent, Canvas hash) for the duration of that claim's execution to avoid raising security flags.

---

# 43. Proxy Management & IP Rotation (Anti-Ban Protection)

## 43.1 Proxy Pool Integration
1. **Dynamic Proxy Support:** The backend execution engine must natively support routing traffic through a residential or datacenter proxy pool. 
2. **Settings UI Integration:** The Automation Settings page MUST include a section for "Proxy Configuration" (e.g., Proxy URL, Username, Password, and a toggle to Enable/Disable proxies).
3. **Per-Worker IP Allocation:** When running at high concurrency (e.g., 10x), the orchestrator must assign a unique IP address to each individual worker context. 10 bots must appear as 10 different users from 10 different locations, rather than 10 requests coming from the same server IP.

## 43.2 IP Ban Detection & Auto-Rotation
1. **Soft-Block Detection:** If a portal returns an "Access Denied", "IP Banned", or HTTP 403 Forbidden error, the worker must immediately identify this as an IP block, rather than a standard page failure.
2. **Automatic IP Release:** Upon detecting a ban, the worker must dump the compromised proxy IP, request a fresh IP from the proxy pool, and retry the claim without failing the entire batch.

---

# 44. Disaster Recovery & State Healing (Crash Resilience)

## 44.1 Stale State Recovery (Orphaned Tasks)
1. **Dead Worker Detection:** If the physical server crashes, loses power, or a Celery worker is unexpectedly killed (OOM error), claims currently being processed will be left permanently stuck in the `In Progress` state. 
2. **Auto-Healing Cron:** The backend must implement a state-healing mechanism (e.g., a background job running every 15 minutes) that looks for claims stuck in `In Progress` longer than a realistic timeout threshold (e.g., 20 minutes). 
3. **Safe Requeue:** The system must automatically revert these orphaned claims back to `Pending/Queue` so they can be picked up by a healthy worker upon system reboot, ensuring zero data loss.

## 44.2 Idempotent Executions
1. **Duplicate Prevention:** The extraction engine must be idempotent. If a crashed claim is restarted, the system must ensure it does not insert duplicate court cases into the database for the same claim if it had partially saved them before the crash.

---

# 45. Adaptive Extraction & Data Normalization

## 45.1 Fuzzy Column Mapping (UI Shift Protection)
1. **Dynamic Header Parsing:** County portals frequently make minor updates (e.g., renaming "Case Status" to "Status", or "File Date" to "Date Filed"). The scraper must NOT rely on strict, hardcoded string matching for table headers.
2. **Fuzzy Matching Logic:** The extraction engine must use fuzzy string matching (e.g., RapidFuzz) or regex aliases to identify the correct columns during extraction. If the UI changes slightly, the bot must adapt and extract the data anyway instead of failing.

## 45.2 Data Cleansing & Standardization
1. **Whitespace & Artifact Stripping:** The bot must automatically strip hidden HTML artifacts, newline characters (`\n`), and excess whitespace from extracted text before saving it to the database.
2. **Date Normalization:** Regardless of how the county portal formats the filing date (e.g., `Jan 05, 2024`, `2024-01-05`, or `01-05-24`), the backend must normalize all extracted dates into a consistent `MM/DD/YYYY` or standard ISO format in the database for seamless Guidewire integration.

---

# 46. Enterprise Security & Execution Scheduling

## 46.1 Execution Scheduling (Business Hours Pacing)
1. **Schedule Configuration:** The Automation Settings MUST include an "Execution Schedule" interface allowing administrators to define allowed operating hours (e.g., Monday-Friday, 8:00 AM to 6:00 PM EST).
2. **Human-Like Working Hours:** If enabled, the orchestrator must automatically pause queue processing outside of these hours. Running bots 24/7, especially at 3:00 AM on weekends, is a massive red flag for county WAFs. Respecting business hours perfectly emulates human paralegal behavior.

## 46.2 Credential Vaulting & Encryption
1. **Encrypted Storage:** Sensitive data inputted in the Settings UI—specifically the Miami-Dade portal password, Proxy pool passwords, and any API keys—MUST be encrypted at rest in the database (e.g., using AES-256). 
2. **No Plaintext Logs:** The backend must strictly mask or redact these passwords in all terminal outputs, debugging logs, and UI displays (showing `••••••••` instead of the plaintext string).

# 47. Advanced Multi-Bot Evasion & Proxy Configuration UI

## 47.1 Proxy Configuration Settings (UI)
1. **Proxy Settings Section:** The Automation Settings page MUST include a dedicated section for "Network Evasion & Proxies."
2. **Provider Selection:** Include a "Proxy Provider" dropdown/card design menu. 
   - This must default to **"Internal/Default Proxy"** (using the system's built-in routing-must be fully working and tested and test button must be there to test and see the response).
   - It must also include options for major external providers (e.g., `Oxylabs`, `Smartproxy`, `BrightData`, `IPRoyal`) and a `Custom External` option.
3. **Required Fields:** When an external or custom proxy is selected, the UI must expose the following configurable inputs:
   - **Proxy Pool URL/Host:** (e.g., `pr.oxylabs.io` or `gate.smartproxy.com`)
   - **Proxy Port:** (e.g., `7777`)
   - **Authentication:** Username and Encrypted Password fields with an eye icon to toggle visibility and see the actual password.
   - **Proxy Type Dropdown:** Select between `Residential`, `Datacenter`, or `Mobile` IP networks.
4. **Sticky Session Toggle:** Add a toggle for "Sticky IPs per Claim" (Default: Enabled). This ensures that while a single worker is processing a claim, its IP address does not change mid-session (which would trigger a CAPTCHA or sudden logout).

## 47.2 Per-Worker Device Spoofing (10x Isolation)
1. **Hardware & Network Isolation:** When "Parallel RPA Concurrency" is set higher than 1 (e.g., 10x), the orchestrator MUST NOT allow the workers to share network signatures.
2. **Context Evasion:** For every parallel worker spawned, the Playwright engine must strictly isolate the `BrowserContext` by assigning it:
   - A unique IP address routed through the configured proxy pool.
   - A unique, randomized User-Agent string.
   - A randomized viewport (screen resolution) to spoof different device monitors.
3. **Cache & Cookie Silos:** Each of the 10 parallel bots must maintain completely isolated cookie jars and cache storage. If Worker 1 triggers a security flag, Worker 2 must remain completely unaffected.

# 48. Legal Data Provenance & Metadata Tagging
1. **Extraction Fingerprinting:** Every successfully scraped court case MUST be appended with a hidden provenance metadata object in the database.
2. **Required Metadata:** This object must record the exact UTC and local timestamp of the successful extraction, the specific Proxy IP address utilized, the final executed URL of the county search results, and the version of the scraping script used.
3. **Export Inclusion:** When exporting claims via JSON (and optionally Excel/CSV), this provenance metadata must be included to serve as a legal audit trail of when the public record was accessed.

# 49. Live Infrastructure Telemetry (Monitor UI)

## 49.1 Resource Dashboards & Metrics
1. **Resource Dashboards:** The `/monitor` or `/health` page MUST include live telemetry widgets tracking the hardware utilization of the execution engine.
2. **Metrics Required:** Display the real-time CPU percentage, RAM consumption, and Active Thread count of the Celery workers and the Playwright browser processes.
3. **OOM Warning:** The UI should visually warn the user (e.g., turning yellow or red) if the RAM consumption approaches the server's maximum threshold, allowing the user to dynamically lower the Concurrency setting before a crash occurs.

## 49.2 Granular Active Worker Status Grid (10x Concurrency Tracking)
1. **Real-Time Worker Table:** The `/monitor` page MUST feature an "Active Execution Fleet" data grid that dynamically displays rows for each concurrent slot (e.g., Worker 1 through Worker 10).
2. **Required Worker Attributes:** For every active slot, the grid must display:
   - **Worker ID & State:** (e.g., `Worker-04` — `Active` or `Idle`)
   - **Assigned Claim Number:** (The specific claim currently being parsed)
   - **County Portal in Execution:** (e.g., `Miami-Dade` or `Broward`)
   - **Current Lifecycle Stage:** (e.g., `Navigating`, `Solving CAPTCHA`, `Data Extraction`, or `Committing to DB`)
   - **Assigned Proxy IP & Type:** (The unique residential/datacenter IP address bound to that isolated `BrowserContext`)
   - **Elapsed Runtime:** (How long that specific claim has been processing in the current thread)
3. **Live Auto-Refresh:** This worker grid must poll the backend via WebSockets or short configurable intervals (default: 30 seconds) so administrators can instantly identify bottlenecks, stuck CAPTCHAs, or proxy connection lags across individual bots.

# 50. Targeted Portal Maintenance Mode
1. **Individual Portal Toggles:** The Automation Settings MUST include a "Targeted Maintenance Mode" section listing all 8 county portals individually with active/inactive toggle switches.
2. **Selective Bypassing:** If a specific county portal undergoes a major UI overhaul and breaks the scraper, an administrator can toggle that specific portal to "Maintenance Mode."
3. **Queue Routing:** The orchestrator must gracefully skip any queue items requiring a portal that is in Maintenance Mode, leaving them safely in the `Pending` state, while continuing to process all claims associated with the remaining healthy portals.

# 51. Dashboard Executive Analytics, Time Tracking & Managerial Reporting

## 51.1 Dashboard Date & Batch Scoping Controls
1. **Global Timeframe Selector:** The primary Dashboard (`/`) MUST feature a persistent filter bar at the top with pre-configured temporal filters:
   - `Today` (default quick-select)
   - `Yesterday`
   - `Last 7 Days`
   - `Custom Date Range` (with date-picker inputs)
   - `Batch / Filename Dropdown` (filters data strictly to a specific CSV/Excel ingestion)
2. **Instant Dynamic Metric Recalculation:** Selecting any time preset or batch MUST instantly recalculate all Dashboard KPI cards, throughput charts, and summary tables to reflect only the selected scope.

## 51.2 Execution Runtime & Predictive Completion Telemetry
1. **Live Duration Tracking:** For every active batch, the Dashboard must display:
   - Total Elapsed Runtime (HH:MM:SS) since batch initiation.
   - Average Processing Time per Record across the active parallel workers.
2. **Estimated Time of Completion (ETC):** The system must compute and display a dynamic countdown for in-flight batches:
   $$\text{ETC} = \frac{\text{Remaining Records} \times \text{Avg Duration per Record}}{\text{Parallel Concurrency}}$$
3. **Historical Batch Duration:** For completed runs, the Dashboard and audit views must display total elapsed execution time from start to finish.

## 51.3 One-Click Executive Summary Export
1. **Executive Export Action:** Provide an **"Export Executive Summary"** action directly in the Dashboard header (supporting both PDF and formatted Excel formats).
2. **Summary Layout:** Rather than dumping thousands of raw data rows, the generated managerial report must provide a concise, high-level overview containing:
   - Reporting Scope (Date range or Batch Name / ID).
   - Volume Metrics (Total Claims Ingested, Completed, Failed, In Queue).
   - Efficiency Metrics (Total Execution Time, Average Time per Claim, Effective Concurrency).
   - High-Level Exception Breakdown (e.g., Portal Outage, CAPTCHA Timeout, Hard Exception).
   - Total Scraped Cases Identified.
3. **Stage-by-Stage Breakdown:** The report MUST include a dedicated section showing the exact distribution of claims across all lifecycle stages at the time of export (e.g., Pending, Navigating, CAPTCHA Resolution, Data Extraction, Completed).

# 52. AI Self-Correction & Gap Analysis Directive
When implementing or modifying any part of this UAIC RPA Orchestrator system, the AI must continuously evaluate the changes against the 52-section requirements baseline. If any gap, missing configuration, unhandled edge case (such as database loss, pagination loops, or proxy blocks), or deployment conflict is discovered, the AI is explicitly instructed to:
1. Immediately flag the inconsistency or security/operational gap.
2. Propose a production-grade, resilient fix before writing code.
3. Update the corresponding technical documentation or Docker configuration automatically to maintain zero-defect alignment.

# 53. Advanced Edge-Case Resilience & Downstream Safeguards

## 53.1 Downstream Rate Limiting & Asynchronous Guidewire Dispatch
1. **Decoupled Publishing Queue:** Scraper workers MUST NOT post extracted court data directly and synchronously to the Guidewire API. Completed extractions must be committed to an internal ingestion queue (e.g., a dedicated Redis/Celery queue or transactional outbox).
2. **Controlled Ingestion Throttling:** A separate publisher service must dispatch payload batches to the Guidewire API using a configurable rate limiter (e.g., maximum 5 requests/sec or burst token-bucket algorithm).
3. **Internal Overload Protection:** If the Guidewire API responds with HTTP 429 (Too Many Requests), HTTP 503, or connection timeouts, the publisher must automatically apply exponential backoff without stalling or crashing active scraping browser contexts.

## 53.2 Pagination Traps & Circular Navigation Detection
1. **Page Content Hash Comparison:** For multi-page query results, the automation engine must compute a content checksum (e.g., SHA-256 hash of extracted case numbers on the current page) prior to advancing.
2. **Circular Loop Detection:** If the checksum of consecutive pages matches (indicating a broken portal "Next" button reloading identical rows), the scraper must immediately break pagination, log an anomaly warning, and continue to the extraction review phase.
3. **Hard Ceiling Pagination Cap:** Scrapers must enforce a strict, configurable safety ceiling: **"Maximum Pagination Limit"** (default: `50` pages per search query). If a portal exceeds this threshold, the scraper terminates pagination gracefully to avoid denial-of-service triggers or runaway proxy consumption.

## 53.3 Decoupled Extraction Retention (Database Connection Failure Recovery)
1. **In-Memory & Local Spool Fallback:** If a database connection error occurs during the persistence phase, the worker MUST NOT discard the extracted dataset or fail the scraping workflow.
2. **Local Staging Buffer:** Extracted payloads must be cached to an encrypted temporary disk buffer (`.\backend\spool\pending_commits\`) or an in-memory queue.
3. **Isolated Persistence Retries:** The worker must initiate a persistence retry loop (up to 5 attempts with 3-second intervals) solely targeting the database connection. The heavy browser context and CAPTCHA solving sequence must never be re-executed if the data was already successfully parsed from the DOM.