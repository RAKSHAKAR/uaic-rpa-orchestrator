import sys

files = [
    "docs/Reports/2026-11-02_uaic_captcha_assessment_report_v1.md",
    "docs/Implementation Reports/UAIC_EIGHT_PORTAL_CAPTCHA_ASSESSMENT_REPORT.md"
]

target_block1 = """```mermaid
flowchart TD
    Run["Multi-Party Search Cycle (1 to 3 Searches)"] --> Check{"Challenge or Gate Triggered?"}
    
    Check -->|reCAPTCHA v2 / Turnstile| TokenWait["Wait for Anti-Captcha Token (<120s)"]
    TokenWait -->|Token Injected| Pass["Submit & Extract Cases"]
    TokenWait -->|Timeout Exceeded| CapErr["CaptchaResolutionError -> 2 Attempts -> Mark FAILED"]
    
    Check -->|Rapid Velocity (>5 req/min)| WAFCheck["Odyssey / Tyler WAF Rate Limit (Travis)"]
    WAFCheck --> HTTP429["HTTP 429 / WAF Block -> 600s Cooldown -> Celery Retry"]
    
    Check -->|Automation Signals Detected| PXCheck["PerimeterX Bot Challenge (Hillsborough)"]
    PXCheck --> PXBlock["'Access Denied - Automation Tools Detected' -> 300s Cooldown -> Celery Retry"]
```"""

replacement_block1 = """```mermaid
flowchart TD
    Run["Multi-Party Search Cycle: 1 to 3 Searches"] --> Check{"Challenge or Gate Triggered?"}
    
    Check -->|"reCAPTCHA v2 or Turnstile"| TokenWait["Wait for Anti-Captcha Token: under 120s"]
    TokenWait -->|"Token Injected"| Pass["Submit & Extract Cases"]
    TokenWait -->|"Timeout Exceeded"| CapErr["CaptchaResolutionError: 2 Attempts to Mark FAILED"]
    
    Check -->|"Rapid Velocity: over 5 req per min"| WAFCheck["Odyssey or Tyler WAF Rate Limit: Travis"]
    WAFCheck --> HTTP429["HTTP 429 WAF Block: 600s Cooldown and Celery Retry"]
    
    Check -->|"Automation Signals Detected"| PXCheck["PerimeterX Bot Challenge: Hillsborough"]
    PXCheck --> PXBlock["Access Denied Automation Tools Detected: 300s Cooldown and Celery Retry"]
```"""

target_block2 = """```mermaid
sequenceDiagram
    autonumber
    actor Worker as Celery Worker Task
    participant Scraper as County Scraper
    participant DOM as Chrome Page
    participant Detector as detect_security_block()
    participant CD as CooldownService
    participant Celery as Celery Queue
    participant DB as SQLite / PostgreSQL

    Worker->>Scraper: search_on_page(party_name)
    Scraper->>DOM: Navigate & Fill Form
    alt WAF / PerimeterX / 429 Detected
        DOM-->>Detector: HTML contains 'PerimeterX' or HTTP 429
        Detector-->>Scraper: raise SecurityBlockException(cooldown=300s/600s)
        Scraper->>CD: set_portal_cooldown(portal, seconds)
        Scraper->>DOM: capture_screenshot_on_error()
        DOM-->>DB: Save PNG to docs/frames/ & ErrorScreenshot table
        Scraper->>Celery: Schedule auto-retry task with countdown=cooldown+5s
        Scraper-->>Worker: Mark portal BLOCKED, isolate session, continue other portals
    else CAPTCHA Timeout Exceeded (>120s x 2 attempts)
        Scraper-->>Worker: raise CaptchaResolutionError
        Worker->>DOM: capture_screenshot_on_error()
        DOM-->>DB: Save PNG to docs/frames/ & ErrorScreenshot table
        Worker-->>DB: Mark portal FAILED, claim PARTIALLY_COMPLETED
    end
```"""

replacement_block2 = """```mermaid
sequenceDiagram
    autonumber
    actor Worker as Celery Worker Task
    participant Scraper as County Scraper
    participant DOM as Chrome Page
    participant Detector as Security Detector
    participant CD as CooldownService
    participant Celery as Celery Queue
    participant DB as System Database

    Worker->>Scraper: search_on_page(party_name)
    Scraper->>DOM: Navigate & Fill Form
    alt WAF or PerimeterX or 429 Detected
        DOM-->>Detector: HTML contains PerimeterX or HTTP 429
        Detector-->>Scraper: raise SecurityBlockException(cooldown=300s/600s)
        Scraper->>CD: set_portal_cooldown(portal, seconds)
        Scraper->>DOM: capture_screenshot_on_error()
        DOM-->>DB: Save PNG to docs/frames/ and ErrorScreenshot table
        Scraper->>Celery: Schedule auto-retry task with countdown=cooldown+5s
        Scraper-->>Worker: Mark portal BLOCKED, isolate session, continue other portals
    else CAPTCHA Timeout Exceeded
        Scraper-->>Worker: raise CaptchaResolutionError
        Worker->>DOM: capture_screenshot_on_error()
        DOM-->>DB: Save PNG to docs/frames/ and ErrorScreenshot table
        Worker-->>DB: Mark portal FAILED, claim PARTIALLY_COMPLETED
    end
```"""

for path in files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    norm_text = text.replace("\r\n", "\n")
    norm_t1 = target_block1.replace("\r\n", "\n")
    norm_r1 = replacement_block1.replace("\r\n", "\n")
    norm_t2 = target_block2.replace("\r\n", "\n")
    norm_r2 = replacement_block2.replace("\r\n", "\n")
    
    if norm_t1 in norm_text:
        norm_text = norm_text.replace(norm_t1, norm_r1)
        print(f"Patched block 1 in {path}")
    else:
        print(f"Warning: block 1 not found in {path}")
        
    if norm_t2 in norm_text:
        norm_text = norm_text.replace(norm_t2, norm_r2)
        print(f"Patched block 2 in {path}")
    else:
        print(f"Warning: block 2 not found in {path}")
        
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(norm_text)
