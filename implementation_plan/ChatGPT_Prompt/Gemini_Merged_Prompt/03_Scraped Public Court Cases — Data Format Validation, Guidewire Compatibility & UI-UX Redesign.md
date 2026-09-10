# Scraped Public Court Cases — Data Format Validation, Guidewire Compatibility & UI/UX Redesign

I do **not** like the current design, UI, or UX of the **“Scraped Public Court Cases (12)”** section.

Currently, the section is showing information in a very limited format such as:

- Case
- Broward County (FL)
- Portal Link
- Case Style: Civil Action Central

This is **not sufficient**.

Before making any UI changes, you must first verify the actual data structure and ensure that the implementation remains **100% compatible with the existing Power Automate workflow and Guidewire integration**.

## 1. FIRST: Inspect and Validate the Existing Implementation

Before changing anything, deeply inspect the **existing project source code, database models, API contracts, scraping logic, Power Automate implementation/reference, fuzzy-match logic, and Guidewire integration**.

Do **not** assume that the currently displayed fields are the correct fields.

Determine exactly:

1. What fields/columns are produced by each county scraping workflow.
2. What fields are stored in the database.
3. What fields are passed to the fuzzy matching process.
4. What fields are used to determine a positive match.
5. What fields are ultimately included in the final Guidewire payload.
6. Whether the current application uses exactly the same field names, values, transformations, and data structure as Power Automate.
7. Whether any existing transformation is required between scraped data → fuzzy matching → final match → Guidewire.

### Critical Rule

If the existing Power Automate workflow is the reference implementation, **do not redesign or simplify the underlying data model just because the current UI is displaying fewer fields.**

The UI must be improved **without changing the backend data contract or breaking the automation pipeline**.

---

# 2. Verify Power Automate Format Before UI Changes

Determine whether the current implementation is using the **same format as Power Automate**.

Compare the current implementation against the validated Power Automate workflow for every supported county portal.

For each portal, verify:

- Portal name
- Portal URL
- County
- State
- Case Number
- Case Style
- Filing Date / Suit Filed Date
- Case Status
- Case Type
- Any other fields produced by the Power Automate workflow
- Internal JSON structure
- Bot status
- Match-related fields
- Any metadata required downstream

Do not remove a field simply because it is not currently visible in the UI.

If Power Automate produces a field, the application must preserve it unless there is a documented reason that the field is intentionally not required.

---

# 3. Verify the Exact Columns

Create a clear mapping between:

**Power Automate → Scraper → Database → Fuzzy Match → Final Match → Guidewire**

For example:

```text
Power Automate Scraped Data
        ↓
Normalized Application Data
        ↓
Database / JSON
        ↓
Fuzzy Matching
        ↓
Positive Match
        ↓
Final Match Object
        ↓
Guidewire Payload
```

For every field, verify:

- Source field name
- Application field name
- Database column
- Data type
- Transformation
- Required/optional status
- Where it is consumed
- Whether it is sent to Guidewire

Do not create duplicate or incompatible fields unnecessarily.

---

# 4. Guidewire Compatibility Is CRITICAL

The most important requirement is:

> **Improving the UI must NOT change, corrupt, omit, rename, or otherwise affect the data being sent to Guidewire.**

The current Guidewire integration must continue to receive the exact expected structure.

Before making changes, identify the current Guidewire payload contract.

Verify:

- Claim Number
- Exposure Number
- Case Items
- Case Number
- Case Style
- County Website / Portal
- Suit Filed Date
- Any other required fields
- Existing formatting/transformation rules
- Existing Activity ID handling
- Existing API response handling

If Power Automate uses a particular format before sending data to Guidewire, preserve that behavior.

### DO NOT:

- Rename Guidewire fields casually.
- Change date formats without verifying the existing contract.
- Change case-number formatting.
- Remove fields from the final payload.
- Send UI-specific objects directly to Guidewire.
- Use the display/table model as the Guidewire API model.

