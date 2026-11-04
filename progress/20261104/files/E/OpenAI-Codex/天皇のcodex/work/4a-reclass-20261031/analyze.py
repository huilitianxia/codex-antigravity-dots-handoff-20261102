import csv, json, re, collections, hashlib
from pathlib import Path
from fractions import Fraction
import openpyxl

ROOT=Path(__file__).parent
SOURCE=Path('D:/下载文件/所有商品报告_10-31-2026.txt')
FBA=Path('D:/下载文件/284701020757.txt')
OLD=Path('D:/下载文件/所有商品报告_09-03-2026.txt')
CAT=Path('C:/Users/24243/Documents/Codex/2026-08-11/7-30-slack-plugin-slack-openai/4A_Amazon_Operations/source_workbooks/亚马逊供应商和开店总表-2026 (1).xlsx')
def read(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f,delimiter='\t'))
rows=read(SOURCE); old=read(OLD)
fba=read(FBA)
fba_by_sku={x['sku']:x for x in fba}
fba_by_asin=collections.defaultdict(list)
for n,x in enumerate(fba,2):fba_by_asin[x['asin']].append((x['product-name'],f'物流库存10-30快照行{n}'))
def numeric(v):
    try:
        n=float(v)
        return int(n) if n.is_integer() else n
    except:return None
def inv(x,key):return numeric(x.get(key,'')) if x else None
byasin=collections.defaultdict(list); historical=collections.defaultdict(list); catalog=collections.defaultdict(list)
for r in rows:byasin[r['asin1']].append(r)
for n,r in enumerate(old,2):historical[r['asin1']].append((r['item-name'],f'09-03报告行{n}'))
w=openpyxl.load_workbook(CAT,read_only=True,data_only=True)
for n,r in enumerate(w['Sheet1'].iter_rows(min_row=2,values_only=True),2):
    for a in set(re.findall(r'B0[A-Z0-9]{8}',str(r[2])+' '+str(r[4]))):
        if r[6]:catalog[a].append((str(r[6]),f'产品总表2026 Sheet1行{n}'))
def generic(t):return not t or ' | B0' in t or len(t)<55 or bool(re.search(r'^4A Self-Stick Notes,',t))
def num(s):
    return sum(float(Fraction(p)) for p in s.strip().split())
N=r'\d+(?:\.\d+)?(?:\s+\d+/\d+|/\d+)?'
DIM=re.compile(r'('+N+r')\s*(?:in\s*)?[x×]\s*('+N+r')\s*(?:inches|inch|in\b|ft\b|mm\b|\")',re.I)
def dimensions(t):
    m=DIM.search(t)
    if not m:return '',None
    a,b=num(m[1]),num(m[2]); unit='ft' if re.search(r'ft\b',m[0],re.I) else 'mm' if re.search(r'mm\b',m[0],re.I) else 'in'
    def label(v):
        n=num(v)
        return f'{n:g}' if abs(n*1000-round(n*1000))<0.00001 else v.strip()
    return f'{label(m[1])} × {label(m[2])} {unit}',(a,b,unit)
