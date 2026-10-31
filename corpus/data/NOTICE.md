# 语料来源与许可

本目录只随源码发布 Prophet 自编的 nakshatra.jsonl、parashara.jsonl（CC0-1.0）、
MIT 字符折叠表 han-variants.json、chinese-fortune-LICENSE 与本说明。
自编摘要不复制现代译文；传统特征仅供文化研究，不构成个人结论。

`bin/prophet corpus build` 从 vendor/chinese-fortune 的 knowledge/manifest.json
及章节文件生成 ziping_classics.jsonl，从 vendor/ziwei-doushu 的
lib/classics/data/{quanshu,quanji,gusuifu}.ts 生成 ziwei_classics.jsonl，
并生成 books.jsonl 和 ../index.sqlite。生成文件不随源码发布。
可用 PROPHET_RENHUAI_DIR 指定替代的本地上游目录。

古籍原作属公有领域；转录本另有许可，适用时包括 Wikisource CC BY-SA 4.0。
每段保留 source/source_url、license、revision、版本和节选信息。
Renhuai 精选可能含现代编辑文字，不标为经校勘底本。规范化只增加检索字段，
不改引文；繁简折叠只用于检索，返回原文。再分发生成语料前应遵守各段许可。

天纪课程默认不进入语料。显式运行 `bin/prophet corpus build --with-tianji`
才读取本地 vendor/ziwei-doushu/docs/tianji-ziwei/entries.jsonl，复制其许可文件，
并在输出报告 CC BY-NC-SA 4.0 条款：署名倪海厦及权利继承人、
Renhuai123/ziwei-doushu 整理；NonCommercial（非商业）；ShareAlike（相同方式共享）。
保留视频来源、原始元数据及逐行编号；修改仅为增加检索字段。
普通 build 会移除之前生成的课程文件并重建索引。

完整来源清单见 ../../THIRD_PARTY_NOTICES.md。检索命中只提供引文候选，
不能证明某条文字适用于某人。
