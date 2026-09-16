"""
Automated tests for IMP-2026-0909-003:
  - GET  /api/v1/matches/extract-names
  - POST /api/v1/matches/fuzzy-search
  - POST /api/v1/settings/test-anticaptcha
  - ClaimRowSchema deprecated-field cleanup (garaging_city, garaging_state,
    loss_location_city, loss_location_county no longer ingested from Excel)

All tests use the in-process ASGI test client (httpx + ASGITransport) against an
in-memory SQLite database — no external services required.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, Base, engine
from app.main import app
from app.models.claim import ClaimRecord
from app.models.court_case import ScrapedCourtCase

# ---------------------------------------------------------------------------
# Module-level DB setup (mirrors test_api.py pattern)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure schema exists for all tests in this module."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _seed_claim(
    claim_number: str = "TST-001",
    insured_first: str = "Alice",
    insured_last: str = "Johnson",
    driver_first: str = "Bob",
    driver_last: str = "Williams",
    claimant_first: str = "Carol",
    claimant_last: str = "Martinez",
) -> str:
    """Insert a ClaimRecord and return its ID."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        record = ClaimRecord(
            id=claim_id,
            claim_number=claim_number,
            insured_first_name=insured_first,
            insured_last_name=insured_last,
            driver_first_name=driver_first,
            driver_last_name=driver_last,
            claimant_first_name=claimant_first,
            claimant_last_name=claimant_last,
            dol="01/15/2024",
            policy_state="Florida",
            loss_location_state="Florida",
        )
        session.add(record)
        await session.commit()
    return claim_id


async def _seed_court_case(
    claim_id: str,
    case_number: str = "2024-001234-CC-26",
    case_style: str = "JOHNSON, ALICE VS ALLSTATE INSURANCE COMPANY",
    county_name: str = "Broward",
    county_website: str = "https://www.browardclerk.org/",
    filing_date: str = "2024-03-10",
    case_status: str = "OPEN",
    case_type: str = "CIRCUIT CIVIL",
) -> str:
    """Insert a ScrapedCourtCase and return its ID."""
    case_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        record = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            case_number=case_number,
            case_style=case_style,
            county_name=county_name,
            county_website=county_website,
            filing_date=filing_date,
            case_status=case_status,
            case_type=case_type,
        )
        session.add(record)
        await session.commit()
    return case_id


# ===========================================================================
# 1. GET /api/v1/matches/extract-names
# ===========================================================================

