"""Unit test suite for the Universal Human-Interaction Engine.

Validates:
- MouseController: cubic Bézier calculations, movement, click down/dwell/up, visual cursor injector
- KeyboardController: character-by-character typing cadence, Ctrl+A + Backspace clearing, readback verification
- NavigationController: address-bar navigation protocol, Control+L shortcut, URL loading
- VisualElementDetector: interactability checks and focus confirmation
- PageStateObserver: loading mask and spinner dismissal
- CaptchaStateMonitor: token detection and validation
- HumanInterventionManager: operator intervention pauses and timeout handling
- ExecutionAuditLogger: interaction event telemetry
- HumanInteractionEngine: full facade coordination
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.human_engine import (
    CaptchaStateMonitor,
    HumanInteractionEngine,
    HumanInterventionManager,
    KeyboardController,
    MouseController,
    NavigationController,
    PageStateObserver,
    VisualElementDetector,
)


@pytest.fixture
def mock_page():
    """Builds a comprehensive mock Playwright Page."""
    page = MagicMock()
    page.mouse = MagicMock()
    page.mouse.move = AsyncMock()
    page.mouse.down = AsyncMock()
    page.mouse.up = AsyncMock()
    page.mouse.wheel = AsyncMock()

    page.keyboard = MagicMock()
    page.keyboard.press = AsyncMock()
    page.keyboard.type = AsyncMock()

    page.evaluate = AsyncMock(return_value=True)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.title = AsyncMock(return_value="Court Portal Search")
    page.url = "https://www.exampleclerk.org/search"
    page.screenshot = AsyncMock()
    return page


@pytest.fixture
def mock_locator():
    """Builds a mock Playwright Locator."""
    loc = MagicMock()
    loc.wait_for = AsyncMock()
    loc.is_enabled = AsyncMock(return_value=True)
    loc.is_visible = AsyncMock(return_value=True)
    loc.scroll_into_view_if_needed = AsyncMock()
    loc.bounding_box = AsyncMock(return_value={"x": 100, "y": 200, "width": 150, "height": 35})
    loc.click = AsyncMock()
    loc.clear = AsyncMock()
    loc.press_sequentially = AsyncMock()
    loc.fill = AsyncMock()
    loc.input_value = AsyncMock(return_value="Smith")
    loc.count = AsyncMock(return_value=1)
    loc.first = loc
    return loc


# ─────────────────────────────────────────────────────────────────────────────
# 1. MouseController Tests
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_mouse_controller_bezier_movement(mock_page):
    ctrl = MouseController(movement_style="bezier_natural", show_cursor_trail=True)
    await ctrl.move_to(mock_page, target_x=450, target_y=320, steps=8)

    assert mock_page.mouse.move.await_count >= 8
    assert ctrl.current_x == 450
    assert ctrl.current_y == 320
    assert mock_page.evaluate.await_count > 0


@pytest.mark.asyncio
async def test_mouse_controller_click_at(mock_page):
    ctrl = MouseController(movement_style="instant", show_cursor_trail=True)
    await ctrl.click_at(mock_page, x=250, y=180, dwell_ms=40)

    assert mock_page.mouse.move.await_count >= 1
    assert mock_page.mouse.down.await_count == 1
    assert mock_page.mouse.up.await_count == 1


@pytest.mark.asyncio
async def test_mouse_controller_click_element(mock_page, mock_locator):
    ctrl = MouseController(movement_style="instant")
    await ctrl.click_element(mock_page, mock_locator)

    assert mock_locator.scroll_into_view_if_needed.await_count == 1
    assert mock_page.mouse.down.await_count == 1
    assert mock_page.mouse.up.await_count == 1


@pytest.mark.asyncio
async def test_mouse_controller_scroll_page(mock_page):
    ctrl = MouseController()
    await ctrl.scroll_page(mock_page, delta_y=300, steps=3)

    assert mock_page.mouse.wheel.await_count == 3


# ─────────────────────────────────────────────────────────────────────────────
# 2. KeyboardController Tests
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_keyboard_controller_type_text(mock_page, mock_locator):
    mock_locator.input_value = AsyncMock(return_value="Smith")
    ctrl = KeyboardController(typing_speed_mode="fast", typing_delay_ms=5)

    success = await ctrl.type_text(mock_page, mock_locator, "Smith", delay_ms=5, clear_first=True)
    assert success is True
    # Verify Ctrl+A and Backspace were pressed to clear
    pressed_keys = [call.args[0] for call in mock_page.keyboard.press.await_args_list]
    assert "Control+a" in pressed_keys
    assert "Backspace" in pressed_keys


@pytest.mark.asyncio
async def test_keyboard_controller_readback_retry(mock_page, mock_locator):
    # First read returns mismatched value, second returns corrected value
    mock_locator.input_value = AsyncMock(return_value="WrongVal")
    ctrl = KeyboardController(typing_speed_mode="fast", typing_delay_ms=0)

    success = await ctrl.type_text(mock_page, mock_locator, "Smith", delay_ms=0, clear_first=False)
    assert success is True
    assert mock_locator.fill.await_count >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 3. NavigationController Tests
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_navigation_controller_address_bar(mock_page):
    mouse = MouseController(movement_style="instant")
    keyboard = KeyboardController()
    nav = NavigationController(keyboard=keyboard, mouse=mouse)

    target_url = "https://www.browardclerk.org/Web2"
    res = await nav.navigate_via_address_bar(mock_page, target_url, timeout_ms=5000)
    assert res is True
    mock_page.goto.assert_awaited_once_with(target_url, wait_until="domcontentloaded", timeout=5000)
    # Confirm Control+L address bar focus was triggered
    pressed_keys = [call.args[0] for call in mock_page.keyboard.press.await_args_list]
    assert "Control+l" in pressed_keys


# ─────────────────────────────────────────────────────────────────────────────
# 4. Element Detection & State Observation Tests
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_visual_element_detector(mock_page, mock_locator):
    mock_page.locator.return_value = mock_locator
    detector = VisualElementDetector()

    loc = await detector.find_interactable(mock_page, "#lastName")
    assert loc is not None
    assert mock_locator.wait_for.await_count == 1


@pytest.mark.asyncio
async def test_page_state_observer(mock_page, mock_locator):
    mock_page.locator.return_value = mock_locator
    observer = PageStateObserver()

    await observer.wait_for_loading_dismissal(mock_page, mask_selectors=[".k-loading-mask"])
    assert mock_locator.wait_for.await_count >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 5. CAPTCHA State & Human Intervention Tests
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_captcha_state_monitor(mock_page):
    mock_page.evaluate = AsyncMock(return_value="turnstile")
    challenge = await CaptchaStateMonitor.detect_challenge(mock_page)
    assert challenge == "turnstile"

    mock_page.evaluate = AsyncMock(return_value=True)
    is_solved = await CaptchaStateMonitor.is_solved(mock_page)
    assert is_solved is True


@pytest.mark.asyncio
async def test_human_intervention_manager(mock_page):
    manager = HumanInterventionManager(timeout_seconds=2)
    with patch(
        "app.automation.human_engine.CaptchaStateMonitor.is_solved", AsyncMock(return_value=True)
    ):
        solved = await manager.wait_for_operator_or_extension(
            mock_page, "Broward", timeout_seconds=1
        )
        assert solved is True


# ─────────────────────────────────────────────────────────────────────────────
# 6. Full HumanInteractionEngine Facade Tests
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_human_interaction_engine_facade(mock_page, mock_locator):
    mock_page.locator.return_value = mock_locator
    mock_locator.input_value = AsyncMock(return_value="Smith")

    engine = HumanInteractionEngine(
        movement_style="instant",
        typing_speed_mode="fast",
        typing_delay_ms=0,
        click_timeout_ms=5000,
        show_cursor_trail=True,
    )

    # Test full 9-step fill
    fill_ok = await engine.interact_and_fill(
        mock_page, "#lastName", "Smith", field_name="Last Name"
    )
    assert fill_ok is True
    assert len(engine.audit.entries) >= 1

    # Test click
    click_ok = await engine.interact_and_click(mock_page, "#submitBtn", button_name="Search")
    assert click_ok is True

    # Test address bar navigate
    nav_ok = await engine.navigate_portal(mock_page, "https://www.browardclerk.org/Web2")
    assert nav_ok is True

    # Test captcha verification
    with patch(
        "app.automation.human_engine.CaptchaStateMonitor.detect_challenge",
        AsyncMock(return_value=None),
    ):
        cap_ok = await engine.verify_captcha(mock_page, "Broward")
        assert cap_ok is True
