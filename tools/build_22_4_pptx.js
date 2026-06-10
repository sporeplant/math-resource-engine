const fs = require("fs");
const path = require("path");
const pptxgen = require("../.pptx-build/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT_DIR = path.join(ROOT, "输出");
const IMG_DIR = path.join(OUT_DIR, "images");
const OUT = path.join(OUT_DIR, "22.4_频数分布与直方图_课件.pptx");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "math-resource-engine";
pptx.subject = "22.4 频数分布与直方图";
pptx.title = "22.4 频数分布与直方图";
pptx.company = "初中数学教学资源系统";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;

const W = 13.333;
const H = 7.5;
const C = {
  ink: "1F2937",
  mut: "6B7280",
  paper: "F8FAFC",
  card: "FFFFFF",
  teal: "0F766E",
  teal2: "14B8A6",
  amber: "F59E0B",
  coral: "EF4444",
  line: "CBD5E1",
  pale: "E0F2F1",
  cream: "FFF7ED",
};

function shadow() {
  return { type: "outer", color: "000000", opacity: 0.10, blur: 2, angle: 45, offset: 1 };
}

function clean(s) {
  return String(s)
    .replace(/\*\*/g, "")
    .replace(/\$/g, "")
    .replace(/\\text\{([^}]*)\}/g, "$1")
    .replace(/\\sim/g, "~")
    .replace(/\\div/g, "÷")
    .replace(/\\approx/g, "≈")
    .replace(/\\%/g, "%")
    .replace(/\\le/g, "≤")
    .replace(/\\ge/g, "≥")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .trim();
}

function slideBg(slide, title, kind = "content") {
  slide.background = { color: kind === "dark" ? C.ink : C.paper };
  if (kind !== "dark") {
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.18, fill: { color: C.teal }, line: { color: C.teal } });
  }
  if (title) {
    slide.addText(title, {
      x: 0.55,
      y: 0.34,
      w: 11.2,
      h: 0.42,
      margin: 0,
      fontFace: "Microsoft YaHei",
      fontSize: 24,
      bold: true,
      color: kind === "dark" ? "FFFFFF" : C.ink,
      breakLine: false,
      fit: "shrink",
    });
  }
  slide.addText("22.4 频数分布与直方图", {
    x: 10.8,
    y: 7.05,
    w: 1.9,
    h: 0.18,
    margin: 0,
    align: "right",
    fontFace: "Microsoft YaHei",
    fontSize: 8.5,
    color: kind === "dark" ? "CBD5E1" : C.mut,
  });
}

function addTag(slide, text, x, y, color = C.teal) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w: 1.25,
    h: 0.34,
    rectRadius: 0.04,
    fill: { color },
    line: { color },
  });
  slide.addText(text, {
    x,
    y: y + 0.06,
    w: 1.25,
    h: 0.14,
    margin: 0,
    fontSize: 9,
    bold: true,
    color: "FFFFFF",
    align: "center",
    fontFace: "Microsoft YaHei",
  });
}

function addTextBox(slide, lines, x, y, w, h, opts = {}) {
  const text = Array.isArray(lines) ? lines.map(clean).filter(Boolean).join("\n") : clean(lines);
  slide.addText(text, {
    x,
    y,
    w,
    h,
    margin: 0.08,
    fontFace: "Microsoft YaHei",
    fontSize: opts.fontSize || 16,
    color: opts.color || C.ink,
    bold: opts.bold || false,
    breakLine: false,
    fit: "shrink",
    valign: opts.valign || "top",
    align: opts.align || "left",
    paraSpaceAfterPt: opts.paraSpaceAfterPt || 5,
    lineSpacingMultiple: 0.95,
  });
}

function addCard(slide, x, y, w, h, title, lines, accent = C.teal) {
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w,
    h,
    fill: { color: C.card },
    line: { color: "E5E7EB", width: 0.75 },
    shadow: shadow(),
  });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color: accent }, line: { color: accent } });
  slide.addText(title, {
    x: x + 0.22,
    y: y + 0.2,
    w: w - 0.44,
    h: 0.25,
    margin: 0,
    fontFace: "Microsoft YaHei",
    fontSize: 14,
    bold: true,
    color: accent,
    fit: "shrink",
  });
  addTextBox(slide, lines, x + 0.22, y + 0.58, w - 0.44, h - 0.78, { fontSize: 13.5 });
}