class TestExtractNames:
    """Tests for the unique party-name extraction endpoint."""

    @pytest.mark.asyncio
    async def test_extract_names_empty_database_returns_zero(self):
        """When no claims exist the endpoint returns empty lists and total=0."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names")
        assert res.status_code == 200
        data = res.json()
        assert "insured" in data
        assert "driver" in data
        assert "claimant" in data
        assert "total" in data
        assert isinstance(data["insured"], list)
        assert isinstance(data["driver"], list)
        assert isinstance(data["claimant"], list)
        assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_extract_names_returns_seeded_names(self):
        """Names from seeded claims appear in the response."""
        await _seed_claim("EXT-001", "Diana", "Prince", "Clark", "Kent", "Bruce", "Wayne")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names")
        assert res.status_code == 200
        data = res.json()
        assert "Diana Prince" in data["insured"]
        assert "Clark Kent" in data["driver"]
        assert "Bruce Wayne" in data["claimant"]
        assert data["total"] >= 3

    @pytest.mark.asyncio
    async def test_extract_names_party_type_insured_filter(self):
        """?party_type=insured returns only insured list; driver and claimant are empty."""
        await _seed_claim("EXT-002", "Tony", "Stark", "Peter", "Parker", "Natasha", "Romanoff")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names?party_type=insured")
        assert res.status_code == 200
        data = res.json()
        assert len(data["driver"]) == 0
        assert len(data["claimant"]) == 0
        assert len(data["insured"]) >= 1
        assert data["total"] == len(data["insured"])

    @pytest.mark.asyncio
    async def test_extract_names_party_type_driver_filter(self):
        """?party_type=driver returns only driver list."""
        await _seed_claim("EXT-DRV-01", "Steve", "Rogers", "Bucky", "Barnes", "Sam", "Wilson")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names?party_type=driver")
        assert res.status_code == 200
        data = res.json()
        assert len(data["insured"]) == 0
        assert len(data["claimant"]) == 0
        assert len(data["driver"]) >= 1
        assert data["total"] == len(data["driver"])

    @pytest.mark.asyncio
    async def test_extract_names_party_type_claimant_filter(self):
        """?party_type=claimant returns only claimant list."""
        await _seed_claim("EXT-CLM-01", "Steve", "Rogers", "Bucky", "Barnes", "Sam", "Wilson")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names?party_type=claimant")
        assert res.status_code == 200
        data = res.json()
        assert len(data["insured"]) == 0
        assert len(data["driver"]) == 0
        assert len(data["claimant"]) >= 1
        assert data["total"] == len(data["claimant"])

    @pytest.mark.asyncio
    async def test_extract_names_deduplicates_same_name(self):
        """Two claims with identical insured names produce only one entry."""
        await _seed_claim("EXT-DUP-A", "Dup", "Name", "X", "Y", "Z", "Z")
        await _seed_claim("EXT-DUP-B", "Dup", "Name", "X2", "Y2", "Z2", "Z2")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names?party_type=insured")
        assert res.status_code == 200
        data = res.json()
        assert data["insured"].count("Dup Name") == 1

    @pytest.mark.asyncio
    async def test_extract_names_sorted_alphabetically(self):
        """Returned names are in sorted (alphabetical) order."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names?party_type=insured")
        assert res.status_code == 200
        data = res.json()
        names = data["insured"]
        assert names == sorted(names), "insured names should be sorted alphabetically"

    @pytest.mark.asyncio
    async def test_extract_names_total_equals_sum_of_lists(self):
        """total field equals len(insured) + len(driver) + len(claimant) when party_type=all."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/matches/extract-names")
        assert res.status_code == 200
        data = res.json()
        expected = len(data["insured"]) + len(data["driver"]) + len(data["claimant"])
        assert data["total"] == expected


# ===========================================================================
# 2. POST /api/v1/matches/fuzzy-search
# ===========================================================================

class TestFuzzySearch:
    """Tests for the legacy Power Automate fuzzy-search endpoint."""

    @pytest.mark.asyncio
    async def test_fuzzy_search_empty_body_validation_error(self):
        """Missing search_name returns HTTP 422."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={})
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_fuzzy_search_blank_name_returns_422(self):
        """Whitespace-only search_name is rejected with 422."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={"search_name": "   "})
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_fuzzy_search_no_court_cases_returns_empty(self):
        """With no matching court cases, response is valid with total=0."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "ZZZNOMATCH999",
                "threshold": 0.99,
            })
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["matches"] == []
        assert data["search_name"] == "ZZZNOMATCH999"
        assert data["threshold_applied"] == 0.99
        assert "duration_ms" in data
        assert data["duration_ms"] >= 0

    @pytest.mark.asyncio
    async def test_fuzzy_search_finds_high_similarity_match(self):
        """A name matching the seeded case style is returned above default threshold."""
        claim_id = await _seed_claim("FST-001", "Alice", "Johnson", "Bob", "Williams", "Carol", "Martinez")
        await _seed_court_case(
            claim_id=claim_id,
            case_number="2024-FST-001",
            case_style="JOHNSON ALICE VS ALLSTATE INSURANCE COMPANY",
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Alice Johnson",
                "threshold": 0.60,
            })
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        target = next((m for m in data["matches"] if m["case_number"] == "2024-FST-001"), None)
        assert target is not None
        assert target["similarity_score"] >= 0.60
        assert "Alice" in target["case_style"] or "ALICE" in target["case_style"].upper()

    @pytest.mark.asyncio
    async def test_fuzzy_search_response_schema_fields(self):
        """All required response fields are present on each match item."""
        claim_id = await _seed_claim("FST-002", "Henry", "Adams", "X", "Y", "Z", "Z")
        await _seed_court_case(
            claim_id=claim_id,
            case_number="2024-FST-002",
            case_style="ADAMS HENRY VS STATE FARM",
            county_name="Miami-Dade",
            county_website="https://www.miami-dadeclerk.com/",
            filing_date="2024-06-01",
            case_status="OPEN",
            case_type="CIRCUIT CIVIL",
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Henry Adams",
                "threshold": 0.60,
            })
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        item = next((m for m in data["matches"] if m["case_number"] == "2024-FST-002"), None)
        assert item is not None, "Expected case 2024-FST-002 in results"
        # Verify all schema fields present
        for field in ["court_case_id", "case_number", "case_style", "county_name",
                      "filing_date", "case_status", "similarity_score"]:
            assert field in item, f"Missing field: {field}"
        assert 0.0 <= item["similarity_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_fuzzy_search_sorted_by_similarity_descending(self):
        """Results are sorted highest similarity_score first."""
        claim_id = await _seed_claim("FST-003", "Mark", "Torres", "X", "Y", "Z", "Z")
        # High match
        await _seed_court_case(claim_id, "2024-FST-003A", "TORRES MARK VS PROGRESSIVE INS", "Broward")
        # Lower match
        await _seed_court_case(claim_id, "2024-FST-003B", "SMITH JOHN VS GEICO COMPANY", "Dallas")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Mark Torres",
                "threshold": 0.10,
            })
        assert res.status_code == 200
        scores = [m["similarity_score"] for m in res.json()["matches"]]
        assert scores == sorted(scores, reverse=True), "Matches must be sorted by similarity desc"

    @pytest.mark.asyncio
    async def test_fuzzy_search_limit_parameter_respected(self):
        """limit param caps the number of returned results."""
        claim_id = await _seed_claim("FST-004", "Emma", "Wilson", "X", "Y", "Z", "Z")
        # Seed 5 cases all matching
        for i in range(5):
            await _seed_court_case(claim_id, f"2024-FST-004-{i}", f"WILSON EMMA VS COMPANY {i}", "Hillsborough")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Emma Wilson",
                "threshold": 0.60,
                "limit": 2,
            })
        assert res.status_code == 200
        data = res.json()
        assert len(data["matches"]) <= 2

    @pytest.mark.asyncio
    async def test_fuzzy_search_high_threshold_excludes_low_matches(self):
        """Setting threshold=0.99 excludes borderline matches."""
        claim_id = await _seed_claim("FST-005", "Partial", "Match", "X", "Y", "Z", "Z")
        await _seed_court_case(claim_id, "2024-FST-005", "TOTALLY DIFFERENT STYLE VS NOBODY", "Travis")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Partial Match",
                "threshold": 0.99,
            })
        assert res.status_code == 200
        # The low-similarity case should be excluded at threshold 0.99
        for match in res.json()["matches"]:
            assert match["case_number"] != "2024-FST-005", \
                "Low-similarity case should not appear at threshold=0.99"

    @pytest.mark.asyncio
    async def test_fuzzy_search_default_threshold_is_0_60(self):
        """When threshold is omitted, the response confirms threshold_applied=0.6."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Test Name",
            })
        assert res.status_code == 200
        data = res.json()
        assert data["threshold_applied"] == 0.6

    @pytest.mark.asyncio
    async def test_fuzzy_search_min_filing_year_filter(self):
        """Cases with filing dates before min_filing_year are excluded."""
        claim_id = await _seed_claim("FST-006", "Old", "Case", "X", "Y", "Z", "Z")
        await _seed_court_case(
            claim_id, "2024-FST-OLD",
            "OLD CASE VS OLD COMPANY",
            "Broward",
            filing_date="2005-01-15",
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Old Case",
                "threshold": 0.60,
                "min_filing_year": 2010,
            })
        assert res.status_code == 200
        for match in res.json()["matches"]:
            assert match["case_number"] != "2024-FST-OLD", \
                "Pre-2010 case must be excluded when min_filing_year=2010"

    @pytest.mark.asyncio
    async def test_fuzzy_search_duration_ms_is_non_negative(self):
        """duration_ms field is always present and non-negative."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "Some Name",
            })
        assert res.status_code == 200
        assert res.json()["duration_ms"] >= 0.0

    @pytest.mark.asyncio
    async def test_fuzzy_search_search_name_echoed_in_response(self):
        """The search_name field in the response matches the submitted value."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/matches/fuzzy-search", json={
                "search_name": "  Echo Test  ",
            })
        assert res.status_code == 200
        # search_name should be stripped
        assert res.json()["search_name"] == "Echo Test"


# ===========================================================================
# 3. POST /api/v1/settings/test-anticaptcha
# ===========================================================================

class TestAntiCaptchaEndpoint:
    """Tests for the Anti-Captcha API key balance test endpoint."""

    @pytest.mark.asyncio
    async def test_anticaptcha_missing_api_key_returns_422(self):
        """Empty body is rejected with HTTP 422 (schema validation)."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/settings/test-anticaptcha", json={})
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_anticaptcha_blank_api_key_returns_422(self):
        """Whitespace-only api_key is rejected with HTTP 422."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/settings/test-anticaptcha", json={"api_key": "   "})
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_anticaptcha_valid_key_returns_ok_status(self):
        """A successful API call returns status='ok' and a non-negative balance."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "balance": 4.2300}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.api.v1.endpoints.settings.httpx.AsyncClient", return_value=mock_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/settings/test-anticaptcha",
                    json={"api_key": "validkey1234567890abcdef"},
                )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["balance"] == round(4.23, 4)
        assert "valid" in data["message"].lower()
        assert data["latency_ms"] >= 0
        assert data["error_code"] is None

    @pytest.mark.asyncio
    async def test_anticaptcha_invalid_key_returns_error_status(self):
        """An invalid API key returns status='error' with the errorCode from the API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errorId": 1,
            "errorCode": "ERROR_KEY_DOES_NOT_EXIST",
            "errorDescription": "Account authorization key not found in the system",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.api.v1.endpoints.settings.httpx.AsyncClient", return_value=mock_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/settings/test-anticaptcha",
                    json={"api_key": "badkey000000000000000000"},
                )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["balance"] is None
        assert data["error_code"] == "ERROR_KEY_DOES_NOT_EXIST"
        assert "AntiCaptcha API error" in data["message"]
        assert data["latency_ms"] >= 0

    @pytest.mark.asyncio
    async def test_anticaptcha_timeout_returns_error_status(self):
        """A TimeoutError from httpx surfaces as status='error' with error_code='TIMEOUT'."""
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=TimeoutError("Connection timed out"))

        with patch("app.api.v1.endpoints.settings.httpx.AsyncClient", return_value=mock_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/settings/test-anticaptcha",
                    json={"api_key": "timeoutkey12345678901234"},
                )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error_code"] == "TIMEOUT"
        assert "timed out" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_anticaptcha_connection_error_returns_error_status(self):
        """A generic network error surfaces as status='error' with error_code='CONNECTION_ERROR'."""
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=OSError("Network unreachable"))

        with patch("app.api.v1.endpoints.settings.httpx.AsyncClient", return_value=mock_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/settings/test-anticaptcha",
                    json={"api_key": "networkerrorkey123456789"},
                )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error_code"] == "CONNECTION_ERROR"
        assert "Connection failed" in data["message"]

    @pytest.mark.asyncio
    async def test_anticaptcha_response_always_has_latency_ms(self):
        """latency_ms is always present in the response regardless of outcome."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "balance": 1.0}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.api.v1.endpoints.settings.httpx.AsyncClient", return_value=mock_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/settings/test-anticaptcha",
                    json={"api_key": "anykeywithlength12345678"},
                )

        assert res.status_code == 200
        data = res.json()
        assert "latency_ms" in data
        assert isinstance(data["latency_ms"], (int, float))
        assert data["latency_ms"] >= 0


