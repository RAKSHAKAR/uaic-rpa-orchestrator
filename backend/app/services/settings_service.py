"""Durable runtime settings with a database source of truth and Redis cache."""

import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import redis.asyncio as aioredis
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import TaskAsyncSessionLocal
from app.models.guidewire import AutomationSetting, SettingsAuditLog
from app.schemas.settings import (
    AutomationSettings,
    BrandingSettings,
    EmailSettings,
    FuzzyMatcherSettings,
    IntegrationSettings,
    PortalsSettings,
    ProxySettings,
    StorageSettings,
    SystemSettings,
    TaskQueueSettings,
    get_default_chrome_binary,
    get_default_extension_dir,
)

logger = logging.getLogger("uaic_orchestrator.settings")
SETTINGS_REDIS_KEY = "uaic:system:settings:v4"
SETTINGS_DB_KEY = "system_settings_v4"



class SettingsUnavailableError(RuntimeError):
    """The durable settings document could not be read or written."""


class SettingsConflictError(RuntimeError):
    """Another operator changed settings after this revision was loaded."""


def get_default_settings() -> SystemSettings:
    """Build default settings from static environment config."""
    return SystemSettings(
        automation=AutomationSettings(
            max_captcha_attempts=2,
            captcha_wait_seconds=45,
            page_timeout_seconds=35,
            reload_backoff_seconds=2,
            headless_mode=getattr(settings, "PLAYWRIGHT_HEADLESS", False),
            browser_engine="chromium",
            use_chrome_browser=False,
            chrome_binary_path=get_default_chrome_binary(),
            chrome_extension_dir=get_default_extension_dir(),
            anticaptcha_api_key=os.environ.get("ANTICAPTCHA_API_KEY", ""),
            chrome_user_data_dir="",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            max_concurrent_claims=10,
            extension_setup_verified=False,
            extension_setup_timestamp=None,
            typing_speed_mode="turbo",
            typing_delay_ms=0,
            action_pacing_ms=50,
            stealth_clicks=False,
        ),
        portals=PortalsSettings(
            broward_url=getattr(settings, "PORTAL_BROWARD_URL", "https://www.browardclerk.org/Web2"),
            broward_enabled=True,
            hillsborough_url=getattr(settings, "PORTAL_HILLSBOROUGH_URL", "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"),
            hillsborough_enabled=True,
            miami_url=getattr(settings, "PORTAL_MIAMI_URL", "https://www2.miamidadeclerk.gov/ocs"),
            miami_enabled=True,
            miami_username=os.environ.get("MIAMI_USERNAME", ""),
            miami_password=os.environ.get("MIAMI_PASSWORD", ""),
            miami_requires_login=True,
            travis_url=getattr(settings, "PORTAL_TRAVIS_URL", "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"),
            travis_enabled=True,
            dallas_url=getattr(settings, "PORTAL_DALLAS_URL", "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"),
            dallas_enabled=True,
            harris_jp_url=getattr(settings, "PORTAL_HARRIS_JP_URL", "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"),
            harris_jp_enabled=True,
            harris_cclerk_url=getattr(settings, "PORTAL_HARRIS_CCLERK_URL", "https://www.cclerk.hctx.net/Applications/WebSearch/"),
            harris_cclerk_enabled=True,
            harris_district_url=getattr(settings, "PORTAL_HARRIS_DISTRICT_URL", "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"),
            harris_district_enabled=True,
        ),
        matcher=FuzzyMatcherSettings(
            auto_match_threshold=getattr(settings, "FUZZY_MATCH_DEFAULT_THRESHOLD", 0.60),
            manual_review_threshold=getattr(settings, "FUZZY_MATCH_BORDERLINE_THRESHOLD", 0.40),
            scorer_algorithm="partial_ratio",
            min_filing_date="2010-01-01",
            unique_names_threshold=0.60,
        ),
        integration=IntegrationSettings(
            guidewire_mock_mode=getattr(settings, "GUIDEWIRE_MOCK_MODE", True),
            guidewire_api_url=getattr(settings, "GUIDEWIRE_API_URL", "https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate"),
            guidewire_auth_type="Bearer",
            guidewire_api_key=settings.GUIDEWIRE_API_KEY,
            guidewire_client_id=os.environ.get("GUIDEWIRE_CLIENT_ID", ""),
            guidewire_client_secret=os.environ.get("GUIDEWIRE_CLIENT_SECRET", ""),
            guidewire_timeout_seconds=30,
            auto_push_on_match=True,
            notification_email="test@test.com",
        ),
        queue=TaskQueueSettings(
            max_task_retries=2,
            task_retry_delay_seconds=30,
            batch_chunk_size=25,
            auto_retry_failed_scrapes=True,
            max_concurrent_claims=10,
            claim_timeout_minutes=30,
        ),
        branding=BrandingSettings(),
        storage=StorageSettings(),
        email=EmailSettings(),
        proxy=ProxySettings(),
    )


