---
name: cross-check
description: 以 Prophet 独立运行至少两个体系，保留分支和规则，轻量比较共识、冲突与独有信息；仅综合分析请求适用。
---

# 轻量跨体系工作流

默认一个代理顺序完成，无需模型服务或额外依赖。运行：

```bash
bin/prophet cross-check run --person S01
bin/prophet cross-check run --person S02 --systems bazi,ziwei,western --include-charts
```

1. 明确对象、问题和时间精度。helper 经共享输入解析后独立调用各体系，东方默认统一 clock；可用 `--time-standard true-solar`。西占始终钟表转 UTC。规则差异仍须读取各 engine。
2. 读取 summaries 各自的 facts / json_path、engine、warnings、invariants、branch_count。默认只携带精简事实，需要审计时才 include-charts。所有候选保留，不选中点。
3. 分别使用 bazi / ziwei 技能形成短摘要，未看其他体系解释之前先固定本体系结论、证据、条件、反证。西占只解释实际算出的星位宫位，不将东方符号直接对应星座。
4. helper 的 comparison 只比较可匹配的事实键。四柱集合相同仅为历法一致；unique 表示无同键可比，绝不等于其他体系反对。集合不同可能来自边界、代表小时、换年规则或分支取样，不自动认定计算错误。
5. 对解释另建 `agreements/conflicts/unique` 三组。每项写主题、各体系原判断、独立 evidence、条件与时间范围、尚待解决的问题。不同体系不强行投票；同源计算不能升级置信度。不把传统跨体系共识写成预测已获验证。
6. Critic 检查人物一致、字段引用、规则差异、区间覆盖、虚构引文和相反解释。结构检验用 evidence check；它不检查语义。最终保留未决冲突。

可选深度模式仅在复杂问题确有需要且用户允许代理协作时使用：为各体系分配独立分析者，仅提供本体系原始盘与问题；汇总者对照摘要，评审者回查证据。不要为了普通问答默认启用多代理；不把它引入确定性核心。

完整数据协议、命令及局限见 [工作流说明](../../docs/agent-workflows.md)。
