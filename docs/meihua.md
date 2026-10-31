# 梅花易数

采用传统先天八卦数字与 MIT chinese-fortune 体用表。时间法为农历年支序加月日，
再加时支序，取余定上下卦及动爻；日界为午夜。闰月显式选 repeat/next。
数字法 A 为上卦，B 为下卦，A+B 定动爻；静卦为体、动卦为用。
输出本卦、变卦、互卦、动爻、原始算数与体用生克。

`coins` 与 `random` 均为随机数字起卦，不等于六爻铜钱法；使用同一随机日志方法键。
默认事件时间为当前时刻，默认时区 Asia/Shanghai；区间按时辰分支。
公开规则回归为《梅花易数》观梅占：34/43、初爻动、泽火革变泽山咸。

## 示例

```bash
bin/prophet meihua numbers 34 43
bin/prophet meihua time --person S02
bin/prophet meihua random --seed 42 --question 演示 --no-record
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## meihua time

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

## meihua numbers

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
| A | 必填 |  |
| B | 必填 |  |

## meihua coins

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

## meihua random

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
