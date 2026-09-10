# MASTER PROMPT — COUNTY PORTAL DISCOVERY, HUMAN-LIKE NAVIGATION, CAPTCHA-SAFE AUTOMATION & VERIFIED IMPLEMENTATION

## 1. OBJECTIVE

Analyze the current solution, the existing Power Platform implementation, the current claim dataset, and all configured county court portals.

The required objective is to:

1. Take the **real claim dataset** from the current solution.
2. Develop and execute a **new fuzzy-matching implementation** specifically for identifying unique names that need to be searched on county court websites.
3. Identify the resulting **unique names**.
4. Use the county court portal tabs that are **already opened or open the relavent tabs if not already open** for the applicable counties.
5. Process **one unique name at a time**.
6. For the current unique name, search that same name sequentially across **all applicable already-opened county portal tabs**.
7. After each portal search:

   * Extract all relevant cases.
   * Match the extracted cases against the **original claim data**.
   * Store the matched results.
8. After all applicable portal tabs have been completed for the current unique name, move to the next unique name.
9. Continue until **ALL unique names** have been processed across **ALL applicable county portals**.
10. Only after every unique name and every applicable portal has been completely processed, execute the **existing fuzzy-matching logic from the Power Platform solution**.
11. Continue with the existing downstream processing exactly as currently implemented.

The existing downstream business logic must not be redesigned or changed unless explicitly required and approved.

---

# 2. IMPORTANT SECURITY / CAPTCHA REQUIREMENT

The automation MUST NOT bypass, defeat, spoof, circumvent, or conceal automation from CAPTCHA, anti-bot, WAF, bot-detection, or security systems.

This includes, but is not limited to:

* reCAPTCHA
* Cloudflare CAPTCHA
* Cloudflare Turnstile
* Cloudflare bot/security challenges
* hCaptcha
* Arkose Labs
* PerimeterX / HUMAN
* DataDome
* AWS WAF challenges
* Other CAPTCHA or anti-automation mechanisms

Do NOT implement:

* CAPTCHA bypass
* CAPTCHA evasion
* CAPTCHA token manipulation
* Forged challenge responses
* Fingerprint spoofing intended to evade detection
* Browser stealth patches intended to defeat detection
* Techniques designed to make automated activity appear to be a human specifically to circumvent security controls
* Automated challenge circumvention
* Repeated challenge submission attempts
* Security-control avoidance techniques

The objective is **reliable, compliant automation through the legitimate website flow**, not CAPTCHA evasion.

If a CAPTCHA or security challenge is encountered:

1. Detect it.
2. Record it.
3. Pause automation where human interaction is required.
4. Allow an authorized human to complete the challenge through the normal website interface.
5. Resume only after legitimate completion.
6. Never falsely mark a CAPTCHA/security challenge as completed.

The automation must respect:

* Website terms and conditions.
* Applicable rate limits.
* robots/security requirements where applicable.
* Normal website navigation.
* Reasonable request frequency.
* Portal-specific cooldowns.
* Security challenge states.

---

# 3. DO NOT ASSUME THE EXISTING URLS ARE CORRECT

Do NOT assume that URLs currently present in the solution are still correct.

Before modifying the scraper/automation implementation:

1. Open the official county portal.
2. Start from the legitimate public home/entry page.
3. Follow the normal website navigation.
4. Verify the current search flow.
5. Record every relevant URL transition.
6. Compare the verified flow with the existing implementation.
7. Identify obsolete, redirected, changed, or incorrect URLs.

Do not silently replace an existing URL without documenting why the URL is no longer valid.

---

# 4. COUNTY PORTALS TO DISCOVER

## Florida

1. Broward County Clerk
2. Hillsborough County Clerk
3. Miami-Dade County Clerk

## Texas

4. Travis County
5. Dallas County
6. Harris County JP
7. Harris County District Clerk
8. Harris County Clerk

### CRITICAL STATE/COUNTY CLASSIFICATION

**Miami-Dade County is in Florida.**

It MUST NEVER be classified or routed as a Texas county.

Verify the state/county mapping everywhere it is represented, including:

* Portal configuration
* Database
* Routing
* Scraper registry
* UI
* Queue
* Logs
* Tests
* Reports
* Search orchestration
* Portal selection logic

