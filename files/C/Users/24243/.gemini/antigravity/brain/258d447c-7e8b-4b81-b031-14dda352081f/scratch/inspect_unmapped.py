import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json", 'r', encoding='utf-8') as f:
    entities = json.load(f)

from test_classification import classify_entity

unmapped = [ent for ent in entities.values() if classify_entity(ent) == 'FAM_UNMAPPED']
print(f"Total unmapped: {len(unmapped)}")
for u in unmapped[:35]:
    print(f"SKU: '{u.get('sku')}' | ASIN: '{u.get('asin')}' | Title: '{u.get('title')[:60]}' | Sources: {u.get('sources')}")
