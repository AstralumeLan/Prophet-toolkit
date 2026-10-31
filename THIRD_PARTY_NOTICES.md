# Third-party notices

Prophet's original code is MIT (see LICENSE). Third-party components retain
their own terms. The MIT grant does not relicense dependencies or fetched texts.
The runtime is offline after setup. Setup uses ordinary git checkouts, pip,
npm and one ephemeris download; it does not download release assets or datasets.

| Source | Included or fetched | Licence and attribution |
| --- | --- | --- |
| [Renhuai123/ziwei-doushu](https://github.com/Renhuai123/ziwei-doushu), 495b79ecb3524b20b2edc026067d7d0b0f407319 | Code excerpts in eastern/ziwei/js/renhuai; checkout fetched into vendor | MIT; original LICENSE and NOTICE.md retained in excerpt directory. Adaptations documented there. |
| [ShousenZHANG/chinese-fortune](https://github.com/ShousenZHANG/chinese-fortune), 81a980a5707505468a10f596f1f19c9088457a9e | Excerpts in eastern/_cf; frozen shensha tables in eastern/_shensha.py; corpus/data/han-variants.json; checkout fetched | MIT for code and character map; eastern/_cf/LICENSE and NOTICE and corpus/data/chinese-fortune-LICENSE retain permission. Classical transcription licences are separate. |
| [adarshj322/dashaflow](https://github.com/adarshj322/dashaflow), f8f8ead76e56b9048f80adbbbff282c007068cf7 | Tables adapted in vedic/_tables.py; checkout fetched | MIT; attribution and original permission in vedic/_dashaflow/LICENSE and NOTICE. |
| [iztro](https://github.com/SylarLong/iztro) 2.6.1 | npm dependency, fetched; node_modules excluded | MIT; package licence retained by npm. Renhuai also uses iztro, so agreement between them is not independent validation. |
| [lunar-python](https://github.com/6tail/lunar-python) 1.4.8 / [lunar-javascript](https://github.com/6tail/lunar-javascript) | Python / npm dependencies, fetched | MIT; upstream 6tail copyright and package licences apply. npm versions are locked in package-lock.json. |
| [astronomy-engine](https://github.com/cosinekitty/astronomy) 2.1.19 | Python dependency, fetched | MIT; Don Cross and contributors; package licence applies. |
| [pyswisseph](https://github.com/astrorigin/pyswisseph) 2.10.3.2 / [Swiss Ephemeris](https://www.astro.com/swisseph/) | Dependency, not bundled | AGPL-3.0 or commercial Swiss Ephemeris licensing as applicable. Distributing a combined work that links pyswisseph is subject to AGPL obligations; Prophet's MIT licence does not remove these. A Swiss commercial licence does not automatically relicense the Python wrapper. Consult upstream terms for the chosen distribution. |
| [seas_18.se1](https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1) | Downloaded by scripts/setup.sh; excluded from release | Swiss Ephemeris licence (AGPL/commercial dual licensing); Astrodienst AG. See [upstream licence](https://github.com/aloistr/swisseph/blob/master/LICENSE). Optional at runtime; Chiron omitted with warning if absent. |
| A. E. Waite, The Pictorial Key to the Tarot (1910), Part III | Original keyword paraphrases in western/data/tarot_rws.json | Underlying 1910 text is public domain. No card artwork is bundled. Prophet's keyword compilation is covered by the project MIT licence. |
| Classical Chinese works via chinese-fortune and Renhuai classics selections | Fetched into vendor; normalised JSONL generated locally, not bundled | Historical works public domain; Wikisource transcriptions CC BY-SA 4.0 where applicable. Keep passage source URLs, edition, revision, licence, attribution and selection metadata. Modern editorial contributions may have separate rights; upstream selections are not critically collated editions. |
| 倪海厦《天纪》 via Renhuai123/ziwei-doushu | Opt-in normalisation only; never bundled | CC BY-NC-SA 4.0: credit 倪海厦 and rights successors, and Renhuai123/ziwei-doushu for structuring; NonCommercial; ShareAlike. Preserve upstream LICENSE.md, source links, and indicate retrieval-field changes. The checkout contains the source, but the default corpus build excludes it. |
| corpus/data/nakshatra.jsonl and parashara.jsonl | Bundled original concise summaries | CC0-1.0; Prophet contributors. Traditional rules summarised independently; no modern translation reproduced. |
| PyJHora | NOT used, copied or installed | Upstream is AGPL. The pyjhora-pvr profile is implemented independently from P.V.R. Narasimha Rao's book description, Vedic Astrology: An Integrated Approach; no PyJHora verification is claimed. |
| B. V. Raman, Graha and Bhava Balas | Numeric reference values cited in tests | Copyright remains with rights holders. No book text or scans bundled. Formula implementation and numeric comparison do not imply permission to redistribute the book. |

The npm lockfile also fetches these support packages; none are bundled in the
source release. Platform-specific packages are installed only where applicable.

| Package | Locked version | Licence (lockfile) |
| --- | --- | --- |
| @babel/runtime | 7.29.10 | MIT |
| @esbuild/aix-ppc64 | 0.28.2 | MIT |
| @esbuild/android-arm | 0.28.2 | MIT |
| @esbuild/android-arm64 | 0.28.2 | MIT |
| @esbuild/android-x64 | 0.28.2 | MIT |
| @esbuild/darwin-arm64 | 0.28.2 | MIT |
| @esbuild/darwin-x64 | 0.28.2 | MIT |
| @esbuild/freebsd-arm64 | 0.28.2 | MIT |
| @esbuild/freebsd-x64 | 0.28.2 | MIT |
| @esbuild/linux-arm | 0.28.2 | MIT |
| @esbuild/linux-arm64 | 0.28.2 | MIT |
| @esbuild/linux-ia32 | 0.28.2 | MIT |
| @esbuild/linux-loong64 | 0.28.2 | MIT |
| @esbuild/linux-mips64el | 0.28.2 | MIT |
| @esbuild/linux-ppc64 | 0.28.2 | MIT |
| @esbuild/linux-riscv64 | 0.28.2 | MIT |
| @esbuild/linux-s390x | 0.28.2 | MIT |
| @esbuild/linux-x64 | 0.28.2 | MIT |
| @esbuild/netbsd-arm64 | 0.28.2 | MIT |
| @esbuild/netbsd-x64 | 0.28.2 | MIT |
| @esbuild/openbsd-arm64 | 0.28.2 | MIT |
| @esbuild/openbsd-x64 | 0.28.2 | MIT |
| @esbuild/openharmony-arm64 | 0.28.2 | MIT |
| @esbuild/sunos-x64 | 0.28.2 | MIT |
| @esbuild/win32-arm64 | 0.28.2 | MIT |
| @esbuild/win32-ia32 | 0.28.2 | MIT |
| @esbuild/win32-x64 | 0.28.2 | MIT |
| dayjs | 1.11.23 | MIT |
| esbuild | 0.28.2 | MIT |
| fsevents | 2.3.3 | MIT |
| i18next | 23.16.8 | MIT |
| lunar-lite | 0.2.8 | MIT |
| lunar-typescript | 1.8.6 | MIT |
| tsx | 4.23.15 | MIT |

Python/npm build tooling is external to this source release. Keep dependency
licence files when packaging an installed environment or executable.
