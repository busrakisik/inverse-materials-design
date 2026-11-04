# Bayesian Hypothesis Search (BHS): Publication Readiness Audit v1

**Date:** 2026-11-04  |  **Scope:** `bhs-scientific-audit` development branch  |  **Verdict:** **Not publication-ready as an empirical superiority claim.**

This is an evidence/claim-boundary review, not an independent code-security, numerical correctness, real-world performance or scientific validation audit. Reviewed source includes `scripts/bhs_research_to_value_v1.py`, `scripts/reliability_gated_design_v1.py`, `scripts/competing_hypotheses_v2.py`, `scripts/predictive_calibration_audit_v1.py`, README, development protocol and relevant tests, with the latest paired CI run **41861188872** observed successful. The audit does not run any independent held-out benchmark.

## Publication-facing research question

**Candidate question:** Under a common resource cap, can explicit competing-hypothesis uncertainty and experiment cost improve *identification* of the generating scientific model, with calibrated predictive uncertainty, relative to strong experiment-selection baselines?

This is a candidate question, **not an answered hypothesis**. At present BHS does not support claims about improved physical material fitness, synthesis yield, scientific discovery rate, economic savings, or superiority over published methods.

## Evidence inventory and claim limits

| Evidence | Verified developer-level fact | Allowed interpretation | Not allowed |
| --- | --- | --- | --- |
| GitHub Actions run 41861188872 | 15/15 specific unit tests passed; comparison execution successful | Code execution and specified contracts ran | Mathematical proof or external replication |
| Paired development study | 24 development conditions x four policies = 96 campaign rows, 72 contrasts with EIG; cap 8 synthetic cost units | Exploratory matched-budget descriptive comparison | 96 independent trials; significance or population effect |
| Competing hypothesis model v2 | Three scalar basis families with one amplitude each, stated normal noise | Controlled synthetic model identification | General scientific hypothesis discovery |
| Reliability-gated design v1 | Synthetic provenance string checked, known noise and cost used in EIG / cost heuristic | Metadata contract check | Physical instrument calibration or certified reliability |
| Prequential / stress diagnostics | Prediction-before-update, six developer-picked stress examples | Illustrations of posterior predictive misfit | Validated out-of-family detector |
| Existing MCTS prototypes | Open-loop and approximate observation-bin branches implemented separately | Experimental planning prototypes | Full formally validated BAMCP / POMCP |
| Zenodo DOI 10.5281/zenodo.21761835 | Archived initial research release v1.0.1 | Citable archive | Publication of the new branch or peer-reviewed validation |

## Priority findings

**P0 — No independent evidence of algorithmic superiority.** All benchmark conditions and simulator choices are researcher-accessible and post-selection. `scored_validation_allowed=false` must remain unchanged. Repeatedly editing development policies and reusing the same cases can overfit the demonstration.

**P0 — Objective mismatch.** `true_model_log_loss` measures model-family identification, *not* best physical property or success of materials synthesis. Compare against scientific model-discrimination baselines on the same objective. Physical discovery objectives require a separate protocol.

**P0 — Synthetic generator contains the answer family.** All generating families are in the learner's set in the paired grid. This substantially favors identification assumptions; stronger out-of-family tests exist only as separate, developer-chosen diagnostics, not paired policy evidence.

**P0 — The cost budget is arbitrary.** Cost units 1/3 and cap 8 are not lab time, actual consumables or currency. A per-cost heuristic and lower loss do not establish savings. Budget matching alone is not equivalent to equal experiment counts or equal schedule constraints.

**P1 — Experimental unit and dependence.** 24 paired cases derive from 3 generator types × 2 cost patterns × 2 noise patterns × 2 deterministic repetitions. Four policies within each case are paired, not independent. The two repeats are not a credible basis for inferential error bars; no significance tests should be reported as confirmatory.

