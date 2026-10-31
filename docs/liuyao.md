# 六爻

规则取自 MIT chinese-fortune 的京房纳甲、八宫、世应、六亲、六神表。
`manual` 的 --lines 必须为六位 6/7/8/9，自下而上；6/9 为动爻。
变卦六亲仍以本卦宫五行为基准，伏神由所属纯卦缺失六亲补出。
月建按节气，日辰与旬空按日历；不自动作占断。

`time` 用农历年支序、月、日、时支起卦；闰月须明确 repeat/next 约定。
`coins` 使用 seed 可复现铜钱抽样；默认记入共享日志，演示用 --no-record。
省略事件日期时间时使用指定时区当前时刻；区间输入按时辰分支。
公开回归包括乾卦纳甲、天风姤世应和变卦六亲。

## 示例

```bash
bin/prophet liuyao manual --lines 777777 --datetime 2026-10-31T12:00
bin/prophet liuyao coins --seed 42 --question 演示 --no-record
bin/prophet liuyao time --person S02
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## liuyao coins

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
| --datetime | 未指定 | ISO 日期时间；有偏移量时转换到 --tz |
| --question |  |  |
| --leap-month-policy | 未指定 |  可选：repeat, next |
| --seed | 未指定 |  |
| --no-record | False |  |

## liuyao time

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
| --datetime | 未指定 | ISO 日期时间；有偏移量时转换到 --tz |
| --question |  |  |
| --leap-month-policy | 未指定 |  可选：repeat, next |

## liuyao manual

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
| --datetime | 未指定 | ISO 日期时间；有偏移量时转换到 --tz |
| --question |  |  |
| --leap-month-policy | 未指定 |  可选：repeat, next |
| --lines | 必填 |  |
