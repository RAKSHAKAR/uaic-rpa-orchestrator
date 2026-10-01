"""Isolated durable-settings contract checks; no shared database or Redis writes."""

import json

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.v1.endpoints import settings as settings_endpoint
from app.core.database import Base
from app.models.guidewire import AutomationSetting, SettingsAuditLog
from app.schemas.settings import (
    SettingsUpdateRequest,
    merge_settings_update,
    redact_system_settings,
)
from app.services import settings_service as service


class MemoryRedis:
    def __init__(self, legacy: dict | None = None, *, fail_set: bool = False):
        self.value = json.dumps(legacy) if legacy is not None else None
        self.fail_set = fail_set

    async def get(self, _key):
        return self.value

    async def set(self, _key, value):
        if self.fail_set:
            raise ConnectionError("cache unavailable")
        self.value = value

    async def aclose(self):
        pass


@pytest.fixture
async def isolated_settings(tmp_path, monkeypatch):
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path / 'settings.db'}", poolclass=NullPool
    )
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all,
            tables=[AutomationSetting.__table__, SettingsAuditLog.__table__],
        )
    monkeypatch.setattr(service, "TaskAsyncSessionLocal", async_sessionmaker(engine, expire_on_commit=False))
    cache = MemoryRedis()
    monkeypatch.setattr(service.aioredis, "from_url", lambda *_args, **_kwargs: cache)
    yield cache
    await engine.dispose()


@pytest.mark.asyncio
async def test_legacy_migration_and_db_authoritative_roundtrip(isolated_settings):
    legacy = service.get_default_settings()
    legacy.automation.captcha_wait_seconds = 77
    legacy.integration.guidewire_api_key = "unit-test-secret"
    isolated_settings.value = legacy.model_dump_json()

    migrated = await service.get_system_settings_async()
    assert migrated.version == 1
    assert migrated.automation.captcha_wait_seconds == 77

    migrated.automation.captcha_wait_seconds = 29
    saved = await service.save_system_settings_async(migrated)
    assert saved.version == 2
    isolated_settings.value = "{}"  # A stale or lost cache cannot override the DB.
    loaded = await service.get_system_settings_async()
    assert loaded.version == 2
    assert loaded.automation.captcha_wait_seconds == 29
    assert loaded.integration.guidewire_api_key == "unit-test-secret"


@pytest.mark.asyncio
async def test_secret_redaction_retention_explicit_clear_and_revision(isolated_settings):
    current = await service.get_system_settings_async()
    current.integration.guidewire_api_key = "unit-test-secret"
    current = await service.save_system_settings_async(current)

    public = redact_system_settings(current)
    assert public.integration.guidewire_api_key == ""
    assert public.configured_secrets["integration.guidewire_api_key"] is True
    assert "unit-test-secret" not in public.model_dump_json()

    request = SettingsUpdateRequest.model_validate(public.model_dump())
    request.automation.captcha_wait_seconds = 31
    retained = await service.save_system_settings_async(merge_settings_update(current, request))
    assert retained.integration.guidewire_api_key == "unit-test-secret"
    assert retained.automation.captcha_wait_seconds == 31

    with pytest.raises(service.SettingsConflictError):
        await service.save_system_settings_async(merge_settings_update(retained, request))

    clear = SettingsUpdateRequest.model_validate(redact_system_settings(retained).model_dump())
    clear.clear_secrets = ["integration.guidewire_api_key"]
    cleared = await service.save_system_settings_async(merge_settings_update(retained, clear))
    assert cleared.integration.guidewire_api_key == ""


@pytest.mark.asyncio
async def test_cache_failure_does_not_fake_db_failure(isolated_settings):
    current = await service.get_system_settings_async()
    isolated_settings.fail_set = True
    current.automation.captcha_wait_seconds = 42
    saved = await service.save_system_settings_async(current)
    assert saved.version == 2
    assert (await service.get_system_settings_async()).automation.captcha_wait_seconds == 42


@pytest.mark.asyncio
async def test_portal_and_fleet_settings_persist_with_masked_miami_password(isolated_settings):
    current = await service.get_system_settings_async()
    current.portals.miami_password = "unit-test-miami-password"
    current = await service.save_system_settings_async(current)
    public = redact_system_settings(current)
    assert public.portals.miami_password == ""

    request = SettingsUpdateRequest.model_validate(public.model_dump())
    request.portals.miami_url = "https://example.test/miami"
    request.portals.miami_enabled = False
    request.portals.miami_requires_login = False
    request.automation.browser_engine = "msedge"
    request.automation.max_concurrent_claims = 3
    saved = await service.save_system_settings_async(merge_settings_update(current, request))
    assert saved.portals.miami_password == "unit-test-miami-password"
    assert saved.portals.miami_url == "https://example.test/miami"
    assert not saved.portals.miami_enabled
    assert not saved.portals.miami_requires_login
    assert saved.automation.browser_engine == "msedge"
    assert not saved.automation.use_chrome_browser
    assert saved.queue.max_concurrent_claims == 3