function addSource(slide, id) {
  slide.addText(id, {
    x: 0.55,
    y: 7.05,
    w: 8.6,
    h: 0.18,
    margin: 0,
    fontFace: "Microsoft YaHei",
    fontSize: 7.8,
    color: C.mut,
    fit: "shrink",
  });
}

function addStudentReveal(slide, text, x, y, w = 3.2, h = 0.35) {
  slide.addText(text, {
    x,
    y,
    w,
    h,
    margin: 0,
    fontFace: "Microsoft YaHei",
    fontSize: 15,
    bold: true,
    color: C.coral,
    fit: "shrink",
  });
}

function addSimpleTable(slide, data, x, y, w, h, opts = {}) {
  const rows = data.length;
  const cols = Math.max(...data.map((r) => r.length));
  const colW = opts.colW || Array(cols).fill(w / cols);
  const rowH = opts.rowH || Array(rows).fill(h / rows);
  let cy = y;
  for (let r = 0; r < rows; r++) {
    let cx = x;
    for (let c = 0; c < cols; c++) {
      const cw = colW[c] || w / cols;
      const rh = rowH[r] || h / rows;
      const isHead = r === 0;
      slide.addShape(pptx.ShapeType.rect, {
        x: cx,
        y: cy,
        w: cw,
        h: rh,
        fill: { color: isHead ? C.teal : r % 2 ? "FFFFFF" : "F1F5F9" },
        line: { color: "D1D5DB", width: 0.55 },
      });
      slide.addText(clean(data[r][c] || ""), {
        x: cx + 0.03,
        y: cy + 0.07,
        w: cw - 0.06,
        h: Math.max(0.1, rh - 0.14),
        margin: 0,
        fontFace: "Microsoft YaHei",
        fontSize: opts.fontSize || 11,
        bold: isHead,
        color: isHead ? "FFFFFF" : C.ink,
        align: "center",
        valign: "mid",
        fit: "shrink",
      });
      cx += cw;
    }
    cy += rowH[r] || h / rows;
  }
}

function addFlow(slide, labels, x, y, w, accent = C.teal) {
  const gap = 0.16;
  const bw = (w - gap * (labels.length - 1)) / labels.length;
  labels.forEach((label, i) => {
    const bx = x + i * (bw + gap);
    slide.addShape(pptx.ShapeType.roundRect, {
      x: bx,
      y,
      w: bw,
      h: 0.74,
      rectRadius: 0.05,
      fill: { color: i === labels.length - 1 ? accent : "FFFFFF" },
      line: { color: i === labels.length - 1 ? accent : C.line, width: 1 },
      shadow: i === labels.length - 1 ? undefined : shadow(),
    });
    slide.addText(clean(label), {
      x: bx + 0.06,
      y: y + 0.25,
      w: bw - 0.12,
      h: 0.18,
      margin: 0,
      fontFace: "Microsoft YaHei",
      fontSize: 12,
      bold: true,
      color: i === labels.length - 1 ? "FFFFFF" : C.ink,
      align: "center",
      fit: "shrink",
    });
    if (i < labels.length - 1) {
      slide.addShape(pptx.ShapeType.chevron, {
        x: bx + bw - 0.03,
        y: y + 0.22,
        w: 0.28,
        h: 0.28,
        fill: { color: C.amber },
        line: { color: C.amber },
      });
    }
  });
}

function addImage(slide, file, x, y, w, h) {
  const full = path.join(IMG_DIR, file);
  if (!fs.existsSync(full)) return false;
  slide.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: "FFFFFF" }, line: { color: C.line }, shadow: shadow() });
  slide.addImage({ path: full, x: x + 0.08, y: y + 0.08, w: w - 0.16, h: h - 0.16 });
  return true;
}

