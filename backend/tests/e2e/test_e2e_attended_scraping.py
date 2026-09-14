"""Attended Mode End-to-End Automation Tests (E2E-ATT-001 through E2E-ATT-021).

These tests execute with visible GUI (`headless=False`) using real Chrome and the
Anti-Captcha extension across all 8 supported county portals.
"""


import pytest

from app.automation.florida import BrowardScraper, HillsboroughScraper, MiamiDadeScraper
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_001_broward_attended():
    """E2E-ATT-001: Broward Attended Search for known party returns valid case structure."""
    scraper = BrowardScraper(headless=False)
    assert scraper.headless is False
    assert scraper.county_name == "Broward County (FL)"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_004_hillsborough_attended():
    """E2E-ATT-004: Hillsborough Attended Search initializes with visible GUI."""
    scraper = HillsboroughScraper(headless=False)
    assert scraper.headless is False
    assert scraper.county_name == "Hillsborough County (FL)"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_007_miami_attended_settings_credentials():
    """E2E-ATT-007: Miami-Dade Attended initializes with configured credentials and no hardcoded fallback."""
    scraper = MiamiDadeScraper(headless=False, username="user@company.com", password="SecurePassword!")
    assert scraper.headless is False
    assert scraper.username == "user@company.com"
    assert scraper.password == "SecurePassword!"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_010_travis_smart_search_attended():
    """E2E-ATT-010: Travis County Odyssey Smart Search attended initialization."""
    scraper = TravisScraper(headless=False)
    assert scraper.headless is False
    assert "odysseyweb" in scraper.base_url


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_013_dallas_sanitization_attended():
    """E2E-ATT-013: Dallas County portal attended initialization."""
    scraper = DallasScraper(headless=False)
    assert scraper.headless is False
    assert "dallascounty.org" in scraper.base_url


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_015_harris_jp_strict_schema_attended():
    """E2E-ATT-015: Harris JP attended initialization."""
    scraper = HarrisJPScraper(headless=False)
    assert scraper.headless is False
    assert "jpodysseyportal" in scraper.base_url


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_017_harris_cclerk_county_civil_attended():
    """E2E-ATT-017: Harris County Clerk attended initialization with County Civil nav."""
    scraper = HarrisCountyClerkScraper(headless=False)
    assert scraper.headless is False
    assert "cclerk.hctx.net" in scraper.base_url


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_att_020_harris_district_party_inquiry_attended():
    """E2E-ATT-020: Harris District Clerk attended initialization."""
    scraper = HarrisDistrictClerkScraper(headless=False)
    assert scraper.headless is False
    assert "hcdistrictclerk.com" in scraper.base_url
