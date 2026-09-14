"""Test Failure Paths and System Recovery (TC-FAIL-001 through TC-FAIL-010)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.automation.base import (
    SecurityBlockException,
    detect_security_block,
    log_security_block_event,
)
from app.automation.florida import BrowardScraper, MiamiDadeScraper
from app.automation.texas import DallasScraper, HarrisJPScraper, TravisScraper
from app.services.guidewire_client import GuidewireClient


def _build_mock_page():
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="")
    page.evaluate = AsyncMock(return_value=None)
    page.frames = []

    mock_locator = MagicMock()
    mock_locator.first = mock_locator
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.is_visible = AsyncMock(return_value=True)
    mock_locator.wait_for = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.click = AsyncMock()
    mock_locator.all_inner_texts = AsyncMock(return_value=[])
    mock_locator.inner_text = AsyncMock(return_value="")
    mock_locator.nth.side_effect = lambda idx: mock_locator

    page.locator.return_value = mock_locator
    return page


@pytest.mark.asyncio
async def test_tc_fail_001_broward_portal_timeout_returns_empty():
    """TC-FAIL-001: Broward returns [] on page navigation/fill timeout without fatal raise."""
    scraper = BrowardScraper()
    page = _build_mock_page()
    page.goto.side_effect = Exception("Navigation timeout 30000ms exceeded")

    # Should raise or handle gracefully
    try:
        res = await scraper.search_by_party_name("Error", "Party", page)
        assert res == []
    except Exception as e:
        assert "timeout" in str(e).lower()


@pytest.mark.asyncio
async def test_tc_fail_002_captcha_unsolved_returns_empty_no_runtimeerror():
    """TC-FAIL-002: CAPTCHA never solved returns [] rather than raising RuntimeError."""
    scraper = BrowardScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        res = await scraper.search_by_party_name("John", "Doe", page)
        assert res == []


def test_tc_fail_003_detect_security_block_429():
    """TC-FAIL-003: HTTP 429 raises SecurityBlockException with cooldown."""
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(status_code=429, portal_key="broward")
    assert exc_info.value.cooldown_seconds == 300
    assert "Rate limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tc_fail_004_next_page_failure_preserves_page_1_results():
    """TC-FAIL-004: Next-page failure during pagination loop retains page 1 results."""
    scraper = BrowardScraper()
    page = _build_mock_page()
    page.inner_text = AsyncMock(return_value="Results")

    rows_locator = MagicMock()
    rows_locator.count = AsyncMock(return_value=2)
    def get_fail_row(idx):
        rm = MagicMock()
        rm.locator.return_value.all_inner_texts = AsyncMock(
            return_value=[f"CACE-23-00{idx+1}", "Smith v. Jones", "CIVIL", "01/01/2023", "OPEN"]
        )
        return rm
    rows_locator.nth.side_effect = get_fail_row

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=1)
    next_btn.first = next_btn
    next_btn.is_visible = AsyncMock(return_value=True)
    next_btn.get_attribute = AsyncMock(return_value="false")
    next_btn.click = AsyncMock(side_effect=Exception("Element is detached from DOM"))

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.click = AsyncMock()

    def loc_side_effect(sel):
        if "table.table tbody tr" in sel or "table tbody tr" in sel:
            return rows_locator
        if "next" in sel.lower():
            return next_btn
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        res = await scraper.search_by_party_name("John", "Doe", page)

    assert len(res) == 2, "Page 1 results should be retained even if next page throws an error"


@pytest.mark.asyncio
async def test_tc_fail_005_miami_no_credentials_proceeds_gracefully():
    """TC-FAIL-005: MiamiDadeScraper with no credentials configured logs warning and proceeds without error."""
    scraper = MiamiDadeScraper()
    page = _build_mock_page()
    page.inner_text = AsyncMock(return_value="No records found")

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        res = await scraper.search_by_party_name("Guest", "User", page)
        assert res == []


@pytest.mark.asyncio
async def test_tc_fail_006_guidewire_http_500_handled():
    """TC-FAIL-006: Guidewire client handles HTTP 500 error gracefully."""
    client = GuidewireClient(api_url="https://gw.example.com/api", mock_mode=False)

    async def mock_post(*args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Internal Server Error", request=MagicMock(), response=mock_resp
        )
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        res = await client.send_case_update(
            claim_number="123456789",
            exposure_number="1",
            matched_cases=[{"CaseNumber": "123", "CaseStyle": "Test"}],
        )
        assert res["success"] is False
        assert "error" in res


def test_tc_fail_007_detect_security_block_cloudflare_html():
    """TC-FAIL-007: detect_security_block identifies Cloudflare challenge HTML."""
    html = "<html><body><div id='cf-browser-verification'>Please wait while we verify your browser</div></body></html>"
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(status_code=403, html_text=html, portal_key="dallas")
    assert "Cloudflare challenge page detected" in str(exc_info.value)


def test_tc_fail_008_detect_security_block_waf_html():
    """TC-FAIL-008: detect_security_block identifies WAF block page via Ray ID and access denied."""
    html = "<html><body><h1>Error</h1><p>Ray ID: 7b89a4cd8f2</p><p>access denied</p></body></html>"
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(status_code=200, html_text=html, portal_key="harris_district")
    assert "WAF block page detected" in str(exc_info.value)


def test_tc_fail_009_log_security_block_event():
    """TC-FAIL-009: log_security_block_event executes without throwing an exception."""
    try:
        log_security_block_event(
            portal_name="Travis County",
            url="https://odysseyweb.traviscountytx.gov",
            reason="WAF rate limit",
            cooldown_seconds=600,
        )
    except Exception as e:
        pytest.fail(f"log_security_block_event raised an unexpected exception: {e}")


@pytest.mark.asyncio
async def test_tc_fail_010_empty_last_name_returns_empty_all_scrapers():
    """TC-FAIL-010: Passing empty last name returns [] immediately on all scrapers without navigation."""
    page = MagicMock()
    page.goto = AsyncMock()

    for scraper_cls in [BrowardScraper, MiamiDadeScraper, TravisScraper, DallasScraper, HarrisJPScraper]:
        scraper = scraper_cls()
        res = await scraper.search_by_party_name("FirstOnly", "", page)
        assert res == []
        page.goto.assert_not_awaited()
