import json

with open(r'C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\ss_217940.json', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

print("Keys:", list(data.keys()))
