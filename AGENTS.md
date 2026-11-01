# Working on Prophet

Prophet is an offline JSON CLI for cultural research and reproducible rule comparisons.
Read `cli.py`, `bin/prophet`, `core/inputs.py`, the affected engine and its `register()`,
`tests/selftest.py`, relevant `docs/`, `scripts/setup.sh`, and `THIRD_PARTY_NOTICES.md`
before changing behavior. Do not commit unless explicitly asked.

## Setup and run

`bash scripts/setup.sh` creates `.venv` using uv or `python3 -m venv`, installs pinned
Python/npm dependencies, fetches pinned vendor sources and optional ephemeris data,
builds the local corpus and runs tests. Setup requires network access; runtime must
stay offline. Python 3.12 and Node 20 are the CI baseline. `--no-tests` skips the final
test run; `--with-tianji` explicitly opts into restricted course material.
If networking is unavailable, use the installed environment and report missing dependencies.

```bash
bin/prophet bazi chart --person S01 --pretty
bin/prophet tools --pretty
bin/prophet --describe
bin/prophet selftest
bin/prophet selftest -k test_bazi
bin/prophet selftest -k test_mcp
```

Selftest discovers plain `test_*` functions and exits nonzero for any failure or no
matching tests. Use temporary directories for persistence tests; never rely on
existing caches or journals. Run the full selftest and relevant optional dependency
checks after changes, including missing-data fallbacks. Shared-library agreement
is not independent validation. Document frozen numeric fixtures and provenance.

## Layout

- `cli.py`, `bin/`: parser, JSON dispatch and entry points.
- `core/`: input precision, coordinates, solar time, draws, cache and tool discovery.
- `eastern/`, `western/`, `vedic/`: engines; Ziwei uses a local Node JSON bridge.
- `corpus/`, `validate/`: local source normalization/search and scoped comparisons.
- `tests/`: offline regression functions and public/fictional fixtures.
- `schemas/`, `prophet_mcp/`: generated output contracts and stdio MCP adapter.
- `docs/`, `scripts/`: system rules, setup and reproducible generators.

## Adding an engine

1. Implement `register(subparsers)` with argparse types, choices, defaults and help;
   register the module in `cli.MODULES`. Return JSON-serializable data.
2. Include `engine` with `name`, `version`, `rules`, and explicit `warnings`.
   Use `rules_ext` for provenance or school details. Keep fallback rules explicit.
3. Resolve inputs through shared helpers. Preserve branches/candidates and invariants
   for uncertain times; distinguish a calculation sample from a confirmed time.
4. Test public reference charts or fictional S01–S04, boundaries, missing dependencies,
   and relevant invariants. Cite numeric provenance, licence and tolerances.
5. Document flags/defaults in the affected system docs. Add fictional/public sample
   values to `scripts/gen_schemas.py` if needed and run `.venv/bin/python scripts/gen_schemas.py`.
   The manifest and MCP list automatically discover the argparse tree.
6. Run tests, regenerate `.venv/bin/python scripts/gen_llms_full.py` after docs changes,
   and inspect the release file list for private or generated content.

## Invariants and privacy

Runtime never accesses the network. Command handlers emit JSON, including explicit
errors and nonzero failure status. Keep output changes backward-compatible and additive.
Never overwrite raw time with a correction. Never silently turn approximate ranges
into confirmed midpoints. Never redraw a recorded question implicitly; use the ordinary
draw policy, preserving reuse and explicit redraw warnings, including through MCP.

Real people belong only in gitignored `core/people.json`. Examples must be fictional
S01–S04 or documented public charts. Never add real birth records, private locations,
caches, journals, credentials, or personalized reports. Do not read private files to
create fixtures. Use temporary directories for all test persistence.

Preserve third-party LICENSE/NOTICE files and attribution. Never bundle vendor
checkouts, generated corpora, node_modules, or Swiss Ephemeris data. Restricted course
material is opt-in and retains CC BY-NC-SA 4.0 restrictions; default builds exclude it.

## Optional agent layer (v0.2.0)

Read `docs/agent-workflows.md` and the relevant `skills/*/SKILL.md` before changing
evidence or analysis workflows. Skills remain optional original guidance outside
deterministic chart engines. `core/evidence.py` checks shape and restricted paths,
not claim semantics or source authenticity. Keep its schema and rejection behavior
aligned. `core/cross_check.py` runs engines independently and compares candidate
fact sets; never describe these as predictive consensus or pair unlike branches.
MCP discovers both commands automatically. Retain the current stdio transport;
SDK migration is future work. Add tests for paths, invalid evidence, interval
branches, skill references and MCP calls. New examples use fictional S01–S04 only.
