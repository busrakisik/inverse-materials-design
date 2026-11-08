# BHS v12.10 — First frozen processing-scope development evidence

**8 November 2026 | No physical observations, laboratory action, prospective validation, tested physical hypothesis or demonstrated resource savings.**

## Purpose and immutable lineage

V12.9 compared two hypothetical session layouts for paired reference and modified Fe–Co–Ni coupons. Both required an unverified assumption that the two treatments could be independently assigned *within one deposition batch*. V12.10 separates the physically distinct **post-deposition, independently treated coupon** and **whole-deposition-run treatment** routes.

The protocol and all failure conditions were recorded before the new GitHub Actions source-only assessment at `research/BHS_V1210_ASSIGNMENT_UNIT_FEASIBILITY_PROTOCOL.md`, commit `286f1c4b1aeb22a849bd629ce0f3d8709c4c4ee7`. This is a **development comparison based on the already viewed V12.9 design structure**, not an independent performance experiment.

Source commit: `24090be9adc7a6ba7d672e7ab9f8ad33033bb47a`.

- New fixture `research/BHS_V1210_ASSIGNMENT_UNIT_FIXTURES.json`: Git blob `e93e5630cbae7c63dcbb069a0a095b3182a3f349`, SHA-256 `adc920e2eba62c7e86ad93b227a0327c692952e0bbb2036907c38326974a5a42`.
- New checker `scripts/bhs_v1210_assignment_unit.py`: Git blob `a41a34962710d31965477b3533f2bba6ba5a7c2b`.
- Adversarial contracts `tests/test_bhs_v1210_assignment_unit.py`: Git blob `9c66286ca6fe93153909b3dd9f3fa9fc696ec030`.
- Pinned CI `.github/workflows/bhs-v1210-assignment-unit.yml`: Git blob `56d73695583cfab357039094a624edb4d4deb3e4`.
- Successful GitHub Actions run: https://github.com/busrakisik/inverse-materials-design/actions/runs/42466850732; **181/181 tests** (162 prior, 19 new); no test failure.
- Original Actions result artifact `13612405751`. Its JSON bytes were independently compared with the locally generated result, **identical at 26,474 bytes**; SHA-256 `455cfee87698b6dabf2da95380ca82593c350ec21ad04dfd4f1a130f3bf94d80`.
- The exact JSON is retained as lossless `research/bhs_v1210_first_assignment_unit.json.xz`, compressed SHA-256 `ac21272ba9ae147eab24b24149051ed69ccaec30e57452e0667f2bc5b8af5ad3`, compressed Git blob `7dbac569519e0c8e1ed48ca0a31242a52f03bf76`. Restoration must recover the original JSON hash.

## Full-plan and removal diagnostics

All counts below describe **manufactured candidate schedules**; named synthesis runs are not independently verified experiments.

| Structural diagnostic | Independently applied coupon-level post-deposition route | Whole-deposition-run route |
|---|---:|---:|
| Planned coupons | 16 | 16 |
| Planned MOKE technical traces | 48 | 48 |
| Named comparison blocks | 8 | 8 |
| Separate deposition runs | **8** | **16** |
| Separate named treatment events | 16 | 16 |
| Nuisance/full additive rank | 11/12 | 10/11 |
| Residual **coupon-row** degrees of freedom | 4 | 5 |
| Treatment column distinguishable in this matrix | yes | yes |
| Individual treatment-event deletions retaining nominal structural pass | 16/16 | 16/16 |
| Entire MOKE session deletions retaining nominal structural pass | 2/2 | 2/2 |
| Complete paired comparison blocks after session deletion | 4 | 4 |
| Residual **coupon-row** df after session deletion | **1** | **2** |
| Physical treatment assignment verified | **no** | **no** |
| Statistically valid clustered precision or sample size | **not established** | **not established** |

The apparently greater residual row df for the whole-deposition-run route is not evidence that it is more accurate, cheaper or feasible. A single complete session loss leaves only four named comparison blocks; valid group-aware uncertainty is unverified. Neither scenario contains physical observations or known outcome/measurement variance. Intended MOKE traces cannot increase the number of treatment-assignment units.

## Negative controls and interpretation

The implementation rejects a whole-deposition-run intervention declared as two opposite arms in the same synthesis run; multiple coupons sharing a purportedly independent postprocessing event; treatment/session or treatment/specimen-position confounding; duplicate sample/slot IDs; missing original MOKE/XRD trace plans; forbidden physical claims and manufactured response values. These software failures do not establish how any actual collaborator's tools operate.

The question **which physical processing route is scientifically possible** remains unresolved. Co-sputtered film location can correspond to changed composition or thickness; position balancing is not a substitute for an independently verified composition map or matched thickness. A defensible real analysis needs a partner-reviewed process contrast, treatment assignment at the true physical unit, independently reproduced batches, authentic raw traces, calibrated field and structural measurements, predeclared meaningful response threshold, uncertainty model, safety, source rights and real costs.

## Release boundaries

- `physical_measurements_performed=false`
- `actual_treatment_assignability_verified=false`
- `formal_sample_size_established=false`
- `statistical_guarantee_supported=false`
- `independent_physical_validation_established=false`
- `physical_recommendation_allowed=false`
- `laboratory_action_allowed=false`
- `status=NO_GO_EXTERNAL_PROCESSING_SCOPE_AND_LAB_REVIEW_REQUIRED`

V11's unfavorable original comparison, first V12 replay parity failure and V12.3–V12.9 negative/mixed results remain unchanged. No reserved independent seed, released version tag, Zenodo evidence, public default branch or external physical source has been modified.

Method references: experimental units and repeated measurements (Lazic et al., 2018; DOI `10.1371/journal.pbio.2005282`) and combinatorial film composition-position variation (https://onlinelibrary.wiley.com/doi/10.1002/mgea.87).
