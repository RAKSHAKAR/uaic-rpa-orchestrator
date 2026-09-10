"""Dynamic runtime settings service backed by Redis with local fallback."""

import json
import logging
import os

import redis
import redis.asyncio as aioredis

from app.core.config import settings
from app.schemas.settings import (
    AutomationSettings,
    BrandingSettings,
    EmailSettings,
    FuzzyMatcherSettings,
    IntegrationSettings,
    PortalsSettings,
    StorageSettings,
    SystemSettings,
    TaskQueueSettings,
    get_default_chrome_binary,
    get_default_extension_dir,
)

logger = logging.getLogger("uaic_orchestrator.settings")
SETTINGS_REDIS_KEY = "uaic:system:settings:v4"


def get_default_settings() -> SystemSettings:
    """Build default settings from static environment config."""
    return SystemSettings(
        automation=AutomationSettings(
            max_captcha_attempts=2,
            captcha_wait_seconds=120,
            page_timeout_seconds=60,
            reload_backoff_seconds=2,
            headless_mode=getattr(settings, "PLAYWRIGHT_HEADLESS", False),
            browser_engine="chromium",
            use_chrome_browser=True,
            chrome_binary_path=get_default_chrome_binary(),
            chrome_extension_dir=get_default_extension_dir(),
            anticaptcha_api_key="28b486b8f31f74c6bf4453735815aa53",
            chrome_user_data_dir="",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            max_concurrent_claims=3,
        ),
        portals=PortalsSettings(
            broward_url="https://www.browardclerk.org/",
            broward_enabled=True,
            hillsborough_url="https://hover.hillsclerk.com/",
            hillsborough_enabled=True,
            miami_url="https://www2.miamidadeclerk.gov/ocs",
            miami_enabled=True,
            miami_username="apoorvnigam07@gmail.com",
            miami_password="Apoorv@12345",
            miami_requires_login=True,
            travis_url="https://odysseyweb.traviscountytx.gov/Portal/",
            travis_enabled=True,
            dallas_url="https://courtsportal.dallascounty.org/DALLASPROD/Home/",
            dallas_enabled=True,
            harris_jp_url="https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/",
            harris_jp_enabled=True,
            harris_cclerk_url="https://www.cclerk.hctx.net/Applications/WebSearch/",
            harris_cclerk_enabled=True,
            harris_district_url="https://www.hcdistrictclerk.com/",
            harris_district_enabled=True,
        ),
        matcher=FuzzyMatcherSettings(
            auto_match_threshold=getattr(settings, "FUZZY_MATCH_DEFAULT_THRESHOLD", 0.60),
            manual_review_threshold=getattr(settings, "FUZZY_MATCH_BORDERLINE_THRESHOLD", 0.40),
            scorer_algorithm="token_sort_ratio",
            min_filing_date="2010-01-01",
            clean_party_name_patterns=[
                "LLC",
                "INC",
                "CORP",
                "CORPORATION",
                "CO.",
                "COMPANY",
                "ET AL",
                "INDIVIDUALLY",
                "A/A/O",
                "AS ASSIGNEE OF",
                "D/B/A",
                "PA",
                "P.A.",
                "L.L.C.",
            ],
            whitelisted_statuses=getattr(settings, "ALLOWED_CASE_STATUSES", ["ACTIVE", "OPEN", "PENDING", "UNKNOWN", "FILED", "REOPENED"]),
            whitelisted_case_types=getattr(settings, "ALLOWED_CASE_TYPES", [
                "COUNTY CIVIL",
                "DISTRICT COURTS – CIVIL",
                "CIRCUIT CIVIL",
                "CIVIL",
                "AUTO NEGLIGENCE",
                "INSURANCE CLAIM",
                "CONTRACT AND INDEBTEDNESS",
                "JUSTICE OF THE PEACE – CIVIL",
            ]),
        ),
        integration=IntegrationSettings(
            guidewire_mock_mode=getattr(settings, "GUIDEWIRE_MOCK_MODE", True),
            guidewire_api_url=getattr(settings, "GUIDEWIRE_API_URL", "https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate"),
            guidewire_auth_type="Bearer",
            guidewire_api_key="gw_demo_token_xyz890",
            guidewire_client_id="uaic_service_account",
            guidewire_client_secret="sec_gw_secret_9981",
            guidewire_timeout_seconds=30,
            auto_push_on_match=True,
            notification_email="test@test.com",
        ),
        queue=TaskQueueSettings(
            max_task_retries=3,
            task_retry_delay_seconds=30,
            batch_chunk_size=25,
            auto_retry_failed_scrapes=True,
            max_concurrent_claims=3,
        ),
        branding=BrandingSettings(),
        storage=StorageSettings(),
        email=EmailSettings(),
    )


