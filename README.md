# Bayesian Hypothesis Search (BHS)

**An independent research prototype for Bayesian hypothesis evaluation and sequential experiment selection in computational materials research.**

> **Version context:** The historical August 2026 release is distinct from the later NIST development experiments documented here. Cite a specific Git commit and its associated evidence when discussing the current BHS research.

BHS investigates how explicit competing model assumptions, evidence updates, uncertainty diagnostics and decision rules can support more transparent and reproducible scientific computation. The repository contains developmental software, synthetic verification tests, retrospective evaluations and provenance records. Software tests do not by themselves establish scientific efficacy.

## Scientific questions

1. **Hypothesis discrimination:** Can competing falsifiable hypotheses be distinguished by selecting informative observations when likelihoods, experimental feasibility and costs are sufficiently specified?
2. **Property optimization:** Can predictive-model selection or averaging improve sample efficiency against strong Gaussian-process baselines under matched retrospective conditions?

These are distinct tasks. The historical NIST Kerr experiments investigate property optimization; statistical response-model families are **not** established physical mechanisms.

## Research implementation

- Mathematical Bayesian updates on explicitly supplied priors and likelihoods, with input validation and provenance output.
- Experimental sequential search, decision policies, benchmarks and reliability checks (see the [research branch](https://github.com/busrakisik/inverse-materials-design/tree/bhs-scientific-audit)).
- Optional CHGNet integration for computational evaluation, not a claimed physical laboratory verification.
- Source-integrity checks, synthetic unit tests, and real-data retrospective diagnostics.

The current focused demonstration does not perform physical materials discovery, and its 20-system benchmark scaffold is a planned protocol rather than a completed experimental campaign. The historical Zenodo deposit refers to a different earlier software scope; it does not independently authenticate the later BHS experiments.

## NIST development evidence — v1 to v4

The NIST REMI historical Kerr data provide **921 eligible retrospective observations**. The composition-coordinate columns are treated as anonymous because their precise element mapping has not been independently verified. All reported comparisons below are **exploratory development**, not a held-out independent evaluation.

| Study | Verified developmental outcome |
| --- | --- |
| **v1** | Mean normalized final simple regret over three 15-acquisition development campaigns: **GP–EI 0.0250** vs **BHS–BMA–EI 0.1392** (smaller is better). |
| **v2** | Post-hoc hyperparameter/model ablations showed substantial sensitivity and no independently validated superiority. |
| **v3** | Across 900 prequential development forecasts, nominal 90% intervals undercovered substantially. On random trajectories: GP **43.3%**, BHS–BMA **28.3%** coverage. |
| **v4** | 540 miscalibration diagnostics, variance/distance/phase analyses and **36/36** passing software tests. |

**Negative result retained:** In the original protocol, BHS did not outperform the GP expected-improvement reference. Calibration failures for both models, more severe for BHS in these diagnostic comparisons, remain unresolved. Post-hoc interval widening is not independent calibration.

Primary preserved evidence:
- [v1 aggregate report](https://github.com/busrakisik/inverse-materials-design/blob/bhs-scientific-audit/research/nist_anonymous_offline_pilot_v1.json)
- [v2 ablation aggregate report](https://github.com/busrakisik/inverse-materials-design/blob/bhs-scientific-audit/research/nist_diagnostics_ablation_v2.json)
- [v3 prediction-adequacy aggregate report](https://github.com/busrakisik/inverse-materials-design/blob/bhs-scientific-audit/research/nist_model_adequacy_v3.json)
- [v4 miscalibration aggregate report](https://github.com/busrakisik/inverse-materials-design/blob/bhs-scientific-audit/research/nist_miscalibration_rootcause_v4.json)
- [v4 GitHub Actions run](https://github.com/busrakisik/inverse-materials-design/actions/runs/42046318788)

## New external real-data development (v5 — November 2026)

A separate [UCI concrete 28-day retrospective development study](research/UCI_CONCRETE_V5_FIRST_REAL_DEVELOPMENT_RESULT.md) was implemented after the NIST work using a publicly licensed dataset (1,030 original rows; 416 distinct 28-day feature profiles). Five software tests and nine paired development campaigns completed in [GitHub Actions](https://github.com/busrakisik/inverse-materials-design/actions/runs/42214172524).

In the exploratory comparison, **fixed GP–EI (0.095889) slightly outperformed the kernel portfolio (0.097209)** on mean normalized final regret; random selection was 0.242408 (lower is better). The statistical model portfolio is not a physical hypothesis-discrimination result. Three development seeds do not justify superiority or generalization claims; independent holdout and physical validation remain **not performed**.

## Reproduce the software checks

The following commands exercise the **development-only synthetic and contract tests**; they do **not** download real NIST observations, run an independent holdout or demonstrate physical validation.

```bash
git clone https://github.com/busrakisik/inverse-materials-design.git
cd inverse-materials-design
python -m venv .venv
source .venv/bin/activate
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2
python -m unittest discover -s tests -p 'test_nist_model_adequacy_v3.py' -v
python -m unittest discover -s tests -p 'test_nist_miscalibration_rootcause_v4.py' -v
```

The above two test modules have previously passed **31** and **36** checks respectively on Python 3.11 in the research verification environment. Additional components such as Streamlit, pymatgen and optional CHGNet require their own dependencies and environment checks. Consult [the research overview](research/RESEARCH_OVERVIEW.md), [the evidence register](research/BHS_EVIDENCE_REGISTER.json) and [the test suite](tests/) before interpreting model outputs.

## Scientific boundaries and next steps

No independent scored validation or physical validation has been performed. The independent evaluation seeds `10000–10099` remain reserved and unused. No verified novel material, true physical mechanism, instrument-calibrated uncertainty, commercial benefit or method superiority is claimed.

The next stage targets distinct, permission-cleared external scientific evidence and a predeclared comparison against strong baselines, with appropriate domain-expert review. Planned external studies must not be described as completed.

## Software and citation

- [Research source and test suites](https://github.com/busrakisik/inverse-materials-design/tree/bhs-scientific-audit)
- [Historical predecessor software archive, August 2026](https://doi.org/10.5281/zenodo.21761835) — an archived earlier version, **not** a publication or archival snapshot of the NIST v1–v4 results
- [CITATION.cff](CITATION.cff) · [MIT license](LICENSE)
- Maintainer: [@busrakisik](https://github.com/busrakisik)

Scientific source data retain their original provenance and reuse constraints. Interpret each code path and result according to its recorded evidence level and limitations.
