"""Tests for Prompt 04: Master Scraping Engine, CAPTCHA Compliance & QA Fixes.

Covers:
1. Strict unique-name derivation and search counts.
2. Guidewire SuitFiledDate extraction (FilingDate key support + DOL fallback) and 9-digit ClaimNumber prefix.
3. Absence of deprecated fields (Loss Location City/County, Garaging City/State) in ingestion.
4. Exact default portal URLs across all 8 county portals.
5. Auto Queue enabled by default (True).
6. Security block non-blocking architecture, execution logs, and cooldowns.
7. Filing date normalization and fallback logic.
8. AntiCaptcha extension configuration and presence.
"""

import os
import uuid

import pytest

from app.automation.base import (
    SecurityBlockException,
    append_portal_execution_log,
    detect_security_block,
)
from app.core.config import settings
from app.services.excel_parser import TARGET_CLAIM_FIELDS
from app.services.fuzzy_engine import derive_search_counts_fuzzy, generate_unique_names_for_claim
from app.services.guidewire_client import GuidewireClient, format_claim_number
from app.tasks.queue_runner import is_auto_queue_enabled
from app.tasks.scraper_tasks import normalize_court_date


def test_p4_001_unique_name_generation_and_counts():
    """Verify unique name derivation from Insured, Driver, Claimant and search counts."""
    # Scenario A: All different -> 3 unique names
    claim_a = {
        "insured_first_name": "JOHN",
        "insured_last_name": "DOE",
        "driver_first_name": "JANE",
        "driver_last_name": "SMITH",
        "claimant_first_name": "BOB",
        "claimant_last_name": "JONES",
    }
    names_a = generate_unique_names_for_claim(claim_a)
    assert len(names_a) == 3
    full_names_a = [n["full_name"] for n in names_a]
    assert "JOHN DOE" in full_names_a
    assert "JANE SMITH" in full_names_a
    assert "BOB JONES" in full_names_a

    dual_a, triple_a = derive_search_counts_fuzzy(claim_a)
    assert dual_a == 2
    assert triple_a == 3

    # Scenario B: Insured == Driver != Claimant -> 2 unique names
    claim_b = {
        "insured_first_name": "ALICE",
        "insured_last_name": "WONDER",
        "driver_first_name": "ALICE",
        "driver_last_name": "WONDER",
        "claimant_first_name": "CHARLIE",
        "claimant_last_name": "BROWN",
    }
    names_b = generate_unique_names_for_claim(claim_b)
    assert len(names_b) == 2
    full_names_b = [n["full_name"] for n in names_b]
    assert "ALICE WONDER" in full_names_b
    assert "CHARLIE BROWN" in full_names_b

    dual_b, triple_b = derive_search_counts_fuzzy(claim_b)
    assert dual_b == 1
    assert triple_b == 3

    # Scenario C: All same -> 1 unique name
    claim_c = {
        "insured_first_name": "SAM",
        "insured_last_name": "SMITH",
        "driver_first_name": "SAM",
        "driver_last_name": "SMITH",
        "claimant_first_name": "SAM",
        "claimant_last_name": "SMITH",
    }
    names_c = generate_unique_names_for_claim(claim_c)
    assert len(names_c) == 1
    assert names_c[0]["full_name"] == "SAM SMITH"

    dual_c, triple_c = derive_search_counts_fuzzy(claim_c)
    assert dual_c == 1
    assert triple_c == 1


@pytest.mark.asyncio
async def test_p4_002_guidewire_suitfileddate_mapping_and_dol_fallback():
    """Verify Guidewire payload maps FilingDate properly and falls back to claim DOL if empty."""
    client = GuidewireClient(mock_mode=True)

    # 1. Case with PascalCase 'FilingDate'
    res_1 = await client.send_case_update(
        claim_number="123456789",  # 9 digits -> should become 0123456789
        exposure_number="1",
        matched_cases=[
            {
                "CaseNumber": "2024-CA-001",
                "CaseStyle": "SMITH VS DOE",
                "FilingDate": "04/15/2024",
                "CountyWebsite": "https://www.browardclerk.org/Web2",
            }
        ],
    )
    item_1 = res_1["payload_sent"]["CaseItems"][0]
    assert res_1["payload_sent"]["ClaimNumber"] == "0123456789"
    assert item_1["SuitFiledDate"] == "04/15/2024"
    assert item_1["CaseNumber"] == "2024-CA-001"

    # 2. Case with empty filing date falls back to DOL
    res_2 = await client.send_case_update(
        claim_number="0123456789",
        exposure_number="1",
        matched_cases=[
            {
                "CaseNumber": "2023-CC-999",
                "CaseStyle": "STATE VS DOE",
                "FilingDate": "",
                "dol": "02/10/2023",
                "CountyWebsite": "https://hover.hillsclerk.com/html/caseSearch.html",
            }
        ],
    )
    item_2 = res_2["payload_sent"]["CaseItems"][0]
    assert item_2["SuitFiledDate"] == "02/10/2023"

    # 3. 9-digit prefix verification
    assert format_claim_number("123456789") == "0123456789"
    assert format_claim_number("0123456789") == "0123456789"
    assert format_claim_number("987654321") == "0987654321"


def test_p4_003_deprecated_fields_absent_from_ingest_fields():
    """Verify Loss Location City/County and Garaging City/State are removed from TARGET_CLAIM_FIELDS."""
    deprecated_fields = [
        "loss_location_city",
        "loss_location_county",
        "garaging_city",
        "garaging_state",
    ]
    for field in deprecated_fields:
        assert field not in TARGET_CLAIM_FIELDS, f"Field '{field}' should be removed from TARGET_CLAIM_FIELDS"


