import json
import re
from pathlib import Path

BASE = Path(__file__).parent


def read(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def money(text):
    found = re.search(r"(?:US)?\$\s*([\d,]+\.\d{2})", text or "")
    return float(found.group(1).replace(",", "")) if found else None


def offer_data(row):
    text = row.get("text", "")
    price_match = re.search(r"(?:^|\n)New\s*\n\s*\$([\d,]+\.\d{2})", text)
    price = float(price_match.group(1).replace(",", "")) if price_match else None
    seller = " ".join((row.get("seller") or "").split())
    shipper = " ".join((row.get("shipper") or "").split())
    own = "4A (USA) LIMITED" in seller
    fulfillment = "FBM" if "4A (USA) LIMITED" in shipper else "FBA" if "Amazon" in shipper else None
    charge = re.search(r"\$([\d,]+\.\d{2})\s+delivery", text)
    freight = float(charge.group(1).replace(",", "")) if charge else None
    conditional_free = "FREE delivery" in text and ("over $35" in text or "Prime" in text)
    if freight is None and "FREE delivery" in text:
        freight = 0.0
    coupon = re.search(r"Coupon price\s*\n\s*\$([\d,]+\.\d{2})", text)
    return {
        "price": price,
        "shipping": freight,
        "total": round(price + freight, 2) if price is not None and freight is not None else None,
        "coupon_price": float(coupon.group(1).replace(",", "")) if coupon else None,
        "conditional_free": conditional_free,
        "shipping_note": "页面有条件免邮（亚马逊订单满$35等）；非Prime单件未结算核验" if conditional_free else "页面免邮" if freight == 0 else "页面按此地址收取运费",
        "fulfillment": fulfillment,
        "own": own,
        "seller": seller,
        "shipper": shipper,
        "reference_price_visible": "List Price:" in text or "Typical price:" in text,
        "text": text,
    }


scope = read("ad-sku-price-mapping-audit-scope.json")
campaigns = [c for c in scope["campaigns"] if c["source"] != "old-retained"]
assert len(campaigns) == 27
skus = sorted({s for c in campaigns for s in c["skus"]})
assert len(skus) == 37
inventory = read("all-ad-inventory-current.json")
inv_by_asin = {r["asin"]: r for r in inventory["records"]}
latest_5082 = read("5082-independent-current-backend.json")
inv_by_asin["B07F2BHFJH"] = {"asin": "B07F2BHFJH", "at": latest_5082["at"], "rows": latest_5082["rows"]}
public = {r["requested_asin"]: r for r in read("all-ad-public-pack-current.json")["records"]}
aod = {r["requested_asin"]: r for r in read("today-ads-all-own-offers-current.json")["records"]}
masters = read("excel-final-2026-3-current-rows.json")
master_rows = masters["rows"]
fixed_promos = {}
for r in read("30315-promo-other-SKUs-before.json"):
    sku_match = re.search(r"SKU[:：]\s*(.+)", r["cells"].get("name", ""))
    if sku_match:
        fixed_promos[sku_match.group(1).strip()] = money(r["cells"].get("4"))
# The live sale price now takes precedence for 30315; this old fixed promotion is being removed.
fixed_promos.pop("4A GM30315", None)
freight_classes = {"N": 4.99, "B": 9.99, "H": 11.99, "2H": 22.99}
model_overrides = {"B0F2TKL2P5": 57, "B07FK7PBHJ": 114}

details = []
products = []
for campaign in campaigns:
    asin = campaign["asin"]
    assert asin in inv_by_asin and asin in aod and asin in public, asin
    candidates = [r for r in master_rows if asin in str(r["values"][2] or "") or asin in str(r["values"][4] or "")]
    basis = "ASIN与终表直接匹配"
    if not candidates and asin in model_overrides:
        candidates = [r for r in master_rows if r["row"] == model_overrides[asin]]
        basis = "按型号及包装规格匹配；终表ASIN空缺" if asin == "B0F2TKL2P5" else "按NYNRx2型号及2卷+2补充卷匹配；终表ASIN不同"
    assert len(candidates) <= 1, (asin, candidates)
    master = candidates[0] if candidates else None
    mv = master["values"] if master else None
    excel_sale = float(mv[12]) if mv else None
    excel_freight = freight_classes.get(str(mv[7]).strip()) if mv else None
    offers = [offer_data(o) for o in aod[asin].get("offers", [])]
    own_offers = [o for o in offers if o["own"] and o["price"] is not None]
    item = {
        "asin": asin,
        "group": campaign["group"],
        "campaign_id": campaign["campaign"],
        "advertised_skus": campaign["skus"],
        "name": mv[0] if mv else "4A 303x18-Y（黄色18本，SKU 4A 020）",
        "master_row": master["row"] if master else None,
        "master_basis": basis if master else "终表未找到黄色18本的精确型号/ASIN；不能套用混色或荧光18本价格",
        "excel_list": float(mv[11]) if mv else None,
        "excel_sale": excel_sale,
        "excel_shipping_class": mv[7] if mv else None,
        "excel_shipping": excel_freight,
        "excel_fob": float(mv[9]) if mv else None,
        "excel_weight_lb": mv[14] if mv else None,
        "title": public[asin].get("title"),
        "main_seller": offers[0]["seller"] if offers else None,
        "main_price": offers[0]["price"] if offers else None,
        "main_fulfillment": offers[0]["fulfillment"] if offers else None,
        "own_offers": own_offers,
        "rows": [],
        "findings": [],
    }
    for sku in campaign["skus"]:
        matches = [r for r in inv_by_asin[asin]["rows"] if r["sku"] == sku]
        assert len(matches) == 1, (sku, len(matches))
        source = matches[0]
        text = source["text"]
        fbm = "配送模板" in text or "卖家自配送" in text
        fulfillment = "FBM" if fbm else "FBA"
        controls = source["controls"]
        regular = float(controls[1 if fbm else 0]["value"].replace(",", ""))
        floor_raw = controls[2 if fbm else 1]["value"]
        floor = float(floor_raw.replace(",", "")) if floor_raw else None
        freight_match = re.search(r"运费\s*\n\+ \$([\d,.]+)", text)
        freight = float(freight_match.group(1).replace(",", "")) if freight_match else None
        sale_match = re.search(r"促销价格\s*\n\$([\d,.]+)", text)
        sale = float(sale_match.group(1).replace(",", "")) if sale_match else None
        promo = fixed_promos.get(sku)
        # Live Seller Central labels the currently active sale price explicitly.
        # 5082 currently demonstrates that an old sale can override a lower base price.
        effective = sale if sale is not None else regular
        if promo is not None:
            effective = min(effective, promo)
        eligible = [o for o in own_offers if o["fulfillment"] == fulfillment]
        same_price = [o for o in eligible if abs(o["price"] - effective) < 0.005]
        selected = same_price[0] if len(same_price) == 1 else min(eligible, key=lambda o: abs(o["price"] - effective)) if eligible else None
        backend_total = round(effective + freight, 2) if freight is not None else None
        template = re.search(r"配送模板\s*\n([^\n]+)", text)
        notes = []
        if sale is not None and sale > regular + 0.005:
            notes.append(f"旧促销价{sale:.2f}高于常规价{regular:.2f}；前台仍按促销价显示")
        if selected is None:
            status = "前台未匹配到本配送方式报价"
        elif abs(selected["price"] - effective) >= 0.005:
            status = "后台与前台商品价不一致"
            notes.append(f"后台有效价{effective:.2f}，前台{selected['price']:.2f}")
        elif freight is not None and selected["shipping"] is not None and abs(freight - selected["shipping"]) >= 0.005:
            status = "后台与前台运费不一致"
        else:
            status = "后台与前台一致"
        if excel_sale is None:
            notes.append("终表缺少精确价格对应行")
        elif selected and selected["price"] > excel_sale + 0.005:
            notes.append(f"商品价较终表折后价高{selected['price']-excel_sale:.2f}")
        if fbm and freight is not None and excel_freight is not None and abs(freight - excel_freight) > 0.005:
            notes.append(f"运费较终表档位{'高' if freight>excel_freight else '低'}{abs(freight-excel_freight):.2f}")
        if promo is not None:
            notes.append("固定价格促销已纳入后台有效价")
        if selected and selected["coupon_price"] is not None:
            notes.append("另有领券价，需满足优惠券条件")
        row = {
            "asin": asin, "sku": sku, "fulfillment": fulfillment,
            "name": item["name"], "master_row": item["master_row"],
            "excel_sale": excel_sale, "excel_shipping": excel_freight,
            "excel_shipping_class": item["excel_shipping_class"],
            "backend_regular": regular, "backend_sale": sale, "backend_fixed_promo": promo,
            "backend_effective": effective, "backend_shipping": freight, "backend_total": backend_total,
            "minimum": floor, "shipping_template": template.group(1) if template else None,
            "public_price": selected["price"] if selected else None,
            "public_shipping": selected["shipping"] if selected else None,
            "public_total": selected["total"] if selected else None,
            "public_coupon": selected["coupon_price"] if selected else None,
            "public_shipping_note": selected["shipping_note"] if selected else "未核验",
            "status": status, "notes": "；".join(notes),
            "source_at": inv_by_asin[asin]["at"], "public_at": aod[asin]["at"],
        }
        details.append(row)
        item["rows"].append(row)
    fba = [o for o in own_offers if o["fulfillment"] == "FBA"]
    fbm = [o for o in own_offers if o["fulfillment"] == "FBM"]
    item["own_fba_lowest"] = min((o["price"] for o in fba), default=None)
    item["own_fbm_lowest"] = min((o["price"] for o in fbm), default=None)
    item["fbm_item_extra_over_fba"] = None
    if fba and fbm:
        advertised_fbm_prices = [r["public_price"] for r in item["rows"] if r["fulfillment"] == "FBM" and r["public_price"] is not None]
        if advertised_fbm_prices:
            item["fbm_item_extra_over_fba"] = round(max(advertised_fbm_prices) - item["own_fba_lowest"], 2)
            if item["fbm_item_extra_over_fba"] > 0.005:
                item["findings"].append(f"广告FBM商品价高于同页自家FBA {item['fbm_item_extra_over_fba']:.2f}，运费另加")
    if any(r["status"] != "后台与前台一致" for r in item["rows"]):
        item["findings"].append("后台与前台报价差异需再核验")
    if master is None:
        item["findings"].append("终表缺少黄色18本精确行")
    products.append(item)

assert len(details) == 37 and len(products) == 27
result = {
    "asof": max(r["public_at"] for r in details),
    "source_workbook": masters["source"],
    "source_sheet": "Sheet1",
    "address": "New York 10001",
    "counts": {"campaigns_today": 27, "asins_today": 27, "skus_today": 37,
               "direct_excel_asin_matches": sum(p["master_basis"] == "ASIN与终表直接匹配" for p in products),
               "model_matches": sum(p["asin"] in model_overrides for p in products),
               "missing_exact_master": sum(p["master_row"] is None for p in products),
               "price_shipping_matches": sum(r["status"] == "后台与前台一致" for r in details)},
    "products": products, "sku_details": details,
    "limits": ["FBA页面免邮有Prime或满$35等条件，单件非Prime运费没有进入结算核验。",
               "优惠券价格另列，未当作所有买家自动享有的价格。",
               "前台不显示SKU；按相同ASIN、4A卖家、配送方式和价格对应，无法仅凭同页主报价认定广告SKU价格。",
               "Excel物流档位是定价参考，不是实际出库运单成本。",
               "R009黄色24本误选整箱广告继续暂停；不纳入当前27款在投范围。"],
}
(BASE / "today-ad-price-threeway-analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result["counts"], ensure_ascii=False))
for p in products:
    if p["findings"]:
        print(p["name"], p["asin"], p["findings"])
for r in details:
    if r["status"] != "后台与前台一致":
        print("MISMATCH", r["sku"], r["backend_effective"], r["public_price"], r["backend_shipping"], r["public_shipping"])
