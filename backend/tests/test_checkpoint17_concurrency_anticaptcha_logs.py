"""
Tests for Checkpoint 17 features:
  1. Redis-backed concurrency semaphore (scraper_tasks)
  2. AntiCaptcha settings schema validation
  3. resolve_extension_dir backward-compat shim (session_runner)
  4. ExtensionManager.resolve_extension_path
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. resolve_extension_dir shim - backward-compat
# ---------------------------------------------------------------------------


def test_resolve_extension_dir_shim_importable():
    """session_runner must export resolve_extension_dir (compat shim)."""
    from app.automation.session_runner import resolve_extension_dir
    assert callable(resolve_extension_dir)


def test_resolve_extension_dir_shim_returns_none_or_str():
    """Returns None or str - never raises on bad paths (falls back to repo root)."""
    from app.automation.session_runner import resolve_extension_dir
    result = resolve_extension_dir("/nonexistent/path/that/does/not/exist")
    # The function either returns None or finds the repo-root extension fallback
    # Both are valid - it must never raise an exception.
    assert result is None or isinstance(result, str)


def test_resolve_extension_dir_shim_returns_str_for_valid_dir(tmp_path):
    """Returns string path when a valid extension dir (with manifest.json) is passed."""
    ext_dir = tmp_path / "anticaptcha-plugin_v0.83"
    ext_dir.mkdir()
    # Create manifest.json so resolve_extension_path recognises it as valid
    (ext_dir / "manifest.json").write_text('{"manifest_version": 3}')

    from app.automation.session_runner import resolve_extension_dir
    result = resolve_extension_dir(str(ext_dir))
    # Must return the path string (or a normalized version of it)
    assert result is not None
    assert isinstance(result, str)


def test_resolve_extension_dir_shim_returns_str_type():
    """shim always returns str (not Path) when a value is returned."""
    from app.automation.session_runner import resolve_extension_dir
    result = resolve_extension_dir(None)
    # None when no extension found, otherwise a str
    assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# 2. AntiCaptcha settings schema validation
# ---------------------------------------------------------------------------


def test_anticaptcha_settings_schema_has_core_fields():
    """AutomationSettings must include the core anticaptcha fields."""
    from app.schemas.settings import AutomationSettings
    required = [
        "anticaptcha_api_key",
        "anticaptcha_solve_recaptcha2",
        "anticaptcha_solve_recaptcha3",
        "anticaptcha_solve_hcaptcha",
        "anticaptcha_solve_turnstile",
        "anticaptcha_solve_funcaptcha",
        "anticaptcha_solve_geetest",
        "anticaptcha_auto_submit",
        "anticaptcha_play_sounds",
        "anticaptcha_recaptcha3_score",   # actual field name
    ]
    try:
        fields = AutomationSettings.model_fields
    except AttributeError:
        fields = AutomationSettings.__fields__
    for field in required:
        assert field in fields, f"Missing AntiCaptcha field: {field}"


def test_anticaptcha_defaults_are_safe():
    """Boolean solve fields should default to True; non-critical to False."""
    from app.schemas.settings import AutomationSettings
    inst = AutomationSettings()
    assert inst.anticaptcha_solve_recaptcha2 is True
    assert inst.anticaptcha_solve_hcaptcha is True
    assert inst.anticaptcha_auto_submit is False   # must not auto-submit by default
    assert inst.anticaptcha_play_sounds is False   # sounds off by default


def test_anticaptcha_recaptcha3_score_valid_range():
    """anticaptcha_recaptcha3_score must accept a float value."""
    from app.schemas.settings import AutomationSettings
    valid = AutomationSettings(anticaptcha_recaptcha3_score=0.7)
    assert abs(valid.anticaptcha_recaptcha3_score - 0.7) < 0.001


def test_anticaptcha_recaptcha3_score_default_in_range():
    """Default score must be in [0.1, 0.9] per AntiCaptcha v3 specification."""
    from app.schemas.settings import AutomationSettings
    inst = AutomationSettings()
    score = inst.anticaptcha_recaptcha3_score
    assert 0.1 <= score <= 0.9, f"Default reCAPTCHA v3 score {score} out of [0.1, 0.9]"


# ---------------------------------------------------------------------------
# 3. Redis semaphore constants (scraper_tasks)
# ---------------------------------------------------------------------------


def test_browser_semaphore_key_defined():
    """BROWSER_SEMAPHORE_KEY constant must be defined in scraper_tasks."""
    import app.tasks.scraper_tasks as st
    assert hasattr(st, "BROWSER_SEMAPHORE_KEY"), "BROWSER_SEMAPHORE_KEY missing from scraper_tasks"
    key = st.BROWSER_SEMAPHORE_KEY
    assert isinstance(key, str) and len(key) > 0


def test_concurrency_slot_key_contains_identifier():
    """Semaphore key must contain a recognizable domain identifier."""
    import app.tasks.scraper_tasks as st
    key = st.BROWSER_SEMAPHORE_KEY.lower()
    # Must contain at least one of: uaic, browser, semaphore, rpa
    assert any(x in key for x in ("uaic", "browser", "semaphore", "rpa")), (
        f"Key '{key}' doesn't contain a recognizable domain identifier"
    )


# ---------------------------------------------------------------------------
# 4. ExtensionManager API surface
# ---------------------------------------------------------------------------


def test_extension_manager_has_resolve_path():
    """ExtensionManager must expose resolve_extension_path as a callable."""
    from app.automation.browser_manager import ExtensionManager
    assert hasattr(ExtensionManager, "resolve_extension_path")
    assert callable(getattr(ExtensionManager, "resolve_extension_path"))


def test_extension_manager_sync_api_key_exists():
    """ExtensionManager.sync_api_key must exist for dynamic config injection."""
    from app.automation.browser_manager import ExtensionManager
    assert hasattr(ExtensionManager, "sync_api_key")
    assert callable(getattr(ExtensionManager, "sync_api_key"))


def test_extension_manager_is_extension_configured_exists():
    """ExtensionManager.is_extension_configured must exist for API key check."""
    from app.automation.browser_manager import ExtensionManager
    assert hasattr(ExtensionManager, "is_extension_configured")


def test_extension_manager_resolve_path_returns_path_or_none(tmp_path):
    """resolve_extension_path returns a Path or None - never raises."""
    from app.automation.browser_manager import ExtensionManager
    # A completely invalid path with no manifest should return None (or repo fallback)
    result = ExtensionManager.resolve_extension_path(str(tmp_path / "nonexistent"))
    assert result is None or hasattr(result, "__fspath__")


# ---------------------------------------------------------------------------
# 5. derive_search_counts business logic (state routing)
# ---------------------------------------------------------------------------


def test_derive_search_counts_all_same():
    """All 3 parties same name -> DualSearch=1, TripleSearch=1."""
    from app.automation.session_runner import derive_search_counts
    claim = type("C", (), {
        "claimant_first_name": "John", "claimant_last_name": "Doe",
        "insured_first_name": "John", "insured_last_name": "Doe",
        "driver_first_name": "John", "driver_last_name": "Doe",
    })()
    dual, triple = derive_search_counts(claim)
    assert dual == 1
    assert triple == 1


def test_derive_search_counts_all_different():
    """All 3 parties different -> DualSearch=2, TripleSearch=3."""
    from app.automation.session_runner import derive_search_counts
    claim = type("C", (), {
        "claimant_first_name": "Alice", "claimant_last_name": "Smith",
        "insured_first_name": "Bob", "insured_last_name": "Jones",
        "driver_first_name": "Carol", "driver_last_name": "Brown",
    })()
    dual, triple = derive_search_counts(claim)
    assert dual == 2
    assert triple == 3
