import json

with open(r'C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\ss_217940.json', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

print("Total items:", len(data.get('items', [])))
for it in data.get('items', []):
    s = str(it)
    if '30315' in s or 'FKG29KB' in s or 'F295DPC' in s:
        print(f"SKU: {it.get('sku')}, ASIN: {it.get('asin')}, Price: {it.get('price')}, Status: {it.get('status')}, Fulfillment: {it.get('fulfillment')}")
