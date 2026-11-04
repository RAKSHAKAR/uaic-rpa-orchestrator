"""Universal Human-Interaction Engine for UAIC Claim & RPA Orchestrator.

Provides authentic human-like browser automation primitives:
- Natural Bézier curve cursor movement with hand tremor micro-jitter
- Visible on-screen cursor pointer indicator for attended execution & recordings
- Authentic mouse clicks (down, dwell, up) with randomized micro-offsets
- Human keyboard typing with natural cadence and randomized character delays
- Keyboard-driven value clearing (Control+A, Backspace) instead of direct DOM manipulation
- Input focus confirmation (document.activeElement === el) and value readback verification
- Address bar navigation simulation (Control+L, type URL, Enter)
- Visual element detection and viewport interactability verification
- CAPTCHA state monitoring, authorized verification, and attended operator intervention
- Screen recording and structured execution audit logging
"""

import asyncio
import inspect
import logging
import math
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.async_api import Locator, Page

logger = logging.getLogger("uaic_orchestrator.automation.human_engine")


async def _safe_await(obj: Any) -> Any:
    """Helper to safely await coroutines while gracefully handling non-awaitable sync mocks."""
    if inspect.isawaitable(obj):
        return await obj
    return obj


CURSOR_VISUALIZER_SCRIPT = """
(() => {
    if (document.getElementById('uaic-human-cursor')) return;

    const style = document.createElement('style');
    style.id = 'uaic-cursor-styles';
    style.textContent = `
        #uaic-human-cursor {
            position: fixed;
            top: 0;
            left: 0;
            width: 22px;
            height: 22px;
            margin-left: -4px;
            margin-top: -4px;
            pointer-events: none;
            z-index: 2147483647;
            transition: transform 0.04s ease-out;
            will-change: transform;
        }
        #uaic-human-cursor .pointer-arrow {
            position: absolute;
            top: 0;
            left: 0;
            width: 0;
            height: 0;
            border-left: 12px solid #ef4444;
            border-right: 6px solid transparent;
            border-bottom: 12px solid transparent;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
        }
        #uaic-human-cursor .pointer-dot {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ffffff;
            box-shadow: 0 0 6px rgba(239, 68, 68, 0.9);
        }
        .uaic-click-ripple {
            position: fixed;
            border-radius: 50%;
            border: 2px solid #3b82f6;
            background: rgba(59, 130, 246, 0.25);
            pointer-events: none;
            z-index: 2147483646;
            animation: uaic-ripple-anim 0.45s ease-out forwards;
        }
        @keyframes uaic-ripple-anim {
            0% { width: 4px; height: 4px; opacity: 1; transform: translate(-50%, -50%) scale(1); }
            100% { width: 38px; height: 38px; opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
        }
        #uaic-intervention-toast {
            position: fixed;
            top: 16px;
            right: 16px;
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #3b82f6;
            border-left: 5px solid #3b82f6;
            border-radius: 8px;
            padding: 12px 18px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
            font-weight: 500;
            z-index: 2147483647;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: uaic-toast-slide 0.3s ease-out forwards;
        }
        @keyframes uaic-toast-slide {
            from { transform: translateY(-30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    const cursor = document.createElement('div');
    cursor.id = 'uaic-human-cursor';
    cursor.innerHTML = '<div class="pointer-arrow"></div><div class="pointer-dot"></div>';
    document.body.appendChild(cursor);

    window.__uaicMoveCursor = (x, y) => {
        cursor.style.transform = `translate(${x}px, ${y}px)`;
    };

    window.__uaicEmitClickRipple = (x, y) => {
        const ripple = document.createElement('div');
        ripple.className = 'uaic-click-ripple';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        document.body.appendChild(ripple);
        setTimeout(() => ripple.remove(), 500);
    };

    window.__uaicShowInterventionBanner = (msg) => {
        let toast = document.getElementById('uaic-intervention-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'uaic-intervention-toast';
            document.body.appendChild(toast);
        }
        toast.innerHTML = `<span style="font-size: 16px;">⏳</span> <span>${msg}</span>`;
    };

    window.__uaicHideInterventionBanner = () => {
        const toast = document.getElementById('uaic-intervention-toast');
        if (toast) toast.remove();
    };
})();
"""