function addHistogram(slide, x, y, w, h) {
  const labels = ["100-120", "120-140", "140-160", "160-180", "180-200", "200-220"];
  const vals = [5, 10, 15, 12, 5, 3];
  const max = 16;
  slide.addShape(pptx.ShapeType.line, { x, y: y + h, w, h: 0, line: { color: C.ink, width: 1.2 } });
  slide.addShape(pptx.ShapeType.line, { x, y, w: 0, h, line: { color: C.ink, width: 1.2 } });
  labels.forEach((lab, i) => {
    const bw = w / labels.length;
    const bh = (vals[i] / max) * (h - 0.22);
    const bx = x + i * bw;
    slide.addShape(pptx.ShapeType.rect, {
      x: bx + 0.01,
      y: y + h - bh,
      w: bw - 0.02,
      h: bh,
      fill: { color: i === 2 ? C.amber : C.teal2 },
      line: { color: "FFFFFF", width: 0.5 },
    });
    slide.addText(String(vals[i]), { x: bx, y: y + h - bh - 0.25, w: bw, h: 0.15, margin: 0, fontSize: 10, bold: true, align: "center", color: C.ink, fontFace: "Microsoft YaHei" });
    slide.addText(lab, { x: bx, y: y + h + 0.08, w: bw, h: 0.24, margin: 0, fontSize: 8.4, align: "center", color: C.mut, fontFace: "Microsoft YaHei", fit: "shrink" });
  });
  slide.addText("频数", { x: x - 0.36, y: y - 0.12, w: 0.38, h: 0.2, margin: 0, fontSize: 9, color: C.mut, fontFace: "Microsoft YaHei" });
  slide.addText("用电量 x", { x: x + w - 0.5, y: y + h + 0.42, w: 0.75, h: 0.2, margin: 0, fontSize: 9, color: C.mut, fontFace: "Microsoft YaHei" });
}

function titleSlide() {
  const slide = pptx.addSlide();
  slideBg(slide, "", "dark");
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.ink }, line: { color: C.ink } });
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.28, h: H, fill: { color: C.teal2 }, line: { color: C.teal2 } });
  slide.addText("22.4", { x: 0.72, y: 1.06, w: 2.1, h: 0.55, margin: 0, fontSize: 30, bold: true, color: C.amber, fontFace: "Microsoft YaHei" });
  slide.addText("频数分布与直方图", { x: 0.72, y: 1.82, w: 7.1, h: 0.75, margin: 0, fontSize: 38, bold: true, color: "FFFFFF", fontFace: "Microsoft YaHei", fit: "shrink" });
  slide.addText("第二十二章 数据的收集、整理与描述", { x: 0.75, y: 2.78, w: 5.2, h: 0.26, margin: 0, fontSize: 16, color: "CBD5E1", fontFace: "Microsoft YaHei" });
  addFlow(slide, ["分组", "制表", "画图", "读图应用"], 0.75, 4.3, 6.7, C.amber);
  addHistogram(slide, 8.15, 1.55, 4.2, 3.6);
  addSource(slide, "source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4_courseware");
}

function objectives() {
  const slide = pptx.addSlide();
  slideBg(slide, "🎯 本课目标");
  const items = [
    ["1", "从连续数据中确定最大值、最小值和极差"],
    ["2", "按组距分组，列出频数和频率分布表"],
    ["3", "画出频数分布直方图，并读出集中范围"],
    ["4", "用直方图信息评价实际方案"],
  ];
  items.forEach((it, i) => {
    const y = 1.25 + i * 1.05;
    slide.addShape(pptx.ShapeType.ellipse, { x: 0.85, y, w: 0.5, h: 0.5, fill: { color: i === 3 ? C.amber : C.teal }, line: { color: i === 3 ? C.amber : C.teal } });
    slide.addText(it[0], { x: 0.85, y: y + 0.15, w: 0.5, h: 0.1, margin: 0, fontSize: 13, bold: true, color: "FFFFFF", align: "center", fontFace: "Microsoft YaHei" });
    addTextBox(slide, it[1], 1.65, y + 0.03, 5.7, 0.42, { fontSize: 17, bold: true });
  });
  addFlow(slide, ["分组", "频数表", "直方图", "方案评价"], 7.25, 2.55, 5.15, C.teal);
}

