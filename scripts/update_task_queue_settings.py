"""Update TaskQueueSettings schema to include portal-specific WAF cooldown settings."""

from pathlib import Path

settings_path = Path("backend/app/schemas/settings.py")
text = settings_path.read_text(encoding="utf-8")

target = """    claim_timeout_minutes: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Watchdog timeout in minutes before marking a stuck/interrupted claim",
    )"""

replacement = """    claim_timeout_minutes: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Watchdog timeout in minutes before marking a stuck/interrupted claim",
    )
    waf_rate_limit_cooldown_seconds: int = Field(
        default=600,
        ge=10,
        le=3600,
        description="Cooldown delay in seconds for WAF rate-limiting (Travis County 600s)",
    )
    perimeterx_cooldown_seconds: int = Field(
        default=300,
        ge=10,
        le=1800,
        description="Cooldown delay in seconds for PerimeterX / HUMAN Security challenges (Hillsborough County 300s)",
    )
    ip_ban_cooldown_seconds: int = Field(
        default=600,
        ge=10,
        le=7200,
        description="Cooldown delay in seconds for IP restriction / ban blocks",
    )
    generic_waf_cooldown_seconds: int = Field(
        default=300,
        ge=10,
        le=1800,
        description="Default cooldown delay in seconds for generic WAF / Cloudflare challenges",
    )"""

if target in text:
    new_text = text.replace(target, replacement, 1)
    settings_path.write_text(new_text, encoding="utf-8")
    print("SUCCESS: TaskQueueSettings updated with WAF cooldown fields.")
else:
    print("ERROR: Target block not found in settings.py")

