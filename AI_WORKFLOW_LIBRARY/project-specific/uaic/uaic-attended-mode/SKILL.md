---
name: uaic-attended-mode
description: >-
  Run visible, attended browser execution with genuine Google Chrome window, human pacing, and video evidence capture.
---

# Uaic Attended Mode

## 1. Purpose & Overview
Executes court portal automation in visible GUI mode (`headless=False`), allowing human operators to watch browser interactions, intervene if necessary, and record video evidence.

---

## 2. When to Use & When NOT to Use

### When to Use
- Running live client demonstrations or operator walkthroughs.
- Debugging complex portal interactions or CAPTCHA challenges.
- Generating video recordings (`.webp`) for documentation.

### When NOT to Use
- Headless CI/CD test runners.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Windows desktop environment with display server, Google Chrome, and test claims.

### Prerequisites
- Settings configured with `headless=False`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Attended Settings Activation
Set `headless: false` in `SystemSettings` or pass `--attended` flag to launcher scripts.

### Step 2: Visible Window Launch
Launch Chrome with visible viewport (1280x800). Position window prominently on desktop.

### Step 3: Human Pacing Injection
Apply deliberate human pacing delays (500ms - 1500ms) between typing and click actions to emulate human behavior.

### Step 4: Video & Screen Recording
Initialize Playwright video recording or frame capture script (`record_all_8bots_attended.py`).

### Step 5: Interactive Operator Observation
Allow operator to observe portal navigation, CAPTCHA resolution, and table extraction in real time.

### Step 6: Recording Compression & Archival
Convert recorded frames into compressed WebP video and archive in `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never minimize or close the attended Chrome window while scraping is active.
- Ensure attended mode respects rate limits and human pacing.

---

## 6. Expected Deliverables & Artifacts
- Visible, attended scraper execution.
- Compressed demonstration video recording (.webp) in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Chrome window opens visibly and displays full automation sequence.
- [ ] Pacing is smooth and human-like without abrupt robotic jumps.
- [ ] Video recording is captured and committed to `docs/`.

---

## 8. Error Recovery & Troubleshooting
- If attended window loses focus or crashes, restart session cleanly via `Launch_Attended_Browser.bat`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-attended-mode` or run `scripts/record_all_8bots_attended.py`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-attended-mode` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-attended-mode`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-attended-mode` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-attended-mode`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-attended-mode`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-attended-mode` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `Launch_Attended_Browser.bat`
- `scripts/record_all_8bots_attended.py`
