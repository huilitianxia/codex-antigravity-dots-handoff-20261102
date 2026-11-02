import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\.system_generated\logs\transcript.jsonl"
with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx in [2312, 2314, 2355, 2356, 2357]:
            obj = json.loads(line)
            print(f"=== Step {obj.get('step_index')} ({obj.get('type')}, {obj.get('source')}) ===")
            content = obj.get('content', '')
            print(content[:1500])
            print("...")
            print(content[-500:])