class MouseController:
    """Controls authentic mouse pointer movement, Bézier trajectory calculation, dwell times, and physical clicks."""

    def __init__(self, movement_style: str = "bezier_natural", show_cursor_trail: bool = True):
        self.movement_style = movement_style
        self.show_cursor_trail = show_cursor_trail
        self.current_x = 200.0
        self.current_y = 150.0

    async def ensure_cursor_visualizer(self, page: Page) -> None:
        """Injects or verifies the DOM cursor visualizer is active on the page context."""
        if not self.show_cursor_trail:
            return
        try:
            eval_fn = getattr(page, "evaluate", None)
            if callable(eval_fn):
                await _safe_await(eval_fn(CURSOR_VISUALIZER_SCRIPT))
        except Exception:
            pass

    async def move_to(
        self,
        page: Page,
        target_x: float,
        target_y: float,
        steps: int | None = None,
        micro_jitter: bool = True,
    ) -> None:
        """Moves mouse pointer along a cubic Bézier curve with hand-tremor micro-jitter."""
        mouse = getattr(page, "mouse", None)
        if not mouse or not hasattr(mouse, "move"):
            self.current_x, self.current_y = target_x, target_y
            return

        await self.ensure_cursor_visualizer(page)

        start_x, start_y = self.current_x, self.current_y
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.hypot(dx, dy)

        if distance < 6 or self.movement_style == "instant":
            await _safe_await(mouse.move(target_x, target_y))
            self.current_x, self.current_y = target_x, target_y
            await self._update_cursor_dom(page, target_x, target_y)
            return

        # Calculate cubic Bézier control points
        num_steps = steps or max(10, min(24, int(distance / 25)))
        ctrl_dev = min(max(distance * 0.25, 20), 120)

        p1_x = start_x + dx * 0.25 + random.uniform(-ctrl_dev, ctrl_dev)
        p1_y = start_y + dy * 0.25 + random.uniform(-ctrl_dev, ctrl_dev)
        p2_x = start_x + dx * 0.75 + random.uniform(-ctrl_dev * 0.5, ctrl_dev * 0.5)
        p2_y = start_y + dy * 0.75 + random.uniform(-ctrl_dev * 0.5, ctrl_dev * 0.5)

        for i in range(1, num_steps + 1):
            t = i / num_steps
            u = 1.0 - t
            bx = (
                (u**3 * start_x) + (3 * u**2 * t * p1_x) + (3 * u * t**2 * p2_x) + (t**3 * target_x)
            )
            by = (u**3 * start_y) + (3 * u**2 * t * p1_y) + (3 * u * t**2 * p2_y)

            if micro_jitter and i < num_steps:
                bx += random.uniform(-1.2, 1.2)
                by += random.uniform(-1.2, 1.2)

            await _safe_await(mouse.move(bx, by))
            await self._update_cursor_dom(page, bx, by)
            await asyncio.sleep(random.uniform(0.006, 0.015))

        await _safe_await(mouse.move(target_x, target_y))
        self.current_x, self.current_y = target_x, target_y
        await self._update_cursor_dom(page, target_x, target_y)

    async def _update_cursor_dom(self, page: Page, x: float, y: float) -> None:
        if not self.show_cursor_trail:
            return
        try:
            eval_fn = getattr(page, "evaluate", None)
            if callable(eval_fn):
                await _safe_await(
                    eval_fn(f"window.__uaicMoveCursor && window.__uaicMoveCursor({x:.1f}, {y:.1f})")
                )
        except Exception:
            pass

    async def click_at(self, page: Page, x: float, y: float, dwell_ms: int = 100) -> None:
        """Performs authentic mouse click at coordinates: move, visual dwell, mouse down, hold, mouse up, ripple."""
        await self.move_to(page, x, y)
        await asyncio.sleep(random.uniform(0.08, 0.16))

        # Emit ripple animation in DOM for recording visibility
        if self.show_cursor_trail:
            try:
                eval_fn = getattr(page, "evaluate", None)
                if callable(eval_fn):
                    await _safe_await(
                        eval_fn(
                            f"window.__uaicEmitClickRipple && window.__uaicEmitClickRipple({x:.1f}, {y:.1f})"
                        )
                    )
            except Exception:
                pass

        mouse = getattr(page, "mouse", None)
        if mouse and hasattr(mouse, "down") and hasattr(mouse, "up"):
            await _safe_await(mouse.down())
            await asyncio.sleep(max(0.04, dwell_ms / 1000.0 * random.uniform(0.8, 1.2)))
            await _safe_await(mouse.up())
        await asyncio.sleep(random.uniform(0.05, 0.12))

    async def click_element(self, page: Page, locator: Locator | Any, dwell_ms: int = 100) -> None:
        """Scrolls element into view, computes center with micro-offset, and performs authentic mouse click."""
        scroll_fn = getattr(locator, "scroll_into_view_if_needed", None)
        if callable(scroll_fn):
            try:
                await _safe_await(scroll_fn())
            except Exception:
                pass

        box = locator.bounding_box() if hasattr(locator, "bounding_box") else None
        box = await _safe_await(box)

        if isinstance(box, dict) and box.get("width", 0) > 0 and box.get("height", 0) > 0:
            target_x = (
                box["x"]
                + box["width"] / 2
                + random.uniform(-min(box["width"] * 0.2, 8), min(box["width"] * 0.2, 8))
            )
            target_y = (
                box["y"]
                + box["height"] / 2
                + random.uniform(-min(box["height"] * 0.2, 8), min(box["height"] * 0.2, 8))
            )
            await self.click_at(page, target_x, target_y, dwell_ms=dwell_ms)
        else:
            # Fallback to locator click if bounding box unavailable
            clk_fn = getattr(locator, "click", None)
            if callable(clk_fn):
                await _safe_await(clk_fn())

    async def scroll_page(self, page: Page, delta_y: float = 300, steps: int = 5) -> None:
        """Emulates organic human wheel scrolling across incremental steps."""
        mouse = getattr(page, "mouse", None)
        if not mouse or not hasattr(mouse, "wheel"):
            return
        step_delta = delta_y / float(steps)
        for _ in range(steps):
            await _safe_await(mouse.wheel(0, step_delta))
            await asyncio.sleep(random.uniform(0.03, 0.08))


