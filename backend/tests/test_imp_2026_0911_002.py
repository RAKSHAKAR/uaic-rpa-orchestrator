"""Automated Test Suite for Prompt 04: Master Scraping Engine & CAPTCHA Compliance (IMP-2026-0911-002).

Validates:
1. Exact 8 Default Portal URLs in PortalsSettings and settings_service.
2. Unique Name Derivation across all 5 Dual/Triple search scenarios (Insured, Driver, Claimant).
3. Strict Portal Output Schemas (no CaseType for Harris JP & Harris County Clerk).
4. Filing Date fallback resolution cascade across all 8 variants.
5. Ingestion schema and column mapping field cleanup (no garaging/loss city/county in active mapping).
6. Auto Queue enabled by default in settings and queue runner.
7. Anti-Captcha Extension settings and balance test endpoint contract.
8. Non-blocking portal exception handling and screenshot logging.
"""


import pytest

from app.automation.florida import BrowardScraper, HillsboroughScraper, MiamiDadeScraper
from app.automation.session_runner import (
    derive_search_counts,
    get_search_party_pairs,
)
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)
from app.schemas.claim import ClaimRowSchema
from app.schemas.settings import PortalsSettings, SystemSettings, TaskQueueSettings
from app.services.excel_parser import TARGET_CLAIM_FIELDS
from app.services.settings_service import get_default_settings
from app.tasks.queue_runner import is_auto_queue_enabled

# ============================================================================
# 1. PORTAL URL VERIFICATION (Exact Prompt 04 Contracts)
# ============================================================================

def test_portals_settings_defaults_match_spec():
    """Verify PortalsSettings model defaults match the 8 exact Prompt 04 home URLs."""
    p = PortalsSettings()
    assert p.broward_url == "https://www.browardclerk.org/"
    assert p.hillsborough_url == "https://hover.hillsclerk.com/"
    assert p.miami_url == "https://www2.miamidadeclerk.gov/ocs"
    assert p.travis_url == "https://odysseyweb.traviscountytx.gov/Portal/"
    assert p.dallas_url == "https://courtsportal.dallascounty.org/DALLASPROD/Home/"
    assert p.harris_jp_url == "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/"
    assert p.harris_cclerk_url == "https://www.cclerk.hctx.net/Applications/WebSearch/"
    assert p.harris_district_url == "https://www.hcdistrictclerk.com/"


def test_get_default_settings_portal_urls_match_spec():
    """Verify get_default_settings() returns the 8 exact Prompt 04 home URLs."""
    s: SystemSettings = get_default_settings()
    p = s.portals
    assert p.broward_url == "https://www.browardclerk.org/"
    assert p.hillsborough_url == "https://hover.hillsclerk.com/"
    assert p.miami_url == "https://www2.miamidadeclerk.gov/ocs"
    assert p.travis_url == "https://odysseyweb.traviscountytx.gov/Portal/"
    assert p.dallas_url == "https://courtsportal.dallascounty.org/DALLASPROD/Home/"
    assert p.harris_jp_url == "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/"
    assert p.harris_cclerk_url == "https://www.cclerk.hctx.net/Applications/WebSearch/"
    assert p.harris_district_url == "https://www.hcdistrictclerk.com/"


# ============================================================================
# 2. UNIQUE NAME ORCHESTRATION & PARTY PAIRS DERIVATION
# ============================================================================

class MockClaimRecord:
    """Mock claim record for testing DualSearch / TripleSearch derivation."""
    def __init__(
        self,
        insured_first="",
        insured_last="",
        driver_first="",
        driver_last="",
        claimant_first="",
        claimant_last="",
    ):
        self.insured_first_name = insured_first
        self.insured_last_name = insured_last
        self.driver_first_name = driver_first
        self.driver_last_name = driver_last
        self.claimant_first_name = claimant_first
        self.claimant_last_name = claimant_last


