with open("backend/app/automation/florida/hillsborough.py", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "first_input = page.locator(" in line or "dol_input = page.locator(" in line:
        skip = True
        continue
    if skip and line.strip() == ")":
        skip = False
        continue
    if not skip:
        new_lines.append(line)

with open("backend/app/automation/florida/hillsborough.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned unused locators in hillsborough.py")