---

# 5. FIRST PHASE — DISCOVERY ONLY

Before changing the current scraper implementation, perform a complete discovery of every applicable county portal.

The discovery phase must determine:

* Official portal
* Starting/home URL
* Search URL
* Navigation path
* Search mechanism
* Required fields
* Optional fields
* Date-of-loss handling
* CAPTCHA/security behavior
* Result page
* Pagination
* Case-detail navigation
* Extractable case fields
* URL transitions
* New-tab behavior
* Back-navigation behavior
* Session requirements
* Failure conditions
* Recovery behavior
* Rate/interaction observations

Unknown information must be explicitly marked:

`UNKNOWN — REQUIRES MANUAL VALIDATION`

Do not guess.

---

# 6. START FROM THE REAL HOME PAGE

For discovery, begin from the actual public county portal home/entry page where a normal user would begin.

Do not begin discovery by directly opening an assumed deep search URL unless the legitimate website flow itself leads there.

Document:

```text
Home Page
    ↓
Navigation Link/Button
    ↓
Search Page
    ↓
Search Form
    ↓
Search Submission
    ↓
Results Page
    ↓
Case Detail
```

The actual sequence must be verified for each portal.

---

# 7. DOCUMENT URL TRANSITIONS

For every portal, document:

* Initial URL
* Home page URL
* Search page URL
* Search submission URL
* Results URL
* Case-detail URL
* Pagination URL/state
* Any redirect
* Any new-tab URL
* Any authentication/session transition

Maintain a clear distinction between:

```text
CURRENT IMPLEMENTATION
```

and

```text
VERIFIED CURRENT PORTAL FLOW
```

Any difference must be documented before implementation.

---

# 8. CAPTCHA / SECURITY DISCOVERY

For every county portal determine:

* Whether CAPTCHA exists.
* CAPTCHA type.
* When it appears.
* Whether it appears on the home page.
* Whether it appears on the search page.
* Whether it appears after repeated searches.
* Whether it appears on case-detail navigation.
* Whether a WAF/security challenge appears.
* Whether a human must intervene.
* What legitimate recovery flow exists.

Record the security state without attempting to defeat it.

---

# 9. NORMAL INTERACTION FLOW

The implementation must follow the legitimate website interaction flow.

Where applicable:

```text
Open Existing Portal Tab
        ↓
Use Existing Page State
        ↓
Enter Search Information
        ↓
Submit Search
        ↓
Handle Legitimate CAPTCHA/Security Challenge
        ↓
Read Results
        ↓
Handle Pagination
        ↓
Open Case Details
        ↓
Extract Data
        ↓
Return to Results
```

Do not introduce unnecessary direct navigation to deep URLs.

---

# 10. RATE / REQUEST MANAGEMENT

The implementation must include controlled request management.

Requirements:

* Controlled request frequency.
* Reasonable delays where required by portal behavior.
* Bounded retries.
* Exponential/backoff behavior where appropriate.
* Portal-specific cooldowns.
* No rapid repeated searches.
* No rapid repeated CAPTCHA attempts.
* No infinite reload loops.
* No infinite search loops.
* No repeated navigation after a security block.

Security challenges must not trigger aggressive retry behavior.

---

# 11. CAPTCHA STATE MACHINE

Implement explicit CAPTCHA/security states.

Example:

```text
NORMAL
   ↓
SECURITY_CHALLENGE_DETECTED
   ↓
WAITING_FOR_AUTHORIZED_HUMAN_ACTION
   ↓
CHALLENGE_COMPLETED
   ↓
RESUME
```

Failure state:

```text
SECURITY_CHALLENGE_DETECTED
   ↓
HUMAN_ACTION_REQUIRED
   ↓
TIMEOUT
   ↓
FAILED_REQUIRES_ATTENTION
```

Never treat an unresolved CAPTCHA as success.

---

# 12. EXTRACTION OBJECTIVE

The extraction objective is to retrieve **all relevant cases** for each search.

Search inputs must preserve the existing data contract and current Power Automate/V4 behavior.

Where applicable, search using:

* Insured First Name
* Insured Last Name
* Driver First Name
* Driver Last Name
* Claimant First Name
* Claimant Last Name
* Date of Loss
* Other currently required fields

