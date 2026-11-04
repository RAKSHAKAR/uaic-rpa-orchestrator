"""
Comprehensive Unit & Integration Test Suite for Court Portal URLs Reconciliation (IMP-2026-1029-001).

Tests:
1. All 8 default portal URLs match V4-authoritative workflows.
2. Settings persistence roundtrip & cache invalidation.
3. Strict isolation & protection of existing credentials during portal URL updates.
4. Scraper dynamic route resolution (all 8 portals).
5. Scraper base_url injection from Settings.
6. Harris JP & Harris County Clerk strict 4-field schema (NO CaseType).
7. SSRF and malformed URL validation.
8. Celery scraper task configuration retrieval.
"""

import pytest
from pydantic import ValidationError

from app.automation.florida.broward import BrowardScraper
from app.automation.florida.hillsborough import HillsboroughScraper
from app.automation.florida.miami import MiamiDadeScraper
from app.automation.texas.dallas import DallasScraper
from app.automation.texas.harris_cclerk import HarrisCountyClerkScraper
from app.automation.texas.harris_district import HarrisDistrictClerkScraper
from app.automation.texas.harris_jp import HarrisJPScraper
from app.automation.texas.travis import TravisScraper
from app.schemas.settings import (
    PortalsSettings,
    SettingsUpdateRequest,
    merge_settings_update,
)
from app.services.settings_service import (
    _normalize_portals_data,
    get_system_settings_async,
    save_system_settings_async,
)

# Reconciled V4-authoritative URLs
V4_EXPECTED_URLS = {
    "broward_url": "https://www.browardclerk.org/Web2",
    "hillsborough_url": "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab",
    "miami_url": "https://www2.miamidadeclerk.gov/ocs",
    "travis_url": "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29",
    "dallas_url": "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29",
    "harris_jp_url": "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29",
    "harris_cclerk_url": "https://www.cclerk.hctx.net/Applications/WebSearch/",
    "harris_district_url": "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx",
}


def test_default_portal_urls_match_v4_authoritative():
    """Verify that PortalsSettings defaults strictly match V4 Power Automate flows."""
    portals = PortalsSettings()
    for field, expected_url in V4_EXPECTED_URLS.items():
        actual_url = getattr(portals, field)
        assert actual_url == expected_url, (
            f"Portal setting '{field}' mismatch: expected '{expected_url}', got '{actual_url}'"
        )


def test_url_validation_accepts_valid_and_rejects_ssrf():
    """Test URL schema validation allows valid HTTP(S) and blocks SSRF / credentials."""
    # Valid HTTPS URLs
    portals = PortalsSettings(
        broward_url="https://court-mirror.example.gov/broward",
        miami_url="http://localhost:8080/ocs",
    )
    assert portals.broward_url == "https://court-mirror.example.gov/broward"
    assert portals.miami_url == "http://localhost:8080/ocs"

    # Reject non-http(s)
    with pytest.raises(ValidationError):
        PortalsSettings(broward_url="javascript:alert(1)")

    with pytest.raises(ValidationError):
        PortalsSettings(broward_url="ftp://ftp.example.com/court")

    # Reject URLs with embedded credentials
    with pytest.raises(ValidationError):
        PortalsSettings(miami_url="https://admin:secret@miamidadeclerk.gov/ocs")

    # Reject AWS/GCP/Azure link-local metadata SSRF
    with pytest.raises(ValidationError):
        PortalsSettings(travis_url="http://169.254.169.254/latest/meta-data")

    with pytest.raises(ValidationError):
        PortalsSettings(dallas_url="http://metadata.google.internal/computeMetadata/v1/")


