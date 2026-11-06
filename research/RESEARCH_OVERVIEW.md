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
