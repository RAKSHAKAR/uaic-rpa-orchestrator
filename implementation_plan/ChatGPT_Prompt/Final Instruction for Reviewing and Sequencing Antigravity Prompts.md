Please check all the `.md` files attached in the ZIP file line by line and determine the correct sequence in which they should be executed in Antigravity IDE as prompts.

Also, make sure that this solution is specifically intended for scraping data from the specified site(s). The solution we have developed must operate in a human-like and responsible manner while respecting the behavior, requirements, and terms of security systems such as reCAPTCHA, Cloudflare CAPTCHA, and similar protections. The implementation should minimize unnecessary triggering of these security protections while remaining compliant with the applicable website rules and restrictions.

If the system is blocked in exceptional cases, such as due to an IP address, MAC address, or any other site-specific restriction, it must not stop the entire process. Instead, it must continue processing the remaining site(s) and items.

The affected site or item must be marked as `Failed`, `Blocked`, or another appropriate status, and the system must capture the relevant error details, logs, and a screenshot for troubleshooting, auditing, and future retry purposes.

Once the applicable blocking or cooldown period has ended, based on the site's stated terms, conditions, retry guidance, or the response provided by the applicable CAPTCHA/security system, the system should automatically retry and resume processing the previously failed or blocked items.

The system must not attempt to bypass, defeat, or circumvent reCAPTCHA, Cloudflare CAPTCHA, or any other security or access-control mechanism. If human verification is required, the system must follow the site's permitted workflow and resume processing only when access is legitimately available.

While reviewing the `.md` files, please also identify whether the existing prompts already contain sufficient requirements to implement the above behavior. If any requirement is missing, incomplete, contradictory, or unclear, identify it and add a separate, properly structured prompt only where necessary.

Do not unnecessarily duplicate, rewrite, or change the intended requirements of the existing prompts.

Finally, provide the complete recommended execution sequence, including:

1. The exact `.md` file/prompt to run first.
2. The exact `.md` file/prompt to run next.
3. The purpose of each prompt.
4. Any dependency between prompts.
5. Any prompt that must be executed only after another prompt has been completed and validated.
6. Any additional prompt that should be added to address missing requirements.
7. The recommended validation/testing point after each major implementation stage.

The final sequence should ensure that Antigravity IDE implements the solution in the correct dependency order without skipping, duplicating, or conflicting with requirements from the existing `.md` files.