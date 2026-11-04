# Historical Implementation: CAPTCHA Resolution & Browser Engine

> **Subsystem:** Anti-Captcha MV3 Integration & Playwright Browser Engine  
> **Historical Scope:** October 2026 Engineering Sprints  
> **Status:** Fully Remediated, Benchmarked & Verified  

---

## 1. Anti-Captcha Extension Architecture (Manifest v3)

The project migrated browser automation from basic Playwright headless mode to a genuine Google Chrome instance with the official Anti-Captcha extension (`anticaptcha-plugin_v0.83`).

### Key Implementation Actions:
- **Manifest v3 Service Worker**: Adapted scraper hooks to respect Chrome MV3 security policies where background scripts run as service workers.
- **Automated API Key Injection**: Implemented automatic population of `antiCapthaPredefinedApiKey` in `anticaptcha-plugin_v0.83/js/config_ac_api_key.js` dynamically from `SystemSettings` at session launch.
- **One-Click Extension Setup (`POST /api/v1/settings/setup-extension`)**:
  - Automatically pins extension to Chrome toolbar in `Default/Preferences`.
  - Verifies account balance against `https://api.anti-captcha.com/getBalance`.
  - Opens visual attended browser for 5 seconds to verify extension activation.

---

## 2. Multi-Challenge CAPTCHA Handling

| Challenge Type | Target Portals | Solver Mechanism | Fallback Behavior |
|---|---|---|---|
| **Google reCAPTCHA v2** | Broward, Hillsborough, Travis | `RecaptchaV2TaskProxyless` injected via content script | 60s timeout -> screenshot -> `HUMAN_INTERVENTION_REQUIRED` |
| **Google reCAPTCHA v3** | Miami-Dade OCS | `RecaptchaV3TaskProxyless` (minScore: 0.7) | Inserts token into `#g-recaptcha-response` and triggers callback |
| **Cloudflare Turnstile** | Dallas Courts Portal | `TurnstileTaskProxyless` | Waits for `input[name="cf-turnstile-response"]` value |
| **Traditional Image CAPTCHA** | Harris County Clerk (EDOCS) | `ImageToTextTask` OCR solver | Types text into `#txtCaptcha` |

---

## 3. Playwright Browser Flags & Anti-Detection

To eliminate Cloudflare and bot-detection challenges, `BrowserManager` launches Google Chrome with strict production flags:
- `--disable-blink-features=AutomationControlled`
- `--no-sandbox`, `--disable-infobars`
- `--load-extension` and `--disable-extensions-except` pointing to `anticaptcha-plugin_v0.83/`
- Realistic user agent strings matching modern Windows desktop Chrome.
- Preserves Chrome user profile data across sessions in `backend/data/browser_profile/` to retain session cookies and Cloudflare tokens.

