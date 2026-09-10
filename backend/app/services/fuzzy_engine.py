"""RapidFuzz Matching and Deduplication Engine."""

import logging
import re
from datetime import datetime
from typing import Any

from rapidfuzz import fuzz

from app.core.config import settings
from app.models.match_result import MatchReviewStatusEnum, PartyTypeEnum

logger = logging.getLogger("uaic_orchestrator.fuzzy_engine")


def strip_noise_patterns(text: str, noise_patterns: list[str] | None = None) -> str:
    """Strips corporate noise and legal suffix words configured in settings."""
    if not text or not noise_patterns:
        return text or ""
    sorted_patterns = sorted([p.strip() for p in noise_patterns if p.strip()], key=len, reverse=True)
    if not sorted_patterns:
        return text
    regex_parts = []
    for p in sorted_patterns:
        escaped = re.escape(p)
        regex_parts.append(r"(?:^|\b|\s)" + escaped + r"(?:\b|\s|$)")
    combined = re.compile("|".join(regex_parts), re.IGNORECASE)
    cleaned = combined.sub(" ", text)
    # Clean dangling commas/periods before conjunctions or at end
    cleaned = re.sub(r"[,;]+\s*(?=and\b|\bv[s.]*\b|$)", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[\s,.-]+$", "", cleaned.strip())
    return re.sub(r"\s+", " ", cleaned).strip()


def clean_case_style(case_style: str | None, noise_patterns: list[str] | None = None) -> str:
    """
    Clean raw case style string mirroring legacy Power Automate flow:
    - Replaces CRLF, LF, non-breaking space (\\xa0) with spaces
    - Removes parentheses ()
    - Condenses multiple consecutive spaces into single space
    - Trims leading and trailing whitespace
    - Optionally strips configured corporate noise patterns
    """
    if not case_style:
        return ""
    
    text = str(case_style)
    # Remove carriage returns and line feeds
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    # Remove non-breaking spaces
    text = text.replace("\xa0", " ")
    # Remove parentheses
    text = text.replace("(", "").replace(")", "")
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    if noise_patterns:
        text = strip_noise_patterns(text, noise_patterns)
    return text


def clean_party_name(
    first_name: str | None,
    last_name: str | None,
    noise_patterns: list[str] | None = None,
) -> str:
    """Combines and cleans party first and last name, stripping noise words if provided."""
    f = (first_name or "").strip()
    l = (last_name or "").strip()
    full = f"{f} {l}".strip()
    full = re.sub(r"\s+", " ", full)
    if noise_patterns:
        full = strip_noise_patterns(full, noise_patterns)
    return full


def is_case_eligible(
    filing_date: str | None,
    case_status: str | None,
    case_type: str | None,
    min_filing_date: str = "2010-01-01",
    allowed_statuses: list[str] | None = None,
    allowed_types: list[str] | None = None,
) -> bool:
    """
    Validates if court case meets business criteria:
    1. FilingDate >= 2010-01-01
    2. CaseStatus is in allowed statuses (or empty)
    3. CaseType is in allowed types (or empty)
    """
    allowed_statuses = allowed_statuses or settings.ALLOWED_CASE_STATUSES
    allowed_types = allowed_types or settings.ALLOWED_CASE_TYPES

    # Check filing date if present
    if filing_date:
        f_date = str(filing_date).strip()
        parsed_dt = None
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y"]:
            try:
                parsed_dt = datetime.strptime(f_date, fmt)
                break
            except ValueError:
                pass

        if parsed_dt:
            min_dt = datetime.strptime(min_filing_date, "%Y-%m-%d")
            if parsed_dt < min_dt:
                return False

    # Check Case Status
    if case_status:
        st_clean = case_status.strip().upper()
        if st_clean:
            matches_status = any(st_clean in allowed.upper() or allowed.upper() in st_clean for allowed in allowed_statuses)
            if not matches_status:
                return False

    # Check Case Type
    if case_type:
        ct_clean = case_type.strip().upper()
        if ct_clean:
            matches_type = any(ct_clean in allowed.upper() or allowed.upper() in ct_clean for allowed in allowed_types)
            if not matches_type:
                return False

    return True


SCORER_MAP = {
    "token_sort_ratio": fuzz.token_sort_ratio,
    "token_set_ratio": fuzz.token_set_ratio,
    "partial_ratio": fuzz.partial_ratio,
    "ratio": fuzz.ratio,
}


def calculate_match_score(
    party_name: str,
    case_style: str,
    scorer_algorithm: str = "token_sort_ratio",
) -> float:
    """
    Calculates fuzzy similarity between party name and case style based on configured scorer algorithm.
    Supported algorithms from settings: token_sort_ratio, token_set_ratio, partial_ratio, ratio.
    Returns normalized score between 0.0 and 1.0.
    """
    if not party_name or not case_style:
        return 0.0

    p_norm = party_name.lower().strip()
    c_norm = case_style.lower().strip()

    # Token containment score
    p_tokens = set(re.findall(r"\b\w+\b", p_norm))
    c_tokens = set(re.findall(r"\b\w+\b", c_norm))
    
    containment_score = 0.0
    if p_tokens:
        matched_tokens = p_tokens.intersection(c_tokens)
        containment_score = len(matched_tokens) / len(p_tokens)

    scorer_fn = SCORER_MAP.get(scorer_algorithm.lower(), fuzz.token_sort_ratio)
    raw_algo_score = scorer_fn(p_norm, c_norm) / 100.0

    if scorer_algorithm.lower() == "token_set_ratio":
        final_score = max(raw_algo_score, containment_score if containment_score == 1.0 else 0.0)
    elif scorer_algorithm.lower() == "partial_ratio":
        final_score = max(raw_algo_score, containment_score if containment_score == 1.0 else 0.0)
    elif scorer_algorithm.lower() == "ratio":
        final_score = raw_algo_score
    else:
        # Default composite (token_sort_ratio with token_set / WRatio fallback)
        token_score = fuzz.token_set_ratio(p_norm, c_norm) / 100.0
        partial_score = fuzz.partial_ratio(p_norm, c_norm) / 100.0
        w_score = fuzz.WRatio(p_norm, c_norm) / 100.0
        final_score = max(raw_algo_score, token_score, partial_score, w_score, containment_score)

    return round(final_score, 4)


def evaluate_case_against_parties(
    case: dict[str, Any],
    claimant_name: str,
    insured_name: str,
    driver_name: str,
    threshold: float = 0.60,
    borderline_threshold: float = 0.40,
    scorer_algorithm: str = "token_sort_ratio",
    noise_patterns: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Evaluates a single court case against the 3 parties (Claimant, Insured, Driver).
    Returns list of comparison results for each party adhering to configured scorer and noise patterns.
    """
    raw_style = case.get("CaseStyle") or case.get("case_style") or ""
    cleaned_style = clean_case_style(raw_style, noise_patterns=noise_patterns)

    parties = [
        (PartyTypeEnum.CLAIMANT, claimant_name),
        (PartyTypeEnum.INSURED, insured_name),
        (PartyTypeEnum.DRIVER, driver_name),
    ]

    results = []
    for party_type, p_name in parties:
        if not p_name:
            continue

        score = calculate_match_score(p_name, cleaned_style, scorer_algorithm=scorer_algorithm)
        is_positive_match = score >= threshold
        
        if is_positive_match:
            review_status = MatchReviewStatusEnum.AUTO_MATCHED
        elif score >= borderline_threshold:
            review_status = MatchReviewStatusEnum.PENDING_REVIEW
        else:
            review_status = MatchReviewStatusEnum.REJECTED

        results.append({
            "party_type": party_type,
            "party_name": p_name,
            "case_style": cleaned_style,
            "similarity_score": score,
            "threshold_applied": threshold,
            "is_match": is_positive_match,
            "review_status": review_status,
            "court_case": case,
        })

    return results
