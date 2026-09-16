"""Utility script to clean encoding and code block artifacts in implementation_plan markdown files."""
import pathlib

def clean_docs():
    # 1. master-gap-analysis.md
    p1 = pathlib.Path("implementation_plan/master-gap-analysis.md")
    if p1.exists():
        t1 = p1.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
        t1 = t1.replace("`\text", "```text").replace("\n`\n", "\n```\n")
        p1.write_text(t1, encoding="utf-8")
        print("master-gap-analysis.md cleaned.")

    # 2. master-walkthrough.md
    p2 = pathlib.Path("implementation_plan/master-walkthrough.md")
    if p2.exists():
        t2 = p2.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
        t2 = t2.replace("`\text", "```text").replace("\n`\n\n**Status:**", "\n```\n\n**Status:**")
        p2.write_text(t2, encoding="utf-8")
        print("master-walkthrough.md cleaned.")

    # 3. 2026-09-15_uaic_v4_parity_audit_final_record_v1.md
    p3 = pathlib.Path("implementation_plan/2026-09-15_uaic_v4_parity_audit_final_record_v1.md")
    if p3.exists():
        raw = p3.read_bytes()
        raw = raw.replace(b'\xc3\xa2\xc2\x9d\xc5\x92', '❌'.encode('utf-8'))
        p3.write_bytes(raw)
        print("2026-09-15_uaic_v4_parity_audit_final_record_v1.md cleaned.")

    # 4. 2026-09-15_uaic_final_acceptance_matrix_and_v4_issues_v1.md
    p4 = pathlib.Path("implementation_plan/2026-09-15_uaic_final_acceptance_matrix_and_v4_issues_v1.md")
    if p4.exists():
        t4 = p4.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
        t4 = t4.replace("\test_broward_header_filter", "`test_broward_header_filter`")
        t4 = t4.replace("\x0ciling_date", "filing_date")
        t4 = t4.replace("\test_miami_filing_date_empty_fallback", "`test_miami_filing_date_empty_fallback`")
        t4 = t4.replace("\x08reak", "break")
        t4 = t4.replace("\test_miami_card_parser_label_map", "`test_miami_card_parser_label_map`")
        t4 = t4.replace("\test_hillsborough_pagination", "`test_hillsborough_pagination`")
        t4 = t4.replace("\x07wait", "await")
        p4.write_text(t4, encoding="utf-8")
        print("2026-09-15_uaic_final_acceptance_matrix_and_v4_issues_v1.md cleaned.")

if __name__ == "__main__":
    clean_docs()