def classify(t):
    l=t.lower();dim,d=dimensions(t)
    ruled='横线' if re.search(r'\blined\b|\bruled\b|with lines',l) else '网格' if 'grid' in l or 'graph sticky' in l else '未注明横线'
    full=bool(re.search(r'full adhesive|full glue|full stick(?:y)? back|full sticky',l))
    pop=bool(re.search(r'pop[ -]?up|accordion',l))
    cycle=bool(re.search(r'color[ -]cycl|color cyclic|magic',l))
    glue='满胶' if full else '强粘' if 'super sticky' in l else '半胶' if 'half-adhesive' in l else '普通自粘或未注明'
    form='抽取式' if pop else '平叠'
    ds=dim or '尺寸待核'
    if re.search(r'whiteboard|white board|dry erase',l) and not re.search(r'easel|flip chart',l):return '会议展示','白板贴',ds,glue,ruled,form
    if re.search(r'easel|flip chart|anchor chart',l):return '会议展示','桌立会议本含白板' if 'dry erase' in l else '桌立会议本' if 'tabletop' in l else '大幅会议纸',ds,glue,ruled,form
    if re.search(r'roll|tape',l):
        typ='卷带套装含替芯' if re.search(r'dispenser|cutter',l) and 'refill' in l else '卷带含切割器' if re.search(r'dispenser|cutter',l) else '卷带替芯' if 'refill' in l else '卷带配置待核'
        return '满胶卷带',typ,ds,glue,ruled,form
    if re.search(r'non[ -]sticky|non[ -]adhesive',l):return '便签砖','无胶便签砖',ds,'无胶',ruled,form
    if re.search(r'cube|note block|sticky blocks',l):return '便签砖','印花自粘便签砖' if re.search(r'print|pattern',l) else '彩色自粘便签砖',ds,glue,ruled,form
    if 'chalkboard' in l:return '标签贴纸','金边黑板贴' if 'gold' in l else '黑板贴',ds,glue,ruled,form
    if re.search(r'coding|circle dot',l):return '标签贴纸','圆点分类贴',ds,glue,ruled,form
    if re.search(r'magnet',l):return '计划与清单','磁吸便签含笔',ds,glue,ruled,form
    if 'planner' in l or 'schedule' in l:
        return '计划与清单','月计划' if 'monthly' in l and 'weekly' not in l else '周计划' if 'weekly' in l and 'monthly' not in l else '日计划' if 'daily' in l else '计划本周期待核',ds,glue,ruled,form
    if re.search(r'bs\s*180|leather|hard cardboard cover',l):
        return '桌面套装','BS便签替芯' if 'refill' in l else 'BS商务便签套装',ds,glue,ruled,form
    if 'pp box' in l or 'storage pp' in l:return '桌面套装','PP盒多尺寸便签', '多尺寸',glue,ruled,form
    if re.search(r'holder|dispenser|organizer',l) and not re.search(r'flag|tabs',l):return '桌面配件','抽取便签座' if pop else '便签收纳座',ds,glue,ruled,form
    if re.search(r'pen holder|holder dispenser|holder.*sticky notes|dispenser pen',l):return '桌面套装','笔筒便签标签组合','多组件',glue,ruled,form
    if re.search(r'divider sticky notes|tabbed .*note|sheets/divider|divders/|dividers/',l) and not 'transparent' in l:return '纸质分隔便签','分隔便签',ds,glue,ruled,form
    if re.search(r'sign here',l):return '索引与签字贴','签字指示贴',ds,glue,ruled,form
    if re.search(r'transparent|durable (?:file )?tabs|flags with pp rule|film sticky notes',l):
        typ='带孔活页索引' if re.search(r'hole|binder',l) else '带尺索引' if re.search(r'ruler|pp rule',l) else '印花透明索引' if re.search(r'print',l) else '耐用分隔索引' if 'durable' in l else '箭头透明索引' if 'arrow' in l else '透明索引'
        return '索引与签字贴',typ,ds,glue,ruled,form
    if re.search(r'3d shape',l):return '印花与异形','3D动物印花便签',ds,glue,ruled,form
    if re.search(r'folding page',l):return '印花与异形','折页印花套装',ds,glue,ruled,form
    if re.search(r'printed sticky|sticky note set.*print',l):return '印花与异形','印花便签套装',ds,glue,ruled,form
    if re.search(r'shape|heart|bubble|leaf|puzzle|door lock',l):
        shape=[cn for kw,cn in [('heart','心形'),('arrow','箭头形'),('bubble','对话框'),('leaf','叶形'),('tree','树形'),('puzzle','拼图形'),('door lock','门挂形'),('star','星形'),('flower','花形'),('apple','苹果形')] if kw in l]
        return '印花与异形','混合异形' if len(shape)>1 else shape[0] if shape else '其他异形',ds,glue,ruled,form
    if full:return '满胶平叠便签','满胶便签',ds,glue,ruled,form
    if 'rainbow sticky' in l and not dim:return '印花与异形','彩虹造型便签','多尺寸或待核',glue,ruled,form
    if re.search(r'big (?:sticky )?(?:notes|pad)',l) and not dim:return '会议展示','大幅便签尺寸待核',ds,glue,ruled,form
    if re.search(r'page mark|page maker|sticky note tabs|sticky notes flags|index flags',l):return '索引与签字贴','纸质或材质待核索引',ds,glue,ruled,form
    if d and d[2]=='in' and max(d[:2])>=11:return '会议展示','大幅方形便签',ds,glue,ruled,form
    if d and d[2]=='mm':return '日常便签','毫米规格小便签',ds,glue,ruled,form
    if d and d[2]=='in':
        typ='循环色抽取便签' if cycle and pop else '循环色平叠便签' if cycle else '抽取便签' if pop else '强粘便签' if glue=='强粘' else '窄条纸便签' if min(d[:2])<1 else '常规平叠便签'
        return '日常便签',typ,ds,glue,ruled,form
    return '待核实','信息不足','尺寸待核',glue,ruled,form

