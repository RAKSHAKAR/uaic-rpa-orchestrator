from fastapi import FastAPI

from app.matching import is_match
from app.models import FuzzyMatchRequest, FuzzyMatchResponse

app = FastAPI(title="Fuzzy Match API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/fuzzymatchapi", response_model=FuzzyMatchResponse)
def fuzzy_match(payload: FuzzyMatchRequest) -> FuzzyMatchResponse:
    result, score = is_match(payload.text1, payload.text2, payload.threshold)
    return FuzzyMatchResponse(result=result, score=score)
