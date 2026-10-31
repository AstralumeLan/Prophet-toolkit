# Changelog

All notable changes to Prophet are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Community issue forms, pull request checklist, conduct and security policies.
- Argparse-derived `tools` manifest and `--describe` alias, generated output schemas,
  and a stdlib MCP stdio server with `bin/prophet-mcp` entry point.
- Agent documentation, llms.txt and generated full documentation, and social preview.

### Changed

- Setup without uv bootstraps pip and upgrades pip, setuptools, and wheel before installing dependencies.

## [0.1.0] — 2026-10-31

### Added

- Offline JSON CLI with fictional S-series examples, explicit rule metadata and warnings.
- Shared input resolution, approximate time candidates and invariants, coordinates,
  true solar time, explicit chart caching, and reusable random draw records.
- Bazi charts and daily/yearly/monthly queries; Ziwei charts, comparison and horoscopes.
- Liuyao, Meihua, Qimen and Huangli engines with declared methods and conventions.
- Western natal, transit, progression, solar return and synastry calculations;
  optional Chiron data and RWS tarot draws and card lookup.
- Lahiri Vedic charts, Vimshottari periods, nakshatra, Ashtakavarga and Shadbala.
- Local corpus build, literal search and passage neighbours with provenance;
  restricted course material excluded by default and enabled only by opt-in.
- Scoped cross-checks and offline regression tests using fictional and public references.
- Pinned dependency setup and third-party licence and attribution documentation.

Agreement between engines sharing libraries is not independent validation.
Outputs support cultural research and entertainment, not professional advice.
