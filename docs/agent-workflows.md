# Agent Skills · Evidence · Cross-check (v0.2.0)

Optional agent guidance lives in [Bazi](../skills/bazi/SKILL.md),
[Ziwei](../skills/ziwei/SKILL.md) and [Cross-check](../skills/cross-check/SKILL.md).
These original instructions separate chart calculation, retrieval, interpretation
and review. No model, external service or new package is required. They draw on the
general ideas of staged analysis and a final critic; no third-party project text or
implementation is copied. Load only the relevant skill and its field/rule reference.

## Evidence / 证据

Save a local JSON document with exactly `chart` (the unchanged raw chart JSON) and
`evidence` (a nonempty list). Each item follows
[evidence-item.schema.json](../schemas/evidence-item.schema.json):

```json
{
  "claim": "日主为己；这是一项盘面事实，尚未判断旺衰。",
  "system": "bazi",
  "json_paths": ["$.candidates[0].day_master"],
  "school": "盘面事实",
  "rule_id": "bazi.day-master.fact",
  "corpus_reference": {"query": "日主"},
  "confidence": "high",
  "counter_interpretation": "日主本身不足以确定旺衰、格局或喜忌；其他候选应分别核对。"
}
```

This item illustrates the fictional S01 Bazi chart; obtain the actual chart with
`bin/prophet bazi chart --person S01`. Do not paste an item onto an unrelated chart.
`confidence` is qualitative analyst confidence, never a calibrated probability.
`rule_id` and `school` identify the analyst's rule and tradition, not verified corpus
identifiers. `corpus_reference` accepts nonblank `id` and/or `query`. A query records
research still to do; only retrieved passages can be quoted as sources.

```bash
bin/prophet evidence check evidence.json
```

Exit 0 means valid structure and resolving references; invalid evidence exits 1.
Malformed JSON or envelopes also return JSON errors and nonzero status. Paths use
`$`, `.key`, `[0]` and JSON double-quoted keys such as `$["中文.字段"]`.
No wildcards, negative indices, filters, recursive descent or expressions. Missing
keys, wrong container types and out-of-range indices fail; present null values resolve
but cannot substantiate an interpretation of unavailable data. Root-only references
are rejected. Each item must match the embedded chart engine's system.

The validator returns resolved values to help reviewers compare claims with facts.
It does **not** establish that words in a claim follow from those values, authenticate
corpus IDs, assess a school, or verify that the supplied raw chart is unmodified.
Keep the source chart and review meaning, retrieved context, conditions and alternative
interpretations separately. Evidence documents and resolved values may contain personal data;
keep them local and review before sharing.

## Cross-check / 交叉分析

```bash
bin/prophet cross-check run --person S01
bin/prophet cross-check run --person S02 --systems bazi,ziwei,western
bin/prophet cross-check run --person S01 --include-charts
```

At least two distinct systems are required; the supported choices are Bazi, Ziwei
and Western. Shared birth flags go through `core.inputs.resolve_birth`. Each engine
runs independently using its ordinary parser defaults, without saving caches or draws.
Eastern time standard defaults to `clock` for comparison; `--time-standard true-solar`
applies to both eastern engines. Western keeps clock/UTC. Engine-specific school and
boundary overrides remain available through the ordinary chart commands, not this
small helper. Missing input or an engine failure fails the command; partial success
is not presented as a comparison.

The default response contains `input`, per-system `summaries` and `comparison` with
`agreements`, `conflicts`, `unique`. Summaries carry metadata, warnings, candidate
counts, invariants and facts with raw-chart paths. Four pillar facts from Ziwei use
the explicitly recorded whitespace-splitting transform of `iztro.chineseDate`.
Other facts stay system-specific. All candidates are retained; candidate value sets
are compared without assuming branch-to-branch alignment. Agreement is limited to
those sets, never whole-chart or predictive agreement. For interval input, read
per-system invariants and warnings; Western samples do not cover every instant.

Use `--include-charts` to retain raw charts for review. Summary paths are relative to
each system's raw chart, **not** the combined helper document. For evidence checking,
embed `charts.bazi`, for example, as the evidence document's `chart`. Default compact
mode omits raw charts but preserves each system's invariants and candidate facts.

Interpreted cross-system themes require a separate agent pass: independent short
interpretations first, then compare theme, time range, evidence and counter-reading. Do not
map unrelated symbols to a common verdict or count shared libraries as independent
confirmation. Optional deep multi-agent review is described in the cross-check skill;
ordinary use stays single-agent and lightweight.

## MCP and scope

Where the existing MCP adapter is installed, argparse discovery exposes
`evidence_check` (`file`) and `cross_check_run` (shared birth flags plus `systems`,
`time_standard`, `include_charts`). File paths are local to the server process;
only connect trusted clients. Calls use the ordinary CLI and preserve exit status.
The minimal stdio transport is unchanged. Official MCP SDK migration is deferred:
it would add a dependency and protocol changes without helping these offline tools.
No HTTP listener or network runtime is introduced.
