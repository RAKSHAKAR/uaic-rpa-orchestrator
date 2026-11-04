"""Update base.py to use dynamic cooldown settings and exact observed block strings."""

from pathlib import Path

base_path = Path("backend/app/automation/base.py")
text = base_path.read_text(encoding="utf-8")

# 1. Update module-level detect_security_block to recognize WAF rate limit and apply 600s default for Travis/Odyssey
old_mod_block = """    if status_code == 429:
        raise SecurityBlockException(
            message=f"Rate limit exceeded (HTTP 429) on {portal_key or 'portal'}",
            cooldown_seconds=default_cooldown,
            portal_key=portal_key,
        )"""

new_mod_block = """    if status_code == 429:
        effective_cd = 600 if portal_key and "travis" in str(portal_key).lower() else default_cooldown
        raise SecurityBlockException(
            message=f"WAF rate limit" if portal_key and "travis" in str(portal_key).lower() else f"Rate limit exceeded (HTTP 429) on {portal_key or 'portal'}",
            cooldown_seconds=effective_cd,
            portal_key=portal_key,
        )"""

if old_mod_block in text:
    text = text.replace(old_mod_block, new_mod_block, 1)
    print("SUCCESS: Module-level detect_security_block updated.")
else:
    print("WARNING: old_mod_block not found.")

# Also add check for "waf rate limit" in html_text in module-level
old_ray_id = """        if "ray id" in lower_html and any(
            term in lower_html for term in ["access denied", "blocked", "attention required"]
        ):
            raise SecurityBlockException(
                message=f"WAF block page detected on {portal_key or 'portal'}",
                cooldown_seconds=default_cooldown,
                portal_key=portal_key,
            )"""

new_ray_id = """        if "waf rate limit" in lower_html or ("rate limit" in lower_html and "cooldown" in lower_html):
            effective_cd = 600 if portal_key and "travis" in str(portal_key).lower() else default_cooldown
            raise SecurityBlockException(
                message="WAF rate limit",
                cooldown_seconds=effective_cd,
                portal_key=portal_key,
            )
        if "ray id" in lower_html and any(
            term in lower_html for term in ["access denied", "blocked", "attention required"]
        ):
            raise SecurityBlockException(
                message=f"WAF block page detected on {portal_key or 'portal'}",
                cooldown_seconds=default_cooldown,
                portal_key=portal_key,
            )"""

if old_ray_id in text:
    text = text.replace(old_ray_id, new_ray_id, 1)
    print("SUCCESS: WAF rate limit check added to module-level.")
else:
    print("WARNING: old_ray_id not found.")

# 2. Update BaseCourtScraper.detect_security_block
old_method_start = """            # 1. Check Rate Limit / 429
            if any(
                term in body_text or term in title_lower
                for term in [
                    "429 too many requests",
                    "rate limit exceeded",
                    "too many requests",
                    "rate limited",
                    "request limit reached",
                    "retry after",
                ]
            ):
                cooldown = 180
                reason = "Rate Limit Exceeded (HTTP 429 / Throttled)"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown

            # 2. Check PerimeterX / HUMAN Security
            if any(
                term in body_text or term in title_lower
                for term in [
                    "perimeterx",
                    "powered by perimeterx",
                    "access to this page has been denied because we believe you are using automation tools",
                    "automation tools to browse",
                    "px-captcha",
                    "press & hold",
                    "press and hold",
                    "_pxhd",
                    "perimeterx, inc",
                ]
            ):
                cooldown = 300
                reason = "PerimeterX WAF Challenge: Automation Tools Detected"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown"""

new_method_start = """            # Query settings for dynamic cooldowns
            waf_rate_limit_cd = 600
            perimeterx_cd = 300
            generic_waf_cd = 300
            ip_ban_cd = 600
            try:
                from app.services.settings_service import get_system_settings_sync
                sys_cfg = get_system_settings_sync()
                if sys_cfg and hasattr(sys_cfg, "task_queue"):
                    waf_rate_limit_cd = getattr(sys_cfg.task_queue, "waf_rate_limit_cooldown_seconds", 600)
                    perimeterx_cd = getattr(sys_cfg.task_queue, "perimeterx_cooldown_seconds", 300)
                    generic_waf_cd = getattr(sys_cfg.task_queue, "generic_waf_cooldown_seconds", 300)
                    ip_ban_cd = getattr(sys_cfg.task_queue, "ip_ban_cooldown_seconds", 600)
            except Exception:
                pass

            # 1. Check Rate Limit / 429 / WAF Throttling
            if any(
                term in body_text or term in title_lower
                for term in [
                    "429 too many requests",
                    "rate limit exceeded",
                    "too many requests",
                    "rate limited",
                    "request limit reached",
                    "retry after",
                    "waf rate limit",
                ]
            ):
                cooldown = waf_rate_limit_cd
                reason = "WAF rate limit"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown

            # 2. Check PerimeterX / HUMAN Security
            if any(
                term in body_text or term in title_lower
                for term in [
                    "perimeterx",
                    "powered by perimeterx",
                    "access to this page has been denied because we believe you are using automation tools",
                    "automation tools to browse",
                    "px-captcha",
                    "press & hold",
                    "press and hold",
                    "_pxhd",
                    "perimeterx, inc",
                ]
            ):
                cooldown = perimeterx_cd
                reason = "PerimeterX WAF Challenge: Automation Tools Detected"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown"""

if old_method_start in text:
    text = text.replace(old_method_start, new_method_start, 1)
    print("SUCCESS: BaseCourtScraper.detect_security_block updated with dynamic cooldowns.")
else:
    print("WARNING: old_method_start not found.")

base_path.write_text(text, encoding="utf-8")
print("Done writing base.py")