def pack(t):
    l=t.lower(); lead=re.search(r'^(?:aaaa\s+)?4a\s+(\d+)\s+pads?\b',l)
    spp=re.search(r'(\d+)\s*sheets\s*/\s*pad',l)
    total=re.search(r'(\d+)\s*sheets\s*total',l)
    ppp=re.search(r'(\d+)\s*pads?\s*[, ]*/\s*(?:pack|box|set)',l)
    outer=re.search(r'(\d+)\s+(?:packs?|boxes)\b',l)
    pads=int(lead[1]) if lead else None
    evidence='标题明确总本数' if lead else ''
    if pads is None and ppp:
        pads=int(ppp[1])*(int(outer[1]) if outer else 1);evidence='标题每包本数×明确包数' if outer else '标题每包本数；外包装倍数未注明'
    if pads is None:
        standalone=re.search(r'(\d+)\s+pads?\b(?!\s*[, ]*/)',l)
        if standalone:pads=int(standalone[1]);evidence='标题独立本数描述，需核对整套装量'
    snippets=re.findall(r'\d+[\d,]*\s*(?:pads?|sheets?|rolls?|refills?|flags?|pcs|packs?|sets?|dividers?|divders?|colors?)(?:\s*/\s*(?:pad|pack|box|set|color|divider|dispenser|roll))?(?:\s+total)?',t,re.I)
    warn=''
    if pads and spp and total and int(spp[1])<=1000 and pads*int(spp[1])!=int(total[1]):warn='标题本数×每本张数与总张数不符'
    if spp and int(spp[1])>1000:warn='每本张数疑似串码'
    return pads,evidence,'；'.join(snippets),warn

feed=list(csv.reader(open('E:/Desktop/4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv',encoding='utf-8-sig'),delimiter='\t'))[6:]
feeds=collections.defaultdict(list)
for r in feed:feeds[r[1]].append(r)
mapping=openpyxl.load_workbook('E:/Desktop/4A_全店变体合并全量大排查与挂载映射总表.xlsx',read_only=True,data_only=True)
maprows=collections.defaultdict(list)
for r in mapping.worksheets[1].iter_rows(min_row=2,values_only=True):
    if r[6]:maprows[(str(r[6]),str(r[7]))].append(r)
archive=openpyxl.load_workbook('E:/Desktop/全店幽灵死链接归档隔离库_待后续安全删除.xlsx',read_only=True,data_only=True)
archived=collections.defaultdict(list); archive_stats=[]
for s in archive.worksheets:
    rr=list(s.iter_rows(min_row=2,values_only=True));archive_stats.append([s.title,len(rr),sum(x[3] is None for x in rr),sum(str(x[3] or '').isdigit() and int(x[3])>0 for x in rr)])
    for x in rr:archived[str(x[0])].append(s.title)
