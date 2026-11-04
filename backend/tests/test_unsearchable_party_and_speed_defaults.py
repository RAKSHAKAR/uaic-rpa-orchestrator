from app.schemas.settings import SystemSettings
from app.services.fuzzy_engine import (
    DEFAULT_UNSEARCHABLE_PARTY_PATTERNS,
    generate_unique_names_for_claim,
    is_unsearchable_party,
)
from app.services.settings_service import _decode_row, get_default_settings


def test_unsearchable_party_patterns_match_placeholders():
    """Verify placeholder, municipal, fleet, and corporate entities are recognized as unsearchable."""
    unsearchable_cases = [
        ("UNKNOWN", "IV DRIVER"),
        ("UNKNOWN", "P1 PROPERTY OWNER"),
        ("", "UNKNOWN DRIVER"),
        ("NO", "NAME PROVIDED"),
        ("N/A", ""),
        ("NOT", "AVAILABLE"),
        ("MIAMI DADE", "POLICE DEPARTMENT"),
        ("CITY OF", "HIALEAH"),
        ("COUNTY OF", "DALLAS"),
        ("FL", "DEPT OF TRANSPORTATION"),
        ("METROPOLITAN", "TRANSIT"),
        ("ABC", "TOWING LLC"),
        ("ACE", "RENTAL CAR INC"),
        ("LABRADOR & SON", "FOOD PRODUCTS INC."),
        ("McKenneys", "Inc."),
        ("Threaded", "Fasteners, Inc."),
        ("", "Enterprise"),
        ("", "Penske Truck Leasing Co"),
        ("PGM", "Transportation"),
        ("JOHN", "DOE"),
        ("JANE", "DOE"),
        ("HIT", "AND RUN"),
        ("MIAMI", "FIRE RESCUE"),
        ("GEICO", "INSURANCE"),
        ("MEMORIAL", "HOSPITAL"),
        ("TOWN OF", "PALM BEACH"),
    ]
    for fn, ln in unsearchable_cases:
        assert is_unsearchable_party(fn, ln), f"Expected ({fn}, {ln}) to be flagged as unsearchable"


def test_unsearchable_party_patterns_preserve_real_names():
    """Verify legitimate person names are never falsely flagged as unsearchable."""
    legitimate_names = [
        ("DIANA", "PRINCE"),
        ("BRHAYAN", "RINCON GUIZA"),
        ("LUISA", "VALENCIA RINCON"),
        ("CARLOS", "SANTANA"),
        ("MARIA", "FERNANDEZ"),
        ("CORNJHIA", "DUNN"),
    ]
    for fn, ln in legitimate_names:
        assert not is_unsearchable_party(fn, ln), (
            f"Expected legitimate name ({fn}, {ln}) NOT to be flagged as unsearchable"
        )


def test_clean_case_style_legal_noise_patterns():
    """Verify legal boilerplate and fiduciary designations are cleanly stripped from case styles."""
    from app.services.fuzzy_engine import DEFAULT_CLEAN_CASE_STYLE_PATTERNS, clean_case_style

    raw_style = (
        "JOHN DOE, AS PERSONAL REPRESENTATIVE OF THE ESTATE OF JANE DOE, DECEASED VS PROGRESSIVE"
    )
    # Noise stripping requires explicit patterns — callers responsible for passing them.
    cleaned = clean_case_style(raw_style, noise_patterns=DEFAULT_CLEAN_CASE_STYLE_PATTERNS)
    assert "PERSONAL REPRESENTATIVE" not in cleaned
    assert "ESTATE OF" not in cleaned
    assert "DECEASED" not in cleaned
    assert "JOHN DOE" in cleaned
    assert "PROGRESSIVE" in cleaned


def test_generate_unique_names_filters_unsearchable_parties():
    """Verify generate_unique_names_for_claim skips unsearchable entities while keeping real parties."""
    claim = {
        "insured_first_name": "CORNJHIA",
        "insured_last_name": "DUNN",
        "driver_first_name": "MIAMI DADE",
        "driver_last_name": "POLICE DEPT",
        "claimant_first_name": "UNKNOWN",
        "claimant_last_name": "IV DRIVER",
    }

    targets = generate_unique_names_for_claim(
        claim=claim,
        noise_patterns=[],
        unsearchable_patterns=DEFAULT_UNSEARCHABLE_PARTY_PATTERNS,
    )
    assert len(targets) == 1
    assert targets[0]["first_name"] == "CORNJHIA"
    assert targets[0]["last_name"] == "DUNN"


def test_generate_unique_names_all_unsearchable_returns_empty():
    """Verify generate_unique_names_for_claim returns empty list when all parties are placeholders."""
    claim = {
        "insured_first_name": "NOT",
        "insured_last_name": "PROVIDED",
        "driver_first_name": "N/A",
        "driver_last_name": "N/A",
        "claimant_first_name": "UNKNOWN",
        "claimant_last_name": "DRIVER",
    }

    targets = generate_unique_names_for_claim(
        claim=claim,
        unsearchable_patterns=DEFAULT_UNSEARCHABLE_PARTY_PATTERNS,
    )
    assert targets == []


def test_default_settings_fast_speed_values():
    """Verify production default settings are optimized for high speed and zero timeouts."""
    defaults = get_default_settings()

    # Automation speed defaults
    assert defaults.automation.captcha_wait_seconds in (45, 120)
    assert defaults.automation.page_timeout_seconds in (35, 180)
    assert defaults.automation.reload_backoff_seconds in (2, 5)
    assert defaults.automation.action_pacing_ms in (50, 250)

    # Queue timeout default
    assert defaults.queue.claim_timeout_minutes == 30

    # Matcher unsearchable patterns
    assert len(defaults.matcher.unsearchable_party_patterns) >= 50
    assert len(defaults.matcher.clean_party_name_patterns) >= 30
    assert len(defaults.matcher.clean_case_style_patterns) >= 20


def test_settings_decode_row_auto_migrates_legacy_values():
    """Verify _decode_row automatically migrates legacy slow defaults to fast settings."""
    legacy_doc = {
        "automation": {
            "captcha_wait_seconds": 120,
            "page_timeout_seconds": 60,
            "reload_backoff_seconds": 5,
            "action_pacing_ms": 100,
        },
        "queue": {
            "max_task_retries": 3,
        },
        "matcher": {
            "auto_match_threshold": 0.6,
        },
    }

    settings = _decode_row(legacy_doc)
    assert isinstance(settings, SystemSettings)

    # Legacy 120s must be upgraded to 45s
    assert settings.automation.captcha_wait_seconds == 45
    assert settings.automation.page_timeout_seconds == 35
    assert settings.automation.reload_backoff_seconds == 2
    assert settings.automation.action_pacing_ms == 50

    # Missing claim_timeout_minutes must be set to 30
    assert settings.queue.claim_timeout_minutes == 30

    # Missing unsearchable_party_patterns must be populated
    assert len(settings.matcher.unsearchable_party_patterns) >= 50
    assert len(settings.matcher.clean_case_style_patterns) >= 20
