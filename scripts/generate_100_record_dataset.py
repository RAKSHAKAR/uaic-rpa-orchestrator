"""Generate UAIC 100-Record Cross-State Test Dataset (UAIC_100_RECORD_CROSS_STATE_TEST_DATA.xlsx).

Requirements:
- Exactly 100 records.
- 3 distinct individuals per record: Driver, Insured, Claimant (300 individual user identities).
- Validated via generate_unique_names_for_claim to guarantee exactly 3 distinct search targets per row.
- Cross-State routing: Policy State = 'FL', Loss Location State = 'TX' (triggers all 8 county bots).
- DOL formatted in MM/DD/YYYY (Excel 1899-12-30 epoch compliant).
- Columns mapped strictly to TARGET_CLAIM_FIELDS in app/services/excel_parser.py.
"""

import os
import sys
from datetime import date, timedelta

# Ensure backend is on pythonpath
sys.path.insert(0, os.path.abspath("backend"))

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from app.services.fuzzy_engine import generate_unique_names_for_claim

# 100 Distinct Drivers
DRIVERS = [
    ("Liam", "Smith"),
    ("Noah", "Johnson"),
    ("Oliver", "Williams"),
    ("James", "Brown"),
    ("Elijah", "Jones"),
    ("William", "Garcia"),
    ("Henry", "Miller"),
    ("Lucas", "Davis"),
    ("Benjamin", "Rodriguez"),
    ("Theodore", "Martinez"),
    ("Mateo", "Hernandez"),
    ("Levi", "Lopez"),
    ("Sebastian", "Gonzalez"),
    ("Daniel", "Wilson"),
    ("Jack", "Anderson"),
    ("Michael", "Thomas"),
    ("Alexander", "Taylor"),
    ("Owen", "Moore"),
    ("Asher", "Jackson"),
    ("Samuel", "Martin"),
    ("Ethan", "Lee"),
    ("Leo", "Perez"),
    ("Jackson", "Thompson"),
    ("Mason", "White"),
    ("Ezra", "Harris"),
    ("John", "Sanchez"),
    ("Hudson", "Clark"),
    ("Luca", "Ramirez"),
    ("David", "Lewis"),
    ("Jacob", "Robinson"),
    ("Logan", "Walker"),
    ("Luke", "Young"),
    ("Julian", "Allen"),
    ("Gabriel", "King"),
    ("Grayson", "Wright"),
    ("Wyatt", "Scott"),
    ("Matthew", "Torres"),
    ("Maverick", "Nguyen"),
    ("Dylan", "Hill"),
    ("Isaac", "Flores"),
    ("Elias", "Green"),
    ("Anthony", "Adams"),
    ("Thomas", "Nelson"),
    ("Jayden", "Baker"),
    ("Carter", "Hall"),
    ("Santiago", "Rivera"),
    ("Ezekiel", "Campbell"),
    ("Charles", "Mitchell"),
    ("Josiah", "Carter"),
    ("Caleb", "Roberts"),
    ("Cooper", "Gomez"),
    ("Lincoln", "Phillips"),
    ("Miles", "Evans"),
    ("Christopher", "Turner"),
    ("Nathan", "Diaz"),
    ("Isaiah", "Parker"),
    ("Kai", "Cruz"),
    ("Joshua", "Edwards"),
    ("Andrew", "Collins"),
    ("Angel", "Reyes"),
    ("Adrian", "Stewart"),
    ("Cameron", "Morris"),
    ("Nolan", "Morales"),
    ("Waylon", "Murphy"),
    ("Jaxon", "Cook"),
    ("Roman", "Rogers"),
    ("Eli", "Gutierrez"),
    ("Wesley", "Ortiz"),
    ("Aaron", "Morgan"),
    ("Ian", "Cooper"),
    ("Christian", "Peterson"),
    ("Ryan", "Bailey"),
    ("Leonardo", "Reed"),
    ("Brooks", "Kelly"),
    ("Axel", "Howard"),
    ("Walker", "Ramos"),
    ("Jonathan", "Kim"),
    ("Easton", "Cox"),
    ("Everett", "Ward"),
    ("Weston", "Richardson"),
    ("Bennett", "Watson"),
    ("Robert", "Brooks"),
    ("Greyson", "Chavez"),
    ("Nicholas", "Wood"),
    ("Beau", "James"),
    ("Dominic", "Bennett"),
    ("Austin", "Gray"),
    ("Silas", "Mendoza"),
    ("Amir", "Ruiz"),
    ("Colton", "Hughes"),
    ("Jordan", "Price"),
    ("Luca", "Alvarez"),
    ("Carson", "Castillo"),
    ("Jeremiah", "Sanders"),
    ("Gael", "Patel"),
    ("Rowan", "Myers"),
    ("Micah", "Long"),
    ("Emmett", "Ross"),
    ("River", "Foster"),
    ("Declan", "Jimenez"),
]

