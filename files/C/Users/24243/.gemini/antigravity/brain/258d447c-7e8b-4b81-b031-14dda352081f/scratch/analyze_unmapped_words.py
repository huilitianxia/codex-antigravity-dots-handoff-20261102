import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json", 'r', encoding='utf-8') as f:
    entities = json.load(f)

from test_classification import classify_entity

unmapped = [ent for ent in entities.values() if classify_entity(ent) == 'FAM_UNMAPPED']
print(f"Total unmapped: {len(unmapped)}")

words = Counter()
for u in unmapped:
    title = (u.get('title') or '') + " " + (u.get('sku') or '')
    for w in title.upper().split():
        if len(w) > 2:
            words[w] += 1

print("Top keywords in unmapped:")
for w, c in words.most_common(40):
    print(f"  {w}: {c}")

print("\nSample 25 unmapped titles:")
for u in unmapped[:25]:
    print(f"SKU: '{u.get('sku')}' | ASIN: '{u.get('asin')}' | Title: '{u.get('title')[:70]}'")
