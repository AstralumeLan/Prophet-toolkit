# 塔罗

RWS 78 张牌，牌义是对 A. E. Waite 1910 年公有领域文本的原创关键词改写，无牌面图像。
默认 one 一张；three 为过去/现在/未来，celtic 十张。seed 驱动 Python Random 洗牌，
每张逆位概率 0.5。可复现性以 Python 算法及版本为限，不声称随机结果有预测效力。

`draw` 需要 --question，默认写 core/draws.jsonl，包含问题原文及结果。
相同方法/问题复用；显式不同 seed 有重抽警告，指定已有旧 seed 时复用旧记录。
--no-record 不追加日志，但仍可读取已有记录。默认时区 Asia/Shanghai。
`card NAME` 支持牌 ID、英文或中文名；不抽牌、不写日志。

## 示例

```bash
bin/prophet tarot draw --spread three --question 虚构演示 --seed 42 --no-record
bin/prophet tarot card "The Fool"
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## tarot draw

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --spread | one |  可选：one, three, celtic |
| --question | 必填 |  |
| --seed | 未指定 |  |
| --no-record | False |  |
| --tz | Asia/Shanghai |  |
| --json | False |  |

## tarot card

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| name | 必填 |  |
| --json | False |  |
