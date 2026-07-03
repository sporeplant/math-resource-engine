# 教材原文拆解技能

## 1. Skill 定位

将 MinerU 转换的教材 Markdown 大文件按课时拆分为独立的教材原文文件，同时将 HTML 表格转换为 Markdown 原生格式。

拆分结果必须写入知识库 `knowledge/textbooks/ch{N}/`，作为后续教学设计、课件生成等任务的基础教材原文数据。

## 2. 输入要求

| 字段 | 说明 |
|------|------|
| 输入文件 | MinerU 输出的单章 Markdown 文件（含 `## 第X章` 标题） |
| 文件编码 | UTF-8 |

## 3. 输出要求

按以下规则输出文件，**必须输出到知识库 `knowledge/textbooks/ch{N}/`**（使用 `--outdir knowledge/textbooks`，工具自动创建 `ch{N}` 子目录）：

| 文件类型 | 命名规则 | 示例 |
|----------|----------|------|
| 课时文件 | `textbook-{章节}.{小节}-{课时号}.md` | `textbook-12.1-1.md` |
| 回顾与反思 | `textbook-{章号}.{续号}-review-{课时号}.md` | `textbook-12.6-review-1.md` |
| 数学活动 | `textbook-{章号}.{续号}-{活动名称}.md` | `textbook-12.6-橙汁与苹果汁的多少.md` |

> `{续号}` = 最大节号 + 1，如第12章小节到 12.5，则续号为 6，文件为 `textbook-12.6-review-1.md`。

每个输出文件必须写入 YAML front matter：

```yaml
---
content_type: textbook_original
textbook_version: JJ2022
semester: 8A
chapter_name: 平面直角坐标系
section_name: 位置的确定
lesson_id: 18.1.1
---
```

## 4. 处理步骤

### 步骤 1：HTML 表格转 Markdown

自动扫描文件中所有 `<table>` 标签，解析 `colspan`/`rowspan` 属性，展开为 Markdown 原生表格（`| --- |` 格式）。

### 步骤 2：章节结构分析

解析所有 `##` 标题行，识别：
- 章标题：`## 第X章 ...`
- 课时边界：`## X.Y ...（第N课时）`
- 回顾与反思：`## 第X章回顾与反思（第N课时）`
- 子标题（不拆分）：做一做、大家谈谈、观察与思考、练习、习题、A/B/C组、读一读、一起探究、法则、知识结构、总结与反思、注意事项、编号条目等

以结构化格式呈现课时分配表，并同时呈现每个输出文件将写入的 YAML 元信息，要求用户确认后再拆分。

### 步骤 3：元信息生成

- `content_type` 固定为 `textbook_original`，除非用户明确指定其他值
- `textbook_version` 默认 `JJ2022`
- `semester` 必须由用户提供，如 `8A`、`8B`、`9A`
- `chapter_name` 默认使用识别到的章标题，可由用户指定覆盖
- `section_name` 使用识别到的小节名称；回顾与反思写 `回顾与反思`；数学活动写活动名称
- `lesson_id` 标准课时写 `{章号}.{节号}.{课时号}`，如 `18.1.1`；回顾与反思写 `ch{章号}-review-{课时号}`；数学活动写 `ch{章号}-activity-{序号}`

### 步骤 4：按课时拆分

- 章引言自动归入第一个小节的第一个课时
- 每个课时对应一个独立文件
- 数学活动单独文件
- 回顾与反思拆分课时
- 图片路径自动转换为 CDN 格式 `https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/<hash>.jpg`（兼容 Markdown `![](...)` 和 HTML `<img>` 标签）

### 步骤 5：图片文件迁移（自动）

工具自动完成图片迁移：

1. 扫描输出文件中的 CDN 图片引用，提取哈希文件名
2. 从 MinerU 输入文件所在目录的 `images/` 子目录复制到 `knowledge/images/`
3. 已存在的跳过，不重复复制
4. 图片文件名为 SHA-256 哈希，内容决定文件名，不同章节引用同一图片时天然去重
5. 使用 `--no-copy-images` 可跳过此步骤

## 5. 章节结构呈现格式

```
============================================================
  第X章  章节名称
============================================================
  章节引言: 0~N 行 (将归入 X.1 第一课时)

  X.1 小节名称
    第一课时
    第二课时
  X.2 小节名称
    第一课时
  ...

  --- 数学活动 / 其他 ---
    活动名称

  --- 回顾与反思 ---
    第一课时
    第二课时

============================================================
  共 N 个课时 + M 个活动 + K 个复习课时
  输出文件: N+M+K 个
```

## 6. OCR 错误修正

MinerU 可能将 `12.5` 误识别为 `05`。若检测到课时号前缀数字小于章号，自动补全为 `{章号}.{前缀}`。

## 7. 禁止事项

- 禁止将子标题（做一做、练习、习题等）作为独立课时拆分
- 禁止遗漏章引言（必须归入第一课时）
- 禁止跳过用户确认直接拆分；如使用 `-y`，必须显式提供必要元信息（至少 `--semester`）
- 禁止修改教材原文内容（仅做格式转换和拆分）
- 禁止输出缺少 YAML front matter 的课时文件
- 禁止将输出文件保留在 MinerU 临时目录或非知识库位置；拆分结果必须通过 `--outdir knowledge/textbooks` 写入 `knowledge/textbooks/ch{N}/`
- 禁止使用 `--no-copy-images` 跳过图片迁移后再手动复制（应让工具自动完成）

## 8. 调用方式

```bash
python tools/split_textbook.py <MinerU文件路径> [--outdir <输出目录>] [--semester 8A] [-y]
```

| 参数 | 说明 |
|------|------|
| `input_file` | MinerU 输出的 Markdown 文件路径（必填） |
| `--outdir` | 输出目录（必须指向 `knowledge/textbooks`，如 `--outdir knowledge/textbooks`） |
| `--semester` | 学期标识，如 `8A`、`8B`、`9A`；`-y` 模式必填 |
| `--textbook-version` | 教材版本标识，默认 `JJ2022` |
| `--content-type` | 内容类型，默认 `textbook_original` |
| `--chapter-name` | 章名称覆盖值，默认使用识别到的章标题 |
| `--flat` | 平铺输出，不创建 `ch{N}/` 子目录（图片路径仍转换为 CDN 格式） |
| `--no-copy-images` | 跳过图片文件复制步骤 |
| `--git-add` | git add 输出文件和新增图片 |
| `-y` / `--yes` | 跳过确认，直接拆分（可选） |

## 9. 自检流程

- [ ] HTML 表格是否全部转换为 Markdown 原生格式
- [ ] 章节结构分析是否正确（课时数、活动数、复习课时数）
- [ ] 是否呈现并确认每个输出文件的 YAML 元信息
- [ ] `semester`、`textbook_version`、`chapter_name` 是否正确
- [ ] `section_name` 与 `lesson_id` 是否逐文件正确
- [ ] 用户是否已确认拆分方案和元信息
- [ ] 章引言是否归入第一课时文件
- [ ] 文件命名是否符合规则
- [ ] 子标题（做一做、练习等）未独立拆分
- [ ] 图片路径是否全部转换为 CDN 格式（非相对路径）
- [ ] 输出位置是否为 `knowledge/textbooks/ch{N}/`（非 MinerU 临时目录）
- [ ] MinerU `images/` 下的图片文件是否已复制到 `knowledge/images/`
- [ ] 是否运行验证器确认：`python tools/validate-textbook-split.py knowledge/textbooks/ch{N}/`
