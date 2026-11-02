from pathlib import Path
from shutil import copy2
from hashlib import sha256
import json, zipfile, re

W=Path(__file__).parent
DEST=Path('D:/4A/00_Codex交接给Gemini_20261101')
DEST.mkdir(exist_ok=True)
manifest=[]
def put(src, sub, name=None, redact=False):
    src=Path(src)
    if not src.is_file():
        raise FileNotFoundError(src)
    target=DEST/sub/(name or src.name)
    target.parent.mkdir(parents=True,exist_ok=True)
    if redact:
        text=src.read_text(encoding='utf-8-sig')
        text=re.sub(r'(?m)^.*X-Amz-[^\n]*\n?', '[临时附件签名链接已从交接副本移除；保留附件名称和原始本地证据位置]\n', text)
        target.write_text(text,encoding='utf-8')
    else:
        copy2(src,target)
    manifest.append({'package_path':target.relative_to(DEST).as_posix(),'source_path':str(src),
        'bytes':target.stat().st_size,'sha256':sha256(target.read_bytes()).hexdigest(),
        'source_sha256':sha256(src.read_bytes()).hexdigest(),'temporary_signed_urls_redacted':redact})

ops=W/'Gemini_运营交接草稿_20261101.txt'
text=ops.read_text(encoding='utf-8-sig').replace('，已在线只改亮点为“Sign Here and Note flags; transparent, writable color tabs for marking documents.”',
    '，已在线只改亮点为“Sign Here and Note flags; transparent, writable color tabs for marking documents”')
text += '\n\n附录C：本交接包中的文件位置\n本包02为已提交历史文件，不可直接重传；03为验收与待办证据；04为已取得处理回执；05为带日期的源数据快照；06为D盘只读审计。本文未复制的证据仍在前文给出的E盘工作目录，可按清单精确读取。\nD盘旧“核心在用”不包含当前01—13修复文件及全部最新回执，不能替代本交接。详细D盘判断见根目录02_D盘清理判断复核.txt。\n'
(DEST/'01_已处理与未处理_完整运营交接.txt').write_text(text,encoding='utf-8')

out=Path('E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes')
for p in sorted(out.glob('*.xlsm')):
    put(p,'02_已提交历史文件_不可直接重传')

names='''本轮收尾_20261101.txt
restart-37-price-reconciliation.json
v1-price-incident-audit.json
root-price-recovery-log.json
agent2-price-recovery-log.json
v4-price-live-acceptance.json
v4-approved-price-rows.json
05-final-minimum-acceptance.json
05-min-delete-diagnosis.txt
05-min-delete-operation-log.json
05-6032-late-readback.txt
07-live-pricing-acceptance.json
09-live-business-acceptance.json
09-073-late-readback.txt
09-073-late-tiers-readback.txt
10-live-pricing-acceptance.json
10-processing-receipt-audit.json
11-processing-receipt-audit.json
11-live-bullet-acceptance.json
12-final-processing-summary.json
12-processing-receipt-audit.json
12-package-verification.json
12-main-independent-check.json
12-one-highlight-saved.txt
12-one-highlight-saved.png
12-language-124-before.txt
12-language-484-before.txt
12-language-500-before.txt
13-package-verification.json
13-upload-submitted.txt
13-upload-submitted.png
coupon15-final22-product-acceptance.json
coupon5-final12-product-acceptance.json
coupon5-final12-live-acceptance.json
coupon-expanded-execution-ledger.json
coupon-expansion-77-complete-readonly-audit.json
coupon77-demand-and-aged-fee-recheck.json
coupon77-demand-recheck.json
coupon-fullscan-parsed.json
fba-live-fees.json
samepage-stocked-fba-execution.json
samepage-live-decisions.txt
merge12-concrete-review.txt
merge13-to12-reviewed-groups.json
merge-three-cases-send-verification.json
merge-next3-support-drafts-unsent.txt
merge-additional6-support-drafts-unsent.txt
merge-pss32-reply-1828.txt
30315-support-send-verification.json
mfn-support-send-verification.json
mfn-p0-two-sku-comparison.json
mfn-p0-support-ready.txt
mfn8-shipping-diagnosis.json
nonfamily-stream2-6-remaining-gaps.txt
residual62-closeout.json
residual-closeout-brief.txt
family08-safe-sequence.txt
family08-support-request-draft.txt
family08-attach-fields-prepared.json
1801-orders-live-summary.json
bs1801-sales-and-switch-review.json
bs1801-refill-bundle-entry.png
bundle-bs1801-acceptance.json
closeout-case-lobby.png
closeout-case-lobby.txt
'''.splitlines()
missing=[]
for name in names:
    p=W/name
    if not p.exists():
        missing.append(name)
        continue
    put(p,'03_验收与待办证据',redact=p.suffix=='.txt')
for p in (W/'merge-support-packages').rglob('*.txt'):
    put(p,'03_验收与待办证据/合并补证材料/'+p.parent.name)

downloads=Path('D:/下载文件')
for prefix in ['01-price','03-catalog','05-remove','06-three','07-star','09-073','10-four','11-remaining','12-catalog']:
    for p in downloads.glob(prefix+'*processing-summary.xlsm'):
        put(p,'04_正式处理回执')
put(downloads/'04-reviewed-nonincident-fixes-processing-summary (2).xlsm','04_正式处理回执')
for name in ['分类商品报告_10-31-2026.xlsm','所有商品报告_11-01-2026.txt']:
    put(downloads/name,'05_源数据快照_按日期使用')
put(W/'D盘只读审计_20261101.json','06_D盘只读审计')
put(W/'audit_d_handoff.py','06_D盘只读审计')

(DEST/'文件索引_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(DEST/'缺失索引检查.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'folder':str(DEST),'copied_files':len(manifest),'missing_requested_evidence':missing,
                  'MiB':round(sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file())/1024**2,2)},ensure_ascii=False))
