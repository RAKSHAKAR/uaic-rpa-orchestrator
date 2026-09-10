"""Tests verifying complete system alignment with the dynamic settings configuration."""

import pytest

from app.api.v1.endpoints.claims import _build_bot_details
from app.models.claim import BotStatusEnum, ClaimRecord
from app.services.fuzzy_engine import (
    calculate_match_score,
    clean_case_style,
    clean_party_name,
    evaluate_case_against_parties,
)
from app.services.settings_service import (
    get_system_settings_async,
    reset_system_settings_async,
    save_system_settings_async,
)


def test_scorer_algorithm_selection():
    """Verify that different scorer algorithms produce scores matching their RapidFuzz semantics."""
    party = "John Doe"
    case_caption = "JOHN DOE VS STATE FARM"

    # token_set_ratio should give 1.0 (100%) for exact token set match
    score_token_set = calculate_match_score(party, case_caption, scorer_algorithm="token_set_ratio")
    assert score_token_set == 1.0

    # partial_ratio should give 1.0 (100%) since 'john doe' is a substring of the caption
    score_partial = calculate_match_score(party, case_caption, scorer_algorithm="partial_ratio")
    assert score_partial == 1.0

    # ratio computes Levenshtein distance directly over unequal lengths
    score_ratio = calculate_match_score(party, case_caption, scorer_algorithm="ratio")
    # 'john doe' (8 chars) vs 'john doe vs state farm' (22 chars) -> 2 * 8 / (8 + 22) = 16/30 ~= 0.5333
    assert 0.40 <= score_ratio <= 0.65

    # token_sort_ratio default with composite matching
    score_token_sort = calculate_match_score(party, case_caption, scorer_algorithm="token_sort_ratio")
    assert score_token_sort >= 0.85


def test_noise_pattern_stripping():
    """Verify that corporate noise patterns are stripped from party names and case styles."""
    noise_words = ["LLC", "INC", "CORP", "ET AL", "P.A.", "D/B/A", "A/A/O"]

    # Party name with LLC
    cleaned_party = clean_party_name("Apex Recovery", "LLC", noise_patterns=noise_words)
    assert cleaned_party == "Apex Recovery"

    # Party name with ET AL
    cleaned_et_al = clean_party_name("John", "Doe et al.", noise_patterns=noise_words)
    assert cleaned_et_al == "John Doe"

    # Case style with P.A. and INC
    case_style = "JOHN DOE ET AL VS SMITH CHIROPRACTIC CLINIC, P.A. AND GEICO INC."
    cleaned_style = clean_case_style(case_style, noise_patterns=noise_words)
    assert "ET AL" not in cleaned_style
    assert "P.A." not in cleaned_style
    assert "INC" not in cleaned_style
    assert "JOHN DOE VS SMITH CHIROPRACTIC CLINIC AND GEICO" in cleaned_style


def test_evaluate_case_against_parties_with_settings():
    """Verify evaluate_case_against_parties applies configured algorithm and noise stripping."""
    case = {
        "CaseNumber": "2024-CA-001234",
        "CaseStyle": "JOHN DOE ET AL VS TRAVELERS PROPERTY CASUALTY CORP",
        "CountyWebsite": "https://www.browardclerk.org/Web2/",
        "SuitFiledDate": "2024-03-15",
    }
    noise_patterns = ["ET AL", "CORP", "LLC"]

    evals = evaluate_case_against_parties(
        case=case,
        claimant_name="John Doe",
        insured_name="Bob Builder",
        driver_name="",
        threshold=0.60,
        borderline_threshold=0.40,
        scorer_algorithm="token_set_ratio",
        noise_patterns=noise_patterns,
    )

    claimant_eval = next((e for e in evals if e["party_name"] == "John Doe"), None)
    assert claimant_eval is not None
    assert claimant_eval["is_match"] is True
    assert claimant_eval["similarity_score"] >= 0.90
    assert "ET AL" not in claimant_eval["case_style"]


@pytest.mark.asyncio
async def test_claims_bot_details_uses_configured_portal_urls():
    """Verify that _build_bot_details reflects custom portal URLs from dynamic settings."""
    settings = await get_system_settings_async()
    original_broward_url = settings.portals.broward_url

    # Update Broward URL dynamically
    settings.portals.broward_url = "https://custom-portal.browardclerk.org/TestWeb"
    await save_system_settings_async(settings)

    try:
        mock_claim = ClaimRecord(
            id="test-claim-uuid-99",
            claim_number="0100999999",
            fl_website_broward="Yes",
            fl_botstatus_broward=BotStatusEnum.COMPLETED,
            fl_jsonbody_broward=[],
        )
        bot_details = _build_bot_details(mock_claim)
        broward_bot = next((b for b in bot_details if "Broward" in b.name), None)
        assert broward_bot is not None
        assert broward_bot.website_url == "https://custom-portal.browardclerk.org/TestWeb"
    finally:
        # Restore settings
        settings.portals.broward_url = original_broward_url
        await save_system_settings_async(settings)


