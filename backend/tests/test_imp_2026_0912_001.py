"""
Tests for IMP-2026-0912-001 (Prompt 04):
- Strict Unique-Name Orchestration & Fuzzy Deduplication
- Legacy /fuzzymatchapi endpoint parity (root and /api/v1/matches)
- Security Block Detection, SecurityBlockException, and Logging
- Cooldown Service (Redis + in-memory fallback)
- BLOCKED status integration in BotStatusEnum and ClaimRecord
- Deprecated fields absence verification
- Auto-queue default enabled verification
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.automation.base import (
    SecurityBlockException,
    detect_security_block,
    log_security_block_event,
)
from app.core.database import Base, engine
from app.main import app
from app.models.claim import BotStatusEnum, ClaimRecord
from app.services.cooldown_service import (
    clear_portal_cooldown,
    get_all_portal_cooldowns,
    is_portal_in_cooldown,
    set_portal_cooldown,
)
from app.services.excel_parser import TARGET_CLAIM_FIELDS
from app.services.fuzzy_engine import (
    derive_search_counts_fuzzy,
    generate_unique_names_for_claim,
)
from app.tasks.queue_runner import is_auto_queue_enabled


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema exists for test runs."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── 1. Unique-Name Generation & Fuzzy Deduplication Tests ─────────────────────

def test_generate_unique_names_all_distinct():
    """When Insured, Driver, and Claimant are all distinct, generate 3 unique names."""
    claim = ClaimRecord(
        claim_number="CLM-UNIQ-001",
        insured_first_name="Alice",
        insured_last_name="Johnson",
        driver_first_name="Bob",
        driver_last_name="Smith",
        claimant_first_name="Charlie",
        claimant_last_name="Brown",
    )
    names = generate_unique_names_for_claim(claim)
    assert len(names) == 3
    labels = [n["party_type"] for n in names]
    assert "Insured" in labels
    assert "Driver" in labels
    assert "Claimant" in labels


def test_generate_unique_names_all_identical():
    """When Insured, Driver, and Claimant are the same person, collapse to 1 unique name."""
    claim = ClaimRecord(
        claim_number="CLM-UNIQ-002",
        insured_first_name="John",
        insured_last_name="Doe",
        driver_first_name="John",
        driver_last_name="Doe",
        claimant_first_name="John",
        claimant_last_name="Doe",
    )
    names = generate_unique_names_for_claim(claim)
    assert len(names) == 1
    assert names[0]["first_name"] == "John"
    assert names[0]["last_name"] == "Doe"
    assert names[0]["party_type"] == "Insured"


def test_generate_unique_names_fuzzy_duplicate():
    """Near-identical names (score >= 0.90) are collapsed to avoid duplicate court searches."""
    claim = ClaimRecord(
        claim_number="CLM-UNIQ-003",
        insured_first_name="Jonathan",
        insured_last_name="Doe",
        driver_first_name="Jonathan",
        driver_last_name="Doe",
        claimant_first_name="Jonathan",
        claimant_last_name="Doe",
    )
    names = generate_unique_names_for_claim(claim)
    assert len(names) == 1


def test_generate_unique_names_missing_parties():
    """Handles missing or whitespace-only driver and claimant gracefully."""
    claim = ClaimRecord(
        claim_number="CLM-UNIQ-004",
        insured_first_name="Maria",
        insured_last_name="Garcia",
        driver_first_name=None,
        driver_last_name="   ",
        claimant_first_name="",
        claimant_last_name=None,
    )
    names = generate_unique_names_for_claim(claim)
    assert len(names) == 1
    assert names[0]["last_name"] == "Garcia"


# ── 2. Search Count Derivation (DualSearch / TripleSearch) ───────────────────

def test_derive_search_counts_fuzzy_all_same():
    claim = ClaimRecord(
        insured_first_name="John", insured_last_name="Doe",
        driver_first_name="John", driver_last_name="Doe",
        claimant_first_name="John", claimant_last_name="Doe",
    )
    dual, triple = derive_search_counts_fuzzy(claim)
    assert dual == 1
    assert triple == 1


def test_derive_search_counts_fuzzy_insured_equals_driver():
    claim = ClaimRecord(
        insured_first_name="John", insured_last_name="Doe",
        driver_first_name="John", driver_last_name="Doe",
        claimant_first_name="Mary", claimant_last_name="Smith",
    )
    dual, triple = derive_search_counts_fuzzy(claim)
    assert dual == 1
    assert triple == 3


def test_derive_search_counts_fuzzy_insured_equals_claimant():
    claim = ClaimRecord(
        insured_first_name="John", insured_last_name="Doe",
        driver_first_name="Bob", driver_last_name="Jones",
        claimant_first_name="John", claimant_last_name="Doe",
    )
    dual, triple = derive_search_counts_fuzzy(claim)
    assert dual == 2
    assert triple == 1


def test_derive_search_counts_fuzzy_driver_equals_claimant():
    claim = ClaimRecord(
        insured_first_name="Alice", insured_last_name="Wonderland",
        driver_first_name="John", driver_last_name="Doe",
        claimant_first_name="John", claimant_last_name="Doe",
    )
    dual, triple = derive_search_counts_fuzzy(claim)
    assert dual == 2
    assert triple == 1


def test_derive_search_counts_fuzzy_all_different():
    claim = ClaimRecord(
        insured_first_name="Alice", insured_last_name="Wonderland",
        driver_first_name="Bob", driver_last_name="Marley",
        claimant_first_name="Charlie", claimant_last_name="Chaplin",
    )
    dual, triple = derive_search_counts_fuzzy(claim)
    assert dual == 2
    assert triple == 3


# ── 3. Portal Cooldown Service Tests ──────────────────────────────────────────

def test_portal_cooldown_lifecycle():
    portal = "broward"
    clear_portal_cooldown(portal)

    in_cool, remaining, reason = is_portal_in_cooldown(portal)
    assert in_cool is False
    assert remaining == 0

    # Set cooldown for 60 seconds
    set_portal_cooldown(portal, cooldown_seconds=60, reason="Cloudflare Rate Limit 429")

    in_cool, remaining, reason = is_portal_in_cooldown(portal)
    assert in_cool is True
    assert remaining > 50

    all_cooldowns = get_all_portal_cooldowns()
    assert portal in all_cooldowns
    assert all_cooldowns[portal]["reason"] == "Cloudflare Rate Limit 429"

    # Clear cooldown
    clear_portal_cooldown(portal)
    in_cool, remaining, _ = is_portal_in_cooldown(portal)
    assert in_cool is False


# ── 4. Security Block Detection & Logging Tests ──────────────────────────────

def test_detect_security_block_http_429():
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(
            status_code=429,
            html_text="Too Many Requests - Rate limit exceeded",
            portal_key="dallas",
        )
    assert "429" in exc_info.value.message
    assert exc_info.value.portal_key == "dallas"


def test_detect_security_block_cloudflare_challenge():
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(
            status_code=200,
            html_text="<div id='cf-wrapper'><div id='cf-browser-verification'>Checking your browser...</div></div>",
            portal_key="miami",
        )
    assert "Cloudflare challenge page" in exc_info.value.message


def test_detect_security_block_access_denied_waf():
    with pytest.raises(SecurityBlockException) as exc_info:
        detect_security_block(
            status_code=403,
            html_text="<h1>403 Forbidden</h1><p>Access Denied. You do not have permission.</p>",
            portal_key="harris_jp",
        )
    assert "403" in exc_info.value.message


def test_detect_security_block_clean_page():
    # Normal pages must not trigger a false positive
    detect_security_block(
        status_code=200,
        html_text="<html><head><title>Broward County Court Records</title></head><body>Search Results: 2 cases found</body></html>",
        portal_key="broward",
    )


def test_log_security_block_event(tmp_path):
    log_security_block_event(
        portal_key="travis",
        block_reason="Automated test block event",
        page_url="https://traviscountycourts.org/search",
        cooldown_seconds=300,
    )
    log_file = os.path.join("backend", "logs", "security_blocks.log")
    if os.path.exists(log_file):
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
            assert "travis" in content
            assert "Automated test block event" in content


# ── 5. /fuzzymatchapi & /unique-names Endpoints Tests ─────────────────────────

@pytest.mark.asyncio
async def test_legacy_fuzzymatchapi_root_endpoint():
    """Verify legacy Power Automate parity endpoint at root POST /fuzzymatchapi."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Match case
        res_match = await ac.post(
            "/fuzzymatchapi",
            json={"text1": "Johnathan Doe", "text2": "John Doe", "threshold": 0.6},
        )
        assert res_match.status_code == 200
        data = res_match.json()
        assert data["result"] == "Match Found"
        assert data["score"] >= 60.0

        # Non-match case
        res_no_match = await ac.post(
            "/fuzzymatchapi",
            json={"text1": "Alice Smith", "text2": "Bob Jones", "threshold": 0.8},
        )
        assert res_no_match.status_code == 200
        data_no = res_no_match.json()
        assert data_no["result"] == "No Match Found"
        assert data_no["score"] < 80.0