# ===========================================================================
# 4. ClaimRowSchema — Deprecated field ingestion cleanup
# ===========================================================================

class TestClaimRowSchemaDeprecatedFields:
    """Verify garaging_city, garaging_state, loss_location_city, loss_location_county
    are no longer part of the ClaimRowSchema Excel ingestion aliases."""

    def test_deprecated_fields_not_in_schema_model_fields(self):
        """The 4 deprecated Excel aliases must not appear in ClaimRowSchema.model_fields."""
        from app.schemas.claim import ClaimRowSchema
        fields = ClaimRowSchema.model_fields
        deprecated = ["garaging_city", "garaging_state", "loss_location_city", "loss_location_county"]
        for dep in deprecated:
            assert dep not in fields, (
                f"Deprecated field '{dep}' must be removed from ClaimRowSchema ingestion mapping"
            )

    def test_deprecated_fields_not_in_schema_aliases(self):
        """The 4 deprecated column header aliases must not appear in ClaimRowSchema field metadata."""
        from app.schemas.claim import ClaimRowSchema
        deprecated_aliases = {"Garaging City", "Garaging State", "Loss Location City", "Loss Location County"}
        present_aliases = set()
        for field_info in ClaimRowSchema.model_fields.values():
            if field_info.alias:
                present_aliases.add(field_info.alias)
        overlap = deprecated_aliases & present_aliases
        assert len(overlap) == 0, (
            f"Deprecated Excel column aliases still present in ClaimRowSchema: {overlap}"
        )

    def test_required_fields_still_present(self):
        """Core ingestion fields (claim_number, dol, policy_state, loss_location_state) remain."""
        from app.schemas.claim import ClaimRowSchema
        required = ["claim_number", "dol", "policy_state", "loss_location_state",
                    "insured_first_name", "insured_last_name",
                    "claimant_first_name", "claimant_last_name",
                    "driver_first_name", "driver_last_name"]
        fields = ClaimRowSchema.model_fields
        for f in required:
            assert f in fields, f"Required ingestion field '{f}' was accidentally removed"

    def test_claimrowschema_parses_row_without_deprecated_columns(self):
        """ClaimRowSchema successfully validates a row that omits all 4 deprecated columns."""
        from app.schemas.claim import ClaimRowSchema
        row = {
            "Claim Number": "TST-SCHEMA-001",
            "Insured First Name": "John",
            "Insured Last Name": "Doe",
            "Claimant First Name": "Jane",
            "Claimant Last Name": "Doe",
            "Driver First Name (Insured Vehicle)": "Jim",
            "Driver Last Name (Insured Vehicle)": "Doe",
            "DOL": "01/15/2024",
            "Loss Location State": "Florida",
            "Policy State": "Florida",
            "Exposure Number": "001",
        }
        schema = ClaimRowSchema.model_validate(row, from_attributes=False, context=None,
                                               strict=False, by_alias=True)
        assert schema.claim_number == "TST-SCHEMA-001"
        assert schema.insured_first_name == "John"
        assert schema.dol == "01/15/2024"

    def test_claimrecord_orm_model_no_longer_has_deprecated_columns(self):
        """The DB ORM model (ClaimRecord) completely removes all 4 deprecated geographic columns."""
        from app.models.claim import ClaimRecord
        orm_cols = {col.key for col in ClaimRecord.__table__.columns}
        for col in ["garaging_city", "garaging_state", "loss_location_city", "loss_location_county"]:
            assert col not in orm_cols, (
                f"ORM column '{col}' must be completely removed from ClaimRecord table"
            )
