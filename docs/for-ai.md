# Prophet for AI clients

Prophet computes explicit traditional rule systems and retrieves local texts. It runs
offline after setup, returns JSON, and does not establish predictive validity.
All examples below use fictional S-series fixtures.

## Discover commands and contracts

```bash
bin/prophet tools --pretty
bin/prophet --describe
bin/prophet bazi chart --person S01
bin/prophet person resolve --person S02
```

`tools` and `--describe` return the same JSON object with a `tools` array. Each entry
contains a dotted name such as `bazi.chart`, a description, an argparse-derived
JSON Schema `parameters` object, and an `output_schema` repository-relative path.
Parameter keys use argparse destination names, such as `time_range`; positional
parameters are required unless argparse marks them optional. Global `pretty` is
included. Alternative input requirements such as person OR date/location are checked
by the engine; a manifest with no required parameters does not imply empty inputs work.

[Output schemas](../schemas/) use JSON Schema draft 2020-12. They describe stable
successful top-level output types/keys and engine metadata, allowing additive fields.
Nested structures are intentionally permissive; inspect rules and warnings rather
than assuming every engine uses identical branches. Errors use `error`/`message`
and a nonzero CLI exit code, and are separate from successful output schemas.
Schemas are generated from fictional S01/S02 and documented public inputs by
`scripts/gen_schemas.py`; raw sample values are never saved. Regeneration needs the
installed optional engines and pinned local corpus sources, but performs no downloads.

## MCP stdio server

Launch `bin/prophet-mcp` after setup. The server uses newline-delimited JSON-RPC 2.0
on stdin/stdout, with protocol version `2025-06-18`. Diagnostics stay on stderr.
It supports `initialize`, `notifications/initialized`, `ping`, `tools/list`, and
`tools/call`. Tool names replace dots and hyphens with underscores: `bazi_chart`,
`western_solar_return`. Input schemas come from the same manifest. Calls return
text content containing CLI JSON and `isError` when invocation fails.

Claude Desktop / Cursor style configuration (replace the illustrative absolute path
with your local checkout; do not add private paths to shared reports):

```json
{
  "mcpServers": {
    "prophet": {
      "command": "/opt/prophet-toolkit/bin/prophet-mcp",
      "args": []
    }
  }
}
```

A call after initialize and the initialized notification:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"bazi_chart","arguments":{"person":"S01"}}}
```

The adapter invokes the ordinary CLI with an argument array, without a shell. It
exposes the full CLI, including local record queries, corpus builds, and selftests;
connect only trusted clients. Random tools follow the existing draw log policy:
same method/question reuses the prior draw, and a changed explicit seed warns of a
redraw. `no_record` stops appending but still reads existing records. Do not use it
to evade reuse. Questions and draw records may be sensitive; avoid logging them in
shared client transcripts. There is no network service or authentication layer.

## Recommended workflow

1. Resolve input with `person.resolve`; preserve raw time, precision and candidates.
2. Compute with the intended engine and explicit rule flags. Read warnings first.
3. Search the local corpus, then retrieve passages and neighbouring context.
4. Cite `engine.rules`, `rules_ext`, source URLs, edition and licence metadata.
   Separate calculated facts, traditional textual claims, and your interpretation.

```bash
bin/prophet bazi chart --person S01
bin/prophet corpus search 用神 --book ziping --limit 2
bin/prophet corpus get ziping:c001:p0001
```

Example prompts:

- 用 S01 排八字并检索子平真诠相关段落；列出 engine.rules、warnings 和出处，区分计算与解读。
- Compare the time branches for fictional S02. Preserve the original interval and
  report which chart fields remain invariant, with rules and uncertainty.
- Compute a Bazi chart for S01, search related passages in Ziping Zhenquan, and
  cite the engine rules and passage provenance before interpreting them.

## Caveats

Approximate times are intervals; representative calculation samples are not confirmed
birth times. Unknown time can make time-sensitive results unavailable. Optional
Chiron data may be absent and is then omitted with warnings. Agreement between
engines sharing a library is not independent validation. Corpus text may contain
historical assumptions; retrieval is not endorsement or individualized advice.
Restricted course material is excluded unless explicitly enabled and retains
CC BY-NC-SA 4.0 restrictions. Never substitute divination output for medical,
legal, financial, or other professional advice. Keep real records only in ignored
`core/people.json`; do not publish personalized reports, caches, or journals.

See [shared inputs](core.md), [design contract](SPEC.md), [corpus](corpus.md),
[validation](validate.md), and [third-party notices](../THIRD_PARTY_NOTICES.md).
