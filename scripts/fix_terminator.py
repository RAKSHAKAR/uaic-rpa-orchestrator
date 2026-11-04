path = r"d:\scratch\Bot_UAIC\e2e\run_all_e2e_tests.ps1"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "</html>" in line and '"@' in line:
        new_lines.append("</html>\n")
        new_lines.append('"@\n')
    else:
        new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned terminator in run_all_e2e_tests.ps1")

