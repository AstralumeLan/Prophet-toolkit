# 西方占星

主行星及月交点采用 Swiss Ephemeris Moshier、地心视位置、热带黄道，UT 以 UTC 近似。
默认 Placidus 宫制；可选 whole-sign/koch/equal/porphyry。极地 Placidus/Koch 回退 Porphyry，
计算失败进一步回退整宫并警告。默认主要相位容许度：合冲 8、拱刑 6、六合 4 度。
--minor 增加次要相位，--orbs 接收 JSON 度数映射。宫位按黄经宫头区间分配。

`transits/progressions` 需 --at；次限为每 365.2425 个经过日对应一个星历日。
`solar-return` 需 --year；人物输入时 --place 可指定返照地点，不改本命地点。
`synastry` 可用 --other S03，或完整 --other-date/time/place 等输入。
Chiron 依赖下载的 seas_18.se1，缺失或超范围省略并警告；其他星体仍可算。
近停阈值是每日 0.001 度，属于本工具约定。

约略出生按 15 分钟加端点取样，宫位稳定只指样本。未知时间用中午占位并警告。
公开回归包括 Einstein 1879-03-14 11:30 LMT Ulm（测试直接换算地方平时）、
J2000 与 astronomy-engine 经度对照。现代时区输入不等价于历史 LMT。

## 示例

```bash
bin/prophet western natal --person S01
bin/prophet western transits --person S01 --at 2026-10-31
bin/prophet western solar-return --person S01 --year 2026
bin/prophet western synastry --person S01 --other S03
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## western natal

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
| --house-system | placidus |  可选：placidus, whole-sign, koch, equal, porphyry |
| --minor | False |  |
| --orbs | 未指定 |  |
| --save-cache | False |  |

## western transits

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
| --house-system | placidus |  可选：placidus, whole-sign, koch, equal, porphyry |
| --minor | False |  |
| --orbs | 未指定 |  |
| --save-cache | False |  |
| --at | 必填 |  |

## western progressions

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
| --house-system | placidus |  可选：placidus, whole-sign, koch, equal, porphyry |
| --minor | False |  |
| --orbs | 未指定 |  |
| --save-cache | False |  |
| --at | 必填 |  |

## western solar-return

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
| --house-system | placidus |  可选：placidus, whole-sign, koch, equal, porphyry |
| --minor | False |  |
| --orbs | 未指定 |  |
| --save-cache | False |  |
| --year | 必填 |  |

## western synastry

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
| --house-system | placidus |  可选：placidus, whole-sign, koch, equal, porphyry |
| --minor | False |  |
| --orbs | 未指定 |  |
| --save-cache | False |  |
| --other | 未指定 |  |
| --other-date | 未指定 |  |
| --other-time | 未指定 |  |
| --other-time-range | 未指定 |  |
| --other-place | 未指定 |  |
| --other-tz | 未指定 |  |
| --other-lat | 未指定 |  |
| --other-lon | 未指定 |  |

## western check

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
| --house-system | placidus |  可选：placidus, whole-sign, koch, equal, porphyry |
| --minor | False |  |
| --orbs | 未指定 |  |
| --save-cache | False |  |
