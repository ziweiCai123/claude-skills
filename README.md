# Claude Skills Collection

四套自建的 Claude Code skill——把重复性工作流工程化成「方法论文件 + 参考资料库 + 确定性脚本」,让 agent 每次都按同一套纪律执行。**只是方法论,不含任何个人数据。**

## 安装到本地

每个目录是一个独立 skill。复制到 `~/.claude/skills/<name>/`(Windows: `%USERPROFILE%\.claude\skills\<name>\`),重启 Claude Code 即生效。

```
~/.claude/skills/
├── trace/    ← 学习笔记
├── trip/     ← 旅行规划
├── essay/    ← 留学文书(需自建 profile.md 个人信息池)
└── linkup/   ← 人物关系链
```

## Skills

### 📒 trace — 会话学习笔记
把 Claude Code 会话整理成结构化每日学习笔记 + 游戏化成长轨迹。四种模式:标记(「记一下」追加暂存)/ 完整笔记(分析会话→交互反思→关联历史→聚合)/ 周报(聚合 daily notes→工作汇报体)/ 日报(转正式书面语,四版本供 copy)。
- 设计要点:YAML frontmatter 作统计唯一数据源;`[[双链]]` 只进笔记不进日报(避免污染企业 IM);确定性聚合用纯标准库手写
- 配套开源项目:[shiji](https://github.com/ziweiCai123/shiji)(standalone 形态)

### 🗺 trip — 旅行行程规划
六阶段流程:需求收集 → 资料调研 → 数据包 → OR-Tools 多方案求解 → 七维指标量化 → 渲染(方案对比页+抗风险作战手册+美食打卡)。天气进目标函数(晴定景点雨天打折,溶洞夜市雨天加成)。
- 配套开源项目:[trip-planner](https://github.com/ziweiCai123/trip-planner)(求解引擎+渲染器)
- `references/` 内含数据包规范、风险卡模板、调研模板

### ✍️ essay — 留学申请文书
中英双语五阶段:信息收集 → 规划 → 起草 → 润色(系统化去 AI 腔)→ 迭代。另支持 Why School 联网调研、简历按地区风格改写、推荐信代拟。
- **需要自建 `profile.md` 个人信息池**(学校/成绩/项目等,本仓库不含);`references/` 含去 AI 腔规则、学科框架、地区差异、Why School 方法论

### 🔗 linkup — 人物关系链
六度分隔游戏:推理两个真实人物间的社会联系链(合作/校友/亲属/同事件…),每跳联网核实,输出可视化链条+置信度+来源。支持单向展开关系网、1-2 跳快判。
- `references/verification.md` 是核心:每跳必须搜索核实、置信度分级、失败要明说

## 设计原则(跨 skill 通用)

1. **frontmatter description 是激活入口** —— 加模式/触发词必须同步改它,否则自然语不触发(踩过的坑)
2. **数据与表现分离** —— 统计只读 frontmatter;人读正文;双链只在笔记层
3. **触发词宁多勿少** —— 用户说「出周报」「生成日报」都应该命中,不要只有 slash 命令
4. **大方法论拆 references** —— SKILL.md 只留 runbook,按场景懒加载参考资料
5. **敏感信息外置** —— 个人数据(profile/笔记仓库)永远在 skill 仓库之外

## License

MIT