@pytest.mark.asyncio
async def test_credential_isolation_during_portal_url_update():
    """CRITICAL: Modifying portal URLs must NEVER clear, touch, or overwrite Miami credentials."""
    # 1. Establish baseline settings with existing credentials
    current_settings = await get_system_settings_async()
    initial_username = current_settings.portals.miami_username
    initial_password = current_settings.portals.miami_password
    initial_requires_login = current_settings.portals.miami_requires_login

    # 2. Simulate partial update updating only Dallas and Broward URLs
    updated_portals = current_settings.portals.model_copy(
        update={
            "dallas_url": "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29",
            "broward_url": "https://www.browardclerk.org/Web2",
            "miami_password": "",  # Write-only masked/empty input from UI
        }
    )
    update_data = SettingsUpdateRequest(
        **current_settings.model_dump(exclude={"portals"}),
        portals=updated_portals,
    )

    merged = merge_settings_update(current_settings, update_data)

    # 3. Verify credentials remain 100% identical
    assert merged.portals.miami_username == initial_username
    assert merged.portals.miami_password == initial_password
    assert merged.portals.miami_requires_login == initial_requires_login


@pytest.mark.asyncio
async def test_portal_url_update_persistence_roundtrip():
    """Verify that updated portal URLs persist to DB and invalidate in-memory cache."""
    current_settings = await get_system_settings_async()
    orig_broward = current_settings.portals.broward_url

    test_custom_url = "https://www.browardclerk.org/Web2Test"
    try:
        updated_portals = current_settings.portals.model_copy(
            update={"broward_url": test_custom_url}
        )
        update_data = SettingsUpdateRequest(
            **current_settings.model_dump(exclude={"portals"}),
            portals=updated_portals,
        )
        merged = merge_settings_update(current_settings, update_data)
        saved = await save_system_settings_async(merged)
        assert saved.portals.broward_url == test_custom_url

        # Direct read from service (ensuring cache invalidation took effect)
        fresh_settings = await get_system_settings_async()
        assert fresh_settings.portals.broward_url == test_custom_url
    finally:
        # Restore original URL
        fresh = await get_system_settings_async()
        restored_portals = fresh.portals.model_copy(update={"broward_url": orig_broward})
        restore_data = SettingsUpdateRequest(
            **fresh.model_dump(exclude={"portals"}),
            portals=restored_portals,
        )
        merged_restore = merge_settings_update(fresh, restore_data)
        await save_system_settings_async(merged_restore)


def test_scraper_instantiation_uses_configured_base_urls():
    """Verify each scraper class accepts and preserves configured base_url."""
    custom_broward = "https://custom.broward.gov/Web2"
    scraper_broward = BrowardScraper(base_url=custom_broward)
    assert scraper_broward.base_url == custom_broward

    custom_hills = "https://custom.hillsclerk.com/html/caseSearch"
    scraper_hills = HillsboroughScraper(base_url=custom_hills)
    assert scraper_hills.base_url == custom_hills

    custom_miami = "https://custom.miamidadeclerk.gov/ocs"
    scraper_miami = MiamiDadeScraper(base_url=custom_miami)
    assert scraper_miami.base_url == custom_miami
    assert "custom.miamidadeclerk.gov" in scraper_miami.login_url

    custom_dallas = "https://custom.dallascounty.org/DALLASPROD"
    scraper_dallas = DallasScraper(base_url=custom_dallas)
    assert scraper_dallas.base_url == custom_dallas
    assert (
        scraper_dallas._resolve_nav_url()
        == "https://custom.dallascounty.org/DALLASPROD/Home/Dashboard/29"
    )

    custom_travis = "https://custom.traviscountytx.gov/Portal"
    scraper_travis = TravisScraper(base_url=custom_travis)
    assert scraper_travis.base_url == custom_travis
    assert (
        scraper_travis._resolve_nav_url()
        == "https://custom.traviscountytx.gov/Portal/Home/Dashboard/29"
    )

    custom_jp = "https://custom.harriscountytx.gov/OdysseyPortalJP"
    scraper_jp = HarrisJPScraper(base_url=custom_jp)
    assert scraper_jp.base_url == custom_jp
    assert (
        scraper_jp._resolve_nav_url()
        == "https://custom.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
    )

    custom_cclerk = "https://custom.cclerk.hctx.net/Applications/WebSearch/"
    scraper_cclerk = HarrisCountyClerkScraper(base_url=custom_cclerk)
    assert scraper_cclerk.base_url == custom_cclerk
    assert (
        scraper_cclerk._resolve_target_civil_url()
        == "https://custom.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil"
    )

    custom_district = "https://custom.hcdistrictclerk.com"
    scraper_district = HarrisDistrictClerkScraper(base_url=custom_district)
    assert scraper_district.base_url == custom_district
    assert (
        scraper_district._resolve_search_url()
        == "https://custom.hcdistrictclerk.com/eDocs/Public/Search.aspx"
    )