deletion=list(csv.reader(open('E:/Desktop/4A_100个无货低评幽灵SKU_官方批量删除表.tsv',encoding='utf-8-sig'),delimiter='\t'))[6:]
delete_skus={r[1] for r in deletion}
master=[];issues=[]
def issue(sku,a,kind,detail):issues.append([sku,a,kind,detail,'未提交后台'])
for i,r in enumerate(rows,2):
    sku,a=r['seller-sku'],r['asin1']; parent='parent' in sku.lower()
    title=r['item-name'];basis=title;src=f'10-31报告行{i}'
    candidates=[(x['item-name'],'10-31报告同ASIN其他SKU') for x in byasin[a] if 'parent' not in x['seller-sku'].lower() and not generic(x['item-name'])]
    candidates+=fba_by_asin[a]+historical[a]+catalog[a]
    if generic(title) and not parent:
        detailed=[(t,s) for t,s in candidates if not generic(t)]
        if detailed:basis,src=max(detailed,key=lambda x:len(x[0]))
        issue(sku,a,'当前标题信息缺失','分类采用'+src if basis!=title else '现有精确ASIN来源仍无完整标题')
    cat,typ,dim,glue,ruled,form=classify(basis)
    if parent:cat,typ,dim='父SKU待核','父体或占位记录','不适用'
    fine=' / '.join([typ,dim]+([ruled] if cat in ['日常便签','纸质分隔便签','满胶卷带'] else []))
    pads,packsource,packtext,packwarn=pack(basis)
    if parent:pads=None;packsource='';packtext=''
    if cat=='待核实':issue(sku,a,'分类待核',basis)
    if packwarn and not parent:issue(sku,a,'标题装量冲突',packwarn)
    fs=feeds.get(sku,[]);oldp='；'.join(sorted({x[5] for x in fs}));oldsize='；'.join(sorted({x[51] for x in fs}));oldcolor='；'.join(sorted({x[50] for x in fs}))
    if any(x[11] and x[11]!=a for x in fs):issue(sku,a,'旧上传SKU映射冲突','当前ASIN='+a+'；旧V2 ASIN='+','.join(sorted({x[11] for x in fs})))
    if re.search(r'\(Pack \d+\)',oldsize):issue(sku,a,'旧V2虚构Pack后缀','旧提交值：'+oldsize+'；本次仅标记，需读当前属性后更正')
    if parent and any('parent' not in x['seller-sku'].lower() for x in byasin[a]):issue(sku,a,'父SKU与商品SKU共用ASIN','父体身份或SKU映射待核，不能直接删除')
    q=int(r['quantity']) if r['quantity'] else None
    if parent:op='父SKU身份待核'
    elif r['status']=='Incomplete':op='未完成记录待筛选'
    elif r['fulfillment-channel']=='AMAZON_NA':op='FBA有效性待库存报告核实'
    elif r['status']=='Active' and q and q>0:op='自配送在售且报告数量>0'
    elif r['status']=='Inactive' and q and q>0:op='自配送停用但数量>0'
    elif q==0:op='自配送数量0待评估'
    else:op='状态待核'
    fx=fba_by_sku.get(sku)
    if fx and fx['asin']!=a:
        issue(sku,a,'跨报告SKU对应ASIN不一致','物流库存ASIN='+fx['asin']);fx=None
    av=inv(fx,'available');reserved=inv(fx,'Total Reserved Quantity');incoming=inv(fx,'inbound-quantity');bad=inv(fx,'unfulfillable-quantity');sold30=inv(fx,'units-shipped-t30');sold90=inv(fx,'units-shipped-t90')
    if not parent and fx:
        if av is not None and av>0:op='FBA有货且在售' if r['status']=='Active' and r['fulfillment-channel']=='AMAZON_NA' else 'FBA有货但销售状态需修复'
        elif (reserved or 0)>0 or (incoming or 0)>0 or (bad or 0)>0:op='可售为0但有预留在途或不可售库存'
        elif (sold90 or 0)>0:op='当前无可售但90天有出货'
        elif av==0 and reserved==0 and incoming==0 and bad==0 and sold90==0:op='零库存且90天零出货候选'
        elif av==0:op='零库存但销量数据缺失'
    mr=maprows[(sku,a)];stock='；'.join(sorted({str(x[11]) for x in mr if x[11] is not None}));rating='；'.join(sorted({str(x[13]) for x in mr if x[13] is not None}))
    master.append({'row':i,'sku':sku,'asin':a,'status':r['status'],'channel':r['fulfillment-channel'],'quantity':q,'price':float(r['price']) if r['price'] else None,'parent':parent,'op':op,'category':cat,'type':typ,'fine':fine,'dimensions':dim,'glue':glue,'layout':ruled,'form':form,'pads':pads,'packsource':packsource,'packtext':packtext,'title':title,'basis':basis,'source':src,'asin_skus':len(byasin[a]),'old_parent':oldp,'old_size':oldsize,'old_color':oldcolor,'old_stock':stock,'old_rating':rating,'archive':'；'.join(archived.get(sku,[])),'delete_list':sku in delete_skus,'local_status':'已完成本地分类' if cat!='待核实' else '待补产品信息','live_status':'未更改'})
    master[-1].update({'fnsku':fx['fnsku'] if fx else '', 'available':av,'reserved':reserved,'inbound':incoming,'unfulfillable':bad,'sold30':sold30,'sold90':sold90,'sales30':inv(fx,'sales-shipped-last-30-days'),'snapshot':fx['snapshot-date'] if fx else '', 'colors':'；'.join(c.strip() for c in re.split(r'[,;]',basis) if re.search(r'\b(?:colors?|assorted|neon|pastel|yellow|white|black|blue|green|pink|purple|orange|red)\b',c,re.I) and len(c)<100)})