@pytest.mark.asyncio
async def test_settings_save_and_retrieve_persistence():
    """Verify settings can be saved and reloaded via settings_service without loss of fidelity."""
    current = await get_system_settings_async()
    current.matcher.auto_match_threshold = 0.72
    current.integration.auto_push_on_match = False
    current.queue.batch_chunk_size = 50

    saved = await save_system_settings_async(current)
    assert saved.matcher.auto_match_threshold == 0.72
    assert saved.integration.auto_push_on_match is False
    assert saved.queue.batch_chunk_size == 50

    # Reload from storage
    reloaded = await get_system_settings_async()
    assert reloaded.matcher.auto_match_threshold == 0.72
    assert reloaded.integration.auto_push_on_match is False
    assert reloaded.queue.batch_chunk_size == 50

    # Reset back to defaults
    await reset_system_settings_async()
    reset_settings = await get_system_settings_async()
    assert reset_settings.matcher.auto_match_threshold == 0.60
    assert reset_settings.integration.auto_push_on_match is True


def test_default_windows_chrome_detection():
    """Verify get_default_chrome_binary() accurately checks Windows directories or returns None cleanly."""
    from app.schemas.settings import get_default_chrome_binary
    chrome_bin = get_default_chrome_binary()
    # On machines with Chrome installed, it returns a valid chrome.exe path; otherwise None
    if chrome_bin:
        from pathlib import Path
        assert isinstance(chrome_bin, str)
        assert Path(chrome_bin).name.lower() == "chrome.exe"
        assert Path(chrome_bin).exists()


def test_default_root_extension_detection():
    """Verify get_default_extension_dir() returns relative path and ExtensionManager resolves it dynamically."""
    from pathlib import Path

    from app.automation.browser_manager import ExtensionManager
    from app.schemas.settings import get_default_extension_dir

    ext_dir = get_default_extension_dir()
    assert ext_dir is not None
    assert "anticaptcha-plugin_v0.83" in ext_dir
    assert ext_dir.startswith(".\\") or not Path(ext_dir).is_absolute()

    resolved_path = ExtensionManager.resolve_extension_path(ext_dir)
    assert resolved_path is not None
    assert resolved_path.exists()
    assert (resolved_path / "manifest.json").exists()


def test_engine_user_agents():
    """Verify engine-specific User-Agent resolution."""
    from app.schemas.settings import (
        CHROME_USER_AGENT,
        CHROMIUM_USER_AGENT,
        MSEDGE_USER_AGENT,
        get_engine_user_agent,
    )

    assert get_engine_user_agent("chromium") == CHROMIUM_USER_AGENT
    assert get_engine_user_agent("chrome") == CHROME_USER_AGENT
    assert get_engine_user_agent("msedge") == MSEDGE_USER_AGENT
    assert "Edg/" in MSEDGE_USER_AGENT
    assert "Edg/" not in CHROME_USER_AGENT


@pytest.mark.asyncio
async def test_browser_engine_setting_persistence():
    """Verify browser_engine setting initializes to 'chromium', accepts 'chrome'/'msedge', and persists."""
    settings = await get_system_settings_async()
    assert settings.automation.browser_engine in ["chromium", "chrome", "msedge"]

    # Update to msedge
    settings.automation.browser_engine = "msedge"
    saved = await save_system_settings_async(settings)
    assert saved.automation.browser_engine == "msedge"

    reloaded = await get_system_settings_async()
    assert reloaded.automation.browser_engine == "msedge"

    # Reset to default
    await reset_system_settings_async()
    reset_settings = await get_system_settings_async()
    assert reset_settings.automation.browser_engine == "chromium"


