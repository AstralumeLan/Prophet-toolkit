# 黄历

使用 lunar-python 的农历、干支、宜忌、值神、十二建除、二十八宿与彭祖百忌 API。
`day` 接受事件输入；省略日期时使用当地当前日，默认 Asia/Shanghai。
输出十二时辰及其宜忌、冲煞、黄黑道；日历数据来自所用库版本，不代表行动建议。
约略人物区间按共享时辰候选机制返回 branches，即使部分日级字段相同。
公开测试采用日历 API 的固定日期与时神循环表，区分日级与时级字段。

## 示例

```bash
bin/prophet huangli day --date 2026-10-31
bin/prophet huangli day --person S02
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## huangli day

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
