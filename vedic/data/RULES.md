# Prophet Jyotish 1.0 rules and provenance

Runtime is offline. Only pyswisseph and the Python standard library are used.
All birth timestamps retain their original clock values; UTC conversion uses
zoneinfo. Moshier sidereal coordinates use Lahiri, geocentric apparent positions,
and mean nodes by default. Ketu is precisely opposite the selected Rahu.
Whole-sign houses start at the sidereal ascendant sign.

## Sources

* Swiss Ephemeris programmer reference: https://www.astro.com/swisseph/swephprg.htm
  `get_ayanamsa` takes TT; `get_ayanamsa_ut`, `calc_ut`, and `houses_ex` take UT.
* BPHS, Shodashavarga, planetary characteristics, Vimshottari and Ashtakavarga
  chapters (chapter numbering varies by edition). No PyJHora code is imported,
  copied, or installed. The `pyjhora-pvr` profile is implemented from PVR's published description; not verified against PyJHora.
* dashaflow MIT reference commit f8f8ead76e56b9048f80adbbbff282c007068cf7:
  https://github.com/adarshj322/dashaflow . Constant tables adapted into
  `_tables.py`; copyright and permission retained in `_dashaflow/LICENSE`.
* Classical Ashtakavarga variant comparison: Phaladeepika chapter 23, verses
  3–9, including the Parashara variant footnote under verse 8:
  https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621595.html

## Explicit profile differences

The default `parashara` BAV profile uses the BPHS contribution convention below.
All other contributions are the same as the pinned dashaflow table. Each row
lists favorable positions counted inclusively from the source sign:

| Recipient / source | parashara | dashaflow |
| --- | --- | --- |
| Moon / Moon | 1,3,6,7,9,10,11 | 1,3,6,7,10,11 |
| Moon / Mars | 2,3,5,6,10,11 | 2,3,5,6,9,10,11 |
| Venus / Mars | 3,4,6,9,11,12 | 3,5,6,9,11,12 |

Both profiles total Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56,
Venus 52, Saturn 39; SAV totals 337. All arrays run Aries through Pisces.
BAV is unreduced; Lagna contributes to each BAV but has no separate SAV row.
The returned contribution arrays make the complete selected table auditable.

Dignity uses permanent friendship to the sign lord. Moolatrikona is evaluated
before sign exaltation with half-open degree ranges: Sun Leo 0–20, Moon Taurus
3–30, Mars Aries 0–12, Mercury Virgo 15–20, Jupiter Sagittarius 0–10,
Venus Libra 0–15, Saturn Aquarius 0–20. Exaltation and debilitation are sign
categories outside these ranges, not orb-based strengths. Node dignities are
left unassigned because schools disagree.

D9 uses longitude * 9 modulo 360. D7 starts from the natal sign for odd signs
and the seventh for even signs. D10 starts from the natal sign for odd signs
and the ninth for even signs. D12 starts from the natal sign. Count all parts
forward; Aries has odd sign number 1. Only sign and house placements, rather
than divisional degrees or strength estimates, are returned.

Vimshottari uses 365.25 days/year and a 120-year cycle. The first full maha
starts before birth according to the elapsed fraction of the Moon's nakshatra.
Antar/pratyantar periods divide the full original parent; no restart at birth.
The timeline includes that full birth maha and the next nine mahas, covering
at least birth+120 years. Periods are half-open [start,end) UTC timestamps.
A query outside timeline coverage returns an empty current mapping. `--at`
is interpreted at midnight in the birthplace timezone; omitted means now.

## Validation and limitations

`bin/prophet selftest -k vedic` checks Lahiri J2000 TT 23.85 +/- .02 degrees,
the BAV totals, exact profile contribution differences, classical divisional
boundaries, full Ketu 7 years at 0 Ashwini, birth-balance subdivision continuity,
and the Delhi fixture in dashaflow's public tests (1990-04-15 14:30 IST,
28.6139N, 77.2090E): Leo ascendant, Aries Sun, Scorpio Moon, Capricorn Saturn,
Aquarius Mars, Gemini Jupiter. It also checks fictional exact and approximate birth fixtures.

