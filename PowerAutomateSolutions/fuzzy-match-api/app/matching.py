from rapidfuzz import fuzz


def is_match(text1: str, text2: str, threshold: float) -> tuple[str, float]:
    """Check whether text1 is present in text2, case-insensitively.

    Uses partial_ratio so text1 can match a substring of text2 without being
    penalized for the length difference between the two strings.
    """
    normalized1 = text1.strip().lower()
    normalized2 = text2.strip().lower()

    score = fuzz.partial_ratio(normalized1, normalized2)
    result = "Match Found" if score >= threshold * 100 else "No Match Found"
    return result, score
