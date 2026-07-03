"""生成正式课件图表：扇形图、条形图、折线图、直方图"""

import matplotlib

matplotlib.use("Agg")
import os

import matplotlib.pyplot as plt
import numpy as np

os.makedirs("support/easinote/MRE-Plugin/assets", exist_ok=True)

# ── 中文字体 ──
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DPI = 120
FIGSIZE = (10, 5.6)
BG = "#FAFAFA"
TITLE_COLOR = "#1a3a5c"

# ═════════════════════════════════════════
# 1. 扇形统计图 — 最喜欢的科目
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 6), facecolor=BG)
ax.set_facecolor(BG)
labels = ["数学", "语文", "英语", "物理", "其他"]
sizes = [35, 25, 20, 12, 8]
colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
explode = (0.05, 0, 0, 0, 0)
wedges, texts, autotexts = ax.pie(
    sizes,
    explode=explode,
    labels=labels,
    colors=colors,
    autopct="%1.1f%%",
    startangle=90,
    textprops={"fontsize": 14},
)
for at in autotexts:
    at.set_fontsize(12)
    at.set_fontweight("bold")
ax.set_title(
    "八年级学生最喜欢的科目调查",
    fontsize=18,
    fontweight="bold",
    color=TITLE_COLOR,
    pad=20,
)
fig.tight_layout()
fig.savefig(
    "support/easinote/MRE-Plugin/assets/img_01.png",
    dpi=DPI,
    bbox_inches="tight",
    facecolor=BG,
)
plt.close()

# ═════════════════════════════════════════
# 2. 条形统计图 — 各科目喜爱人数
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG)
ax.set_facecolor(BG)
categories = ["数学", "语文", "英语", "物理", "历史", "道法"]
values = [42, 30, 24, 15, 18, 20]
bars = ax.bar(
    categories,
    values,
    color=["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"],
    edgecolor="white",
    linewidth=1.5,
)
for bar, v in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        str(v),
        ha="center",
        va="bottom",
        fontsize=13,
        fontweight="bold",
        color="#333",
    )
ax.set_title(
    "八年级学生最喜爱的科目人数统计",
    fontsize=18,
    fontweight="bold",
    color=TITLE_COLOR,
    pad=15,
)
ax.set_ylabel("人数", fontsize=13)
ax.set_ylim(0, 52)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(labelsize=12)
fig.tight_layout()
fig.savefig(
    "support/easinote/MRE-Plugin/assets/img_04.png",
    dpi=DPI,
    bbox_inches="tight",
    facecolor=BG,
)
plt.close()

# ═════════════════════════════════════════
# 3. 折线统计图 — 各科成绩趋势
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG)
ax.set_facecolor(BG)
months = ["第1周", "第2周", "第3周", "第4周", "第5周", "第6周"]
math_scores = [78, 80, 76, 82, 85, 84]
chinese_scores = [72, 74, 73, 75, 72, 77]
ax.plot(
    months,
    math_scores,
    "o-",
    color="#3498db",
    linewidth=2.5,
    markersize=8,
    label="数学",
)
ax.plot(
    months,
    chinese_scores,
    "s-",
    color="#e74c3c",
    linewidth=2.5,
    markersize=8,
    label="语文",
)
for i, (m, c) in enumerate(zip(math_scores, chinese_scores)):
    ax.annotate(
        str(m),
        (months[i], m),
        textcoords="offset points",
        xytext=(0, 12),
        ha="center",
        fontsize=11,
        color="#3498db",
        fontweight="bold",
    )
    ax.annotate(
        str(c),
        (months[i], c),
        textcoords="offset points",
        xytext=(0, -18),
        ha="center",
        fontsize=11,
        color="#e74c3c",
        fontweight="bold",
    )
ax.set_title(
    "每周测验平均分变化趋势", fontsize=18, fontweight="bold", color=TITLE_COLOR, pad=15
)
ax.set_ylabel("平均分", fontsize=13)
ax.set_ylim(60, 95)
ax.legend(fontsize=12, loc="lower right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(labelsize=12)
fig.tight_layout()
fig.savefig(
    "support/easinote/MRE-Plugin/assets/img_05.png",
    dpi=DPI,
    bbox_inches="tight",
    facecolor=BG,
)
plt.close()

# ═════════════════════════════════════════
# 4. 频数分布直方图 — 身高分布
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG)
ax.set_facecolor(BG)
np.random.seed(42)
heights = np.random.normal(162, 8, 100)
bins = [140, 145, 150, 155, 160, 165, 170, 175, 180]
n, bins_out, patches = ax.hist(
    heights, bins=bins, color="#3498db", edgecolor="white", linewidth=1.5
)
bin_centers = 0.5 * (np.array(bins[:-1]) + np.array(bins[1:]))
for center, count in zip(bin_centers, n):
    if count > 0:
        ax.text(
            center,
            float(count) + 0.5,
            str(int(count)),
            ha="center",
            fontsize=12,
            fontweight="bold",
            color="#333",
        )
ax.set_title(
    "八年级某班身高频数分布直方图 (n=100)",
    fontsize=18,
    fontweight="bold",
    color=TITLE_COLOR,
    pad=15,
)
ax.set_xlabel("身高 / cm", fontsize=13)
ax.set_ylabel("频数", fontsize=13)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(labelsize=12)
fig.tight_layout()
fig.savefig(
    "support/easinote/MRE-Plugin/assets/img_02.png",
    dpi=DPI,
    bbox_inches="tight",
    facecolor=BG,
)
plt.close()

# ═════════════════════════════════════════
# 5. 频数分布直方图 — 步骤分解版
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG)
ax.set_facecolor(BG)
ax.hist(heights, bins=bins, color="#e67e22", edgecolor="white", linewidth=1.5)
for center, count in zip(bin_centers, n):
    if count > 0:
        ax.text(
            center,
            float(count) + 0.5,
            str(int(count)),
            ha="center",
            fontsize=12,
            fontweight="bold",
            color="#333",
        )
# 标注极差和组距
ax.annotate(
    "极差 = 最大 − 最小\n= 179 − 142 = 37 cm",
    xy=(171, 22),
    fontsize=12,
    bbox=dict(
        boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#f39c12", alpha=0.9
    ),
)
ax.annotate(
    "组距 = 5 cm\n组数 = 8",
    xy=(147, 18),
    fontsize=12,
    bbox=dict(
        boxstyle="round,pad=0.5", facecolor="#d4edda", edgecolor="#28a745", alpha=0.9
    ),
)
ax.set_title(
    "频数分布直方图画法步骤", fontsize=18, fontweight="bold", color=TITLE_COLOR, pad=15
)
ax.set_xlabel("身高 / cm", fontsize=13)
ax.set_ylabel("频数", fontsize=13)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(labelsize=12)
fig.tight_layout()
fig.savefig(
    "support/easinote/MRE-Plugin/assets/img_03.png",
    dpi=DPI,
    bbox_inches="tight",
    facecolor=BG,
)
plt.close()

print("✅ 5张正式统计图表已生成")
for f in sorted(os.listdir("support/easinote/MRE-Plugin/assets")):
    sz = os.path.getsize(f"support/easinote/MRE-Plugin/assets/{f}")
    print(f"  assets/{f}  ({sz:,} bytes)")
