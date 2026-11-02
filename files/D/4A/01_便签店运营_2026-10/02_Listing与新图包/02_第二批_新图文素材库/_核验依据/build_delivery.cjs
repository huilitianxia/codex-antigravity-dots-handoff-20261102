const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/24243/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT='E:/Desktop/待上架_新图文素材库_第二批';
const J=JSON.parse(fs.readFileSync(ROOT+'/_核验依据/generation_jobs.json','utf8'));
const R=JSON.parse(fs.readFileSync(ROOT+'/_核验依据/revisions.json','utf8'));
const CAT=JSON.parse(fs.readFileSync(ROOT+'/_核验依据/Amazon_catalog_20261030.json','utf8'));
const defs=[
 {id:'305FA',folder:'305FullAdhesive',sku:'4A 305-Full Adhesive',asin:'B0FBG138ND',spec:'3 × 5 in · 5 pads × 20 sheets · 100 sheets total',correction:'按Amazon标题、五点及包装：5本×20张，共100张，不是100张/本。包装保留Non-stick edge；满胶示意须保留取纸边。'},
 {id:'608NL210',folder:'608NL210',sku:'4A 608-N-L-210',asin:'B07HDVVZ1B',spec:'6 × 8 in · 1 lined pad · 7 colors × 30 sheets · 210 sheets',correction:'按Amazon标题、五点及包装：6×8英寸，横向8英寸长边上胶，1本210张，7色×30张；不是4×6英寸。'},
 {id:'BS1801',folder:'BS1801',sku:'4A BS 1801',asin:'B07JVSYNYV',spec:'6 pads × 100 sheets · 600 sheets · Open desktop organizer',correction:'保留深色开放托盒、六组色块和前沿取纸缺口，不改为带盖硬盒。页面尺寸翻译混乱且各部件尺寸未独立核样，本轮仅标注功能分区。'}
];
const titles={"305FA_01":'主图｜五本立放',"305FA_02":'副图｜满胶与取纸边',"305FA_03":'副图｜洁净移除',"305FA_04":'副图｜3×5尺寸及100张规格',"305FA_05":'副图｜办公／厨房／冰箱',"608NL210_01":'主图｜210张七色厚本',"608NL210_02":'副图｜6×8尺寸与横线',"608NL210_03":'副图｜Smooth Writing',"608NL210_04":'副图｜清单与会议备忘',"608NL210_05":'副图｜七色与210张规格',BS1801_01:'主图｜六分区收纳套装',BS1801_02:'副图｜不同尺寸功能分区',BS1801_03:'副图｜取纸与收纳细节',BS1801_04:'副图｜商务礼赠场景',BS1801_05:'副图｜整洁办公桌面'};
const notes={
"305FA_01":['五本独立可数；绿、粉、橙、珊瑚、黄；无广告字道具。','20张/本纸厚、实际色值与批次须核样。'],
"305FA_02":['保留Full adhesive backing与Non-stick edge；明确示意。','实际无胶边宽度、胶面覆盖位置须实物核验；非微观胶层证据。'],
"305FA_03":['单张撕取动作；当前Listing支持clean removal/without damaging pages表述。','未做残胶或纸面损伤实测；上架采用前需确认性能依据。'],
"305FA_04":['原生SVG 3:5几何；5×20=100；仅英制。','颜色/纸面为尺寸示意，不是纸张色准证明。'],
"305FA_05":['办公、厨房、冰箱场景；贴附平整且未借用磁铁或夹子。','场景粘性与纸张比例仍须实物核验；不含耐热、防水承诺。'],
"608NL210_01":['单一纸本，7个连续色层；黄色横线顶页。','厚度、行距与批次色序须核样；图像不证明80GSM。'],
"608NL210_02":['原生SVG 8:6横向比例；横线平行等距；8英寸长边方向正确。','横线是版式示意，不宣称毫米行距或精确实物行数。'],
"608NL210_03":['色序已返修；钢笔/中性笔书写场景；未写No bleed。','Smooth Writing为书写场景，不作为不透墨测试；纸厚与色序须核样。'],
"608NL210_04":['已返修为两张薄纸；横向清单与会议纪要示例。','手写为用途展示；非预印清单；实际纸色和行距须核样。'],
"608NL210_05":['单本7色×30张=210；页面和包装支持规格。','实际纸厚、行距与批次色序须核样。'],
BS1801_01:['六个色块、深色开放托盒、三个前沿取纸区；无多余赠品。','托盒尺寸、壁厚、各便签尺寸与实际材料须核样。'],
BS1801_02:['六块结构与Notes/Quick reminders/Page markers/Lists四组功能标注对应。','未指定各部件英寸尺寸；数值待实物尺寸资料。'],
BS1801_03:['单张粉色索引条撕取；托盒与其他块保持原位。','实际取纸动作、胶位及托盒缺口细节须核样。'],
BS1801_04:['保留开放托盒；礼赠氛围由场景布光呈现；标明道具不包含。','未更改包装成礼盒；实物质感与批次色值须核样。'],
BS1801_05:['完整桌面套装，六色块正确；600张文案。','场景比例及部件尺寸须核样；场景道具不包含。']
};
const mkdir=p=>fs.mkdirSync(p,{recursive:true}),json=(p,o)=>fs.writeFileSync(p,JSON.stringify(o,null,2),'utf8');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
function svgBase(body){return '<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000"><defs><filter id="s" x="-25%" y="-25%" width="150%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#203040" flood-opacity=".13"/></filter><marker id="ar" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto-start-reverse"><path d="M0 0L9 4.5L0 9Z" fill="#46515b"/></marker></defs><rect width="2000" height="2000" fill="#fff"/><g font-family="Arial, sans-serif" fill="#101b24">'+body+'</g></svg>';}
function txt(x,y,size,str,weight=400,anchor='middle',fill='#101b24'){return '<text x="'+x+'" y="'+y+'" text-anchor="'+anchor+'" font-size="'+size+'" font-weight="'+weight+'" fill="'+fill+'">'+str+'</text>';}
function arrow(x1,y1,x2,y2){return '<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#46515b" stroke-width="2.5" marker-start="url(#ar)" marker-end="url(#ar)"/>';}
function dim305(){let b=txt(1000,160,103,'More room for your reminder',700)+txt(1000,258,49,'3 × 5 in full adhesive notes');
b+='<rect x="350" y="440" width="600" height="1000" fill="#f9fa65" filter="url(#s)"/>';
b+=arrow(350,375,950,375)+'<rect x="570" y="331" width="160" height="75" fill="white"/>'+txt(650,389,49,'3 in');
b+=arrow(250,440,250,1440)+'<rect x="174" y="899" width="152" height="82" fill="white"/>'+txt(250,959,49,'5 in');
b+=txt(650,1530,45,'15 sq in of sheet area',600);
b+=txt(1320,570,56,'Five bright colors',700,'start');
const colors=['#b9e561','#f578cc','#ffb12d','#ffc1a3','#f7fb56'];
colors.forEach((c,i)=>{b+='<rect x="'+(1190+i*110)+'" y="650" width="82" height="135" fill="'+c+'"/>';});
b+=txt(1190,980,100,'5 pads',700,'start')+txt(1190,1085,52,'20 sheets per pad',400,'start')+'<line x1="1190" y1="1175" x2="1770" y2="1175" stroke="#dce0e3" stroke-width="2"/>'+txt(1190,1310,82,'100 sheets',700,'start')+txt(1190,1400,44,'total',400,'start');
b+=txt(1000,1775,56,'Write. Plan. Keep it in view.',500)+txt(1000,1880,32,'Unlined pages for everyday notes',400,'middle','#61707b');return svgBase(b);}
function dim608(){let b=txt(1000,160,103,'Room to keep the details',700)+txt(1000,258,49,'6 × 8 in landscape lined notes');
b+='<rect x="400" y="560" width="1200" height="900" fill="#f9fa70" filter="url(#s)"/>';
for(let y=640;y<1420;y+=60)b+='<line x1="400" x2="1600" y1="'+y+'" y2="'+y+'" stroke="#b0b65c" stroke-opacity=".65" stroke-width="2"/>';
b+=arrow(400,480,1600,480)+'<rect x="920" y="435" width="160" height="80" fill="white"/>'+txt(1000,495,49,'8 in');
b+=arrow(300,560,300,1460)+'<rect x="222" y="970" width="156" height="80" fill="white"/>'+txt(300,1028,49,'6 in');
b+=txt(1000,1605,51,'Parallel ruling for lists, notes and next steps');
b+='<line x1="300" y1="1700" x2="1700" y2="1700" stroke="#e1e5e7" stroke-width="2"/>';
b+=txt(1000,1815,61,'1 pad · 7 colors · 210 sheets',700)+txt(1000,1900,31,'Landscape format · Adhesive along the 8 in edge',400,'middle','#61707b');return svgBase(b);}
function bboxAlpha(data,info,t){let l=info.width,top=info.height,r=-1,bot=-1;for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>t){l=Math.min(l,x);top=Math.min(top,y);r=Math.max(r,x);bot=Math.max(bot,y);}if(r<0)throw Error('Empty alpha');return {left:l,top,width:r-l+1,height:bot-top+1};}
async function mainOutput(src,out){
const {data,info}=await sharp(src).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const visible=bboxAlpha(data,info,0),solid=bboxAlpha(data,info,230);
const scale=Math.min(1878/Math.max(visible.width,visible.height),1800/Math.max(solid.width,solid.height));
const w=Math.round(visible.width*scale),h=Math.round(visible.height*scale),left=Math.floor((2000-w)/2),top=Math.floor((2000-h)/2);
const buf=await sharp(src).extract(visible).resize(w,h,{kernel:'lanczos3'}).png().toBuffer();
const rr=await sharp(buf).ensureAlpha().raw().toBuffer({resolveWithObject:true}),sb=bboxAlpha(rr.data,rr.info,230);
await sharp({create:{width:2000,height:2000,channels:3,background:'#ffffff'}}).composite([{input:buf,left,top}]).png().toFile(out);
const raw=await sharp(out).removeAlpha().raw().toBuffer();let total=0,white=0;for(let y=0;y<2000;y++)for(let x=0;x<2000;x++)if(x<60||x>=1940||y<60||y>=1940){let i=(y*2000+x)*3;total++;if(raw[i]===255&&raw[i+1]===255&&raw[i+2]===255)white++;}
return {pixel_dimensions:[2000,2000],safety_margins_including_shadow:[left,top,2000-left-w,2000-top-h],product_bbox_alpha230:{left:left+sb.left,top:top+sb.top,width:sb.width,height:sb.height},product_longest_span_percent:Math.max(sb.width,sb.height)/20,occupancy_definition:'主体外接框最长边占2000px画幅的比例；不是面积占比。alpha>230近似实体产品。',background_rgb:[255,255,255],border60_checked:total,border60_exact_white:white,white_background_pass:total===white,margin_pass:Math.min(left,top,2000-left-w,2000-top-h)>=60,occupancy_pass:Math.max(sb.width,sb.height)>=1700};
}
(async()=>{
const all=[];
for(const d of defs){
const dir=ROOT+'/'+d.folder;for(const sub of ['原图参考','生成源图','交付候选_2000px','审稿待核_2000px','可交付_已批准'])mkdir(dir+'/'+sub);
const dj=J.filter(j=>j.key.startsWith(d.id+'_')),refs=[...new Set(dj.flatMap(j=>j.refs))],reference_files=[];
for(let i=0;i<refs.length;i++){const dest=dir+'/原图参考/'+String(i+1).padStart(2,'0')+'_'+path.basename(refs[i]);fs.copyFileSync(refs[i],dest);reference_files.push({original:refs[i],copy:path.relative(dir,dest),sha256:hash(dest)});}
for(const j of [...dj,...R.filter(r=>r.key.startsWith(d.id+'_'))])fs.copyFileSync(j.source,dir+'/生成源图/'+j.key+'.png');
const images=[];
for(let n=1;n<=5;n++){
const id=d.id+'_'+String(n).padStart(2,'0'),j=dj.find(j=>j.key===id),revision=R.find(r=>r.parent===id),source=revision?.source||j?.source;
const native=id==='305FA_04'||id==='608NL210_02',hold=['305FA_02','305FA_03'].includes(id);
const file=(hold?'审稿待核_2000px/':'交付候选_2000px/')+id+'.png',out=dir+'/'+file;
let source_pixels,source_file,processing,tech=null;
if(native){const svg=id==='305FA_04'?dim305():dim608();source_file='生成源图/'+id+'_exact.svg';fs.writeFileSync(dir+'/'+source_file,svg);await sharp(Buffer.from(svg)).png().toFile(out);source_pixels=[2000,2000];processing='原生SVG精确比例绘制并直接渲染2000×2000，无放大；示意图不等于实物照片。';}
else{const meta=await sharp(source).metadata();source_pixels=[meta.width,meta.height];source_file='生成源图/'+(revision?.key||id)+'.png';
if(n===1){tech=await mainOutput(source,out);processing='内置imagegen透明底源图；按alpha外接框去除空白，Lanczos3等比插值；主体最长边约90%；合成RGB255白底；不恢复真实细节。';}
else{await sharp(source).resize(2000,2000,{fit:'contain',background:'white',kernel:'lanczos3'}).flatten({background:'white'}).png().toFile(out);processing='内置imagegen；Lanczos3等比插值至2000×2000；源图留存；不是原生2000像素细节或AI超分。';}}
const entry={id,sku:d.sku,asin:d.asin,order:n,role:n===1?'main':'secondary',title:titles[id],file,pixels:[2000,2000],generation_method:native?'exact_vector_diagram':'built_in_imagegen',generation_source:source_file,generation_source_pixels:source_pixels,processing,reference_sources:reference_files,review_status:hold?'needs_claim_or_structure_check':'final_candidate',design_check:notes[id][0],pending_checks:[notes[id][1],'实际批次颜色、纸质与尺寸仍需实物核样；未获得发布批准。'],catalog_source:'https://www.amazon.com/dp/'+d.asin,approved_for_automation:false,approved_for_upload:false,physical_sample_verified:false,technical_checks:tech,sha256:hash(out)};
images.push(entry);all.push({...entry,folder:d.folder});
}
json(dir+'/manifest.json',{sku:d.sku,asin:d.asin,spec:d.spec,correction:d.correction,date:'2026-10-30 Asia/Shanghai',status_definitions:{final_candidate:'本轮设计检查完成，待实物核样和最终采用',needs_claim_or_structure_check:'有明确结构或性能待核项，先审稿',approved:'审核通过后才可进入已批准目录；本轮未设置'},approved_files:[],images});
fs.writeFileSync(dir+'/可交付_已批准/当前无已批准文件.txt','当前为本地审稿和交付候选，尚未实物核样或批准发布。','utf8');
const comp=[];for(let i=0;i<images.length;i++)comp.push({input:await sharp(dir+'/'+images[i].file).resize(400,400).png().toBuffer(),left:i*400,top:0});
await sharp({create:{width:2000,height:400,channels:3,background:'white'}}).composite(comp).png().toFile(dir+'/preview.png');
const cards=images.map(e=>'<article><h2>'+esc(e.title)+'</h2><span class="'+(e.review_status==='final_candidate'?'tag':'hold')+'">'+(e.review_status==='final_candidate'?'交付候选 · 未批准上架':'审稿待核')+'</span><a href="'+e.file+'"><img src="'+e.file+'"></a><p>'+esc(e.design_check)+'</p><p class="muted">'+esc(e.pending_checks[0])+'</p>'+(e.technical_checks?'<p>主图主体最长边占比 '+e.technical_checks.product_longest_span_percent.toFixed(1)+'%；四边安全边距≥'+Math.min(...e.technical_checks.safety_margins_including_shadow)+'px。</p>':'')+'</article>').join('');
fs.writeFileSync(dir+'/审稿.html',page(d.sku,'<h1>'+esc(d.sku)+'</h1><p>'+esc(d.spec)+'</p><p class="note">'+esc(d.correction)+'</p><section class="grid">'+cards+'</section><p><a href="manifest.json">完整manifest</a> · <a href="../审稿总览.html">总览</a></p>'),'utf8');
}
json(ROOT+'/交付总清单.json',{date:'2026-10-30 Asia/Shanghai',count:15,final_candidates:13,needs_review:2,approved_count:0,all_2000px:true,main_checks_pass:all.filter(x=>x.role==='main').every(x=>x.technical_checks.white_background_pass&&x.technical_checks.margin_pass&&x.technical_checks.occupancy_pass),images:all});
let body='<h1>4A · 第二批主副图</h1><p>3款 × 5张 · 全部2000×2000 PNG · 2026-10-30</p><p>13张交付候选＋2张结构/性能待核稿；可交付已批准0张。候选图仍需实物核样。未上传或修改Amazon。</p><div class="note"><b>Catalog核对后采用：</b><p>305：3×5英寸，5本×20张＝100张，保留非粘取纸边。<br>608：6×8英寸、1本、7色×30张＝210张，沿8英寸长边上胶。<br>BS1801：实际开放托盒，6组×100张＝600张；保留原分区与取纸缺口。</p><p>未取得80 GSM、不透墨或精确毫米行距证据。305洁净移除表述来源于当前Listing，仍需性能资料复核。</p></div>';
for(const d of defs)body+='<article class="wide"><h2>'+esc(d.sku)+'</h2><a href="'+d.folder+'/审稿.html"><img src="'+d.folder+'/preview.png"></a><p><a href="'+d.folder+'/审稿.html">查看5张大图和逐图待核项</a> · <a href="'+d.folder+'/manifest.json">manifest</a></p></article>';
body+='<p><a href="交付说明.txt">交付说明</a> · <a href="_核验依据/generation_jobs.json">生成提示词</a> · <a href="_核验依据/Amazon_catalog_20261030.json">Amazon核验记录</a></p>';
fs.writeFileSync(ROOT+'/审稿总览.html',page('4A 第二批审稿',body),'utf8');
const sheet=[];for(let i=0;i<all.length;i++)sheet.push({input:await sharp(ROOT+'/'+all[i].folder+'/'+all[i].file).resize(400,400).png().toBuffer(),left:i%5*400,top:Math.floor(i/5)*400});
await sharp({create:{width:2000,height:1200,channels:3,background:'white'}}).composite(sheet).png().toFile(ROOT+'/15张总预览.png');
console.log(JSON.stringify({count:all.length,main_checks:all.filter(x=>x.role==='main').map(x=>({id:x.id,...x.technical_checks}))},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
function page(title,body){return '<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+esc(title)+'</title><style>body{font:16px/1.65 system-ui,Microsoft YaHei,sans-serif;color:#17232e;background:#f4f6f7;margin:40px}main{max-width:1500px;margin:auto}h1{font-size:36px}h2{font-size:20px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}article{background:white;padding:22px;border-radius:12px;margin:20px 0}.grid article{margin:0}img{width:100%;display:block;margin-top:14px}a{color:#215a80}.tag,.hold{font-size:13px;padding:5px 9px;border-radius:5px;background:#e8eff2}.hold{background:#fff0d5}.note{background:#fff6df;padding:20px;border-radius:10px;margin:22px 0}.muted{color:#705e46}@media(max-width:900px){.grid{grid-template-columns:1fr}body{margin:16px}}</style><main>'+body+'</main></html>';}