def _normalize_portals_data(data: dict) -> bool:
    """Migrate legacy portal URLs to the required defaults (Requirement #33). Returns True if mutated."""
    portals = data.setdefault("portals", {})
    # V4-authoritative CountyWebsite URL targets (from PA_FuzzyMatch_ActivityCreation_v1_Main workflow)
    V4_PORTAL_URLS: dict[str, str] = {
        "broward_url": "https://www.browardclerk.org/Web2",
        "hillsborough_url": "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab",
        "miami_url": "https://www2.miamidadeclerk.gov/ocs",
        "travis_url": "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29",
        "dallas_url": "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29",
        "harris_jp_url": "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29",
        "harris_cclerk_url": "https://www.cclerk.hctx.net/Applications/WebSearch/",
        "harris_district_url": "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx",
    }
    known_legacy: dict[str, set[str]] = {
        "broward_url": {"https://www.browardclerk.org/", "https://www.browardclerk.org"},
        "hillsborough_url": {"https://hover.hillsclerk.com/", "https://hover.hillsclerk.com"},
        "miami_url": {"https://onlineservices.miami-dadeclerk.com/civil/", "https://onlineservices.miami-dadeclerk.com/civil"},
        "travis_url": {"https://odysseyweb.traviscountytx.gov/Portal/", "https://odysseyweb.traviscountytx.gov/Portal"},
        "dallas_url": {"https://courtsportal.dallascounty.org/DALLASPROD/Home/", "https://courtsportal.dallascounty.org/DALLASPROD/Home"},
        "harris_jp_url": {"https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/", "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home"},
        "harris_cclerk_url": {
            "https://www.cclerk.hctx.net/applications/websearch/courtsearch.aspx?CaseType=Civil",
            "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx",
        },
        "harris_district_url": {"https://www.hcdistrictclerk.com/", "https://www.hcdistrictclerk.com"},
    }
    changed = False
    for field, new_val in V4_PORTAL_URLS.items():
        current = portals.get(field, "")
        if not current or current in known_legacy.get(field, set()):
            portals[field] = new_val
            changed = True
    return changed


def _decode_row(row: AutomationSetting) -> SystemSettings:
    value = getattr(row, "value", row)
    if not isinstance(value, dict):
        raise SettingsUnavailableError("Stored settings document is invalid")
    revision = value.get("version", 1)
    document = value.get("settings", value)
    try:
        result = SystemSettings.model_validate(document)
        result.version = int(revision)
        # Auto-upgrade legacy slowness defaults to high-speed values
        if result.automation.captcha_wait_seconds == 120:
            result.automation.captcha_wait_seconds = 45
        if result.automation.page_timeout_seconds == 60:
            result.automation.page_timeout_seconds = 35
        if result.automation.reload_backoff_seconds == 5:
            result.automation.reload_backoff_seconds = 2
        if result.automation.action_pacing_ms == 100:
            result.automation.action_pacing_ms = 50
        if not getattr(result.queue, "claim_timeout_minutes", None) or result.queue.claim_timeout_minutes < 30:
            result.queue.claim_timeout_minutes = 30
        if not getattr(result.matcher, "unsearchable_party_patterns", None):
            result.matcher.unsearchable_party_patterns = FuzzyMatcherSettings().unsearchable_party_patterns
        return result
    except Exception as exc:
        logger.error("Stored settings validation failed (%s)", type(exc).__name__)
        raise SettingsUnavailableError("Stored settings document is invalid") from None


def _database_value(document: SystemSettings, version: int) -> dict:
    return {"version": version, "settings": document.model_dump(exclude={"version"})}


async def _read_legacy_redis_document() -> SystemSettings:
    """Read the previous Redis key once when the durable row is absent."""
    client = aioredis.from_url(
        settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.3, socket_timeout=0.3
    )
    try:
        raw = await asyncio.wait_for(client.get(SETTINGS_REDIS_KEY), timeout=0.3)
    except Exception as exc:
        logger.warning("Legacy settings migration read failed (%s), using defaults", type(exc).__name__)
        return get_default_settings()
    finally:
        await client.aclose()
    if raw is None:
        return get_default_settings()
    try:
        return SystemSettings.model_validate(json.loads(raw))
    except Exception as exc:
        logger.error("Legacy settings document is invalid (%s)", type(exc).__name__)
        return get_default_settings()


async def _refresh_redis_cache(document: SystemSettings) -> None:
    """Keep legacy readers warm; a cache outage never changes the committed DB result."""
    if getattr(settings, "SEMAPHORE_BYPASS", False):
        return
    try:
        client = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.3, socket_timeout=0.3
        )
        try:
            await asyncio.wait_for(client.set(SETTINGS_REDIS_KEY, document.model_dump_json()), timeout=0.3)
        finally:
            await client.aclose()
    except Exception as exc:
        logger.warning("Settings Redis cache refresh failed (%s)", type(exc).__name__)


