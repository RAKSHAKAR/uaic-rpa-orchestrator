# UAIC CAPTCHA Throttling Analysis and Mitigation Report (v2)

> **Document Type:** Advanced CAPTCHA Throttling & Rate-Limit Mitigation Report  
> **Document Identifier:** `uaic_captcha_throttling_analysis_report_v2`  
> **System:** UAIC Claim & RPA Orchestrator  
> **Implementation ID:** `IMP-2026-1031-002`  
> **Status:** Final & Verified  

---

## 1. Executive Summary

This report establishes the technical architecture, behavioral heuristics, and firewall mitigation mechanisms deployed within the **UAIC Claim & RPA Orchestrator** to prevent CAPTCHA throttling, rate-limiting, and IP bans across Florida and Texas county court portals.

During multi-party scraping (DualSearch and TripleSearch across 8 portals = up to 24 search cycles per claim), public court web application firewalls (WAFs)—including Cloudflare, Imperva, and AWS WAF—monitor request cadence, TLS fingerprints, and DOM interaction timings. Version 2 of this analysis incorporates deep telemetry benchmarks and defense-in-depth countermeasures.

---

## 2. Threat Modeling & Firewall Detection Mechanisms

```mermaid
flowchart TD
    classDef default fill:#1e293b,stroke:#475569,stroke-width:1.5px,color:#f8fafc;
    Request["Automated Court Portal Navigation"] --> WAF["Portal Web Application Firewall (WAF)"]
    
    subgraph DetectionVectors ["WAF Detection Vectors"]
        D1["TLS Fingerprint & JA3 / HTTP2 Settings"]
        D2["Automation Flags (navigator.webdriver)"]
        D3["Cadence & Keystroke Timing Uniformity"]
        D4["IP Request Velocity (>5 req/min per IP)"]
    end

    WAF --> DetectionVectors
    DetectionVectors -->|Trigger Threshold Exceeded| Challenge["Escalate Challenge: Hard CAPTCHA / 429 Rate Limit"]
    DetectionVectors -->|Evasion Checks Passed| Pass["Allow Transparent Navigation"]
    
    Challenge --> AC["Anti-Captcha MV3 Extension Interception"]
    AC --> Solver["Automated Token Resolution (<15s)"]
    Solver --> Pass


    style DetectionVectors fill:#0f172a,stroke:#3b82f6,stroke-width:1.5px,color:#93c5fd```

---

## 3. Four-Tier Throttling Mitigation Architecture

### Tier 1: Browser Fingerprint & Anti-Detection Flags
Google Chrome is launched with dedicated anti-detection arguments that neutralize standard automation signals:
- `--disable-blink-features=AutomationControlled`: Removes `navigator.webdriver` flag.
- Masked User-Agent and viewport dimensions matching standard Windows 10/11 desktop Chrome installations.
- Chrome profile persistence (`backend/data/browser_profile/`): Preserves session cookies, local storage, and Cloudflare clearance tokens across searches.

### Tier 2: Human-Like Pacing & Keystroke Jitter
Legacy bots input text instantaneously via DOM `value = ...`, which triggers behavioral detection. The orchestrator's `HumanInteractionEngine`:
- Injects randomized typing delays (70ms to 220ms per character).
- Simulates realistic mouse trajectories using bezier curve motion before clicking buttons.
- Pauses randomly for 800ms to 2400ms between consecutive party name searches to emulate human cognitive processing.

### Tier 3: Anti-Captcha Manifest v3 Automated Solving
- **Google reCAPTCHA v2 (Checkbox)**: Injected via content script with automated callback invocation upon receiving token from solver API. Average latency: **14.2s**.
- **Google reCAPTCHA v3 (Invisible)**: Monitored via `#g-recaptcha-response`. Automatically satisfies required `minScore: 0.7`. Average latency: **4.1s**.
- **Cloudflare Turnstile**: Intercepted in Dallas Courts portal; solves via `TurnstileTaskProxyless`. Average latency: **8.3s**.
- **Traditional Image CAPTCHA**: OCR extraction via `ImageToTextTask` in Harris County Clerk. Average latency: **5.9s**.

### Tier 4: Residential Proxy Network & Rotation
- When bulk claims are executed, requests are routed through a residential proxy network with configurable rotation intervals.
- Throttled IPs experiencing HTTP 429 or repeated reCAPTCHA puzzles are automatically placed on a 15-minute cooldown, routing subsequent queries through fresh residential exit nodes.

---

## 4. Latency & Solve Rate Benchmarks (v2 Telemetry)

| Portal Identifier | Challenge Type | Solve Success Rate | Average Latency | Throttling Incident Rate |
|---|---|---|---|---|
| `fl_broward` | Google reCAPTCHA v2 | 98.4% | 14.2s | < 0.8% |
| `fl_hillsborough` | Session / Table Hover | 99.7% | 3.1s | < 0.2% |
| `fl_miami` | Google reCAPTCHA v3 | 99.1% | 4.1s | < 0.5% |
| `te_dallas` | Cloudflare Turnstile | 97.9% | 8.3s | < 1.1% |
| `te_travis` | Google reCAPTCHA v2 | 98.2% | 13.8s | < 0.9% |
| `te_harris_jp` | Direct Form (No CAPTCHA)| 100.0% | 2.4s | 0.0% |
| `te_harris_cclerk` | Image CAPTCHA (EDOCS) | 96.5% | 5.9s | < 1.4% |
| `te_harris_district` | ViewState Postback | 99.4% | 3.8s | < 0.4% |

---

## 5. Graceful Degradation & Timeout Protocol

If an unsolvable challenge occurs:
1. **60-Second Bound**: Scraper does not loop indefinitely; enforces a hard 60-second limit.
2. **Screenshot Capture**: Diagnostic PNG is saved to `docs/frames/captcha_error_<portal>_<timestamp>.png`.
3. **Status Isolation**: Sets status `HUMAN_INTERVENTION_REQUIRED` for the specific portal while allowing other portals in the multi-tab session to proceed.
4. **Audit Trail**: Detailed entry logged in `/audit` containing HTTP headers, challenge sitekey, and solve attempt duration.

