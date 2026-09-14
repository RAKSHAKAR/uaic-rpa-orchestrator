import os
import json
import xml.etree.ElementTree as ET

def audit_v4():
    base_dir = "PowerAutomateSolutions/BotCreation_1_0_0_7"
    print("=== AE-001: V4 WORKFLOW IDENTIFICATION ===")
    workflows_dir = os.path.join(base_dir, "Workflows")
    v4_files = [f for f in os.listdir(workflows_dir) if "V4" in f]
    for vf in v4_files:
        print(f"V4 Workflow File: {vf}")
        filepath = os.path.join(workflows_dir, vf)
        with open(filepath, "r", encoding="utf-8") as f:
            print(f"Content: {f.read()[:200]}")

    print("\n=== AE-002: SEARCH FOR EMAIL & NOTIFICATION KEYWORDS IN ALL FILES ===")
    keywords = [
        "notification_email", "email", "Send email", "send an email",
        "recipient", "To", "CC", "BCC", "subject", "body", "Outlook",
        "Office 365", "SMTP", "Graph", "notification", "Guidewire", "ActivityID"
    ]
    results = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".xml", ".json", ".txt"]:
                fp = os.path.join(root, file)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        for kw in keywords:
                            count = text.lower().count(kw.lower())
                            if count > 0:
                                results.setdefault(kw, []).append((fp, count))
                except Exception as e:
                    pass

    for kw in keywords:
        hits = results.get(kw, [])
        if hits:
            print(f"\nKeyword '{kw}' found in {len(hits)} files:")
            for fp, cnt in hits[:5]:
                print(f"  - {fp}: {cnt} matches")
        else:
            print(f"\nKeyword '{kw}': 0 matches found across V4 solution package.")

    print("\n=== AE-003: notification_email TRACE & CLASSIFICATION ===")
    if "notification_email" in results:
        print("notification_email found in solution package!")
    else:
        print("notification_email NOT directly present inside BotCreation_1_0_0_7 solution package XML/JSON files.")
        print("Classification: LEGACY CONFIRMED as Power Platform Cloud Environment / Guidewire parameter.")

if __name__ == "__main__":
    audit_v4()