@pytest.mark.asyncio
async def test_database_failure_cannot_return_success(isolated_settings, monkeypatch):
    current = await service.get_system_settings_async()

    def unavailable_session():
        raise RuntimeError("isolated database unavailable")

    monkeypatch.setattr(service, "TaskAsyncSessionLocal", unavailable_session)
    with pytest.raises(service.SettingsUnavailableError):
        await service.save_system_settings_async(current)


@pytest.mark.asyncio
async def test_api_masks_secrets_and_reports_stale_revision(isolated_settings, monkeypatch):
    monkeypatch.setattr(settings_endpoint, "record_audit_event_background", lambda **_kwargs: None)
    application = FastAPI()
    application.include_router(settings_endpoint.router, prefix="/api/v1/settings")
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://isolated-test"
    ) as client:
        initial = (await client.get("/api/v1/settings")).json()
        initial["integration"]["guidewire_api_key"] = "unit-test-secret"
        initial["automation"]["anticaptcha_api_key"] = "unit-test-anticaptcha-secret"
        save = await client.post("/api/v1/settings", json=initial)
        assert save.status_code == 200
        assert save.json()["integration"]["guidewire_api_key"] == ""
        assert save.json()["configured_secrets"]["integration.guidewire_api_key"] is True
        assert save.json()["automation"]["anticaptcha_api_key"] == ""
        assert save.json()["configured_secrets"]["automation.anticaptcha_api_key"] is True
        assert "unit-test-secret" not in save.text
        assert "unit-test-anticaptcha-secret" not in save.text

        retry = await client.post("/api/v1/settings", json=initial)
        assert retry.status_code == 409
        active = (await client.get("/api/v1/settings")).json()
        active["automation"]["captcha_wait_seconds"] = 45
        retained = await client.post("/api/v1/settings", json=active)
        assert retained.status_code == 200
        assert (await service.get_system_settings_async()).integration.guidewire_api_key == "unit-test-secret"
        assert (await service.get_system_settings_async()).automation.anticaptcha_api_key == "unit-test-anticaptcha-secret"

        def unavailable_session():
            raise RuntimeError("isolated database unavailable")

        monkeypatch.setattr(service, "TaskAsyncSessionLocal", unavailable_session)
        unavailable = await client.get("/api/v1/settings")
        assert unavailable.status_code == 503
        assert "unit-test-secret" not in unavailable.text


@pytest.mark.asyncio
async def test_api_rejects_change_to_fixed_v4_unique_name_threshold(isolated_settings):
    application = FastAPI()
    application.include_router(settings_endpoint.router, prefix="/api/v1/settings")
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://isolated-test"
    ) as client:
        current = (await client.get("/api/v1/settings")).json()
        current["matcher"]["unique_names_threshold"] = 0.75
        rejected = await client.post("/api/v1/settings", json=current)

    assert rejected.status_code == 422
    assert (await service.get_system_settings_async()).matcher.unique_names_threshold == 0.60


@pytest.mark.asyncio
async def test_branding_save_returns_committed_document(isolated_settings, monkeypatch):
    monkeypatch.setattr(settings_endpoint, "record_audit_event_background", lambda **_kwargs: None)
    application = FastAPI()
    application.include_router(settings_endpoint.router, prefix="/api/v1/settings")
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://isolated-test"
    ) as client:
        branding = (await client.get("/api/v1/settings/branding")).json()
        branding["app_title"] = "Unit Test Identity"
        response = await client.post("/api/v1/settings/branding", json=branding)
        assert response.status_code == 200
        assert response.json()["app_title"] == "Unit Test Identity"
        assert (await service.get_system_settings_async()).branding.app_title == "Unit Test Identity"


@pytest.mark.parametrize(
    ("section", "field", "invalid"),
    [
        ("automation", "browser_engine", "safari"),
        ("automation", "typing_speed_mode", "unknown"),
        ("integration", "notification_dispatch_mode", "discard"),
        ("email", "digest_mode", "weekly_digest"),
        ("email", "provider", "sendgrid"),
        ("email", "smtp_encryption", "insecure"),
        ("integration", "guidewire_auth_type", "Unknown"),
        ("storage", "storage_provider", "other"),
        ("matcher", "scorer_algorithm", "unknown"),
        ("portals", "broward_url", ""),
        ("portals", "dallas_url", "javascript:alert(1)"),
    ],
)
def test_enum_like_settings_reject_invalid_values(section, field, invalid):
    document = service.get_default_settings().model_dump()
    document[section][field] = invalid
    with pytest.raises(ValidationError):
        SettingsUpdateRequest.model_validate(document)


def test_enabled_proxy_requires_valid_host():
    document = service.get_default_settings().model_dump()
    document["proxy"]["enabled"] = True
    with pytest.raises(ValidationError):
        SettingsUpdateRequest.model_validate(document)
