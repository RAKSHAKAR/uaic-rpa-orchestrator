from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sample_request_matches():
    response = client.post(
        "/fuzzymatchapi",
        json={
            "text1": " Miami Dade Police Department",
            "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
            "threshold": 0.6,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "Match Found"
    assert body["score"] >= 60


def test_clear_non_match():
    response = client.post(
        "/fuzzymatchapi",
        json={
            "text1": "Miami Dade Police Department",
            "text2": "Completely unrelated text about bicycles",
            "threshold": 0.6,
        },
    )
    assert response.status_code == 200
    assert response.json()["result"] == "No Match Found"


def test_case_insensitivity():
    lower = client.post(
        "/fuzzymatchapi",
        json={"text1": "miami dade police", "text2": "miami dade police department", "threshold": 0.6},
    ).json()
    upper = client.post(
        "/fuzzymatchapi",
        json={"text1": "MIAMI DADE POLICE", "text2": "MIAMI DADE POLICE DEPARTMENT", "threshold": 0.6},
    ).json()
    assert lower["result"] == "Match Found"
    assert upper["result"] == "Match Found"
    assert lower["score"] == upper["score"]


def test_default_threshold_applied_when_omitted():
    response = client.post(
        "/fuzzymatchapi",
        json={
            "text1": "Miami Dade Police Department",
            "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
        },
    )
    assert response.status_code == 200
    assert response.json()["result"] == "Match Found"


def test_threshold_out_of_range_rejected():
    response = client.post(
        "/fuzzymatchapi",
        json={"text1": "a", "text2": "a", "threshold": 1.5},
    )
    assert response.status_code == 422


def test_empty_text_rejected():
    response = client.post(
        "/fuzzymatchapi",
        json={"text1": "", "text2": "something", "threshold": 0.6},
    )
    assert response.status_code == 422