Do not remove existing required fields without verification and approval.

---

# 13. PAGINATION IS MANDATORY

Pagination must be fully discovered and implemented.

Determine whether each portal uses:

* Next
* Previous
* Numbered pages
* Load More
* Infinite scrolling
* Page size
* Server-side pagination
* Dynamic loading

The implementation must prevent:

* Duplicate extraction
* Skipped pages
* Skipped cases
* Infinite pagination loops
* Stale result processing

Track at minimum:

```text
page_number
total_pages
records_on_page
records_extracted
records_skipped
duplicate_records
```

---

# 14. CASE-DETAIL NAVIGATION

For each portal determine the verified case-detail navigation pattern.

Examples:

```text
Results
   ↓
Click Case
   ↓
Case Detail
   ↓
Extract
   ↓
Back to Results
```

or:

```text
Results
   ↓
Click Case
   ↓
New Tab
   ↓
Extract
   ↓
Close Case Tab
   ↓
Return to Results
```

Only use the behavior actually verified for that portal.

---

# 15. UNIQUE NAME GENERATION AND SEARCH PROCESS

This section is **MANDATORY**.

There are two distinct fuzzy-matching stages in the complete workflow.

## Stage 1 — NEW FUZZY MATCHING

A **new fuzzy-matching implementation must be developed in the current solution**.

Its purpose is to process the real claim dataset and identify the **unique names** that must be searched on county court portals.

This Stage 1 fuzzy matching must:

1. Read the real claim dataset.
2. Apply the newly implemented fuzzy-matching logic.
3. Group/identify the required unique names.
4. Produce the ordered unique-name search set.
5. Pass one unique name at a time to the portal-search process.

The exact business rules for this new fuzzy matching must be validated against the current data requirements before implementation.

---

## Stage 2 — SEARCH ONE UNIQUE NAME AT A TIME

Once the unique names are generated, process them **sequentially, one unique name at a time**.

For the current unique name:

1. Search the name in the **first applicable county portal tab that is already open**.
2. Extract relevant cases.
3. Match extracted cases against the **original claim data**.
4. Store the matched results.
5. Move to the **next applicable already-opened county portal tab**.
6. Search the **same unique name**.
7. Extract relevant cases.
8. Match extracted cases against the **original claim data**.
9. Store the matched results.
10. Continue until every applicable portal tab has been completed for that unique name.
11. Only then move to the next unique name.
12. Repeat until ALL unique names have been processed.

### ABSOLUTE SEQUENCING RULE

**Do NOT process all unique names in Portal Tab 1 before moving to Portal Tab 2.**

The required unit of processing is:

> **ONE UNIQUE NAME**

The required sequence is:

> **One unique name → all applicable portal tabs → extract → match → store → next unique name.**

---

# 16. REQUIRED PROCESSING ORDER

The processing order is extremely important and must be implemented **exactly** as follows:

```text
Real Claim Dataset

        ↓

New Fuzzy Matching

        ↓

Identify Unique Names

        ↓

Process Unique Names One by One

        ↓

For Current Unique Name

        ↓

Portal Tab 1

        ↓

Extract Relevant Cases

        ↓

Match Cases Against Original Claim Data

        ↓

Store Results

        ↓

Portal Tab 2

        ↓

Extract Relevant Cases

        ↓

Match Cases Against Original Claim Data

        ↓

Store Results

        ↓

Portal Tab 3

        ↓

Extract Relevant Cases

        ↓

Match Cases Against Original Claim Data

        ↓

Store Results

        ↓

All Applicable Portal Tabs Completed

        ↓

Move to Next Unique Name

        ↓

Repeat Until ALL Unique Names Are Completed

        ↓

Existing Power Platform Fuzzy Matching

        ↓

Existing Downstream Processing
```

The number of portal tabs is dynamic.

If a state/county combination has 3 applicable portals, process all 3.

If it has 5 applicable portals, process all 5.

The implementation must not hard-code the workflow to exactly three portals.

---

# 17. EXAMPLE — FLORIDA

If Florida has three applicable county court portals and those portal pages/tabs are already open:

