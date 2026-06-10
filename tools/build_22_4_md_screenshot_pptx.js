const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { pathToFileURL } = require("url");
const pptxgen = require("../.pptx-build/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT_DIR = path.join(ROOT, "输出");
const IMG_DIR = path.join(OUT_DIR, "images");
const BUILD_DIR = path.join(OUT_DIR, "md_screenshot_22_4");
const MD = path.join(OUT_DIR, "22.4_频数分布与直方图_课件.md");
const sampleCount = Number(process.env.SAMPLE_SLIDES || 0);
const PPTX = path.join(
  OUT_DIR,
  sampleCount
    ? `22.4_频数分布与直方图_课件_文档截图版_前${sampleCount}页样稿.pptx`
    : "22.4_频数分布与直方图_课件_文档截图版.pptx"
);
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

fs.mkdirSync(BUILD_DIR, { recursive: true });

const raw = fs.readFileSync(MD, "utf8");
const body = raw.replace(/^---[\s\S]*?---\s*/, "").trim();
const allPages = body
  .split(/<div\s+style="page-break-after:\s*always;"><\/div>/i)
  .map((p) => p.trim())
  .filter(Boolean);
const pages = sampleCount ? allPages.slice(0, sampleCount) : allPages;

const studentNamesByPage = [];

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function cleanMath(s) {
  return String(s)
    .replace(/\$([^$]+)\$/g, (_, m) => `<span class="math">${esc(m)}</span>`)
    .replace(/\\text\{([^}]*)\}/g, "$1")
    .replace(/\\sim/g, "~")
    .replace(/\\div/g, "÷")
    .replace(/\\approx/g, "≈")
    .replace(/\\%/g, "%")
    .replace(/\\le/g, "≤")
    .replace(/\\ge/g, "≥");
}

function inline(s) {
  let out = cleanMath(esc(s));
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  return out;
}

