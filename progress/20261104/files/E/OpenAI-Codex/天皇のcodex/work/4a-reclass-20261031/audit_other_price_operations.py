import json,re
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter
P=Path(__file__).parent;O=Path('E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes')
def load(n):return json.loads((P/n).read_text(encoding='utf8'))
ws=openpyxl.load_workbook(O/'03-catalog-errors-consolidated.xlsm',read_only=True,data_only=False)['Template']
rows=[];price_hits=[];allowed={'C','D','E','I','J','L','M','T','BG'}
for i,row in enumerate(ws.iter_rows(min_row=7,values_only=True),7):
 vals={get_column_letter(j):v for j,v in enumerate(row,1) if v is not None}
 if not vals:continue
 rows.append(vals)
 for c,v in vals.items():
  if c not in allowed:price_hits.append({'row':i,'column':c,'value':v})
assert len(rows)==164 and not price_hits
restore=load('urgent-batches-data.json')['restore'];wr=openpyxl.load_workbook(O/'02-restore-original-skus.xlsm',read_only=True,data_only=True)['Template'];restored_actual=[]
for i,x in enumerate(restore,7):
 for c,v in x['cells'].items():assert wr[f'{c}{i}'].value==v
 restored_actual.append({'sku':x['sku'],'asin':x['asin'],'price':x['price'],'source_basis':x['basis']})
manual=[
 {'sku':'4A073','asin':'B00SMEEVKQ','channel':'FBA','changes':{'ordinary':[10.99,4.99],'business':[4.49,4.49]},'source':'CONTINUE_CHECKPOINT.txt lines33,206; pricing-expanded.txt','status':'需优先复核：手工FBA普通价下降54.6%，与v1无关；Excel另邮价混用疑点'},
 {'sku':'AAAA 4A 608-N-L-210','asin':'B07B8RBCKT','channel':'FBA','changes':{'ordinary':[14.99,11.99]},'source':'restore-price-evidence.json;608-price-saved.txt;CONTINUE_CHECKPOINT.txt line35','status':'需复核：先按历史14.99恢复，随后按Excel11.99降价20%；已有15%券，需分清当时授权与运费口径'},
 {'sku':'4A 5036-B00SM-FBA','asin':'B00SMEEVC4','channel':'FBA','changes':{'ordinary':[7.20,6.99],'business':[9.69,6.99]},'source':'CONTINUE_CHECKPOINT.txt lines34,143','status':'小幅2.92%普通降价及企业倒挂纠正，不能等同50%事故；仍需核当时授权与原价'},
 {'sku':'4A GM30315','asin':'B07FKG29KB','channel':'FBM','changes':{'ordinary':[18.99,15.99],'sale':[15.99,14.99],'list':[18.99,15.99]},'source':'CONTINUE_CHECKPOINT.txt line84;30315-price-submitted.png;30315-public-before.txt','status':'手工FBM单独编辑；到手价另8.99运费；真实有效价15.99→14.99约6.25%，不能按普通18.99→14.99误称一次实际21%降价'},
 {'sku':'4A BP 1111-Nx4 / 4A GMBP 1111-Nx4','asin':'B07QWKYQV7','channel':'FBA+FBM','changes':{'ordinary':[27.99,27.39]},'source':'bp1111-coupon-price-before.txt/bp1111-coupon-price-saved.txt/bp1111-coupon-retry-after-price.txt','status':'用户后来明确要求小幅调价重试Coupon；约2.14%，单独目的，与v1的37.39→27.99分开；提交后当前仍需回读'},
 {'sku':'4A 354818','asin':'B07DJKDB63','channel':'FBA','changes':{'minimum':[9.99,7.99],'ordinary':[7.99,7.99]},'source':'354818-live-status.txt;CONTINUE_CHECKPOINT.txt lines153','status':'只修最低价冲突，原普通7.99未下降；不能将最低价调整当普通降价'},
 {'sku':'4A 40623','asin':'B00SMEF542','channel':'FBA','changes':{'minimum':[6.39,5.99],'ordinary':[5.99,5.99]},'source':'40623-floor-fixed.png; earlier current plan','status':'只修最低价冲突；截图普通5.99、最低5.99、最高7.39，未降普通价'}]
out={'batch03':{'rows':len(rows),'populated_data_columns':sorted({c for r in rows for c in r}),'unexpected_columns':price_hits,'price_fields_written':False,'conclusion':'实际03成品无价格/企业/阶梯/最低价/运费/库存字段，未发现重复覆盖价格风险'},'batch02':{'rows':len(restore),'actual_file_matches_prepared_cells':True,'actual_rows':restored_actual,'audit':load('v2-nine-restores-audit.json')},'manual_operations':manual,'scope':'根据现有会话证据已定位7组手工价格/参考价/最低价操作；不是未搜索历史的绝对无遗漏保证。当前恢复动作另见各代理日志。'}
(P/'other-price-operations-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
text=['02/03及手工价格操作复核','03实际文件164行，仅C,D,E,I,J,L,M,T,BG有值；无价格字段，无价格重复覆盖风险。','02实际9行逐单元格与作者数据一致；6条恢复价与原历史价一致；2028、holder、6032三条下降正在恢复。','']
for x in manual:text += [x['sku']+' | '+x['asin']+' | '+x['channel'],json.dumps(x['changes'],ensure_ascii=False),x['status'],'依据：'+x['source'],'']
(P/'other-price-operations-audit.txt').write_text('\n'.join(text),encoding='utf8')
print(json.dumps({'batch03_rows':len(rows),'batch03_price_fields':False,'batch02_rows':len(restore),'manual_groups':len(manual)},ensure_ascii=False))

