---
name: fl-broward-workflow
description: >-
  Complete operational specification and runbook for the Broward County Clerk of Courts scraper, CAPTCHA verification, and Guidewire push.
---

# Fl Broward Workflow

## 1. Purpose & Overview
Provides the complete, authoritative runbook for automating case search and discovery on the Broward County Clerk of Courts portal (`https://www.browardclerk.org/Web2`).

---

## 2. When to Use & When NOT to Use

### When to Use
- Operating, testing, or updating the Broward County court scraper (`BrowardScraper`).
- Debugging Turnstile/reCAPTCHA resolution on Broward County.

### When NOT to Use
- Texas court portals.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Claim record with Florida policy/loss, unique names list, and Broward portal URL.

### Prerequisites
- AntiCaptcha extension active and Broward portal reachability.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Portal Navigation
Navigate to `https://www.browardclerk.org/Web2`. Click Case Search, activate 'Party Name' tab.

### Step 2: Data Entry
Fill Last Name, First Name, and DOL normalized to `MM/dd/yyyy` format.

### Step 3: CAPTCHA Verification
Inspect for reCAPTCHA/Turnstile. Verify solve tokens (`g-recaptcha-response > 25`, `cf-turnstile-response > 20`). If unsolved, check `has_active_captcha_challenge`. Block submit if active challenge remains.

### Step 4: Search Submission
Click `#PersonSearchResults` directly.

### Step 5: Result Table Extraction
Parse table rows (`table.table tbody tr`). Filter out glossary rows (`CACE`, `COCE`). Extract 5 fields: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`. Handle pagination.

### Step 6: Tab Reset & Downstream Push
Call `return_to_search_state(page)`. Save cases to database and dispatch fuzzy matching cascade.


---

## 5. Safety Considerations & Guardrails
- Strictly filter out static prefix glossary rows; real cases must contain digits.
- Block speculative search submits when active CAPTCHA is present.

---

## 6. Expected Deliverables & Artifacts
- Extracted Broward County cases adhering to 5-field schema.
- Verified Broward scraper test pass.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Broward scraper extracts valid cases with digits in CaseNumber.
- [ ] Filing dates normalized to MM/DD/YYYY.
- [ ] 5-field schema verified.

---

## 8. Error Recovery & Troubleshooting
- If Broward portal returns Cloudflare Turnstile box, wait for extension resolution or apply proxy rotation.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fl-broward-workflow` or follow `.agents/skills/fl-broward-workflow/SKILL.md`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fl-broward-workflow` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fl-broward-workflow`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fl-broward-workflow` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fl-broward-workflow`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fl-broward-workflow`. | `PROMPT FILE` |
| **Windsurf** | Activate `fl-broward-workflow` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/fl-broward-workflow/SKILL.md`
- `backend/app/automation/florida/broward.py`