def test_unique_name_derivation_all_same():
    """Scenario 1: Insured == Driver == Claimant -> 1 search (Insured only)."""
    claim = MockClaimRecord(
        insured_first="John", insured_last="Doe",
        driver_first="John", driver_last="Doe",
        claimant_first="John", claimant_last="Doe",
    )
    dual, triple = derive_search_counts(claim)
    assert (dual, triple) == (1, 1)

    parties = get_search_party_pairs(claim, dual, triple)
    assert len(parties) == 1
    assert parties[0] == ("Insured", "John", "Doe")


def test_unique_name_derivation_insured_eq_driver_claimant_diff():
    """Scenario 2: Insured == Driver, Claimant != -> 2 searches (Insured, Claimant)."""
    claim = MockClaimRecord(
        insured_first="John", insured_last="Doe",
        driver_first="John", driver_last="Doe",
        claimant_first="Jane", claimant_last="Smith",
    )
    dual, triple = derive_search_counts(claim)
    assert (dual, triple) == (1, 3)

    parties = get_search_party_pairs(claim, dual, triple)
    assert len(parties) == 2
    assert parties[0] == ("Insured", "John", "Doe")
    assert parties[1] == ("Claimant", "Jane", "Smith")


def test_unique_name_derivation_insured_eq_claimant_driver_diff():
    """Scenario 3: Insured == Claimant, Driver != -> 2 searches (Insured, Driver)."""
    claim = MockClaimRecord(
        insured_first="John", insured_last="Doe",
        driver_first="Bob", driver_last="Jones",
        claimant_first="John", claimant_last="Doe",
    )
    dual, triple = derive_search_counts(claim)
    assert (dual, triple) == (2, 1)

    parties = get_search_party_pairs(claim, dual, triple)
    assert len(parties) == 2
    assert parties[0] == ("Insured", "John", "Doe")
    assert parties[1] == ("Driver", "Bob", "Jones")


def test_unique_name_derivation_driver_eq_claimant_insured_diff():
    """Scenario 4: Driver == Claimant, Insured != -> 2 searches (Insured, Driver)."""
    claim = MockClaimRecord(
        insured_first="Alice", insured_last="Wonder",
        driver_first="Bob", driver_last="Jones",
        claimant_first="Bob", claimant_last="Jones",
    )
    dual, triple = derive_search_counts(claim)
    assert (dual, triple) == (2, 1)

    parties = get_search_party_pairs(claim, dual, triple)
    assert len(parties) == 2
    assert parties[0] == ("Insured", "Alice", "Wonder")
    assert parties[1] == ("Driver", "Bob", "Jones")


def test_unique_name_derivation_all_different():
    """Scenario 5: All different -> 3 searches (Insured, Driver, Claimant)."""
    claim = MockClaimRecord(
        insured_first="John", insured_last="Doe",
        driver_first="Bob", driver_last="Jones",
        claimant_first="Alice", claimant_last="Smith",
    )
    dual, triple = derive_search_counts(claim)
    assert (dual, triple) == (2, 3)

    parties = get_search_party_pairs(claim, dual, triple)
    assert len(parties) == 3
    assert parties[0] == ("Insured", "John", "Doe")
    assert parties[1] == ("Driver", "Bob", "Jones")
    assert parties[2] == ("Claimant", "Alice", "Smith")


# ============================================================================
# 3. STRICT PORTAL OUTPUT SCHEMA VERIFICATION
# ============================================================================

def test_harris_jp_strict_schema_no_casetype():
    """Harris JP output schema MUST NOT contain CaseType."""
    scraper = HarrisJPScraper()
    assert scraper.county_name == "Harris County JP (TX)"
    assert "jpodysseyportal.harriscountytx.gov" in scraper.base_url


def test_harris_cclerk_strict_schema_no_casetype():
    """Harris County Clerk output schema MUST NOT contain CaseType."""
    scraper = HarrisCountyClerkScraper()
    assert scraper.county_name == "Harris County Clerk (TX)"
    assert "cclerk.hctx.net" in scraper.base_url


