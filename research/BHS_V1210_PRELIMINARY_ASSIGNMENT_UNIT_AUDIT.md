# BHS v12.10 — Preliminary outcome-free assignment-unit audit

**8 November 2026 | Development evidence only.** This report concerns two manufactured schedules; it does not use physical Fe–Co–Ni measurements, certify lab feasibility, predict a magnetic property, calculate sample size, or demonstrate decision superiority.

## Scientific premise

The V12.9 within-batch pairing assumption is **conditional on how an actual laboratory applies the intervention**. An individually applied after-deposition intervention could in principle be assigned to different coupons from one preparation batch. An intervention on the entire deposition process would instead require physically distinct deposition runs for the reference and modified arms. The corresponding experimental unit is different. This cannot be resolved by software alone.

## Reproducible first local check

- Frozen review protocol: `research/BHS_V1210_ASSIGNMENT_UNIT_FEASIBILITY_PROTOCOL.md`, commit `286f1c4b1aeb22a849bd629ce0f3d8709c4c4ee7`.
- Original inspected V12.9 source archive and negative/mixed conclusions remain untouched on `bhs-v129-attrition-evidence-archive`.
- **Local** source-only test execution: 59/59 passed, including 19 new assignment-unit tests plus 18 V12.8 and 22 V12.9 inherited tests. This is **not** a GitHub Actions result; the new code and tests are not yet committed on this branch.
- Manufactured fixture SHA-256: `adc920e2eba62c7e86ad93b227a0327c692952e0bbb2036907c38326974a5a42`, 15,752 bytes; intended public path `research/BHS_V1210_ASSIGNMENT_UNIT_FIXTURES.json`.
- Local checker SHA-256: `8492d8e317bc0ab51de44364d1f757238c552dbf8a426631ab67efaeb381164d`, 14,802 bytes; intended path `scripts/bhs_v1210_assignment_unit.py`.
- Local adversarial tests SHA-256: `89c920d8c0eacdd28a813d5f62882f0e592f64948f1c77051afffeac09da9b14`, 10,747 bytes; intended path `tests/test_bhs_v1210_assignment_unit.py`.
- First local, non-physical report SHA-256: `455cfee87698b6dabf2da95380ca82593c350ec21ad04dfd4f1a130f3bf94d80`, 26,474 bytes. All 16 single-assignment-event loss cases and both whole-MOKE-session loss cases are retained for each route.

## Structural comparison under the same additive matrix

| Diagnostic | Individually applied post-deposition condition | Whole-deposition-run condition |
|---|---:|---:|
| Proposed coupons | 16 | 16 |
| Intended MOKE technical traces | 48 | 48 |
| Named matched comparison blocks | 8 | 8 |
| Separate deposition runs | **8** | **16** |
| Separately named treatment events | 16 | 16 |
| Nuisance / full matrix ranks | 11 / 12 | 10 / 11 |
| Residual **coupon-row** degrees of freedom | 4 | 5 |
| Processing column distinguishable under declared model | yes | yes |
| One treatment-event loss preserving rank and positive residual df | 16/16 | 16/16 |
| One MOKE-session loss preserving rank and positive residual df | 2/2 | 2/2 |
| Residual row df after loss of one complete session | 1 | 2 |
| Verified physical independence or field calibration | **no** | **no** |

Although both source-only layouts pass elementary rank tests, they use different production-run counts. The observed **one versus two** residual row degrees of freedom after one session loss is not reliable cluster-level inferential precision. It is only arithmetic under the declared fixed-block/session/position/stratum matrix; the true batch covariance and measurement noise have not been established.

These figures are not optimized or independently tested materials experiments. Repeated MOKE traces cannot replace independent treatment-assignment events. The actual batch independence, processing route and relative costs are unresolved; no physical design recommendation follows.

## Audited failure conditions

- Mixing reference and modified coupons within a **single deposition run** when the intervention is defined as a whole-run setting.
- Treating multiple coupons in a shared postprocessing event as individually randomized units.
- Confounding processing with MOKE session or spatial substrate stratum; ignoring compositional gradients.
- Duplicate coupon or instrument slot, fabricated measurement value, changed source identity, missing diffraction or raw MOKE trace plan, altered approval flag and unbalanced treatment units.
- Inflating the independent replication count by multiplying intended technical scans.

The earlier V12.8 saturated plan remains a negative example; V12.9's first-run comparisons remain unmodified. The new results are explicitly local and development-only until exact files are published and GitHub CI checks their preserved SHA-256 identities.

## Conditions required from an external investigator

A qualified Fe–Co–Ni thin-film specialist must identify the *actual* processing contrast, whether it is applied independently to coupons, furnace runs or entire deposition batches; verify local composition/thickness and sample position; examine real equipment calibration, independent processing and synthesis batches, safety, data rights, original measurement chronology and physical costs. They must approve the primary response, minimum meaningful effect in A/m, covariance model and prospective statistical precision plan before measurements. Neither the current manuscript nor its tests assert such authorization.

**Permanent gates:** `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`; `independent_physical_validation_established=false`; `statistical_guarantee_supported=false`; `real_savings_measured=false`; `claim_of_superiority=false`.

Scientific context: Lazic, Clarke-Williams and Munafò (2018), DOI 10.1371/journal.pbio.2005282; combinatorial thin-film position effects https://onlinelibrary.wiley.com/doi/10.1002/mgea.87.