### Required Architecture

Maintain a clear separation:

```text
Scraped Case Model
        ↓
Normalized Case Model
        ↓
UI/View Model
```

and separately:

```text
Normalized Case Model
        ↓
Guidewire Payload Mapper
        ↓
Guidewire API
```

The UI must never become the source of truth for the Guidewire payload.

---

# 5. Redesign “Scraped Public Court Cases (12)” Completely

Once the data structure and Guidewire compatibility have been verified, redesign the **“Scraped Public Court Cases (12)”** section.

The current card-style presentation is not acceptable.

Instead, when multiple cases belong to the same portal, they must be presented in a **professional enterprise table grouped by Portal Link**.

---

# 6. Group Cases by Portal Link

If multiple scraped cases come from the same portal, group them together.

Example:

```text
Broward County Clerk
https://www.browardclerk.org/Web2
────────────────────────────────────────────────────────────

| Case Number | Case Style | Filing Date | Case Status | Case Type |
|-------------|------------|-------------|-------------|-----------|
| ...         | ...        | ...         | ...         | ...       |
| ...         | ...        | ...         | ...         | ...       |
| ...         | ...        | ...         | ...         | ...       |
```

Then another portal:

```text
Hillsborough County Clerk
https://hover.hillsclerk.com/...
────────────────────────────────────────────────────────────

| Case Number | Case Style | Filing Date | Case Status | Case Type |
|-------------|------------|-------------|-------------|-----------|
| ...         | ...        | ...         | ...         | ...       |
```

Do **not** create one large confusing table containing unrelated portal records without grouping.

---

# 7. Portal Group Header

Each portal group should have a clear enterprise-style header containing:

- County name
- State badge
- Portal name
- Portal link
- Number of cases found
- Match/result status where applicable
- Expand/collapse control

Example:

```text
┌──────────────────────────────────────────────────────────────┐
│ Broward County Clerk                         FL              │
│ Public Court Records                                          │
│ https://www.browardclerk.org/Web2                            │
│ 4 Cases Found                                      [Collapse] │
└──────────────────────────────────────────────────────────────┘
```

The portal URL should be clickable and should open the official portal in a new browser tab.

Do not display unnecessarily long URLs in a visually ugly way. Use a readable label with tooltip/copy functionality where appropriate.

---

# 8. Show ALL Relevant Columns

The table must display all relevant scraped fields that are actually produced by the Power Automate workflow/current backend.

For the standard five-field county result structure, include:

1. Case Number
2. Case Style
3. Filing Date
4. Case Status
5. Case Type

For portals where the Power Automate workflow does not produce Case Type, do not fabricate a value.

Instead, clearly handle the field according to the actual source contract.

If additional fields are legitimately produced and useful for the application's workflow, expose them appropriately.

### Important

Do not reduce the table to:

```text
Case
County
Portal Link
Case Style
```

That is insufficient.

---

# 9. Table Features — REQUIRED

The **Scraped Public Court Cases** section must support full enterprise-grade table functionality.

Implement:

### Sorting

Allow sorting by:

- Case Number
- Case Style
- Filing Date
- Case Status
- Case Type
- Any other sortable displayed column

Support ascending and descending sorting.

### Filtering

Provide filters for relevant fields, including:

- Portal / County
- State
- Case Status
- Case Type
- Filing Date
- Case Number
- Case Style

Filtering must work correctly across all grouped portal sections.

### Search

Provide a global search for:

- Case Number
- Case Style
- County
- Portal
- Case Status
- Case Type

Search should update results without breaking grouping.

### Pagination

Implement proper pagination.

Do not render hundreds or thousands of cases into the DOM unnecessarily.

Provide:

- Page size selector
- Previous/Next
- First/Last where appropriate
- Current page indicator
- Total record count

Example:

```text
Showing 1–25 of 124 cases

[25 ▼]   [First] [Previous] 1 2 3 4 5 [Next] [Last]
```

