---
name: uaic-captcha-handling
description: >-
  Safe CAPTCHA resolution with AntiCaptcha MV3 extension, Turnstile/reCAPTCHA token inspection, and timeout limits.
---

# Uaic Captcha Handling

## 1. Purpose & Overview
Governs the detection, automated resolution, and verification of Google reCAPTCHA v2/v3 and Cloudflare Turnstile challenges across court portals, strictly blocking speculative form submits when challenges remain unsolved.

---

## 2. When to Use & When NOT to Use

### When to Use
- Navigating portals with active CAPTCHA challenges (Broward, Travis, Hillsborough).
- Configuring AntiCaptcha API key and solving timeouts.

### When NOT to Use
- Portals without CAPTCHA protections (Dallas, Harris JP).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Playwright Page instance, AntiCaptcha extension, and configured `captcha_wait_seconds`.

### Prerequisites
- AntiCaptcha API key configured in `SystemSettings`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: CAPTCHA Challenge Detection
Inspect DOM for challenge indicators: `iframe[src*='recaptcha']`, `iframe[src*='turnstile']`, `#cf-turnstile`, or `div.g-recaptcha`.

### Step 2: Extension Solving Wait Loop
Wait up to `captcha_wait_seconds` (default 25-45s) for AntiCaptcha extension to solve the challenge.

### Step 3: Token & Solution Verification
Inspect DOM for solve tokens: `g-recaptcha-response` value length > 25, `cf-turnstile-response` length > 20, or extension `.solved_flag`.

### Step 4: Active Challenge Safety Gate
If unsolved after timeout, call `has_active_captcha_challenge(page)`. If active challenge remains, raise `CaptchaResolutionError`. Strictly block speculative search submission.

### Step 5: Token Injection Fallback
If solved, ensure response token is populated in hidden form inputs before triggering search click.

### Step 6: Screenshot on Failure
If resolution fails, capture error screenshot and record failed CAPTCHA event in audit log.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: NEVER click search button speculatively when an active, unsolved CAPTCHA challenge is present (prevents portal IP bans).
- Never bypass CAPTCHA wait loops.

---

## 6. Expected Deliverables & Artifacts
- Verified CAPTCHA resolution with valid response tokens.
- Safe `CaptchaResolutionError` handling on timeout.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] CAPTCHA tokens are validated before form submission.
- [ ] Unsolved challenges raise `CaptchaResolutionError` and capture screenshots.
- [ ] Zero speculative submits occur during active challenges.

---

## 8. Error Recovery & Troubleshooting
- If AntiCaptcha account balance is exhausted, trigger operator notification email via `NotificationRule`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-captcha-handling`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-captcha-handling` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-captcha-handling`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-captcha-handling` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-captcha-handling`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-captcha-handling`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-captcha-handling` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/base.py` - `has_active_captcha_challenge`
- `backend/scripts/test_broward_turnstile_box.py`
