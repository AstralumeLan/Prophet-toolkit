# 紫微斗数

本地 Node 桥接 iztro 2.6.1 与 MIT Renhuai 算法摘录。默认钟表时、农历新年分年、
闰月 split（十五日前后分配）、亮度 default；可选 QS/XD1/ZZ/XD2 亮度表。
晚子 23 点采用次日，保留 iztro 索引 12 与 Renhuai 次日索引 0 的适配信息。
Renhuai 内部调用 iztro，两者一致只能说明适配一致，不能声称独立验证。

`chart/compare` 的 --year 用该年 7 月 1 日作农历年参考，输出流年四化等信息。
`horoscope` 的 --date 是目标日期，--birth-date 为临时出生日期；可选 --hour 0..23，
省略时不输出流时。含大限、小限与年/月/日/时干支、四化落宫和流宫对照。
未知出生时间会拒绝；约略时间按时辰分支，跨午夜保留不同日期。
公开例使用 iztro README 的 2000-08-16 寅时女命；独立排星子集由 validate 校验。


## 示例

```bash
bin/prophet ziwei compare --person S01 --year 2026
bin/prophet ziwei horoscope --person S02 --date 2026-08-28 --hour 12
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## ziwei chart

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
| --year | 未指定 | 流年（以该年7月1日的农历年为准） |
| --time-standard | clock |  可选：clock, true-solar |
| --school, --brightness-school | default |  可选：default, QS, XD1, ZZ, XD2 |
| --leap-month | split |  可选：split, prev-month, next-month, origin-month |
| --save-cache | False |  |

## ziwei compare

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
| --year | 未指定 | 流年（以该年7月1日的农历年为准） |
| --time-standard | clock |  可选：clock, true-solar |
| --school, --brightness-school | default |  可选：default, QS, XD1, ZZ, XD2 |
| --leap-month | split |  可选：split, prev-month, next-month, origin-month |
| --save-cache | False |  |

## ziwei horoscope

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --person | 未指定 | 人物代号，如 S01（core/people.json，缺省时用虚构示例 core/people.example.json） |
| --date | 未指定 | 目标日期 YYYY-MM-DD（非出生日期） |
| --time | 未指定 | 当地钟表时间 HH:MM |
| --time-range | 未指定 | 约略时间区间 HH:MM-HH:MM（覆盖人物档案的区间） |
| --place | 未指定 | 地点名（core/geo 常量表） |
| --lat | 未指定 |  |
| --lon | 未指定 |  |
| --tz | 未指定 | IANA 时区，如 Asia/Shanghai |
| --gender | 未指定 |  可选：male, female, 男, 女 |
| --json | False | 输出 JSON（默认即 JSON，保留兼容） |
| --birth-date | 未指定 | 临时出生日期 YYYY-MM-DD；--person 时默认档案日期 |
| --hour | 未指定 | 目标钟表小时0–23；省略不输出流时 |
| --time-standard | clock |  可选：clock, true-solar |
| --leap-month | split |  可选：split, prev-month, next-month, origin-month |
