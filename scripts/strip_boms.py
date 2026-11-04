from pathlib import Path

files_with_bom = [
    Path(".agents/skills/diagnose-plan-confirm-execute/SKILL.md"),
    Path("e2e/README.md"),
    Path("scripts/diag_claims.py"),
    Path("scripts/diag_claims2.py"),
    Path("scripts/diag_claims3.py"),
    Path("scripts/diag_errors.py"),
    Path("scripts/diag_fail_errs.py"),
    Path("scripts/diag_schema.py"),
    Path("scripts/diag_settings.py"),
    Path("scripts/pytest_result.txt"),
    Path("scripts/verify_live_fleet.py"),
]

for p in files_with_bom:
    if p.is_file():
        data = p.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            p.write_bytes(data[3:])
            print(f"Stripped BOM from: {p}")
        else:
            print(f"No BOM in: {p}")
    else:
        print(f"File not found: {p}")

