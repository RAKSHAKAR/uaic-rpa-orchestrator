import json

p = r'C:\Users\priyer\.gemini\antigravity-ide\brain\08905db1-04bf-40f4-8bfa-8e79acf462e2\.system_generated\logs\transcript.jsonl'
with open(p, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            txt = data.get('content', '')[:120].replace('\n', ' ')
            print(f"Step {data.get('step_index')}: {txt}")
