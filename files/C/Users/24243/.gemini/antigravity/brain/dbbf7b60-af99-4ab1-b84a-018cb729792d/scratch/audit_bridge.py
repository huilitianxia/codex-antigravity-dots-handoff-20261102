import zipfile, re, sys, hashlib, json
sys.stdout.reconfigure(encoding='utf-8')
z = zipfile.ZipFile(r'E:\OpenAI-Codex\天皇のcodex\outputs\Antigravity-Context-Bridge-1.0.0.zip')
src = z.read('antigravity-context-bridge/context-bridge/scripts/bridge.py').decode('utf-8')
print('lines', src.count('\n'))
pat = r'import (socket|urllib|requests|http|ftplib|smtplib|subprocess|ctypes|webbrowser)|from (urllib|http|subprocess)|os\.remove|os\.unlink|rmtree|shutil\.|os\.system|eval\(|exec\(|__import__|\.gemini|expanduser|Path\.home|open\(|write_text|unlink|rename|replace\('
for i, l in enumerate(src.splitlines(), 1):
    if re.search(pat, l):
        print(i, l.strip()[:150])
print('--- import lines ---')
for l in src.splitlines():
    if l.startswith(('import ', 'from ')):
        print(l)
sums = json.loads(z.read('antigravity-context-bridge/SHA256SUMS.json'))
bad = []
for k, v in sums.items():
    name = 'antigravity-context-bridge/' + k
    try:
        h = hashlib.sha256(z.read(name)).hexdigest()
        if h != v: bad.append(k)
    except KeyError:
        bad.append(k + ' (missing)')
print('sha256 entries', len(sums), 'mismatch', bad)
