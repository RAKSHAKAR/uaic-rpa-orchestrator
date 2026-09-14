# Security, CAPTCHA Compliance & Error Handling Guidelines

**1. Primary Objective & Compliance**
This solution is specifically intended for scraping data from the specified county/court site(s). The solution must operate in a human-like and responsible manner while strictly respecting the behavior, requirements, and terms of security systems such as reCAPTCHA, Cloudflare CAPTCHA, and similar protections. The implementation should minimize unnecessary triggering of these security protections while remaining 100% compliant with the applicable website rules and restrictions.

**2. Strict Non-Circumvention Rule**
The system must NOT attempt to bypass, defeat, or circumvent reCAPTCHA, Cloudflare CAPTCHA, or any other security or access-control mechanism. If human verification is required, the system must follow the site's permitted workflow (e.g., pausing the automation) and resume processing only when access is legitimately available.

**3. Non-Blocking Architecture & Exception Handling**
If the system is blocked in exceptional cases—such as due to an IP address block, MAC address restriction, or any other site-specific rate limit—it must NOT stop the entire orchestration process. Instead, it must continue processing the remaining site(s) and queue items.

**4. Error Logging & Evidence Capture**
When an affected site or item is blocked, it must be instantly marked with `Failed`, `Blocked`, or another appropriate status. The system must capture the relevant error details, system logs, and a full-page screenshot for troubleshooting, auditing, and future retry purposes.

**5. Automated Cooldown & Retry Logic**
Once the applicable blocking or cooldown period has ended—based on the site's stated terms, conditions, retry guidance (e.g., `Retry-After` headers), or the response provided by the applicable CAPTCHA/security system—the system should automatically retry and resume processing the previously failed or blocked items.