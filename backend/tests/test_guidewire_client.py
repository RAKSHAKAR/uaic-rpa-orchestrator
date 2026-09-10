"""Unit tests for GuidewireClient, request builders, authentication headers, and mock simulations."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.schemas.settings import GuidewireTestRequest
from app.services.guidewire_client import GuidewireClient, format_claim_number

# ============================================================================
# 1. Claim Number Formatting (Power Automate logic)
# ============================================================================

def test_format_claim_number():
    # 9-digit numbers must be prefixed with '0' to make 10 digits
    assert format_claim_number("123456789") == "0123456789"
    assert format_claim_number(" 123456789 ") == "0123456789"

    # 10-digit numbers stay intact
    assert format_claim_number("0123456789") == "0123456789"
    assert format_claim_number("9876543210") == "9876543210"

    # Alphanumeric or other lengths stay intact
    assert format_claim_number("CLM-1234") == "CLM-1234"


# ============================================================================
# 2. Header Construction Across Auth Types
# ============================================================================

def test_guidewire_client_headers():
    # Bearer auth
    c_bearer = GuidewireClient(auth_type="Bearer", api_key="secret-token-123")
    headers = c_bearer._build_headers()
    assert headers["Authorization"] == "Bearer secret-token-123"
    assert headers["Content-Type"] == "application/json"

    # ApiKey auth
    c_apikey = GuidewireClient(auth_type="ApiKey", api_key="key-xyz-789")
    headers = c_apikey._build_headers()
    assert headers["X-API-Key"] == "key-xyz-789"

    # Basic auth
    c_basic = GuidewireClient(auth_type="Basic", client_id="myuser", client_secret="mypass")
    headers = c_basic._build_headers()
    assert headers["Authorization"].startswith("Basic ")

    # OAuth2 auth
    c_oauth = GuidewireClient(auth_type="OAuth2", api_key="oauth-bearer-token")
    headers = c_oauth._build_headers()
    assert headers["Authorization"] == "Bearer oauth-bearer-token"


# ============================================================================
# 3. Payload and Mock Execution
# ============================================================================

@pytest.mark.asyncio
async def test_guidewire_send_case_update_mock_mode():
    client = GuidewireClient(mock_mode=True)

    matched_cases = [
        {
            "CaseNumber": "2026-111719-CC-26",
            "CaseStyle": "TOLEDO VS GONZALEZ",
            "CountyWebsite": "https://www2.miamidadeclerk.gov/ocs/",
            "SuitFiledDate": "08/21/2026",
        }
    ]

    res = await client.send_case_update(
        claim_number="123456789",  # 9 digits -> 0123456789
        exposure_number="1",
        matched_cases=matched_cases,
    )

    assert res["success"] is True
    assert res["status_code"] == 200
    assert "response" in res
    assert res["response"]["mock"] is True
    assert res["response"]["activityId"].startswith("MOCK-ACT-")

    payload = res["payload_sent"]
    assert payload["ClaimNumber"] == "0123456789"
    assert payload["ExposureNumber"] == "1"
    assert len(payload["CaseItems"]) == 1
    assert payload["CaseItems"][0]["CaseNumber"] == "2026-111719-CC-26"


# ============================================================================
# 4. Live Request Simulation (Mocked httpx)
# ============================================================================

@pytest.mark.asyncio
async def test_guidewire_send_case_update_live_success():
    client = GuidewireClient(
        api_url="https://gw.example.com/api/caseupdate",
        auth_type="Bearer",
        api_key="valid-token",
        mock_mode=False,
    )

    mock_resp = httpx.Response(
        status_code=200,
        json={"ActivityID": "GW-ACT-99001", "status": "CREATED"},
        request=httpx.Request("POST", "https://gw.example.com/api/caseupdate"),
    )

    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_resp)):
        res = await client.send_case_update(
            claim_number="0100234567",
            exposure_number="1",
            matched_cases=[{"CaseNumber": "C-1", "CaseStyle": "A vs B"}],
        )

    assert res["success"] is True
    assert res["status_code"] == 200
    assert res["response"]["ActivityID"] == "GW-ACT-99001"


@pytest.mark.asyncio
async def test_guidewire_send_case_update_live_unauthorized():
    client = GuidewireClient(
        api_url="https://gw.example.com/api/caseupdate",
        mock_mode=False,
    )

    mock_resp = httpx.Response(
        status_code=401,
        text='{"error": "Unauthorized", "status": 401}',
        request=httpx.Request("POST", "https://gw.example.com/api/caseupdate"),
    )

    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_resp)):
        res = await client.send_case_update(
            claim_number="0100234567",
            exposure_number="1",
            matched_cases=[],
        )

    assert res["success"] is False
    assert res["status_code"] == 401
    assert "response_body" in res


# ============================================================================
# 5. Interactive Test Connection Runner
# ============================================================================

@pytest.mark.asyncio
async def test_guidewire_interactive_test_connection():
    client = GuidewireClient(mock_mode=True)
    req = GuidewireTestRequest(
        api_url="https://test.guidewire.com/caseupdate",
        auth_type="Bearer",
        api_key="token-12345678",
        mock_mode=True,
    )

    result = await client.test_connection(req)
    assert result.success is True
    assert result.status_code == 200
    assert result.request_url == "https://test.guidewire.com/caseupdate"
    assert "Authorization" in result.request_headers
    # Make sure token was masked for security
    assert "***" in result.request_headers["Authorization"]
