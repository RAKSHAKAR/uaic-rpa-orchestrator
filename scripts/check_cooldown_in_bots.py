"""Audit and verify security block detection and real WAF cooldown handling across all 8 county bots."""

import re

BOTS = [
    ("backend/app/automation/florida/broward.py", "fl_broward"),
    ("backend/app/automation/florida/hillsborough.py", "fl_hillsborough"),
    ("backend/app/automation/florida/miami.py", "fl_miami"),
    ("backend/app/automation/texas/travis.py", "te_travis"),
    ("backend/app/automation/texas/dallas.py", "te_dallas"),
    ("backend/app/automation/texas/harris_jp.py", "te_harris_jp"),
    ("backend/app/automation/texas/harris_cclerk.py", "te_harris_cclerk"),
    ("backend/app/automation/texas/harris_district.py", "te_harris_district"),
]

for path, key in BOTS:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    has_import = "SecurityBlockException" in content
    count_detect = content.count("detect_security_block")
    has_raise = "raise SecurityBlockException" in content
    print(
        f"{key:20} -> import: {str(has_import):5} | detect_security_block calls: {count_detect:2d} | raises SecurityBlockException: {has_raise}"
    )

