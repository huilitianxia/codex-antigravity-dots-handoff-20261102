// UI-only campaign creation. Loaded into the already-authorized Chrome connection.
adb.firstUidMatching = async (page, test, label) => {
  const s = await adb.saveSnap(page, 'last-page-' + page);
  const lines = s.split('\n').filter(l => test(l) && !l.includes('disableable disabled'));
  if (!lines.length) throw new Error('Missing ' + label);
  return lines[0].match(/uid=([^\s]+)/)[1];
};
adb.clickMatching = async (page, test, label) => {
  const uid = await adb.firstUidMatching(page, test, label);
  await adb.checkedTool('click', {pageId:page, uid});
  await new Promise(r => setTimeout(r,350));
};
adb.waitSnapshot = async (page, label, test, limit=24) => {
  for (let k=0;k<limit;k++) {
    await new Promise(r=>setTimeout(r,350));
    const s=await adb.saveSnap(page,label);
    if (test(s)) return s;
  }
  throw new Error('UI did not reach ' + label);
};
adb.setEndDate = async (page, dateLabel) => {
  await adb.clickNamed(page,'button','选择结束日期');
  let s=await adb.saveSnap(page,'end-date-calendar-'+page);
  const year=s.split('\n').find(l=>/button "20\d\d".*haspopup="listbox"/.test(l));
  if (!year) throw new Error('Missing end date year');
  if (!year.includes('"2026"')) {
    await adb.checkedTool('click',{pageId:page,uid:year.match(/uid=([^\s]+)/)[1]});
    await new Promise(r=>setTimeout(r,250));
    await adb.clickNamed(page,'option','2026');
  }
  s=await adb.saveSnap(page,'end-date-year-'+page);
  const month=s.split('\n').find(l=>/button "(January|February|March|April|May|June|July|August|September|October|November|December)".*haspopup="listbox"/.test(l));
  if (!month) throw new Error('Missing end date month');
  if (!month.includes('"November"')) {
    await adb.checkedTool('click',{pageId:page,uid:month.match(/uid=([^\s]+)/)[1]});
    await new Promise(r=>setTimeout(r,250));
    await adb.clickNamed(page,'option','November');
  }
  await adb.clickNamed(page,'button',dateLabel);
};
adb.addExactSku = async (page,spec,sku) => {
  let s=await adb.waitSnapshot(page,'product-search-'+spec.group,s=>s.includes('switch "所有商品"'));
  if (!s.includes('switch "所有商品" checked')) await adb.clickNamed(page,'switch','所有商品');
  const search=await adb.namedUid(page,'searchbox','按商品名称、ASIN 或 SKU 搜索');
  await adb.typeUid(page,search,spec.asin,'Enter');
  s=await adb.waitSnapshot(page,'product-match-'+spec.group, s=>s.includes('StaticText "'+sku+'"')&&s.includes('StaticText "'+spec.asin+'"'));
  const lines=s.split('\n');
  const at=lines.findIndex(l=>l.includes('StaticText "'+sku+'"'));
  if(at<0||!lines.slice(Math.max(0,at-10),at).some(l=>l.includes(spec.asin))) throw new Error('SKU identity mismatch: '+sku);
  const add=lines.slice(at+1,at+7).find(l=>l.includes('button "添加"')&&!l.includes('disabled'));
  if(!add) throw new Error('SKU not eligible for add: '+sku);
  await adb.checkedTool('click',{pageId:page,uid:add.match(/uid=([^\s]+)/)[1]});
  await adb.waitSnapshot(page,'product-added-'+spec.group,s=>{const rows=s.split('\n');const n=rows.findIndex(l=>l.includes('StaticText "'+sku+'"'));return n>=0&&rows.slice(n+1,n+7).some(l=>l.includes('button "已添加"'));});
};
adb.createPrecisionCampaign = async spec => {
  const page=2;
  const rec={...spec,name:'SP_REACTIVATE_'+spec.group+'_'+spec.code+'_EXACT_20261102',status:'building',stage:'open',sent:false,started_at:new Date().toISOString()};
  adb.adBatch.records.push(rec);adb.adBatch.current=rec.group;
  const persist=async()=>adb.fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/precision-ad-execution.json',JSON.stringify(adb.adBatch.records,null,2));
  try {
    await persist();
    await adb.checkedTool('navigate_page',{pageId:page,type:'url',url:'https://advertising.amazon.com/cb/sp?entityId=ENTITY2EFMPU8GWXHSP&ref=alltoolsnav'});
    await adb.waitSnapshot(page,'builder-'+spec.group,s=>s.includes('textbox "广告组名称"')&&s.includes('searchbox "按商品名称、ASIN 或 SKU 搜索"'));
    rec.stage='products';
    for(const sku of spec.skus) await adb.addExactSku(page,spec,sku);
    rec.stage='manual';
    await adb.clickMatching(page,l=>l.includes('radio "手动投放 '),'manual targeting');
    let s=await adb.waitSnapshot(page,'keyword-ready-'+spec.group,s=>s.includes('竞价选择')&&s.includes('关键词投放'));
    const section=s.slice(s.indexOf('heading "关键词投放"'));
    const list=section.split('\n').find(l=>l.includes('button "输入列表"'));
    if(!list) throw new Error('Missing keyword input tab');
    await adb.checkedTool('click',{pageId:page,uid:list.match(/uid=([^\s]+)/)[1]});
    s=await adb.saveSnap(page,'keyword-input-'+spec.group);
    const keywordSection=s.slice(s.indexOf('heading "关键词投放"'));
    const deleteAll=keywordSection.split('\n').find(l=>l.includes('button "删除所有"')&&!l.includes('disabled'));
    if(deleteAll) await adb.checkedTool('click',{pageId:page,uid:deleteAll.match(/uid=([^\s]+)/)[1]});
    await adb.clickMatching(page,l=>l.includes('button "竞价选择 '),'bid selector');
    await adb.clickMatching(page,l=>l.includes('option "自定义竞价 '),'custom bidding');
    const custom=await adb.firstUidMatching(page,l=>l.includes('textbox "US$')&&l.includes('针对关键词的竞价，匹配类型'),'custom bid input');
    await adb.typeUid(page,custom,String(spec.bid));
    await adb.checkedTool('evaluate_script',{pageId:page,function:"()=>{for(const type of ['BROAD','PHRASE']){const e=document.querySelector('input[data-match-type='+type+']');if(!e)throw new Error('Missing match checkbox '+type);if(e.checked)e.click();}const exact=document.querySelector('input[data-match-type=EXACT]');if(exact&&!exact.checked)exact.click();const video=document.querySelector('input[data-takt-id=\"SPVCreativeCard:AutoAssemble:Checkbox\"]');if(video?.checked)video.click();return 'Exact-only';}"});
    const keywordText=spec.keywords.join('\n');
    await adb.checkedTool('evaluate_script',{pageId:page,function:"()=>{const e=document.getElementById('kwp:kwp-enter-list-text-input-area');const v="+JSON.stringify(keywordText)+";Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(e,v);e.dispatchEvent(new InputEvent('input',{bubbles:true,data:v}));return e.value;}"});
    await adb.clickNamed(page,'button','添加关键词');
    s=await adb.waitSnapshot(page,'keywords-added-'+spec.group,s=>s.split('\n').filter(l=>/textbox.*针对关键词.+EXACT匹配类型/.test(l)).length===spec.keywords.length);
    const groupLines=s.split('\n');
    for(let i=0;i<groupLines.length;i++){
      if(groupLines[i].includes('GROUP匹配类型')){
        const remove=groupLines.slice(i+1,i+4).find(l=>/uid=\S+ button\s*$/.test(l));
        if(!remove)throw new Error('Cannot identify default category removal');
        await adb.checkedTool('click',{pageId:page,uid:remove.match(/uid=([^\s]+)/)[1]});
        await new Promise(r=>setTimeout(r,350));
      }
    }
    await adb.waitSnapshot(page,'exact-only-'+spec.group,s=>s.includes('已添加 '+spec.keywords.length+' 个')&&!s.includes('GROUP匹配类型'));
    rec.stage='campaign-settings';
    await adb.typeUid(page,await adb.namedUid(page,'textbox','广告组名称'),spec.group+'_'+spec.code+'_EXACT');
    await adb.typeUid(page,await adb.namedUid(page,'textbox','广告活动名称'),rec.name);
    await adb.typeUid(page,await adb.namedUid(page,'textbox','enter amount in $'),String(spec.daily));
    await adb.clickMatching(page,l=>l.includes('radio "动态竞价 - 仅降低 '),'down-only strategy');
    await adb.setEndDate(page,'Tuesday November 10 2026');
    await adb.clickNamed(page,'button','选择广告组合');
    await adb.clickNamed(page,'option','OLD_PRODUCTS_REACTIVATE_20261102_300USD');
    s=await adb.saveSnap(page,spec.group+'-before-submit');
    const bidLines=s.split('\n').filter(l=>/textbox.*针对关键词.+EXACT匹配类型/.test(l));
    const bidExpected=Number(spec.bid).toFixed(2);
    if(bidLines.length!==spec.keywords.length||bidLines.some(l=>!l.includes('value="'+bidExpected+'"'))) throw new Error('Exact keyword bid mismatch');
    if(!s.includes(spec.skus.length+' 件商品')||!s.includes('value="Nov 10, 2026"')||!s.includes('value="'+Number(spec.daily).toFixed(2)+'"')||!s.includes('OLD_PRODUCTS_REACTIVATE_20261102_300USD')) throw new Error('Campaign settings mismatch');
    if(!s.split('\n').some(l=>l.includes('radio "动态竞价 - 仅降低')&&l.includes('checked'))) throw new Error('Down-only not checked');
    const badChecked=s.split('\n').filter(l=>/checkbox "(Include 加拿大|Include 墨西哥|提高高流量日子的竞价|应用到此广告活动)/.test(l)&&l.includes('checked'));
    if(badChecked.length) throw new Error('Unexpected expansion: '+badChecked.join(';'));
    rec.stage='submit';rec.sent=true;rec.sent_at=new Date().toISOString();await persist();
    await adb.clickNamed(page,'button','启动1个广告活动');
    const receipt=await adb.waitSnapshot(page,spec.group+'-launch-success',s=>s.includes('恭喜，您的广告活动已成功启动。'),36);
    const url=adb.decode(await adb.checkedTool('evaluate_script',{pageId:page,waitForStableDom:false,function:'()=>location.href'}));
    const parsed=new URL(url);rec.campaignId=parsed.searchParams.get('campaign');rec.publicCampaignId=parsed.searchParams.get('publicCampaign');
    rec.status='launched';rec.stage='pending-independent-verification';rec.finished_at=new Date().toISOString();await persist();
  } catch(e) { rec.status=rec.sent?'submission-uncertain':'not-launched';rec.error=String(e);await persist(); }
  return rec;
};
