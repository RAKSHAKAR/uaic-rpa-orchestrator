import json

path = r"C:\Users\priyer\.gemini\antigravity-ide\brain\8aab3435-51dd-4fe7-935c-be310e748637\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        if '"step_index":1106' in line:
            obj = json.loads(line)
            with open("scripts/step1106_content.txt", "w", encoding="utf-8") as out:
                out.write(obj.get("content", ""))
            print("WROTE CONTENT SUCCESSFULLY, length:", len(obj.get("content", "")))
            break