async def get_system_settings_async() -> SystemSettings:
    """Load the authoritative settings document from the database."""
    try:
        async with TaskAsyncSessionLocal() as session:
            row = await session.get(AutomationSetting, SETTINGS_DB_KEY)
            if row is not None:
                return _decode_row(row)
    except SettingsUnavailableError:
        raise
    except Exception as exc:
        logger.error("Durable settings read failed (%s)", type(exc).__name__)
        raise SettingsUnavailableError("Settings database is unavailable") from None

    # One-time migration, after the operator's existing Redis document has been
    # snapshotted. An unavailable Redis key is different from a missing key.
    initial = await _read_legacy_redis_document()
    initial.version = 1
    try:
        async with TaskAsyncSessionLocal() as session:
            row = AutomationSetting(
                key=SETTINGS_DB_KEY,
                value=_database_value(initial, 1),
                category="system",
            )
            session.add(row)
            session.add(SettingsAuditLog(
                key=SETTINGS_DB_KEY,
                old_value=None,
                new_value={"version": 1, "action": "legacy_migration"},
                updated_by="system:migration",
            ))
            await session.commit()
            return initial
    except IntegrityError:
        # Another process won the migration race; use its committed document.
        async with TaskAsyncSessionLocal() as session:
            row = await session.get(AutomationSetting, SETTINGS_DB_KEY)
            if row is not None:
                return _decode_row(row)
        raise SettingsUnavailableError("Settings migration could not be verified") from None
    except Exception as exc:
        logger.error("Durable settings migration failed (%s)", type(exc).__name__)
        raise SettingsUnavailableError("Settings migration failed") from None


_settings_cache: tuple[float, SystemSettings] | None = None


def get_system_settings_sync() -> SystemSettings:
    """Synchronous bridge for callers both inside and outside an event loop with 3s memory cache."""
    import time

    global _settings_cache
    now = time.monotonic()
    if _settings_cache is not None and (now - _settings_cache[0]) < 3.0:
        return _settings_cache[1]

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        res = asyncio.run(get_system_settings_async())
        _settings_cache = (now, res)
        return res
    with ThreadPoolExecutor(max_workers=1) as executor:
        res = executor.submit(lambda: asyncio.run(get_system_settings_async())).result()
        _settings_cache = (now, res)
        return res


async def save_system_settings_async(new_settings: SystemSettings) -> SystemSettings:
    """Commit a validated document atomically; reject stale revisions."""
    global _settings_cache
    _settings_cache = None
    from datetime import UTC, datetime

    from sqlalchemy import update

    # Validate again because callers can mutate a Pydantic model after creation.
    candidate = SystemSettings.model_validate(new_settings.model_dump())
    current = await get_system_settings_async()
    if candidate.version != current.version:
        raise SettingsConflictError("Settings changed since they were loaded")
    candidate.queue.max_concurrent_claims = candidate.automation.max_concurrent_claims
    candidate.automation.use_chrome_browser = candidate.automation.browser_engine == "chrome"
    next_version = current.version + 1
    candidate.version = next_version
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with TaskAsyncSessionLocal() as session:
                row = await session.get(AutomationSetting, SETTINGS_DB_KEY)
                if row is None:
                    raise SettingsUnavailableError("Settings database row is missing")
                result = await session.execute(
                    update(AutomationSetting)
                    .where(AutomationSetting.key == SETTINGS_DB_KEY)
                    .where(AutomationSetting.updated_at == row.updated_at)
                    .values(value=_database_value(candidate, next_version), updated_at=datetime.now(UTC))
                )
                if result.rowcount != 1:
                    raise SettingsConflictError("Settings changed during save")
                session.add(SettingsAuditLog(
                    key=SETTINGS_DB_KEY,
                    old_value={"version": current.version},
                    new_value={"version": next_version},
                    updated_by="settings-api",
                ))
                await session.commit()
                break
        except (SettingsConflictError, SettingsUnavailableError):
            raise
        except Exception as exc:
            is_locked = "locked" in str(exc).lower() or "busy" in str(exc).lower()
            if is_locked and attempt < max_retries - 1:
                backoff = 0.2 * (2 ** attempt)
                logger.warning(
                    "Settings save hit SQLite lock contention (attempt %d/%d), retrying in %.2fs...",
                    attempt + 1, max_retries, backoff
                )
                await asyncio.sleep(backoff)
                continue
            logger.error("Durable settings save failed (%s): %s", type(exc).__name__, exc, exc_info=True)
            raise SettingsUnavailableError("Settings database save failed") from None
    await _refresh_redis_cache(candidate)
    return candidate


async def reset_system_settings_async() -> SystemSettings:
    """Reset defaults through the same revision-safe database write path."""
    current = await get_system_settings_async()
    defaults = get_default_settings()
    defaults.version = current.version
    return await save_system_settings_async(defaults)


