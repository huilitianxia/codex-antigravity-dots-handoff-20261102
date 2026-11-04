export function install(mergeBrowser){mergeBrowser.resumeCurrentFromProducts=async()=>{const rec=mergeBrowser.approvedAdsBatch.records.at(-1),spec=rec,page=rec.page;if(rec.sent)throw Error('Already submitted');const persist=async()=>mergeBrowser.fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/approved-ad-execution-20261103.json',JSON.stringify(mergeBrowser.approvedAdsBatch.records,null,2));try{const pre=await mergeBrowser.snap(page,rec.group+'-resume-products');if(!pre.includes(rec.skus.length+' 件商品')||!pre.includes(rec.asin)||!rec.skus.every(s=>pre.includes(s)))throw Error('existing selected product mismatch');rec.status='building';delete rec.error;    rec.stage='manual';
    await mergeBrowser.clickMatching(page,l=>l.includes('radio "手动投放 '),'manual targeting');
    let s=await mergeBrowser.waitSnapshot(page,'keyword-ready-'+spec.group,s=>s.includes('竞价选择')&&s.includes('关键词投放'));
    const section=s.slice(s.indexOf('heading "关键词投放"'));
    const list=section.split('\n').find(l=>l.includes('button "输入列表"'));
    if(!list) throw new Error('Missing keyword input tab');
    await mergeBrowser.checkedTool('click',{pageId:page,uid:list.match(/uid=([^\s]+)/)[1]});
    s=await mergeBrowser.saveSnap(page,'keyword-input-'+spec.group);
    const keywordSection=s.slice(s.indexOf('heading "关键词投放"'));
    const deleteAll=keywordSection.split('\n').find(l=>l.includes('button "删除所有"')&&!l.includes('disabled'));
    if(deleteAll) await mergeBrowser.checkedTool('click',{pageId:page,uid:deleteAll.match(/uid=([^\s]+)/)[1]});
    await mergeBrowser.clickMatching(page,l=>l.includes('button "竞价选择 '),'bid selector');
    await mergeBrowser.clickMatching(page,l=>l.includes('option "自定义竞价 '),'custom bidding');
    const custom=await mergeBrowser.firstUidMatching(page,l=>l.includes('textbox "US$')&&l.includes('针对关键词的竞价，匹配类型'),'custom bid input');
    await mergeBrowser.typeUid(page,custom,String(spec.bid));
    await mergeBrowser.checkedTool('evaluate_script',{pageId:page,function:"()=>{for(const type of ['BROAD','PHRASE']){const e=document.querySelector('input[data-match-type='+type+']');if(!e)throw new Error('Missing match checkbox '+type);if(e.checked)e.click();}const exact=document.querySelector('input[data-match-type=EXACT]');if(exact&&!exact.checked)exact.click();const video=document.querySelector('input[data-takt-id=\"SPVCreativeCard:AutoAssemble:Checkbox\"]');if(video?.checked)video.click();return 'Exact-only';}"});
    const keywordText=spec.keywords.join('\n');
    await mergeBrowser.checkedTool('evaluate_script',{pageId:page,function:"()=>{const e=document.getElementById('kwp:kwp-enter-list-text-input-area');const v="+JSON.stringify(keywordText)+";Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(e,v);e.dispatchEvent(new InputEvent('input',{bubbles:true,data:v}));return e.value;}"});
    await mergeBrowser.clickNamed(page,'button','添加关键词');
    s=await mergeBrowser.waitSnapshot(page,'keywords-added-'+spec.group,s=>s.split('\n').filter(l=>/textbox.*针对关键词.+EXACT匹配类型/.test(l)).length===spec.keywords.length);
    const groupLines=s.split('\n');
    for(let i=0;i<groupLines.length;i++){
      if(groupLines[i].includes('GROUP匹配类型')){
        const remove=groupLines.slice(i+1,i+4).find(l=>/uid=\S+ button\s*$/.test(l));
        if(!remove)throw new Error('Cannot identify default category removal');
        await mergeBrowser.checkedTool('click',{pageId:page,uid:remove.match(/uid=([^\s]+)/)[1]});
        await new Promise(r=>setTimeout(r,350));
      }
    }
    await mergeBrowser.waitSnapshot(page,'exact-only-'+spec.group,s=>s.includes('已添加 '+spec.keywords.length+' 个')&&!s.includes('GROUP匹配类型'));
    rec.stage='campaign-settings';
    await mergeBrowser.typeUid(page,await mergeBrowser.namedUid(page,'textbox','广告组名称'),spec.group+'_'+spec.code+'_EXACT');
    await mergeBrowser.typeUid(page,await mergeBrowser.namedUid(page,'textbox','广告活动名称'),rec.name);
    await mergeBrowser.typeUid(page,await mergeBrowser.namedUid(page,'textbox','enter amount in $'),String(spec.daily));
    await mergeBrowser.clickMatching(page,l=>l.includes('radio "动态竞价 - 仅降低 '),'down-only strategy');
    await mergeBrowser.setEndDate(page,'Tuesday November 10 2026');
    await mergeBrowser.clickNamed(page,'button','选择广告组合');
    await mergeBrowser.clickNamed(page,'option','OLD_PRODUCTS_REACTIVATE_20261103_DAILY');
    s=await mergeBrowser.saveSnap(page,spec.group+'-before-submit');
    const bidLines=s.split('\n').filter(l=>/textbox.*针对关键词.+EXACT匹配类型/.test(l));
    const bidExpected=Number(spec.bid).toFixed(2);
    if(bidLines.length!==spec.keywords.length||bidLines.some(l=>!l.includes('value="'+bidExpected+'"'))) throw new Error('Exact keyword bid mismatch');
    if(!s.includes(spec.skus.length+' 件商品')||!s.includes('value="Nov 10, 2026"')||!s.includes('value="'+Number(spec.daily).toFixed(2)+'"')||!s.includes('OLD_PRODUCTS_REACTIVATE_20261103_DAILY')) throw new Error('Campaign settings mismatch');
    if(!s.split('\n').some(l=>l.includes('radio "动态竞价 - 仅降低')&&l.includes('checked'))) throw new Error('Down-only not checked');
    const badChecked=s.split('\n').filter(l=>/checkbox "(Include 加拿大|Include 墨西哥|提高高流量日子的竞价|应用到此广告活动)/.test(l)&&l.includes('checked'));
    if(badChecked.length) throw new Error('Unexpected expansion: '+badChecked.join(';'));
    rec.stage='submit';rec.sent=true;rec.sent_at=new Date().toISOString();await persist();
    await mergeBrowser.clickNamed(page,'button','启动1个广告活动');
    const receipt=await mergeBrowser.waitSnapshot(page,spec.group+'-launch-success',s=>s.includes('恭喜，您的广告活动已成功启动。'),36);
    const url=mergeBrowser.decode(await mergeBrowser.checkedTool('evaluate_script',{pageId:page,waitForStableDom:false,function:'()=>location.href'}));
    const parsed=new URL(url);rec.campaignId=parsed.searchParams.get('campaign');rec.publicCampaignId=parsed.searchParams.get('publicCampaign');
    rec.status='launched';rec.stage='pending-independent-verification';rec.finished_at=new Date().toISOString();await persist();
  } catch(e) { rec.status=rec.sent?'submission-uncertain':'not-launched';rec.error=String(e);await persist(); }
  return rec;
};}
