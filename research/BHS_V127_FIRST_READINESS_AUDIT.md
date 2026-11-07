# BHS v12.7 — First scientific pilot readiness audit

**7 November 2026 | Proposed Fe–Co–Ni thin-film study | Development-only structural evidence**

## Outcome

**NO_GO_EXTERNAL_REVIEW_REQUIRED**. The first code-checked pilot passport contains **27 unresolved scientific, physical, institutional and resource conditions**. It contains no new sample measurements, no physical posterior update, no independent evaluation and no laboratory authorization. This is a legitimate readiness failure, not evidence that a physical hypothesis has been refuted.

- First-pass software and earlier method contracts: **122/122 successful** in https://github.com/busrakisik/inverse-materials-design/actions/runs/42389697957.
- Exact source commit `595b331296271a2359d36e6b11240d8e4ca8a245`.
- Candidate protocol Git blob `4a31f403c580b91dca475c2fd373c93cb2350c87`.
- Candidate passport Git blob `d3fb4c46092ac8e51959d8cecbf0d2a365dec663`, raw SHA-256 `5b817799e331b341bb306a25aae1a99d95322e38c46156ddc263ebf6784906e7`.
- Passport checker Git blob `9902f5fe18b5e34afa061c90c856ae954bee87ec`.
- First readiness result JSON SHA-256 `f9a2674e68aca13daf8e944acdd7c140554c1c76d5e601c1741d32f4d55d7256` (1,813 bytes), Git blob `d4d912fc99890e72ed5a98eaf8992a5e46361c52`.
- Original GitHub Actions artifact ID `13581151816`. A byte-exact copy of its inner JSON is preserved as `research/BHS_V127_FIRST_PILOT_READINESS.json`.

## Outstanding scientific and operational conditions

| Domain | Unresolved | What a responsible collaborator must establish |
|---|---:|---|
| Experimental design | 13 | Verify material composition; define processing conditions, substrate/thickness controls, independently collected calibration/evaluation batches, measurement chronology, randomization, nuisance variables, structure contrast, meaningful effect in A/m, measurement uncertainty, sample size and missing-data rule |
| Provenance and rights | 2 | Verify the actual source/license and immutable source fingerprint; an old inspected NIST composition library cannot serve as independent prospective data |
| Institutional and physical governance | 5 | Confirm a qualified laboratory partner, investigator review, source rights, approved experiment safety and independent protocol registration |
| Measurement instrumentation | 2 | Verify MOKE magnetic-field calibration and X-ray measurement calibration with original records, not merely a self-declared checkbox |
| Actual resource model | 5 | Set an allowed response budget, observed cost and duration per response, currency/cost unit, and externally approved abstention cost |
| **Total** | **27** | **Physical experiment and performance claims remain blocked** |

The exact alphabetically sorted blocker keys are in the original JSON. Empty fields are not replaced with fabricated plausible values. A passport with all reported fields filled still cannot prove authentic external approval or real physical evidence: the checker always rejects action/release until a separate, independently verified procedure exists.

## One-page collaborator feasibility conversation

**Research question.** In Fe–Co–Ni magnetic thin films, does a *lab-approved processing contrast*, at matched independently verified composition, film thickness, substrate and measurement geometry, produce a reproducible change in coercive field beyond a jointly declared meaningful threshold, accompanied by a separately verified diffraction-observed structural contrast?

**Rival explanations.** H0 expects no reproducible above-threshold processing-associated coercive-field contrast at matched conditions. H1 expects a reproducible coercive-field contrast together with an independently measured structural contrast. Neither is mechanistically exhaustive. An association alone does not demonstrate texture causality: annealing or other processing can modify strain, roughness, composition segregation and defects.

**Requested feasibility answer from a research partner:** Which specimen-production route and two safe processing conditions are actually feasible? Are magneto-optical Kerr hysteresis and X-ray structural scans available, with auditable calibration logs? Can a laboratory obtain true independent synthesis batches, verified composition and film thickness, original raw traces and timestamped repeats? What measurement precision, meaningful effect threshold, sample/batch count and real cost can be justified *before* observations? What institutional safety, data-rights and investigator reviews are required? If any of these cannot be established, the pilot remains on hold.

**Baselines.** A fixed expert-reviewed measurement plan, a composition-only reference, a structure-aware reference, and an explicit defer-without-action rule; comparisons require equal actual experimental budget and prespecified loss/coverage metrics. The older mathematical linear/quadratic/oscillatory models are not physical mechanism claims.

**Physical actions.** All fabrication and measurements are supervised and decided by the responsible laboratory. This project provides no instrument operating instructions, no source access grant, no prospective sample and no verified economic saving.

## Evidence preservation

V11's unfavorable component comparison; the first V12 historical parity failure; and V12.3–V12.6 mixed and negative findings remain unchanged. This report neither selects a successful subset nor changes old source or calibration thresholds. Public main and prior draft reviews remain unmerged. Historical release tags have not been rewritten.

**Hard status:** `structural_contract_passed=true`; `independent_physical_validation_established=false`; `laboratory_action_allowed=false`; `physical_recommendation_allowed=false`; `posterior_calibration_established=false`; `statistical_risk_guarantee_established=false`; `real_savings_measured=false`.

Reference context: https://pages.nist.gov/remi/data/ ; https://doi.org/10.1088/0022-3727/33/12/304 ; https://doi.org/10.3379/jmsjmag.15.S1_113.