function imageSrc(rel) {
  const name = rel.replace(/^\.\/images\//, "");
  return pathToFileURL(path.join(IMG_DIR, name)).href;
}

function renderTable(lines) {
  const rows = lines
    .filter((line) => !/^\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$/.test(line.trim()))
    .map((line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim()));
  const html = rows.map((row, ri) => {
    const tag = ri === 0 ? "th" : "td";
    return `<tr>${row.map((c) => `<${tag}>${inline(c)}</${tag}>`).join("")}</tr>`;
  }).join("");
  return `<table>${html}</table>`;
}

function renderMermaid(lines) {
  const labels = [];
  lines.forEach((line) => {
    const matches = [...line.matchAll(/\["([^"]+)"\]/g)].map((m) => m[1]);
    matches.forEach((m) => {
      if (!labels.includes(m)) labels.push(m);
    });
  });
  if (!labels.length) return `<pre>${esc(lines.join("\n"))}</pre>`;
  return `<div class="flow">${labels.map((l, i) => `<div class="flowBox">${esc(l)}</div>${i < labels.length - 1 ? '<div class="flowArrow">›</div>' : ""}`).join("")}</div>`;
}

function renderPage(md, pageIndex) {
  const names = [];
  const lines = md.split(/\r?\n/);
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    if (!line) {
      i++;
      continue;
    }
    if (/^请.+同学/.test(line)) {
      names.push(line);
      i++;
      continue;
    }
    if (/^source_id:/.test(line)) {
      out.push(`<div class="source">${inline(line)}</div>`);
      i++;
      continue;
    }
    if (/^```mermaid/.test(line)) {
      const block = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i].trim())) {
        block.push(lines[i]);
        i++;
      }
      i++;
      out.push(renderMermaid(block));
      continue;
    }
    if (/^```/.test(line)) {
      const block = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i].trim())) {
        block.push(lines[i]);
        i++;
      }
      i++;
      out.push(`<pre>${esc(block.join("\n"))}</pre>`);
      continue;
    }
    if (/^\|/.test(line)) {
      const block = [];
      while (i < lines.length && /^\|/.test(lines[i].trim())) {
        block.push(lines[i]);
        i++;
      }
      out.push(renderTable(block));
      continue;
    }
    const img = line.match(/<img\s+src="([^"]+)"(?:\s+width="([^"]+)")?\s*>/i);
    if (img) {
      out.push(`<div class="imgWrap"><img src="${imageSrc(img[1])}"></div>`);
      i++;
      continue;
    }
    if (/^###\s+/.test(line)) {
      out.push(`<h1>${inline(line.replace(/^###\s+/, ""))}</h1>`);
      i++;
      continue;
    }
    if (/^##\s+/.test(line)) {
      out.push(`<h2>${inline(line.replace(/^##\s+/, ""))}</h2>`);
      i++;
      continue;
    }
    if (/^---+$/.test(line)) {
      out.push(`<hr>`);
      i++;
      continue;
    }
    const para = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !/^###\s+/.test(lines[i].trim()) &&
      !/^##\s+/.test(lines[i].trim()) &&
      !/^\|/.test(lines[i].trim()) &&
      !/^```/.test(lines[i].trim()) &&
      !/<img\s+src=/.test(lines[i].trim()) &&
      !/^source_id:/.test(lines[i].trim()) &&
      !/^请.+同学/.test(lines[i].trim()) &&
      !/^---+$/.test(lines[i].trim())
    ) {
      para.push(lines[i].trim());
      i++;
    }
    out.push(`<p>${inline(para.join("<br>"))}</p>`);
  }
  studentNamesByPage[pageIndex] = names;
  return out.join("\n");
}

const css = `
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#e5e7eb}
body{font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;color:#1f2937}
.slide{width:1600px;height:900px;background:#fff;position:relative;overflow:hidden;padding:54px 78px 66px}
.slide:before{content:"";position:absolute;left:0;top:0;width:100%;height:18px;background:#0f766e}
h1{font-size:45px;line-height:1.16;margin:0 0 34px;font-weight:800;letter-spacing:0}
h2{font-size:34px;line-height:1.2;margin:0 0 24px;font-weight:800;letter-spacing:0}
p{font-size:25px;line-height:1.55;margin:18px 0;max-width:960px}
strong{font-weight:800}
em{color:#64748b}
code,.math{font-family:"Cambria Math","Times New Roman",serif;color:#111827;background:#f8fafc;border-radius:4px;padding:1px 5px}
table{border-collapse:collapse;margin:18px 0 24px;font-size:19px;max-width:100%}
th,td{border:1px solid #cbd5e1;padding:10px 13px;text-align:center;line-height:1.35}
th{background:#0f766e;color:#fff;font-weight:800}
tr:nth-child(even) td{background:#f8fafc}
.flow{display:flex;align-items:center;gap:14px;margin:26px 0 18px;flex-wrap:wrap}
.flowBox{min-width:132px;min-height:58px;padding:16px 20px;border:1px solid #cbd5e1;border-radius:6px;background:#fff;box-shadow:0 3px 10px rgba(15,23,42,.08);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800}
.flowBox:last-child{background:#0f766e;color:#fff}
.flowArrow{font-size:32px;font-weight:800;color:#f59e0b}
.imgWrap{position:absolute;right:115px;top:135px;width:610px;height:610px;border:1px solid #cbd5e1;background:#fff;display:flex;align-items:center;justify-content:center;padding:14px}
.imgWrap img{max-width:100%;max-height:100%;object-fit:contain}
.source{position:absolute;left:78px;bottom:34px;color:#64748b;font-size:16px;max-width:1180px}
hr{border:0;height:1px;background:#e5e7eb;margin:28px 0}
.slide:after{content:"22.4 频数分布与直方图";position:absolute;right:70px;bottom:34px;color:#64748b;font-size:17px}
`;

const pngs = [];
pages.forEach((page, index) => {
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body><section class="slide">${renderPage(page, index)}</section></body></html>`;
  const htmlPath = path.join(BUILD_DIR, `slide-${String(index + 1).padStart(2, "0")}.html`);
  const pngPath = path.join(BUILD_DIR, `slide-${String(index + 1).padStart(2, "0")}.png`);
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
pptx.subject = "22.4 频数分布与直方图 - 文档截图版";
pptx.title = "22.4 频数分布与直方图 - 文档截图版";

pngs.forEach((png, index) => {
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addImage({ path: png, x: 0, y: 0, w: 13.333, h: 7.5 });
  const names = studentNamesByPage[index] || [];
  names.forEach((name, j) => {
    slide.addText(name, {
      x: 0.66,
      y: 5.22 + j * 0.38,
      w: 5.3,
      h: 0.3,
      margin: 0,
      fontFace: "Microsoft YaHei",
      fontSize: 15,
      bold: true,
      color: "EF4444",
      fit: "shrink",
    });
  });
});

pptx.writeFile({ fileName: PPTX }).then(() => {
  fs.writeFileSync(path.join(BUILD_DIR, "student_names_by_page.json"), JSON.stringify(studentNamesByPage, null, 2), "utf8");
  console.log(PPTX);
});
