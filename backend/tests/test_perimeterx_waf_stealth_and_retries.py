"""Tests for PerimeterX WAF Stealth Evasion, Bézier Human Movements, and Lockout Retries.

Verifies:
1. PerimeterX / HUMAN Security bot challenge detection in detect_security_block.
2. Universal stealth cloaking payload and launch flags in browser_manager.
3. Human Bézier curve trajectory calculation and micro-jitter cursor movement.
4. Human page warmup micro-scrolling on portal landing.
5. Cooldown tracking and Celery automated countdown retry dispatch.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.base import (
    BaseCourtScraper,
    SecurityBlockException,
    detect_security_block,
)
from app.automation.browser_manager import (
    STEALTH_JS_PAYLOAD,
    ChromeSession,
)
from app.services.cooldown_service import (
    clear_all_portal_cooldowns,
    is_portal_in_cooldown,
    set_portal_cooldown,
)


def test_detect_security_block_perimeterx_signature():
    """Verify detect_security_block identifies PerimeterX challenge HTML."""
    perimeterx_html = """
    <html>
        <head><title>Access Denied</title></head>
        <body>
            <h1>Access to this page has been denied because we believe you are using automation tools to browse the website.</h1>
            <p>Powered by PerimeterX, Inc.</p>
            <div id="px-captcha"></div>
        </body>
    </html>
    """
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(status_code=200, html_text=perimeterx_html, portal_key="hillsborough")

    assert "PerimeterX" in exc_info.value.message
    assert exc_info.value.cooldown_seconds == 300
    assert exc_info.value.portal_key == "hillsborough"


def test_detect_security_block_datadome_and_turnstile():
    """Verify detect_security_block catches DataDome and Cloudflare Turnstile challenges."""
    datadome_html = "<html><body><p>Protected by DataDome. Verification required.</p></body></html>"
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(status_code=403, html_text=datadome_html, portal_key="miami")
    assert "DataDome" in exc_info.value.message

    turnstile_html = "<html><body><div id='cf-turnstile' src='https://challenges.cloudflare.com/turnstile'></div></body></html>"
    with pytest.raises(SecurityBlockException) as exc_info_cf:
        detect_security_block(status_code=200, html_text=turnstile_html, portal_key="broward")
    assert "Cloudflare Turnstile" in exc_info_cf.value.message


class DummyScraper(BaseCourtScraper):
    async def search_by_party_name(self, party_name: str, page: Any, **kwargs):
        return []


@pytest.mark.asyncio
async def test_base_court_scraper_detect_security_block_perimeterx():
    """Verify BaseCourtScraper.detect_security_block identifies PerimeterX in live page body."""
    scraper = DummyScraper(
        county_name="Hillsborough County (FL)", base_url="https://hover.hillsclerk.com/"
    )
    mock_page = MagicMock()
    mock_page.url = "https://hover.hillsclerk.com/html/case/caseSearch.html"
    mock_page.title = AsyncMock(return_value="Access Denied")
    mock_page.evaluate = AsyncMock(
        return_value="Access to this page has been denied because we believe you are using automation tools to browse the website. Powered by PerimeterX, Inc."
    )

    is_blocked, reason, cooldown = await scraper.detect_security_block(mock_page)
    assert is_blocked is True
    assert "PerimeterX" in reason
    assert cooldown == 300


def test_stealth_js_payload_structure():
    """Verify STEALTH_JS_PAYLOAD contains required anti-detection overrides."""
    assert "navigator" in STEALTH_JS_PAYLOAD
    assert "webdriver" in STEALTH_JS_PAYLOAD
    assert "window.chrome" in STEALTH_JS_PAYLOAD
    assert "plugins" in STEALTH_JS_PAYLOAD
    assert "languages" in STEALTH_JS_PAYLOAD
    assert "permissions.query" in STEALTH_JS_PAYLOAD


@pytest.mark.asyncio
async def test_chrome_session_apply_stealth_scripts():
    """Verify ChromeSession._apply_stealth_scripts calls add_init_script on context."""
    mock_context = MagicMock()
    mock_context.add_init_script = AsyncMock()

    await ChromeSession._apply_stealth_scripts(mock_context)
    mock_context.add_init_script.assert_called_once_with(STEALTH_JS_PAYLOAD)


@pytest.mark.asyncio
async def test_base_court_scraper_human_bezier_move():
    """Verify human_bezier_move computes trajectory and updates cursor coordinates."""
    scraper = DummyScraper(county_name="Broward County", base_url="https://www.browardclerk.org/")
    mock_page = MagicMock()
    mock_mouse = MagicMock()
    mock_mouse.move = AsyncMock()
    mock_page.mouse = mock_mouse

    scraper._cursor_x = 100.0
    scraper._cursor_y = 100.0

    await scraper.human_bezier_move(mock_page, 450.0, 350.0)

    assert mock_mouse.move.call_count >= 10
    assert scraper._cursor_x == 450.0
    assert scraper._cursor_y == 350.0


@pytest.mark.asyncio
async def test_base_court_scraper_human_page_warmup():
    """Verify human_page_warmup dispatches realistic micro-scrolls."""
    scraper = DummyScraper(
        county_name="Hillsborough County (FL)", base_url="https://hover.hillsclerk.com/"
    )
    mock_page = MagicMock()
    mock_mouse = MagicMock()
    mock_mouse.wheel = AsyncMock()
    mock_page.mouse = mock_mouse
    mock_page.wait_for_timeout = AsyncMock()

    await scraper.human_page_warmup(mock_page)

    assert mock_mouse.wheel.call_count == 2


def test_cooldown_tracking_lifecycle():
    """Verify setting and checking portal cooldown status."""
    clear_all_portal_cooldowns()
    portal = "hillsborough"

    in_cool, remaining, reason = is_portal_in_cooldown(portal)
    assert in_cool is False

    set_portal_cooldown(portal, seconds=120, reason="PerimeterX WAF Lockout")

    in_cool2, remaining2, reason2 = is_portal_in_cooldown(portal)
    assert in_cool2 is True
    assert remaining2 > 0
    assert "PerimeterX" in reason2

    clear_all_portal_cooldowns()


@pytest.mark.asyncio
async def test_hillsborough_navigate_to_search_raises_security_block_on_perimeterx():
    """Verify HillsboroughScraper.navigate_to_search raises SecurityBlockException when blocked on landing."""
    from app.automation.florida.hillsborough import HillsboroughScraper

    scraper = HillsboroughScraper()
    mock_page = MagicMock()
    mock_page.url = "https://hover.hillsclerk.com/"
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.inner_text = AsyncMock(
        return_value="Access to this page has been denied because we believe you are using automation tools to browse the website. Powered by PerimeterX, Inc."
    )
    mock_page.title = AsyncMock(return_value="Access Denied")
    mock_page.evaluate = AsyncMock(
        return_value="Access to this page has been denied because we believe you are using automation tools to browse the website. Powered by PerimeterX, Inc."
    )

    with pytest.raises(SecurityBlockException) as exc_info:
        await scraper.navigate_to_search(mock_page)

    assert "PerimeterX" in exc_info.value.message
    assert exc_info.value.cooldown_seconds == 300
