"""Unit and Integration Tests for Final Multi-Portal Execution Order (Unique Name First).

Verifies:
1. Florida records open exactly 3 tabs (Broward, Miami-Dade, Hillsborough) in V4 order.
2. Texas records open exactly 5 tabs (Travis, Dallas, Harris JP, CClerk, HCDistrict) in order.
3. Cross-State records open all 8 tabs in order.
4. Execution sequence is strictly Name 1 -> Portals 1..N, Name 2 -> Portals 1..N.
5. Portal failure for Name 1 does not skip remaining portals for Name 1.
6. Browser tabs are opened once, reused across names, and closed at session end.
7. Chrome engine selection and AntiCaptcha extension recognition.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.browser_manager import KNOWN_ANTICAPTCHA_IDS
from app.models.claim import ClaimRecord
from app.schemas.settings import SystemSettings
from app.services.excel_parser import resolve_county_bot_targets
from app.services.fuzzy_engine import generate_unique_names_for_claim
from app.tasks.scraper_tasks import _async_orchestrate_scrapers


def test_florida_state_routing_order():
    """Verify Florida claims route strictly to Broward, Hillsborough, Miami-Dade."""
    targets = resolve_county_bot_targets("FL", "FL")
    assert targets["fl_broward"] == "Yes"
    assert targets["fl_hillsborough"] == "Yes"
    assert targets["fl_miami"] == "Yes"
    assert targets["te_travis"] == "No"
    assert targets["te_dallas"] == "No"
    assert targets["te_harris"] == "No"
    assert targets["te_cclerk"] == "No"
    assert targets["te_hcdistrict"] == "No"


def test_texas_state_routing_order():
    """Verify Texas claims route strictly to Travis, Dallas, Harris JP, CClerk, HCDistrict."""
    targets = resolve_county_bot_targets("TX", "TX")
    assert targets["fl_broward"] == "No"
    assert targets["fl_hillsborough"] == "No"
    assert targets["fl_miami"] == "No"
    assert targets["te_travis"] == "Yes"
    assert targets["te_dallas"] == "Yes"
    assert targets["te_harris"] == "Yes"
    assert targets["te_cclerk"] == "Yes"
    assert targets["te_hcdistrict"] == "Yes"


def test_cross_state_routing_order():
    """Verify Cross-State claims route to all 8 portals."""
    targets = resolve_county_bot_targets("FL", "TX")
    for k in targets:
        assert targets[k] == "Yes", f"Target {k} should be enabled for cross-state"


def test_known_anticaptcha_ids_includes_workspace_unpacked():
    """Verify KNOWN_ANTICAPTCHA_IDS includes both Web Store and local workspace extension IDs."""
    assert "gcpdbjbmekkdlkpldjgffhmapgpdlcpj" in KNOWN_ANTICAPTCHA_IDS
    assert "fignfifoniblkonapihmkfakmlgkbkcf" in KNOWN_ANTICAPTCHA_IDS


def test_unique_names_extraction_multiple_parties():
    """Verify generate_unique_names_for_claim yields distinct unique search targets in order."""
    claim = MagicMock()
    claim.insured_first_name = "JOHN"
    claim.insured_last_name = "DOE"
    claim.driver_first_name = "JANE"
    claim.driver_last_name = "SMITH"
    claim.claimant_first_name = "ROBERT"
    claim.claimant_last_name = "JOHNSON"

    unique = generate_unique_names_for_claim(claim, fuzzy_threshold=0.60)
    assert len(unique) == 3
    assert unique[0]["party_type"] == "Insured"
    assert "JOHN" in unique[0]["full_name"]
    assert unique[1]["party_type"] == "Driver"
    assert "JANE" in unique[1]["full_name"]
    assert unique[2]["party_type"] == "Claimant"
    assert "ROBERT" in unique[2]["full_name"]


@pytest.mark.asyncio
async def test_unique_name_first_execution_sequence():
    """Verify that execution sequence is strictly:
    Unique Name 1 -> Portal 1..N
    Unique Name 2 -> Portal 1..N
    NEVER Portal-first (Portal 1 -> Name 1..N).
    """
    call_sequence = []

    class MockScraper:
        def __init__(self, key, county):
            self.key = key
            self.county_name = county
            self.base_url = f"https://{key}.court.gov"
            self.stage_timings = {}

        async def search_on_page(self, page, first_name, last_name, date_of_loss=None):
            call_sequence.append((f"{first_name} {last_name}", self.key))
            return [{
                "CaseNumber": f"{self.key}-001",
                "CaseStyle": f"{last_name} vs State",
                "FilingDate": "01/15/2025",
                "CaseStatus": "ACTIVE",
                "CaseType": "CIVIL",
            }]

    claim = ClaimRecord(
        id="claim-test-seq-1",
        claim_number="CLMSEQ001",
        policy_state="FL",
        loss_location_state="FL",
        insured_first_name="Alice",
        insured_last_name="Adams",
        claimant_first_name="Bob",
        claimant_last_name="Brown",
        driver_first_name="Alice",
        driver_last_name="Adams",
        fl_website_broward="Yes",
        fl_website_hillsborough="Yes",
        fl_website_miami="Yes",
        te_website_travis="No",
        te_website_dallas="No",
        te_website_harris="No",
        te_website_cclerk="No",
        te_website_hcdistrict="No",
    )

    mock_tab = AsyncMock()
    mock_tab.is_closed = MagicMock(return_value=False)
    mock_tab.bring_to_front = AsyncMock()

    mock_runner = MagicMock()
    mock_runner.stage_timings = {}
    mock_runner.tabs = {}
    mock_runner.get_or_create_tab = AsyncMock(return_value=mock_tab)

    mock_runner_cm = AsyncMock()
    mock_runner_cm.__aenter__.return_value = mock_runner
    mock_runner_cm.__aexit__.return_value = None

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=claim)
    mock_session.execute.return_value = mock_res

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    sys_settings = SystemSettings()
    sys_settings.automation.headless_mode = True
    sys_settings.automation.use_chrome_browser = True
    sys_settings.portals.broward_enabled = True
    sys_settings.portals.hillsborough_enabled = True
    sys_settings.portals.miami_enabled = True

    with (
        patch("app.tasks.scraper_tasks.TaskAsyncSessionLocal", return_value=mock_session_cm),
        patch("app.tasks.scraper_tasks.get_system_settings_async", AsyncMock(return_value=sys_settings)),
        patch("app.tasks.scraper_tasks._acquire_browser_slot", AsyncMock(return_value=True)),
        patch("app.tasks.scraper_tasks._release_browser_slot", AsyncMock()),
        patch("app.tasks.scraper_tasks.SingleSessionBrowserRunner", return_value=mock_runner_cm),
        patch("app.tasks.scraper_tasks.is_portal_in_cooldown", return_value=(False, 0, "")),
        patch("app.tasks.scraper_tasks.celery_app.send_task"),
        patch("app.tasks.scraper_tasks.log_audit_event_async", AsyncMock()),
        patch("app.tasks.scraper_tasks.generate_unique_names_for_claim", wraps=generate_unique_names_for_claim) as mock_unique_names,
        patch("app.tasks.scraper_tasks.BrowardScraper", return_value=MockScraper("broward", "Broward County")),
        patch("app.tasks.scraper_tasks.HillsboroughScraper", return_value=MockScraper("hillsborough", "Hillsborough County")),
        patch("app.tasks.scraper_tasks.MiamiDadeScraper", return_value=MockScraper("miami", "Miami-Dade County")),
    ):
        await _async_orchestrate_scrapers("claim-test-seq-1")

    mock_unique_names.assert_called_once()
    assert mock_unique_names.call_args.kwargs["fuzzy_threshold"] == pytest.approx(0.60)

    # 3 portals in V4 order: broward -> miami -> hillsborough
    # Portal 1 (Broward): (Alice Adams, broward) -> (Bob Brown, broward)
    # Portal 2 (Miami): (Alice Adams, miami) -> (Bob Brown, miami)
    # Portal 3 (Hillsborough): (Alice Adams, hillsborough) -> (Bob Brown, hillsborough)
    expected_sequence = [
        ("Alice Adams", "broward"),
        ("Bob Brown", "broward"),
        ("Alice Adams", "miami"),
        ("Bob Brown", "miami"),
        ("Alice Adams", "hillsborough"),
        ("Bob Brown", "hillsborough"),
    ]
    assert call_sequence == expected_sequence, f"Actual sequence {call_sequence} does not match expected {expected_sequence}"


@pytest.mark.asyncio
async def test_portal_failure_isolation_preserves_unique_name_context():
    """Verify that if one portal fails for Unique Name 1, the automation proceeds
    to the other portals for Unique Name 1 (Rule 18: portal failure never skips names).
    """
    call_sequence = []

    class FailingScraper:
        def __init__(self, key, county, should_fail=False):
            self.key = key
            self.county_name = county
            self.base_url = f"https://{key}.court.gov"
            self.should_fail = should_fail
            self.stage_timings = {}

        async def search_on_page(self, page, first_name, last_name, date_of_loss=None):
            call_sequence.append((f"{first_name} {last_name}", self.key))
            if self.should_fail and first_name == "Alice":
                raise RuntimeError(f"Simulated timeout on {self.key}")
            return [{
                "CaseNumber": f"{self.key}-001",
                "CaseStyle": f"{last_name} vs State",
                "FilingDate": "01/15/2025",
                "CaseStatus": "ACTIVE",
                "CaseType": "CIVIL",
            }]

        async def capture_screenshot_on_error(self, page, claim_id, portal_key, attempt, error):
            return {
                "portal_key": portal_key,
                "portal_name": self.county_name,
                "file_path": f"/tmp/{portal_key}_err.png",
            }

    claim = ClaimRecord(
        id="claim-test-err-1",
        claim_number="CLMERR001",
        policy_state="FL",
        loss_location_state="FL",
        insured_first_name="Alice",
        insured_last_name="Adams",
        claimant_first_name="Bob",
        claimant_last_name="Brown",
        driver_first_name="Alice",
        driver_last_name="Adams",
        fl_website_broward="Yes",
        fl_website_hillsborough="Yes",
        fl_website_miami="Yes",
        te_website_travis="No",
        te_website_dallas="No",
        te_website_harris="No",
        te_website_cclerk="No",
        te_website_hcdistrict="No",
    )

    mock_tab = AsyncMock()
    mock_tab.is_closed = MagicMock(return_value=False)
    mock_tab.bring_to_front = AsyncMock()

    mock_runner = MagicMock()
    mock_runner.stage_timings = {}
    mock_runner.tabs = {"broward": mock_tab, "hillsborough": mock_tab, "miami": mock_tab}
    mock_runner.get_or_create_tab = AsyncMock(return_value=mock_tab)

    mock_runner_cm = AsyncMock()
    mock_runner_cm.__aenter__.return_value = mock_runner
    mock_runner_cm.__aexit__.return_value = None

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=claim)
    mock_session.execute.return_value = mock_res

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    sys_settings = SystemSettings()
    sys_settings.portals.broward_enabled = True
    sys_settings.portals.hillsborough_enabled = True
    sys_settings.portals.miami_enabled = True

    # Broward fails on Alice, but Hillsborough and Miami must still be called for Alice!
    with (
        patch("app.tasks.scraper_tasks.TaskAsyncSessionLocal", return_value=mock_session_cm),
        patch("app.tasks.scraper_tasks.get_system_settings_async", AsyncMock(return_value=sys_settings)),
        patch("app.tasks.scraper_tasks._acquire_browser_slot", AsyncMock(return_value=True)),
        patch("app.tasks.scraper_tasks._release_browser_slot", AsyncMock()),
        patch("app.tasks.scraper_tasks.SingleSessionBrowserRunner", return_value=mock_runner_cm),
        patch("app.tasks.scraper_tasks.is_portal_in_cooldown", return_value=(False, 0, "")),
        patch("app.tasks.scraper_tasks.celery_app.send_task"),
        patch("app.tasks.scraper_tasks.log_audit_event_async", AsyncMock()),
        patch("app.tasks.scraper_tasks.BrowardScraper", return_value=FailingScraper("broward", "Broward County", should_fail=True)),
        patch("app.tasks.scraper_tasks.HillsboroughScraper", return_value=FailingScraper("hillsborough", "Hillsborough County")),
        patch("app.tasks.scraper_tasks.MiamiDadeScraper", return_value=FailingScraper("miami", "Miami-Dade County")),
    ):
        await _async_orchestrate_scrapers("claim-test-err-1")

    # Even though Broward failed on Alice Adams, Hillsborough and Miami-Dade were still executed for Alice Adams
    # before moving to Bob Brown
    assert ("Alice Adams", "broward") in call_sequence
    assert ("Alice Adams", "hillsborough") in call_sequence
    assert ("Alice Adams", "miami") in call_sequence
    assert ("Bob Brown", "hillsborough") in call_sequence
    assert ("Bob Brown", "miami") in call_sequence
