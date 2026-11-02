import fs from "node:fs/promises";

function colToIdx(ref) {
  const letters = ref.replace(/\d+/g, "");
  let n = 0;
  for (let i = 0; i < letters.length; i++) {
    n = n * 26 + (letters.charCodeAt(i) - 64);
  }
  return n - 1;
}

function parseSheetJson(data) {
  const sheet = data.sheets[0];
  const rows = sheet.rows;
  if (!rows || !rows.length) return [];
  const headerCells = rows[0].cells;
  const headers = [];
  for (const c of headerCells) {
    headers[colToIdx(c.ref)] = c.value;
  }
  const result = [];
  for (let i = 1; i < rows.length; i++) {
    const obj = {};
    for (const c of rows[i].cells) {
      const h = headers[colToIdx(c.ref)];
      if (h) obj[h] = c.value;
    }
    if (obj.ASIN) result.push(obj);
  }
  return result;
}

async function run() {
  const scratch = "C:/Users/24243/.gemini/antigravity/brain/dbbf7b60-af99-4ab1-b84a-018cb729792d/scratch";
  const byAsin = new Map();
  for (const name of ["ss_217940.json", "ss_863796.json", "ss_863876.json"]) {
    const raw = JSON.parse(await fs.readFile(`${scratch}/${name}`, "utf8"));
    const rows = parseSheetJson(raw);
    for (const r of rows) {
      r._source = name;
      const prev = byAsin.get(r.ASIN);
      if (!prev || (r["评分"] != null && r["评分"] !== "")) {
        byAsin.set(r.ASIN, r);
      }
    }
  }

  const allSS = [...byAsin.values()];
  const toNum = v => {
    if (v == null || v === "") return 0;
    const n = Number(String(v).replace(/[$,%]/g, ""));
    return isNaN(n) ? 0 : n;
  };

  const withSales = allSS.filter(r => toNum(r["月销量"]) > 0).sort((a, b) => toNum(b["月销量"]) - toNum(a["月销量"]));
  const withSubSales = allSS.filter(r => toNum(r["子体销量"]) > 0).sort((a, b) => toNum(b["子体销量"]) - toNum(a["子体销量"]));

  const byParent = new Map();
  for (const r of allSS) {
    const p = String(r["父ASIN"] || r.ASIN).trim();
    if (!byParent.has(p) || toNum(r["月销量"]) > toNum(byParent.get(p)["月销量"])) {
      byParent.set(p, r);
    }
  }

  const parentMonthlyUnits = [...byParent.values()].reduce((s, r) => s + toNum(r["月销量"]), 0);
  const parentMonthlyRev = [...byParent.values()].reduce((s, r) => s + toNum(r["月销售额($)"]), 0);
  const subMonthlyUnits = allSS.reduce((s, r) => s + toNum(r["子体销量"]), 0);
  const subMonthlyRev = allSS.reduce((s, r) => s + toNum(r["子体销售额($)"]), 0);

  const countBy = (arr, key) => {
    const m = {};
    for (const r of arr) {
      const k = String(r[key] ?? "(空)").trim() || "(空)";
      m[k] = (m[k] || 0) + 1;
    }
    return m;
  };

  const lqsVals = allSS.map(r => toNum(r["LQS"])).filter(n => n > 0);
  const avgLqs = lqsVals.reduce((a, b) => a + b, 0) / (lqsVals.length || 1);

  const ratings = allSS.map(r => toNum(r["评分"])).filter(n => n > 0);
  const ratingBuckets = {
    "4.5-5.0": ratings.filter(x => x >= 4.5).length,
    "4.0-4.4": ratings.filter(x => x >= 4.0 && x < 4.5).length,
    "3.0-3.9": ratings.filter(x => x >= 3.0 && x < 4.0).length,
    "<3.0": ratings.filter(x => x < 3.0).length,
    "无评分": allSS.length - ratings.length
  };

  // Analyze SC report 09-03-2026
  const scRaw = (await fs.readFile("D:/下载文件/所有商品报告_09-03-2026.txt", "utf8")).replace(/^\uFEFF/, "");
  const scLines = scRaw.split(/\r?\n/).filter(Boolean);
  const scHeaders = scLines[0].split("\t");
  const scRows = scLines.slice(1).map(l => {
    const cols = l.split("\t");
    return Object.fromEntries(scHeaders.map((h, i) => [h, cols[i] ?? ""]));
  });

  const scStatusChannel = {};
  for (const r of scRows) {
    const k = `${r.status} | ${r["fulfillment-channel"]}`;
    scStatusChannel[k] = (scStatusChannel[k] || 0) + 1;
  }

  const scByAsin = {};
  for (const r of scRows) {
    if (!r.asin1) continue;
    if (!scByAsin[r.asin1]) scByAsin[r.asin1] = [];
    scByAsin[r.asin1].push(r);
  }
  const multiOfferAsins = Object.entries(scByAsin).filter(([, list]) => list.length > 1);
  const multiOffer3Plus = Object.entries(scByAsin).filter(([, list]) => list.length >= 3);
  const fbaActiveAndFbmActiveSameAsin = Object.entries(scByAsin).filter(([, list]) =>
    list.some(x => x.status === "Active" && x["fulfillment-channel"] === "AMAZON_NA") &&
    list.some(x => x.status === "Active" && x["fulfillment-channel"] === "DEFAULT")
  );
  const onlyFbmActiveAsins = Object.entries(scByAsin).filter(([, list]) =>
    !list.some(x => x.status === "Active" && x["fulfillment-channel"] === "AMAZON_NA") &&
    list.some(x => x.status === "Active" && x["fulfillment-channel"] === "DEFAULT")
  );
  const onlyFbaActiveAsins = Object.entries(scByAsin).filter(([, list]) =>
    list.some(x => x.status === "Active" && x["fulfillment-channel"] === "AMAZON_NA") &&
    !list.some(x => x.status === "Active" && x["fulfillment-channel"] === "DEFAULT")
  );
  const allInactiveAsins = Object.entries(scByAsin).filter(([, list]) =>
    !list.some(x => x.status === "Active")
  );

  console.log(JSON.stringify({
    sellerSprite: {
      uniqueAsins: allSS.length,
      uniqueParents: byParent.size,
      asinsWithMonthlySalesGT0: withSales.length,
      asinsWithSubSalesGT0: withSubSales.length,
      parentLevelTotalMonthlyUnits: parentMonthlyUnits,
      parentLevelTotalMonthlyRev: parentMonthlyRev,
      subLevelTotalMonthlyUnits: subMonthlyUnits,
      subLevelTotalMonthlyRev: subMonthlyRev,
      avgLqs: Number(avgLqs.toFixed(2)),
      lqsUnder60: lqsVals.filter(x => x < 60).length,
      lqs60To75: lqsVals.filter(x => x >= 60 && x < 75).length,
      lqs75Plus: lqsVals.filter(x => x >= 75).length,
      ratingBuckets,
      fulfillment: countBy(allSS, "配送方式"),
      buyBoxType: countBy(allSS, "BuyBox类型"),
      buyBoxSeller: countBy(allSS, "BuyBox卖家"),
      hasVideo: countBy(allSS, "视频介绍"),
      hasAPlus: countBy(allSS, "A+页面"),
      hasBrandStory: countBy(allSS, "品牌故事"),
      hasSPAds: countBy(allSS, "SP广告"),
      hasBrandAds: countBy(allSS, "品牌广告"),
      hasCoupon: countBy(allSS, "Coupon"),
      top20ParentsBySales: [...byParent.values()]
        .filter(r => toNum(r["月销量"]) > 0)
        .sort((a, b) => toNum(b["月销量"]) - toNum(a["月销量"]))
        .slice(0, 20)
        .map(r => ({
          asin: r.ASIN,
          parent: r["父ASIN"],
          sku: r.SKU,
          title: String(r["商品标题"] || "").slice(0, 55),
          monthlySales: toNum(r["月销量"]),
          subSales: toNum(r["子体销量"]),
          monthlyRev: toNum(r["月销售额($)"]),
          price: toNum(r["价格($)"]),
          rating: toNum(r["评分"]),
          reviews: toNum(r["评分数"]),
          fulfillment: r["配送方式"],
          buyBox: r["BuyBox卖家"],
          spAds: r["SP广告"],
          video: r["视频介绍"],
          aplus: r["A+页面"],
          lqs: toNum(r["LQS"])
        }))
    },
    scReport0903: {
      totalRows: scRows.length,
      uniqueAsins: Object.keys(scByAsin).length,
      statusChannelBreakdown: scStatusChannel,
      onlyFbaActiveAsins: onlyFbaActiveAsins.length,
      onlyFbmActiveAsins: onlyFbmActiveAsins.length,
      bothFbaAndFbmActiveAsins: fbaActiveAndFbmActiveSameAsin.length,
      allInactiveOrIncompleteAsins: allInactiveAsins.length,
      asinsWithMultipleSkus: multiOfferAsins.length,
      asinsWith3PlusSkus: multiOffer3Plus.length,
      topDuplicatedAsins: multiOfferAsins.sort((a, b) => b[1].length - a[1].length).slice(0, 10).map(([a, l]) => ({
        asin: a,
        count: l.length,
        skus: l.map(x => `${x["seller-sku"]}(${x.status}/${x["fulfillment-channel"] === "AMAZON_NA" ? "FBA" : "FBM"})`)
      }))
    }
  }, null, 2));
}
run();
