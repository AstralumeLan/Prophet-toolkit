# 奇门遁甲

实现时家转盘参考兼容盘，表格与基础函数来自 MIT chinese-fortune。
默认 chaibu（符头拆补）；futou 为兼容选择，zhirun/置闰使用连续超神接气算法。
置闰门槛默认 9，允许 0..14；严格大于门槛才闰，7 可复现部分八日差置闰例。
结果明确输出节气上下文、符头、三元、局数、值符、值使、九宫、空亡与马星。
天禽寄宫等流派差异未经过古籍全盘校核，不能声称唯一正统盘。

提供 --lon 时才应用经度真太阳时修正，--place/--person 解析地点本身不自动开启该修正。
约略输入按候选分支；时间、UTC 偏移与节气处理的假设随结果提供。
测试覆盖节气、拆补表、置闰年度连续性、阈值和兼容默认规则。

## 示例

```bash
bin/prophet qimen chart --datetime 2026-10-31T12:00 --tz Asia/Shanghai
bin/prophet qimen chart --person S02 --ju-method zhirun
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## qimen chart

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
| --ju-method | chaibu | 默认符头拆补；zhirun/置闰为连续超神接气置闰法 可选：chaibu, 拆补, futou, zhirun, 置闰 |
| --zhirun-threshold | 9 | 至日期减不闰时至上元符头日期，严格大于门槛才闰（0..14；默认9；7复现8日差置闰） |
