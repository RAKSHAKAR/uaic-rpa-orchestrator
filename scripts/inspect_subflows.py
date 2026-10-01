import os

path = os.path.join(os.path.dirname(__file__), 'extracted_v4_flow.robin')
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

subflows = [
    ("Subflow_Broward", 173, 334),
    ("Subflow_Dallas", 335, 476),
    ("Subflow_Travis", 477, 616),
    ("Subflow_Harris (Harris JP)", 617, 832),
    ("Subflow_Cclerk (Harris County Clerk)", 833, 900),
    ("Subflow_Miami", 901, 1108),
    ("Subflow_HarrisDistrict", 1109, 1204),
    ("Subflow_Hillsborough", 1205, 1390),
]

for name, start, end in subflows:
    print("=" * 80)
    print(f"  {name.upper()} (Lines {start}-{end})")
    print("=" * 80)
    for i in range(start - 1, end):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            continue
        if any(keyword in line for keyword in [
            'WebAutomation', 'UIAutomation', 'PopulateTextField', 'Click', 'SelectOption',
            'ExtractTable', 'ExecuteJavascript', 'WaitFor', 'SendKeys', 'PressKey', 'GoToWebPage',
            'LABEL', 'SET'
        ]):
            print(f"  Line {i+1:>4}: {line}")
    print()
