---
name: trace
description: 把 Claude Code 会话整理成结构化的每日实习学习笔记 + 游戏化成长轨迹。四种用法——(1)用户说"记一下"/"这是个坑"/"mark this"等标记意图时，把该学习点追加到 notes/.today-marks.md 暂存，不写笔记；(2)用户输入 /trace 或明确要"整理今天的学习/生成学习笔记"时，分析本次会话提取技术/问题/踩坑/概念，交互式问反思，关联历史笔记，写/合并 notes/YYYY-MM-DD.md，跑 aggregate.py 更新成长轨迹，并给明天建议与间隔复习；(3)用户输入 /trace weekly 或"生成周报"/"出本周周报"/"这周的汇报"时，聚合本周 daily notes 生成工作汇报体周报 reports/YYYY-Www.md 并跑 aggregate；(4)用户输入 /trace daily 或"生成日报"/"出今天的工作汇报"时，把当天 daily note 转成正式书面语工作日报 reports/YYYY-MM-DD.md（不跑 aggregate）。仅当用户明确表达这些意图时使用，不要在普通对话里主动打断。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# 拾迹 Trace — 实习学习笔记

把当前 Claude Code 会话整理成一篇**结构化每日学习笔记**，并维护一个游戏化的**成长轨迹**。
**本会话的对话就在你的上下文里**——直接分析它，不读 JSONL、不调外部模型。

## 配置（换路径只改这里）

- 笔记仓库根目录 `NOTES_REPO` = `<你的笔记仓库>(如 shiji)`
- 每日笔记：`NOTES_REPO\notes\YYYY-MM-DD.md`
- 成长轨迹：`NOTES_REPO\notes\README.md`（由 aggregate.py 重算）
- Obsidian 索引：`NOTES_REPO\notes\INDEX.md`（Dataview 实时查询页，手动维护，aggregate 不碰它）
- 当天临时标记：`NOTES_REPO\notes\.today-marks.md`
- 周报：`NOTES_REPO\reports\YYYY-Www.md`（ISO 8601 周编号，如 `2026-W27.md`）
- 日报：`NOTES_REPO\reports\YYYY-MM-DD.md`（与周报同目录，按天）
- 聚合脚本：`trace\scripts\aggregate.py`

## 先判断用哪种模式

- 意图是**标记单条**（"记一下这个"、"这是个坑"、"mark this"、"这个值得记"）→ **模式 1（标记）**
- 意图是**出周报**（`/trace weekly`、`/trace 周报`、"生成周报"、"出本周周报"、"这周的汇报"）→ **模式 3（周报）**
- 意图是**出日报**（`/trace daily`、`/trace 日报`、"生成日报"、"出今天的工作汇报"、"今日工作汇报"）→ **模式 4（日报）**
- 否则（`/trace`、"整理今天的学习"、"生成今天的学习笔记"、"记一下今天的学习"）→ **模式 2（完整）**

---

## 模式 1 · 标记（轻量）

1. 把用户要记的内容提炼成一行（学习点 / 踩坑）。
2. 追加到 `NOTES_REPO\notes\.today-marks.md`（没有就创建），每行格式：
   `- [学习] 内容` 或 `- [踩坑] 内容`
3. 简短确认一句（如"已记下，`/trace` 时会一起整理进今天的笔记"），然后**结束**。不写笔记、不跑 aggregate。

---

## 模式 2 · 完整 `/trace`

**动手前先 Read 这两个参考文件**（按需）：
- `trace\references\extraction-guide.md` — 提取规则
- `trace\references\note-template.md` — 笔记格式
- `trace\references\badges-rules.md` — 徽章/技能/连击规则

按以下顺序执行：

### 步骤 1 · 分析本次会话
用上下文里的对话，按 extraction-guide 提取：技术/工具（带 confidence）、问过的问题、踩坑（问题+根因+是否解决，**最重要**）、理解的概念、一句话总结、挣扎度。**只抽真实发生的，禁止臆造。** 若 `NOTES_REPO\notes\.today-marks.md` 存在，读出来一并纳入今天的踩坑/学习。同时判断今天是否**跨多个不相关领域**（见 extraction-guide「领域/主题识别」）——是则用主题分区形态（note-template 形态 B），frontmatter 的 `domains` 记录各领域名。

### 步骤 2 · 交互式反思（仅当天首次）
若今天的笔记还不存在、或其"三段反思"区为空：在对话里问用户**最多 2 个**反思问题，如"今天最有收获的是哪件事？""如果重来会怎么做？"。用户可拒答（留空）。若今日笔记已有反思内容则**跳过**。

### 步骤 3 · 关联历史
Read `NOTES_REPO\notes\` 下过往笔记的 frontmatter（用 Grep 抓 `---` 块即可，别整篇读）。找出今天技术在过去的出现，准备一句"🔗 与过去的连接"。检测重复学习（同概念本周多次）→ 在对话里提示。

### 步骤 4 · 写入/合并今日笔记
路径 `NOTES_REPO\notes\YYYY-MM-DD.md`（YYYY-MM-DD = 今天本地日期，下同），格式照 note-template。
- **不存在** → 按 note-template 新建。
- **已存在**（同天多次 /trace）→ **合并**：frontmatter 的 technologies、**domains** 取并集、questions/mistakes_* 计数相加、sessions+1；正文按主题归并——本次会话属于已有主题就并入该块、属于新领域就新开一个 `## 📂 主题` 块（单主题天遇新领域则升级成主题分区形态 B）；**保留** `<!-- user-notes -->` 区原样不动。
- 步骤 2 反思答案写进"三段反思"，步骤 3 连接写进"🔗 与过去的连接"。
- **Obsidian 双链（仅 daily note）**：正文技术名用 `[[]]`（如 `[[Docker]]`）、关联历史用 `[[2026-06-30]]`；frontmatter 加 `tags: [type/daily]`。日报/周报（reports/）**保持纯文本、不用双链**——它们要 copy 进企业系统。

