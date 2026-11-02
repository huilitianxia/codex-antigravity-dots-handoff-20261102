"""Search archived UTF-8 conversations and project text without executing project code."""
from pathlib import Path
import argparse
p=argparse.ArgumentParser(description=__doc__);p.add_argument('query');p.add_argument('--limit',type=int,default=100);p.add_argument('--scope',choices=['conversations','files','all'],default='conversations');a=p.parse_args()
root=Path(__file__).resolve().parent.parent;base=root if a.scope=='all' else root/a.scope;count=0
for f in base.rglob('*'):
 if not f.is_file() or any(x in f.parts for x in ['.git','.local']):continue
 try:
  with f.open(encoding='utf-8') as lines:
   for i,line in enumerate(lines,1):
    if a.query.casefold() in line.casefold():
     print(f'{f.relative_to(root)}:{i}: {line.strip()[:1200]}');count+=1
     if count>=a.limit:raise SystemExit(0)
 except (UnicodeError,OSError):continue
