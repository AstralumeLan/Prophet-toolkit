# 实际字段与规则索引

所有路径针对 `bazi chart` 原始返回。逐 `$.candidates[i]` 分支替换索引：

| 用途 | 精确示例路径 | 注意 |
| --- | --- | --- |
| 元数据 | `$.engine.rules`、`$.warnings`、`$.input.时间精度` | 原始时间在 `$.input.time` / `$.input.time_range` |
| 月令/日主 | `$.candidates[0].pillars.month.branch`、`$.candidates[0].day_master` | 月令不是单一计数 |
| 四柱 | `$.candidates[0].pillars.year.ganzhi`、`$.candidates[0].pillars.month.ganzhi`、`$.candidates[0].pillars.day.ganzhi`、`$.candidates[0].pillars.hour.ganzhi` | 每柱另有 stem / branch |
| 藏透十神 | `$.candidates[0].pillars.month.hidden_stems`、`$.candidates[0].pillars.month.stem_ten_god`、`$.candidates[0].pillars.month.hidden_ten_gods` | year/day/hour 同结构 |
| 计数 | `$.candidates[0].five_elements`、`$.candidates[0].hidden_stem_elements` | 未加权，非强弱分数 |
| 时间校正 | `$.candidates[0].clock_time`、`$.candidates[0].true_solar`、`$.candidates[0].calculation_time` | 查看 `$.engine.rules.time_standard` |
| 运限 | `$.candidates[0].dayun` | 未提供性别时可能为 null |
| 运限明细 | `$.candidates[0].dayun.direction`、`$.candidates[0].dayun.start_date`、`$.candidates[0].dayun.age_convention`、`$.candidates[0].dayun.steps[0].ganzhi`、`$.candidates[0].dayun.steps[0].start_year`、`$.candidates[0].dayun.steps[0].end_year` | 仅 dayun 非 null 时使用 |
| 稳定性 | `$.invariants` | 每字段分别比较，不能推为整盘稳定 |
| 流年（liunian） | `$.candidates[0].liunian.year`、`$.candidates[0].liunian.ganzhi`、`$.candidates[0].liunian.dayun` | 仅 liunian 返回；额外保存该份原始输出 |

原创建议规则 ID（分析协议标签，不冒充古籍条文编号）：

| school / rule_id | 检验内容 | 本地 corpus 查询 |
| --- | --- | --- |
| 扶抑 / bazi.strength.context | 月令、通根与助泄克并看 | `corpus search 通根 --book ditian --limit 3` |
| 格局 / bazi.pattern.conditions | 月令格局、成败救应 | `corpus search 用神 --book ziping --limit 3` |
| 调候 / bazi.climate.conditions | 日干月份寒暖燥湿条件 | `corpus search 甲木 --book qiongtong --limit 3`（按日干替换） |
| 病药 / bazi.remedy.countercase | 障碍与解除条件分别取证 | `corpus search 病药 --limit 3` |
| 十神 / bazi.relationship.context | 位置、透藏及结构条件 | `corpus search 正官 --book yuanhai --limit 3`（按主题替换） |
| 运限 / bazi.timing.conditional | 运限与本命条件叠加 | `corpus search 行运 --limit 3` |

先 `corpus books` 核对本地书籍 ID，若 ID 不存在则去掉 book 过滤；零命中报告缺证。
拿到结果后用 `corpus get ID` 核对来源、原文与邻文。保留 edition / license 等返回元数据。