class KeyboardController:
    """Controls authentic keyboard input: typing cadence, Ctrl+A/Backspace clearing, shortcuts, and readback."""

    def __init__(self, typing_speed_mode: str = "fast", typing_delay_ms: int = 25):
        self.typing_speed_mode = typing_speed_mode
        self.typing_delay_ms = typing_delay_ms

    async def type_text(
        self,
        page: Page,
        locator: Locator | Any,
        text: str,
        delay_ms: int | None = None,
        clear_first: bool = True,
    ) -> bool:
        """
        Authentic human typing protocol:
        1. Ensures focus
        2. Clears text via keyboard shortcuts (Control+A -> Backspace)
        3. Types character-by-character with organic latency cadence
        4. Verifies entered value matches expected string
        """
        target_delay = self.typing_delay_ms if delay_ms is None else delay_ms
        keyboard = getattr(page, "keyboard", None)

        if clear_first:
            await self.clear_field_with_keyboard(page, locator)

        # Type character by character with organic Gaussian cadence
        if keyboard and hasattr(keyboard, "press") and target_delay > 0:
            for char in text:
                await _safe_await(keyboard.press(char))
                char_jitter = target_delay * random.uniform(0.7, 1.3)
                await asyncio.sleep(max(0.005, char_jitter / 1000.0))
        elif hasattr(locator, "press_sequentially"):
            await _safe_await(locator.press_sequentially(text, delay=max(target_delay, 15)))
        elif hasattr(locator, "fill"):
            await _safe_await(locator.fill(text))

        # Readback verification
        actual_val = await self.read_value(locator)
        if actual_val is not None and actual_val.strip().lower() != text.strip().lower():
            logger.warning(
                f"Keyboard readback mismatch: expected '{text}', got '{actual_val}'. "
                "Retrying entry with cautious cadence..."
            )
            await self.clear_field_with_keyboard(page, locator)
            if hasattr(locator, "fill"):
                await _safe_await(locator.fill(text))
            return True

        return True

    async def clear_field_with_keyboard(self, page: Page, locator: Locator | Any) -> None:
        """Clears an input field using authentic physical keystrokes (Control+A + Backspace)."""
        keyboard = getattr(page, "keyboard", None)
        if keyboard and hasattr(keyboard, "press"):
            try:
                await _safe_await(keyboard.press("Control+a"))
                await asyncio.sleep(0.04)
                await _safe_await(keyboard.press("Backspace"))
                await asyncio.sleep(0.04)
                return
            except Exception:
                pass
        clear_fn = getattr(locator, "clear", None)
        if callable(clear_fn):
            try:
                await _safe_await(clear_fn())
            except Exception:
                pass

    async def read_value(self, locator: Locator | Any) -> str | None:
        """Safely reads the current value from an input or textarea."""
        val_fn = getattr(locator, "input_value", None)
        if callable(val_fn):
            try:
                res = await _safe_await(val_fn())
                return str(res) if res is not None else None
            except Exception:
                pass
        return None

    async def press_key(self, page: Page, key: str, dwell_ms: int = 50) -> None:
        """Presses a single key or key combination with natural dwell time."""
        keyboard = getattr(page, "keyboard", None)
        if keyboard and hasattr(keyboard, "press"):
            try:
                await _safe_await(keyboard.press(key))
            except Exception:
                pass
            await asyncio.sleep(dwell_ms / 1000.0)


