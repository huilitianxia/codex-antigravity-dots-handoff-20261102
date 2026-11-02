"""Download, verify and restore this archive's binary/native files. Python stdlib only."""
from pathlib import Path
import argparse,hashlib,json,os,urllib.request,urllib.parse,zipfile,shutil,subprocess,fnmatch

repo=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--download',action='store_true')
parser.add_argument('--packages',type=Path,default=repo/'.local/packages')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--verify-only',action='store_true')
parser.add_argument('--match',action='append',help='Restore/download only paths matching this glob; may be repeated.')
args=parser.parse_args();args.packages.mkdir(parents=True,exist_ok=True)
packages=json.loads((repo/'manifests/payload-packages.json').read_text('utf-8'))
rows=[json.loads(line) for line in (repo/'manifests/payload-files.jsonl').read_text('utf-8').splitlines()]
if args.match:
 rows=[x for x in rows if any(fnmatch.fnmatchcase(x['path'],pattern) for pattern in args.match)]
 if not rows:raise SystemExit('No paths matched the requested glob.')
 names={x['package'] for x in rows};packages=[p for p in packages if p['name'] in names]
def fs(p):
 p=Path(p)
 return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' and not str(p).startswith('\\\\?\\') else p
def digest(p):
 with fs(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
class SafeRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
  if redirected and urllib.parse.urlsplit(req.full_url).netloc!=urllib.parse.urlsplit(newurl).netloc:redirected.remove_header('Authorization')
  return redirected
opener=urllib.request.build_opener(SafeRedirect())
def request(url,token,accept='application/vnd.github+json'):
 return opener.open(urllib.request.Request(url,headers={'Authorization':'Bearer '+token,'Accept':accept,'X-GitHub-Api-Version':'2022-11-28','User-Agent':'Dots-Archive-Restore'}),timeout=120)
if args.download:
 token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
 if not token:
  result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GCM_INTERACTIVE':'never'})
  token=next((s.partition('=')[2] for s in result.stdout.splitlines() if s.startswith('password=')),None)
 if not token:raise SystemExit('Use an existing GitHub login or set GH_TOKEN with read access to this private repository.')
 with request('https://api.github.com/repos/huilitianxia/codex-antigravity-dots-handoff-20261102/releases/tags/4a-business-20261102',token) as r:release=json.load(r)
 assets={};page=1
 while True:
  with request(release['assets_url']+'?per_page=100&page='+str(page),token) as r:batch=json.load(r)
  assets.update((a['name'],a) for a in batch)
  if len(batch)<100:break
  page+=1
 for p in packages:
  dest=args.packages/p['name']
  if dest.is_file() and dest.stat().st_size==p['bytes'] and digest(dest)==p['sha256']:continue
  asset=assets.get(p['name'])
  if not asset:raise SystemExit('Missing release asset: '+p['name'])
  temp=dest.with_suffix('.downloading')
  with request(asset['url'],token,'application/octet-stream') as r,temp.open('wb') as f:shutil.copyfileobj(r,f)
  if temp.stat().st_size!=p['bytes'] or digest(temp)!=p['sha256']:raise SystemExit('Download verification failed: '+p['name'])
  temp.replace(dest);print('Downloaded and verified',p['name'])
for p in packages:
 source=args.packages/p['name']
 if not source.is_file() or source.stat().st_size!=p['bytes'] or digest(source)!=p['sha256']:raise SystemExit('Package missing or checksum mismatch: '+p['name'])
print('All package checksums verified.')
if args.verify_only:raise SystemExit(0)
root=args.output.resolve();root.mkdir(parents=True,exist_ok=True);handles={};count=0
try:
 for x in rows:
   target=(root/x['path']).resolve()
   if not target.is_relative_to(root):raise SystemExit('Unsafe target path')
   fs(target.parent).mkdir(parents=True,exist_ok=True)
   if fs(target).exists():
    if fs(target).is_file() and digest(target)==x['sha256']:continue
    raise SystemExit('Refusing to overwrite different existing file: '+str(target))
   if x['package'] not in handles:handles[x['package']]=zipfile.ZipFile(args.packages/x['package'])
   temp=target.with_name(target.name+'.restoring')
   with handles[x['package']].open(x['entry']) as src,fs(temp).open('wb') as dst:shutil.copyfileobj(src,dst)
   if fs(temp).stat().st_size!=x['bytes'] or digest(temp)!=x['sha256']:raise SystemExit('Object checksum mismatch: '+x['path'])
   fs(temp).replace(fs(target));count+=1
finally:
 for h in handles.values():h.close()
print('Restored',count,'files to',root)
