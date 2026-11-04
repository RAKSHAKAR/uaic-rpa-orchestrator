"""Update _WAF_SIGNATURE_MAP in error_classifier.py to include 'waf rate limit' and 'rate limit'."""

from pathlib import Path

file_path = Path("backend/app/services/error_classifier.py")
text = file_path.read_text(encoding="utf-8")

old_block = """    (
        ["429 too many requests", "rate limit exceeded", "too many requests", "rate limited",
         "request limit reached", "retry after"],
        ErrorCode.WAF_RATE_LIMIT,
        600,
    ),"""

new_block = """    (
        ["waf rate limit", "rate limit", "429 too many requests", "rate limit exceeded", "too many requests", "rate limited",
         "request limit reached", "retry after", "429"],
        ErrorCode.WAF_RATE_LIMIT,
        600,
    ),"""

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    file_path.write_text(text, encoding="utf-8")
    print("SUCCESS: Updated _WAF_SIGNATURE_MAP with rate limit variants.")
else:
    print("ERROR: old_block not found.")