def test_p4_004_exact_default_portal_urls():
    """Verify all 8 default county portal URLs in settings configuration match prompt specifications."""
    from app.schemas.settings import PortalsSettings

    p_schema = PortalsSettings()
    assert settings.PORTAL_BROWARD_URL == "https://www.browardclerk.org/Web2"
    assert p_schema.broward_url == "https://www.browardclerk.org/Web2"

    assert settings.PORTAL_HILLSBOROUGH_URL == "https://hover.hillsclerk.com/html/caseSearch.html"
    assert p_schema.hillsborough_url == "https://hover.hillsclerk.com/html/caseSearch.html"

    assert settings.PORTAL_MIAMI_URL == "https://onlineservices.miami-dadeclerk.com/civil/"
    assert p_schema.miami_url == "https://onlineservices.miami-dadeclerk.com/civil/"

    assert settings.PORTAL_TRAVIS_URL == "https://odysseypa.traviscountytx.gov/CourtDirectorySearch/"
    assert p_schema.travis_url == "https://odysseypa.traviscountytx.gov/CourtDirectorySearch/"

    assert settings.PORTAL_DALLAS_URL == "https://courtsportal.dallascounty.org/DALLASPROD/"
    assert p_schema.dallas_url == "https://courtsportal.dallascounty.org/DALLASPROD/"

    assert settings.PORTAL_HARRIS_JP_URL == "https://jpwebsite.harriscountytx.gov/Public/CivilSearch.aspx"
    assert p_schema.harris_jp_url == "https://jpwebsite.harriscountytx.gov/Public/CivilSearch.aspx"

    assert (
        settings.PORTAL_HARRIS_CCLERK_URL
        == "https://www.cclerk.hctx.net/applications/websearch/courtsearch.aspx?CaseType=Civil"
    )
    assert (
        p_schema.harris_cclerk_url
        == "https://www.cclerk.hctx.net/applications/websearch/courtsearch.aspx?CaseType=Civil"
    )

    assert (
        settings.PORTAL_HARRIS_DISTRICT_URL
        == "https://www.hcdistrictclerk.com/edocs/public/CaseDetails.aspx"
    )
    assert (
        p_schema.harris_district_url
        == "https://www.hcdistrictclerk.com/edocs/public/CaseDetails.aspx"
    )


def test_p4_005_auto_queue_enabled_by_default(mocker):
    """Verify Auto Queue is enabled by default (True) when Redis uninitialized."""
    mock_redis = mocker.MagicMock()
    mock_redis.get.return_value = None
    mocker.patch("app.tasks.queue_runner.get_redis_client", return_value=mock_redis)
    assert is_auto_queue_enabled() is True
    mock_redis.set.assert_called_with("uaic:queue:auto_mode", "true")


def test_p4_006_security_block_and_cooldown_behavior():
    """Verify security block detection, cooldown parameters, and logging."""
    # 1. HTTP 429 detection
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(status_code=429, portal_key="dallas")
    assert "Rate limit exceeded" in str(exc_info.value)
    assert exc_info.value.cooldown_seconds == 300

    # 2. Cloudflare challenge detection
    cf_html = "<html><head><title>Just a moment...</title></head><body><div class='cf-challenge'>Checking browser</div></body></html>"
    with pytest.raises(SecurityBlockException) as exc_info_cf:
        detect_security_block(status_code=403, html_text=cf_html, portal_key="miami")
    assert "Access blocked" in str(exc_info_cf.value) or "challenge" in str(exc_info_cf.value)

    # 3. Execution log appending
    test_claim_id = str(uuid.uuid4())
    append_portal_execution_log(
        claim_id=test_claim_id,
        portal_key="broward",
        message="Test execution log entry for Prompt 04 compliance",
        level="INFO",
    )

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    expected_log_path = os.path.join(backend_dir, "logs", test_claim_id, "broward", "execution.log")
    assert os.path.exists(expected_log_path)
    with open(expected_log_path, encoding="utf-8") as f:
        content = f.read()
    assert "Test execution log entry for Prompt 04 compliance" in content


def test_p4_007_filing_date_normalization():
    """Verify court date normalization handles various formats accurately."""
    assert normalize_court_date("04/15/2023") == "04/15/2023"
    assert normalize_court_date("2023-04-15") == "04/15/2023"
    assert normalize_court_date("") == ""
    assert normalize_court_date(None) is None


from app.automation.browser_manager import ChromeSession
from app.automation.session_runner import resolve_extension_dir
from app.schemas.settings import get_default_extension_dir


def test_p4_008_anticaptcha_extension_and_profile_pinning(tmp_path):
    """Verify Anti-Captcha extension directory resolution and profile toolbar pinning."""
    default_dir = get_default_extension_dir()
    assert default_dir is not None
    resolved = resolve_extension_dir(default_dir)
    assert resolved is not None
    assert os.path.exists(resolved)

    # Test profile configuration and toolbar pinning
    profile_dir = tmp_path / "browser_profile"
    result_dir = ChromeSession.configure_and_pin_profile(
        profile_dir=profile_dir,
        api_key="test_api_key_456",
    )
    assert result_dir.is_dir()
    pref_file = result_dir / "Default" / "Preferences"
    assert pref_file.is_file()
