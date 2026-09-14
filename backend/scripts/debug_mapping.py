import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend"))

from app.services.excel_parser import auto_detect_column_mapping

cols = [
    "Primary Key",
    "Insured First Name",
    "Insured Last Name",
    "DOL",
    "Driver First Name (Insured Vehicle)",
    "Driver Last Name (Insured Vehicle)",
    "Policy State",
    "Claim Number",
    "Loss Location State",
    "Loss Location City",
    "Loss Location County",
    "Exposure Number",
    "Claimant First Name",
    "Claimant Last Name"
]

recs = auto_detect_column_mapping(cols)
for r in recs:
    print(r["target_key"], "->", r["source_column"])

