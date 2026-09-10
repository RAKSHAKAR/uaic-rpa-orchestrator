from typing import Literal

from pydantic import BaseModel, Field


class FuzzyMatchRequest(BaseModel):
    text1: str = Field(..., min_length=1, description="Text to look for")
    text2: str = Field(..., min_length=1, description="Text to search within")
    threshold: float = Field(
        0.6, ge=0, le=1, description="Minimum match score (0-1) to count as a match"
    )


class FuzzyMatchResponse(BaseModel):
    result: Literal["Match Found", "No Match Found"]
    score: float
