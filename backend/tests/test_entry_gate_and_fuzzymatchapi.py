from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.settings import SystemSettings


@pytest.mark.asyncio
async def test_fuzzy_match_direct_array():
    """Test that fuzzymatchapi accepts an array and evaluates multiple targets."""
    payload = {
        "reference_string": "JOHN DOE",
        "target_strings": ["john doe", "jon do", "jane smith", "johnny doe"],
        "threshold": 0.85
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/fuzzymatchapi", json=payload)
        
    assert response.status_code == 200, response.text
    data = response.json()
    
    assert data["reference_string"] == "JOHN DOE"
    assert data["threshold_applied"] == 85.0
    assert len(data["matches"]) == 4
    
    # Check exact match
    match_1 = next(m for m in data["matches"] if m["target_string"] == "john doe")
    assert match_1["score"] == 100.0
    assert match_1["result"] == "Match Found"
    
    # Check non-match
    match_2 = next(m for m in data["matches"] if m["target_string"] == "jane smith")
    assert match_2["score"] < 85.0
    assert match_2["result"] == "No Match Found"


@pytest.mark.asyncio
async def test_entry_gate_blocks_missing_anticaptcha():
    """Test that start endpoints block execution if anti-captcha is missing."""
    
    # Create a mock settings object without Anti-Captcha key
    mock_settings = SystemSettings()
    mock_settings.automation.anticaptcha_api_key = ""
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # We need a valid claim ID, we can just use a random UUID, since it checks claim first
        # But wait, start_single_claim checks DB first. If it's a random UUID it returns 404.
        # Let's mock the db or create a real one. We can mock get_system_settings_async.
        
        with patch("app.api.v1.endpoints.claims.get_system_settings_async", return_value=mock_settings), \
             patch("app.api.v1.endpoints.queue.get_system_settings_async", return_value=mock_settings), \
             patch("app.api.v1.endpoints.claims.select"), \
             patch("app.api.v1.endpoints.claims.Depends"):
             
             # The easiest way without DB is bulk-start with empty list -> returns 200. Wait, bulk-start returns 200 if empty.
             # Wait, in claims.py, bulk-start checks claim_ids first. Let's pass a dummy id.
             # But it executes DB query.
             
             # Actually, toggle_auto_queue_mode doesn't query DB!
             response = await client.post("/api/v1/queue/auto-mode", json={"enabled": True})
             assert response.status_code == 422
             assert "Anti-Captcha API key is not configured" in response.text
             
             # Also test run-next
             response = await client.post("/api/v1/queue/run-next")
             assert response.status_code == 422
             assert "Anti-Captcha API key is not configured" in response.text
             
             # Also test start-all
             # start-all queries DB for stuck claims.
