from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
root=Path('E:/Desktop/待上架_新图文素材库_第三批')
data=json.loads((root/'交付总清单.json').read_text(encoding='utf-8-sig'))
checks=[]
for item in data['images']:
    p=Path(item['absolute_file'])
    with Image.open(p) as im:
        assert im.size==(2000,2000),str(p)
        assert im.mode=='RGB',(str(p),im.mode)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],str(p)
    assert (root/item['folder']/item['source_copy']).exists(),item['source_copy']
    checks.append({'id':item['id'],'pixels':[2000,2000],'mode':'RGB','sha256_match':True,'local_source_copy':True})
assert len(checks)==15
report=json.loads((root/'验证记录.json').read_text(encoding='utf-8-sig'))
report['file_checks']=checks
report['browser_check']={'all_15_images_loaded_at_2000px':True,'horizontal_overflow':False,'checked_page':'审稿总览.html'}
report['visual_review']='已逐图查看13张生成图、2张40609返修图、2张最终SVG尺寸图及15张总预览；检查数量、文字、结构、贴附平整与比例。PSS动作及换卷保留待核状态。'
(root/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
archive=root.parent/'待上架_新图文素材库_第三批_15张_20261030.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():z.write(p,Path(root.name)/p.relative_to(root))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    members=len(z.infolist())
print(json.dumps({'count':len(checks),'archive':str(archive),'bytes':archive.stat().st_size,'members':members,'zip_crc_pass':True},ensure_ascii=False))