_local_settings_cache: SystemSettings | None = None


async def get_system_settings_async() -> SystemSettings:
    """Retrieve system settings from Redis with fallback to in-memory or default config."""
    global _local_settings_cache
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5, socket_timeout=0.5)
        raw = await r.get(SETTINGS_REDIS_KEY)
        await r.aclose()
        if raw:
            data = json.loads(raw)
            auto_data = data.setdefault("automation", {})
            chrome_bin = auto_data.get("chrome_binary_path", "")
            if not chrome_bin or not os.path.exists(chrome_bin):
                auto_data["chrome_binary_path"] = get_default_chrome_binary()
            ext_dir = auto_data.get("chrome_extension_dir", "")
            if not ext_dir or "D:\\UAIG" in ext_dir:
                auto_data["chrome_extension_dir"] = get_default_extension_dir()
            elif os.path.isabs(ext_dir) and not os.path.exists(ext_dir):
                auto_data["chrome_extension_dir"] = get_default_extension_dir()
            data.setdefault("branding", {})
            data.setdefault("email", {})
            return SystemSettings.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to fetch settings from Redis: {e}. Using in-memory fallback.")

    return _local_settings_cache or get_default_settings()


def get_system_settings_sync() -> SystemSettings:
    """Synchronous getter for settings (used by Celery workers if outside event loop)."""
    global _local_settings_cache
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5, socket_timeout=0.5)
        raw = r.get(SETTINGS_REDIS_KEY)
        if raw:
            data = json.loads(raw)
            auto_data = data.setdefault("automation", {})
            chrome_bin = auto_data.get("chrome_binary_path", "")
            if not chrome_bin or not os.path.exists(chrome_bin):
                auto_data["chrome_binary_path"] = get_default_chrome_binary()
            ext_dir = auto_data.get("chrome_extension_dir", "")
            if not ext_dir or "D:\\UAIG" in ext_dir:
                auto_data["chrome_extension_dir"] = get_default_extension_dir()
            elif os.path.isabs(ext_dir) and not os.path.exists(ext_dir):
                auto_data["chrome_extension_dir"] = get_default_extension_dir()
            data.setdefault("branding", {})
            data.setdefault("email", {})
            return SystemSettings.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to fetch settings from Redis (sync): {e}. Using in-memory fallback.")

    return _local_settings_cache or get_default_settings()


async def save_system_settings_async(new_settings: SystemSettings) -> SystemSettings:
    """Save system settings into Redis with in-memory fallback."""
    global _local_settings_cache
    _local_settings_cache = new_settings
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5, socket_timeout=0.5)
        await r.set(SETTINGS_REDIS_KEY, new_settings.model_dump_json())
        await r.aclose()
        logger.info("System settings saved to Redis successfully.")
    except Exception as e:
        logger.warning(f"Failed to persist settings to Redis: {e}. Preserved in local memory cache.")

    return new_settings


async def reset_system_settings_async() -> SystemSettings:
    """Reset system settings to initial default configuration in Redis and memory."""
    global _local_settings_cache
    default_cfg = get_default_settings()
    _local_settings_cache = default_cfg
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5, socket_timeout=0.5)
        await r.set(SETTINGS_REDIS_KEY, default_cfg.model_dump_json())
        await r.aclose()
        logger.info("System settings reset to default in Redis.")
    except Exception as e:
        logger.warning(f"Failed to reset settings in Redis: {e}. Reset local memory cache.")

    return default_cfg
