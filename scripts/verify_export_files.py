import json
import csv
import openpyxl
import os

print("=== VERIFYING SAVED EXPORT FILES ===")

# 1. JSON
json_path = "scratch_test_32b240c2.json"
try:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[JSON PASS] Successfully parsed JSON. Claim Number: {data.get('claim_number')}, Keys: {list(data.keys())[:6]}")
except Exception as e:
    print(f"[JSON FAIL] {e}")

# 2. CSV
csv_path = "scratch_test_32b240c2.csv"
try:
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    print(f"[CSV PASS] Successfully parsed CSV. Total rows: {len(rows)}, Header: {rows[0] if rows else []}")
except Exception as e:
    print(f"[CSV FAIL] {e}")

# 3. XLSX
xlsx_path = "scratch_test_32b240c2.xlsx"
try:
    wb = openpyxl.load_workbook(xlsx_path)
    sheet_names = wb.sheetnames
    print(f"[XLSX PASS] Successfully opened Excel workbook! Sheets: {sheet_names}")
    for name in sheet_names:
        sheet = wb[name]
        print(f"   Sheet '{name}': {sheet.max_row} rows, {sheet.max_column} columns")
except Exception as e:
    print(f"[XLSX FAIL] {e}")

# 4. PDF
pdf_path = "scratch_test_32b240c2.pdf"
try:
    size = os.path.getsize(pdf_path)
    with open(pdf_path, "rb") as f:
        header = f.read(10)
        f.seek(-32, os.SEEK_END)
        footer = f.read(32)
    is_valid_header = header.startswith(b"%PDF-")
    has_eof = b"%%EOF" in footer or b"EOF" in footer
    print(f"[PDF CHECK] Size: {size} bytes, Header: {header}, Valid Header: {is_valid_header}, Has EOF: {has_eof}")
    
    # Try reading with PyPDF/pypdf or pypdf2 or pdfminer if available
    try:
        import importlib
        pypdf = importlib.import_module("pypdf")
        reader = pypdf.PdfReader(pdf_path)
        print(f"[PDF PASS] Successfully loaded PDF via pypdf! Pages: {len(reader.pages)}")
    except ImportError:
        print("   (pypdf not installed, checking via Playwright or Chrome)")
except Exception as e:
    print(f"[PDF FAIL] {e}")
