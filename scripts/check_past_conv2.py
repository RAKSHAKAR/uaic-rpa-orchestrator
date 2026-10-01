import json

p = r'C:\Users\priyer\.gemini\antigravity-ide\brain\0474f91b-fae2-412c-92fb-2503ed1dcb45\.system_generated\logs\transcript.jsonl'
with open(p, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            txt = data.get('content', '')[:120].replace('\n', ' ')
            print(f"Step {data.get('step_index')}: {txt}")