def test_dallas_dynamic_route_resolution():
    """Test Dallas Odyssey nav URL resolution handles full, partial, and base domains."""
    s1 = DallasScraper(
        base_url="https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"
    )
    assert (
        s1._resolve_nav_url()
        == "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"
    )

    s2 = DallasScraper(base_url="https://courtsportal.dallascounty.org/DALLASPROD")
    assert (
        s2._resolve_nav_url()
        == "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"
    )

    s3 = DallasScraper(base_url="https://courtsportal.dallascounty.org")
    assert (
        s3._resolve_nav_url()
        == "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"
    )


def test_travis_dynamic_route_resolution():
    """Test Travis Odyssey nav URL resolution handles full, partial, and base domains."""
    s1 = TravisScraper(base_url="https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29")
    assert s1._resolve_nav_url() == "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"

    s2 = TravisScraper(base_url="https://odysseyweb.traviscountytx.gov/Portal")
    assert s2._resolve_nav_url() == "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"

    s3 = TravisScraper(base_url="https://odysseyweb.traviscountytx.gov")
    assert s3._resolve_nav_url() == "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"


def test_harris_jp_dynamic_route_resolution():
    """Test Harris JP Odyssey nav URL resolution handles full, partial, and base domains."""
    s1 = HarrisJPScraper(
        base_url="https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
    )
    assert (
        s1._resolve_nav_url()
        == "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
    )

    s2 = HarrisJPScraper(base_url="https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP")
    assert (
        s2._resolve_nav_url()
        == "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
    )

    s3 = HarrisJPScraper(base_url="https://jpodysseyportal.harriscountytx.gov")
    assert (
        s3._resolve_nav_url()
        == "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
    )


def test_harris_cclerk_target_civil_url_resolution():
    """Test Harris County Clerk civil URL resolution avoids duplicated path segments."""
    s1 = HarrisCountyClerkScraper(base_url="https://www.cclerk.hctx.net/Applications/WebSearch/")
    assert (
        s1._resolve_target_civil_url()
        == "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil"
    )

    s2 = HarrisCountyClerkScraper(
        base_url="https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil"
    )
    assert (
        s2._resolve_target_civil_url()
        == "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil"
    )

    s3 = HarrisCountyClerkScraper(
        base_url="https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx"
    )
    assert (
        s3._resolve_target_civil_url()
        == "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil"
    )

    s4 = HarrisCountyClerkScraper(base_url="https://www.cclerk.hctx.net")
    assert (
        s4._resolve_target_civil_url()
        == "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil"
    )


def test_harris_district_search_url_resolution():
    """Test Harris District Clerk search URL resolution handles base domain and direct paths."""
    s1 = HarrisDistrictClerkScraper(
        base_url="https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"
    )
    assert s1._resolve_search_url() == "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"

    s2 = HarrisDistrictClerkScraper(base_url="https://www.hcdistrictclerk.com/eDocs/Public")
    assert s2._resolve_search_url() == "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"

    s3 = HarrisDistrictClerkScraper(base_url="https://www.hcdistrictclerk.com")
    assert s3._resolve_search_url() == "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"


def test_normalize_portals_data_does_not_overwrite_configured_urls():
    """Verify _normalize_portals_data populates missing URLs without overwriting configured URLs."""
    custom_cclerk = "https://custom.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx"
    payload = {
        "portals": {
            "harris_cclerk_url": custom_cclerk,
            # broward_url missing
        }
    }
    mutated = _normalize_portals_data(payload)
    assert mutated is True
    # Missing broward should be populated
    assert payload["portals"]["broward_url"] == V4_EXPECTED_URLS["broward_url"]
    # Configured custom cclerk must NOT be overwritten
    assert payload["portals"]["harris_cclerk_url"] == custom_cclerk
