import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

conv_path = r"C:\Users\24243\.gemini\antigravity\brain\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b"
if os.path.exists(conv_path):
    print("Found f1367eb9-fa19-4a11-abf4-4dc63e32dd4b")
    steps_dir = os.path.join(conv_path, ".system_generated", "steps")
    if os.path.exists(steps_dir):
        steps = sorted([int(x) for x in os.listdir(steps_dir) if x.isdigit()])
        print(f"Total steps: {len(steps)}, min={steps[0]}, max={steps[-1]}")
