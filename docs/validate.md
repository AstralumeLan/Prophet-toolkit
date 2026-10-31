# 交叉校验

validate 接受共同出生输入，默认钟表时。all 返回各体系汇总，单体系返回具体字段差异。
八字 lunar-python 立春规则与 iztro 农历新年规则差异明确保留，不能为通过测试而隐去。
紫微独立子集计算命身宫、五行局、十四主星及部分辅星/四化；Renhuai 比较另标非独立。
西方以 astronomy-engine 对照主行星经度，日月至土星容差 1 角分、外行星 2 角分。
印度以独立热带经度减 Swiss Lahiri 交叉检查位置及月宿区间；共享岁差来源，交点排除。

approx 输入返回分支及 invariants。一致只证明选定字段与规则的计算一致，不证明术数的预测能力。
`selftest` 发现 tests/test_*.py 的 test_* 函数，-k 按名字筛选；失败退出码非零。
Chiron 文件缺失时仅相关数值测试打印 NOTE 后通过，降级路径仍测试。
语料课程未启用时跳过课程断言；其余语料/许可/检索检查仍执行。

## 示例

```bash
bin/prophet validate all --person S01
bin/prophet validate ziwei --person S02
bin/prophet selftest -k vedic
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## validate bazi

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

## validate ziwei

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

## validate western

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

## validate vedic

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

## validate all

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
