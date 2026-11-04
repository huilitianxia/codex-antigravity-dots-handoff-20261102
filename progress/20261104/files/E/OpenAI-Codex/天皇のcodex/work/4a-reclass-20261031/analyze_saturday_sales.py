import csv,json,re,statistics
from pathlib import Path
from datetime import datetime,timedelta,timezone,date
from collections import Counter
from decimal import Decimal

root=Path(__file__).parent
source=Path('D:/下载文件/175793876516020757.txt')
pt=timezone(timedelta(hours=-7))
with source.open(encoding='utf-8-sig',newline='') as f:
    raw=list(csv.DictReader(f,delimiter='\t'))
rows=[]
for r in raw:
    if r['ship-country']!='US' or r['currency']!='USD' or r['order-status']=='Cancelled':continue
    r=dict(r)
    r['_dt']=datetime.fromisoformat(r['purchase-date']).astimezone(pt)
    r['_day']=r['_dt'].date().isoformat()
    rows.append(r)

def sums(rs):
    amount=sum((Decimal(r['item-price'] or '0') for r in rs),Decimal(0))
    discount=sum((Decimal(r['item-promotion-discount'] or '0') for r in rs),Decimal(0))
    return dict(orders=len({r['amazon-order-id'] for r in rs}),lines=len(rs),units=sum(int(r['quantity'] or '0') for r in rs),item_amount=float(amount),item_promotion_discount=float(discount),after_item_promotion=float(amount-discount))

def day_stats(d):
    rs=[r for r in rows if r['_day']==d]
    return dict(date=d,weekday=date.fromisoformat(d).strftime('%A'),**sums(rs),business=sums([r for r in rs if r['is-business-order'].lower()=='true']),nonbusiness=sums([r for r in rs if r['is-business-order'].lower()!='true']),fba=sums([r for r in rs if r['fulfillment-channel']=='Amazon']))

days=[day_stats((date(2026,10,1)+timedelta(days=i)).isoformat()) for i in range(31)]
def aggregate(ds):
    out=dict(days=len(ds),dates=[d['date'] for d in ds])
    for k in ['orders','units','item_amount']:
        vals=[d[k] for d in ds]
        out[k+'_total']=round(sum(vals),2)
        out[k+'_daily_mean']=round(statistics.mean(vals),2)
        out[k+'_daily_median']=round(statistics.median(vals),2)
        out[k+'_min']=min(vals)
        out[k+'_max']=max(vals)
    for label in ['business','nonbusiness','fba']:
        out[label]={k+'_daily_mean':round(statistics.mean([d[label][k] for d in ds]),2) for k in ['orders','units','item_amount']}
    out['business_amount_share']=round(sum(d['business']['item_amount'] for d in ds)/sum(d['item_amount'] for d in ds),4)
    out['amount_per_order']=round(out['item_amount_total']/out['orders_total'],2)
    return out

full=[d for d in days if '2026-10-02'<=d['date']<='2026-10-30']
groups={label:aggregate([d for d in full if date.fromisoformat(d['date']).weekday() in indexes]) for label,indexes in [('weekday',range(5)),('saturday',[5]),('sunday',[6])]}
for label in ['saturday','sunday']:
    groups[label]['change_vs_weekday_pct']={k:round((groups[label][k+'_daily_mean']/groups['weekday'][k+'_daily_mean']-1)*100,2) for k in ['orders','units','item_amount']}

snapshot=(root/'orders-5082-price-investigation.txt').read_text(encoding='utf8')
known=[]
for line in snapshot.splitlines():
    if "- 'row" not in line or 'B07F2BHFJH' not in line:continue
    m=re.search(r'(2026/\d+/\d+) (\d+:\d+) PDT (\d{3}-\d{7}-\d{7}).*?数量: (\d+) 商品小计: US\$([\d,.]+)',line)
    if not m:continue
    ds,t,oid,qty,amount=m.groups();qty=int(qty);amount=float(amount.replace(',',''))
    if abs(amount/qty-5.99)<.01:
        known.append(dict(date=ds.replace('/','-'),time_PDT=t,order_suffix=oid[-7:],units=qty,item_amount=amount,in_order_source=any(r['amazon-order-id']==oid for r in rows)))

