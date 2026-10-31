# 公共输入、坐标、时间与持久化

core/inputs.py 优先加载 core/people.json，不存在则用虚构示例文件。真实文件、缓存及随机日志
已忽略；发布前仍须检查暂存清单。S01 精确、S02/S04 约略、S03 暂用；不要当真实人物。
--person 与临时 --date/--time/--place 共用解析；--time-range 显式覆盖区间。
自定义地点传 --lat/--lon/--tz；坐标不全且有 --place 时从通用城市表补齐。
IANA zoneinfo 处理时区和历史夏令时；市中心坐标不是精确出生地点。

shichen_candidates 按分钟扫描区间，包含两端，分组后取计算代表点；sample_candidates
每 15 分钟并加端点。代表点不是确认时间，invariants 只描述已计算结果。
真太阳时保留原钟表时间，拆分夏令时、经度修正、Swiss 均时差，并以 NOAA 近似校验。
不能将不确定的时间自动校正为确定时间。S02 钟表 20:00–21:00 跨戌/亥。

缓存用人物、体系和规则哈希命名，只在显式 --save-cache 时写入。测试重定向到临时目录，
不读取历史缓存。修改规则应考虑版本和缓存身份；不要把计算结果当作源档案。
随机记录默认追加 core/draws.jsonl。相同方法和问题复用原记录，不隐式重抽；
不同显式 seed 提示重抽。--no-record 只停止追加，不停止读取。分享前检查问题原文。

JSON 常见字段为 engine{name,version,rules}、rules_ext、warnings、input 和
branches/candidates；辅助列表和 search 可以直接返回数组。错误为 JSON 并返回非零。
--pretty 全局有效；--version 显示版本。输出中的日期时间是字符串。

```bash
bin/prophet person show S01
bin/prophet person resolve --person S02
bin/prophet geo 北京
bin/prophet solartime --person S01
bin/prophet cache list
bin/prophet draws list --method tarot-three
```

## person list

| 参数 | 默认 | 说明 |
| --- | --- | --- |


## person show

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| code | 必填 |  |

## person resolve

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
| --true-solar | False |  |

## geo 

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| place | 未指定 | 地点名；省略则列出全部 |

## solartime 

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

## cache list

| 参数 | 默认 | 说明 |
| --- | --- | --- |


## draws list

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --method | 未指定 |  |