function rawData() {
  const slide = pptx.addSlide();
  slideBg(slide, "📉 阶梯电价中 50 户用电量");
  addTextBox(slide, "为了制定合理的阶梯电价，需要观察居民全年月平均用电量的分布。", 0.7, 1.0, 6.2, 0.45, { fontSize: 16, bold: true });
  const data = [
    ["155", "198", "175", "158", "158", "124", "154", "148", "169", "120"],
    ["190", "133", "160", "215", "172", "126", "145", "130", "131", "118"],
    ["108", "157", "145", "165", "122", "106", "165", "150", "136", "144"],
    ["140", "159", "110", "134", "170", "168", "162", "170", "205", "186"],
    ["182", "156", "138", "187", "100", "142", "168", "218", "175", "146"],
  ];
  addSimpleTable(slide, data, 0.72, 1.75, 7.05, 3.35, { fontSize: 11, rowH: [0.55, 0.55, 0.55, 0.55, 0.55] });
  addCard(slide, 8.25, 1.55, 3.95, 2.8, "教材对应位置", ["22.4 正文开头", "先观察原始数据，再进入分组统计。"], C.amber);
  addCard(slide, 8.25, 4.65, 3.95, 1.0, "本页任务", ["从散乱数据转向“分布”的表示。"], C.teal);
}

function questionRaw() {
  const slide = pptx.addSlide();
  slideBg(slide, "🤔 原始数据能直接读出规律吗");
  addTag(slide, "口头回答", 0.72, 1.08, C.amber);
  addTextBox(slide, "这 50 个数据散乱排列，直接看能一眼判断居民用电量主要集中在哪个范围吗？", 0.75, 1.68, 7.0, 1.0, { fontSize: 22, bold: true });
  addCard(slide, 0.75, 3.15, 5.15, 1.4, "提示", ["先试着找最大值、最小值，再观察数据是否集中。"], C.teal);
  addCard(slide, 6.25, 3.15, 3.0, 1.4, "指定回答", ["点击后显示姓名"], C.coral);
  addStudentReveal(slide, "请张楷瑞同学回答", 6.5, 4.0, 2.5, 0.3);
  addCard(slide, 9.55, 3.15, 2.0, 1.4, "限时", ["1 分钟"], C.amber);
}

function rangeSlide() {
  const slide = pptx.addSlide();
  slideBg(slide, "📉 步骤一：最大值、最小值、极差");
  addTag(slide, "练习本", 0.72, 1.0, C.teal);
  addTextBox(slide, "在 50 个数据中标出最大值和最小值。", 0.75, 1.55, 5.2, 0.4, { fontSize: 17, bold: true });
  addCard(slide, 0.75, 2.25, 3.25, 1.55, "公式", ["极差 = 最大值 - 最小值"], C.teal);
  addCard(slide, 4.35, 2.25, 3.25, 1.55, "本题数据", ["最大值 218", "最小值 100"], C.amber);
  addCard(slide, 7.95, 2.25, 3.25, 1.55, "计算", ["218 - 100 = 118"], C.coral);
  addStudentReveal(slide, "请孙凡浩同学说出极差的计算过程。", 0.75, 4.55, 5.6, 0.4);
}

function groupDistance() {
  const slide = pptx.addSlide();
  slideBg(slide, "🤔 步骤二：组数与组距怎么定");
  addTag(slide, "口头回答", 0.72, 1.0, C.amber);
  addTextBox(slide, ["数据个数在 100 以内时，一般分为 5~10 组。", "118 ÷ 6 ≈ 19.7", "教材将组距取 20，这样可分成 6 组。"], 0.75, 1.55, 5.6, 1.35, { fontSize: 17, bold: true });
  addFlow(slide, ["极差 118", "约分 6 组", "组距取 20", "端点清晰"], 0.75, 3.3, 6.9, C.teal);
  addCard(slide, 8.1, 1.35, 3.8, 1.65, "基础追问", ["为什么组距取 20 而不是 19.7？"], C.teal);
  addStudentReveal(slide, "请庞若涵同学回答", 8.34, 2.55, 2.4, 0.3);
  addCard(slide, 8.1, 3.35, 3.8, 1.65, "拓展追问", ["组距取 15 或 30 时，分组效果会怎样？"], C.coral);
  addStudentReveal(slide, "请刘森泽同学回答", 8.34, 4.55, 2.4, 0.3);
}

