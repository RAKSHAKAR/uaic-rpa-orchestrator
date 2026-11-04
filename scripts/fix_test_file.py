with open('backend/tests/test_imp_2026_1031_003.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'from app.services.excel_parser import parse_excel_or_csv, resolve_county_bot_targets',
    'from app.services.excel_parser import validate_and_normalize_claim_data, resolve_county_bot_targets'
)
old_block = """    csv_bytes = df.to_csv(index=False).encode("utf-8")

    result = parse_excel_or_csv(io.BytesIO(csv_bytes), "test_missing.csv")"""
new_block = """    result = validate_and_normalize_claim_data(df)"""
text = text.replace(old_block, new_block)

with open('backend/tests/test_imp_2026_1031_003.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('test_imp_2026_1031_003.py updated successfully')

