# 周报模板

文件名：`YYYY-Www.md`（ISO 8601 周编号，如 `2026-W27.md`），放在 `NOTES_REPO\reports\`。
周编号用 ISO 规则：周一为周首、第 1 周含本年第一个周四。判断方法：该日期的 `isocalendar()` → `(年, 周号, 星期几)`，取 `年-W{:0>2}周号`。

**风格**：工作汇报体为主（给导师/团队看），末尾附 1-2 条成长亮点（给自己看）。客观陈述产出，不凑字数、不流水账。

## frontmatter

```yaml
---
week: 2026-W27
period: 2026-07-06 ~ 2026-07-12     # 本周一 ~ 今天（或本周日）
technologies: [Docker, WSL2, pydantic]  # 本周各天 technologies 的并集
items_done: 5                          # "本周完成"条目数
problems_solved: 4                     # 本周各天 mistakes_resolved 之和
problems_open: 1                       # 进行中/未解决（各天 mistakes_total-resolved 之和 + 正文显式未完事项）
generated: 2026-07-12
tags: [type/report-weekly]          # Obsidian/Dataview 类型标签
---
```

## 正文结构

```markdown
# 实习周报 · 2026-W27（07.06–07.12）

> 本周涉及技术 N · 完成 X 项 · 🐛 攻克 Y 个 · 进行中 Z

## 一、本周完成
- [07.06] ……（客观陈述：做了什么 / 产出，带日期；来自各天"今天学到了/做过了"与已解决踩坑）

## 二、进行中
- ……（跨天重复出现的技术或问题；本周开了头还没收尾的事）

## 三、卡点 / 需要支持
- ……（未解决的踩坑 + 环境/权限/工具链类；明确写出"需要导师或团队帮什么"）

## 四、下周计划
- [ ] ……（各天"明天可以试试"去重聚合 + 技能树缺口，3-5 条）

## 五、本周成长亮点（1-2 条，可选）
- ……（给自己看：新触发的徽章 / struggle 高的天 / 最大收获）

<!-- user-notes -->
（手写补充区，重生成不覆盖）
<!-- /user-notes -->

---
导师签名：　　　　　日期：

🤖 由 /trace weekly 从本周 daily notes 生成
```

## 字段映射（daily note → 周报）

| 周报 section | 来自 daily note |
|---|---|
| 一、本周完成 | 「今天学到了/做过了」+ 已解决踩坑（mistakes_resolved）|
| 二、进行中 | 跨天重复出现的技术/问题（出现 ≥2 天）|
| 三、卡点/需要支持 | 未解决踩坑（mistakes_total − mistakes_resolved）+ 环境配置类 |
| 四、下周计划 | 各天「明天可以试试」聚合 + 技能树缺口（只出现 1 次的技术）|
| 五、成长亮点 | 新徽章 / struggle=high 的天 / summary |

frontmatter 的 technologies/problems_solved/problems_open 由读完正文后汇总填。

## 重生成规则

同一周重复触发 `/trace weekly` → **覆盖**正文（周报是状态快照，随 daily note 增多重新组织），但 `<!-- user-notes -->` 区**原样保留**。
若已有同周周报，读出其 `<!-- user-notes -->` 区，写回新文件。
