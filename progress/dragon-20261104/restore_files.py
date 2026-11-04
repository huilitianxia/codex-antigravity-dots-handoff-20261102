"""Restore the lossless business archive from a local clone. Does not run business scripts."""
from pathlib import Path
import argparse,hashlib,json,tarfile,tempfile

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='restored');a=p.parse_args()
 root=Path(__file__).resolve().parent;dest=Path(a.output).resolve();dest.mkdir(parents=True,exist_ok=True)
 m=json.loads((root/'BUNDLE.json').read_text());h=hashlib.sha256()
 with tempfile.TemporaryFile()as stream:
  for item in m['parts']:
   data=(root/item['name']).read_bytes()
   if len(data)!=item['bytes']or hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Damaged archive part: '+item['name'])
   h.update(data);stream.write(data)
  if h.hexdigest()!=m['sha256']:raise ValueError('Archive hash mismatch')
  stream.seek(0)
  with tarfile.open(fileobj=stream,mode='r:gz')as tar:
   for member in tar.getmembers():
    target=(dest/member.name).resolve()
    if not target.is_relative_to(dest)or member.issym()or member.islnk():raise ValueError('Unsafe archive path')
    if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
    data=tar.extractfile(member).read();target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists()and target.read_bytes()!=data:raise ValueError('Refusing to overwrite different file: '+str(target))
    target.write_bytes(data)
 manifest=json.loads((root/'SOURCE_MANIFEST.json').read_text())['files']
 for item in manifest:
  rel=item.get('archive_path') or 'files/'+item['same_content_as'];target=dest/rel
  if hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Restored hash mismatch: '+rel)
 print('Verified',len(manifest),'business files. No business scripts were executed.')
if __name__=='__main__':main()
