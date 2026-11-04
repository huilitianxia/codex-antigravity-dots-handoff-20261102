export async function auditPlans(b, page, plans) {
  b.vcAudit.status = 'running';
  b.vcAudit.stopRequested = false;
  const done = new Set(b.vcAudit.records.filter(r => !r.error).map(r => r.asin));
  for (const p of plans) {
    if (done.has(p.asin)) continue;
    if (b.vcAudit.stopRequested) break;
    b.vcAudit.current = p.asin;
    try {
      await b.typeUid(page, await b.namedUid(page, 'searchbox', '按商品名称、ASIN 或 SKU 搜索'), p.asin, 'Enter');
      const s = await b.waitSnapshot(page, 'vc-audit-' + p.asin,
        s => s.includes('StaticText "' + p.target_sku + '"') && s.includes('StaticText "' + p.asin + '"'), 16);
      const lines = s.split('\n');
      const at = lines.findIndex(l => l.includes('StaticText "' + p.target_sku + '"'));
      const chunk = lines.slice(Math.max(0, at - 20), at + 10).join('\n');
      const rating = chunk.match(/image "([\d.]+) out of 5 stars"/);
      b.vcAudit.records.push({asin:p.asin, sku:p.target_sku, rank:p.history_rank, action:p.action,
        rating:rating ? Number(rating[1]) : null,
        addable:/button "添加"(?!.*disabled)/.test(lines.slice(at + 1, at + 7).join('\n')),
        chunk, at:new Date().toISOString()});
    } catch (e) {
      b.vcAudit.records.push({asin:p.asin, sku:p.target_sku, error:String(e)});
      if (/page.*not|NoPage|connection|Invalid argument/i.test(String(e))) throw e;
    }
    await b.fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/full-coverage/vc-live-product-audit.json', JSON.stringify(b.vcAudit, null, 2));
  }
  b.vcAudit.status = b.vcAudit.stopRequested ? 'stopped' : 'complete';
  await b.fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/full-coverage/vc-live-product-audit.json', JSON.stringify(b.vcAudit, null, 2));
}
