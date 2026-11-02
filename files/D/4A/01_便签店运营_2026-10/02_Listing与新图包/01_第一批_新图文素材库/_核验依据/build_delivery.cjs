const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/24243/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT='E:/Desktop/待上架_新图文素材库';
const jobs=JSON.parse(fs.readFileSync(path.join(ROOT,'_核验依据/generation_jobs.json'),'utf8'));
const revisions=JSON.parse(fs.readFileSync(path.join(ROOT,'_核验依据/revisions.json'),'utf8'));
const skus={PSS32x6:{sku:'4A PSS 32x6',asin:'B08CVLH794',spec:'0.6 × 393 in per roll; 6 rolls with individual cutters',colors:'coral / lime green / orange / yellow / pink / blue'},'5084NL':{sku:'4A 5084-N-L',asin:'B07DJPCBLV',spec:'5 × 8 in; 4 lined pads; 50 sheets/pad; 200 sheets total',colors:'pink / yellow / lime green / blue'},'301x12':{sku:'4A 301x12-Y',asin:'B01LVWFZVZ',spec:'1.5 × 2 in; 12 yellow unlined pads; 100 sheets/pad; 1200 sheets total',colors:'Yellow'}};
const titles={
PSS32x6_01:'主图｜六盒白底',PSS32x6_02:'副图｜拉出与切割',PSS32x6_03:'副图｜书写与全背胶用途',PSS32x6_04:'副图｜电线／文件／收纳／实验室分类',PSS32x6_05:'副图｜六盒与卷长规格',
'5084NL_01':'主图｜四本四色叠放','5084NL_02':'副图｜精确纸面面积对比','5084NL_03':'副图｜Daily To-Do','5084NL_04':'副图｜会议与排班','5084NL_05':'副图｜显示器边框与白板',
'301x12_01':'主图｜十二本金字塔排列','301x12_02':'副图｜教材索引','301x12_03':'副图｜手写签字提示','301x12_04':'副图｜尺寸与钢笔参照','301x12_05':'副图｜1200张规格'};
const checks={
PSS32x6_01:['六盒可数；六色；无广告字和额外道具','切刀齿形、透明外壳与实际批次复核'],
PSS32x6_02:['两步标题及0.6/393英寸文字正确','切割画面与拉出姿势差异较小；需实物切割动作核验后定稿'],
PSS32x6_03:['书写与贴附用途清楚；无耐热或绝缘承诺','背面呈浅色，背面纸色及全背胶结构需实物复核；不得作为胶层证明'],
PSS32x6_04:['四种分类场景；电线仅作识别；无绝缘暗示','标签与道具尺度为场景示意；场景道具不包含在商品中'],
PSS32x6_05:['六盒六色可数；0.6英寸宽/393英寸每卷文字正确','外壳、纸色与实物批次复核'],
'5084NL_01':['四本可数；粉黄绿蓝；有横线；无广告字和道具','实际行距、纸色、纸张厚度需核样'],
'5084NL_02':['矢量几何按130像素/英寸：650×1040与390×390；面积比40/9','比较的是整张纸面积；不表示书写效率或胶面积'],
'5084NL_03':['Daily To-Do手写正确；黄色有横线','纸张长宽在透视下为示意；实际行距待核样'],
'5084NL_04':['蓝/粉两张；会议纪要/排班；4×50=200文案正确','场景中展示样品，不代表整包数量；实际纸厚与行距待核样'],
'5084NL_05':['便签位于显示器下边框下方，未遮屏；白板无磁铁图钉','显示器尺度及短边胶位与实物核对；场景不作为持粘测试'],
'301x12_01':['3+4+5共12本清楚可数；黄色无横线；无道具和广告字','单本纸厚和实际黄度需核样'],
'301x12_02':['教材索引及手写用途；黄色无横线；规格正确','索引露出部分为书边示意；短边胶位及书页比例需核样'],
'301x12_03':['已将整本厚度修成单张；Sign Here明显手写；有Blank notes说明','手写与合同仅使用示例；未暗示预印标签；实际尺寸比例需核样'],
'301x12_04':['1.5×2英寸尺寸；黄色无横线；钢笔参照','生成纸面宽高近似3:4；钢笔仅参照，未宣称钢笔长度；需实物比例核样'],
'301x12_05':['3×4共12本可数；12×100=1200文字正确','纸厚及黄度需核样']
};
const mkdir=p=>fs.mkdirSync(p,{recursive:true}),writeJSON=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2),'utf8');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
function comparisonSVG(){
let lines='';for(let y=500;y<1430;y+=40)lines+='<line x1="360" y1="'+y+'" x2="1010" y2="'+y+'" stroke="#4fa9c8" stroke-opacity=".62" stroke-width="1.8"/>';
return '<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000" viewBox="0 0 2000 2000"><defs><filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#18232c" flood-opacity=".14"/></filter><linearGradient id="blue" x2=".7" y2="1"><stop stop-color="#7ed1eb"/><stop offset="1" stop-color="#68c6e2"/></linearGradient><marker id="arr" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="#39454f"/></marker></defs><rect width="2000" height="2000" fill="#fff"/><g font-family="Arial, sans-serif" fill="#0b1620" text-anchor="middle"><text x="1000" y="165" font-size="104" font-weight="700">Room for the details</text><text x="1000" y="260" font-size="52">Compare the sheet area</text><rect x="360" y="430" width="650" height="1040" fill="url(#blue)" filter="url(#shadow)"/>'+lines+'<rect x="1260" y="1080" width="390" height="390" fill="#eeefef" filter="url(#shadow)"/><g stroke="#39454f" stroke-width="2.6" marker-start="url(#arr)" marker-end="url(#arr)"><line x1="360" y1="375" x2="1010" y2="375"/><line x1="260" y1="430" x2="260" y2="1470"/><line x1="1260" y1="1020" x2="1650" y2="1020"/><line x1="1780" y1="1080" x2="1780" y2="1470"/></g><g fill="white"><rect x="610" y="331" width="150" height="75"/><rect x="180" y="909" width="160" height="82"/><rect x="1380" y="980" width="150" height="75"/><rect x="1700" y="1235" width="160" height="80"/></g><g font-size="49"><text x="685" y="383">5 in</text><text x="260" y="969">8 in</text><text x="1455" y="1030">3 in</text><text x="1780" y="1294">3 in</text></g><g font-size="52" font-weight="700"><text x="685" y="1580">5 × 8 in · 40 sq in</text><text x="1455" y="1580">3 × 3 in · 9 sq in</text></g><line x1="300" y1="1690" x2="1780" y2="1690" stroke="#e3e6e8" stroke-width="2"/><text x="1000" y="1800" font-size="62">About 4.44× the sheet area</text><text x="1000" y="1895" font-size="32" fill="#67727b">Sheet area comparison · Same scale</text></g></svg>';
}
(async()=>{
let all=[];
for(const [key,p] of Object.entries(skus)){
const dir=path.join(ROOT,key);for(const d of ['原图参考','生成源图','交付候选_2000px','审稿待核_2000px','可交付_已批准'])mkdir(path.join(dir,d));
const refs=[...new Set(jobs.filter(j=>j.key.startsWith(key+'_')).flatMap(j=>j.refs))];
const refMap=[];for(let i=0;i<refs.length;i++){let dest=path.join(dir,'原图参考',String(i+1).padStart(2,'0')+'_'+path.basename(refs[i]));fs.copyFileSync(refs[i],dest);refMap.push({original:refs[i],copy:path.relative(dir,dest),sha256:hash(dest)});}
let entries=[];
for(const j of jobs.filter(j=>j.key.startsWith(key+'_'))){
const rev=revisions.find(r=>r.parent===j.key),source=rev?.source||j.source;
for(const item of [j,...revisions.filter(r=>r.parent===j.key)])fs.copyFileSync(item.source,path.join(dir,'生成源图',item.key+'.png'));
const hold=['PSS32x6_02','PSS32x6_03'].includes(j.key),folder=hold?'审稿待核_2000px':'交付候选_2000px',filename=j.key+'.png',out=path.join(dir,folder,filename),meta=await sharp(source).metadata();
let processing='';
if(j.key==='5084NL_02'){const svg=comparisonSVG();fs.writeFileSync(path.join(dir,'生成源图',j.key+'_exact.svg'),svg);await sharp(Buffer.from(svg)).png().toFile(out);processing='尺寸对比信息图由SVG原生渲染至2000×2000；不缩放生成图；单位比例130px/in。两次AI比例稿仅留存、不选用。';}
else if(j.key.endsWith('_01')){await sharp(source).resize(1800,1800,{fit:'contain',background:{r:255,g:255,b:255,alpha:0},kernel:'lanczos3'}).flatten({background:'#ffffff'}).extend({top:100,bottom:100,left:100,right:100,background:'#ffffff'}).png().toFile(out);processing='内置imagegen透明底返修源图；Lanczos3等比缩放至1800方框；合成RGB255白底；四边各100px白色边距；未恢复真实细节。';}
else {await sharp(source).resize(2000,2000,{fit:'contain',background:'#ffffff',kernel:'lanczos3'}).flatten({background:'#ffffff'}).png().toFile(out);processing='Lanczos3等比插值至2000×2000；源图约1254px；无AI超分、未恢复真实细节。';}
const {data,info}=await sharp(out).removeAlpha().raw().toBuffer({resolveWithObject:true});
let bg=null;
if(j.key.endsWith('_01')){
let total=0,white=0;for(let y=0;y<2000;y++)for(let x=0;x<2000;x++)if(x<60||x>=1940||y<60||y>=1940){total++;let i=(y*2000+x)*3;if(data[i]===255&&data[i+1]===255&&data[i+2]===255)white++;}
bg={border_test_width_px:60,border_pixels_checked:total,exact_rgb_255_pixels:white,pass:white===total,method:'透明底合成纯白；边框逐像素核验。产品与浅接触阴影区域不要求为纯白。'};
}
const e={sku:p.sku,asin:p.asin,id:j.key,title:titles[j.key],order:Number(j.key.slice(-2)),role:j.key.endsWith('_01')?'main':'secondary',file:folder+'/'+filename,pixels:[info.width,info.height],reference_sources:refMap,generation_source:j.key==='5084NL_02'?'生成源图/'+j.key+'_exact.svg':'生成源图/'+(rev?.key||j.key)+'.png',generation_source_pixels:j.key==='5084NL_02'?[2000,2000]:[meta.width,meta.height],processing,color_verification:key==='5084NL'?'2026-10-30 Amazon同一子ASIN主图及PT01显示粉黄绿蓝；文字仅称4 Neon Colors；无橙色或80GSM依据。':'Amazon标题/五点和原始素材一致；色值非实物色准测量。',review_status:hold?'needs_product_check':'final_candidate',design_check:checks[j.key][0],pending_checks:[checks[j.key][1],'生成产品图仍需实物批次核样；尚未获得发布批准'],approved_for_automation:false,approved_for_upload:false,physical_sample_verified:false,white_background_check:bg,sha256:hash(out)};
entries.push(e);all.push({...e,root:key});
}
writeJSON(path.join(dir,'manifest.json'),{product:p,created_at:'2026-10-30 Asia/Shanghai',generation_mode:'内置imagegen；尺寸对比图为精确SVG图形',specification_conflicts:key==='301x12'?['Amazon大小属性3×2与标题/五点/包装1.5×2不一致；采用三方一致的1.5×2，后台未改。']:[],status_definitions:{final_candidate:'已完成本轮设计检查，待实物核样和最终采用；不等于已批准上架',needs_product_check:'存在明确待核或需改进项目，先审稿',approved:'仅明确审核通过后进入可交付_已批准，并设置approved_for_automation=true'},approved_files:[],images:entries});
fs.writeFileSync(path.join(dir,'可交付_已批准','当前无已批准文件.txt'),'当前为本地设计候选与审稿稿件。未经实物核样或明确审核，不自动归类为已批准，不上传亚马逊。','utf8');
const thumbs=[];for(let i=0;i<entries.length;i++)thumbs.push({input:await sharp(path.join(dir,entries[i].file)).resize(400,400).png().toBuffer(),left:i*400,top:0});
await sharp({create:{width:2000,height:400,channels:3,background:'white'}}).composite(thumbs).png().toFile(path.join(dir,'preview.png'));
const cards=entries.map(e=>'<article><h2>'+esc(e.title)+'</h2><span class="'+(e.review_status==='needs_product_check'?'hold':'tag')+'">'+(e.review_status==='needs_product_check'?'审稿待核':'交付候选 · 未批准上架')+'</span><a href="'+e.file+'"><img src="'+e.file+'"></a><p>'+esc(e.design_check)+'</p><p class="muted">'+esc(e.pending_checks[0])+'</p></article>').join('');
const html='<!doctype html><html lang="zh"><meta charset="utf-8"><title>'+key+' 图像审稿</title><style>body{font:16px/1.65 system-ui,Microsoft YaHei;background:#f5f6f7;color:#15212a;margin:40px}main{max-width:1500px;margin:auto}h1{font-size:32px}section{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}article{background:white;padding:20px;border-radius:12px}img{width:100%;margin-top:12px}h2{font-size:18px}.tag,.hold{padding:5px 10px;font-size:13px;background:#e8eef3;border-radius:6px}.hold{background:#fff0d4}.muted{color:#6a5a43}a{color:#255b80}</style><main><h1>'+esc(p.sku)+' · 5张图片</h1><p>'+esc(p.spec)+'</p><p>2000 × 2000 PNG；原图与生成源图保留。交付候选仍待实物核样与最终采用。可交付已批准：0张。未上传或修改Amazon。</p><section>'+cards+'</section><p><a href="manifest.json">查看完整manifest</a> · <a href="../审稿总览.html">回到总览</a></p></main></html>';
fs.writeFileSync(path.join(dir,'审稿.html'),html,'utf8');
}
const index='<!doctype html><html lang="zh"><meta charset="utf-8"><title>4A 三款主副图审稿</title><style>body{font:17px/1.65 system-ui,Microsoft YaHei;margin:50px;background:#f6f7f8;color:#15212a}main{max-width:1450px;margin:auto}section{background:white;padding:25px;margin:25px 0;border-radius:14px}img{width:100%}a{color:#255b80}h1{font-size:36px}</style><main><h1>4A · 三款主副图审稿</h1><p>2026-10-30 · 每款1张主图＋4张副图，共15张 · 全部2000×2000</p><p>13张交付候选，2张审稿待核。交付候选表示本轮设计检查完成，仍待实物核样；已批准上架为0张。</p><p>5084已核对Amazon子ASIN B07DJPCBLV主图及PT01：粉、黄、绿、蓝。页面当前显示无货；不将Listing图文核验称为库存可售确认。301x12大小属性有冲突，以标题、五点与包装一致的1.5×2英寸制作。</p>'+Object.entries(skus).map(([k,v])=>'<section><h2>'+esc(v.sku)+'</h2><a href="'+k+'/审稿.html"><img src="'+k+'/preview.png"></a><p><a href="'+k+'/审稿.html">打开五张大图与逐图待核项</a> · <a href="'+k+'/manifest.json">manifest.json</a></p></section>').join('')+'<p>未重做30315、5082、406x6旧包。所有源图保留。未上传或修改Amazon后台。</p></main></html>';
fs.writeFileSync(path.join(ROOT,'审稿总览.html'),index,'utf8');
writeJSON(path.join(ROOT,'交付总清单.json'),{date:'2026-10-30',image_count:all.length,final_candidates:13,needs_product_check:2,approved_count:0,all_2000px:all.every(e=>e.pixels[0]===2000&&e.pixels[1]===2000),main_white_pass:all.filter(e=>e.role==='main').every(e=>e.white_background_check.pass),images:all});
const merged=[];for(let i=0;i<all.length;i++){merged.push({input:await sharp(path.join(ROOT,all[i].root,all[i].file)).resize(400,400).png().toBuffer(),left:(i%5)*400,top:Math.floor(i/5)*400});}
await sharp({create:{width:2000,height:1200,channels:3,background:'white'}}).composite(merged).png().toFile(path.join(ROOT,'15张总预览.png'));
console.log(JSON.stringify({count:all.length,all_2000px:all.every(e=>e.pixels[0]===2000&&e.pixels[1]===2000),main_white:all.filter(e=>e.role==='main').map(e=>({id:e.id,check:e.white_background_check})),root:ROOT},null,2));
})().catch(e=>{console.error(e);process.exit(1)});



