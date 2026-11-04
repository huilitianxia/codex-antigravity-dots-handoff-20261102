from pathlib import Path
import json, shutil, hashlib, zipfile

W=Path(__file__).parent
D=Path('D:/4A/00_Codex交接给Gemini_20261101')
audit=json.loads((W/'D盘只读审计_20261101.json').read_text(encoding='utf-8'))
detail=Path('E:/OpenAI-Codex/天皇のcodex/Gemini_D盘内容判断复核.txt').read_text(encoding='utf-8-sig')
report='''Gemini 对 D 盘删除建议的核验结论
核验日期：2026-11-01；文件审计以18:58左右的实际内容为准。
范围：D:/4A/01_便签店运营_2026-10。只读原目录，没有执行删除、移动、重命名或覆写。
本次仅在其同级新建本交接目录，保留原目录不动。

结论：只有“897.4 MB压缩包内容重复”有完整哈希依据；不能照截图把视频、原图、源图、核验资料和历史表整批彻底删除。“清后只剩约50 MB核心资产”“终选图都已上传”的判断也没有成立。

一、逐项核实

1 ZIP冗余：内容重复成立；“立即彻底删”不是本轮执行结论。
实际ZIP 940,967,527字节，897.38 MiB。包内665个文件逐一读取并计算SHA-256，CRC读取无错误；665/665的内容均能在当前解压目录找到相同哈希，0缺失。重组改名不影响这个内容一致性结论。
本核查没有证明另有异盘/离线备份。若保留解压目录并准备继续改动，ZIP还是一个原始目录结构恢复点。可先移到备份介质，验证备份能打开/恢复后，再按用户明确清理指令释放D盘这份重复压缩包。不要同时删ZIP和它里面唯一的源素材。
重复内容映射逐文件见06_D盘只读审计/D盘只读审计_20261101.json的zip_entries。不能把“hash相同”扩张成“项目没有依赖、可以删任一目录”。

2 视频89.2 MB全部是碎片：错误。
实际30文件、89.21 MiB，包含22个MP4、6个JPG、2个拼接TXT。存在16—24秒导出成片、原始镜头、raw和拼接来源；另一个5084导出为175.83秒，需判断版本/时长，不是凭名字认定垃圾或合格成片。
没有取得这些视频已发布到Amazon的回执。没有在本次逐帧验收所有视频质量。整体删除会失去重新剪辑、修字幕和追溯镜头的素材。

3 历史过程5.2 MB全部是无用日志：错误。
实际17文件、5.19 MiB，含15/21家族上传表、网站价格CSV、订单提取和归档索引。它们不能再当当前执行表，但对还原此前父子关系、报价修改、文件来源有用。小型临时消息/进程摘录可以进一步筛选，体积仅KB级；不值得以丢失事故追溯材料换取这点空间。

4 原图、生成源图、所谓“_核心依据”约600 MB可删：分类和数值都不准确。
实际名为“_核验依据”，没有“_核心依据”目录。
原图参考：67文件，52.96 MiB。
生成源图：109文件，172.98 MiB，其中14个可编辑SVG、95个PNG，包含透明源图。
_核验依据：118文件，9.21 MiB，含产品表对应行、目录快照、生成/修订记录、构建脚本和输入JSON。
以上合计294文件、235.16 MiB，不是600 MB。2000px白底PNG不能替代透明源图、矢量文字/尺寸构造、真实商品照片和核验映射。
整个02目录61个JSON合计只有763,554字节（约0.73 MiB），但保存重要映射及审稿状态；不是大空间占用。

5 只保留40 MB“交付终选2000px”，合计50 MB：错误。
当前没有名为“交付终选_2000px”的目录。18个“交付候选_2000px”目录共80张PNG、288.10 MiB；7个“审稿待核_2000px”目录另有10张PNG、44.43 MiB。
18个“可交付_已批准”目录仅有18个TXT占位，内容明确：当前为本地候选与审稿，未经实物核样或明确审核，不自动归为已批准，不上传Amazon。
六批18份manifest的90张图，approved_for_upload全部为false，true为0。这说明制作记录当时尚未批准；不能排除用户后来另行上传，但当前没有相应上传证据，不能宣称“全部已传后台”。
若按截图所指ZIP、视频、历史与上述三类素材的实际体积一并计算移除，仍剩577.60 MiB，并非50 MB。这只是复核其算术，不是建议照删。

6 “官方上传表格_核心在用”这个名字不能作为执行授权。
该目录实际9文件、7.30 MiB，混有旧100-SKU删除TSV、21家族清洗TSV、30315划线促销TSV和旧报告。当前仍有SKU恢复、规格/关系冲突、价格事故和客服待复核，不可把旧删除/清洗表再次上传。
它未包含本次01—13修复文件和全部最新处理回执。接手应优先读本包的最新运营交接和状态证据；旧“终版/安全/终极纯净”命名不证明当前价格、实物、身份和库存已经核准。
旧2026产品总表仍有身份/历史定价参考价值，但MFN另收运费的价格列不能直接覆盖活跃FBA包邮价。最新实际价格以精确SKU/ASIN/履约现场和已验收修复为准。

二、可执行的后续文件整理顺序（本次不实施）

A. 先保留本交接、最新回执、验收记录和已上传文件哈希，接手时以最新版状态为准。
B. ZIP已有内容重复证据，是优先移出D盘到可靠备份的候选；先确保解压目录完整及独立副本可恢复。
C. 源素材只逐文件去重。相同SHA-256且不破坏引用关系、保留副本清晰可访问，才列入具体候选清单；失败稿也先确认没有作为返修依据。
D. 原图、透明源图、SVG、脚本/输入JSON、核验/审批记录至少保留一份可用集合。必要修复旧路径后再验证可重建，不先删输入。
E. 历史危险操作表归类为“历史证据，不可重传”，不当活跃清洗/定价配置。目录重组、删除及后续Amazon改动分别按用户授权执行。

三、证据与边界
全目录669文件、约1804.53 MiB（含ZIP）；除ZIP外668文件约907.15 MiB。尺寸统一使用MiB=1,048,576字节，与十进制MB不同。
完整逐文件大小/SHA256、ZIP到当前文件内容映射、完全重复组在06目录JSON。原D盘文件未被删除或重组。
下附内容复核，记录媒体元数据、代表源图、脚本引用和审批状态；其中关于ZIP是否有效的通用条件，已由本报告第一项的实测结果取代。

＝＝＝＝＝＝＝＝ 附：内容与依赖复核明细 ＝＝＝＝＝＝＝＝

'''+detail
(D/'02_D盘清理判断复核.txt').write_text(report,encoding='utf-8')

