"""Script to generate production-accurate sample Excel and CSV claim files matching ProdRecords1-500.xlsx."""

import os

import pandas as pd

# Exactly matches the 12 production columns from ProdRecords1-500.xlsx
SAMPLE_DATA = [
    {
        "Primary Key": 2077302,
        "Insured First Name": "LADEEN",
        "Insured Last Name": "MCCRAY DAVIS",
        "DOL": "12/06/2022",
        "Driver First Name (Insured Vehicle)": "LADEEN",
        "Driver Last Name (Insured Vehicle)": "MCCRAY DAVIS",
        "Policy State": "Florida",
        "Claim Number": 100303098,
        "Loss Location State": "Florida",
        "Exposure Number": 2,
        "Claimant First Name": "LaDeen",
        "Claimant Last Name": "McCray-Davis",
    },
    {
        "Primary Key": 2062855,
        "Insured First Name": "TIFFANY LATONYA",
        "Insured Last Name": "YOUNG",
        "DOL": "01/04/2022",
        "Driver First Name (Insured Vehicle)": "TIFFANY LATONYA",
        "Driver Last Name (Insured Vehicle)": "YOUNG",
        "Policy State": "Florida",
        "Claim Number": 100298095,
        "Loss Location State": "Florida",
        "Exposure Number": 1,
        "Claimant First Name": "TIFFANY LATONYA",
        "Claimant Last Name": "YOUNG",
    },
    {
        "Primary Key": 2071806,
        "Insured First Name": "CORNELIUS",
        "Insured Last Name": "BRIGHT",
        "DOL": "01/12/2021",
        "Driver First Name (Insured Vehicle)": "Aquaria",
        "Driver Last Name (Insured Vehicle)": "Mitchell",
        "Policy State": "Florida",
        "Claim Number": 100301036,
        "Loss Location State": "Florida",
        "Exposure Number": 1,
        "Claimant First Name": "Felicia",
        "Claimant Last Name": "Mcmiller",
    },
    {
        "Primary Key": 2075412,
        "Insured First Name": "MICHAEL",
        "Insured Last Name": "JOHNSON",
        "DOL": "05/18/2023",
        "Driver First Name (Insured Vehicle)": "MICHAEL",
        "Driver Last Name (Insured Vehicle)": "JOHNSON",
        "Policy State": "Texas",
        "Claim Number": 100305112,
        "Loss Location State": "Texas",
        "Exposure Number": 1,
        "Claimant First Name": "William",
        "Claimant Last Name": "Taylor",
    },
    {
        "Primary Key": 2078901,
        "Insured First Name": "PATRICIA",
        "Insured Last Name": "BROWN",
        "DOL": "08/22/2023",
        "Driver First Name (Insured Vehicle)": "PATRICIA",
        "Driver Last Name (Insured Vehicle)": "BROWN",
        "Policy State": "Texas",
        "Claim Number": 100307844,
        "Loss Location State": "Texas",
        "Exposure Number": 1,
        "Claimant First Name": "Richard",
        "Claimant Last Name": "Jackson",
    },
]

df = pd.DataFrame(SAMPLE_DATA)

# Output paths
backend_static = os.path.join(os.path.dirname(__file__), "..", "app", "static")
frontend_public = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")

os.makedirs(backend_static, exist_ok=True)
os.makedirs(frontend_public, exist_ok=True)

# Generate Excel
excel_backend = os.path.join(backend_static, "sample_claims.xlsx")
excel_frontend = os.path.join(frontend_public, "sample_claims.xlsx")
df.to_excel(excel_backend, index=False)
df.to_excel(excel_frontend, index=False)

# Generate CSV
csv_backend = os.path.join(backend_static, "sample_claims.csv")
csv_frontend = os.path.join(frontend_public, "sample_claims.csv")
df.to_csv(csv_backend, index=False)
df.to_csv(csv_frontend, index=False)

print(f"Generated sample files in {backend_static} and {frontend_public}")