report_low=[dict(date=r['_day'],time_PDT=r['_dt'].strftime('%H:%M:%S'),order_suffix=r['amazon-order-id'][-7:],units=int(r['quantity']),item_amount=float(r['item-price'])) for r in rows if r['asin']=='B07F2BHFJH' and r['quantity'] and r['item-price'] and abs(float(r['item-price'])/int(r['quantity'])-5.99)<.01]
out=dict(source=str(source),basis='US, USD, non-Cancelled; pending included; PDT UTC-07 calendar days; item-price line total before item promotions; excludes shipping/tax/refunds/fees',raw_rows=len(raw),included=sums(rows),statuses=dict(Counter(r['order-status'] for r in rows)),source_min_purchase_PDT=min(r['_dt'] for r in rows).isoformat(),source_max_purchase_PDT=max(r['_dt'] for r in rows).isoformat(),source_last_modified_local=datetime.fromtimestamp(source.stat().st_mtime).isoformat(),complete_day_basis='2026-10-02..2026-10-30: exclude 10/01 because requested export boundary unknown, exclude unfinished 10/31',groups=groups,daily=days,normal_price_amount=None,normal_price_note='No reliable original regular-price field exists in order export. Do not reprice orders retrospectively or subtract an assumed five orders. The identified $5.99 wrong-price orders in later UI snapshot are reported separately.',known_wrong_price_snapshot_orders=known,wrong_price_matches_in_source=report_low,limitations=['One month only; four complete Saturdays and four complete Sundays.', 'Latest order timestamp is not an exact export completeness cutoff.', 'This source predates later 10/31 orders and cannot measure current Saturday.', 'Revenue versus traffic/conversion cause requires sessions and conversion reports.', 'No market-wide inference can be made solely from this seller.'],same_hour_saved_dashboard=dict(source='sales-20261031-same-hour.txt',cutoff_PDT='07:00',current_date='2026-10-31',current=dict(orders=4,units=4,item_amount=54.96),previous_saturday=dict(orders=3,units=3,item_amount=56.97),amount_change_pct=round((54.96/56.97-1)*100,2)))
(root/'saturday-sales-analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
lines=['周六销售本地只读分析','结论：本店已有明显周末回落。4个完整周六均额$308.59，中位$245.81；21个工作日均额$538.86，中位$553.17，周六均额低42.73%。周六订单均数低42.44%，每单商品额$21.28与工作日$21.39几乎相同，历史差异主要来自订单数。','企业采购订单日均：工作日7.57、周六2.50、周日0.75；普通订单也回落，不能只归因企业客户。','口径：美国/USD/非取消订单；含Pending；按PDT日历日；商品额不含运费税费，未扣退款费用。',f"数据最新购买时间：{out['source_max_purchase_PDT']}；文件最后修改（本机）：{out['source_last_modified_local']}",'完整日对比：10/02—10/30；10/01导出边界不明保守排除，10/31未完整且旧快照排除。',json.dumps(groups,ensure_ascii=False,indent=2),'完整周末每日：',*[json.dumps(d,ensure_ascii=False) for d in full if d['weekday'] in ['Saturday','Sunday']],'10/31旧快照：',json.dumps(days[-1],ensure_ascii=False),'已保存同小时业务报表（指标原名为订单商品总数）：',json.dumps(out['same_hour_saved_dashboard'],ensure_ascii=False),'已知5082错误价$5.99订单（来自较晚UI快照，可能不在订单导出）：',json.dumps(known,ensure_ascii=False),'导出中错误价匹配：',json.dumps(report_low,ensure_ascii=False),'正常价还原金额未知：导出没有逐订单可靠正常价字段，不能随意扣除5单或按5件重估。','局限：仅一个月和四个完整周六；不能证明全市场普遍，也不能区分流量下降与转化下降。']
(root/'saturday-sales-analysis.txt').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps({k:out[k] for k in ['included','source_min_purchase_PDT','source_max_purchase_PDT','groups','known_wrong_price_snapshot_orders','wrong_price_matches_in_source']},ensure_ascii=False,indent=2))
