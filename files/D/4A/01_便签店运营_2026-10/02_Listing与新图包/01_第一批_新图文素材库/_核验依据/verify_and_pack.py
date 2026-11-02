import json,hashlib,zipfile,struct
from pathlib import Path
root=Path(r'E:\Desktop\待上架_新图文素材库')
report={'files':[],'errors':[]}
for sku in ['PSS32x6','5084NL','301x12']:
    manifest=json.loads((root/sku/'manifest.json').read_text(encoding='utf-8'))
    assert len(manifest['images'])==5
    for entry in manifest['images']:
        p=root/sku/entry['file']
        b=p.read_bytes()
        dims=list(struct.unpack('>II',b[16:24]))
        assert dims==[2000,2000],(p,dims)
        assert hashlib.sha256(b).hexdigest()==entry['sha256'],p
        assert (root/sku/entry['generation_source']).exists()
        assert not entry['approved_for_automation']
        report['files'].append({'file':str(p),'pixels':dims,'sha256_match':True,'source_exists':True,'status':entry['review_status']})
report['count']=len(report['files'])
report['visual_review']='15张逐图查看；主图数量及文字检查；尺寸对比改精确SVG；签字提示改单张；PSS动作与背面两图待核。'
report['limitations']='实物批次未核样；主图白底技术通过不等于实物保真认证或Amazon审核通过。'
(root/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
out=root.parent/'待上架_新图文素材库_三款15张_20261030.zip'
if out.exists(): raise RuntimeError('Archive already exists; choose a new filename.')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in root.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(root))
with zipfile.ZipFile(out) as z:
    bad=z.testzip()
    assert bad is None,bad
    count=len(z.infolist())
print(json.dumps({'image_count':report['count'],'zip':str(out),'members':count,'integrity':'passed','bytes':out.stat().st_size},ensure_ascii=False))