function frequencyTable() {
  const slide = pptx.addSlide();
  slideBg(slide, "📉 步骤三：频数与频率");
  addTextBox(slide, ["各组中数据的个数叫作频数。", "频数与数据总个数的比值叫作频率。"], 0.75, 1.1, 5.2, 0.85, { fontSize: 18, bold: true });
  const table = [
    ["用电量 x", "100≤x<120", "120≤x<140", "140≤x<160", "160≤x<180", "180≤x<200", "200≤x<220"],
    ["频数", "5", "10", "15", "12", "5", "3"],
    ["频率", "10%", "20%", "30%", "24%", "10%", "6%"],
  ];
  addSimpleTable(slide, table, 0.7, 2.35, 8.85, 1.95, { fontSize: 10.2, colW: [1.25, 1.26, 1.26, 1.26, 1.26, 1.26, 1.3] });
  addHistogram(slide, 9.95, 1.65, 2.55, 2.25);
  addSource(slide, "source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4-步骤(3)表");
}

function concentrated() {
  const slide = pptx.addSlide();
  slideBg(slide, "🤔 哪个组最集中");
  addTag(slide, "口头回答", 0.72, 1.02, C.amber);
  addCard(slide, 0.75, 1.65, 5.4, 1.75, "问题一", ["哪个组的“正”字最多？这个结果说明什么？"], C.teal);
  addStudentReveal(slide, "请郭玲誊同学回答", 1.0, 2.95, 2.6, 0.3);
  addCard(slide, 0.75, 4.05, 5.4, 1.75, "问题二", ["各组频率加总应是多少？如果不是这个结果，可能哪里出错？"], C.coral);
  addStudentReveal(slide, "请陈祺含同学回答", 1.0, 5.35, 2.6, 0.3);
  addHistogram(slide, 7.0, 1.62, 4.7, 3.35);
  addTextBox(slide, "提示：频率表示各组占全部数据的比例。", 7.0, 5.55, 4.4, 0.36, { fontSize: 14, bold: true, color: C.teal });
}

function histogramSlide() {
  const slide = pptx.addSlide();
  slideBg(slide, "📉 步骤四：频数分布直方图");
  addTextBox(slide, ["横轴表示全年月平均用电量，纵轴表示频数。", "小长方形的高表示各组的频数。"], 0.75, 1.05, 5.2, 0.85, { fontSize: 17, bold: true });
  addHistogram(slide, 0.95, 2.35, 5.2, 3.05);
  addImage(slide, "f01de117d09a9c643fb0ad7636dc4ff80eb59a4dee8061d2ee7bc1ed09cb0a52.jpg", 7.0, 1.05, 4.65, 4.95);
  addTextBox(slide, "图 22.4-1 频数分布直方图", 7.05, 6.18, 4.2, 0.25, { fontSize: 11, color: C.mut });
  addSource(slide, "source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4-图22.4-1");
}

function barVsHist() {
  const slide = pptx.addSlide();
  slideBg(slide, "🤔 直方图和条形图有什么不同");
  addTag(slide, "口头回答", 0.72, 1.0, C.amber);
  addCard(slide, 0.75, 1.62, 5.4, 1.85, "问题一", ["频数分布直方图和以前学过的条形统计图，在画法上有什么关键不同？"], C.teal);
  addStudentReveal(slide, "请赖孟訸同学回答", 1.0, 3.0, 2.6, 0.3);
  addCard(slide, 0.75, 4.05, 5.4, 1.85, "问题二", ["如果用电量改成“低 / 中 / 高”三档分类，应画哪种统计图？理由是什么？"], C.coral);
  addStudentReveal(slide, "请李奇禹同学回答", 1.0, 5.45, 2.6, 0.3);
  addFlow(slide, ["连续数据", "相邻区间", "矩形相连", "看分布"], 6.95, 2.5, 5.1, C.amber);
}