### 步骤 5 · 重算成长轨迹
运行 Bash（确认跑完且无报错）：
```
python "trace\scripts\aggregate.py" "<你的笔记仓库>(如 shiji)"
```
脚本读 `notes\*.md` 的 frontmatter，重写 `notes\README.md`（连击/技能条/徽章/热力图/攻克计数）。

### 步骤 6 · 给反馈
在对话里简短说明（也写进笔记对应 section）：
- **明天建议**（≤2 条）：基于今天"待深入" + 技能树缺口（出现过但没深入的技术）。写进笔记"📚 明天可以试试"。
- **该复习了**：把 3/7/14 天前学过、按间隔该复习的知识点抛给用户。写进笔记"🔁 该复习了"。
- 触发的新徽章（参考 badges-rules.md）。

---

## 模式 3 · 周报（`/trace weekly`）

把**本周**（本周一 → 今天）的 daily notes 汇总成一篇给导师看的工作汇报，直击"周报凑字数"痛点。
**动手前先 Read** `trace\references\report-template.md`。

1. **确定本周范围**：本周一 → 今天。周编号用 ISO 规则——该日期的 `isocalendar()` 返回 `(年, 周号, 星期)`，取 `年-W{周号:0>2d}`。目标文件 `NOTES_REPO\reports\YYYY-Www.md`。
2. **读本周 daily notes**：Glob `NOTES_REPO\notes\*.md`，筛出日期落在本周范围内的，逐篇 Read（frontmatter + 正文）。**若本周一篇都没有** → 告诉用户"本周还没有 daily note，先用 `/trace` 记录几天再来出周报"，**不写空文件，结束**。
3. **按 report-template 组织正文**：照模板「字段映射」表，从各天提炼「一、本周完成 / 二、进行中 / 三、卡点需要支持 / 四、下周计划 / 五、成长亮点」五段；客观陈述、带日期、不凑字数、不流水账。frontmatter 的 technologies 取各天并集，problems_solved / problems_open 按各天 mistakes 计数汇总。
4. **保留手写区**：若同周周报已存在，先读出其 `<!-- user-notes -->` 区内容，原样写回新文件。
5. **写文件** → `NOTES_REPO\reports\YYYY-Www.md`（UTF-8）。
6. **重算成长轨迹**：运行 Bash `python "trace\scripts\aggregate.py" "<你的笔记仓库>(如 shiji)"`（会把本周报列进 README 的"📋 最近周报"）。
7. **口播**：简短报告"本周完成 X 项 / 🐛 攻克 Y 个 / Z 个待支持"，并把**「卡点 / 需要支持」段重点提示**给用户——那是要找导师沟通的部分。

---

## 模式 4 · 日报（`/trace daily`）

把**当天**的 daily note 转成一份交给企业/导师的**正式工作日报**（正式书面语）。与 daily note（给自己看的学习/游戏化）分开——日报里**绝不出现** confidence / 徽章 / 挣扎度 / "踩坑" 等内部或口语表达。
**动手前先 Read** `trace\references\report-daily-template.md`（含书面语要求和转译示例）。

1. **读当天 daily note**：`NOTES_REPO\notes\YYYY-MM-DD.md`（YYYY-MM-DD = 今天）。**若不存在** → 提示"今天还没有 daily note，先用 `/trace` 记录今天再来出日报"，**不写空文件，结束**。
2. **按 report-daily-template 组织正文**：先照「字段映射」把 daily note 内容**转译成正式书面语**素材，再**默认生成 4 个版本**——分点版（全量结构化，默认推荐）、段落版（全量一段话，适合钉钉/飞书消息框）、**亮点要点版（只挑最有价值的 2-3 点高度概括，适合给领导/导师的重点汇报）**、简版（一句话，适合站会/群报）——放在同一文件里，用 `---` 分隔、每个标注适用场景，方便用户直接 copy 对应版本贴进企业管理系统。**严格遵守书面语要求**——用"完成/推进/梳理/对接/解决"，禁用"踩坑/搞懂/confidence/徽章/折腾"。若用户指定了单一风格（如"段落式日报"、"亮点日报"、`/trace daily 段落`、`/trace daily 亮点`），只出该版本。
3. **保留手写区**：若同天日报已存在，先读出其 `<!-- user-notes -->` 区内容，原样写回。
4. **写文件** → `NOTES_REPO\reports\YYYY-MM-DD.md`（UTF-8）。
5. **不跑 aggregate**（日报是每日交差快消品，不进成长轨迹 README；README 只索引周报）。
6. **口播**：简短说"日报已生成 `reports\YYYY-MM-DD.md`，请过目后提交"，并把**「需协调 / 存在问题」段重点提示**给用户——那是要找领导/同事沟通的部分。

---

## 边界
- 会话过长、上下文可能丢早期内容时：可读当前会话 JSONL 补全——路径模式 `~/.claude/projects\<编码后的cwd>\<sessionId>.jsonl`，sessionId 取自 `$CLAUDE_SESSION_ID`。
- 只处理 Claude Code 本会话；不碰 ChatGPT/Cursor。
- aggregate.py 失败时：保留已写的笔记，把错误如实告诉用户，别静默。
- 写文件用 UTF-8。