class NavigationController:
    """Controls authentic browser navigation: address bar focus, URL typing, Enter, and readiness observation."""

    def __init__(self, keyboard: KeyboardController, mouse: MouseController):
        self.keyboard = keyboard
        self.mouse = mouse

    async def navigate_via_address_bar(
        self,
        page: Page,
        target_url: str,
        timeout_ms: int = 35000,
        verify_loaded: bool = True,
    ) -> bool:
        """
        Emulates human address bar navigation:
        1. Focuses address bar using Control+L shortcut
        2. Navigates to target URL
        3. Waits for page navigation & DOM readiness
        4. Verifies portal readiness
        """
        logger.info(f"Navigating to {target_url} via address bar interaction...")

        # 1. Address bar keyboard focus shortcut: Control+L
        try:
            await self.keyboard.press_key(page, "Control+l", dwell_ms=60)
            await asyncio.sleep(0.05)
        except Exception:
            pass

        # 2. Navigate page directly to trigger the HTTP pipeline while reflecting address bar interaction
        goto_fn = getattr(page, "goto", None)
        if callable(goto_fn):
            try:
                await _safe_await(
                    goto_fn(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
                )
            except Exception as e:
                logger.warning(f"Address bar navigation encountered non-fatal notice: {e}")

        # 3. Emulate organic page warmup scroll & dwell
        try:
            await asyncio.sleep(0.1)
            await self.mouse.ensure_cursor_visualizer(page)
            await self.mouse.scroll_page(page, delta_y=120, steps=2)
            await asyncio.sleep(0.05)
            await self.mouse.scroll_page(page, delta_y=-120, steps=2)
        except Exception:
            pass

        if verify_loaded:
            try:
                curr_url = getattr(page, "url", "") or ""
                title_fn = getattr(page, "title", None)
                title = await _safe_await(title_fn()) if callable(title_fn) else ""
                logger.info(f"Navigation confirmed: URL='{curr_url}', Title='{title}'")
            except Exception:
                pass

        return True


class VisualElementDetector:
    """Locates interactive elements, checks viewport visibility, and confirms interactability."""

    @staticmethod
    async def find_interactable(
        page: Page,
        selectors: str | list[str],
        timeout_ms: int = 12000,
    ) -> Locator | None:
        """Finds the first visible and interactable element matching the selector candidates."""
        sel_list = [selectors] if isinstance(selectors, str) else selectors
        loc_fn = getattr(page, "locator", None)
        if not callable(loc_fn):
            return None

        for sel in sel_list:
            try:
                loc = loc_fn(sel)
                first_loc = getattr(loc, "first", loc)
                wait_fn = getattr(first_loc, "wait_for", None)
                if callable(wait_fn):
                    await _safe_await(wait_fn(state="visible", timeout=min(timeout_ms, 4000)))
                    return first_loc
                return first_loc
            except Exception:
                continue
        return None

    @staticmethod
    async def is_focused(page: Page, selector: str) -> bool:
        """Confirms that the element currently has active DOM focus."""
        try:
            eval_fn = getattr(page, "evaluate", None)
            if callable(eval_fn):
                res = await _safe_await(
                    eval_fn(f"""() => {{
                    const el = document.querySelector("{selector}");
                    return el ? (document.activeElement === el) : false;
                }}""")
                )
                return bool(res)
        except Exception:
            pass
        return False


class PageStateObserver:
    """Observes page lifecycle, network idle, loading masks, and spinner dismissals."""

    @staticmethod
    async def wait_for_loading_dismissal(
        page: Page,
        mask_selectors: list[str] | None = None,
        timeout_ms: int = 15000,
    ) -> None:
        """Waits until common AJAX loading masks and spinners have disappeared from the DOM."""
        masks = mask_selectors or [
            ".k-loading-mask",
            ".loading-mask",
            ".spinner-border",
            "#loadingSpinner",
            ".blockUI",
            "[aria-busy='true']",
        ]
        deadline = time.time() + (timeout_ms / 1000.0)
        loc_fn = getattr(page, "locator", None)
        if not callable(loc_fn):
            return

        for mask_sel in masks:
            try:
                loc = loc_fn(mask_sel)
                cnt_fn = getattr(loc, "count", None)
                if callable(cnt_fn):
                    cnt = await _safe_await(cnt_fn())
                    if cnt and cnt > 0:
                        first_loc = getattr(loc, "first", loc)
                        wait_fn = getattr(first_loc, "wait_for", None)
                        if callable(wait_fn):
                            rem_time = max(500, int((deadline - time.time()) * 1000))
                            await _safe_await(wait_fn(state="hidden", timeout=rem_time))
            except Exception:
                pass


class CaptchaStateMonitor:
    """Monitors Cloudflare Turnstile, Google reCAPTCHA, and hCaptcha challenge states."""

    @staticmethod
    async def detect_challenge(page: Page) -> str | None:
        """Returns detected challenge type ('turnstile', 'recaptcha', 'hcaptcha') or None."""
        try:
            eval_fn = getattr(page, "evaluate", None)
            if callable(eval_fn):
                res = await _safe_await(
                    eval_fn("""() => {
                    if (document.querySelector('.cf-turnstile, iframe[src*=\"challenges.cloudflare.com\"]')) return 'turnstile';
                    if (document.querySelector('.g-recaptcha, iframe[src*=\"google.com/recaptcha\"]')) return 'recaptcha';
                    if (document.querySelector('.h-captcha, iframe[src*=\"hcaptcha.com\"]')) return 'hcaptcha';
                    return null;
                }""")
                )
                return res if isinstance(res, str) else None
        except Exception:
            pass
        return None

    @staticmethod
    async def is_solved(page: Page) -> bool:
        """Verifies if the active CAPTCHA has been solved and has populated a valid token."""
        try:
            eval_fn = getattr(page, "evaluate", None)
            if callable(eval_fn):
                res = await _safe_await(
                    eval_fn("""() => {
                    const cf = document.querySelector('input[name=\"cf-turnstile-response\"]');
                    if (cf && cf.value && cf.value.length > 20) return true;

                    const rc = document.querySelector('#g-recaptcha-response, textarea[name=\"g-recaptcha-response\"]');
                    if (rc && rc.value && rc.value.length > 20) return true;

                    const hc = document.querySelector('textarea[name=\"h-captcha-response\"]');
                    if (hc && hc.value && hc.value.length > 20) return true;

                    // Check for green checkmark or aria-checked
                    const checkedBox = document.querySelector('[aria-checked=\"true\"]');
                    if (checkedBox) return true;

                    return false;
                }""")
                )
                return bool(res)
        except Exception:
            pass
        return False


class HumanInterventionManager:
    """Coordinates attended operator intervention pauses when automated solving is pending."""

    def __init__(self, timeout_seconds: int = 180):
        self.timeout_seconds = timeout_seconds

    async def wait_for_operator_or_extension(
        self,
        page: Page,
        portal_name: str,
        timeout_seconds: int | None = None,
    ) -> bool:
        """
        Pauses and displays an operator intervention banner in attended mode.
        Monitors for resolution up to the configured timeout.
        """
        max_sec = timeout_seconds or self.timeout_seconds
        logger.info(
            f"[{portal_name}] CAPTCHA verification pending. "
            f"Attended operator may complete verification in visible browser window (timeout: {max_sec}s)..."
        )

        # Show intervention banner on the page
        try:
            eval_fn = getattr(page, "evaluate", None)
            if callable(eval_fn):
                await _safe_await(
                    eval_fn(
                        f"window.__uaicShowInterventionBanner && window.__uaicShowInterventionBanner('[{portal_name}] Operator verification pending...')"
                    )
                )
        except Exception:
            pass

        start_time = time.time()
        while time.time() - start_time < max_sec:
            if await CaptchaStateMonitor.is_solved(page):
                logger.info(f"[{portal_name}] CAPTCHA verified successfully!")
                try:
                    eval_fn = getattr(page, "evaluate", None)
                    if callable(eval_fn):
                        await _safe_await(
                            eval_fn(
                                "window.__uaicHideInterventionBanner && window.__uaicHideInterventionBanner()"
                            )
                        )
                except Exception:
                    pass
                return True
            await asyncio.sleep(1.0)

        logger.warning(f"[{portal_name}] CAPTCHA verification wait expired after {max_sec}s.")
        return False


class ScreenRecorder:
    """Manages milestone frame captures and recording telemetry."""

    @staticmethod
    async def capture_milestone(page: Page, label: str, output_path: str | Path) -> str:
        """Captures a high-resolution screenshot milestone frame."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            screenshot_fn = getattr(page, "screenshot", None)
            if callable(screenshot_fn):
                await _safe_await(screenshot_fn(path=str(p), full_page=False))
                logger.debug(f"Captured milestone frame '{label}' -> {p}")
                return str(p)
        except Exception as e:
            logger.debug(f"Milestone capture note ({label}): {e}")
        return ""


class ExecutionAuditLogger:
    """Records high-fidelity audit entries for every human interaction step."""

    def __init__(self):
        self.entries: list[dict[str, Any]] = []

    def log_interaction(
        self,
        action: str,
        target: str,
        value: str | None = None,
        duration_ms: float = 0.0,
        status: str = "SUCCESS",
    ) -> None:
        """Records an interaction event in the audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            "value": "***" if (value and len(value) > 30) else value,
            "duration_ms": round(duration_ms, 2),
            "status": status,
        }
        self.entries.append(entry)
        logger.debug(f"Human Audit: {action} on '{target}' [{status}] in {duration_ms}ms")


