import json,collections
from pathlib import Path
P=Path(__file__).parent
a=json.loads((P/'12-processing-receipt-audit.json').read_text(encoding='utf8'))
issues=collections.defaultdict(list)
for i in a['sku_errors']:issues[i['count_or_sku']].append(i)
groups=[
 ('真实合规或商品限制待核',{'100227','19083','18370','19084'}),
 ('SKU或ASIN不存在或不能匹配',{'13013','8567'}),
 ('家族关系或套装设置暂缓',{'8047','100899','100893','8801','8066','8603','18837'}),
 ('目录属性冲突待核',{'8541','99022'}),
 ('语言数据旧提示',{'100720'}),
 ('图片问题暂缓',{'101156','18320','300403','20000','100581'}),
 ('其他属性枚举待核',{'100095','90244'}),
 ('需卖家支持诊断',{'18128'}),
 ('本次重复亮点已纠正并回验',{'100470'}),
 ('仅物流销售预测建议',{'101265'}),
]
rows=[]
for r in a['rows_detail']:
 if r['status']=='SUCCESS':continue
 codes={i['code']for i in issues[r['sku']]}
 bucket=next((label for label,c in groups if c&codes),'其他待核')
 rows.append({'sku':r['sku'],'asin':r['asin'],'primary_bucket':bucket,'all_codes':sorted(codes)})
assert len(rows)==99
accepted_languages=[]
ops={o['sku']:o for o in json.loads((P/'12-text-operations-draft.json').read_text(encoding='utf8'))['operations']}
for short,sku in [('124','4A GM124418*3'),('484','4A GM484812-N*2'),('500','4A GM50024')]:
 t=(P/f'12-language-{short}-before.txt').read_text(encoding='utf8')
 assert '商品信息采用的语言：English'in t and '100720'not in t and '个错误'not in t
 assert ops[sku]['cells']['I']in t and ops[sku]['cells']['J']in t
 accepted_languages.append({'sku':sku,'title_and_highlight_saved_match':True,'visible_language':'English','current_editor_100720_absent':True,'new_edits_or_resubmission':False})
out={'batch_id':'285175020758','status_counts':a['statuses'],'failed_rows':0,'submitted_cells_checked':4903,'submitted_cell_mismatches':0,'no_100476_in_receipt':True,'no_99300_in_receipt':True,'primary_buckets':dict(collections.Counter(r['primary_bucket']for r in rows)),'bucket_rule':'One primary bucket per OTHER ERROR row. Multiple issues may coexist; all_codes retains every code. These are residual catalog issues, not a claim that all submitted changes failed or all buyer pages are live.','rows':rows,'three_language_titles_current_acceptance':accepted_languages,'one_highlight_correction':{'sku':'4A GM60171*3','asin':'B07FK9VK5L','new_highlight':'Sign Here and Note flags; transparent, writable color tabs for marking documents','saved_independent_readback':True,'100470_absent':True,'frozen_upload_file_unchanged':True},'public_pages_all_verified':False}
(P/'12-final-processing-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items()if k not in ['rows']},ensure_ascii=False,indent=2))
