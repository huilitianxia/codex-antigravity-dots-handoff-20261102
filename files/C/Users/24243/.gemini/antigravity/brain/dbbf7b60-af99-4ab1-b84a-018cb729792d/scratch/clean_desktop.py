import os, sys, json, shutil
sys.stdout.reconfigure(encoding='utf-8')
R = r'E:\Desktop'
items = json.load(open(r'D:\4A\_桌面归档清单_20261101.json', encoding='utf-8'))['items']
before = shutil.disk_usage('E:\\').free
ok, fail = 0, []
for n in items:
    p = os.path.join(R, n)
    if os.path.dirname(os.path.abspath(p)).lower() != R.lower():
        fail.append((n, 'unexpected path')); continue
    try:
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
        ok += 1
    except Exception as e:
        fail.append((n, str(e)))
after = shutil.disk_usage('E:\\').free
print('removed', ok, 'failed', len(fail))
for f in fail: print(' FAIL', f)
print('E free GB: %.1f -> %.1f' % (before / 2**30, after / 2**30))
print('remaining items on Desktop:', len(os.listdir(R)))