# 100 Distinct Insureds
INSUREDS = [
    ("Emma", "Powell"),
    ("Olivia", "Jenkins"),
    ("Amelia", "Perry"),
    ("Sophia", "Russell"),
    ("Charlotte", "Sullivan"),
    ("Ava", "Bell"),
    ("Isabella", "Coleman"),
    ("Mia", "Butler"),
    ("Evelyn", "Henderson"),
    ("Harper", "Barnes"),
    ("Luna", "Gonzales"),
    ("Camila", "Fisher"),
    ("Gianna", "Vasquez"),
    ("Elizabeth", "Simmons"),
    ("Eleanor", "Romero"),
    ("Ella", "Jordan"),
    ("Abigail", "Patterson"),
    ("Sofia", "Alexander"),
    ("Avery", "Hamilton"),
    ("Scarlett", "Graham"),
    ("Emily", "Reynolds"),
    ("Aria", "Griffin"),
    ("Penelope", "Wallace"),
    ("Chloe", "Moreno"),
    ("Layla", "West"),
    ("Mila", "Cole"),
    ("Nora", "Atkins"),
    ("Hazel", "Bryant"),
    ("Madison", "Herrera"),
    ("Ellie", "Gibson"),
    ("Lily", "Ellis"),
    ("Nova", "Tran"),
    ("Isla", "Medina"),
    ("Grace", "Aguilar"),
    ("Violet", "Stevens"),
    ("Aurora", "Murray"),
    ("Riley", "Ford"),
    ("Zoey", "Castro"),
    ("Willow", "Marshall"),
    ("Emilia", "Owens"),
    ("Stella", "Harrison"),
    ("Zoe", "Fernandez"),
    ("Victoria", "Mcdonald"),
    ("Hannah", "Woods"),
    ("Addison", "Washington"),
    ("Leah", "Kennedy"),
    ("Lucy", "Wells"),
    ("Eliana", "Vargas"),
    ("Ivy", "Henry"),
    ("Everly", "Chen"),
    ("Lillian", "Freeman"),
    ("Paisley", "Webb"),
    ("Elena", "Tucker"),
    ("Naomi", "Guzman"),
    ("Maya", "Burns"),
    ("Natalie", "Crawford"),
    ("Kinsley", "Olson"),
    ("Delilah", "Simpson"),
    ("Claire", "Porter"),
    ("Audrey", "Hunter"),
    ("Aaliyah", "Gordon"),
    ("Ruby", "Mendez"),
    ("Brooklyn", "Silva"),
    ("Alice", "Shaw"),
    ("Aubrey", "Snyder"),
    ("Autumn", "Mason"),
    ("Leilani", "Dixon"),
    ("Savannah", "Munoz"),
    ("Valentina", "Hunt"),
    ("Kennedy", "Hicks"),
    ("Madelyn", "Holmes"),
    ("Josephine", "Palmer"),
    ("Bella", "Wagner"),
    ("Skylar", "Black"),
    ("Genesis", "Robertson"),
    ("Sophie", "Boyd"),
    ("Hailey", "Rose"),
    ("Sadie", "Stone"),
    ("Natalia", "Salazar"),
    ("Quinn", "Fox"),
    ("Caroline", "Warren"),
    ("Allison", "Mills"),
    ("Gabriella", "Meyer"),
    ("Anna", "Rice"),
    ("Serenity", "Schmidt"),
    ("Nevaeh", "Garza"),
    ("Cora", "Daniels"),
    ("Ariana", "Ferguson"),
    ("Lydia", "Nichols"),
    ("Jade", "Stephens"),
    ("Peyton", "Soto"),
    ("Marie", "Ray"),
    ("Eva", "Grant"),
    ("Adeline", "Carr"),
    ("Madeline", "Larson"),
    ("Clara", "Hart"),
    ("Vivian", "Weber"),
    ("Maeve", "Willis"),
    ("Sarah", "Dunn"),
    ("Melanie", "Pierce"),
]

