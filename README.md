# Prophet

Prophet 是离线命令行传统术数与天文排盘工具。它计算规则、保存来源、展示分歧，
不生成对个人命运的确定性判断。Python 负责统一输入与 JSON 输出，紫微桥接本地 Node。

支持八字四柱、大运、流年流月、日历与神煞；紫微双适配排盘与运限；六爻纳甲、
梅花易数、时家奇门及黄历；西方热带黄道星盘、行运、次限、太阳返照与合盘；
RWS 塔罗；印度 Lahiri 恒星黄道、分盘、Vimshottari、Ashtakavarga 与可选 Shadbala。
经典语料支持本地全文检索，校验模块提供独立天文及部分传统表格交叉检查。

## 安装

需要 Python 3.12、Node.js（支持 `--import tsx`）、npm、git、curl 和 bash。
安装阶段需要联网；安装后的计算和检索不需要网络。
pyswisseph 若无预编译 wheel 会从源码编译，需要 C/C++ 编译器（如 gcc/g++、clang）及 Python 头文件；用 uv 时可设 `UV_PYTHON=3.12` 固定解释器版本。

```bash
bash scripts/setup.sh
# 可选：不运行测试
bash scripts/setup.sh --no-tests
# 显式接受非商业、署名、相同方式共享课程许可后启用
bash scripts/setup.sh --with-tianji
```

脚本可重复运行：创建 .venv、安装 requirements.txt、npm ci、按固定提交检出三个
vendor 仓库、下载可选 Chiron 星历、生成语料和索引、运行 selftest。
不会下载发布附件或大型数据集。若 vendor 有本地修改，先自行保存修改再运行。
Python 依赖固定为 lunar-python 1.4.8、pyswisseph 2.10.3.2、astronomy-engine 2.1.19；
npm 由 package-lock.json 锁定。uv 可用时用于创建环境及安装，否则使用 venv/pip。
离线环境可预备相同依赖与 vendor，再执行 `bin/prophet corpus build`。

项目原创代码采用 MIT；第三方代码、语料及 Swiss Ephemeris 另有条款。
尤其是链接 pyswisseph 的组合发行物受 AGPL 义务约束。
分发前请阅读 [第三方说明](THIRD_PARTY_NOTICES.md)。星历和生成语料不包含在源码发布中。

## 快速开始

S01–S04 全部是虚构示例：S01 精确时间、S02 区间、S03 暂用时间、S04 区间。

```bash
bin/prophet person list
bin/prophet bazi chart --person S01 --pretty
bin/prophet ziwei chart --person S01
bin/prophet western natal --person S01
bin/prophet vedic chart --person S01 --levels 1 --at 2026-10-31
bin/prophet bazi chart --person S02 --time-standard clock
bin/prophet corpus search 用神 --book ziping
bin/prophet validate all --person S01
bin/prophet tarot draw --spread three --question '虚构演示问题' --seed 42 --no-record
```

## CLI 参考

`bin/prophet --help` 与任意子命令 `--help` 为选项的完整说明。
`--pretty` 可放任意位置；`--json` 是部分命令保留的兼容参数，默认就输出 JSON。

| 体系 | 子命令 | 说明 |
| --- | --- | --- |
| person | list / show CODE / resolve | 档案及时间候选 |
| geo | [PLACE] | 城市中心坐标，省略列出地点 |
| solartime | 出生输入选项 | 经度、时区与均时差修正 |
| cache | list | 本地命盘缓存 |
| draws | list [--method METHOD] | 本地随机记录 |
| bazi | chart / liunian / liuyue / daily | 四柱、大运、年/月/日信息 |
| ziwei | chart / compare / horoscope | 双适配盘与运限 |
| liuyao | coins / time / manual | 铜钱、时间、手工六爻 |
| meihua | time / numbers A B / coins / random | 时间、数字、随机起卦 |
| qimen | chart | 拆补或置闰时家转盘 |
| huangli | day | 日历宜忌及十二时辰 |
| western | natal / check / transits / progressions / solar-return / synastry | 星盘、交叉计算与衍生盘 |
| tarot | draw / card NAME | 抽牌与牌义索引 |
| vedic | chart / dasha / nakshatra / shadbala | 印度占星与六力 |
| corpus | build / search QUERY / get ID / books | 本地语料生成、全文检索与出处 |
| validate | all / bazi / ziwei / western / vedic | 差异与规则说明 |
| selftest | [-k PATTERN] | 执行离线回归 |

