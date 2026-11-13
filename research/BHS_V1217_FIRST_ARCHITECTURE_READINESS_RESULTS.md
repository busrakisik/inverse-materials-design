# BHS V12.17 — First implementation-scope audit and honest fair-comparison decision

**13 November 2026. Source-code and synthetic Bayes arithmetic audit only; NO new scientific outcomes, prospective holdout, model performance run, physical experiment or resource-cost measurement.**

## Motivation

The research owner's acceptance condition is stricter than a passing software suite: each actual model input needs separately documented origin, availability **before** the expensive action, and access by **all policies at their decision time**. Furthermore, evaluating a synthetic linear posterior or a statistical kernel portfolio does not establish the performance of a complete competing-scientific-hypothesis and adaptive-evidence-search implementation.

The prior V12.16 first original input-to-`structure_unrel` comparison remained a source-level **NEGATIVE** (0.4521222246251549 Å max atom match displacement; prior 0.001 Å tolerance), and the author archive includes a static `NSW=0` charge-analysis stage. No DFT candidate geometry was promoted to permitted selection-time input.

## Preregistered implementation scope and first workflow chronology

- Protocol frozen **before** producing the first machine-checked capability report: `research/BHS_V1217_IMPLEMENTATION_SCOPE_PROTOCOL.md`, Git blob `d6bf0deb49cb447aea09397c5e69ac70fe2275ef`. The protocol explicitly acknowledges that the analyst had already read the relevant code before freezing this automated audit. It is not blind preregistration.
- Inherited **11** audited source modules are pinned to their historical default Git blobs (listed in the protocol). These include the legacy hypothesis registry, posterior updater, heuristic structural scores, open-loop PUCT prototype, budget interface, statistical v11 comparator and actual worker. The audit does **not** claim these are all possible sources or branches.
- First GitHub CI [43424639135](https://github.com/busrakisik/inverse-materials-design/actions/runs/43424639135) **FAILED** because one new unit test demanded a byte-exact `0.75` posterior while the correct floating-point computation was `0.7499999999999999`. The code/protocol remained unchanged.
- An intermediate test-only update CI [43424748049](https://github.com/busrakisik/inverse-materials-design/actions/runs/43424748049) also **FAILED** its frozen-file-hash step because the workflow pin had not yet been updated. This remains part of the original chronology.
- The next CI [43424769777](https://github.com/busrakisik/inverse-materials-design/actions/runs/43424769777) passed the corrected **18/18** new implementation tests, then **FAILED** because historical pytest-based tests were launched through unittest without their required pytest dependency. The fix added only the appropriate pinned test runner, retaining the same source, protocol, mathematical tolerances and negative result.
- **First completed source audit** [43424897424](https://github.com/busrakisik/inverse-materials-design/actions/runs/43424897424): **SUCCESS with 176 software checks**, consisting of 18 new unittest cases, 120 inherited pytest cases, and three further unittest groups of 13, 12 and 13. Corrected source branch `bhs-v1217-architecture-evaluation-readiness` commit `200c0a9f880ff054f1bc5e2a4425f1c190fd870f`. Initial exact JSON artifact ID `14036645950`; file `bhs_v1217_first_implementation_readiness.json` **7,424 bytes**, SHA-256 **`c6a04b61f88daa84e728eac358c26fede676b840cee4dbe3bcf1849eab458dcb`**. The artifact contains only checked implementation states, explicitly synthetic posterior arithmetic and unchanged previously reported V11 summary values; it has no fresh source labels, candidate selections, real hypothesis victories or improved performance numbers.

## Findings by implemented function, not branding

| Source implementation | Verified behavior within scope | Research limitation |
| --- | --- | --- |
| `HypothesisAndExplainabilityEngine.evaluate_competing_hypotheses` | Returns three **illustrative** material-family templates and `chosen_hypothesis=None` | No candidate-level falsifiable scientific predictions, learned evidence, completed selection or physical result |
| `BayesianHypothesisSearchEngine.accumulate_evidence` | Correct mathematical posterior: fabricated priors 0.5/0.5 and supplied likelihoods 0.75/0.25 produce posterior approximately 0.75/0.25 | Likelihoods are externally supplied, not independently scientifically calibrated; this does not discover a material |
| `BayesianHypothesisSearchEngine.compute_uct` | Raises `NotImplementedError` rather than fabricating tree search scores | Cannot claim the historical Bayes module implements MCTS |
| `LikelihoodEngine` | Computes declared overlap and novelty **heuristic** scores | These are not authenticated physical likelihood functions `P(evidence|hypothesis)` |
| `OpenLoopPUCTPolicyV1` | Actually simulates and updates an open-loop candidate-ID tree using a scalar synthetic posterior | Does not branch on possible **observed outcomes**, does not use scientific rival hypotheses or real material evidence |
| `AdaptiveBudgetPlanner.allocate_and_evaluate` | Returns `NOT_ALLOCATED` and `NOT_RUN` | No verified compute/experiment allocation or costs |
| `policy_worker_v1` | Dispatches scalar `BayesianOnlyPolicyV1`; synthetic first-unqueried worker also exists | Neither worker is the full hypothesis-evidence-planning architecture |
| `bhs_replicate_pool_v11.select_next` | Dispatches inherited statistical `uci_concrete_v5.choose_next` with matched retrospective labels | Existing V11 data estimate performance of old kernel-portfolio component only, not complete BHS |
| `MultiModelConsensusEngine` | Arithmetic on caller-supplied values with explicit uncertainty/provenance warnings | Does not execute underlying computational models or certify reference alignment |

No trusted code path was identified **in these 11 pinned inspected entrypoints** that combines domain-specific falsifiable hypotheses, physically justified likelihoods from previously acquired measurements, posterior reasoning, *observation-contingent* planning and an end-to-end decision policy. This is a precisely scoped implementation-readiness assessment, not a statement that no such path could exist in any other repository.

## The actual pre-existing empirical comparator must not be lost

The source-pinned V11 study used **600 physical 3D-printed crossed-barrel designs × three measured toughness replicates**, equal budget of **16 distinct designs / 48 historical responses** and five development seeds. Mean final **retrospective simple regret J** (lower is better):

| Method | Mean regret (J) |
| --- | ---: |
| GP–ARD EI | **7.363** |
| RF–UCB | **8.983** |
| Existing BHS v5 statistical kernel portfolio EI | 9.368 |
| Random | 15.951 |

Old BHS component exceeds GP–ARD regret by **2.005 J** and RF–UCB by **0.385 J**; the result is unfavorable to BHS. It is development-only, not statistically conclusive or representative of full BHS. Preserve unchanged original source `research/BHS_REPLICATE_POOL_V11_RESULTS.md` Git blob `400ac9271dbf24f229a8b50823af773d1c0b6ea5`, source run `42347524338`, no new V11 rerun as independent evaluation.

Unlike the current DFT input-structure uncertainties, the crossed-barrel design variables `n`, `theta`, `r`, `t` denote geometry parameters set before manufacturing/testing. The actual V11 evaluation code exposes those unlabelled descriptors and previously acquired triplicates to all four methods. This supports an honest **V11 component-level** time-of-information contract, but it does not create an untouched independent sample or a full-BHS validation.

## Decision and next scientific work

**`FULL_BHS_NOT_EVALUABLE_YET_EXISTING_COMPONENT_RESULT_NEGATIVE`.** `full_bhs_fair_comparison_ready=false`, `scored_validation_allowed=false`, `per_feature_origin_timing_access_certified=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `laboratory_action_allowed=false`.

The next productive work is **implementation, not more decorative benchmark suites**: define a concrete physical question with at least two scientifically distinct and potentially falsifiable models; specify how to generate their distinct quantitative predictions from source-certified *design-time* inputs; justify evidence likelihoods with source author/experiment noise, track chronology and decisions and implement posterior-coupled candidate selection. If adaptive lookahead is required, branch on possible future *observation outcomes* and compare to a correctly defined noncontingent simpler strategy at matched actual budget. Do not label an arbitrary kernel mixture as scientific hypotheses. Obtain genuinely independent outcomes or an externally approved prospective design for meaningful evaluation. Preserve negative results, all old failed workflow attempts, default and releases, earlier draft/unmerged pull requests and protected NIST seeds `10000..10099`.