function practice12() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 练习 / 检测");
  addTag(slide, "练习本", 0.72, 1.0, C.teal);
  addTextBox(slide, ["教材练习第 (1)(2) 题（来源：教材练习）", "限时 3 分钟", "评分：第 (1) 题 2 分，第 (2) 题 2 分，满分 4 分", "产出：写出 n、分布范围、组距、组数"], 0.75, 1.62, 5.7, 2.15, { fontSize: 16, bold: true });
  addImage(slide, "ff4ecd374db12bf0125ad0afa1992fbb96b5dd1ad2dd6b74a26b0a8785bd8d1e.jpg", 7.05, 1.0, 4.6, 4.8);
  addSource(slide, "source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4-练习(1)(2)");
}

function answer12() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 参考答案");
  addCard(slide, 0.78, 1.25, 5.5, 2.2, "练习 (1)", ["数据个数：n = 2+4+10+22+20+11+6+4+1 = 80", "数据大致分布在 148 cm 到 174 cm 之间。"], C.teal);
  addCard(slide, 6.85, 1.25, 4.35, 2.2, "练习 (2)", ["组距为 3 cm。", "共有 9 组。"], C.amber);
}

function practice34() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 练习 / 检测");
  addTag(slide, "练习本", 0.72, 1.0, C.teal);
  addTextBox(slide, ["教材练习第 (3)(4) 题（来源：教材练习）", "限时 4 分钟", "评分：第 (3) 题 3 分，第 (4) 题 3 分，满分 6 分", "产出：写出最大频数组、频数、频率，并填写表格"], 0.75, 1.62, 5.7, 2.15, { fontSize: 16, bold: true });
  addImage(slide, "ff4ecd374db12bf0125ad0afa1992fbb96b5dd1ad2dd6b74a26b0a8785bd8d1e.jpg", 7.05, 1.0, 4.6, 4.8);
  addSource(slide, "source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4-练习(3)(4)");
}

function answer34() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 参考答案");
  addCard(slide, 0.75, 1.1, 4.95, 2.05, "练习 (3)", ["频数最大的组为 156.5~159.5。", "该组频数为 22，频率为 22÷80=27.5%。"], C.teal);
  const table = [
    ["身高/cm", "148~156", "157~165", "166~174"],
    ["频数", "16", "53", "11"],
    ["频率", "20%", "66.25%", "13.75%"],
  ];
  addSimpleTable(slide, table, 6.25, 1.25, 5.6, 2.25, { fontSize: 12, colW: [1.4, 1.4, 1.4, 1.4] });
  addTextBox(slide, "练习 (4)", 6.25, 0.95, 2.0, 0.22, { fontSize: 15, bold: true, color: C.teal });
}

function discuss() {
  const slide = pptx.addSlide();
  slideBg(slide, "🤔 大家谈谈：阶梯电价是否合理");
  addTag(slide, "小组讨论", 0.72, 1.0, C.amber);
  addCard(slide, 0.75, 1.58, 4.8, 1.55, "已知信息", ["全年月平均用电量小于 180 千瓦时的有 42 户。", "42÷50=84%"], C.teal);
  addCard(slide, 6.0, 1.58, 5.3, 2.0, "讨论问题", ["42 户占 84% 的居民在第一档，你认为这个阶梯电价方案合理吗？", "如果提出调整建议，你会怎么说？"], C.coral);
  addStudentReveal(slide, "请焦子轩同学代表发言", 6.0, 4.08, 3.3, 0.36);
  addFlow(slide, ["读图", "计算比例", "判断方案", "表达建议"], 0.78, 5.05, 8.4, C.amber);
}

function practice5a() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 练习 / 检测");
  addTag(slide, "练习本", 0.72, 1.0, C.teal);
  addTextBox(slide, ["教材练习第 (5) 题 + 教材 A 组第 1 题", "来源：教材练习、教材习题 A 组", "限时 5 分钟", "评分：练习 (5) 2 分，A 组第 1 题 6 分，满分 8 分", "产出：写出校服尺码建议和 A 组第 1 题答案"], 0.75, 1.55, 5.9, 2.65, { fontSize: 15.5, bold: true });
  addImage(slide, "ecb6cead8bee31141ae3de57a3f6e1529a77c0f303efcf61232147c50482ee27.jpg", 7.05, 1.0, 4.6, 4.8);
  addSource(slide, "source_id: 教材原文_22.4_频数分布与直方图 | source_type: textbook | question_id: 22.4-练习(5)+22.4-A组1");
}

