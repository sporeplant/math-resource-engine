import json, os

# Build the complete exam JSON

slides = []

def add_slide(slides, elements):
    sid = f"s{len(slides)+1:02d}"
    for i, e in enumerate(elements):
        e["id"] = f"{sid}_e{i+1:03d}"
    slides.append({"id": sid, "elements": elements})

def text(text, y, fs=24, bold=False, color="#222222", w=1120, h=40):
    return {"type": "text", "text": text, "x": 70, "y": y, "width": w, "height": h,
            "fontSize": fs, "bold": bold, "color": color, "fontFamily": "Microsoft YaHei"}

def img(name, y, w=700, h=380):
    return {"type": "image", "src": name, "x": (1280-w)//2, "y": y, "width": w, "height": h}

# ========== 标题页 ==========
add_slide(slides, [
    text("📐 遵化市 2024—2025 学年度第二学期期末学业水平评估", 54, 32, True, "#1f4e79"),
    text("八年级数学试卷", 120, 28, True, "#1f4e79"),
    text("希沃白板课件 · 题目展示（无解答）", 180, 22, False, "#555555"),
    text("总分 100 分    考试时间 90 分钟", 220, 22, False, "#555555"),
])

# ========== 选择题 ==========
mc_data = [
    ("1", "内角为 $108^{\\circ}$ 的正多边形是",  ["A. 3", "B. 4", "C. 5", "D. 6"], None),
    ("2", "如图，边长为3的正方形OBCD的两边落在坐标轴正半轴上，点C的坐标是",
     ["A. (3, -3)", "B. (-3, 3)", "C. (3, 3)", "D. (-3, -3)"],
     "e827819294a1ab9237bf2fac7d258e9db1beab5661afb22c986f163ebf249e3b.jpg"),
    ("3", "如图，菱形ABCD中，$\\angle D = 150^{\\circ}$，则 $\\angle 1 =$",
     ["A. $30^{\\circ}$", "B. $25^{\\circ}$", "C. $20^{\\circ}$", "D. $15^{\\circ}$"],
     "f0a805e835ca7e5dd4c94fedb318ceb0c933fceb1cd5b3896bc7554dba09c694.jpg"),
    ("4", "如图，在矩形ABCD中，对角线AC、BD相交于点O，$\\angle ABD = 60^{\\circ}$，AB=2，则AC的长为",
     ["A. 6", "B. 5", "C. 4", "D. 3"],
     "be18c603b9b5831ecbd2ebfa85ad8d5f8d319051f47e2442050fe416009a2b27.jpg"),
    ("5", "如图，平地上A、B两点被池塘隔开，测量员在岸边选一点C，并分别找到AC和BC的中点D、E，测得DE=16米，则A、B两点间的距离为",
     ["A. 30米", "B. 32米", "C. 36米", "D. 48米"],
     "1ed08c8554a06a2f2932041715c06dd0aa022c22c82a952bc410f76ab107301b.jpg"),
    ("6", "如图，在每个四边形上所做的标记中，线段上的划记数量相同的表示线段相等，角的标记弧线数量相同的表示角相等，则下列一定为平行四边形的有",
     ["A. 1个", "B. 2个", "C. 3个", "D. 4个"],
     None),  # multi-image, handled specially
    ("7", "如图，在平行四边形ABCD中，E是边CD上一点，将 $\\triangle ADE$ 沿AE折叠至 $\\triangle AD'E$ 处，AD'与CE交于点F，若 $\\angle B=52^{\\circ}$，$\\angle DAE=20^{\\circ}$，则 $\\angle FED'$ 的度数为",
     ["A. $40^{\\circ}$", "B. $36^{\\circ}$", "C. $50^{\\circ}$", "D. $45^{\\circ}$"],
     "fd63c31d9ad0962fe101830173fca617aad3c0695fe986eddce2b5bf169fbd1f.jpg"),
    ("8", "如图，两条直线的交点坐标(-2,3)可以看作两个二元一次方程的公共解，其中一个方程是 $x+y=1$，则另一个方程是",
     ["A. $2x-y=1$", "B. $2x+y=-1$", "C. $2x+y=1$", "D. $3x-y=1$"],
     "8b0eb14e5887a4540a0ac3d592bd68d654c2bd337ffc958925c08166990bb7e1.jpg"),
    ("9", '“漏壶”是一种古代计时器，用 $x$ 表示漏水时间，$y$ 表示壶底到水面的高度。不考虑水量变化对压力的影响，下列图象最适合表示 $y$ 与 $x$ 对应关系的是',
     [], None),  # image options
    ("10", "下列有关一次函数 $y=-3x+2$ 的说法中，错误的是",
     ["A. 当x值增大时，y的值随着x增大而减小", "B. 函数图象与y轴的交点坐标为(0,2)", "C. 函数图象经过第一、二、四象限", "D. 图象经过点(1,5)"],
     None),
    ("11", "下面三个问题中都有两个变量：①货车匀速通过隧道，货车在隧道内的长度y与时间x；②王大爷散步离家的距离y与时间x；③往圆柱形空杯中匀速倒水，杯中水的体积y与时间x。其中变量y与x之间的函数关系大致符合图4的是",
     ["A. ①②", "B. ①③", "C. ②③", "D. ①②③"],
     "86d42bd3f821a2ca6c85a2070271029032f264306da56331b73da809507cc201.jpg"),
    ("12", "若一组数据共有100个，则通常分成",
     ["A. 3～5组", "B. 5～12组", "C. 12～20组", "D. 20～25组"],
     None),
]

for qnum, stem, opts, qimg in mc_data:
    el, y = [], 54
    el.append(text(f"选择题 第{qnum}题", y, 28, True, "#1f4e79"))
    y += 60

    # body text
    el.append(text(stem, y, 24, False, "#222222", 1120, 60))
    y += 68

    # options
    if opts and qnum != "9":
        opt_text = "    ".join(opts)
        el.append(text(opt_text, y, 22))
        y += 64

    # images
    if qimg and qnum != "6" and qnum != "9" and qnum != "11":
        src = f"assets/{qimg}"
        el.append(img(src, y, 650, 360))
    elif qnum == "6":
        # 4 images side by side
        imgs = ["01fa17df5b950a5f85caa1ed7e4b69ee96f5ce9ea013e7bc63962f0e8b5ca9c4.jpg",
                "7d4f793370f315b42cbd6461e1bb512c49d712235659ee375de0753333f91024.jpg",
                "2d9aa8ed7135a2116845532196adee02a0ed2eac949980b97a151b9d634e0355.jpg",
                "a188d6484c2e624f9eab9f8e48539cb63a7355568cedfa1fe6ab57c28630ab75.jpg"]
        el.append(text("A. 1个                                          B. 2个", y, 22))
        y += 30
        # row 1
        for idx in [0, 1]:
            el.append({"type": "image", "src": f"assets/{imgs[idx]}", "x": 70+idx*520, "y": y, "width": 480, "height": 320})
        y += 330
        el.append(text("C. 3个                                          D. 4个", y, 22))
        y += 30
        for idx in [2, 3]:
            el.append({"type": "image", "src": f"assets/{imgs[idx]}", "x": 70+(idx-2)*520, "y": y, "width": 480, "height": 320})
    elif qnum == "9":
        imgs = ["73e85b84ef371969bb74bf6aebf48fa9a5415e3af45f88e8aba98d10794d088a.jpg",
                "bf2ea3ed2cc0280880ae15dda714f0bd38a8e0b0c9b7051462d334cab0c33bd7.jpg",
                "88c1c7420d9fe5134ccb79552d5d6574209f7e150041207339b2d10f8bba9f38.jpg",
                "fa4af7aee71aade9246782546eeb32a67a41871f8c310edc57f5e882c0360696.jpg",
                "e26b275dd93606f6738c28b3572e4f9e9c7949fe56f372ae10f506d3b9f255e8.jpg"]
        # A/B row 1
        for idx in [0, 1]:
            el.append(text(["A.", "B."][idx], y, 22))
            y += 26
            el.append({"type": "image", "src": f"assets/{imgs[idx]}", "x": 70+idx*280, "y": y, "width": 250, "height": 170})
        y += 180
        # C/D row 2
        for idx in [2, 3]:
            el.append(text(["C.", "D."][idx-2], y, 22))
            y += 26
            el.append({"type": "image", "src": f"assets/{imgs[idx]}", "x": 70+(idx-2)*280, "y": y, "width": 250, "height": 170})
    elif qnum == "11":
        imgs = ["86d42bd3f821a2ca6c85a2070271029032f264306da56331b73da809507cc201.jpg",
                "cb7b5334f49a5c7e54284f0146068e154428ffdb1ff29bc297a12bbb732f3184.jpg",
                "25058dda470f80ea5ede87f0757ac4309568e1aa7caf4c7d275679036f2b0654.jpg",
                "fc05ff80a9f7692870b925863705fc697e5508e16ebf9048ab737845218c4d7e.jpg"]
        for idx in range(4):
            el.append({"type": "image", "src": f"assets/{imgs[idx]}", "x": 70+idx*270, "y": y, "width": 250, "height": 180})
            if idx == 0:
                y += 190

    add_slide(slides, el)

# ========== 填空题 ==========
fb_data = [
    ("13", "点P到x轴的距离是2，到y轴的距离是3，且在y轴的左侧，则点P的坐标是", None),
    ("14", "如图，矩形ABCD的顶点A、B在数轴上，CD=6，点A对应的数为 -1，则点B所对应的为",
     "42829149c1b4b7d648261afff8b953313b06c6a35403396492ff61a425d99717.jpg"),
    ("15", "已知点 $(-4,y_1)$，$(2,y_2)$ 在直线 $y=-\\frac{1}{2}x+2$ 上，则 $y_1$  ____  $y_2$（填“＞”“＜”或“＝”）", None),
    ("16", "如图1，平行四边形ABCD中，$\\angle D=150^{\\circ}$，两动点M、N同时从点A出发，点M在边AB上以2cm/s的速度匀速运动，点N沿A-D-C-B的路径匀速运动。$\\triangle AMN$的面积$S(cm^2)$与点N的运动时间$t(s)$的关系如图2所示，已知AB=4cm。\n(1) N点的运动速度是____cm/s\n(2) c处的数值等于____",
     "97eb3328e3a75ead90edea616b495558706a8aa3319e12aec86984eaac9683c0.jpg"),
]

for qnum, stem, qimg in fb_data:
    el, y = [], 54
    el.append(text(f"填空题 第{qnum}题", y, 28, True, "#1f4e79"))
    y += 60
    el.append(text(stem, y, 24, False, "#222222", 1120, 80))
    y += 90

    if qimg:
        el.append(img(f"assets/{qimg}", y, 650, 360))
        y += 370
    if qnum == "16":
        el.append(img("assets/221b815ed110dfb01eddb7674be7aa7376dc6a6da1636e0ae055f25a5bb0fbd4.jpg", y, 650, 360))
    add_slide(slides, el)

# ========== 解答题 ==========
sa_data = [
    ("17", "一次函数图象经过(3,1)，(2,0)两点。\n(1) 求这个一次函数的解析式；\n(2) 求当 x=6 时，y 的值。", None),
    ("18", "(1) 如图1，在 $\\triangle ABC$ 中，D、E分别是AC、BC的中点，则线段DE与边AB的数量关系是____，位置关系是____；\n(2) 拓展应用：如图2，在ABCD中，连接AC并延长至点E，连接DE并延长至点F，使得EF=DE，连接BF。求证：AE//BF。",
     ["57d129a16f12904d47b4653ee2421ee88c416f2ff7af7373798a767f691bf772.jpg",
      "e11a9af5eef4aac00ce45ce4fb317935eed3bce56b43843548c22ae53e9397d2.jpg"]),
    ("19", "图1是某房子的房顶，图2是其示意图，其中AB=DE，BC=EF，AD=CF，且 $\\angle ABC = \\angle DEF$。试判断四边形ADFC的形状，并说明理由。",
     ["09d88953c9379657f2ff71fb29eebae7f5dbc0d3b05f8e36c986ec314926393a.jpg",
      "1df59253629f22be23e2432e4e7039a920b9d55926bf4519515e0ccca6a1df63.jpg"]),
    ("20", "如图，矩形ABCD的对角线AC、BD相交于点O，BE//AC，AE//BD。\n(1) 求证：四边形AOBE是菱形；\n(2) 若 $\\angle AOB=60^{\\circ}$，AC=12，求菱形AOBE的面积。",
     "76abf02d8c4d3a2a630162af3eff22ad137cfd495d8dc7884a531a422546669a.jpg"),
    ("21", "如图，直线 $l_1$ 的解析式为 $y=x+2$，$l_1$ 和 $l_2$ 相交于点A，$l_1$ 与x轴交于点B，与y轴交于点D，$l_2$ 与x轴交于点C(4,0)，与y轴交于点E(0,4)。\n(1) 求直线 $l_2$ 的解析式；\n(2) 求 $\\triangle ABC$ 的面积。",
     "ac722a524254de2e811239acd014977a28a73ea9c4f1e1cfeecffc3900654d2f.jpg"),
    ("22", "将一张长方形的纸对折，可得到一条折痕，继续对折，对折时每条折痕与上次的折痕保持平行。连续对折3次后，可以得到7条折痕。\n(1) 对折4次可以得到____条折痕；\n(2) 写出折痕的条数y与对折次数x之间的函数关系式；\n(3) 求出对折10次后的折痕条数。",
     "ab2b86c0cd23a80e3c022d83721458c29bd560a47d1262316e3ee2ac123bec44.jpg"),
    ("23", "在平面直角坐标系中，O为原点，$\\triangle ABC$ 顶点坐标分别为A(0,2)、B(-2,0)、C(4,0)。将点B右平移7个单位，再向上平移4个单位，得到对应点D。\n(1) 直接写出点D的坐标____；\n(2) 求 $\\triangle ACD$ 的面积；\n(3) 点P(m,3)是一个动点，若 $\\triangle APO$ 的面积等于 $\\triangle ACO$ 的面积，请求出点P坐标。",
     "c5833bded8d306ad284e9b7aed500958869240d3fc82be8dc4775aaeee90d268.jpg"),
    ("24", "小强是校学生会体育部部长，他想了解同学们更喜欢什么球类运动。全校每班随机选取学生调查：A.篮球 B.足球 C.排球 D.乒乓球 E.羽毛球 F.其他\n统计表：篮球69人，足球m人，排球27人，乒乓球n人，羽毛球36人，其他9人\n(1) 求m=____，n=____；\n(2) 羽毛球所对应扇形的圆心角等于____°；\n(3) 请你根据调查结果给小强部长提出合理化的建议。",
     "8bbbdcd7e21ef0221c7db0756c9d8ea314ea7dc665f09e70227495716c554a7e.jpg"),
]

for qnum, stem, qimg in sa_data:
    el, y = [], 54
    el.append(text(f"解答题 第{qnum}题", y, 28, True, "#1f4e79"))
    y += 60
    el.append(text(stem, y, 24, False, "#222222", 1120, 100))
    y += 110

    if isinstance(qimg, list):
        # two images side by side
        for i, fn in enumerate(qimg):
            el.append({"type": "image", "src": f"assets/{fn}", "x": 70+i*540, "y": y, "width": 500, "height": 300})
    elif qimg:
        el.append(img(f"assets/{qimg}", y, 650, 360))

    add_slide(slides, el)

# ========== 写入 ==========
doc = {"slides": slides}
json_str = json.dumps(doc, ensure_ascii=False, indent=2)
out_path = r"C:\MRE\outputs\exam-json\24-25期末试卷.json"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(json_str)

print(f"OK: {out_path}")
print(f"Slides: {len(slides)}")
img_count = sum(1 for s in slides for e in s["elements"] if e["type"] == "image")
print(f"Images: {img_count}")
