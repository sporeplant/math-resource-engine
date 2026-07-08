#!/usr/bin/env python3
"""
生成希沃白板课件 (lesson.json + assets/)。
每道题一页，左文右图排版。不包含解答过程。
"""

import json
import os
import shutil
import sys

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR = os.path.join("outputs", "24-25期末试卷课件")
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")
IMAGE_SOURCE_DIR = os.path.join("knowledge", "images")

os.makedirs(ASSETS_DIR, exist_ok=True)

# ============================================================
# 工具函数：复制图片
# ============================================================
def copy_image(hash_name: str) -> str:
    """从 knowledge/images/ 复制图片到 assets/，返回相对路径。"""
    src = os.path.join(IMAGE_SOURCE_DIR, hash_name)
    if os.path.exists(src):
        dst = os.path.join(ASSETS_DIR, hash_name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        return hash_name
    else:
        print(f"  [警告] 图片不存在: {src}")
        return ""


# ============================================================
# 工具函数：创建元素
# ============================================================
def make_text(text: str, x: float, y: float, w: float, h: float,
              font_size: float = 22, bold: bool = False,
              color: str = "#222222", align: str = "left",
              font_family: str = "") -> dict:
    el = {
        "type": "text",
        "text": text,
        "x": x, "y": y,
        "width": w, "height": h,
        "fontSize": font_size,
        "bold": bold,
        "color": color,
        "align": align,
    }
    if font_family:
        el["fontFamily"] = font_family
    return el


def make_image(src: str, x: float, y: float, w: float, h: float) -> dict:
    return {
        "type": "image",
        "src": src,
        "x": x, "y": y,
        "width": w, "height": h,
    }


# ============================================================
# 页面数据
# ============================================================
# 页面尺寸：1920x1080
# 左侧文本区：x=60, y=80~100, width=780
# 右侧图片区：x=920, y=100, width=900

TEXT_X = 60
TEXT_W = 780
TITLE_Y = 50
TITLE_H = 60
CONTENT_Y = 130
CONTENT_H = 900
CONTENT_FS = 22
SMALL_FS = 20

IMG_X = 920
IMG_W = 920
IMG_Y0 = 100
IMG_H_LARGE = 880
IMG_H_MID = 420

slides = []
el_id = 0


def next_id(prefix="el"):
    global el_id
    el_id += 1
    return f"{prefix}_{el_id:03d}"


def make_slide(elements, slide_id=None):
    if slide_id is None:
        slide_id = f"slide_{len(slides) + 1:02d}"
    return {"id": slide_id, "elements": elements}



# ============================================================
# 第1题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第1题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("内角为 108° 的正多边形是\n\nA. 3\nB. 4\nC. 5\nD. 6",
              TEXT_X, CONTENT_Y, TEXT_W, 300, font_size=CONTENT_FS)
]))