groups=collections.defaultdict(list)
for x in master:groups[x['fine']].append(x)
summary=[]
for k,v in sorted(groups.items(),key=lambda kv:(kv[1][0]['category'],kv[0])):
    summary.append([v[0]['category'],k,len(v),len({x['asin'] for x in v}),sum(x['status']=='Active' for x in v),sum(x['channel']=='AMAZON_NA' for x in v),sum(x['status']=='Incomplete' for x in v),'内部分类，非已建父体'])
asinrows=[]
for a in byasin:
    v=[x for x in master if x['asin']==a];cats=sorted({x['fine'] for x in v if not x['parent']})
    asinrows.append([a,len(v),'；'.join(x['sku'] for x in v),'；'.join(cats),'；'.join(sorted({x['status'] for x in v})),sum(x['channel']=='AMAZON_NA' for x in v),'同ASIN多SKU，不能相加评价数' if len(v)>1 else '',v[0]['basis']])
ghost=[]
cur={x['sku']:x for x in master}
for sku in sorted(set(archived)|delete_skus):
    x=cur.get(sku);rr=[r for (s,a),v in maprows.items() if s==sku for r in v]
    prior=next((r for r in old if r['seller-sku']==sku),None)
    fx=fba_by_sku.get(sku)
    ghost.append([sku,x['asin'] if x else prior['asin1'] if prior else '','当前报告存在' if x else '当前报告未出现（不等于确认删除）',x['status'] if x else '',x['channel'] if x else '',x['quantity'] if x else None,'；'.join(archived.get(sku,[])),'是' if sku in delete_skus else '否','；'.join(sorted({str(r[11]) for r in rr if r[11] is not None})),'；'.join(sorted({str(r[13]) for r in rr if r[13] is not None})),prior['quantity'] if prior else '',prior['fulfillment-channel'] if prior else '',fx['fnsku'] if fx else '',inv(fx,'available'),inv(fx,'Total Reserved Quantity'),inv(fx,'inbound-quantity'),inv(fx,'units-shipped-t30'),inv(fx,'units-shipped-t90'),'已匹配10-30物流快照' if fx else '物流库存未匹配，仍不能当零'])

# Inventory quantities deduplicated by marketplace and FNSKU; repeated values must agree.
fgroups=collections.defaultdict(list)
for fx in fba:fgroups[(fx['marketplace'],fx['fnsku'])].append(fx)
fba_unique=[]
for (market,fn),vv in fgroups.items():
    vals={}
    for key in ['available','Total Reserved Quantity','inbound-quantity','unfulfillable-quantity','units-shipped-t30','units-shipped-t90','sales-shipped-last-30-days','sales-shipped-last-7-days']:
        nonblank={inv(x,key) for x in vv if inv(x,key) is not None}
        vals[key]=next(iter(nonblank)) if len(nonblank)==1 else None
        if len(nonblank)>1:issue('；'.join(x['sku'] for x in vv),vv[0]['asin'],'同FNSKU数值不一致',key+'='+str(nonblank))
    fba_unique.append({'fnsku':fn,'market':market,'skus':[x['sku'] for x in vv],'asin':vv[0]['asin'],**vals})
