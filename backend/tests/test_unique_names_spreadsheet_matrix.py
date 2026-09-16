"""Tests for Unique Names Deduplication Engine Matrix.
Validates all 10 rows from the user's Excel spreadsheet (Rows 2 to 11)
across both the service layer (generate_unique_names_for_claim) and the API endpoint
(/api/v1/matches/unique-names) with fuzzy_threshold=0.60.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.claim import ClaimRecord
from app.services.fuzzy_engine import (
    derive_search_counts_fuzzy,
    generate_unique_names_for_claim,
)

SPREADSHEET_10_ROWS = [
    (
        2,
        {"first": "MARIA", "last": "MARTINEZ"},
        {"first": "MARIA", "last": "MARTINEZ"},
        {"first": "MARIA", "last": "MARTINEZ"},
        ["MARIA MARTINEZ"],
        (1, 1),
    ),
    (
        3,
        {"first": "LADEEN", "last": "MCCRAY DAVIS"},
        {"first": "LADEEN", "last": "MCCRAY DAVIS"},
        {"first": "LaDeen", "last": "McCray-Davis"},
        ["LADEEN MCCRAY DAVIS"],
        (1, 1),
    ),
    (
        4,
        {"first": "SERGIO", "last": "GONZALEZ"},
        {"first": "SERGIO", "last": "GONZALEZ"},
        {"first": "SERGIO", "last": "GONZALEZ"},
        ["SERGIO GONZALEZ"],
        (1, 1),
    ),
    (
        5,
        {"first": "TIFFANY LATONYA", "last": "YOUNG"},
        {"first": "TIFFANY LATONYA", "last": "YOUNG"},
        {"first": "TIFFANY LATONYA", "last": "YOUNG"},
        ["TIFFANY LATONYA YOUNG"],
        (1, 1),
    ),
    (
        6,
        {"first": "CRYSTAL", "last": "BROWN"},
        {"first": "CRYSTAL", "last": "BROWN"},
        {"first": "CRYSTAL", "last": "BROWN"},
        ["CRYSTAL BROWN"],
        (1, 1),
    ),
    (
        7,
        {"first": "CORNELIUS", "last": "BRIGHT"},
        {"first": "Aquaria", "last": "Mitchell"},
        {"first": "Felicia", "last": "Mcmiller"},
        ["CORNELIUS BRIGHT", "Aquaria Mitchell", "Felicia Mcmiller"],
        (2, 3),
    ),
    (
        8,
        {"first": "ASHLEY", "last": "RODRIGUEZ"},
        {"first": "ASHLEY", "last": "RODRIGUEZ"},
        {"first": "ASHLEY", "last": "RODRIGUEZ"},
        ["ASHLEY RODRIGUEZ"],
        (1, 1),
    ),
    (
        9,
        {"first": "EMANUEL", "last": "TORRES"},
        {"first": "EMANUEL", "last": "TORRES"},
        {"first": "EMANUEL", "last": "TORRES"},
        ["EMANUEL TORRES"],
        (1, 1),
    ),
    (
        10,
        {"first": "CESAR", "last": "ARIAS"},
        {"first": "CESAR", "last": "ARIAS"},
        {"first": "CESAR", "last": "ARIAS"},
        ["CESAR ARIAS"],
        (1, 1),
    ),
    (
        11,
        {"first": "ARMANDO", "last": "FERNANDEZ HERNANDEZ"},
        {"first": "ARMANDO", "last": "FERNANDEZ HERNANDEZ"},
        {"first": "Jorge", "last": "Bencomo Santana"},
        ["ARMANDO FERNANDEZ HERNANDEZ", "Jorge Bencomo Santana"],
        (1, 3),
    ),
]


@pytest.mark.parametrize(
    "row_num,insured,driver,claimant,expected_names,expected_counts",
    SPREADSHEET_10_ROWS,
)
def test_spreadsheet_matrix_service_layer(
    row_num, insured, driver, claimant, expected_names, expected_counts
):
    """Verify each spreadsheet row directly in generate_unique_names_for_claim service."""
    claim = ClaimRecord(
        claim_number=f"ROW-{row_num:03d}",
        insured_first_name=insured["first"],
        insured_last_name=insured["last"],
        driver_first_name=driver["first"],
        driver_last_name=driver["last"],
        claimant_first_name=claimant["first"],
        claimant_last_name=claimant["last"],
    )

    unique_names = generate_unique_names_for_claim(claim, fuzzy_threshold=0.60)
    assert len(unique_names) == len(expected_names), f"Row {row_num} count mismatch"
    extracted_names = [item["name"] for item in unique_names]
    assert extracted_names == expected_names, f"Row {row_num} names mismatch: {extracted_names} != {expected_names}"

    # Verify search order numbers
    for idx, item in enumerate(unique_names, start=1):
        assert item["target_number"] == idx
        assert item["search_order"] == idx
        assert item["party_type"].lower() in ["insured", "driver", "claimant"]

    # Verify dual/triple search counters
    dual, triple = derive_search_counts_fuzzy(claim, fuzzy_threshold=0.60)
    assert (dual, triple) == expected_counts, f"Row {row_num} count mismatch: {(dual, triple)} != {expected_counts}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "row_num,insured,driver,claimant,expected_names,expected_counts",
    SPREADSHEET_10_ROWS,
)
async def test_spreadsheet_matrix_api_endpoint_3_arrays(
    row_num, insured, driver, claimant, expected_names, expected_counts
):
    """Verify /api/v1/matches/unique-names endpoint with 3-array request payload structure."""
    payload = {
        "Claimants": [
            {"FirstName": claimant["first"], "LastName": claimant["last"], "MiddleName": "", "Suffix": ""}
        ],
        "Insureds": [
            {"FirstName": insured["first"], "LastName": insured["last"], "MiddleName": "", "Suffix": ""}
        ],
        "Drivers": [
            {"FirstName": driver["first"], "LastName": driver["last"], "MiddleName": "", "Suffix": ""}
        ],
        "threshold": 0.60,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/unique-names", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_unique_names"] == len(expected_names)
    assert data["count"] == len(expected_names)
    assert len(data["unique_names"]) == len(expected_names)
    assert "dual_search" not in data
    assert "triple_search" not in data
    assert "claim_number" not in data

    extracted_names = [item["name"] for item in data["unique_names"]]
    assert extracted_names == expected_names, f"Row {row_num} API names mismatch: {extracted_names} != {expected_names}"


@pytest.mark.asyncio
async def test_unique_names_api_exact_user_maria_martinez():
    """Verify exact payload specified in the user prompt for Maria Martinez."""
    payload = {
        "Claimants": [
            {"FirstName": "MARIA", "LastName": "MARTINEZ", "MiddleName": "", "Suffix": ""}
        ],
        "Insureds": [
            {"FirstName": "MARIA", "LastName": "MARTINEZ", "MiddleName": "", "Suffix": ""}
        ],
        "Drivers": [
            {"FirstName": "MARIA", "LastName": "MARTINEZ", "MiddleName": "", "Suffix": ""}
        ],
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/unique-names", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_unique_names"] == 1
    assert data["count"] == 1
    assert "dual_search" not in data
    assert "triple_search" not in data
    assert "claim_number" not in data
    assert len(data["unique_names"]) == 1
    assert data["unique_names"][0]["name"] == "MARIA MARTINEZ"
    assert data["unique_names"][0]["target_number"] == 1
    assert data["unique_names"][0]["party_type"].lower() == "insured"


@pytest.mark.asyncio
async def test_unique_names_api_exact_user_cornelius_bright():
    """Verify exact payload specified by user for Cornelius Bright, Aquaria Mitchell, Felicia Mcmiller."""
    payload = {
        "Claimants": [
            {"FirstName": "CORNELIUS", "LastName": "BRIGHT", "MiddleName": "", "Suffix": ""}
        ],
        "Insureds": [
            {"FirstName": "Aquaria", "LastName": "Mitchell", "MiddleName": "", "Suffix": ""}
        ],
        "Drivers": [
            {"FirstName": "Felicia", "LastName": "Mcmiller", "MiddleName": "", "Suffix": ""}
        ],
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/unique-names", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_unique_names"] == 3
    assert data["count"] == 3
    assert len(data["unique_names"]) == 3
    names = [u["name"] for u in data["unique_names"]]
    assert "Aquaria Mitchell" in names
    assert "Felicia Mcmiller" in names
    assert "CORNELIUS BRIGHT" in names


@pytest.mark.asyncio
async def test_unique_names_api_flat_backward_compatibility():
    """Verify backwards-compatible flat fields: insured_first_name, driver_first_name, claimant_first_name."""
    payload = {
        "insured_first_name": "JOHN",
        "insured_last_name": "DOE",
        "driver_first_name": "JANE",
        "driver_last_name": "DOE",
        "claimant_first_name": "JOHN",
        "claimant_last_name": "DOE",
        "threshold": 0.60,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/matches/unique-names", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()

    # Insured (JOHN DOE) + Driver (JANE DOE) = 2 unique names (Claimant JOHN DOE duplicates Insured)
    assert data["total_unique_names"] == 2
    assert data["unique_names"][0]["name"] == "JOHN DOE"
    assert data["unique_names"][1]["name"] == "JANE DOE"