### Lazy Loading / Efficient Rendering

If the dataset is large:

- Use server-side pagination where appropriate.
- Avoid loading the entire dataset into the browser unnecessarily.
- Use virtualization/lazy rendering where appropriate.
- Display loading/skeleton states.

---

# 10. Grouping Must Work With Pagination and Filtering

Do not implement grouping in a way that breaks pagination.

The architecture should correctly handle:

```text
Search
   ↓
Filter
   ↓
Sort
   ↓
Group by Portal
   ↓
Pagination
   ↓
Render
```

or use a server-side equivalent where appropriate.

The user must always understand:

- How many total cases exist.
- How many cases belong to each portal.
- Which portal a case belongs to.
- Which page they are viewing.

---

# 11. Case Row Actions

Each case row should support appropriate actions without disturbing the underlying data.

Depending on existing functionality, provide:

- View Details
- Open Portal
- Copy Case Number
- View Raw Scraped Data / JSON
- View Match Details
- View Guidewire payload/status where permitted
- Retry/reprocess where applicable

Do not expose sensitive/internal information unnecessarily.

---

# 12. Case Details

Clicking a case should open a professional:

- Modal
- Drawer
- Or dedicated details panel

It should show the complete record in a readable format.

Suggested sections:

### Case Information

- Case Number
- Case Style
- Filing Date
- Case Status
- Case Type

### Source Information

- County
- State
- Portal
- Portal URL

### Matching Information

- Matched person
- Match type
- Fuzzy match score
- Match status

### Processing Information

- Scraping status
- Processing timestamp
- Bot status
- Error/retry information if applicable

### Integration Information

Only where appropriate:

- Guidewire submission status
- Activity ID
- Submission timestamp
- Response/error status

Do not expose secrets, credentials, tokens, or API keys.

---

# 13. Raw JSON Must Remain Available

The application must preserve the raw scraped JSON/data generated by the scraping process.

Provide a way to inspect it for troubleshooting/auditing.

For example:

```text
[View Raw Data]
```

The raw data viewer should:

- Be read-only.
- Use formatted JSON.
- Support copy.
- Not modify the source data accidentally.

This is important for comparing the application's output with Power Automate.

---

# 14. Do NOT Modify the Automation Logic Just for UI

The purpose of this task is primarily to correct the presentation and ensure data-contract correctness.

Do not rewrite working scraping logic unnecessarily.

Do not modify:

- CAPTCHA behavior
- County search logic
- Fuzzy matching rules
- Guidewire integration
- Queue processing
- Retry behavior
- Existing API contracts

unless the audit identifies an actual mismatch or bug.

If a mismatch is discovered, fix it carefully and test the complete downstream flow.

---

# 15. Verify End-to-End Data Integrity

After implementation, test the complete pipeline:

```text
Queue Record
   ↓
County Website Scraping
   ↓
Scraped Case Data
   ↓
Database
   ↓
Scraped Public Court Cases UI
   ↓
Fuzzy Matching
   ↓
Positive Match
   ↓
Guidewire Payload
   ↓
Guidewire API
   ↓
Activity ID / Result
```

Verify that the data displayed in the UI is consistent with the data stored in the backend.

Then verify that the same underlying data produces the expected Guidewire payload.

---

# 16. Regression Testing

Test at minimum:

### County Results

- Broward
- Hillsborough
- Miami-Dade
- Dallas
- Travis
- Harris JP
- Harris District
- Harris County Clerk

### Scenarios

- Multiple cases from one portal.
- Cases from multiple portals.
- No cases found.
- One case found.
- Many cases found.
- Missing optional fields.
- Long Case Style.
- Long Case Number.
- Different Case Status values.
- Different Case Types.
- Duplicate cases if they occur.
- Failed scraping.
- Retry/reprocessing.
- Positive fuzzy match.
- No fuzzy match.
- Guidewire submission success.
- Guidewire submission failure.

