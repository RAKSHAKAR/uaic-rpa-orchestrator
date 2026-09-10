# 03 - CORE ORCHESTRATOR ARCHITECTURE & GLOBAL UI/UX

## 1. GLOBAL RESPONSIVENESS & THEME
- **Full Viewport Width:** The application must use the full available viewport width. Remove unnecessary `max-width` constraints. No horizontal overflow.
- **Mobile Navigation:** Implement a fixed bottom/footer navigation bar for mobile views. Ensure it respects safe-area insets and does not overlap scrolling content.
- **Dark/Light Mode:** Ensure 100% visibility and parity across both themes for all tables, inputs, modals, charts, and Others.

## 2. ORCHESTRATOR & ROUTING LOGIC
- **State Routing:** 
  - If Policy State == Loss Location State == Florida: Route to Broward, Hillsborough, Miami-Dade.
  - If Policy State == Loss Location State == Texas: Route to Travis, Dallas, Harris JP, Harris Clerk, Harris District.
  - If Policy State != Loss Location State: Route to all 8 portals.
  - **CRITICAL:** Miami-Dade is Florida. Never classify it as Texas.
- **Guidewire Contract:** Improving the UI must NOT change, corrupt, omit, or rename the data payload being sent to Guidewire. Preserve the exact Power Automate format.

## 3. SCRAPED PUBLIC COURT CASES (UI REDESIGN)
- Redesign the "Scraped Public Court Cases (12)" section into a professional enterprise table.
- **Grouping:** Group cases explicitly by **Portal Link**.
- **Table Features:** Implement column-based Sorting, Multi-select Filtering, Global Search, and Pagination (max 500 records). Remove the broken standalone `sort:descending` button.
- **Data Integrity:** Do not drop fields from the UI just because they are empty. Provide a "View Raw JSON" button and "View Screenshot" button for debugging.

## 4. DASHBOARD, EXPORTS & UI REFINEMENTS
- **Dashboard:** Connect to real application data. Update the Scraper Execution (8 Bots) cards to match the global dashboard card design.
- **Exports:** Implement the background export popup (currently on `/monitor`) as a reusable component across the app. Ensure Top/Bottom exports (Excel, CSV, JSON, and PDF on the Claim Detail page contain identical, complete data. Remove PDF from the bottom export PDF only show when pdf funcationality is there for any page.


Suporting Docs you can ref:
1) MANDATORY RESPONSIVE UI-UX REDESIGN & FULL-VIEWPORT IMPLEMENTATION.md  
2) Scraped Public Court Cases — Data Format Validation, Guidewire Compatibility & UI-UX Redesign.md  
3) MASTER IMPLEMENTATION PROMPT_1.md  
4) MASTER IMPLEMENTATION, CORRECTION, VALIDATION & PRODUCTIONIZATION PROMPT.md  
5) UAIC Claim & RPA Orchestrator — Final Comprehensive Implementation, Validation & Productionization Prompt.md
6) UAIC Claim & RPA Orchestrator — Corrected and Ordered Requirements.md

Note: Most of them are already implemented, test before making any changes.