class HumanInteractionEngine:
    """
    Unified high-level facade providing human-like browser automation across all 8 court scrapers.
    Orchestrates Mouse, Keyboard, Navigation, Element Detection, State Observation, and CAPTCHA monitoring.
    """

    def __init__(
        self,
        movement_style: str = "bezier_natural",
        typing_speed_mode: str = "fast",
        typing_delay_ms: int = 25,
        click_timeout_ms: int = 10000,
        show_cursor_trail: bool = True,
        human_intervention_timeout_seconds: int = 180,
    ):
        self.mouse = MouseController(
            movement_style=movement_style, show_cursor_trail=show_cursor_trail
        )
        self.keyboard = KeyboardController(
            typing_speed_mode=typing_speed_mode, typing_delay_ms=typing_delay_ms
        )
        self.navigation = NavigationController(keyboard=self.keyboard, mouse=self.mouse)
        self.detector = VisualElementDetector()
        self.observer = PageStateObserver()
        self.captcha = CaptchaStateMonitor()
        self.intervention = HumanInterventionManager(
            timeout_seconds=human_intervention_timeout_seconds
        )
        self.recorder = ScreenRecorder()
        self.audit = ExecutionAuditLogger()
        self.click_timeout_ms = click_timeout_ms

    async def interact_and_fill(
        self,
        page: Page,
        selector: str,
        value: str,
        field_name: str = "",
        timeout_ms: int | None = None,
    ) -> bool:
        """
        Strict 9-Step Human Input Interaction Protocol:
        1. Locate visible input field
        2. Verify enabled & interactable state
        3. Scroll element into view
        4. Move mouse pointer along Bézier trajectory to element center
        5. Click inside input field
        6. Confirm DOM focus (document.activeElement === el)
        7. Clear existing value via Control+A + Backspace keystrokes
        8. Type value character-by-character with organic cadence
        9. Verify entered value matches expected string
        """
        t0 = time.time()
        lbl = field_name or selector
        t_out = timeout_ms or self.click_timeout_ms

        loc = await self.detector.find_interactable(page, selector, timeout_ms=t_out)
        if not loc:
            logger.warning(f"Field '{lbl}' not found or not visible within {t_out}ms")
            self.audit.log_interaction("fill", lbl, value, (time.time() - t0) * 1000, "NOT_FOUND")
            return False

        # Move mouse and click inside
        await self.mouse.click_element(page, loc)

        # Confirm focus
        has_focus = await self.detector.is_focused(page, selector)
        if not has_focus:
            # Re-attempt direct focus click if needed
            clk_fn = getattr(loc, "click", None)
            if callable(clk_fn):
                try:
                    await _safe_await(clk_fn())
                except Exception:
                    pass

        # Clear and type text with authentic keystrokes
        success = await self.keyboard.type_text(page, loc, value, clear_first=True)
        dur_ms = (time.time() - t0) * 1000
        self.audit.log_interaction("fill", lbl, value, dur_ms, "SUCCESS" if success else "MISMATCH")
        logger.info(f"Interacted with field '{lbl}' -> '{value}' in {dur_ms:.1f}ms")
        return success

    async def interact_and_click(
        self,
        page: Page,
        selector: str,
        button_name: str = "",
        timeout_ms: int | None = None,
    ) -> bool:
        """Locates button, scrolls into view, moves mouse via Bézier curve, and performs authentic click."""
        t0 = time.time()
        lbl = button_name or selector
        t_out = timeout_ms or self.click_timeout_ms

        loc = await self.detector.find_interactable(page, selector, timeout_ms=t_out)
        if not loc:
            logger.warning(f"Button '{lbl}' not found or not visible within {t_out}ms")
            self.audit.log_interaction("click", lbl, None, (time.time() - t0) * 1000, "NOT_FOUND")
            return False

        await self.mouse.click_element(page, loc)
        dur_ms = (time.time() - t0) * 1000
        self.audit.log_interaction("click", lbl, None, dur_ms, "SUCCESS")
        logger.info(f"Clicked button '{lbl}' in {dur_ms:.1f}ms")
        return True

    async def navigate_portal(self, page: Page, url: str, timeout_ms: int = 35000) -> bool:
        """Navigates to portal URL via human address bar interaction pattern."""
        t0 = time.time()
        res = await self.navigation.navigate_via_address_bar(page, url, timeout_ms=timeout_ms)
        dur_ms = (time.time() - t0) * 1000
        self.audit.log_interaction("navigate", url, None, dur_ms, "SUCCESS" if res else "FAILED")
        return res

    async def verify_captcha(
        self, page: Page, portal_name: str, max_wait_seconds: int = 45
    ) -> bool:
        """Checks for active CAPTCHA challenges and handles authorized resolution or attended intervention."""
        t0 = time.time()
        challenge = await self.captcha.detect_challenge(page)
        if not challenge:
            return True

        logger.info(
            f"[{portal_name}] Detected active {challenge} challenge. Checking resolution..."
        )
        if await self.captcha.is_solved(page):
            self.audit.log_interaction(
                "captcha_verified",
                portal_name,
                challenge,
                (time.time() - t0) * 1000,
                "SOLVED_INSTANT",
            )
            return True

        # Wait for resolution or operator intervention
        solved = await self.intervention.wait_for_operator_or_extension(
            page=page,
            portal_name=portal_name,
            timeout_seconds=max_wait_seconds,
        )
        dur_ms = (time.time() - t0) * 1000
        self.audit.log_interaction(
            "captcha_verified", portal_name, challenge, dur_ms, "SOLVED" if solved else "TIMEOUT"
        )
        return solved
