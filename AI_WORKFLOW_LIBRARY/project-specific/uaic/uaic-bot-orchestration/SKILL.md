---
name: uaic-bot-orchestration
description: >-
  Coordinate execution of the 8 county court scrapers across single-session multi-tab Chrome browser runners.
---

# Uaic Bot Orchestration

## 1. Purpose & Overview
Orchestrates court portal scraping across Florida and Texas counties using a high-performance single-session browser runner (`SingleSessionBrowserRunner`), recycling tabs and maintaining anti-detection posture.

---

## 2. When to Use & When NOT to Use

### When to Use
- Executing or modifying the multi-portal automation sequence.
- Optimizing portal execution throughput or tab recycling.

### When NOT to Use
- Single-portal isolated unit testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target claim record with policy state and loss location state.
- Configured `SingleSessionBrowserRunner`.

### Prerequisites
- Installed Google Chrome with AntiCaptcha extension.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Portal Target Resolution
Resolve target portals using `resolve_county_bot_targets()` based on policy and loss states.

### Step 2: Browser Session Initialization
Initialize genuine Chrome browser session with unpacked AntiCaptcha MV3 extension.

### Step 3: Sequential / Multi-Tab Execution
Iterate through target portals. Open portal tab, navigate to search page, enter party names, wait for CAPTCHA, submit search, and extract results.

### Step 4: Tab State Reset
Call `return_to_search_state(page)` to reset form for the next party search without reloading the browser.

### Step 5: Result Persistence & Task Handoff
Persist extracted cases to database, populate `fl_jsonbody_*` / `te_jsonbody_*`, and dispatch `evaluate_fuzzy_matches_task` to matcher queue.

### Step 6: Clean Session Teardown
Close browser tabs cleanly and update claim status to `SCRAPED`.


---

## 5. Safety Considerations & Guardrails
- Avoid aggressive Chrome process termination between portals (preserve session stability).
- Ensure failures on one portal do not abort execution of remaining target portals.

---

## 6. Expected Deliverables & Artifacts
- Executed court case discovery across all target portals.
- Extracted cases persisted in database and linked to claim.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All resolved target portals are searched for each unique party name.
- [ ] Cases are parsed into exact schemas and saved to database.
- [ ] Claim transitions cleanly from `QUEUED` to `SCRAPED`.

---

## 8. Error Recovery & Troubleshooting
- If a portal times out or encounters CAPTCHA failure, record error screenshot, mark portal as FAILED, and continue with remaining portals.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-bot-orchestration`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-bot-orchestration` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-bot-orchestration`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-bot-orchestration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-bot-orchestration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-bot-orchestration`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-bot-orchestration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/session_runner.py`
- `backend/app/tasks/scraper_tasks.py`
