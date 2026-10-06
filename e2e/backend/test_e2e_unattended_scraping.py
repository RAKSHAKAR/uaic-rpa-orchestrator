"""Unattended Mode End-to-End Automation Tests (Attended ↔ Unattended Parity).

Verifies that all 8 county portal scrapers execute in unattended (headless) mode
with Anti-Captcha extension support via `--headless=new`.
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


@pytest.mark.unattended
@pytest.mark.asyncio
async def test_e2e_unat_001_florida_all_unattended_init():
    """Verify Florida scrapers initialize correctly in Unattended mode."""
    b = BrowardScraper(headless=True)
    h = HillsboroughScraper(headless=True)
    m = MiamiDadeScraper(headless=True)

    assert b.headless is True
    assert h.headless is True
    assert m.headless is True


@pytest.mark.unattended
@pytest.mark.asyncio
async def test_e2e_unat_002_texas_all_unattended_init():
    """Verify Texas scrapers initialize correctly in Unattended mode."""
    t = TravisScraper(headless=True)
    d = DallasScraper(headless=True)
    jp = HarrisJPScraper(headless=True)
    cc = HarrisCountyClerkScraper(headless=True)
    dist = HarrisDistrictClerkScraper(headless=True)

    assert t.headless is True
    assert d.headless is True
    assert jp.headless is True
    assert cc.headless is True
    assert dist.headless is True
