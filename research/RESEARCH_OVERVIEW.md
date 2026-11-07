# BHS — Research overview and evidence boundaries

Bayesian Hypothesis Search is an independent scientific software research effort exploring explicit probabilistic hypotheses, evidence updates, uncertainty diagnostics and the selection of informative computational or experimental evaluations.

## Research paths

**Hypothesis discrimination** seeks to distinguish genuine, falsifiable scientific explanations using independently justified priors and likelihoods, realistic experimental feasibility and appropriate costs. This remains a research objective rather than a demonstrated capability on independently validated physical hypotheses.

**Property optimization** is a different task: retrospectively choose recorded candidates to maximize a measured property. Development experiments on the NIST Fe–Co–Ni historical Kerr data used 921 eligible anonymous-composition observations. The experimental mathematical response families are not validated physical mechanisms.

## Results and verification

- **v1:** original BHS–BMA–EI produced worse mean normalized final regret than GP–EI: 0.13924594 vs 0.02500128 (three development seeds, 15 acquisitions).
- **v2:** post-hoc parameter/model choices affected outcomes substantially; those comparisons are not independent.
- **v3:** both GP and BHS predictors severely undercovered nominal 90% intervals. On random acquisition histories: 43.3% coverage for the original GP and 28.3% for BHS–BMA.
- **v4:** 540 prequential development diagnostics, with 36 synthetic/contract tests passing in GitHub Actions; numerical outcomes did not establish a calibrated physical error model.