# ============================================================
# 第2题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第2题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，边长为3的正方形OBCD的两边落在坐标轴正半轴上，点C的坐标是\n\n"
              "A. (3, -3)\nB. (-3, 3)\nC. (3, 3)\nD. (-3, -3)",
              TEXT_X, CONTENT_Y, TEXT_W, 400, font_size=CONTENT_FS),
    make_image(copy_image("e827819294a1ab9237bf2fac7d258e9db1beab5661afb22c986f163ebf249e3b.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第3题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第3题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，菱形ABCD中，∠D = 150°，则 ∠1 =\n\n"
              "A. 30°\nB. 25°\nC. 20°\nD. 15°",
              TEXT_X, CONTENT_Y, TEXT_W, 400, font_size=CONTENT_FS),
    make_image(copy_image("f0a805e835ca7e5dd4c94fedb318ceb0c933fceb1cd5b3896bc7554dba09c694.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第4题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第4题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，在矩形ABCD中，对角线AC, BD相交于点O，∠ABD = 60°，AB = 2，则AC的长为\n\n"
              "A. 6\nB. 5\nC. 4\nD. 3",
              TEXT_X, CONTENT_Y, TEXT_W, 400, font_size=CONTENT_FS),
    make_image(copy_image("be18c603b9b5831ecbd2ebfa85ad8d5f8d319051f47e2442050fe416009a2b27.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第5题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第5题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，平地上A、B两点被池塘隔开，测量员在岸边选一点C，"
              "并分别找到AC和BC的中点D、E，测量得DE = 16米，则A、B两点间的距离为\n\n"
              "A. 30米\nB. 32米\nC. 36米\nD. 48米",
              TEXT_X, CONTENT_Y, TEXT_W, 450, font_size=CONTENT_FS),
    make_image(copy_image("1ed08c8554a06a2f2932041715c06dd0aa022c22c82a952bc410f76ab107301b.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第6题 (4张图)
# ============================================================
q6_hashes = [
    "01fa17df5b950a5f85caa1ed7e4b69ee96f5ce9ea013e7bc63962f0e8b5ca9c4.jpg",
    "7d4f793370f315b42cbd6461e1bb512c49d712235659ee375de0753333f91024.jpg",
    "2d9aa8ed7135a2116845532196adee02a0ed2eac949980b97a151b9d634e0355.jpg",
    "a188d6484c2e624f9eab9f8e48539cb63a7355568cedfa1fe6ab57c28630ab75.jpg",
]
q6_elements = [
    make_text("选择题（第6题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，在每个四边形上所做的标记中，线段上的划记数量相同的表示线段相等，"
              "角的标记弧线数量相同的表示角相等，则下列一定为平行四边形的有\n\n"
              "A. 1个\nB. 2个\nC. 3个\nD. 4个",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=SMALL_FS),
]
# 2x2 grid of images on the right
positions_2x2 = [
    (IMG_X, IMG_Y0 + 0, 450, 420),
    (IMG_X + 470, IMG_Y0 + 0, 450, 420),
    (IMG_X, IMG_Y0 + 440, 450, 420),
    (IMG_X + 470, IMG_Y0 + 440, 450, 420),
]
for i, h in enumerate(q6_hashes):
    src = copy_image(h)
    if src:
        x, y, w, ht = positions_2x2[i]
        q6_elements.append(make_image(src, x, y, w, ht))
slides.append(make_slide(q6_elements))

# ============================================================
# 第7题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第7题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，在平行四边形ABCD中，E是边CD上一点，将△ADE沿AE折叠至△AD'E处，"
              "AD'与CE交于点F，若∠B = 52°，∠DAE = 20°，则∠FED'的度数为\n\n"
              "A. 40°\nB. 36°\nC. 50°\nD. 45°",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=CONTENT_FS),
    make_image(copy_image("fd63c31d9ad0962fe101830173fca617aad3c0695fe986eddce2b5bf169fbd1f.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第8题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第8题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，两条直线的交点坐标(-2,3)可以看作两个二元一次方程的公共解，"
              "其中一个方程是 x + y = 1，则另一个方程是\n\n"
              "A. 2x - y = 1\nB. 2x + y = -1\nC. 2x + y = 1\nD. 3x - y = 1",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=CONTENT_FS),
    make_image(copy_image("8b0eb14e5887a4540a0ac3d592bd68d654c2bd337ffc958925c08166990bb7e1.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第9题 (4张选项图)
# ============================================================
q9_hashes = [
    "73e85b84ef371969bb74bf6aebf48fa9a5415e3af45f88e8aba98d10794d088a.jpg",
    "bf2ea3ed2cc0280880ae15dda714f0bd38a8e0b0c9b7051462d334cab0c33bd7.jpg",
    "88c1c7420d9fe5134ccb79552d5d6574209f7e150041207339b2d10f8bba9f38.jpg",
    "fa4af7aee71aade9246782546eeb32a67a41871f8c310edc57f5e882c0360696.jpg",
]
q9_elements = [
    make_text("选择题（第9题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("\"漏壶\"是一种古代计时器，在它内部盛一定量的水，水从壶下的小孔漏出。"
              "壶内壁有刻度，人们根据壶中水面的位置计算时间。用x表示漏水时间，"
              "y表示壶底到水面的高度。不考虑水量变化对压力的影响，"
              "下列图象最适合表示y与x对应关系的是\n\n"
              "A.            B.\nC.            D.",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=SMALL_FS),
]
# 4 images in 2x2 grid
for i, h in enumerate(q9_hashes):
    src = copy_image(h)
    if src:
        x, y, w, ht = positions_2x2[i]
        q9_elements.append(make_image(src, x, y, w, ht))
slides.append(make_slide(q9_elements))

# ============================================================
# 第10题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第10题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("下列有关一次函数 y = -3x + 2 的说法中，错误的是\n\n"
              "A. 当x值增大时，y的值随着x增大而减小\n"
              "B. 函数图象与y轴的交点坐标为(0,2)\n"
              "C. 函数图象经过第一、二、四象限\n"
              "D. 图象经过点(1,5)",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=CONTENT_FS),
]))

# ============================================================
# 第11题 (4张图)
# ============================================================
q11_hashes = [
    "86d42bd3f821a2ca6c85a2070271029032f264306da56331b73da809507cc201.jpg",
    "cb7b5334f49a5c7e54284f0146068e154428ffdb1ff29bc297a12bbb732f3184.jpg",
    "25058dda470f80ea5ede87f0757ac4309568e1aa7caf4c7d275679036f2b0654.jpg",
    "fc05ff80a9f7692870b925863705fc697e5508e16ebf9048ab737845218c4d7e.jpg",
]
q11_elements = [
    make_text("选择题（第11题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("下面三个问题中都有两个变量：\n\n"
              "① 货车匀速通过隧道，货车在隧道内的长度y与时间x\n"
              "② 王大爷从家出发匀速散步，离家的距离y与时间x\n"
              "③ 往圆柱形空杯中匀速倒水再倒出，杯中水的体积y与时间x\n\n"
              "其中，变量y与x之间的函数关系大致符合图4的是\n\n"
              "A. ①②\nB. ①③\nC. ②③\nD. ①②③",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=SMALL_FS),
]
for i, h in enumerate(q11_hashes):
    src = copy_image(h)
    if src:
        x, y, w, ht = positions_2x2[i]
        q11_elements.append(make_image(src, x, y, w, ht))
slides.append(make_slide(q11_elements))

# ============================================================
# 第12题
# ============================================================
slides.append(make_slide([
    make_text("选择题（第12题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("若一组数据共有100个，则通常分成\n\n"
              "A. 3~5组\nB. 5~12组\nC. 12~20组\nD. 20~25组",
              TEXT_X, CONTENT_Y, TEXT_W, 300, font_size=CONTENT_FS),
]))

# ============================================================
# 第13题
# ============================================================
slides.append(make_slide([
    make_text("填空题（第13题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("点P到x轴的距离是2，到y轴的距离是3，且在y轴的左侧，则点P的坐标是 ______",
              TEXT_X, CONTENT_Y, TEXT_W, 200, font_size=CONTENT_FS),
]))

# ============================================================
# 第14题
# ============================================================
slides.append(make_slide([
    make_text("填空题（第14题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，矩形ABCD的顶点A, B在数轴上，CD = 6，点A对应的数为 -1，则点B所对应的为 ______",
              TEXT_X, CONTENT_Y, TEXT_W, 400, font_size=CONTENT_FS),
    make_image(copy_image("42829149c1b4b7d648261afff8b953313b06c6a35403396492ff61a425d99717.jpg"),
               IMG_X, IMG_Y0, 800, 500)
]))

# ============================================================
# 第15题
# ============================================================
slides.append(make_slide([
    make_text("填空题（第15题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("已知点(-4, y₁)，(2, y₂)在直线 y = -½x + 2 上，则 y₁ ___ y₂（填\">\"\"<\"或\"=\"）",
              TEXT_X, CONTENT_Y, TEXT_W, 200, font_size=CONTENT_FS),
]))

# ============================================================
# 第16题 (2张图)
# ============================================================
q16_hashes = [
    "97eb3328e3a75ead90edea616b495558706a8aa3319e12aec86984eaac9683c0.jpg",
    "221b815ed110dfb01eddb7674be7aa7376dc6a6da1636e0ae055f25a5bb0fbd4.jpg",
]
q16_elements = [
    make_text("填空题（第16题）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("平行四边形ABCD中，∠D = 150°，两动点M, N同时从点A出发，\n"
              "点M在边AB上以 2cm/s 的速度匀速运动，到达点B时停止，\n"
              "点N沿 A-D-C-B 的路径匀速运动，到达点B时停止。\n"
              "△AMN的面积S(cm²)与点N的运动时间t(s)的关系如图2所示，\n"
              "已知 AB = 4cm\n\n"
              "(1) N点的运动速度是 ____ cm/s;\n"
              "(2) c处的数值等于 ____",
              TEXT_X, CONTENT_Y, TEXT_W, 550, font_size=SMALL_FS),
]
# 2 images stacked vertically on the right
for i, h in enumerate(q16_hashes):
    src = copy_image(h)
    if src:
        q16_elements.append(make_image(
            src, IMG_X, IMG_Y0 + i * 440, IMG_W, 400))
slides.append(make_slide(q16_elements))

# ============================================================
# 第17题
# ============================================================
slides.append(make_slide([
    make_text("解答题（第17题，6分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("一次函数图象经过(3,1)，(2,0)两点。\n\n"
              "(1) 求这个一次函数的解析式;\n\n"
              "(2) 求当 x = 6 时，y 的值。",
              TEXT_X, CONTENT_Y, TEXT_W, 400, font_size=CONTENT_FS),
]))

# ============================================================
# 第18题 (2张图)
# ============================================================
q18_hashes = [
    "57d129a16f12904d47b4653ee2421ee88c416f2ff7af7373798a767f691bf772.jpg",
    "e11a9af5eef4aac00ce45ce4fb317935eed3bce56b43843548c22ae53e9397d2.jpg",
]
q18_elements = [
    make_text("解答题（第18题，6分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("(1) 如图1，在△ABC中，D, E分别是AC, BC的中点，\n"
              "则线段DE与边AB的数量关系是 ______，位置关系是 ______;\n\n"
              "(2) 拓展应用：如图2，在ABCD中，连接AC并延长至点E，\n"
              "连接DE并延长至点F，使得EF = DE，连接BF。\n"
              "求证：AE // BF。",
              TEXT_X, CONTENT_Y, TEXT_W, 550, font_size=SMALL_FS),
]
for i, h in enumerate(q18_hashes):
    src = copy_image(h)
    if src:
        q18_elements.append(make_image(
            src, IMG_X, IMG_Y0 + i * 440, IMG_W, 400))
slides.append(make_slide(q18_elements))

# ============================================================
# 第19题 (2张图)
# ============================================================
q19_hashes = [
    "09d88953c9379657f2ff71fb29eebae7f5dbc0d3b05f8e36c986ec314926393a.jpg",
    "1df59253629f22be23e2432e4e7039a920b9d55926bf4519515e0ccca6a1df63.jpg",
]
q19_elements = [
    make_text("解答题（第19题，6分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("图1是某房子的房顶，图2是其示意图，其中AB = DE, BC = EF, "
              "AD = CF，且∠ABC = ∠DEF。\n\n"
              "试判断四边形ADFC的形状，并说明理由。",
              TEXT_X, CONTENT_Y, TEXT_W, 400, font_size=CONTENT_FS),
]
for i, h in enumerate(q19_hashes):
    src = copy_image(h)
    if src:
        q19_elements.append(make_image(
            src, IMG_X, IMG_Y0 + i * 440, IMG_W, 400))
slides.append(make_slide(q19_elements))

# ============================================================
# 第20题
# ============================================================
slides.append(make_slide([
    make_text("解答题（第20题，8分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，矩形ABCD的对角线AC，BD相交于点O，BE // AC，AE // BD。\n\n"
              "(1) 求证：四边形AOBE是菱形;\n\n"
              "(2) 若∠AOB = 60°，AC = 12，求菱形AOBE的面积。",
              TEXT_X, CONTENT_Y, TEXT_W, 500, font_size=CONTENT_FS),
    make_image(copy_image("76abf02d8c4d3a2a630162af3eff22ad137cfd495d8dc7884a531a422546669a.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第21题
# ============================================================
slides.append(make_slide([
    make_text("解答题（第21题，8分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("如图，直线l₁的解析式为 y = x + 2，直线l₁和直线l₂相交于点A，\n"
              "直线l₁与x轴相交于点B，与y轴相交于点D，\n"
              "直线l₂与x轴相交于点C(4,0)，与y轴相交于点E(0,4)。\n\n"
              "(1) 求直线l₂的解析式;\n\n"
              "(2) 求△ABC的面积。",
              TEXT_X, CONTENT_Y, TEXT_W, 600, font_size=CONTENT_FS),
    make_image(copy_image("ac722a524254de2e811239acd014977a28a73ea9c4f1e1cfeecffc3900654d2f.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第22题
# ============================================================
slides.append(make_slide([
    make_text("解答题（第22题，8分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("将一张长方形的纸对折，如图①，可得到一条折痕，继续对折，\n"
              "对折时每条折痕与上次的折痕保持平行，如图②，\n"
              "连续对折3次后，可以得到7条折痕，如图③。\n\n"
              "回答下列问题：\n"
              "(1) 对折4次可以得到 ______ 条折痕;\n\n"
              "(2) 写出折痕的条数y与对折次数x之间的函数关系式;\n\n"
              "(3) 求出对折10次后的折痕条数。",
              TEXT_X, CONTENT_Y, TEXT_W, 650, font_size=SMALL_FS),
    make_image(copy_image("ab2b86c0cd23a80e3c022d83721458c29bd560a47d1262316e3ee2ac123bec44.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第23题
# ============================================================
slides.append(make_slide([
    make_text("解答题（第23题，10分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("在平面直角坐标系中，O为原点，△ABC的顶点坐标分别为\n"
              "A(0,2), B(-2,0), C(4,0)，\n"
              "将点B向右平移7个单位长度，再向上平移4个单位长度，得到对应点D。\n\n"
              "(1) 直接写出点D的坐标 ______;\n\n"
              "(2) 求△ACD的面积;\n\n"
              "(3) 点P(m,3)是一个动点，若△APO的面积等于△ACO的面积，\n"
              "请求出点P坐标。",
              TEXT_X, CONTENT_Y, TEXT_W, 700, font_size=SMALL_FS),
    make_image(copy_image("c5833bded8d306ad284e9b7aed500958869240d3fc82be8dc4775aaeee90d268.jpg"),
               IMG_X, IMG_Y0, IMG_W, IMG_H_LARGE)
]))

# ============================================================
# 第24题
# ============================================================
slides.append(make_slide([
    make_text("解答题（第24题，12分）", TEXT_X, TITLE_Y, TEXT_W, TITLE_H,
              font_size=28, bold=True, color="#1a4b8c"),
    make_text("小强是校学生会体育部部长，他想了解现在同学们更喜欢什么球类运动，"
              "以便学生会组织受欢迎的比赛。于是他设计了调查问卷，\n"
              "在全校每个班都随机选取了一定数量的学生进行调查。\n\n"
              "调查问卷：你最喜欢的球类运动是 ____（单选）\n"
              "A. 篮球  B. 足球  C. 排球  D. 乒乓球  E. 羽毛球  F. 其他\n\n"
              "小强根据统计数据制作的各活动小组人数分布情况的统计表和扇形统计图如下：\n\n"
              "表：篮球69人，足球m人，排球27人，乒乓球n人，羽毛球36人，其他9人\n\n"
              "(1) m = ____，n = ____;\n\n"
              "(2) 在扇形统计图中，羽毛球所对应扇形的圆心角等于 ____;\n\n"
              "(3) 请你根据调查结果，给小强部长简要提出合理化的建议。",
              TEXT_X, CONTENT_Y, TEXT_W, 750, font_size=SMALL_FS),
    make_image(copy_image("8bbbdcd7e21ef0221c7db0756c9d8ea314ea7dc665f09e70227495716c554a7e.jpg"),
               IMG_X, IMG_Y0, 850, 800)
]))

# ============================================================
# 输出 JSON
# ============================================================
lesson = {"slides": slides}
json_path = os.path.join(OUTPUT_DIR, "lesson.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)

print(f"✅ 课件生成完成！")
print(f"   路径: {OUTPUT_DIR}")
print(f"   页面数: {len(slides)}")
print(f"   JSON: lesson.json")
print(f"   图片: assets/ 目录")

# 统计图片
img_count = len([f for f in os.listdir(ASSETS_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))])
print(f"   共复制 {img_count} 张图片")
