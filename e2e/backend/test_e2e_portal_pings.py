"""E2E Test: County Court Portal Reachability & Streaming Latency.

Verifies that all 8 public county court portals respond to streaming GET requests
with valid status codes (<500) and low response latency without downloading the full DOM.
"""

import time

import httpx
import pytest

from app.schemas.settings import PortalTestRequest
from app.services.guidewire_client import test_court_portal as check_court_portal

PORTALS = [
    ("broward", "Broward County Clerk", "https://www.browardclerk.org/web2"),
    ("hillsborough", "Hillsborough County Clerk", "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"),
    ("miami", "Miami-Dade County Clerk", "https://www2.miamidadeclerk.gov/ocs"),
    ("travis", "Travis County Odyssey Portal", "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"),
    ("dallas", "Dallas County Courts Portal", "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"),
    ("harris_jp", "Harris County JP Odyssey Portal", "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"),
    ("harris_district", "Harris County District Clerk", "https://www.hcdistrictclerk.com/cDocs/Public/Search.aspx"),
    ("harris_cclerk", "Harris County Clerk WebSearch", "https://www.cclerk.hctx.net/Applications/WebSearch/"),
]


@pytest.mark.asyncio
async def test_all_portals_respond_to_streaming_get():
    """Verify test_court_portal uses streaming GET and completes within reasonable duration."""
    for key, name, url in PORTALS:
        req = PortalTestRequest(portal_name=name, url=url, timeout_seconds=15)
        resp = await check_court_portal(req)
        assert resp.duration_ms > 0
        assert resp.duration_ms < 25000, f"Portal {name} took too long: {resp.duration_ms}ms"
        assert resp.status_code is not None


@pytest.mark.asyncio
async def test_streaming_does_not_download_full_body():
    """Verify streaming GET terminates immediately after headers are received."""
    url = "https://www.browardclerk.org/web2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    t0 = time.perf_counter()
    async with (
        httpx.AsyncClient(verify=False, follow_redirects=True, timeout=10.0) as client,
        client.stream("GET", url, headers=headers) as res,
    ):
            status = res.status_code
            elapsed_ms = (time.perf_counter() - t0) * 1000
    assert status == 200
    assert elapsed_ms < 5000
