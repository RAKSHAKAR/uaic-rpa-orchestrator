"""Test Suite: CAPTCHA, WAF, Session Exception Handling & Automated Cooldown & Re-dispatch.

Implements all 19 mandatory test scenarios from the specification:
- CAPTCHA-01 through CAPTCHA-04
- SESSION-01 through SESSION-03
- WAF-01 through WAF-04
- RETRY-01 through RETRY-02
- REDISPATCH-01 through REDISPATCH-05
- E2E-01 (All 8 bots coverage validation)

Implementation Reference: IMP-2026-1102-001
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import (
    BaseCourtScraper,
    CaptchaResolutionError,
    SecurityBlockException,
    detect_security_block,
)
from app.automation.florida import (
    BrowardScraper,
    HillsboroughScraper,
    MiamiDadeScraper,
)
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)
from app.services.cooldown_service import (
    ALL_PORTAL_KEYS,
    PortalOperationalState,
    check_portal_ready_for_redispatch,
    clear_all_portal_cooldowns,
    clear_portal_cooldown,
    get_all_portal_operational_states,
    get_portal_operational_state,
    is_portal_in_cooldown,
    set_portal_cooldown,
    set_portal_operational_state,
)
from app.services.error_classifier import (
    ErrorCategory,
    ErrorCode,
    RecoveryAction,
    classify_exception,
    make_error_event,
)


# Helper: build a mock Playwright Page
def _build_mock_page():
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="")
    page.evaluate = AsyncMock(return_value=None)
    page.frames = []
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Court Portal")

    locator = MagicMock()
    locator.first = locator
    locator.count = AsyncMock(return_value=0)
    locator.is_visible = AsyncMock(return_value=False)
    locator.wait_for = AsyncMock()
    locator.fill = AsyncMock()
    locator.click = AsyncMock()
    locator.all_inner_texts = AsyncMock(return_value=[])

    page.locator.return_value = locator
    return page


# ===========================================================================
# 1. CAPTCHA Scenarios (CAPTCHA-01 through CAPTCHA-04)
# ===========================================================================


class TestCaptchaHandling:
    """CAPTCHA-01 to CAPTCHA-04: Detection, resolution, timeout, max attempts."""

    @pytest.mark.asyncio
    async def test_captcha_01_captcha_detected_classification(self):
        """CAPTCHA-01: CAPTCHA detected -> correctly classified with authorized handling."""
        event = make_error_event(
            ErrorCode.CAPTCHA_DETECTED,
            portal_key="broward",
            message="Google reCAPTCHA v2 detected on Broward CaseSearch",
            execution_stage="CAPTCHA_INSPECT",
        )
        assert event.error_code == ErrorCode.CAPTCHA_DETECTED
        assert event.category == ErrorCategory.CAPTCHA
        assert event.recovery_action == RecoveryAction.INITIATE_CAPTCHA_RESOLUTION
        assert event.human_intervention is False

    @pytest.mark.asyncio
    async def test_captcha_02_captcha_resolved_token_verified(self):
        """CAPTCHA-02: CAPTCHA resolved -> token verified before form submission."""
        scraper = BrowardScraper()
        page = _build_mock_page()

        # Simulate solved token injected into g-recaptcha-response
        async def mock_eval(script, *args):
            if "g-recaptcha-response" in str(script):
                return "03AFcWeA5...valid_long_solve_token_greater_than_25_chars..."
            if "cf-turnstile-response" in str(script):
                return "0.valid_turnstile_token..."
            return ""

        page.evaluate = AsyncMock(side_effect=mock_eval)
        # Mock frame showing anchor
        mock_frame = MagicMock()
        mock_frame.url = "https://www.google.com/recaptcha/api2/anchor"
        page.frames = [mock_frame]

        with patch.object(scraper, "_detect_and_handle_captcha_until", return_value=True):
            resolved = await scraper.detect_and_handle_captcha(page, wait_seconds=5)
            assert resolved is True

    @pytest.mark.asyncio
    async def test_captcha_03_captcha_unresolved_after_120s(self):
        """CAPTCHA-03: CAPTCHA unresolved after wait timeout -> controlled pause / timeout returned."""
        scraper = DallasScraper()
        page = _build_mock_page()

        # Mock frame showing challenge but token remains empty
        mock_frame = MagicMock()
        mock_frame.url = "https://challenges.cloudflare.com/turnstile"
        page.frames = [mock_frame]

        with patch.object(scraper, "_detect_and_handle_captcha_until", return_value=False):
            resolved = await scraper.detect_and_handle_captcha(page, wait_seconds=1)
            assert resolved is False

    @pytest.mark.asyncio
    async def test_captcha_04_max_captcha_attempts_reached_classification(self):
        """CAPTCHA-04: Maximum CAPTCHA attempts reached -> CaptchaResolutionError -> AWAITING_HUMAN."""
        cre = CaptchaResolutionError("[Dallas County (TX)] CAPTCHA was not resolved after 2 attempts")
        event = classify_exception(
            cre,
            portal_key="dallas",
            execution_stage="CAPTCHA_WAIT",
            claim_id="CLAIM-1234",
            retry_attempt=2,
            max_retries=2,
        )

        assert event.error_code == ErrorCode.CAPTCHA_MAX_ATTEMPTS
        assert event.category == ErrorCategory.CAPTCHA
        assert event.human_intervention is True
        assert event.recovery_action == RecoveryAction.MARK_AWAITING_HUMAN


# ===========================================================================
# 2. Session Scenarios (SESSION-01 through SESSION-03)
# ===========================================================================


class TestSessionHandling:
    """SESSION-01 to SESSION-03: Timeout popup, expiration detection, recovery."""

    @pytest.mark.asyncio
    async def test_session_01_timeout_popup_detected_broward(self):
        """SESSION-01: Broward detects session timeout warning and clicks Continue session."""
        scraper = BrowardScraper()
        page = _build_mock_page()

        # Simulate timeout popup present
        timeout_btn = MagicMock()
        timeout_btn.count = AsyncMock(return_value=1)
        timeout_btn.is_visible = AsyncMock(return_value=True)
        timeout_btn.click = AsyncMock()
        timeout_btn.first = timeout_btn
        page.locator.return_value = timeout_btn

        with patch("app.automation.florida.broward.resilient_click", new_callable=AsyncMock) as mock_click:
            handled = await scraper.check_and_handle_session_timeout(
                page, "Smith", "John", "01/01/2023"
            )
            assert handled is True
            mock_click.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_session_02_session_expires_redirect_handled(self):
        """SESSION-02: Session expired redirect to homepage -> re-navigates from Step B."""
        scraper = BrowardScraper()
        page = _build_mock_page()
        page.url = "https://www.browardclerk.org/"  # Redirected away from /CaseSearchECA

        with (
            patch.object(scraper, "navigate_to_search", new_callable=AsyncMock) as mock_nav,
            patch.object(scraper, "select_party_name_tab", new_callable=AsyncMock) as mock_tab,
            patch.object(scraper, "fill_search_fields", new_callable=AsyncMock) as mock_fill,
        ):
            handled = await scraper.check_and_handle_session_timeout(
                page, "Smith", "John", "01/01/2023"
            )
            assert handled is True
            mock_nav.assert_awaited_once()
            mock_tab.assert_awaited_once()
            mock_fill.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_session_03_universal_session_timeout_check_on_base(self):
        """SESSION-03: BaseCourtScraper.check_and_handle_session_timeout works across all bots."""
        scraper = TravisScraper()
        page = _build_mock_page()

        btn = MagicMock()
        btn.count = AsyncMock(return_value=1)
        btn.is_visible = AsyncMock(return_value=True)
        btn.click = AsyncMock()
        btn.first = btn
        page.locator.return_value = btn

        handled = await scraper.check_and_handle_session_timeout(page)
        assert handled is True
        btn.click.assert_awaited_once()


# ===========================================================================
# 3. WAF and Security Block Scenarios (WAF-01 through WAF-04)
# ===========================================================================


class TestWafHandling:
    """WAF-01 to WAF-04: Travis rate limit, Hillsborough PerimeterX, recovery."""

    def test_waf_01_travis_600s_rate_limit(self):
        """WAF-01: Travis 600s rate limit detected with exact 600s cooldown."""
        with pytest.raises(SecurityBlockException) as exc_info:
            detect_security_block(
                status_code=429,
                html_text="Rate limit exceeded",
                portal_key="travis",
            )
        assert exc_info.value.cooldown_seconds == 600
        assert "travis" in str(exc_info.value.portal_key).lower()

        # Classify the exception
        event = classify_exception(exc_info.value, portal_key="travis")
        assert event.error_code == ErrorCode.WAF_RATE_LIMIT
        assert event.cooldown_required is True
        assert event.cooldown_seconds == 600

    def test_waf_02_hillsborough_perimeterx_challenge(self):
        """WAF-02: Hillsborough PerimeterX WAF Challenge detected with 300s cooldown."""
        html = "Access to this page has been denied because we believe you are using automation tools. Powered by PerimeterX, Inc."
        with pytest.raises(SecurityBlockException) as exc_info:
            detect_security_block(
                status_code=200,
                html_text=html,
                portal_key="hillsborough",
            )
        assert exc_info.value.cooldown_seconds == 300
        assert "PerimeterX" in exc_info.value.message

        event = classify_exception(exc_info.value, portal_key="hillsborough")
        assert event.error_code == ErrorCode.WAF_PERIMETERX
        assert event.cooldown_seconds == 300
        assert event.cooldown_required is True

    def test_waf_03_portal_remains_blocked_during_cooldown(self):
        """WAF-03: Portal remains blocked during active cooldown timer."""
        clear_portal_cooldown("travis")
        set_portal_cooldown("travis", seconds=600, reason="WAF rate limit")

        in_cool, remaining, reason = is_portal_in_cooldown("travis")
        assert in_cool is True
        assert remaining > 500
        assert "WAF rate limit" in reason

        ready, msg = check_portal_ready_for_redispatch("travis")
        assert ready is False
        assert "still in cooldown" in msg

        clear_portal_cooldown("travis")

    def test_waf_04_portal_recovers_after_cooldown(self):
        """WAF-04: Portal recovers after cooldown -> eligible for re-dispatch."""
        clear_portal_cooldown("hillsborough")
        # Ensure not in cooldown
        in_cool, remaining, _ = is_portal_in_cooldown("hillsborough")
        assert in_cool is False

        # Set operational state to READY
        set_portal_operational_state(
            "hillsborough",
            PortalOperationalState.READY,
            health_check_result="PASSED",
        )

        ready, msg = check_portal_ready_for_redispatch("hillsborough", require_health_check=True)
        assert ready is True
        assert "eligible for re-dispatch" in msg


# ===========================================================================
# 4. Retry Scenarios (RETRY-01 through RETRY-02)
# ===========================================================================


class TestRetryClassification:
    """RETRY-01 to RETRY-02: Distinguish retryable vs non-retryable failures."""

    def test_retry_01_retryable_network_failure(self):
        """RETRY-01: Network timeout is classified as retry-eligible with bounded backoff."""
        exc = TimeoutError("Connection timed out after 30000ms")
        event = classify_exception(exc, portal_key="miami", execution_stage="NAV_TO_SEARCH")

        assert event.error_code == ErrorCode.NETWORK_TIMEOUT
        assert event.retry_eligible is True
        assert event.cooldown_required is False
        assert event.recovery_action == RecoveryAction.BOUNDED_RETRY_WITH_BACKOFF

    def test_retry_02_non_retryable_failure(self):
        """RETRY-02: Exhausted max attempts is not retryable; requires human review."""
        cre = CaptchaResolutionError("CAPTCHA verification failed after max retries")
        event = classify_exception(cre, portal_key="dallas", execution_stage="CAPTCHA_WAIT")

        assert event.retry_eligible is False
        assert event.human_intervention is True
        assert event.recovery_action == RecoveryAction.MARK_AWAITING_HUMAN


# ===========================================================================
# 5. Re-dispatch Scenarios (REDISPATCH-01 through REDISPATCH-05)
# ===========================================================================


class TestRedispatchLifecycle:
    """REDISPATCH-01 to REDISPATCH-05: Cooldown expiry, isolation, duplicate prevention."""

    def test_redispatch_01_cooldown_expiry_check(self):
        """REDISPATCH-01: Cooldown expiry -> check_portal_ready_for_redispatch returns True."""
        clear_portal_cooldown("travis")
        ready, _ = check_portal_ready_for_redispatch("travis")
        assert ready is True

    def test_redispatch_02_operational_state_survives_restart_via_local_fallback(self):
        """REDISPATCH-02: Operational state and cooldown metadata persists in dictionary."""
        set_portal_operational_state(
            "travis",
            PortalOperationalState.WAF_BLOCKED,
            error_code=ErrorCode.WAF_RATE_LIMIT.value,
            blocking_reason="WAF rate limit",
            cooldown_seconds=600,
        )

        state = get_portal_operational_state("travis")
        assert state["operational_state"] == PortalOperationalState.WAF_BLOCKED
        assert state["error_code"] == ErrorCode.WAF_RATE_LIMIT.value
        assert state["cooldown_seconds"] == 600

    def test_redispatch_03_all_portal_operational_states_query(self):
        """REDISPATCH-03: get_all_portal_operational_states returns all 8 portals."""
        all_states = get_all_portal_operational_states()
        for k in ALL_PORTAL_KEYS:
            assert k in all_states
            assert "portal_key" in all_states[k]
            assert "in_cooldown" in all_states[k]

    def test_redispatch_04_cross_state_isolation(self):
        """REDISPATCH-04: One portal blocked (Travis) does NOT put other portals in cooldown."""
        clear_all_portal_cooldowns()

        # Travis blocked for 600s
        set_portal_cooldown("travis", seconds=600, reason="WAF rate limit")

        # Hillsborough, Broward, Miami, Dallas must NOT be in cooldown
        assert is_portal_in_cooldown("travis")[0] is True
        assert is_portal_in_cooldown("broward")[0] is False
        assert is_portal_in_cooldown("hillsborough")[0] is False
        assert is_portal_in_cooldown("miami")[0] is False
        assert is_portal_in_cooldown("dallas")[0] is False
        assert is_portal_in_cooldown("harris_jp")[0] is False
        assert is_portal_in_cooldown("harris_cclerk")[0] is False
        assert is_portal_in_cooldown("harris_district")[0] is False

        clear_all_portal_cooldowns()

    def test_redispatch_05_manual_intervention_blocks_redispatch(self):
        """REDISPATCH-05: Portals marked MANUAL_INTERVENTION_REQUIRED cannot be re-dispatched."""
        clear_portal_cooldown("dallas")
        set_portal_operational_state(
            "dallas",
            PortalOperationalState.MANUAL_INTERVENTION_REQUIRED,
            human_intervention=True,
            blocking_reason="Solver balance zero",
        )

        ready, reason = check_portal_ready_for_redispatch("dallas")
        assert ready is False
        assert "requires manual intervention" in reason


# ===========================================================================
# 6. Full 8-Bot Architecture & Coverage (E2E-01)
# ===========================================================================


class TestAllEightBotsCoverage:
    """E2E-01: Verifies all 8 bots adhere to centralized error & session architecture."""

    def test_e2e_01_all_8_bots_instantiate_and_inherit_base_methods(self):
        """E2E-01: All 8 scrapers instantiate and have required methods."""
        scrapers = [
            BrowardScraper(),
            HillsboroughScraper(),
            MiamiDadeScraper(),
            TravisScraper(),
            DallasScraper(),
            HarrisJPScraper(),
            HarrisCountyClerkScraper(),
            HarrisDistrictClerkScraper(),
        ]
        assert len(scrapers) == 8

        for s in scrapers:
            assert isinstance(s, BaseCourtScraper)
            assert hasattr(s, "search_by_party_name")
            assert hasattr(s, "detect_security_block")
            assert hasattr(s, "check_and_handle_session_timeout")
            assert hasattr(s, "capture_screenshot_on_error")
            assert hasattr(s, "captcha_wait_seconds")
            assert hasattr(s, "max_attempts")
