import json

with open("data/processed/pages.jsonl", "r", encoding="utf-8") as f:
    pages = [json.loads(line) for line in f]

with open("scratch_investigate.txt", "w", encoding="utf-8") as out:
    for p in pages[:5]:
        out.write(f"--- PAGE {p['page']} ---\n")
        lines = p['text'].split('\n')
        out.write("FIRST 3 LINES:\n")
        for l in lines[:3]:
            out.write(f"{repr(l)}\n")
        out.write("LAST 3 LINES:\n")
        for l in lines[-3:] if len(lines) >= 3 else lines:
            out.write(f"{repr(l)}\n")
        out.write("\n")