The [four preserved aggregate JSON reports](./) and relevant [GitHub Actions run](https://github.com/busrakisik/inverse-materials-design/actions/runs/42046318788) document exploratory results. They do not establish the superiority of BHS, a new material, a physical discovery or a laboratory cost advantage.

**Hard scientific limits:** `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`. The reserved independent seed IDs 10000–10099 have not been used. The NIST source's composition columns have not been authoritatively mapped to Fe, Co and Ni.

## Subsequent direction

Seek separately sourced, legally usable data and domain-reviewed physical hypotheses. Define observables, experimental costs, uncertainty assumptions, pre-reveal isolation and strong baselines before running further evaluations. The proposed external validation phase is a plan, not independently confirmed scientific evidence.

The initial [Zenodo software release](https://doi.org/10.5281/zenodo.21761835) predates the research branch. Preserved experimental reports and source citations should be considered in their original evidence scope.

## Evidence sufficiency under scientifically necessary assumptions — v6

In the UCI 28-day concrete data, BHS evaluated whether the measurement records could justify an actual recommendation about water-to-binder ratio. Tight matching produced just **one** disjoint observational pair (±5 kg/m³ among six other ingredients), versus **11** at ±15 and **52** at ±30 kg/m³; increasing tolerance weakens comparability. Identical recorded mixture inputs had discordant strength outcomes (maximum within-group span 12.61 MPa), and key material-lot/curing/test metadata were unavailable.

The explicit decision was to **abstain from a causal or laboratory recommendation**, not to claim that the usual strength–water/binder direction was validated. [Assumption protocol](CONCRETE_ASSUMPTION_AUDIT_V6.md) · [Real-data development report](CONCRETE_ASSUMPTION_AUDIT_V6_RESULT.md) · [Source/tests](../scripts/uci_concrete_assumptions_v6.py).

## External real-data development, 6 November 2026

A new exploratory 28-day UCI concrete data experiment used 416 unique feature profiles from a published source (Yeh, DOI 10.24432/C5PK67; CC BY 4.0). Three paired development seeds and fixed 10-step acquisition budgets yielded mean normalized final simple regret of 0.242408 (random), 0.095889 (GP–EI), and 0.097209 (kernel portfolio EI). The portfolio did **not** outperform GP–EI. See [full exploratory evidence and limitations](UCI_CONCRETE_V5_FIRST_REAL_DEVELOPMENT_RESULT.md) and [aggregate reviewed JSON](uci_concrete_development_v5.json).

This is a retrospective **property optimization** comparison, not physical hypothesis discrimination, independent scored validation, calibration, real acquisition-cost measurement or a new materials discovery. All independent validation safeguards remain in effect.

## Evidence sufficiency before consequential action (v7)

A deterministic decision contract now distinguishes descriptive, observational, and laboratory-action evidence requirements. Missing or contradicted assumptions cause explicit information requests or refusal; a claimed risk bound requires independently documented provenance, and even a complete case is only eligible for external expert review, never autonomous laboratory action. The historical v6 UCI source permits descriptive reporting but lacks **four** evidence categories for observational assessment and **nine** for laboratory review. The [method note](BHS_EVIDENCE_SUFFICIENCY_V7.md) and [development output](bhs_evidence_sufficiency_v7.json) preserve the scope; this is a formal software contract, not prospective validation of reliability or practical savings.

## Review-record integrity and falsifiable decision evaluation (v8)

The [v8 source/review integrity preflight](BHS_PROVENANCE_INTEGRITY_V8.md) extends the tested v7 evidence contract with explicit risk-unit comparability and an out-of-band reviewer trust boundary. Tampered, expired or untrusted review packets fail closed. **Sixteen synthetic adversarial contracts** passed; real measurement validity, probability calibration and a benefit over simpler decision policies remain **unproven**. The [prospective study design](BHS_PROSPECTIVE_DECISION_RELIABILITY_STUDY_DESIGN.md) defines matched-coverage selective risk, abstention burden, measurement costs and independent control/baseline requirements before any PhD-level or commercial effectiveness claim.

## Observation-identical causal worlds (v9)

The [v9 structural counterexample](BHS_CAUSAL_NONIDENTIFIABILITY_V9.md) is a fully **synthetic, exact mathematical demonstration**: two worlds with identical observable `P(A,Y)` have opposing mean intervention effects `+5` and `-5` (arbitrary response units). Under a stated illustrative regret model, always selecting either intervention has worst-case regret 5, the minimax randomized choice has regret 2.5, and abstention with an *assumed* cost of 1 has regret 1. These are **not measured laboratory benefits, calibration outcomes, or a new theoretical discovery**.

The [stored exact output](bhs_v9_exact_counterexample.json), [tested guard](../bhs/decisions/causal_nonidentifiability_v9.py) and regression tests prevent a signed document or source metadata from being confused with a justified causal intervention. Agreement among a finite list of possible worlds never proves that all physically plausible worlds have been considered. The essential next step remains **controlled independent scientific evidence** and decision risk–coverage evaluation, not more software model variants.

## Real experimental replicate dependence (v10)

A [new source-locked audit](BHS_REPLICATE_LEAKAGE_AUDIT_V10_RESULTS.md) examines **1,800 actual mechanical measurements** from 600 distinct 3D-printed geometries, each experimentally repeated three times (Liang et al., 2021; Gongora et al., 2020). The exact external Git source is pinned; BHS did not carry out the physical experiments.

Random measurement-row validation exposes **92.4%** of test measurements at geometries already present in training (mean development MAE **3.81 J** for a fixed Random Forest reference), whereas physically distinct geometry-group validation has **0%** overlap (MAE **4.79 J**). The largest measured triplicate response range is **37.30 J**. These observations show why replicate identity and unobserved geometry must be distinguished; differing split populations prevent attributing the complete error difference solely to leakage.

The [predeclared protocol](BHS_REPLICATE_LEAKAGE_AUDIT_V10_PROTOCOL.md), [checked code](../scripts/bhs_replicate_leakage_v10.py), [tests](../tests/test_bhs_replicate_leakage_v10.py) and [aggregate evidence](bhs_replicate_leakage_v10.json) are available. Results are **retrospective development only**, not proof of BHS algorithm superiority, causal inference, measured economic benefit or independently verified laboratory recommendations.