```text
Unique Name A

    ↓

Florida Portal Tab 1

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results

    ↓

Florida Portal Tab 2

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results

    ↓

Florida Portal Tab 3

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results


Unique Name B

    ↓

Florida Portal Tab 1

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results

    ↓

Florida Portal Tab 2

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results

    ↓

Florida Portal Tab 3

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results


Unique Name C

    ↓

Florida Portal Tab 1

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results

    ↓

Florida Portal Tab 2

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results

    ↓

Florida Portal Tab 3

    ↓

Extract Cases

    ↓

Match Against Claim Data

    ↓

Store Results


...continue until ALL unique names are completed...

    ↓

Existing Power Platform Fuzzy Matching

    ↓

Existing Downstream Processing
```

### WRONG SEQUENCE

The following is explicitly prohibited:

```text
Unique Name A → Portal 1
Unique Name B → Portal 1
Unique Name C → Portal 1
...
ALL Names → Portal 1

        ↓

Portal 2

        ↓

Unique Name A
Unique Name B
Unique Name C
...
```

### CORRECT SEQUENCE

```text
Unique Name A
    ↓
Portal 1
    ↓
Extract → Match → Store
    ↓
Portal 2
    ↓
Extract → Match → Store
    ↓
Portal 3
    ↓
Extract → Match → Store

        ↓

Unique Name B
    ↓
Portal 1
    ↓
Extract → Match → Store
    ↓
Portal 2
    ↓
Extract → Match → Store
    ↓
Portal 3
    ↓
Extract → Match → Store

        ↓

Unique Name C
    ↓
Portal 1
    ↓
Extract → Match → Store
    ↓
Portal 2
    ↓
Extract → Match → Store
    ↓
Portal 3
    ↓
Extract → Match → Store
```

---

# 18. EXISTING FUZZY MATCHING — AFTER ALL PORTAL SEARCHES

The **existing fuzzy-matching logic from the Power Platform solution** must be executed only after:

1. ALL unique names have been generated.
2. ALL unique names have been processed.
3. ALL applicable county portal tabs have been searched for every unique name.
4. Relevant cases have been extracted.
5. Extracted cases have been matched against the original claim data.
6. Results have been stored.

Only after all of the above is complete:

```text
Existing Power Platform Fuzzy Matching
        ↓
Existing Downstream Processing
```

Do NOT execute the existing final fuzzy matching after only one unique name.

Do NOT execute it after only one portal.

Do NOT execute it before all portal results have been stored.

### IMPORTANT DISTINCTION

There are two separate fuzzy-matching stages:

```text
STAGE 1
New Fuzzy Matching
        ↓
Identify Unique Names
        ↓
Website Searching
```

and:

```text
STAGE 2
Existing Power Platform Fuzzy Matching
        ↓
Final Result Processing
        ↓
Existing Downstream Processing
```

Do not merge these two stages.

Do not replace Stage 2 with Stage 1.

Do not remove the existing Power Platform fuzzy-matching business logic.

---

# 19. DUPLICATE HANDLING

Duplicate cases must be handled deterministically.

Where appropriate, use a composite identifier such as:

```text
Portal + County + Case Number
```

However, do not remove legitimate cases merely because they have similar names or other similar attributes.

Duplicate handling must be documented and testable.

---

# 20. CURRENT SOLUTION INTEGRATION

After discovery and approval, integrate only the verified portal flows into the current solution.

Preserve existing:

* Database contracts
* Queue behavior
* Guidewire integration
* Notifications
* Exports
* Status tracking
* Error handling
* Existing working functionality
* Existing downstream processing

Do not redesign unrelated parts of the application.

---

# 21. APPROVAL GATE

The workflow must be:

```text
DISCOVER
    ↓
DOCUMENT
    ↓
COMPARE WITH CURRENT IMPLEMENTATION
    ↓
SHOW DIFFERENCES
    ↓
USER REVIEW
    ↓
APPROVAL
    ↓
IMPLEMENT
    ↓
TEST
```

Do not modify the existing scraper implementation before approval.

The discovery report must be created first.

---

# 22. AFTER APPROVAL — IMPLEMENT ONLY VERIFIED FLOWS

After explicit approval:

1. Implement only verified portal behavior.
2. Preserve existing data contracts.
3. Implement the required unique-name processing sequence.
4. Use already-opened portal tabs where required.
5. Implement extraction per portal.
6. Implement match-against-original-claim-data processing after each portal.
7. Store results after each portal.
8. Move to the next portal only after the current portal's extract/match/store sequence is complete.
9. Move to the next unique name only after all applicable portal tabs for the current name are complete.
10. Run the existing Power Platform fuzzy matching only after all names and portals are complete.
11. Continue existing downstream processing.

---

# 23. ATTENDED MODE

Attended mode must visibly demonstrate:

```text
Portal Tabs Already Open
        ↓
Current Unique Name
        ↓
Portal Tab
        ↓
Search
        ↓
CAPTCHA/Security Challenge if encountered
        ↓
Human Intervention if Required
        ↓
Results
        ↓
Pagination
        ↓
Case Navigation
        ↓
Extraction
        ↓
Match Against Claim Data
        ↓
Store
        ↓
Next Portal Tab
```

The browser must not hide security challenges from the authorized user.

---

# 24. UNATTENDED MODE

Unattended mode must never pretend that a CAPTCHA/security challenge was completed.

If human interaction is required:

```text
Pause
    ↓
Mark Human Action Required
    ↓
Notify / Queue
    ↓
Wait for Legitimate Completion
    ↓
Resume
```

If the required human action cannot be completed within the configured timeout:

```text
Timeout
    ↓
Failed / Requires Attention
    ↓
Preserve Partial Results
    ↓
Apply Controlled Retry Policy
```

---

# 25. EVIDENCE REQUIRED

For each county portal provide evidence of:

* Home page
* Navigation
* Search page
* Search fields
* Search submission
* CAPTCHA/security behavior
* Results
* Pagination
* Case details
* URL transitions
* New-tab behavior where applicable
* Extraction
* Match against claim data
* Stored result
* Failure/recovery behavior

Evidence must demonstrate that the implementation follows the legitimate verified flow.

---

# 26. DISCOVERY REPORT

Create:

```text
COUNTY_PORTAL_DISCOVERY_REPORT.md
```

The report must contain, for each portal:

* State
* County
* Official portal
* Official URL
* Starting URL
* Verified navigation
* Search flow
* Search fields
* CAPTCHA/security behavior
* Human interaction requirements
* Result fields
* Pagination
* Case-detail navigation
* URL transitions
* Failure conditions
* Recovery behavior
* Screenshots/evidence
* Differences from current implementation
* Recommended changes
* Unknowns requiring validation

Also include a **Unique Name Processing Matrix**:

| Unique Name | Portal   | Search Completed | Cases Extracted | Matched | Stored | Status |
| ----------- | -------- | ---------------: | --------------: | ------: | -----: | ------ |
| Name A      | Portal 1 |           Yes/No |           Count |   Count | Yes/No | Status |
| Name A      | Portal 2 |           Yes/No |           Count |   Count | Yes/No | Status |
| Name A      | Portal 3 |           Yes/No |           Count |   Count | Yes/No | Status |
| Name B      | Portal 1 |           Yes/No |           Count |   Count | Yes/No | Status |
| Name B      | Portal 2 |           Yes/No |           Count |   Count | Yes/No | Status |
| Name B      | Portal 3 |           Yes/No |           Count |   Count | Yes/No | Status |

The report must also verify:

* Stage 1 new fuzzy matching
* Unique-name generation
* One-name-at-a-time processing
* Portal-by-portal processing
* Extract → Match → Store sequencing
* Stage 2 existing Power Platform fuzzy matching
* Final downstream processing

---

# 27. REQUIRED TESTING

Testing must verify the exact orchestration sequence.

At minimum, test:

### Test 1 — One Unique Name / Three Portals

Expected:

```text
Name A
 → Portal 1
 → Extract
 → Match
 → Store
 → Portal 2
 → Extract
 → Match
 → Store
 → Portal 3
 → Extract
 → Match
 → Store
```

### Test 2 — Multiple Unique Names

Expected:

```text
Name A → All Portals → Complete
Name B → All Portals → Complete
Name C → All Portals → Complete
```

### Test 3 — Verify Incorrect Sequence Is Impossible

The system must NOT produce:

```text
Portal 1 → Name A
Portal 1 → Name B
Portal 1 → Name C
Portal 2 → Name A
...
```

### Test 4 — Final Fuzzy Matching Timing

