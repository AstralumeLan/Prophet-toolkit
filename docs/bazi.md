# 八字

基于 lunar-python EightChar、节气与大运 API，神煞查表采用已注明来源的传统表。
默认 sect=2（晚子日柱处理）、立春换年、节气换月、真太阳时、yun-sect=1。
可选钟表时与春节年界；规则选择随结果输出，不做五行吉凶评分。

`chart` 返回四柱、藏干、十神、五行计数、大运与神煞；`liunian/liuyue` 需要 --year。
`daily` 的 --date 为查询日，--birth-date 才是临时出生日期；不提供人物也能查日历。
日历按当地中午判断年月日，并列十二时辰，晚子分段。原始时间和修正时间均保留。
约略盘还会检测区间内节气、换日等边界；候选点只用于计算。

公开回归：lunar-python README 2005-12-23 08:37，钟表时四柱为乙酉、戊子、辛巳、壬辰。
扩展神煞来源与流派差异见 rules_ext 和 eastern/_shensha.py。

## 示例

```bash
bin/prophet bazi chart --person S01
bin/prophet bazi liunian --person S01 --year 2026
bin/prophet bazi liuyue --person S01 --year 2026
bin/prophet bazi daily --person S02 --date 2026-10-31 --time-standard clock
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## bazi chart

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --person | 未指定 | 人物代号，如 S01（core/people.json，缺省时用虚构示例 core/people.example.json） |
| --date | 未指定 | 公历日期 YYYY-MM-DD |
| --time | 未指定 | 当地钟表时间 HH:MM |
| --time-range | 未指定 | 约略时间区间 HH:MM-HH:MM（覆盖人物档案的区间） |
| --place | 未指定 | 地点名（core/geo 常量表） |
| --lat | 未指定 |  |
| --lon | 未指定 |  |
| --tz | 未指定 | IANA 时区，如 Asia/Shanghai |
| --gender | 未指定 |  可选：male, female, 男, 女 |
| --json | False | 输出 JSON（默认即 JSON，保留兼容） |
| --sect | 2 |  可选：1, 2 |
| --year-boundary | lichun |  可选：lichun, spring-festival |
| --month-boundary | jieqi |  可选：jieqi |
| --time-standard | true-solar |  可选：true-solar, clock |
| --yun-sect | 1 |  可选：1, 2 |
| --save-cache | False |  |

## bazi liunian

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --person | 未指定 | 人物代号，如 S01（core/people.json，缺省时用虚构示例 core/people.example.json） |
| --date | 未指定 | 公历日期 YYYY-MM-DD |
| --time | 未指定 | 当地钟表时间 HH:MM |
| --time-range | 未指定 | 约略时间区间 HH:MM-HH:MM（覆盖人物档案的区间） |
| --place | 未指定 | 地点名（core/geo 常量表） |
| --lat | 未指定 |  |
| --lon | 未指定 |  |
| --tz | 未指定 | IANA 时区，如 Asia/Shanghai |
| --gender | 未指定 |  可选：male, female, 男, 女 |
| --json | False | 输出 JSON（默认即 JSON，保留兼容） |
| --sect | 2 |  可选：1, 2 |
| --year-boundary | lichun |  可选：lichun, spring-festival |
| --month-boundary | jieqi |  可选：jieqi |
| --time-standard | true-solar |  可选：true-solar, clock |
| --yun-sect | 1 |  可选：1, 2 |
| --save-cache | False |  |
| --year | 必填 |  |

## bazi liuyue

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --person | 未指定 | 人物代号，如 S01（core/people.json，缺省时用虚构示例 core/people.example.json） |
| --date | 未指定 | 公历日期 YYYY-MM-DD |
| --time | 未指定 | 当地钟表时间 HH:MM |
| --time-range | 未指定 | 约略时间区间 HH:MM-HH:MM（覆盖人物档案的区间） |
| --place | 未指定 | 地点名（core/geo 常量表） |
| --lat | 未指定 |  |
| --lon | 未指定 |  |
| --tz | 未指定 | IANA 时区，如 Asia/Shanghai |
| --gender | 未指定 |  可选：male, female, 男, 女 |
| --json | False | 输出 JSON（默认即 JSON，保留兼容） |
| --sect | 2 |  可选：1, 2 |
| --year-boundary | lichun |  可选：lichun, spring-festival |
| --month-boundary | jieqi |  可选：jieqi |
| --time-standard | true-solar |  可选：true-solar, clock |
| --yun-sect | 1 |  可选：1, 2 |
| --save-cache | False |  |
| --year | 必填 |  |

## bazi daily

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --person | 未指定 | 人物代号，如 S01（core/people.json，缺省时用虚构示例 core/people.example.json） |
| --date | 未指定 | 公历日期 YYYY-MM-DD |
| --time | 未指定 | 当地钟表时间 HH:MM |
| --time-range | 未指定 | 约略时间区间 HH:MM-HH:MM（覆盖人物档案的区间） |
| --place | 未指定 | 地点名（core/geo 常量表） |
| --lat | 未指定 |  |
| --lon | 未指定 |  |
| --tz | 未指定 | IANA 时区，如 Asia/Shanghai |
| --gender | 未指定 |  可选：male, female, 男, 女 |
| --json | False | 输出 JSON（默认即 JSON，保留兼容） |
| --birth-date | 未指定 | 临时出生日期；--date 专用于查询日期 |
| --sect | 2 |  可选：1, 2 |
| --year-boundary | lichun |  可选：lichun, spring-festival |
| --month-boundary | jieqi |  可选：jieqi |
| --time-standard | true-solar | 仅用于出生盘 可选：true-solar, clock |
| --yun-sect | 1 |  可选：1, 2 |