按体系阅读 [八字](docs/bazi.md)、[紫微](docs/ziwei.md)、[六爻](docs/liuyao.md)、
[梅花](docs/meihua.md)、[奇门](docs/qimen.md)、[黄历](docs/huangli.md)、
[西方](docs/western.md)、[塔罗](docs/tarot.md)、[印度](docs/vedic.md)、
[语料](docs/corpus.md)、[校验](docs/validate.md)、[公共层](docs/core.md)。

## 输入、JSON 与不确定时间

出生输入用 `--person S01`，或 `--date YYYY-MM-DD --time HH:MM --place 北京`；
自定义地点用 `--lat --lon --tz`（IANA 时区）。原始钟表时间保留，真太阳时另列。
城市坐标为市中心近似，历史地方平时不能直接当现代时区时间处理。

计算结果通常有 `engine: {name, version, rules}`，说明算法与默认规则；
新增解释字段放 `rules_ext`（部分体系在 engine 内）。`warnings` 保留降级、流派和精度提示。
`input` 为解析输入；`candidates`（八字）或 `branches`（多体系）为候选结果。
`invariants` 分“不随时间变化”和“随时间变化”，其值仅适用于实际计算的候选。
列表、检索等辅助命令可直接返回数组或其他结构。错误为 JSON `error/message/trace`，
退出码非零；selftest 的失败也返回非零。日期时间经 JSON 序列化为字符串。

约略时间使用 `--time-range 20:00-21:00`，不把中点当确认时间。
S02 的钟表区间包括端点，覆盖戌、亥两个时辰。东方法一般按时辰及必要日期/节气边界分支；
西方和印度按 15 分钟加端点取样，不能据此证明整个连续区间都稳定。
S03 的 provisional 仍是暂用输入。未知时间某些系统拒绝，西方可给中午占位并警告宫位不可靠。
八字默认真太阳时，紫微默认钟表时；比较前应对齐规则。

## 随机记录与隐私

随机起卦默认追加到 core/draws.jsonl，包括问题原文、seed、时区、时间和结果。
同方法同问题复用原结果；显式不同 seed 会标记重抽警告。塔罗也可复用较早 seed 的结果。
演示与测试使用 `--no-record` 或临时日志；该选项不屏蔽已有记录的复用。
日志已忽略但可能包含敏感问题，请自行妥善保存。

真实资料只放 core/people.json（gitignored），不存在时加载 core/people.example.json。
不要提交真实人物数据、缓存、抽签记录、个性化报告或环境凭据。
测试使用虚构或公开参考图，不依赖预先生成的缓存。共享错误输出前也请检查 input 和 trace。

## 准确性与局限

`bin/prophet selftest` 覆盖公开 lunar-python 例、iztro README 例、Einstein 地方平时参考盘、
Delhi 图、Raman Standard Horoscope 数值、边界、区间、缓存往返及语料检索。
新虚构回归数值由引擎计算一次，结合历法/五行或公开参考检查后冻结；不是独立准确性证明。
`validate` 显示具体差异而不强行统一：八字立春与农历新年边界可能不同；
Renhuai 内部使用 iztro，两者一致不算独立校验。紫微另有有限独立排星检查。
西方/印度用 astronomy-engine 交叉检查部分经度，容差及排除项在输出规则中。

已知缺口：流派覆盖有限；神煞不作吉凶评分；奇门为参考兼容盘；经典精选未经完整校勘；
印度无自动校时、D60、瑜伽或 BAV 消减；六力历史平运动近似缺少额外独立样本。
Chiron 缺少 seas_18.se1 或超出覆盖范围会省略并警告。语料命中不代表可用于个人推断。
天纪仅显式启用，非商业限制不因本项目 MIT 而消失。

本工具仅供娱乐与文化研究，不构成医疗、法律、投资或其他专业建议。

## English

Prophet is an offline CLI for traditional calendrical/divination calculations,
tropical and sidereal astrology, reproducible tarot draws and sourced corpus search.
Install Python 3.12, Node.js/npm, git and curl, then run `bash scripts/setup.sh`.
Setup needs network access; runtime does not. Use `bin/prophet bazi chart --person S01`
and `bin/prophet selftest`. All S-series people are fictional.

Keep real records in ignored core/people.json; caches and draw journals are private.
Approximate times produce candidates, never a silently confirmed midpoint. JSON
reports engine rules, warnings and sampled invariants. Public reference checks do
not establish predictive validity. Original code is MIT, but dependencies and texts
have separate terms: see THIRD_PARTY_NOTICES.md, especially AGPL obligations for
pyswisseph-linked distributions. Course material is optional and CC BY-NC-SA 4.0.
For entertainment and cultural study only; no professional advice.
