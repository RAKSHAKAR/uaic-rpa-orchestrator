"""Unit tests for IMP-2026-0926-001:
- Browser engine parity (Google Chrome & Microsoft Edge vs. Chromium)
- Hillsborough down green search button retargeting
- Miami-Dade authentication and navbar Party Name selection
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import resolve_browser_launch_target
from app.automation.florida.hillsborough import HillsboroughScraper
from app.automation.florida.miami import MiamiDadeScraper


def test_resolve_browser_launch_target_permutations():
    """Verify that resolve_browser_launch_target correctly maps engine settings without defaulting to Chromium."""
    # 1. Chrome
    exe, channel = resolve_browser_launch_target("chrome")
    assert (exe is not None and "chrome" in exe.lower()) or channel == "chrome"

    # 2. Edge
    exe_edge, channel_edge = resolve_browser_launch_target("msedge")
    assert (exe_edge is not None and "msedge" in exe_edge.lower()) or channel_edge == "msedge"

    exe_edge2, channel_edge2 = resolve_browser_launch_target("edge")
    assert (exe_edge2 is not None and "msedge" in exe_edge2.lower()) or channel_edge2 == "msedge"

    # 3. Chromium (only when explicitly requested)
    exe_chrom, channel_chrom = resolve_browser_launch_target("chromium")
    assert exe_chrom is None
    assert channel_chrom is None


def test_explicit_missing_browser_binary_fails_instead_of_falling_back(tmp_path):
    with pytest.raises(FileNotFoundError, match="Configured browser executable"):
        resolve_browser_launch_target("chrome", chrome_binary_path=str(tmp_path / "missing.exe"))


@pytest.mark.skipif(sys.platform != "win32", reason="Windows Chrome enterprise policy")
def test_managed_chrome_with_extension_requires_explicit_engine_choice():
    with patch("winreg.OpenKey", return_value=MagicMock()):
        with pytest.raises(RuntimeError, match="choose Chromium in Settings"):
            resolve_browser_launch_target("chrome", has_extension=True)


@pytest.mark.asyncio
async def test_hillsborough_clicks_green_search_under_date_filed():
    """Verify HillsboroughScraper clicks the green submit button under Date Filed inside #nav-Party."""
    scraper = HillsboroughScraper()
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.reload = AsyncMock()
    mock_page.inner_text = AsyncMock(return_value="Case Search Party Name")
    mock_page.url = "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"

    clicked_selectors = []
    down_btn = MagicMock()
    down_btn.count = AsyncMock(return_value=1)
    down_btn.first = down_btn
    down_btn.is_visible = AsyncMock(return_value=True)

    async def mock_click(**kwargs):
        clicked_selectors.append("btnSubmitPartySearch")

    down_btn.click = mock_click

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()

    empty_msg = MagicMock()
    empty_msg.count = AsyncMock(return_value=1)
    empty_msg.first = empty_msg
    empty_msg.is_visible = AsyncMock(return_value=True)

    def loc_side_effect(sel):
        if "btnSubmitPartySearch" in sel or "btn-success" in sel:
            assert "button:has-text('Search')" not in sel, "Global button:has-text('Search') must not be present"
            return down_btn
        if "dataTables_empty" in sel:
            return empty_msg
        return mock_input

    mock_page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        await scraper.search_by_party_name("Alice", "Smith", mock_page)

    assert "btnSubmitPartySearch" in clicked_selectors


@pytest.mark.asyncio
async def test_miami_initiates_login_when_unauthenticated():
    """Verify MiamiDadeScraper initiates login sequence when not authenticated."""
    scraper = MiamiDadeScraper(
        username="apoorvnigam07@gmail.com",
        password="TestPassword123!",
        requires_login=True,
    )
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.keyboard.press = AsyncMock()
    mock_page.url = "https://www2.miamidadeclerk.gov/ocs"
    mock_page.goto = AsyncMock()

    mock_body = MagicMock()
    # Notice: Body has public welcome text that previously triggered false positive
    mock_body.inner_text = AsyncMock(return_value="Welcome to the Miami-Dade County Clerk and Comptroller Online Court Services")

    mock_login_link = MagicMock()
    mock_login_link.count = AsyncMock(return_value=1)
    mock_login_link.first = mock_login_link
    mock_login_link.is_visible = AsyncMock(return_value=True)
    mock_login_link.click = AsyncMock()

    mock_email = MagicMock()
    mock_email.count = AsyncMock(return_value=1)
    mock_email.first = mock_email
    mock_email.first.wait_for = AsyncMock()
    mock_email.first.fill = AsyncMock()
    mock_email.first.clear = AsyncMock()

    mock_pwd = MagicMock()
    mock_pwd.count = AsyncMock(return_value=1)
    mock_pwd.first = mock_pwd
    mock_pwd.first.fill = AsyncMock()
    mock_pwd.first.clear = AsyncMock()

    mock_submit = MagicMock()
    mock_submit.count = AsyncMock(return_value=1)
    mock_submit.first = mock_submit
    mock_submit.first.is_visible = AsyncMock(return_value=True)
    mock_submit.first.click = AsyncMock()

    def loc_side_effect(sel):
        if "Logout" in sel:
            none_loc = MagicMock()
            none_loc.count = AsyncMock(return_value=0)
            none_loc.first.is_visible = AsyncMock(return_value=False)
            return none_loc
        if "body" in sel:
            return mock_body
        if "btnLogin" in sel or "LOGIN" in sel or "submit" in sel:
            return mock_submit
        if "Register/Login" in sel or "Login" in sel:
            return mock_login_link
        if "userName" in sel or "UserName" in sel or "email" in sel:
            return mock_email
        if "password" in sel or "Password" in sel:
            return mock_pwd
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        return generic

    mock_page.locator.side_effect = loc_side_effect

    await scraper.ensure_authenticated(mock_page)

    # Login link was clicked, credentials filled, submit clicked
    mock_login_link.first.click.assert_called_once()
    mock_submit.first.click.assert_called_once()
    mock_page.keyboard.press.assert_called_with("Escape")


@pytest.mark.asyncio
async def test_miami_selects_party_name_from_navbar():
    """Verify MiamiDadeScraper always clicks 'Party Name' from navbar."""
    scraper = MiamiDadeScraper()
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    nav_party_link = MagicMock()
    nav_party_link.count = AsyncMock(return_value=1)
    nav_party_link.first = nav_party_link
    nav_party_link.is_visible = AsyncMock(return_value=True)
    nav_party_link.click = AsyncMock()

    last_input = MagicMock()
    last_input.count = AsyncMock(return_value=1)
    last_input.first = last_input
    last_input.wait_for = AsyncMock()

    def loc_side_effect(sel):
        if "Party Name" in sel:
            return nav_party_link
        if "txtLastName" in sel:
            return last_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        return generic

    mock_page.locator.side_effect = loc_side_effect

    await scraper.select_party_search_tab(mock_page)

    nav_party_link.first.click.assert_called_once()
