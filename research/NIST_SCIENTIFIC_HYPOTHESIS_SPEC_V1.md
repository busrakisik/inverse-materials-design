# BHS — NIST Fe–Co–Ni Scientific Hypothesis Specification v1

**Status: Research-question and claim-gate specification ONLY; no physical-mechanism verification, model fitting or real-data benchmark.**

## Source-verified motivation

- NIST REMI and Wang et al. (2022) describe a 921-sample experimentally acquired Fe–Co–Ni thin-film library, with composition, XRD, Kerr rotation in mrad and magnetic coercivity in mT.
- Wang et al. present a **materials property optimization** benchmark, not a ground-truth classification benchmark identifying true causal physical mechanisms. They describe a relatively smooth Kerr landscape and more locally complex coercivity landscape. Expected Improvement performed strongly in their acquisition-function study.
- This *descriptive* rationale motivates **Kerr as the proposed initial pilot response** and coercivity as a secondary stress/complexity comparison, not a validated method choice or an outcome chosen by fitting our BHS policies.

Primary: https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery
Full paper: https://academic.oup.com/ooms/article/2/1/itac006/6637521
Source data: https://pages.nist.gov/remi/data/
Source pinned commit: `usnistgov/remi@596b04435fb577175264a70c4434f5539b809510`; source `.mat` blob SHA-1 `e506db115d522d62618042abead7df2695ccf13e`.

## Primary research question — deliberately modest

**Can predeclared phenomenological composition-response model families provide interpretable, prequential predictions of an experimental ternary magnetic response, under a leakage-safe offline protocol?**

This asks whether mathematically distinct predictive *shapes* help describe observations. It **does not claim** to identify which physical mechanism actually causes Fe–Co–Ni magnetism. It is distinct from maximizing Kerr or coercivity with Bayesian optimization; there is no ground-truth “true model family” label in the NIST dataset.

## Candidate models from the existing synthetic prototype

Let `c=(c_Fe,c_Co,c_Ni)` with nonnegative components summing to one, **only after authoritative column order and scale verification**.

1. **Linear composition response:** `[1, Fe, Co]`; Ni is the remainder, avoiding exact multicollinearity on the simplex.
2. **One interaction response:** `[1, Fe, Co, Fe*Co]`.
3. **Localized response:** `[1, Fe, Co, exp(-||c-(1/3,1/3,1/3)||²/(2*0.18²))]`.

These three are **illustrative statistical bases, not independently competing mechanistic hypotheses**, and share nested terms. Fixed bump width 0.18, regularization, noise model and posterior model probabilities are developer choices. Domain approval and out-of-family checks are prerequisites to defensible scientific inference. None of these hypotheses is validated by NIST's paper.

## Data-to-model blockers

- **Element order not verified:** Source data dictionary labels `C` only as composition; no secure per-column Fe/Co/Ni mapping has been established. Do not assign elements from the dataset title alone.
- **Composition units not authoritatively verified:** numeric sums near 1 versus 100 do not certify physical units.
- **Target row alignment not authoritatively verified:** equal lengths and valid array shapes are necessary but not a complete sample-ID/provenance check.
- **Per-measurement uncertainty not verified:** never substitute a synthetic standard deviation and label it calibrated; a sensitivity-only study would need explicit disclaimers.
- **Actual per-experiment costs not verified:** no monetary/time savings claim from arbitrary units.
- **Permissions/physical review unresolved:** review reuse terms, missing-data policy and domain validity with scientific collaborators before fitting.

## Proposed gated pilot (not executed)

1. Secure authoritatively cited mapping/units and review the element-specific interpretation with an Fe–Co–Ni researcher.
2. Freeze sample inclusion rules, primary `Kerr` target, nuisance features, transformations and group-based split boundaries **before any model fitting or policy comparisons**.
3. Specify baseline predictions (constant mean, linear ridge/Bayesian regression, Gaussian process), calibrated uncertainty plan and prequential log density/coverage metrics. Define an explicit failure/abstention status for unknown noise rather than converting uncalibrated model uncertainty to lab-calibrated confidence.
4. Only then consider **retrospective offline next-experiment selection** with an oracle that hides unselected labels and compare against matching-budget random selection, uncertainty sampling, GP-Expected Improvement and relevant cost-aware methods. **Model-discrimination and material optimization results must be reported separately.**
5. Review licensing and scholarly attribution. The data reference requests citations to Wang et al. (2022) and Yoo et al. (2006).
6. Obtain independent protocol review before any scored evaluation. The BHS holdout seed range 10000..10099 is not accessed.

## Current machine-readable contract

`research/NIST_SCIENTIFIC_HYPOTHESIS_SPEC_V1.json` contains six unresolved gates and strict false-only claim flags. It is *deliberately impossible* to mark the dataset, model families, source order, source units, calibrated measurement error or commercial ROI as validated in this version merely by editing the JSON. Future evidence must be separately reviewed and versioned.

Commands:

```bash
python -m unittest discover -s tests -p 'test_nist_scientific_hypothesis_spec_v1.py' -v
python -m scripts.nist_scientific_hypothesis_spec_v1
```

`scored_validation_allowed=false`; `physical_validation=false`; `independent_holdout_used=false`. This contract does not download any dataset or create predictions.