Verify that existing Power Platform fuzzy matching does not execute until:

```text
ALL Names
+
ALL Applicable Portals
+
ALL Extraction
+
ALL Matching
+
ALL Storage
```

are complete.

### Test 5 — CAPTCHA/Security Challenge

Verify that:

* Challenge is detected.
* Automation pauses.
* Human action is requested when required.
* Automation does not attempt bypass.
* Automation resumes only after legitimate completion.
* Timeout/failure is handled correctly.

### Test 6 — Pagination

Verify:

* Every page is processed.
* No cases are skipped.
* No cases are duplicated unintentionally.
* Pagination terminates correctly.

---

# 28. IMPORTANT SUCCESS CRITERIA

The implementation is successful only if ALL of the following are true:

1. Real claim data is used.
2. New fuzzy matching identifies the unique names.
3. Unique names are processed one at a time.
4. Already-opened portal tabs are reused where applicable.
5. The current unique name is searched across every applicable portal before moving to the next unique name.
6. Relevant cases are extracted after each portal search.
7. Extracted cases are matched against the original claim data after each portal search.
8. Results are stored after each portal search.
9. No portal is processed for the next unique name until all applicable portals for the current unique name are complete.
10. All unique names are completed before final fuzzy matching.
11. Existing Power Platform fuzzy matching is preserved and executed at the correct stage.
12. Existing downstream processing remains intact.
13. Pagination is fully handled.
14. Duplicate handling is deterministic.
15. CAPTCHA/security challenges are handled compliantly.
16. No CAPTCHA or anti-bot bypass is implemented.
17. The workflow is observable and auditable.
18. The discovery report accurately reflects the verified portal behavior.
19. Tests prove the required processing order.

---

# 29. FINAL REPORT

At completion, provide a final implementation report containing:

### Discovery

* Portals discovered
* Verified URLs
* Navigation flows
* CAPTCHA/security findings
* Differences from current implementation

### Implementation

* Files changed
* Components changed
* Portal configurations changed
* New fuzzy-matching implementation
* Unique-name orchestration
* Extraction logic
* Claim-data matching
* Result storage
* Existing Power Platform fuzzy-matching integration

### Processing Sequence Verification

Explicitly confirm:

```text
Real Claim Dataset
        ↓
New Fuzzy Matching
        ↓
Unique Names
        ↓
One Unique Name
        ↓
All Applicable Portal Tabs
        ↓
Extract
        ↓
Match
        ↓
Store
        ↓
Next Unique Name
        ↓
Repeat Until ALL Names Complete
        ↓
Existing Power Platform Fuzzy Matching
        ↓
Existing Downstream Processing
```

### Testing

Include:

* Unit tests
* Integration tests
* End-to-end tests
* Portal-flow tests
* Pagination tests
* CAPTCHA/security-state tests
* Unique-name sequencing tests
* Final fuzzy-matching timing tests
* Result-storage tests

### Remaining Unknowns

Clearly identify anything that remains:

```text
UNKNOWN — REQUIRES MANUAL VALIDATION
```

Do not claim a requirement is verified when it has not been verified.

---

# 30. ABSOLUTE RULE

The most important orchestration rule in this entire prompt is:

> **ONE UNIQUE NAME → ALL APPLICABLE PORTAL TABS → EXTRACT → MATCH AGAINST ORIGINAL CLAIM DATA → STORE RESULTS → NEXT UNIQUE NAME**

More precisely, for each portal:

> **Current Unique Name → Portal Tab → Extract → Match → Store → Next Portal Tab**

Then:

> **All Applicable Portal Tabs Complete → Next Unique Name**

Only after:

> **ALL Unique Names Complete**

execute:

> **Existing Power Platform Fuzzy Matching → Existing Downstream Processing**

**NEVER process all unique names in Portal 1 before moving to Portal 2.**

**NEVER execute the final existing Power Platform fuzzy matching before all unique names and all applicable portals have been completely processed.**

**NEVER bypass or circumvent CAPTCHA/security controls.**

This sequence is mandatory and must be reflected consistently in the:

* Architecture
* Orchestration
* Queue
* State machine
* Portal processing
* Database/result storage
* Logging
* Tests
* Reports
* Error handling
* Retry handling
* UI/status tracking
* Final downstream processing
