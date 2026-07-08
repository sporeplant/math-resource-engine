# 练习册题库拆解技能

## 1. Skill 定位

将 MinerU 转换的练习册 Markdown 大文件按课时拆分为 `knowledge/workbooks/` 下的独立练习册题库文件。

本 Skill 只处理练习册题库原文，不处理教材原文。教材原文拆解仍使用 `skills/textbook-split/SKILL.md`。

## 2. 输入要求

| 字段 | 说明 |
|------|------|
| 输入文件 | MinerU 输出的单章练习册 Markdown 文件 |
| 文件编码 | UTF-8 |
| 典型结构 | `# 第X章 ...`，下设 `## X.Y 课时名(一)`、`## X.Y 课时名(二)`、`# 回顾与反思` 等 |

## 3. 输出要求

拆分结果必须写入 `knowledge/workbooks/`：

| 文件类型 | 命名规则 | 示例 |
|----------|----------|------|
| 单课时 | `workbook-{章节}.{小节}-{课时号}.md` | `workbook-12.1-1.md` |
| 单课时小节 | `workbook-{章节}.{小节}.md` | `workbook-12.4.md` |
| 回顾与反思 | `workbook-ch{章号}-review.md` | `workbook-ch12-review.md` |

课时号由标题中的 `(一)`、`(二)` 等自动识别；没有课时号的小节不追加课时后缀。

## 4. 处理步骤

### 步骤 1：章节结构分析

识别以下边界：

- 章标题：`# 第X章 ...`
- 课时边界：`## X.Y ...`，如 `## 12.1 分式(一)`
- 回顾与反思：`# 回顾与反思` 或 `## 回顾与反思`

以下栏目标题必须保留在当前课时内，不得拆分成独立文件：

- 知识点拨
- 夯实基础
- 数学思考
- 解决问题
- 开阔视野
- 选择题、填空题、解答题等题型标题
- 带题号的标题，如 `## 6. 先阅读材料，再回答问题。`

### 步骤 2：结构预览

拆分前应呈现：

- 识别到的章标题
- 每个输出文件名
- 每个输出文件对应的原始标题
- 图片数量

### 步骤 3：按课时拆分

- 每个课时对应一个独立文件
- 回顾与反思单独输出
- 正文内容只做标题层级、图片路径和必要空行规范化，不改写题目、选项、公式和题号
- 输出文件首行使用一级标题，如 `# 12.1 分式(一)`

### 步骤 4：图片迁移

工具自动完成图片迁移：

1. 扫描输出文件中的 Markdown 图片引用
2. 从 MinerU 输入文件所在目录的 `images/` 子目录复制到 `knowledge/images/`
3. 已存在的图片跳过
4. 输出 Markdown 中图片路径统一改为 CDN 格式：
   `https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/<hash>.jpg`

## 5. 禁止事项

- 禁止使用 `skills/textbook-split/SKILL.md` 处理练习册题库大文件
- 禁止输出到 `knowledge/textbooks/`
- 禁止把“知识点拨”“夯实基础”“数学思考”“解决问题”等栏目拆成独立文件
- 禁止改写题干、选项、公式、题号和栏目顺序
- 禁止遗漏图片迁移
- 禁止覆盖已有 `knowledge/workbooks/` 文件，除非用户明确允许

## 6. 调用方式

```bash
python tools/split_workbook.py <MinerU文件路径> [--outdir knowledge/workbooks] [-y]
```

| 参数 | 说明 |
|------|------|
| `input_file` | MinerU 输出的练习册 Markdown 文件路径 |
| `--outdir` | 输出目录，默认 `knowledge/workbooks` |
| `--chapter` | 手动指定章号，如 `12` |
| `--overwrite` | 允许覆盖已存在的输出文件 |
| `--no-copy-images` | 跳过图片复制 |
| `-y` / `--yes` | 跳过确认，直接拆分 |

## 7. 自检流程

- [ ] 是否正确识别练习册而非教材原文
- [ ] 是否识别所有课时标题
- [ ] 是否识别回顾与反思
- [ ] 是否未将栏目标题拆成独立文件
- [ ] 输出文件名是否符合 `workbook-*` 命名规则
- [ ] 是否写入 `knowledge/workbooks/`
- [ ] 图片路径是否转换为 CDN
- [ ] 图片文件是否复制到 `knowledge/images/`
- [ ] 是否运行验证器：`python tools/validate-workbook-split.py knowledge/workbooks/workbook-12.1-1.md`
