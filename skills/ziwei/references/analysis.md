# 实际字段与规则索引

精确盘前缀为 `$`；约略盘前缀为 `$.branches[0]`（逐一替换索引）。下表用精确盘路径。
`palaces[0]` 是示例，先按实际 `name` / `earthlyBranch` 查索引，不能假设 index 0 是命宫。

| 用途 | 精确示例路径 | 注意 |
| --- | --- | --- |
| 元数据 | `$.engine.rules`、`$.warnings`、`$.input.时间精度` | 元数据始终在根；约略盘另有 `$.invariants` |
| 命身宫 | `$.renhuai.mingGongBranch`、`$.renhuai.shenGongBranch`、`$.renhuai.wuxingJuName` | 地支字段与数值索引不可混用 |
| 宫位 | `$.iztro.palaces[0].name`、`$.iztro.palaces[0].earthlyBranch`、`$.iztro.palaces[0].isBodyPalace` | 以实际宫名与地支定位 |
| 星曜 | `$.iztro.palaces[0].majorStars`、`$.iztro.palaces[0].minorStars`、`$.iztro.palaces[0].adjectiveStars` | 只引用实际存在的数组元素 |
| 四化 | `$.sihua` | 每条实际字段 star / transformation / branch；不要假定顺序 |
| 大限 | `$.daxian`、`$.iztro.palaces[0].decadal` | 记录范围和干支，不能假定当前大限 |
| 流年 | `$.annual` | 不传 year 时为 null；非 null 再读取 year/referenceDate/mingPalace |
| 格局候选 | `$.renhuai.patterns` | 仅规则命中，不自动成为人格或事件断言 |
| horoscope | `$.flows`、`$.target.date` | 单独的命令输出；约略盘 flows 在分支下 |

三方四正的可复现推导：地支序为 子丑寅卯辰巳午未申酉戌亥，目标支索引 i 对应 i、(i+4)%12、(i+8)%12、(i+6)%12。
在实际 `iztro.palaces` 内按地支定位，将参与判断的每宫字段路径写进 evidence。此推导不依赖数组宫位顺序。

| school / rule_id | 条件审核 | 本地 corpus 查询 |
| --- | --- | --- |
| 三合 / ziwei.soul-body.context | 命身宫及会照条件 | `corpus search 命宫 --limit 3` |
| 星曜 / ziwei.stars.context | 星曜所在宫及组合 | `corpus search 紫微 --limit 3`（换为实际星曜） |
| 四化 / ziwei.mutagen.layers | 生年与运限层级分别引用 | `corpus search 化忌 --limit 3`（换为实际四化） |
| 三合 / ziwei.trine-opposition | 四宫定位和会照，不机械评分 | `corpus search 三方 --limit 3` |
| 运限 / ziwei.timing.conditional | 大限、流年与本命对应 | `corpus search 大限 --limit 3` |

规则 ID 为本项目原创审核标签，非古籍编号。先 `corpus books` 确认可用版本，检索后 `corpus get ID` 核对段落及上下文。
经典检索可零命中；不得捏造引文。受限课程资料保持默认关闭；如本地有可用结果，保留其出处和许可，不默认用于可公开传播的报告。
