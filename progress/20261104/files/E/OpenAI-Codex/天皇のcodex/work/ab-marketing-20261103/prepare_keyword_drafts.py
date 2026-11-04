from pathlib import Path
import json
import re

ROOT=Path(__file__).parent
path=ROOT/'full-coverage/vc-execution-preparation.json'
d=json.loads(path.read_text(encoding='utf8'))
by_sku={r['sku']:r for r in d['sku_rows']}

def keywords(r):
    title=r['title'].lower()
    model=(r['history_sku'] or r['master_sku'] or r['sku']).upper()
    title=re.sub(r'(\d+)\s+(\d+)/(\d+)',lambda m:str(int(m[1])+int(m[2])/int(m[3])),title)
    title=re.sub(r'(?<![\d.])(\d+)/(\d+)',lambda m:str(int(m[1])/int(m[2])),title)
    if '4012' in model or '4013' in model or 'value pack' in title:
        return ['sticky notes variety pack','sticky notes assorted sizes','sticky notes value pack','sticky notes storage box'], '多尺寸套装'
    if 'BS 180' in model or 'bundle set' in title or 'leather' in title:
        return ['sticky notes and flags set','sticky notes variety set','sticky notes organizer set','assorted size sticky note set'], '便签套装'
    if 'non-sticky' in title or 'non sticky' in title:
        return ['non sticky memo cube','loose note paper cube','desk memo paper cube','650 sheet memo cube'], '非粘性便笺'
    for shape in ['leaf','arrow','heart','speech bubble','puzzle','apple','flower','car']:
        if re.search(r'\b'+shape.replace(' ',r'\s+')+r'\b',title):
            return [shape+' shaped sticky notes',shape+' sticky notes','colorful '+shape+' sticky notes',shape+' sticky memo pads'], '异形便签'
    if 'memo cube' in title or 'notes cube' in title or 'note cube' in title:
        return ['sticky note cube','printed sticky note cube','patterned sticky memo cube','desk sticky notes cube'], '粘性方块便笺'
    if 'roll' in title or 'PSS 9-' in model or 'PSS 32' in model:
        if 'refill' in title and 'dispenser' not in title and 'cutter' not in title:
            return ['sticky note roll refills','full adhesive sticky roll refill','repositionable sticky paper refill','sticky note roll replacement'], '卷装补充芯'
        width='0.6 inch' if ('0.6' in title or 'PSS 9-3' in model or 'PSS 32' in model) else '2 inch' if ('2 x 315' in title or 'PSS 9-1' in model) else None
        return ['full adhesive sticky note roll','sticky note roll with dispenser','repositionable sticky paper roll',(width+' sticky note roll') if width else 'colored sticky note rolls'], '卷装便签'
    if 'PSS 7' in model or ('pop-up note dispenser' in title and 'with' not in title):
        return ['pop up sticky note dispenser','3x3 pop up note dispenser','black pop up note holder','sticky note dispenser desk'], '弹出便签座'
    if 'BS 180' in model or 'bundle set' in title or 'leather' in title:
        return ['sticky notes and flags set','sticky notes variety set','sticky notes organizer set','assorted size sticky note set'], '便签套装'
    if 'holder' in title:
        return ['sticky note and pen holder','desk sticky note holder','sticky note organizer with pen holder','sticky note holder set'], '便签文具座'
    if '4012' in model or '4013' in model or 'value pack' in title:
        return ['sticky notes variety pack','sticky notes assorted sizes','sticky notes value pack','sticky notes storage box'], '多尺寸套装'
    if 'divider' in title:
        return ['sticky note dividers','lined divider sticky notes','sticky divider tabs','notebook divider sticky notes'], '便签分隔页'
    if 'file tabs' in title or 'page marker' in title or 'flags' in title or '603' in model or '604' in model:
        return ['writable binder index tabs','durable file tabs','repositionable index tabs','transparent book tabs'], '索引标签'
    dim=re.search(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(?:in|inch)',title)
    size=(dim[1]+'x'+dim[2]) if dim else None
    if not size:
        for code,value in [('301','1.5x2'),('303','3x3'),('304','3x4'),('305','3x5'),('406','4x6'),('508','5x8'),('608','6x8'),('404','4x4'),('2028','2x2')]:
            if code in model:size=value;break
    size=size or ''
    pads=[int(x) for x in re.findall(r'(\d+)\s*pads?\b',title.replace(',',' '))]
    pad_count=max(pads) if pads else None
    color='yellow' if 'yellow' in title else 'colored' if any(x in title for x in ['color','neon','bright']) else ''
    if 'pop-up' in title or 'pop up' in title:
        return [f'{size} pop up sticky notes'.strip(),'accordion sticky notes',f'{color} pop up notes'.strip(),'pop up sticky notes refill pads'], '弹出便签'
    if 'full adhesive' in title or 'full glue' in title or 'FULL GLUE' in model:
        return ['full adhesive sticky notes',f'{size} full adhesive sticky notes'.strip(),'fully adhesive sticky note pads','sticky notes full back adhesive'], '全胶便签'
    if 'lined' in title or 'line' in title:
        return [f'lined sticky notes {size}'.strip(),f'{size} lined sticky note pads'.strip(),f'{color} lined sticky notes'.strip(),f'{size} sticky notes with lines'.strip()], '横线便签'
    out=[f'{size} sticky notes'.strip(),f'{color} sticky notes {size}'.strip(),f'sticky notes {pad_count} pads' if pad_count else 'self stick note pads',f'{size} sticky notes bulk'.strip()]
    return out, '尺寸便签'

targets=[]
for i,p in enumerate(d['plans'],1):
    r=by_sku[p['target_sku']]
    p['execution_order']=i
    p['draft_campaign_name']='SP_VC_R'+str(p['history_rank'] or 0).zfill(3)+'_'+p['asin']+'_EXACT'
    if p['action'] in ['维护已有精准','修复已有精准利润']:
        p['keywords']=[]
        continue
    kws,kind=keywords(r)
    kws=list(dict.fromkeys(re.sub(r'\s+',' ',x).strip() for x in kws))
    p['keywords']=kws;p['keyword_type']=kind
    for k in kws:
        targets.append({'order':i,'history_rank':p['history_rank'],'model':p['history_sku'] or r['master_sku'] or r['sku'],
            'asin':p['asin'],'sku':p['target_sku'],'keyword':k,'match':'EXACT','bid_draft':p['bid_draft'],
            'daily_draft':p['daily_draft'],'action':p['action'],'type':kind,'status':'草案，未上传',
            'cvr':p['planned_cvr'],'cvr_basis':p['cvr_basis']})
d['keyword_drafts']=targets
d['summary']['keyword_drafts']=len(targets)
d['summary']['old_models_linked']=len({r['history_sku'] for r in d['sku_rows'] if r['old_candidate'] and r['history_sku']})
path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(d['summary'],ensure_ascii=False,indent=2))