function answer5a() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 参考答案");
  addCard(slide, 0.75, 1.0, 5.0, 1.4, "练习 (5)", ["小号约 16 套，中号约 23 套，大号约 11 套，可适当多订中号。"], C.teal);
  addCard(slide, 0.75, 2.75, 5.0, 2.2, "A 组第 1 题", ["(1) 频数轴刻度依次标为 5、10、15、20、25、30。", "(2) 61~70 分的人数为 30；得分在 81 分及以上的人数为 15+10+5=30。", "(3) 优秀率为 (10+5)÷100=15%。"], C.amber);
}

function summary() {
  const slide = pptx.addSlide();
  slideBg(slide, "💡 本课小结");
  const table = [
    ["层次", "回顾问题", "回答方式"],
    ["基础层", "频数和频率分别表示什么？", "口头回答"],
    ["中间层", "列频数分布表一般经历哪几个步骤？", "口头回答"],
    ["拓展层", "直方图比原始数据表多提供了哪些分布信息？", "口头回答"],
  ];
  addSimpleTable(slide, table, 0.75, 1.15, 11.25, 2.6, { fontSize: 12.2, colW: [1.4, 7.5, 2.35] });
  addFlow(slide, ["散乱数据", "分组计数", "频数分布表", "频数分布直方图", "读图决策"], 0.75, 4.55, 10.5, C.teal);
}

function largeData() {
  const slide = pptx.addSlide();
  slideBg(slide, "🤔 数据量很大时怎么办");
  addTag(slide, "口头回答", 0.72, 1.0, C.amber);
  addTextBox(slide, "如果给你 1000 个数据，还适合一个一个画“正”字吗？", 0.78, 1.68, 6.25, 0.72, { fontSize: 24, bold: true });
  addCard(slide, 0.78, 3.0, 4.8, 1.65, "可用工具", ["计算器、电子表格或统计软件，可快速分组、计数、画图。"], C.teal);
  addCard(slide, 6.05, 3.0, 4.8, 1.65, "方法价值", ["统计方法让数据变清晰，信息工具让处理更高效。"], C.amber);
  addStudentReveal(slide, "请吴瑾璇同学回答", 0.78, 5.35, 2.8, 0.34);
}

function homework() {
  const slide = pptx.addSlide();
  slideBg(slide, "📑 课后作业");
  addCard(slide, 0.75, 1.05, 5.0, 1.45, "必做", ["教材 A 组第 2 题 (1)(2)(3)", "练习册“夯实基础”第 1 题 (1)、第 2 题 (1)"], C.teal);
  addCard(slide, 0.75, 2.95, 5.0, 1.2, "选作", ["教材 B 组第 3 题 (1)(2)"], C.amber);
  addCard(slide, 6.2, 1.05, 5.1, 3.1, "挑战", ["教材 C 组第 4 题：收集连续 30 天空气质量指数，并绘制频数分布直方图。"], C.coral);
  addFlow(slide, ["回到数据", "完成分组", "画出直方图", "解释分布"], 1.0, 5.35, 9.8, C.teal);
}

const builders = [
  titleSlide,
  objectives,
  rawData,
  questionRaw,
  rangeSlide,
  groupDistance,
  frequencyTable,
  concentrated,
  histogramSlide,
  barVsHist,
  practice12,
  answer12,
  practice34,
  answer34,
  discuss,
  practice5a,
  answer5a,
  summary,
  largeData,
  homework,
];

const maxSlides = Number(process.env.MAX_SLIDES || builders.length);
builders.slice(0, maxSlides).forEach((fn) => fn());

pptx.writeFile({ fileName: OUT }).then(() => {
  console.log(`Wrote ${OUT}`);
});
