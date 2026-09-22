import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.settings import FuzzyMatcherSettings, SystemSettings
from app.services.fuzzy_engine import is_case_eligible


@pytest.mark.asyncio
async def test_fuzzymatchapi_root_parity_match_found():
    """Test root /fuzzymatchapi returns exact PowerAutomate schema: Match Found."""
    payload = {
        "text1": "JOHN DOE",
        "text2": "JOHN DOE ET AL",
        "threshold": 0.6,
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/fuzzymatchapi", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "Match Found"
    assert data["score"] >= 60.0
    assert data["guidewire_eligible"] is True
    # Ensure zero null field pollution
    assert "filing_date" not in data
    assert "min_filing_date" not in data
    assert "cases" not in data
    assert "cases_results" not in data
    assert "matches" not in data
    assert "reference_string" not in data


@pytest.mark.asyncio
async def test_fuzzymatchapi_root_parity_no_match():
    """Test root /fuzzymatchapi returns No Match Found when score < threshold."""
    payload = {
        "text1": "JOHN DOE",
        "text2": "COMPLETELY UNRELATED ENTITY CORP",
        "threshold": 0.6,
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/fuzzymatchapi", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "No Match Found"
    assert data["score"] < 60.0
    assert data["guidewire_eligible"] is False


@pytest.mark.asyncio
async def test_fuzzymatchapi_filing_date_filter_eligible():
    """Test /api/v1/matches/fuzzymatchapi qualifies case when filing date >= min_filing_date."""
    payload = {
        "text1": "MICHAEL CORLEONE",
        "text2": "MICHAEL CORLEONE VS STATE FARM",
        "threshold": 0.6,
        "filing_date": "2022-06-15",
        "min_filing_date": "2010-01-01",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/fuzzymatchapi", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "Match Found"
    assert data["score"] >= 60.0
    assert data["guidewire_eligible"] is True
    assert data["filing_date"] == "2022-06-15"
    assert data["min_filing_date"] == "2010-01-01"


@pytest.mark.asyncio
async def test_fuzzymatchapi_filing_date_filter_filtered_out():
    """Test /api/v1/matches/fuzzymatchapi rejects case when filing date < min_filing_date."""
    payload = {
        "text1": "MICHAEL CORLEONE",
        "text2": "MICHAEL CORLEONE VS STATE FARM",
        "threshold": 0.6,
        "filing_date": "2008-11-20",
        "min_filing_date": "2010-01-01",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/fuzzymatchapi", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert "Filtered Out" in data["result"]
    assert data["guidewire_eligible"] is False
    assert "prior to Minimum" in data["filter_reason"]


@pytest.mark.asyncio
async def test_fuzzymatchapi_batch_cases_guidewire_filtering():
    """Test /api/v1/matches/fuzzymatchapi with multiple cases filtering exclusively by filing date."""
    payload = {
        "text1": "ALICE WALKER",
        "threshold": 0.6,
        "min_filing_date": "2010-01-01",
        "cases": [
            {
                "case_number": "CASE-2021-001",
                "case_style": "ALICE WALKER VS PROGRESSIVE",
                "filing_date": "2021-03-12",
                "case_status": "Closed",
                "case_type": "Other Civil",
            },
            {
                "case_number": "CASE-2005-999",
                "case_style": "ALICE WALKER VS ALLSTATE",
                "filing_date": "2005-08-19",
                "case_status": "Disposed",
                "case_type": "Civil",
            },
            {
                "case_number": "CASE-2023-042",
                "case_style": "RANDOM UNRELATED PERSON",
                "filing_date": "2023-10-01",
                "case_status": "Open",
                "case_type": "Auto Negligence",
            },
        ],
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/fuzzymatchapi", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["cases_evaluated"] == 3
    assert data["eligible_for_guidewire"] == 1
    assert len(data["cases"]) == 3
    assert "cases_results" not in data
    assert "matches" not in data
    assert "reference_string" not in data

    c1 = data["cases"][0]
    assert c1["case_number"] == "CASE-2021-001"
    assert c1["CaseNumber"] == "CASE-2021-001"
    assert c1["CaseStyle"] == "ALICE WALKER VS PROGRESSIVE"
    assert c1["SuitFiledDate"] == "2021-03-12"
    assert c1["result"] == "Match Found"
    assert c1["guidewire_eligible"] is True

    c2 = data["cases"][1]
    assert c2["case_number"] == "CASE-2005-999"
    assert c2["CaseNumber"] == "CASE-2005-999"
    assert "Filtered Out" in c2["result"]
    assert c2["guidewire_eligible"] is False

    c3 = data["cases"][2]
    assert c3["case_number"] == "CASE-2023-042"
    assert c3["CaseNumber"] == "CASE-2023-042"
    assert c3["result"] == "No Match Found"
    assert c3["guidewire_eligible"] is False


@pytest.mark.asyncio
async def test_fuzzymatchapi_multi_format_date_filtering():
    """Verify /fuzzymatchapi accepts MM/DD/YYYY, YYYY/MM/DD, and ISO date strings without error."""
    payload = {
        "text1": "JASMINE PHILLIPS",
        "text2": "JASMINE PHILLIPS VS MIAMI DADE POLICE DEPARTMENT",
        "threshold": 0.6,
        "filing_date": "05/14/2023",
        "min_filing_date": "10/01/2020",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/fuzzymatchapi", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "Match Found"
    assert data["guidewire_eligible"] is True
    assert data["filing_date"] == "05/14/2023"
    assert data["min_filing_date"] == "10/01/2020"
    assert "cases" not in data
    assert "matches" not in data


def test_is_case_eligible_pure_date_filter():
    """Verify is_case_eligible evaluates filing date strictly and ignores status/type when none specified."""
    # Case after 2010-01-01
    eligible = is_case_eligible(
        filing_date="2018-04-12",
        case_status=None,
        case_type=None,
        min_filing_date="2010-01-01",
    )
    assert eligible is True

    # Case before 2010-01-01
    eligible_old = is_case_eligible(
        filing_date="2007-12-31",
        case_status=None,
        case_type=None,
        min_filing_date="2010-01-01",
    )
    assert eligible_old is False


def test_settings_fuzzy_matcher_schema_separated_fields():
    """Verify FuzzyMatcherSettings separates unique names and case style cleaning patterns."""
    settings = SystemSettings()
    matcher = settings.matcher
    assert isinstance(matcher, FuzzyMatcherSettings)
    assert matcher.unique_names_threshold == 0.85
    assert matcher.auto_match_threshold == 0.60
    assert matcher.manual_review_threshold == 0.40
    assert "ET AL" in matcher.clean_case_style_patterns
    assert "LLC" in matcher.clean_party_name_patterns
