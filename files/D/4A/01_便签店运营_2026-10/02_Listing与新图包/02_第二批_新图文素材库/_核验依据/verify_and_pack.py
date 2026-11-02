import json,hashlib,zipfile,struct
from pathlib import Path
root=Path(r'E:\Desktop\待上架_新图文素材库_第二批')
entries=[]
for folder in ['305FullAdhesive','608NL210','BS1801']:
    m=json.loads((root/folder/'manifest.json').read_text(encoding='utf-8'))
    assert len(m['images'])==5
    for e in m['images']:
        p=root/folder/e['file'];b=p.read_bytes()
        assert b[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II',b[16:24])==(2000,2000)
        assert hashlib.sha256(b).hexdigest()==e['sha256']
        assert (root/folder/e['generation_source']).exists()
        if e['role']=='main':
            t=e['technical_checks']
            assert t['white_background_pass'] and t['margin_pass'] and t['occupancy_pass']
        entries.append({'id':e['id'],'dimensions':[2000,2000],'hash_match':True,'source_exists':True,'status':e['review_status']})
assert len(entries)==15
report={'date':'2026-10-30','count':15,'image_checks':entries,'html_review':{'all_preview_images_loaded':True,'horizontal_overflow':False},'visual_review':'逐图检查数量、产品结构、颜色、文字；608色序及单张纸厚已返修；2张精确尺寸图已目视检查。','limitations':'305胶区及移除性能待核；所有生成产品仍需实物批次核样。'}
(root/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
out=root.parent/'待上架_新图文素材库_第二批_15张_20261030.zip'
if out.exists(): raise RuntimeError('Existing ZIP; choose new version')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in root.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(root))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    files=len(z.infolist())
print(json.dumps({'image_count':15,'members':files,'zip_integrity':'passed','zip_bytes':out.stat().st_size}))

