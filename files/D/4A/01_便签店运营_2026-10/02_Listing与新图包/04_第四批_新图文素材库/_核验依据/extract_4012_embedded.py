from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import posixpath,json
p=Path('C:/Users/24243/Documents/Codex/2026-08-11/7-30-slack-plugin-slack-openai/4A_Amazon_Operations/source_workbooks/亚马逊供应商和开店总表-2026 (1).xlsx')
out=Path('E:/Desktop/待上架_新图文素材库_第四批/_核验依据')
ns={'xdr':'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
found=[]
with ZipFile(p) as z:
 for d in z.namelist():
  if not d.startswith('xl/drawings/drawing') or not d.endswith('.xml'):continue
  relpath=posixpath.dirname(d)+'/_rels/'+posixpath.basename(d)+'.rels'
  if relpath not in z.namelist():continue
  rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read(relpath))}
  for anchor in ET.fromstring(z.read(d)):
   start=anchor.find('xdr:from/xdr:row',ns);end=anchor.find('xdr:to/xdr:row',ns)
   if start is None:continue
   lo=int(start.text)+1;hi=int(end.text)+1 if end is not None else lo
   if not(lo<=72<=hi or lo==71):continue
   for blip in anchor.findall('.//a:blip',ns):
    rid=blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    target=rels.get(rid,'')
    target=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.dirname(d)+'/'+target)
    if target in z.namelist():
     dest=out/('4012_Excel_'+posixpath.basename(target));dest.write_bytes(z.read(target));found.append({'drawing':d,'row_from':lo,'row_to':hi,'file':str(dest)})
print(json.dumps(found,ensure_ascii=False))