inventory=[];urgent=[]
for fx in fba:
    sku,a=fx['sku'],fx['asin'];x=cur.get(sku); av=inv(fx,'available');rv=inv(fx,'Total Reserved Quantity');ib=inv(fx,'inbound-quantity');bad=inv(fx,'unfulfillable-quantity')
    samefn=[z['sku'] for z in fgroups[(fx['marketplace'],fx['fnsku'])] if z['sku'] in cur and cur[z['sku']]['status']=='Active' and cur[z['sku']]['channel']=='AMAZON_NA']
    sameasin=[z['seller-sku'] for z in byasin.get(a,[]) if z['status']=='Active' and z['fulfillment-channel']=='AMAZON_NA']
    typ=classify(fx['product-name']);inventory.append([sku,a,fx['fnsku'],x['status'] if x else '10-31清单未出现',av,rv,ib,bad,inv(fx,'units-shipped-t7'),inv(fx,'units-shipped-t30'),inv(fx,'units-shipped-t90'),inv(fx,'sales-shipped-last-30-days'),typ[0],typ[1],typ[2],fx['product-name'],fx['snapshot-date'],'；'.join(samefn),'；'.join(sameasin),'是' if sku in delete_skus else '否'])
    if ((av or 0)>0 or (rv or 0)>0 or (ib or 0)>0 or (bad or 0)>0) and (not x or x['status']!='Active' or x['channel']!='AMAZON_NA'):
        action='同FNSKU已有在售SKU，先核对别名，勿重复建档' if samefn else '有库存但清单缺失或停用，优先检查滞留库存及恢复原SKU报价'
        urgent.append([sku,a,fx['fnsku'],av,rv,ib,bad,inv(fx,'units-shipped-t30'),inv(fx,'sales-shipped-last-30-days'),'是' if sku in delete_skus else '否',x['status'] if x else '清单未出现','；'.join(samefn),'；'.join(sameasin),action,'待后台核实，未恢复'])
urgent.sort(key=lambda x:(bool(x[11]),x[9]!='是',-(x[3] or 0)))

# Candidate matching never changes a listing. It matches explicit physical attributes,
# then exposes historical rating evidence without treating it as current or additive.
all_asins=set(byasin)|set(fba_by_asin)
entities={}; signatures=collections.defaultdict(list)
def palette(t):
    l=t.lower();named=sorted(set(re.findall(r'\b(?:yellow|white|black|blue|green|pink|purple|orange|red|magenta)\b',l)))
    if named:return ','.join(named)
    if 'pastel' in l:return 'pastel-assorted'
    if re.search(r'neon|bright|ultra',l):return 'bright-assorted'
    if re.search(r'assorted|rainbow|colors|colored',l):return 'assorted-unspecified'
    return 'unknown'
for a in sorted(all_asins):
    mv=[x for x in master if x['asin']==a and not x['parent']]
    if not mv:continue
    basis=max((x['basis'] for x in mv),key=len)
    typ=classify(basis);p,ps,pt,pw=pack(basis);spp=re.search(r'(\d+)\s*sheets\s*/\s*pad',basis,re.I)
    roll=re.search(r'(\d+)\s*rolls?\s*/\s*pack',basis,re.I)
    qty='Pads '+str(p) if p else 'Rolls '+roll[1] if roll else ''
    unit=spp[1] if spp else ''
    fvals=[z for z in fba_unique if z['asin']==a]
    avs=[z['available'] for z in fvals if z['available'] is not None]
    stock=sum(avs) if avs and len(avs)==len(fvals) else None
    hist=[r for (s,aa),rr in maprows.items() if aa==a for r in rr if r[13] not in [None,'','None']]
    rated=sorted({(numeric(r[13]),numeric(r[12])) for r in hist if numeric(r[13]) is not None},key=lambda x:(x[0],x[1] or 0),reverse=True)
    hs='；'.join(f'{st:g}分/{rc if rc is not None else "未知"}评' for st,rc in rated)
    ent={'asin':a,'title':basis,'type':typ,'pads':p,'qty':qty,'unit':unit,'color':palette(basis),'stock':stock,'rating':hs,'stars':rated[0][0] if rated else None,'reviews':max((z[1] or 0 for z in rated),default=0),'skus':'；'.join(x['sku'] for x in mv),'sales30':sum(z['sales-shipped-last-30-days'] or 0 for z in fvals),'source':'；'.join(sorted({x['source'] for x in mv}))}
    entities[a]=ent
    if typ[0] in ['日常便签','满胶平叠便签','满胶卷带','纸质分隔便签'] and typ[2]!='尺寸待核' and qty and not pw:
        signatures[(typ[0],typ[1],typ[2],typ[4],typ[5],qty,unit,ent['color'])].append(ent)
merge=[];seen=set()
def addpair(a,b,reason):
    if a not in entities or b not in entities:return
    if set([a,b])==set(['B07FKJM2LX','B07T429N23']):return # 5084 two-pack versus 5088: color composition differs.
    x,y=entities[a],entities[b]
    if tuple(sorted([a,b])) in seen:return
    seen.add(tuple(sorted([a,b])))
    benefit='历史页面积累较强，优先核对' if y['reviews']>x['reviews'] and (x['stars'] is None or y['stars']>=x['stars']) else '重复商品候选，尚无页面改善证据'
    merge.append([a,x['stock'],x['rating'],b,y['stock'],y['rating'],reason,x['type'][1],x['type'][2],x['qty'],x['color'],x['sales30'],x['skus'],y['skus'],benefit,'核对当前页面、实物及条码一致后申请重复ASIN合并；主ASIN方向待核','未提交；历史评分未刷新'])