# 100 Distinct Claimants
CLAIMANTS = [
    ("Marcus", "Vance"),
    ("Darius", "Holt"),
    ("Trevor", "Newton"),
    ("Victor", "Ball"),
    ("Bryce", "Monroe"),
    ("Preston", "Booth"),
    ("Garrett", "Barrett"),
    ("Colin", "Hampton"),
    ("Simon", "Shepard"),
    ("Malcolm", "Lowery"),
    ("Tristan", "Holloway"),
    ("Damian", "Barlow"),
    ("Seth", "Barton"),
    ("Cody", "Bradshaw"),
    ("Spencer", "Hensley"),
    ("Grant", "Odom"),
    ("Travis", "Mcbride"),
    ("Devin", "Davenport"),
    ("Jesse", "Browning"),
    ("Curtis", "Garrison"),
    ("Brendan", "Pratt"),
    ("Derek", "Hardy"),
    ("Troy", "Hodge"),
    ("Tanner", "Goodman"),
    ("Keith", "Moon"),
    ("Dustin", "Shields"),
    ("Shane", "Flynn"),
    ("Brett", "Combs"),
    ("Corey", "Manning"),
    ("Russell", "Bridges"),
    ("Clayton", "Hancock"),
    ("Bradley", "Roth"),
    ("Ross", "Small"),
    ("Wesley", "Short"),
    ("Clint", "Duke"),
    ("Darren", "English"),
    ("Casey", "Carson"),
    ("Lance", "Burch"),
    ("Heath", "Frost"),
    ("Brent", "Vaughn"),
    ("Quinton", "Love"),
    ("Dillon", "Rowe"),
    ("Reece", "Finley"),
    ("Zachary", "Spence"),
    ("Phillip", "Rich"),
    ("Wade", "Key"),
    ("Brock", "Dudley"),
    ("Clark", "Kirby"),
    ("Dane", "Hale"),
    ("Landon", "Giles"),
    ("Maxwell", "Kirk"),
    ("Dalton", "Beach"),
    ("Reid", "Golden"),
    ("Graham", "Prince"),
    ("Gage", "Harding"),
    ("Donovan", "Glass"),
    ("Mitchell", "Henson"),
    ("Trenton", "Mckee"),
    ("Chandler", "Mcguire"),
    ("Desmond", "Underwood"),
    ("Solomon", "Pacheco"),
    ("Damien", "Pearson"),
    ("Leon", "Salas"),
    ("Kobe", "Hardin"),
    ("Warren", "Bowers"),
    ("Alberto", "Villarreal"),
    ("Armando", "Puckett"),
    ("Derrick", "Riddle"),
    ("Erick", "Bauer"),
    ("Gerardo", "Mckenzie"),
    ("Marshall", "Callahan"),
    ("Raymond", "Ochoa"),
    ("Eddie", "Parrish"),
    ("Julio", "Lester"),
    ("Enrique", "Mccullough"),
    ("Arturo", "Beard"),
    ("Hector", "Glover"),
    ("Ruben", "Mayo"),
    ("Ramon", "Hess"),
    ("Raul", "Mcconnell"),
    ("Hugo", "Potts"),
    ("Pedro", "Cherry"),
    ("Alfonso", "Snider"),
    ("Orlando", "Mullen"),
    ("Guillermo", "Wilkins"),
    ("Salvador", "Dillon"),
    ("Ramiro", "Benton"),
    ("Felipe", "Browning"),
    ("Ignacio", "Curry"),
    ("Tomas", "Savage"),
    ("Rodrigo", "Dodson"),
    ("Ernesto", "English"),
    ("Gustavo", "Hurley"),
    ("Saul", "Vance"),
    ("Alonso", "Cochran"),
    ("Jaime", "Livingston"),
    ("Rogelio", "Holloway"),
    ("Alfredo", "Oconnor"),
    ("Esteban", "Whitaker"),
    ("Moises", "Buck"),
]

