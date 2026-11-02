from pathlib import Path
src=Path('E:/Desktop/待上架_新图文素材库_第三批/_核验依据/build_delivery.cjs').read_text(encoding='utf-8-sig')
src=src.replace('待上架_新图文素材库_第三批','待上架_新图文素材库_第四批')
a=src.index('const specs=[');b=src.index('function bbox(')
src=src[:a]+"const meta=read(ROOT+'/_核验依据/delivery_data.json');\nconst {specs,titles,checks}=meta;const pending=new Set(meta.pending);\nconst {makeSvg,svgMetrics}=require('./dimension_art.cjs');\n"+src[b:]
src=src.replace("isSvg=id==='5088NL_02'||id==='PSS91_03'","isSvg=n===2")
a=src.index('if(isSvg){source=');b=src.index('else{const m=',a)
src=src[:a]+"if(isSvg){source=dir+'/生成源图/'+id+'_exact.svg';fs.writeFileSync(source,makeSvg(s.id),'utf8');await sharp(Buffer.from(fs.readFileSync(source))).removeAlpha().png().toFile(out);sourceSize=[2000,2000];method='原生2000×2000 SVG规格图；纸面按精确比例绘制后渲染PNG';technical=svgMetrics(s.id);}\n"+src[b:]
src=src.replace("catalog_correction:s.correction,reference_files","catalog_correction:s.correction,workbook_source:s.workbook_source,reference_files")
src=src.replace("occupancy_pass:occupancy>=85","occupancy_pass:occupancy>=85&&occupancy<=90.1")
src=src.replace('第三批','第四批').replace('BATCH 03','BATCH 04')
src=src.replace('40609x2 / 5088-N-L / PSS 9-1 NYNRx2','4012 / 303M-PNx12 / 124418')
src=src.replace('<a href="#40609">40609</a><a href="#5088NL">5088</a><a href="#PSS91">PSS 9-1</a>','<a href="#4012">4012</a><a href="#303M">303M</a><a href="#124418">124418</a>')
old='13张交付候选＋2张PSS待核稿（裁切动作、换卷步骤）。候选仍需核对实物纸厚、颜色、胶位和场景比例。未批准自动上架。<br>PSS五张图对应带分配器套装B07QWKWWP2，不能直接用于四卷纯替换装B07QVKPZXX。原图、生成源图和返修版本均保留。'
new='13张交付候选＋2张待核稿：4012内容物主图尚缺PP盒实拍；124418移除性能尚待实物确认。候选仍需核对纸厚、颜色、胶位和场景比例。未批准自动上架。<br>303M是每本内部循环换色；124418是纸质页签，不是601透明薄膜。4012尺寸取C盘总表，内容物规格取原包装。'
src=src.replace(old,new).replace('两张尺寸图为原生SVG','三张规格图为原生SVG')
src=src.replace('已查看13张生成图及2张40609返修图；最终尺寸图与总览另行检查。','已查看12张摄影图及5张返修图；最终三张SVG规格图与总览另行检查。')
Path('E:/Desktop/待上架_新图文素材库_第四批/_核验依据/build_delivery.cjs').write_text(src,encoding='utf-8')
print('Prepared self-contained batch4 builder')