for vv in signatures.values():
    for x in vv:
        if not (x['stock'] or 0)>0:continue
        targets=[y for y in vv if y['asin']!=x['asin'] and (y['stock']==0 or y['stock'] is None)]
        for y in sorted(targets,key=lambda e:(-(e['reviews'] or 0),e['asin']))[:2]:addpair(x['asin'],y['asin'],'文本规格及装量匹配，页面质量待复核')
# User's 30315 benchmark and a directly comparable roll-note opportunity.
addpair('B07F295DPC','B07FKG29KB','30315对照：同为3×3、15本、100张/本；颜色组成及现有合并状态待核')
addpair('B08DKJ2K3T','B08CVLH794','PSS32x6：同规格6卷；历史参考16评3.6分对74评4分，后者另有5件在途')
merge.sort(key=lambda x:(x[0] not in ['B08DKJ2K3T','B07F295DPC'],not bool(x[5]),-x[11]))
stats={'rows':len(rows),'asins':len(byasin),'parent_candidates':sum(x['parent'] for x in master),'product_skus':sum(not x['parent'] for x in master),'product_asins':len({x['asin'] for x in master if not x['parent']}),'fine_categories':sum(k!='父体或占位记录 / 不适用' and not k.startswith('信息不足') for k in groups),'top_categories':len({x['category'] for x in master if x['category'] not in ['父SKU待核','待核实']}),'unknown_skus':sum(x['category']=='待核实' for x in master),'status':dict(collections.Counter(x['status'] for x in master)),'operations':dict(collections.Counter(x['op'] for x in master)),'archive_stats':archive_stats,'delete_list':len(delete_skus),'delete_list_present':len(delete_skus&set(cur)),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sources':[str(SOURCE),str(OLD),str(CAT)],'issues':dict(collections.Counter(x[2] for x in issues))}
stats.update({'types':len({(x['category'],x['type']) for x in master if not x['parent'] and x['category']!='待核实'}),'fba_rows':len(fba),'fba_fnskus':len(fba_unique),'fba_positive_rows':sum((inv(x,'available') or 0)>0 for x in fba),'fba_positive_fnskus':sum((x['available'] or 0)>0 for x in fba_unique),'fba_available_dedup':sum(x['available'] or 0 for x in fba_unique),'fba_reserved_dedup':sum(x['Total Reserved Quantity'] or 0 for x in fba_unique),'fba_inbound_dedup':sum(x['inbound-quantity'] or 0 for x in fba_unique),'fba_blank_available':sum(x['available'] is None for x in fba_unique),'fba_positive_sales30':sum((x['units-shipped-t30'] or 0)>0 for x in fba_unique),'fba_sales30_dedup':sum(x['sales-shipped-last-30-days'] or 0 for x in fba_unique),'fba_sales7_dedup':sum(x['sales-shipped-last-7-days'] or 0 for x in fba_unique),'deleted_with_available':sum(x[9]=='是' and (x[3] or 0)>0 for x in urgent),'deleted_available_units':sum(x[3] or 0 for x in urgent if x[9]=='是'),'urgent_rows':len(urgent),'merge_pairs':len(merge),'fba_sha256':hashlib.sha256(FBA.read_bytes()).hexdigest(),'fba_snapshot':'2026-10-30','operations':dict(collections.Counter(x['op'] for x in master))})
stats['sources'].append(str(FBA))
(ROOT/'analysis.json').write_text(json.dumps({'stats':stats,'summary':summary,'master':master,'asins':asinrows,'issues':issues,'ghost':ghost,'raw':rows,'fba_raw':fba,'fba_unique':fba_unique,'inventory':inventory,'urgent':urgent,'merge':merge},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2))
print('UNRESOLVED')
for a in dict.fromkeys(x['asin'] for x in master if x['category']=='待核实'):
    x=next(x for x in master if x['asin']==a);print(a,x['sku'],x['basis'])