@pytest.mark.asyncio
async def test_branding_settings_persistence():
    """Verify branding settings default values, dynamic persistence, and reset behavior."""
    settings = await get_system_settings_async()
    assert settings.branding.app_title == "UAIC Orchestrator"
    assert settings.branding.app_subtitle == "RPA & Match Engine"
    assert settings.branding.app_logo_url == "/icon.png"
    assert settings.branding.badge_letter == "U"

    # Update branding settings
    settings.branding.app_title = "Custom Enterprise Orchestrator"
    settings.branding.app_subtitle = "Automated Court Discovery"
    settings.branding.app_logo_url = "/custom-logo.png"
    settings.branding.badge_letter = "C"

    saved = await save_system_settings_async(settings)
    assert saved.branding.app_title == "Custom Enterprise Orchestrator"
    assert saved.branding.app_logo_url == "/custom-logo.png"

    # Verify reloading from persistence
    reloaded = await get_system_settings_async()
    assert reloaded.branding.app_title == "Custom Enterprise Orchestrator"
    assert reloaded.branding.app_subtitle == "Automated Court Discovery"
    assert reloaded.branding.app_logo_url == "/custom-logo.png"
    assert reloaded.branding.badge_letter == "C"

    # Reset back to defaults
    await reset_system_settings_async()
    reset_settings = await get_system_settings_async()
    assert reset_settings.branding.app_title == "UAIC Orchestrator"
    assert reset_settings.branding.app_subtitle == "RPA & Match Engine"
    assert reset_settings.branding.app_logo_url == "/icon.png"
    assert reset_settings.branding.badge_letter == "U"


@pytest.mark.asyncio
async def test_branding_theme_palettes_persistence():
    """Verify light_palette and dark_palette default values, independent custom color persistence, and reset."""
    settings = await get_system_settings_async()
    assert settings.branding.light_palette.primary == "#4f46e5"
    assert settings.branding.light_palette.background == "#f8fafc"
    assert settings.branding.light_palette.text == "#0f172a"
    assert settings.branding.dark_palette.primary == "#6366f1"
    assert settings.branding.dark_palette.background == "#020617"
    assert settings.branding.dark_palette.text == "#f8fafc"

    # Modify light and dark palettes independently
    settings.branding.light_palette.primary = "#2563eb"
    settings.branding.light_palette.background = "#f1f5f9"
    settings.branding.dark_palette.primary = "#38bdf8"
    settings.branding.dark_palette.background = "#050814"

    saved = await save_system_settings_async(settings)
    assert saved.branding.light_palette.primary == "#2563eb"
    assert saved.branding.light_palette.background == "#f1f5f9"
    assert saved.branding.dark_palette.primary == "#38bdf8"
    assert saved.branding.dark_palette.background == "#050814"

    # Verify reloading from storage
    reloaded = await get_system_settings_async()
    assert reloaded.branding.light_palette.primary == "#2563eb"
    assert reloaded.branding.light_palette.background == "#f1f5f9"
    assert reloaded.branding.dark_palette.primary == "#38bdf8"
    assert reloaded.branding.dark_palette.background == "#050814"

    # Reset back to defaults
    await reset_system_settings_async()
    reset_settings = await get_system_settings_async()
    assert reset_settings.branding.light_palette.primary == "#4f46e5"
    assert reset_settings.branding.light_palette.background == "#f8fafc"
    assert reset_settings.branding.dark_palette.primary == "#6366f1"
    assert reset_settings.branding.dark_palette.background == "#020617"



@pytest.mark.asyncio
async def test_upload_logo_endpoint_success():
    """Verify uploading a valid PNG logo returns 200, valid URL, and can be retrieved."""
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        files = {"file": ("my_custom_logo.png", fake_png, "image/png")}
        response = await client.post("/api/v1/settings/upload-logo", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["url"].startswith("/api/v1/settings/logo/logo_my_custom_logo_")
        assert data["url"].endswith(".png")
        assert data["filename"].endswith(".png")

        # Verify downloading via fallback route
        get_res = await client.get(f"/api/v1/settings/logo/{data['filename']}")
        assert get_res.status_code == 200
        assert get_res.content == fake_png


@pytest.mark.asyncio
async def test_upload_logo_endpoint_invalid_extension():
    """Verify uploading unsupported file format returns 400."""
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("malicious.exe", b"MZ\x90\x00", "application/octet-stream")}
        response = await client.post("/api/v1/settings/upload-logo", files=files)
        assert response.status_code == 400
        assert "Unsupported file format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_logo_endpoint_oversize_limit():
    """Verify uploading file exceeding 2MB limit returns 400."""
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        oversize_data = b"0" * (2 * 1024 * 1024 + 1024)
        files = {"file": ("huge_image.png", oversize_data, "image/png")}
        response = await client.post("/api/v1/settings/upload-logo", files=files)
        assert response.status_code == 400
        assert "File exceeds maximum allowed size" in response.json()["detail"]


