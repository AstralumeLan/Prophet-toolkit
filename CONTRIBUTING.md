# 参与开发

使用 scripts/setup.sh 安装固定依赖与参考 checkout，然后运行 bin/prophet selftest。
单体系调试可用 `bin/prophet selftest -k bazi`。网络仅用于安装，运行时不得添加隐式网络请求。
不需要预先生成的命盘缓存。vendor 有本地修改时安装脚本会停止以保护修改。

提交改动时解释规则来源、默认值、候选时间语义和验证证据；更新对应 docs 页面。
新测试用虚构 S01–S04 或明确注明出处的公开图例。冻结数值须先计算、核对基本历法或
独立参考，并在注释中记录来源和局限。缓存/日志测试使用临时目录，不能读开发者历史文件。
语料测试应同时支持课程启用/未启用；Chiron 的可选文件缺失时保留降级测试。

原创代码遵循 MIT；改编代码保留原始许可和来源。第三方依赖、转录文本和星历有独立条款，
详见 THIRD_PARTY_NOTICES.md。不要提交生成语料、SQLite、vendor、node_modules 或星历文件。
不要加入受版权保护的书籍正文或扫描件。

真实人物档案只可保存在 gitignored core/people.json；不要在代码、测试、问题说明、
截图或附件中加入真实出生资料。缓存、日志、私人输出和凭据都不得发布。
PR 前查看 `git status --short --untracked-files=all` 及实际暂存 diff；.gitignore 不是完整隐私审核。

建议代码风格：Python 标准库优先、纯函数可独立验证、JSON 明确记录规则和警告。
保持 CLI 退出码、默认规则和既有字段含义；新增可选字段优先放 rules_ext。
规则冲突应输出具体差异，不通过修改期望来隐藏缺陷。