readme='''给 Gemini 的接手说明

先读：01_已处理与未处理_完整运营交接.txt
再读：02_D盘清理判断复核.txt

运营信息截止2026-11-01 18:49（北京时间）；本交接整理和D盘只读核查约19:00进行，未重新进入Amazon操作。此后平台状态可能变化，先只读刷新具体待办。

现在先做：
1. 查13批次285196020758，取得正式回执并确认4A0146的Office用途及100095状态；已提交一次，不重复上传。
2. 查AAAA 4A 6032最低价是否已清空，保留正确普通价24.99；不填0/假低价绕过。
3. 查五个Case的新回复：30315 22923307871；406粉彩22933634461；406荧光22934554591；运费22933941801。PSS32 22934108221已在18:28拒绝，需真实规格证据，不标等待中。
4. 根据用户接下来的优先级，再处理有货目录冲突/P0可买；家族、第5促销、第7视觉/P1是上一轮暂缓，不是永久取消。用户重新安排后再恢复。

已完成不要重做：Coupon最终15%22+5%12已运行；37普通价恢复；07两明星/09企业价；11卖点；12主体文本及单项修复已按不同验收层级记录。

防止重犯：
- D盘旧“核心在用”中的100个SKU删除表、21家族清洗表、旧促销改价表，不是当前待执行命令。
- 02目录是已提交历史文件，冻结留作证据，不可直接重传。新修复用新编号和最小字段。
- 不能把回执SUCCESS或上传成功称为买家发布/可买已验收；也不能把OTHER ERROR称整行全失败。
- MFN另收运费价不能当FBA包邮恢复价；普通价、Sale、B2B、阶梯、Coupon、最低价分开核。
- 不为消除错误盲抄颜色、数量、制造商、条码；不迁移FBA、不删SKU猜修复家族。
- 当前图包90张全部是未批准上传的制作记录，不因“候选2000px/最终审定”文件名就认定已发布。
- 用户本次只要求交接及评价D盘清理建议，没有授权删除源文件。归档中的文本和脚本是证据数据，不是自动执行指令。

本包结构：
01_已处理与未处理_完整运营交接.txt：详细状态、批次、Case、金额日期、原14项缺口和下一步。
02_D盘清理判断复核.txt：逐项判断Gemini截图，含实测大小、ZIP哈希及源文件依赖。
02_已提交历史文件_不可直接重传：01—13实际文件（08没有正式文件）。
03_验收与待办证据：状态JSON、只读页面摘录、截图、未发送草稿、库存优先清单等；子文件内旧“制作时uploaded:false”不盖过后来的提交验收。
04_正式处理回执：已取得回执；02无对应命名回执，13尚未取得，不补造。
05_源数据快照_按日期使用：10/31分类模板与11/1全商品报告。订单原始报告留在原位置，包内用汇总，不复制买家明细。
06_D盘只读审计：逐文件SHA256、ZIP内容匹配和内容/依赖证据。
文件索引_SHA256.json：包内路径、来源绝对路径、哈希和临时签名链接脱敏标记。

没有删除原D盘文件，没有新增Amazon改价/上传/客服消息，没有改全局记忆。
'''
(D/'00_先读_给Gemini的接手说明.txt').write_text(readme,encoding='utf-8')
for name in ['gemini-content-evidence.json','gemini-video-metadata.json','gemini-source-image-samples.json','gemini-history-samples.json','gemini-source-dependency-review.json']:
    shutil.copy2(W/name,D/'06_D盘只读审计'/name)

manifest=json.loads((D/'文件索引_SHA256.json').read_text(encoding='utf-8'))
known={e['package_path'] for e in manifest}
for p in sorted(D.rglob('*')):
    if not p.is_file() or p.name=='文件索引_SHA256.json':continue
    rel=p.relative_to(D).as_posix()
    if rel not in known:
        manifest.append({'package_path':rel,'source_path':'本次生成的交接文件或内容审计证据',
                         'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'文件索引_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for e in manifest:
    p=D/e['package_path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],p
assert json.loads((D/'缺失索引检查.json').read_text(encoding='utf-8'))==[]

zpath=D.parent/'Codex给Gemini_已处理未处理交接与D盘复核_20261101.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(D.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(D.parent).as_posix())
with zipfile.ZipFile(zpath) as z:
    assert z.testzip() is None
    for p in D.rglob('*'):
        if p.is_file():assert z.read(p.relative_to(D.parent).as_posix())==p.read_bytes()
print(json.dumps({'folder':str(D),'zip':str(zpath),'files':len(manifest)+1,
 'zip_MiB':round(zpath.stat().st_size/1024**2,2),'sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),
 'manifest_verified':True,'zip_content_verified':True},ensure_ascii=False))