Approximate-time stability means agreement among 15-minute samples and both
endpoints, not proof of invariance over the continuous interval. Unknown times
are rejected instead of interpreting the shared noon placeholder. No automatic
rectification, yogas, D60, or BAV reductions are implemented. Shadbala is optional
and follows the documented Raman/Sripathi method below.
`--save-cache` requires a person and uses the shared cache writer; command,
query date, levels, resolved inputs, and rules distinguish cache files.


## Round 2: profiles and compatibility

The default `engine.rules` dictionary is unchanged, including legacy descriptive
strings. New option defaults and their citations live in additive `rules_ext`.
Only a non-default `--node-dignity` adds `engine.rules.node_dignity`; selecting a
new BAV profile uses the existing `bav_table` key. `--shadbala` changes the cache
identity only when enabled. Existing keys, meanings, defaults, and varga output
sets are preserved. No existing cache files are rewritten.

`--node-dignity none` remains the default. `bphs` follows the commonly translated
BPHS ch.3 planetary characteristics (e.g. R. Santhanam): Rahu exalted Taurus,
debilitated Scorpio, moolatrikona Gemini, own Aquarius; Ketu exalted Scorpio,
debilitated Taurus, moolatrikona Sagittarius, own Scorpio. Exaltation takes
precedence over overlapping own sign. `gemini-sagittarius` uses the later-text /
South-Indian convention Rahu exalted Gemini, debilitated Sagittarius, Ketu the
reverse. Own Virgo/Pisces is noted as a variant and is not assigned by that
profile. Other signs stay unassigned; permanent friendship is not extrapolated
for nodes. Outputs carry the chosen convention and citation text.

`--bav-table varahamihira` aliases the pinned dashaflow table. `pyjhora-pvr`
is an independent table adaptation from P.V.R. Narasimha Rao, *Vedic Astrology:
An Integrated Approach*, Ashtakavarga chapter, “Controversies”. PVR also discusses
JHora's mixed definitions in the IndiaDivine thread “Ashtakvarga issue in JH”.
This implementation uses no PyJHora code and makes no PyJHora output comparison.
The output states “implemented from PVR's published description; not verified
against PyJHora”. Relative to dashaflow/Varahamihira it applies:

* Moon / Moon: add 9.
* Moon / Mars: remove 9.
* Moon / Jupiter: add 2, remove 12.
* Venus / Mars: add 4, remove 5.

The legacy default `parashara` applies all but the Moon/Jupiter change. Its
new `notes` field explicitly explains that partial difference from PVR's reading
of Parasara; its table is unchanged. `bav_profile_source` identifies provenance.
All profiles retain totals 48/49/39/54/56/52/39 and SAV 337.

## Raman Shadbala

Use `vedic shadbala <birth args>` or `vedic chart <birth args> --shadbala`.
Chart results add a `shadbala` key only when requested. Approximate births retain
all 15-minute branches; `shadbala_strong` is included in sample invariants.
The pure function `vedic._shadbala.calculate_shadbala` accepts longitudes, speeds,
lagna, MC, ayanamsa, meridian distance in hours, hours from preceding sunrise,
day length, weekday/year/month lords, mean longitudes and seeghrochchas.
Optional `krantis` and Mercury benefic status support historical intermediates.
It returns all six virupa components, detailed Sthana/Kala terms, varga rows,
signed aspect contributions, total virupas/rupas, required rupas, ratio, strong
flag, ishta and kashta phala, input provenance, engine and warnings.