**P1 — Strong baselines absent.** Random and cheapest-first are weak. EIG is relevant, but separate publishable objectives need appropriate expected improvement, knowledge gradient, value-of-information, entropy search, resource-constrained BO, and domain-expert selection methods with matched capabilities and budgets. Baselines should be selected after domain/expert scoping and before independent evaluation.

**P1 — Numerical verification incomplete.** Numerical EIG via midpoint-normal quantiles has approximation error; independent quadrature, extreme-tail cases, posterior evidence checks and tolerance-based comparisons are needed. Local tests alone do not establish a sound numerical implementation.

**P1 — No real-material evaluation.** The current scalar synthetic model, fixed candidates and known Gaussian errors do not demonstrate physical likelihood calibration, candidate feasibility or laboratory relevance. The main README's older `bhs/` demo description also needs an explicit update explaining new `scripts/` developer experiments without implying they are integrated into physical BHS.

**P1 — Leakage and execution security.** The trusted synthetic generator exposes selected values only by code contract; in-process execution is not an adversarial OS security sandbox. Separate process isolation work has not established general sandbox security. Real data benchmarks need sealed label-provider separation and an explicit threat model.

**P1 — Provenance claims.** A value like `instrument_calibrated_synthetic` is only synthetic protocol metadata; it must not be presented as verification of a real instrument. Run manifests should include exact code revision, environment, data permissions, model configuration and artifact hashes.

**P2 — Commercial status.** No paid pilot, verified customer ROI, defensible proprietary advantage or real-cost optimization shown. Commercial claims need consented partner records and measured outcomes.

## Scientific release gate (not met)

1. **Question fixed:** choose model discrimination *or* materials optimization as the primary outcome; write estimand and failure modes. No retrospective swapping.
2. **Mathematics independently checked:** conjugate evidence, posterior predictive distributions and EIG approximation confirmed by an independent implementation and sensitivity tests.
3. **Baseline protocol frozen:** strongest appropriate comparators, budgets, noise/cost semantics, failure handling, and reproducibility requirements set prior to evaluation.
4. **Out-of-family generalization:** demonstrate calibrated predictive uncertainty and misspecification behavior on properly separated data; distinguish descriptive detection from a certified threshold.
5. **External relevance:** permission-cleared offline real experimental/materials dataset, verified measurement errors and feasible action contracts; no labels exposed to selecting policies.
6. **Independent review:** domain advisor checks physics, methods reviewer checks evaluation, and preregistered confirmatory protocol approved before access to any future holdout.
7. **Claims reviewed:** effect estimates, uncertainty, failure cases and negative results reported honestly; code/data licenses and artifact versions linked.

**Do NOT unseal or generate the 10000..10099 independent holdout seeds as part of this audit.** No automated process in this bundle performs evaluations.

## Publication story suitable *now*

Present BHS as an **open-source exploratory framework** with hypothesis selection, sequential Bayesian updating, cost-aware design and explicit robustness audits. Present successful CI and reproducible synthetic demonstrations as *engineering accomplishments*, and observed negative comparisons as transparent exploratory findings. A methodological/software paper **may** become viable after independent checking and clear scope delimitation; superiority, discovery and ROI papers require far stronger evidence.

## Next 3 concrete research deliverables

1. Independent mathematical verification and baseline-specification note (no holdout).
2. Data-use assessment of an existing real closed-loop materials benchmark, with permission, oracle leakage threat model and domain-feasibility check.
3. Frozen offline pilot protocol with explicit scientific endpoint and partner-approved cost units, to be evaluated only after external review.

## Independent sources

- MADE: Benchmark Environments for Closed-Loop Materials Discovery (ICML/PMLR, 2026): https://proceedings.mlr.press/v306/malik26a.html
- Benchmarking Active Learning Strategies for Materials Optimization and Discovery (NIST / npj Computational Materials, 2022): https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery

**Audit flags:** `independent_holdout_used=false`; `scored_validation_allowed=false`; `superiority_claim_validated=false`; `materials_discovery_validated=false`; `commercial_roi_validated=false`.
