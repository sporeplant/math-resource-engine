const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { pathToFileURL } = require("url");
const pptxgen = require("../.pptx-build/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT_DIR = path.join(ROOT, "输出");
const QA_DIR = path.join(OUT_DIR, "typora_like_first3");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PPTX_OUT = path.join(OUT_DIR, "22.4_频数分布与直方图_前三页截图版.pptx");

fs.mkdirSync(QA_DIR, { recursive: true });

const dataRows = [
  [155, 198, 175, 158, 158, 124, 154, 148, 169, 120],
  [190, 133, 160, 215, 172, 126, 145, 130, 131, 118],
  [108, 157, 145, 165, 122, 106, 165, 150, 136, 144],
  [140, 159, 110, 134, 170, 168, 162, 170, 205, 186],
  [182, 156, 138, 187, 100, 142, 168, 218, 175, 146],
];

const css = `
*{box-sizing:border-box}
body{margin:0;background:#e5e7eb;font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;color:#1f2937}
.slide{width:1600px;height:900px;background:#fff;margin:0;position:relative;overflow:hidden;padding:70px 92px}
.slide:before{content:"";position:absolute;left:0;top:0;width:100%;height:20px;background:#0f766e}
.titlePage{background:#111827;color:#fff}
.titlePage:before{width:26px;height:100%;background:#14b8a6}
.lesson{position:absolute;right:88px;bottom:54px;color:#94a3b8;font-size:20px}
.source{position:absolute;left:78px;bottom:54px;color:#64748b;font-size:16px}
.titlePage .source{color:#94a3b8}
h1{font-size:58px;line-height:1.12;margin:0 0 24px;font-weight:800;letter-spacing:0}
h2{font-size:44px;line-height:1.16;margin:0 0 34px;font-weight:800;letter-spacing:0}
.eyebrow{font-size:36px;color:#f59e0b;font-weight:800;margin-bottom:24px}
.sub{font-size:24px;color:#cbd5e1;margin-top:8px}
.keywords{font-size:28px;color:#e5e7eb;margin-top:54px}
.flow{display:flex;gap:16px;align-items:center;margin-top:70px}
.flow .box{min-width:142px;height:58px;border-radius:6px;background:#fff;color:#111827;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800}
.flow .box.hot{background:#f59e0b;color:#fff}
.flow .arrow{color:#f59e0b;font-size:32px;font-weight:800}
.hist{position:absolute;right:150px;top:190px;width:440px;height:380px;border-left:3px solid #cbd5e1;border-bottom:3px solid #cbd5e1}
.hist .bar{position:absolute;bottom:0;background:#14b8a6;width:58px}
.hist .bar.hot{background:#f59e0b}
.hist .lab{position:absolute;bottom:-34px;width:70px;text-align:center;color:#94a3b8;font-size:15px}
.goal{display:grid;grid-template-columns:60px 1fr;gap:20px;align-items:center;margin:34px 0;width:850px}
.num{width:42px;height:42px;border-radius:50%;background:#0f766e;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800}
.goal:nth-of-type(5) .num{background:#f59e0b}
.goalText{font-size:24px;font-weight:700}
.miniFlow{position:absolute;right:130px;top:330px;display:flex;align-items:center;gap:14px}
.miniFlow .box{width:120px;height:62px;background:#fff;border:1px solid #cbd5e1;border-radius:6px;box-shadow:0 4px 12px rgba(15,23,42,.08);display:flex;align-items:center;justify-content:center;font-weight:800}
.miniFlow .box:last-child{background:#0f766e;color:#fff}
.miniFlow .arrow{color:#f59e0b;font-size:28px;font-weight:800}
.lead{font-size:25px;font-weight:800;margin-bottom:34px;width:840px}
table{border-collapse:collapse}
.dataTable{width:850px;font-size:19px;text-align:center}
.dataTable td{border:1px solid #cbd5e1;padding:16px 0;background:#f8fafc}
.dataTable tr:nth-child(even) td{background:#fff}
.sideCard{position:absolute;right:145px;width:405px;background:#fff;border:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(15,23,42,.08);padding:24px 28px}
.sideCard:before{content:"";position:absolute;left:0;top:0;width:8px;height:100%;background:#f59e0b}
.sideCard.teal:before{background:#0f766e}
.cardTitle{font-size:20px;font-weight:800;color:#f59e0b;margin-bottom:14px}
.sideCard.teal .cardTitle{color:#0f766e}
.cardText{font-size:19px;line-height:1.55}
`;

function wrap(body, idx) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${body}</body></html>`;
}

function titleHtml() {
  const bars = [90, 150, 250, 330, 250, 160, 90].map((h, i) => {
    const left = 35 + i * 58;
    return `<div class="bar ${i === 3 ? "hot" : ""}" style="left:${left}px;height:${h}px"></div><div class="lab" style="left:${left - 6}px">${["100","120","140","160","180","200","220"][i]}</div>`;
  }).join("");
  return wrap(`<section class="slide titlePage">
    <div class="eyebrow">22.4</div>
    <h1>频数分布与直方图</h1>
    <div class="sub">第二十二章 数据的收集、整理与描述</div>
    <div class="keywords">频数分布表 · 频数分布直方图 · 数据分布</div>
    <div class="flow"><div class="box">分组</div><div class="arrow">›</div><div class="box">制表</div><div class="arrow">›</div><div class="box">画图</div><div class="arrow">›</div><div class="box hot">读图应用</div></div>
    <div class="hist">${bars}</div>
    <div class="source">source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4_courseware</div>
  </section>`, 1);
}

function goalsHtml() {
  return wrap(`<section class="slide">
    <h2>🎯 本课目标</h2>
    <div class="goal"><div class="num">1</div><div class="goalText">从连续数据中确定最大值、最小值和极差</div></div>
    <div class="goal"><div class="num">2</div><div class="goalText">按组距分组，列出频数和频率分布表</div></div>
    <div class="goal"><div class="num">3</div><div class="goalText">画出频数分布直方图，并读出集中范围</div></div>
    <div class="goal"><div class="num">4</div><div class="goalText">用直方图信息评价实际方案</div></div>
    <div class="miniFlow"><div class="box">分组</div><div class="arrow">›</div><div class="box">频数表</div><div class="arrow">›</div><div class="box">直方图</div><div class="arrow">›</div><div class="box">方案评价</div></div>
    <div class="lesson">22.4 频数分布与直方图</div>
  </section>`, 2);
}

function dataHtml() {
  const rows = dataRows.map((r) => `<tr>${r.map((v) => `<td>${v}</td>`).join("")}</tr>`).join("");
  return wrap(`<section class="slide">
    <h2>📉 阶梯电价中 50 户用电量</h2>
    <div class="lead">为了制定合理的阶梯电价，需要观察居民全年月平均用电量的分布。</div>
    <table class="dataTable">${rows}</table>
    <div class="sideCard" style="top:210px"><div class="cardTitle">教材对应位置</div><div class="cardText">22.4 正文开头<br>先观察原始数据，再进入分组统计。</div></div>
    <div class="sideCard teal" style="top:510px"><div class="cardTitle">本页任务</div><div class="cardText">从散乱数据转向“分布”的表示。</div></div>
    <div class="lesson">22.4 频数分布与直方图</div>
  </section>`, 3);
}

const pages = [titleHtml(), goalsHtml(), dataHtml()];
const pngs = [];
pages.forEach((html, i) => {
  const htmlPath = path.join(QA_DIR, `page-${String(i + 1).padStart(2, "0")}.html`);
  const pngPath = path.join(QA_DIR, `page-${String(i + 1).padStart(2, "0")}.png`);
  fs.writeFileSync(htmlPath, html, "utf8");
  execFileSync(EDGE, [
    "--headless",
    "--disable-gpu",
    "--hide-scrollbars",
    "--window-size=1600,900",
    `--screenshot=${pngPath}`,
    pathToFileURL(htmlPath).href,
  ], { stdio: "ignore" });
  pngs.push(pngPath);
});

const pptx = new pptxgen();
pptx.defineLayout({ name: "WIDE16X9", width: 13.333, height: 7.5 });
pptx.layout = "WIDE16X9";
pptx.author = "math-resource-engine";
pptx.subject = "22.4 频数分布与直方图 - 前三页截图版";
pptx.title = "22.4 频数分布与直方图 - 前三页截图版";
pngs.forEach((png) => {
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addImage({ path: png, x: 0, y: 0, w: 13.333, h: 7.5 });
});

pptx.writeFile({ fileName: PPTX_OUT }).then(() => {
  console.log(PPTX_OUT);
});
