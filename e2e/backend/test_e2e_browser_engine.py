"""E2E Test: Browser Automation Engine Discovery & Extension Resolution.

Verifies that:
1. Playwright bundled Chromium is discoverable across Linux/Docker and Windows.
2. Google Chrome discovery checks system paths and PATH.
3. ExtensionManager resolves the AntiCaptcha extension across normalized paths.
"""

from pathlib import Path

from app.automation.browser_manager import ChromeSession, ExtensionManager


def test_chromium_executable_discovery():
    """Verify Chromium executable detection does not crash and returns a valid path if installed."""
    exe = ChromeSession.find_chromium_executable()
    # In CI or local dev with Playwright, exe is resolved
    if exe is not None:
        assert isinstance(exe, Path)
        assert exe.exists() or exe.name in ("chrome", "chrome.exe", "chromium")


def test_chrome_executable_discovery():
    """Verify Chrome executable detection supports Windows and Linux search."""
    exe = ChromeSession.find_chrome_executable()
    if exe is not None:
        assert isinstance(exe, Path)
        assert exe.exists()


def test_anticaptcha_extension_resolution():
    """Verify AntiCaptcha extension directory resolves properly with normalized paths."""
    resolved = ExtensionManager.resolve_extension_path("anticaptcha-plugin_v0.83")
    assert resolved is not None, "Failed to resolve anticaptcha-plugin_v0.83 directory"
    assert resolved.is_dir()
    assert (resolved / "manifest.json").exists()


def test_anticaptcha_extension_resolution_with_backslashes():
    """Verify AntiCaptcha extension directory resolves even when configured with Windows backslashes."""
    resolved = ExtensionManager.resolve_extension_path(".\\anticaptcha-plugin_v0.83\\")
    assert resolved is not None
    assert (resolved / "manifest.json").exists()
