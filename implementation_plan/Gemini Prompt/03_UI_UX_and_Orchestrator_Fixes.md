# 03 - RESPONSIVE UI/UX, DATA FORMATS, AND CORE ORCHESTRATOR FIXES

## 1. GLOBAL MANDATORY RESPONSIVE DESIGN & THEME
- **Full Viewport Width:** The application must use the full available viewport width. Remove unnecessary `max-width` constraints. No horizontal overflow.
- **Mobile Navigation & Footer:** Implement a fixed bottom/footer navigation bar for mobile views. Ensure it respects safe-area insets and does not overlap scrolling content.
- **Dark/Light Mode:** Ensure 100% visibility and parity across both themes for all tables, inputs, modals, and charts, fonts, color, etc.


## 2. PAGE-SPECIFIC FIXES
- **Dashboard (/):** Connect to real data. Improve performance.
- **Audit & Exceptions:** Ensure Excel export exists. Enable column sorting and multi-select filters.
- **Monitor:** Make the background export popup (Excel, CSV, JSON) a reusable component. Ensure Auto Queue is ON by default.
- **Claim Detail:** Fix "View Stages" button. Fix missing "Filing Date" capture. Ensure Top/Bottom exports (Excel, CSV, JSON) contain identical data. Remove PDF from bottom export. Ensure Audit Events record properly.

## 3. ORCHESTRATOR & ROUTING LOGIC
- **State Routing:** 
  - If Policy State == Loss Location State == Florida: Route to Broward, Hillsborough, Miami-Dade[cite: 20, 21].
  - If Policy State == Loss Location State == Texas: Route to Travis, Dallas, Harris JP, Harris Clerk, Harris District[cite: 20, 21].
  - If Policy State != Loss Location State: Route to all 8 portals[cite: 20, 21].
  - **CRITICAL:** Miami-Dade is Florida. Never classify it as Texas[cite: 20, 21].
- **Guidewire Contract:** Improving the UI must NOT change, corrupt, omit, or rename the data payload being sent to Guidewire. Preserve the exact Power Automate format[cite: 15, 20].

## 4. SCRAPED PUBLIC COURT CASES (UI REDESIGN)
- Validate that the UI does NOT alter the underlying Guidewire payload contract.
- **Grouping:** Group cases explicitly by **Portal Link** and **Portal Name (FL-Florida)**  
- Redesign the "Scraped Public Court Cases (12)" section into a professional enterprise table
- **Table Features:** Implement column-based Sorting, Multi-select Filtering, Global Search, and Pagination (max 500 records). Remove the broken standalone `sort:descending` button[
- **Data Integrity:** Do not drop fields from the UI just because they are empty. Provide a "View Raw JSON" button for debugging

## 5. FORM & API ADJUSTMENTS
- **Remove Fields:** Remove 'Loss Location City', 'Loss Location County', 'Garaging City', and 'Garaging State' from New Form, Edit Form, and Ingestion Mapping.
- **Fuzzy Match APIs:** Create an API to extract unique names from Insured, Driver, and Claimant fields. Re-implement the legacy Power Automate fuzzy match API exactly.
- **Anti-Captcha Extension:** Create a dedicated workflow/UI in Automation Settings to install and test the extension configuration.

## 6. DASHBOARD, EXPORTS & UI REFINEMENTS
- **Dashboard:** Connect to real application data. Update the Scraper Execution (8 Bots) cards to match the global dashboard card design.
- **Exports:** Implement the background export popup (currently on `/monitor`) as a reusable component across the app. Ensure Top/Bottom exports (Excel, CSV, JSON) on the Claim Detail page contain identical, complete data. Remove PDF from the bottom export, PDF export only visible to application at top beacuse we are creating a PDF of the entire website page with entire expended data without breacking UI design.


Supporting Docs you can ref:
    1) MANDATORY RESPONSIVE UI-UX REDESIGN & FULL-VIEWPORT IMPLEMENTATION.md
    2) Scraped Public Court Cases — Data Format Validation, Guidewire Compatibility & UI-UX Redesign.md
    3) MASTER IMPLEMENTATION PROMPT_1.md
    4) MASTER IMPLEMENTATION, CORRECTION, VALIDATION & PRODUCTIONIZATION PROMPT.md
    5) UAIC Claim & RPA Orchestrator — Final Comprehensive Implementation, Validation & Productionization Prompt.
    6) UAIC Claim & RPA Orchestrator — Corrected and Ordered Requirements.md
Note: Most of them are already implemented, test before making any changes.