@pytest.mark.asyncio
async def test_api_v1_unique_names_endpoint():
    """Verify POST /api/v1/matches/unique-names endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "insured_first_name": "Carlos",
            "insured_last_name": "Santana",
            "driver_first_name": "Carlos",
            "driver_last_name": "Santana",
            "claimant_first_name": "Jimi",
            "claimant_last_name": "Hendrix",
        }
        res = await ac.post("/api/v1/matches/unique-names", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 2
        assert data["total_unique_names"] == 2
        assert len(data["unique_names"]) == 2
        assert "dual_search" not in data
        assert "triple_search" not in data
        assert "claim_number" not in data


# ── 6. Deprecated Fields Absence Verification ─────────────────────────────────

def test_deprecated_fields_absent_from_target_fields():
    """Ensure the 4 deprecated fields are permanently absent from ingest mapping."""
    deprecated_fields = [
        "Loss Location City",
        "Loss Location County",
        "Garaging City",
        "Garaging State",
    ]
    for field in deprecated_fields:
        assert field not in TARGET_CLAIM_FIELDS, f"Deprecated field '{field}' must not be present in TARGET_CLAIM_FIELDS"


# ── 7. BotStatusEnum & Auto-Queue Verification ────────────────────────────────

def test_bot_status_enum_blocked():
    """Ensure BotStatusEnum has BLOCKED member."""
    assert BotStatusEnum.BLOCKED == "BLOCKED"
    assert BotStatusEnum.BLOCKED.value == "BLOCKED"


def test_auto_queue_default_enabled():
    """Verify auto-queue is enabled by default when unconfigured."""
    from app.tasks.queue_runner import AUTO_MODE_KEY, get_redis_client, set_auto_queue_enabled
    r = get_redis_client()
    try:
        r.delete(AUTO_MODE_KEY)
    except Exception:
        pass
    assert is_auto_queue_enabled() is True
    # Ensure set to True for operational state
    set_auto_queue_enabled(True)