BASE_DOL = date(2024, 1, 15)

rows = []
for i in range(100):
    drv_fn, drv_ln = DRIVERS[i]
    ins_fn, ins_ln = INSUREDS[i]
    clm_fn, clm_ln = CLAIMANTS[i]

    claim_num = f"CLM-2026-XSTATE-{i+1:03d}"
    primary_k = f"PK-2026-XSTATE-{i+1:03d}"
    dol_val = (BASE_DOL + timedelta(days=i * 3)).strftime("%m/%d/%Y")

    # Validate using genuine UAIC unique names extractor
    mock_claim = {
        "insured_first_name": ins_fn,
        "insured_last_name": ins_ln,
        "driver_first_name": drv_fn,
        "driver_last_name": drv_ln,
        "claimant_first_name": clm_fn,
        "claimant_last_name": clm_ln,
    }
    extracted_names = generate_unique_names_for_claim(
        mock_claim, fuzzy_threshold=0.60
    )
    if len(extracted_names) != 3:
        raise ValueError(
            f"Row {i+1} did not generate exactly 3 distinct search targets (got {len(extracted_names)}): "
            f"Driver='{drv_fn} {drv_ln}', Insured='{ins_fn} {ins_ln}', Claimant='{clm_fn} {clm_ln}'"
        )

    rows.append(
        {
            "Test Record ID": i + 1,
            "Claim Number": claim_num,
            "Primary Key": primary_k,
            "Exposure Number": "001",
            "DOL": dol_val,
            "Policy State": "FL",
            "Loss Location State": "TX",
            "Execution Mode": "Cross-State",
            "Driver First Name": drv_fn,
            "Driver Last Name": drv_ln,
            "Insured First Name": ins_fn,
            "Insured Last Name": ins_ln,
            "Claimant First Name": clm_fn,
            "Claimant Last Name": clm_ln,
            "Target fl_broward": "Yes",
            "Target fl_hillsborough": "Yes",
            "Target fl_miami": "Yes",
            "Target te_travis": "Yes",
            "Target te_dallas": "Yes",
            "Target te_harris_jp": "Yes",
            "Target te_harris_cclerk": "Yes",
            "Target te_harris_district": "Yes",
            "Expected Distinct Searches": 3,
            "Batch Identifier": "BATCH-2026-1103-XSTATE-001",
            "Test Data Indicator": "SYNTHETIC_CROSS_STATE_100REC",
        }
    )

df = pd.DataFrame(rows)

out_path = "UAIC_100_RECORD_CROSS_STATE_TEST_DATA.xlsx"

with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="CrossState_100Records", index=False)
    wb = writer.book
    ws = wb["CrossState_100Records"]

    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(
        start_color="1E3A8A", end_color="1E3A8A", fill_type="solid"
    )
    border_thin = Side(style="thin", color="CBD5E1")
    cell_border = Border(
        left=border_thin, right=border_thin, top=border_thin, bottom=border_thin
    )
    data_font = Font(name="Segoe UI", size=10, color="0F172A")
    alt_fill = PatternFill(
        start_color="F8FAFC", end_color="F8FAFC", fill_type="solid"
    )

    for col_idx, col in enumerate(ws.columns, start=1):
        header_cell = col[0]
        header_cell.font = header_font
        header_cell.fill = header_fill
        header_cell.alignment = Alignment(horizontal="center", vertical="center")

        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        for row_idx, cell in enumerate(col[1:], start=2):
            cell.font = data_font
            cell.border = cell_border
            if row_idx % 2 == 0:
                cell.fill = alt_fill
            if col_idx in (1, 4, 5, 6, 7, 8, 15, 16, 17, 18, 19, 20, 21, 22, 23):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    ws.freeze_panes = "A2"

print(f"Successfully generated {out_path} with {len(df)} records!")
