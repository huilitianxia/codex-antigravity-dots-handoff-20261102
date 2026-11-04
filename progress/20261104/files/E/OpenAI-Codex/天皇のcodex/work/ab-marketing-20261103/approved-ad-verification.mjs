export function install(b){
 b.verifyApprovedCampaign=async(rec,page=174)=>{
  const out={group:rec.group,campaignId:rec.campaignId,checked_at:new Date().toISOString()};
  const root='https://advertising.amazon.com/cm/sp/campaigns/'+rec.campaignId;
  const navigate=async(url)=>{try{await b.checkedTool('navigate_page',{pageId:page,type:'url',url});}catch(e){if(!String(e).includes('Navigation timeout'))throw e;}};
  const gridFn="()=>{const out={};for(const r of document.querySelectorAll('[role=row][row-id]')){const id=r.getAttribute('row-id');out[id]??={id,cells:{}};for(const c of r.querySelectorAll('[role=gridcell]')){if(c.innerText.trim())out[id].cells[c.getAttribute('col-id')]=c.innerText.trim();}}return {url:location.href,rows:Object.values(out)};}";
  const readGrid=async()=>b.decode(await b.checkedTool('evaluate_script',{pageId:page,waitForStableDom:false,function:gridFn}));
  try{
   await navigate(root+'/settings?entityId=ENTITY2EFMPU8GWXHSP');
   let s=await b.waitSnapshot(page,rec.group+'-approved-verified-settings',s=>s.includes(rec.name)&&s.includes('spinbutton "enter amount in US$"'),36);
   out.portfolio=s.includes('OLD_PRODUCTS_REACTIVATE_20261103_DAILY');
   out.campaign_running=s.includes('switch "正在投放" checked');
   out.daily=Number(s.split('\n').find(l=>l.includes('spinbutton "enter amount in US$"'))?.match(/value="([0-9.]+)"/)?.[1]);
   out.daily_matches=out.daily===Number(rec.daily);
   out.end=s.split('\n').find(l=>l.includes('textbox "结束日期"'))?.match(/value="([^"]+)"/)?.[1];
   out.end_matches=/2026.*11.*9|Nov 9, 2026/.test(out.end||'');
   out.down_only=s.includes('button " 动态竞价 - 仅降低"');
   await navigate(root+'/ad-groups?entityId=ENTITY2EFMPU8GWXHSP');
   s=await b.waitSnapshot(page,rec.group+'-approved-verified-adgroups',s=>s.includes(rec.group+'_'+rec.code+'_EXACT')&&s.includes('/targeting?'),36);
   const urls=[...s.matchAll(/url="([^"]+)"/g)].map(m=>m[1]);
   out.ads_url=urls.find(u=>u.includes('/ad-groups/')&&u.includes('/ads?'));
   out.targeting_url=urls.find(u=>u.includes('/ad-groups/')&&u.includes('/targeting?'));
   if(!out.ads_url||!out.targeting_url)throw Error('Missing ad-group URLs');
   await navigate(out.ads_url);
   await b.waitSnapshot(page,rec.group+'-approved-verified-products',s=>s.includes(rec.asin)&&rec.skus.every(sku=>s.includes(sku)),36);
   for(let n=0;n<20;n++){const d=await readGrid();out.products=d.rows.filter(r=>rec.skus.some(sku=>(r.cells.asin||'').split(/\n+/).map(x=>x.trim()).includes(sku)));out.products_running=rec.skus.every(sku=>out.products.some(r=>(r.cells.asin||'').includes(rec.asin)&&(r.cells.asin||'').split(/\n+/).map(x=>x.trim()).includes(sku)&&['进行中','正在投放','已启用'].includes(r.cells.status)));if(out.products_running)break;await new Promise(r=>setTimeout(r,350));}
   await navigate(out.targeting_url);
   await b.waitSnapshot(page,rec.group+'-approved-verified-targets',s=>s.includes('精准')&&s.toLowerCase().includes(rec.keywords[0].toLowerCase()),36);
   for(let n=0;n<20;n++){const d=await readGrid();out.targets=d.rows.filter(r=>rec.keywords.some(k=>(r.cells.target||'').split('\n')[0].toLowerCase()===k.toLowerCase()));out.targets_running=out.targets.length===rec.keywords.length&&rec.keywords.every(k=>out.targets.some(r=>(r.cells.target||'').split('\n')[0].toLowerCase()===k.toLowerCase()&&r.cells.matchType==='精准'&&r.cells.status==='进行中'&&Number(r.cells.bid?.match(/US\$([0-9.]+)/)?.[1])===Number(rec.bid)));if(out.targets_running)break;await new Promise(r=>setTimeout(r,350));}
   out.verified=out.portfolio&&out.campaign_running&&out.daily_matches&&out.end_matches&&out.down_only&&out.products_running&&out.targets_running;
   out.status=out.verified?'verified-running':'requires-review';
  }catch(e){out.status='verification-incomplete';out.error=String(e);out.verified=false;}
  rec.verification=out;rec.independently_verified=out.verified;
  await b.fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/approved-ad-execution-20261103.json',JSON.stringify(b.approvedAdsBatch.records,null,2));return out;
 };
}
