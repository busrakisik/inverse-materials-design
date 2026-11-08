# BHS v12.9 — Original outcome-free design attrition audit

**8 November 2026. Development-only structural plan comparison. No real specimen, magnetic measurement, outcome-based score, external validation, laboratory permission or recommended physical sample size.**

## Reproducible record

- Predeclared design and loss protocol: `research/BHS_V129_ATTRITION_RESILIENCE_PROTOCOL.md`, Git blob `317438b1b66cd68d71bd498e3a498ead8abcb98e`.
- Pair of outcome-free specimen schedules: `research/BHS_V129_DESIGN_VARIANTS.json`, Git blob `0dbd73ce65c48239e94a8e611faa450056217f8d`; original SHA-256 `e65e85a6c2d1a8fed749fdd3502c9021343ca53bb01fb0ec06306101961abde6`, 11,783 bytes.
- Implementation: `scripts/bhs_v129_design_attrition.py`, Git blob `32e8a47b93543336621289446b3ca89ec7dc78e6`.
- Adversarial tests: `tests/test_bhs_v129_design_attrition.py`, Git blob `908c1cb65f7dd925c1e7e0bc480d458548946aae`, 22 new tests.
- GitHub Actions: https://github.com/busrakisik/inverse-materials-design/actions/runs/42464245885, **SUCCESS 162/162 tests** (140 inherited + 22 new). Original result artifact ID `13610986166`.
- Original deterministic JSON `runs/bhs_v129_design_attrition.json`, SHA-256 `4fa0af8d2947a89153e1a7a07d6b2553d63e956c1ad86ea2a598d5b43a6da28f`, 14,663 bytes. The first GitHub output and an independent local execution match this checksum exactly.
- Kayıpsız arşiv: `research/bhs_v129_first_design_attrition.json.xz`, SHA-256 `b12e043f4c5141809c88e116f3a175e694ad1966230aa3891bffd43dec9e40a5`, Git blob `272e9c4e6a68300e3ef856c11919ba0fcb3737eb`, 1,164 bytes.

## Fixed comparison

Each artificial layout has sixteen distinct proposed coupons, eight **named** synthesis batches, two hypothetical MOKE sessions and three planned technical MOKE traces per coupon. Technical traces are **not** independent deposited specimens. The coupon-level processing contrast remains a scientifically unapproved assumption.

| Diagnostic | Cross-session batch pairs | Within-session batch pairs |
|---|---:|---:|
| Coupon rows / named batches / planned traces | 16 / 8 / 48 | 16 / 8 / 48 |
| Full design nuisance rank | 11 | 10 |
| Full design rank with processing indicator | 12 | 11 |
| Residual **coupon-row** degrees of freedom | **4** | **5** |
| Algebraic contrast estimable with no dropout | Yes | Yes |
| One synthesis-batch-loss scenarios maintaining algebraic rank and positive residual df | **8/8** | **8/8** |
| One MOKE-session-loss scenarios maintaining algebraic rank and positive residual df | **0/2** | **2/2** |
| Mathematically independent groups after one session loss | Not established | Not established |

After one batch is removed, the cross-session arrangement has 14 coupons, seven named batches, rank 10/11 (nuisance/full) and residual df 3; within-session arrangement has rank 9/10 and residual df 4. These values hold for every one of the eight batch-deletion scenarios.

After one MOKE session is removed:
- **Cross-session**: eight surviving coupons belong to eight different batches, with no surviving matched reference/modified pair. The nuisance and full model both have rank 8, residual df 0, and processing is **not estimable** in the stated matrix. Both session-loss scenarios fail.
- **Within-session**: eight surviving coupons constitute four matched reference/modified batch pairs, with nuisance/full ranks 5/6 and residual df 2. Processing remains algebraically distinguishable in both session-loss scenarios. Nevertheless, only four named synthesis batches survive and no real batch independence or valid group-robust uncertainty estimate has been established.

The within-session model nests session identities within synthesis batches, so the session main effect cannot be separately inferred from batch effects. Exact rank accounts for this aliasing; it is not permission to ignore drift, batch-to-batch noise or real physical confounders.

### Preservation of the earlier failure

V12.8's original eight-coupon sample, Git blob `3cde6a6ad809effdf21fcdd50ab737c8cfaf07e8`, remains untouched: nuisance rank 7, full rank 8 and **zero residual degrees of freedom**. Multiplying technical trace counts by ten does not change the number of coupons, independent batch identifiers, rank or residual df in V12.9. This demonstrates why repetition cannot be counted as fresh independent specimens.

## Why this is not experimental evidence

- The *nominal robustness condition* is only a rank increment and positive coupon-row residual df under an additive model with batch/session/linear-position nuisance terms. It makes **no statement** about causal identification, unmodeled effects, adequate experimental power or valid cluster-aware confidence intervals.
- Eight labeled batches are **not eight verified independent synthesis batches**. A domain expert must verify physical preparation, processing feasibility and provenance.
- Both demonstrations assume a treatment can be assigned to two coupons from the **same deposition batch**; this may be impossible for some processing routes. If treatment must be applied at whole-batch level, these fixtures do not address the correct experimental unit and must not be used to choose laboratory operations.
- A loss of an entire measurement session could be informative (apparatus failure, drift, missingness not at random), requiring additional domain and missing-data analysis.
- No physical MOKE or diffraction traces, material costs, calibrated noise estimates, effect size in A/m, source rights or approved minimum meaningful effect are available. Neither 16 coupons nor eight batches is endorsed as a real sample size.

## Next independent prerequisites

A suitable magnetic thin-film investigator must decide whether physically paired reference/modified treatments can be prepared inside a synthesis batch; whether specimens can be measured in the same instrument session; what the randomized assignment, batch independence, nuisance structure, field calibration, original magnetic/diffraction trace retention and failure logging would actually entail. The lab must precommit a meaningful effect threshold in A/m, uncertainty and sample-size/precision calculations using realistic within- and between-batch variation, genuine measurement costs, and an independent outcome-validation partition.

Do not optimize towards this previously viewed manufactured result and portray it as independent confirmation. The original V11 negative comparison, nonpassing first V12 replay and V12.3–V12.8 mixed/negative evidence remain unchanged. The public default branch, old release tags and protected seed range are untouched.

**Decision:** `NO_GO_EXTERNAL_LAB_AND_PRECISION_REVIEW_REQUIRED`. `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`; `independent_physical_validation_established=false`; `formal_power_or_precision_established=false`; `statistical_risk_guarantee_supported=false`.

Methodological reading: https://academic.oup.com/ije/article/52/5/1648/7172835 — correlated outcomes require appropriate design and analysis; not a direct endorsement of these fixtures.