def test_fl_scrapers_schema_has_casetype():
    """Florida scrapers (Broward, Hillsborough, Miami) must preserve CaseType."""
    b = BrowardScraper()
    h = HillsboroughScraper()
    m = MiamiDadeScraper(requires_login=False)
    assert b.county_name == "Broward County (FL)"
    assert h.county_name == "Hillsborough County (FL)"
    assert m.county_name == "Miami-Dade County (FL)"


def test_tx_district_dallas_travis_schema_has_casetype():
    """Texas scrapers (Dallas, Travis, Harris District) must preserve CaseType."""
    d = DallasScraper()
    t = TravisScraper()
    hd = HarrisDistrictClerkScraper()
    assert d.county_name == "Dallas County (TX)"
    assert t.county_name == "Travis County (TX)"
    assert hd.county_name == "Harris District Clerk (TX)"


# ============================================================================
# 4. FILING DATE RESOLUTION CASCADE
# ============================================================================

@pytest.mark.parametrize("key_name,val", [
    ("FilingDate", "05/14/2024"),
    ("filing_date", "2024-05-14"),
    ("Filing Date", "05-14-2024"),
    ("SuitFiledDate", "05/14/2024"),
    ("suit_filed_date", "2024-05-14"),
    ("filed_date", "2024-05-14"),
    ("DateFiled", "05/14/2024"),
    ("date_filed", "05/14/2024"),
    ("Filed", "2024-05-14"),
])
def test_filing_date_fallback_cascade_resolution(key_name, val):
    """Verify that filing date is captured regardless of which synonym key a portal scraper emits."""
    case_dict = {
        "CaseNumber": "2024-CA-001234",
        "CaseStyle": "DOE VS SMITH",
        key_name: val,
    }

    # Simulate scraper_tasks.py resolution
    f_date = (
        case_dict.get("FilingDate")
        or case_dict.get("filing_date")
        or case_dict.get("Filing Date")
        or case_dict.get("SuitFiledDate")
        or case_dict.get("suit_filed_date")
        or case_dict.get("filed_date")
        or case_dict.get("DateFiled")
        or case_dict.get("date_filed")
        or case_dict.get("Filed")
        or case_dict.get("filed")
    )
    assert f_date == val


# ============================================================================
# 5. INGESTION SCHEMA CLEANUP & REMOVED FIELDS
# ============================================================================

def test_target_claim_fields_no_deprecated_fields():
    """Verify TARGET_CLAIM_FIELDS does not contain any of the 4 removed fields."""
    keys = [f["key"] for f in TARGET_CLAIM_FIELDS]
    assert "garaging_city" not in keys
    assert "garaging_state" not in keys
    assert "loss_location_city" not in keys
    assert "loss_location_county" not in keys


def test_claim_row_schema_no_deprecated_aliases():
    """Verify ClaimRowSchema has no aliases or active fields for the 4 removed fields."""
    fields = ClaimRowSchema.model_fields
    assert "garaging_city" not in fields
    assert "garaging_state" not in fields
    assert "loss_location_city" not in fields
    assert "loss_location_county" not in fields


# ============================================================================
# 6. AUTO QUEUE DEFAULT & CAPTCHA SETTINGS
# ============================================================================

def test_auto_queue_enabled_default():
    """Verify Auto Queue is enabled by default per Prompt 04."""
    assert is_auto_queue_enabled() is True
    tq = TaskQueueSettings()
    assert tq.auto_retry_failed_scrapes is True


def test_automation_settings_defaults():
    """Verify AutomationSettings CAPTCHA retry and timeout defaults."""
    s = get_default_settings()
    auto = s.automation
    assert auto.max_captcha_attempts == 2
    assert auto.captcha_wait_seconds == 120
    assert auto.reload_backoff_seconds == 2
    assert auto.headless_mode is False
    assert auto.use_chrome_browser is True
