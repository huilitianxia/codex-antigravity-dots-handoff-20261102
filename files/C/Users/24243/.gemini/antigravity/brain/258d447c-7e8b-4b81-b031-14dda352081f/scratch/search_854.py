import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

parent_dir = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d"

# search transcript for 854
transcript_path = os.path.join(parent_dir, ".system_generated", "logs", "transcript.jsonl")
if os.path.exists(transcript_path):
    print("Searching transcript.jsonl for 854...")
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if "854" in line:
                print(f"Line {idx} mentions 854: {line[:200]}")

# search for files in parent scratch
for f in os.listdir(os.path.join(parent_dir, "scratch")):
    p = os.path.join(parent_dir, "scratch", f)
    if os.path.isfile(p) and p.endswith(('.js', '.mjs', '.py', '.txt', '.json')):
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                c = fp.read()
                if "854" in c:
                    print(f"File {f} mentions 854!")
        except Exception:
            pass
