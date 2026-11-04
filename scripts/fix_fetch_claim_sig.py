from pathlib import Path

claims_page = Path("frontend/src/app/claims/[id]/page.tsx")
content = claims_page.read_text(encoding="utf-8")

old_sig = "  const fetchClaim = useCallback(async (isSilent = false) => {"
new_sig = """  const fetchClaim = useCallback(async (isSilentOrEvent: boolean | any = false) => {
    const isSilent = isSilentOrEvent === true;"""

assert old_sig in content, "old_sig not found"
content = content.replace(old_sig, new_sig, 1)

claims_page.write_text(content, encoding="utf-8")
print("Updated fetchClaim signature")

