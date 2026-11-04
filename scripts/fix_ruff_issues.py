"""Fix all ruff warnings in error_classifier, base, scraper_tasks, and test_captcha_waf_session_redispatch."""

from pathlib import Path

# 1. error_classifier.py
ec_path = Path("backend/app/services/error_classifier.py")
ec_text = ec_path.read_text(encoding="utf-8")
ec_text = ec_text.replace("class ErrorCode(str, enum.Enum):", "class ErrorCode(enum.StrEnum):")
ec_text = ec_text.replace("class ErrorCategory(str, enum.Enum):", "class ErrorCategory(enum.StrEnum):")
ec_text = ec_text.replace("class ErrorSeverity(str, enum.Enum):", "class ErrorSeverity(enum.StrEnum):")
ec_text = ec_text.replace("class RecoveryAction(str, enum.Enum):", "class RecoveryAction(enum.StrEnum):")
ec_path.write_text(ec_text, encoding="utf-8")
print("Fixed error_classifier.py")

# 2. base.py
b_path = Path("backend/app/automation/base.py")
b_text = b_path.read_text(encoding="utf-8")
b_text = b_text.replace('message=f"WAF rate limit" if', 'message="WAF rate limit" if')
# In BaseCourtScraper.detect_security_block:
# replace DataDome cooldown = 300 with generic_waf_cd
b_text = b_text.replace("""            # 3. Check DataDome / Akamai / Turnstile Bot Defenses
            if any(
                term in body_text or term in title_lower
                for term in [
                    "datadome",
                    "protected by datadome",
                    "turnstile",
                    "challenges.cloudflare.com",
                ]
            ):
                cooldown = 300""", """            # 3. Check DataDome / Akamai / Turnstile Bot Defenses
            if any(
                term in body_text or term in title_lower
                for term in [
                    "datadome",
                    "protected by datadome",
                    "turnstile",
                    "challenges.cloudflare.com",
                ]
            ):
                cooldown = generic_waf_cd""")

b_text = b_text.replace("""            # 4. Check Cloudflare 1020 / WAF Block
            if any(
                term in body_text or term in title_lower
                for term in [
                    "error 1020",
                    "access denied",
                    "attention required! | cloudflare",
                    "blocked by cloudflare",
                    "cloudflare ray id",
                    "sorry, you have been blocked",
                    "security service to protect itself from online attacks",
                ]
            ):
                cooldown = 300""", """            # 4. Check Cloudflare 1020 / WAF Block
            if any(
                term in body_text or term in title_lower
                for term in [
                    "error 1020",
                    "access denied",
                    "attention required! | cloudflare",
                    "blocked by cloudflare",
                    "cloudflare ray id",
                    "sorry, you have been blocked",
                    "security service to protect itself from online attacks",
                ]
            ):
                cooldown = generic_waf_cd""")

b_text = b_text.replace("""            # 5. Check IP Ban / Forbidden
            if any(
                term in body_text or term in title_lower
                for term in [
                    "your ip has been blocked",
                    "ip address has been banned",
                    "client ip forbidden",
                    "access has been restricted",
                ]
            ):
                cooldown = 600""", """            # 5. Check IP Ban / Forbidden
            if any(
                term in body_text or term in title_lower
                for term in [
                    "your ip has been blocked",
                    "ip address has been banned",
                    "client ip forbidden",
                    "access has been restricted",
                ]
            ):
                cooldown = ip_ban_cd""")
b_path.write_text(b_text, encoding="utf-8")
print("Fixed base.py")

# 3. scraper_tasks.py
st_path = Path("backend/app/tasks/scraper_tasks.py")
st_text = st_path.read_text(encoding="utf-8")
st_text = st_text.replace(
    "from app.services.error_classifier import ErrorCategory, ErrorCode, classify_exception",
    "from app.services.error_classifier import ErrorCategory, ErrorCode",
)
st_text = st_text.replace(
    "    PortalOperationalState,\n    check_portal_ready_for_redispatch,\n    is_portal_in_cooldown,",
    "    PortalOperationalState,\n    is_portal_in_cooldown,",
)
st_path.write_text(st_text, encoding="utf-8")
print("Fixed scraper_tasks.py")

# 4. test_captcha_waf_session_redispatch.py
t_path = Path("backend/tests/test_captcha_waf_session_redispatch.py")
t_text = t_path.read_text(encoding="utf-8")
t_text = t_text.replace("import time\n", "")
t_text = t_text.replace("    get_all_portal_cooldowns,\n", "")
t_text = t_text.replace("    ErrorSeverity,\n", "")
t_path.write_text(t_text, encoding="utf-8")
print("Fixed test_captcha_waf_session_redispatch.py")

