# BHS Benchmark v1 — preregistered design draft

**Status:** DESIGN_ONLY / NOT_RUN. **Date:** 2026-11-01. **Branch:** `bhs-scientific-audit`.

## Scientific question
At equal, strictly metered evaluation budgets and with the same available information, does a **hypothesis-conditioned sequential selection policy** identify higher-value candidates earlier than uniformly random selection and a non-hypothesis ranking baseline?

This is a falsifiable question, **not** a claim of advantage. The existing BHS Bayesian engine updates explicitly supplied prior/likelihood values; it does not yet implement calibrated materials likelihoods, a physical hypothesis search policy, MCTS rollouts, or candidate generation. The first phase must therefore be marked **protocol and infrastructure validation**, not a competitive BHS benchmark.

## Decision gates — do not skip

**Gate 0 — Research specification (this document).** Specify outcome, admissible information, selection policies, budget, random seeds, and expected failure modes *before* seeing benchmark outcomes.

**Gate 1 — Candidate pool and ground truth.** Acquire a legally usable, provenance-rich dataset with structure IDs, chemical compositions, reference property, source/version and license. Do not choose a test set because it produces a favorable BHS result. Validate units and label definitions. No real candidate pool is included with this protocol.

**Gate 2 — Information firewall.** Divide by material *families/compositions*, not merely row-random splits, where appropriate. Lock test set and labels. During each simulated sequential trial, the policy sees only prior/training information and revealed outcomes for previously queried test candidates; unrevealed ground truth is inaccessible through the decision API. Fit calibration, features, priors and hyperparameters solely on training/validation data. Record every candidate query.

**Gate 3 — Oracle and cost.** Agree on a single evaluation oracle: for an initial *offline* benchmark, fixed reference labels from a dataset; all policies get the same per-query cost. This evaluates selection efficiency over a known pool, **not** the cost/accuracy of running DFT or CHGNet. A subsequent *online* benchmark can meter actual CHGNet/DFT wall time and resource use separately.

**Gate 4 — Implement shared interface.** Every policy receives the same eligible candidate IDs and admissible observations and must return one previously unqueried candidate ID. Policies to compare: (a) seeded uniform random without replacement; (b) pre-registered static non-hypothesis score ranking using training/validation-fitted features; (c) BHS hypothesis-conditioned sequential policy *only after it exists and is calibrated*. Do not compare a developed BHS to a deliberately weak random baseline only.

**Gate 5 — Execute blind held-out trials.** Frozen random seeds, matched candidate pools, budgets, and access to information; full query-level logs, including failures. Preserve unsuccessful or null results; do not impute success.

## Primary endpoint (pre-specified, before test inspection)

Mean **best observed validated target score after K distinct queries**, over test problems/seeds; report the full curve as secondary. Choose the target property, its sign (maximize/minimize), normalization, K, and treatment of invalid/missing labels when the actual dataset is selected, *before* unblinding the held-out labels. A score is never the uncalibrated BHS SOAP or clash heuristic interpreted as physical truth.

Secondary endpoints: area under the best-so-far curve; success@K for a frozen scientifically meaningful threshold; number of queries to first success (censored if no success); confidence intervals over appropriately grouped test problems; variability across seeds; observed computation time/cost. Report the negative and null results.

## Statistical plan

Pair trials on the **same held-out problem and random seed**. Summarize per-problem differences first; avoid treating repeated seeds on one structure as independent material observations. Use confidence intervals / bootstrap clustered by test problem as appropriate, report effect sizes and uncertainty, and account for multiple baselines / metrics. No p-value or speedup is currently available.

## Ablations (only after fully implemented)

Freeze all other factors; compare the full BHS policy with hypothesis conditioning removed, evidence updating removed, or a nonadaptive policy. Do not label simulated or supplied likelihoods as learned calibrated physics evidence.

## Exit criteria

A benchmark may be called **EMPIRICAL** only when all of these exist: dataset source/version and split manifests; verified label definitions; executable policies; explicit oracle and budget; end-to-end reproducible runner; query-level result logs; at least two nontrivial baselines; preselected primary metric; repeated test problems; leakage checks; independently regenerable summary. A completed CHGNet single-structure relaxation cannot satisfy these criteria by itself.

## Immediate engineering task

Implement a small *offline* runner and its tests with a **synthetic known-answer oracle** to verify non-leakage, budget counting, without-replacement behavior, and identical policy interfaces. Tag every outcome `SYNTHETIC_SOFTWARE_TEST_NOT_MATERIALS_BENCHMARK`. Only then ingest a real dataset. Do not merge the existing 20-system `NOT_RUN` suite into benchmark results.

## PhD-facing research story

The contribution hypothesis is in **sequential decision making and uncertainty-aware scientific experimental design**, not in claiming discovery from a standalone MLFF call. Communicate both successful reproducibility and missing empirical head-to-head evidence honestly.
