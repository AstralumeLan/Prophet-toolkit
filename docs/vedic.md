# 印度占星

采用 Swiss Ephemeris Moshier、Lahiri 恒星黄道、整宫制、默认平均交点，Ketu 与 Rahu 相对。
分盘 D1/D7/D9/D10/D12；Vimshottari 年长固定 365.25 日，出生前完整大运不重启子运。
--levels 默认为 3，可用 1/2；--at 为出生地时区零点的查询日，省略取当前时刻。
BAV 默认 parashara，另有 dashaflow/varahamihira/pyjhora-pvr；输出逐源贡献与 SAV 总分 337。
pyjhora-pvr 从 P.V.R. Narasimha Rao 书中描述独立实现，不使用 PyJHora。

交点尊贵默认 none，可选 bphs/gemini-sagittarius；不是对不同流派的统一结论。
`shadbala` 或 chart --shadbala 输出 Raman/Sripathi 六力及各分量、来源、阈值和警告。
历史平运动近似、历年/月主规则和参考书勘误见 [规则明细](../vedic/data/RULES.md)。
只在测试引用 Raman Standard Horoscope 数字，不发布书中文字。

约略时间每 15 分钟加端点采样，未知时间拒绝。没有自动校时、D60、瑜伽或 BAV 消减。
公开回归包括 dashaflow Delhi 图、Lahiri J2000、BAV 守恒、分盘边界及 Raman 六力数值。

## 示例

```bash
bin/prophet vedic chart --person S01 --levels 1 --at 2026-10-31
bin/prophet vedic dasha --person S02 --levels 2 --at 2026-10-31
bin/prophet vedic shadbala --person S01 --levels 1
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## vedic chart

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
| --node | mean |  可选：mean, true |
| --bav-table | parashara |  可选：dashaflow, parashara, varahamihira, pyjhora-pvr |
| --node-dignity | none |  可选：none, bphs, gemini-sagittarius |
| --shadbala | False | include Raman sixfold strength |
| --at | 未指定 | 查询日期 YYYY-MM-DD（出生地时区午夜） |
| --levels | 3 |  可选：1, 2, 3 |
| --save-cache | False |  |

## vedic dasha

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
| --node | mean |  可选：mean, true |
| --bav-table | parashara |  可选：dashaflow, parashara, varahamihira, pyjhora-pvr |
| --node-dignity | none |  可选：none, bphs, gemini-sagittarius |
| --shadbala | False | include Raman sixfold strength |
| --at | 未指定 | 查询日期 YYYY-MM-DD（出生地时区午夜） |
| --levels | 3 |  可选：1, 2, 3 |
| --save-cache | False |  |

## vedic nakshatra

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
| --node | mean |  可选：mean, true |
| --bav-table | parashara |  可选：dashaflow, parashara, varahamihira, pyjhora-pvr |
| --node-dignity | none |  可选：none, bphs, gemini-sagittarius |
| --shadbala | False | include Raman sixfold strength |
| --at | 未指定 | 查询日期 YYYY-MM-DD（出生地时区午夜） |
| --levels | 3 |  可选：1, 2, 3 |
| --save-cache | False |  |

## vedic shadbala

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
| --node | mean |  可选：mean, true |
| --bav-table | parashara |  可选：dashaflow, parashara, varahamihira, pyjhora-pvr |
| --node-dignity | none |  可选：none, bphs, gemini-sagittarius |
| --shadbala | False | include Raman sixfold strength |
| --at | 未指定 | 查询日期 YYYY-MM-DD（出生地时区午夜） |
| --levels | 3 |  可选：1, 2, 3 |
| --save-cache | False |  |
