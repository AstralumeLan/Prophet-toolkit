# 经典语料

默认 build 从已检出的 vendor/chinese-fortune 与 vendor/ziwei-doushu 生成规范化 JSONL 和
SQLite FTS5 trigram 索引，不联网。PROPHET_RENHUAI_DIR 可替代后者目录。
PROPHET_CORPUS_DATA / PROPHET_CORPUS_INDEX 可将本地生成目录与索引放到其他位置；
替代 data 目录需预先复制随源码发布的两份原创 JSONL。测试用这两个变量隔离子进程。
输入来源、固定提交和许可见 [语料声明](../corpus/data/NOTICE.md)。生成文件已 gitignore。
自编月宿与 Parashara 摘要随仓库发布，其余转录及精选在本地生成。

天纪默认排除；--with-tianji 才读取本地 entries.jsonl，输出 CC BY-NC-SA 4.0 许可、
署名、NonCommercial、ShareAlike，保留来源与原始许可。缺少 opt-in 源文件时明确报错。
普通 build 会移除之前 opt-in 的规范化文件。上游 git checkout 本身含该材料，语料索引默认不含。

search 默认为 5 条、最大 100，可选 --book。三个字符起使用 trigram 并验证字面子串；
短词用转义 LIKE，繁简单字折叠只用于搜索，返回原文。
get 返回指定 ID 与同书同章前后各一段，books 返回版本、许可与数量。
索引缺失时自动从已有 JSONL 建索引；首次安装应先 build 生成完整书目。
检索命中不代表某条内容适合用于个人解释。

## 示例

```bash
bin/prophet corpus build
bin/prophet corpus search 用神 --book ziping --limit 2
bin/prophet corpus get ziping:c001:p0001
bin/prophet corpus books
```

所有人物示例均为虚构。原始输入、规则、警告和候选解释见 [公共层](core.md)。

## corpus build

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --with-tianji | False | 选择 CC BY-NC-SA 4.0 天纪语料 |
| --json | False | 兼容选项；始终输出 JSON |

## corpus search

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| query | 必填 |  |
| --book | 未指定 |  |
| --limit | 5 |  |
| --json | False | 兼容选项；始终输出 JSON |

## corpus get

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| passage_id | 必填 |  |
| --json | False | 兼容选项；始终输出 JSON |

## corpus books

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| --json | False | 兼容选项；始终输出 JSON |