Source: B.V. Raman, *Graha and Bhava Balas*. Tests cite numeric
reference values only; no book text is distributed. This is an independent implementation
of the book's primarily Sripathi formulation, not a claim that every BPHS edition
uses identical rules. Sthana uses seven vargas D1/D2/D3/D7/D9/D12/D30 with
compound friendship (temporary relation measured in natal Rasi), D1-only
moolatrikona, unequal Parashari trimsamsa, odd/even Rasi/Navamsa, sign-based
kendras, and gendered drekkana strength. Dig uses actual angular longitudes,
not whole-sign house boundaries. Kala includes all nine terms: natonnata,
paksha (Moon doubled), tribhaga, abda, masa, vara, hora, ayana and yuddha.
The Hindu weekday changes at sunrise. Horas are fixed 60-minute intervals after
sunrise, as in Raman art.69, rather than unequal seasonal hours. Year/month
lords use Raman's condensed Ahargana from 1827-05-02, counted inclusively,
with 360/30-day years/months. Solar-day date is determined at local mean time.
Apparent noon uses Swiss equation of time. Sunrise/set are solar-disc centre
without refraction, altitude zero; polar dates lacking these events are rejected
when Shadbala is requested, rather than inventing an event.

Ayana uses Raman's six piecewise-linear declination increments totaling 24°;
planetary latitude is ignored. Mercury is treated as afflicted when sharing a
sign with Sun, Mars, Saturn, or a weak Moon, unless explicitly overridden in the
pure function. The Moon benefic interval is elongation 90–270°, following art.53.
Drik uses piecewise angular aspects plus Mars/Jupiter/Saturn special strengths,
then divides the signed sum by four. Yuddha uses the fixed disc diameters of
art.77 and the pre-ayana subtotal; the western planet wins, including across
0 Aries. Exact ties deterministically follow planet order. Multiple wars are
reported as pairwise adjustments; the worked reference has no war.

Chesta uses the book's mean/true average and seeghrochcha, not a speed proxy.
True longitude is unwrapped about its mean before averaging. Runtime means
use Raman's 1900-01-01 midnight at 76°E epoch with constant daily rates derived
from Tables IV–IX and the printed secular corrections. These historical linear
mean-motion approximations are not modern osculating orbital elements; there
is no claimed precision equivalence to another astrology package. Speeds are
retained for audit. Sun and Moon have zero Chesta in the sixfold total (ex.56);
arts.136–137 supply separate `phala_chesta` for ishta/kashta. Naisargika uses
the printed art.108 decimals. Required rupas follow art.122: 5/6/5/7/6.5/5.5/5.

### Reference discrepancies and tolerances

Tests feed art.6 longitudes, art.7 lagna/MC, art.5 natha/day length and ex.99–105
mean/seeghrochcha intermediates. They use ex.32 rounded krantis explicitly:
Moon's Sayana conversion there differs by one degree from art.6. Saptavargaja
matches all seven ex.13 values exactly. Sthana matches within 0.12 virupa:
Mars's ex.3/ex.13 uchcha is printed 37.06 although 111°30′34″ / 3 = 37.1698.
Other differences are small printed rounding errors. Dig uses MC 216°30′ from
art.7 instead of ex.14's 216°36′. Kala/Chesta/Drik agree within 0.10 virupa using
the book's krantis. Mars Kala is 30.06 in ex.35 but 33.06 in ex.56. Saturn's
seeghrochcha is mean Sun per art.101/ex.49, not ex.104's isolated 151.23 typo.
Moon's saptavargaja ex.9 row sums to 48.75, as ex.13 prints, rather than 49.75.
Mercury ex.56 sums to 537.02 virupas (~8.95 rupas), although its printed rupas
are 8.85. Saturn's ex.56 natural strength 8.37 conflicts with art.108's 8.57;
we use art.108. These errors are documented, not reproduced as formula changes.
Calculated final rupas are approximately 7.084/6.497/4.972/8.949/7.229/6.269/6.486,
within 0.15 rupa of all seven published ex.56 totals. The pure function and
Fictional exact/approximate-birth CLI paths have regression checks. War and the historical
mean-motion extrapolation lack an independent published worked chart beyond
the no-war Standard Horoscope; their conventions are exposed for audit.
