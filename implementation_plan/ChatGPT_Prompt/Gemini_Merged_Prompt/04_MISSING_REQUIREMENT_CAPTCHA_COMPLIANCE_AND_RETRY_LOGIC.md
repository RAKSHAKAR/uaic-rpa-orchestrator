System Task: Implement Graceful Security Handling, Automated Retries, and CAPTCHA Compliance

Context: This solution is specifically intended for scraping data from specified county/public sites. It must operate in a human-like, responsible manner while strictly respecting the behavior and terms of security systems (e.g., reCAPTCHA, Cloudflare CAPTCHA).

Implementation Requirements:

No Circumvention: The system must NEVER attempt to bypass, defeat, or circumvent reCAPTCHA, Cloudflare, or any access-control mechanism. If human verification is required, follow the site's permitted workflow and pause processing for that item until access is legitimately available.

Minimize Triggers: Implement human-like delays, jitter, and appropriate header management to minimize unnecessary triggering of security protections.

Non-Blocking Architecture: If the system is blocked in exceptional cases (e.g., IP address, MAC address, or site-specific rate limit), it MUST NOT stop the entire orchestrator process.

Error Capturing & Status Updates: The system must instantly mark the affected site/item as "Failed" or "Blocked". It must capture full error details, system logs, and save a full-page screenshot for troubleshooting and auditing.

Process Continuation: After capturing the failure state, the orchestrator must seamlessly continue processing the remaining site(s) and queued items in the dataset.

Automated Cooldown & Retry: Implement a scheduling mechanism that reads the site's stated terms, retry guidance (e.g., Retry-After headers), or standard cooldown periods. Once the cooldown has ended, the system must automatically retry and resume processing the previously failed/blocked items.