import pandas as pd

df = pd.read_excel('Testing files/sample_claims - Florida.xlsx')
for idx, row in df.iterrows():
    c = f"{row['Claimant First Name']} {row['Claimant Last Name']}"
    i = f"{row['Insured First Name']} {row['Insured Last Name']}"
    d = f"{row['Driver First Name (Insured Vehicle)']} {row['Driver Last Name (Insured Vehicle)']}"
    print(f"Row {idx} [Claim {row['Claim Number']}]:")
    print(f"  Claimant: {c}")
    print(f"  Insured:  {i}")
    print(f"  Driver:   {d}")
    print(f"  Unique:   {list(dict.fromkeys([c, i, d]))}")