---

# 17. Responsive UI/UX

This section must also follow the application's global responsive requirements.

### Desktop

Use the full available screen width.

Do not leave unnecessary empty space.

### Tablet

Tables must adapt appropriately.

### Mobile

Do **not** simply shrink the desktop table until it becomes unusable.

On mobile, transform each case row into a responsive card/list representation while preserving all important information.

Example:

```text
Broward County Clerk
────────────────────────

Case Number
123456789

Case Style
John Doe vs. ABC Company

Filing Date
09/01/2026

Status
ACTIVE

Case Type
CIVIL ACTION CENTRAL

[View Details]
```

Portal groups should remain clearly separated.

The mobile experience must include the application's **fixed bottom/footer navigation** for the primary navigation destinations.

Do not hide important functionality simply because the screen is small.

---

# 18. UI/UX Quality Requirements

The redesigned section must look like a polished enterprise application.

Use:

- Clear hierarchy
- Consistent spacing
- Proper typography
- Status badges
- Responsive tables/cards
- Sticky table headers where appropriate
- Clean grouping
- Tooltips
- Accessible controls
- Loading/skeleton states
- Empty states
- Error states
- Hover/focus/active states
- Keyboard accessibility
- Touch-friendly controls

Avoid:

- Oversized cards
- Excessive whitespace
- Repetitive information
- Poor alignment
- Tiny text
- Horizontally overflowing content
- Unnecessary nested cards
- Random colors
- Inconsistent spacing
- Desktop-only interactions

---

# 19. Important: Do Not Break Existing Data

The most important rule is:

> **UI redesign must never alter the underlying scraped data, fuzzy-match behavior, or Guidewire integration unless a verified Power Automate/application mismatch requires correction.**

The UI is a representation of the data — it must not become the source of truth.

Before completing the work, verify:

```text
Power Automate Format
        =
Application Scraped Data Format
        =
Database Data
        =
Fuzzy Match Input
        =
Expected Final Match Data
        =
Guidewire-Compatible Payload
```

Where differences legitimately exist because of transformation, document the transformation and ensure it matches the existing validated workflow.

---

# 20. Final Acceptance Criteria

Do not consider this task complete until all of the following are true:

- [ ] Existing implementation was inspected before changes.
- [ ] Power Automate format was verified.
- [ ] Power Automate columns were verified.
- [ ] Current database structure was verified.
- [ ] Fuzzy-match input was verified.
- [ ] Guidewire payload was verified.
- [ ] No Guidewire contract was accidentally changed.
- [ ] Scraped Public Court Cases section has been completely redesigned.
- [ ] Cases are grouped by Portal Link.
- [ ] All relevant columns are displayed.
- [ ] Sorting works.
- [ ] Filtering works.
- [ ] Global search works.
- [ ] Pagination works.
- [ ] Lazy loading/efficient rendering is implemented where required.
- [ ] Case details view works.
- [ ] Raw JSON/data inspection works.
- [ ] Portal links work.
- [ ] Empty states work.
- [ ] Loading states work.
- [ ] Error states work.
- [ ] Desktop responsive behavior works.
- [ ] Tablet responsive behavior works.
- [ ] Mobile responsive behavior works.
- [ ] Mobile footer/bottom navigation works.
- [ ] No horizontal overflow occurs.
- [ ] Existing scraping functionality continues to work.
- [ ] Existing fuzzy matching continues to work.
- [ ] Existing Guidewire integration continues to work.
- [ ] End-to-end regression testing passes.

## Final Rule

**Do not just change the appearance of the existing “Scraped Public Court Cases (12)” section.**

First understand exactly what Power Automate produces, verify the columns and downstream Guidewire contract, then redesign the UI around that verified data model.

The final result should be an **enterprise-grade, responsive, searchable, filterable, sortable, paginated, portal-grouped court-case data experience** while maintaining **100% data integrity and compatibility with the existing automation and Guidewire workflow.**