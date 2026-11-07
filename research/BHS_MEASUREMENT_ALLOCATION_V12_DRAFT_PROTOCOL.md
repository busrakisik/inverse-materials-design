# BHS v12 — draft measurement-allocation protocol (NOT yet preregistered)

**Prepared:** 7 November 2026. **Status:** proposed implementation and synthetic contract checks; the historical v12 replay has **not been executed**. This document must be reviewed and committed **before** the first outcome-scored v12 replay. Earlier v10 and v11 analyses have already inspected this historical source, so it is permanently **development**, never independent confirmation.

## Falsifiable question

Under a fixed budget of *48 individual historical physical-response measurements*, can an explicit evidence-sufficiency repeat rule allocate measurements between existing partly observed designs and unseen designs more effectively than strong bundled GP–ARD, RF and random baselines? This is an evaluation of a **heuristic evidence-allocation rule**, not physical hypothesis identification, measured utility or validated expected information gain. The existence of a repeat-vs-explore decision does not make it automatically valuable.

**Primary failure criterion:** The evidence gate's retrospective *completed-design* simple regret does not improve over the strong GP–ARD bundled policy on the five fixed developmental campaigns; or it explores many partly observed designs without completing useful measurements. Negative and mixed outcomes must be retained without retuning this protocol and describing another split as independent evidence.

## Original source and provenance

- Gongora et al. (2020), *Science Advances*, DOI 10.1126/sciadv.aaz1708 (original 3D-printed mechanical toughness measurements).
- Liang et al. (2021), *npj Computational Materials*, DOI 10.1038/s41524-021-00656-9 (benchmark archive).
- `PV-Lab/Benchmarking`, source commit `7585c517ad88e676c42c6bf24a8ad278e01ddb21`, file `datasets/Crossed barrel_dataset.csv`.
- Git blob SHA-1 `b007fe5d8762233bbd23c8cf83858b169f05492a`; raw source SHA-256 `2c01f875f3c210e986ca6142bf20f417884c2ad7d6f008c2fc574b44a3d5f606`.
- **600 distinct geometries, exactly 3 recorded outcomes per geometry (1,800 historical physical observations).** No new experiments are conducted; no source measurement rows are distributed by BHS.
- The original file contains **no trusted within-geometry chronology or batch/process labels**. For a repeat-based replay, each geometry's three source results are assigned a deterministic artificial observation order using the frozen seed and geometry index. This is **not** historical event order. Its effect must be examined before claiming any transportability.

## Fixed measurement budget and acquisition view

The five seeds `7,13,23,31,43` and source have already been used to guide development. Seeds `10000` to `10099` are **reserved and prohibited**. Every policy starts from the same six geometries, each with all three historical outcomes (18 measured responses), then receives **30 additional atomic measurement actions**, for a total of **48 responses**. One action reveals only the next previously unobserved response of one selected geometry, up to three; a recommendation is eligible only after all three results for that geometry have been revealed.

All policies may know the entire candidate geometry descriptor matrix, standardized using **unlabelled descriptors only**. Each selector gets only a mapping from acquired geometry ID to its 1–3 already revealed values. It never receives hidden responses, the pool optimum, hidden replicate deviations, or experiment-source order. The evaluator alone holds the historical source and computes regret after all actions. An incomplete geometry is not eligible for the primary final recommendation; completed designs remain eligible. This **completion requirement is a predeclared evaluation convention, not a laboratory safety standard**.

## Frozen method definitions (development, not established best practices)

1. `random_bundled`: choose an unseen geometry uniformly, then acquire its three measurements consecutively. Same 48-measurement budget and six initial triplicates.
2. `gp_ard_bundled`: using only completed geometries, select unseen geometry by Matérn-5/2 GP–ARD EI (lengthscales optimized from completed data, variance diagonal estimated from *acquired* triplicates), then acquire three repeats consecutively. Replicate-noise plug-in is **uncalibrated**.
3. `rf_ucb_bundled`: using only completed geometries, choose mean plus standard deviation across 160 RF trees, then acquire all three repeats. Spread is an **uncalibrated heuristic**, not a confidence bound.
4. `evidence_gate_development`: starts with the same fully measured geometries; in each subsequent action, a partially measured candidate receives another measurement if `partial sample mean + pooled sample SD of *completed* triplicates >= best completed mean`. Among eligible candidates, select the highest partial mean (ties by ID). If three partially measured geometries are already pending, force an additional measurement of the highest-partial-mean pending geometry even when the threshold is not met; this **three-pending-design cap** prevents unbounded one-shot screening. With only one action remaining, prioritize completing a two-observation geometry if possible. Otherwise select an unseen geometry by the same GP–ARD EI used in (2). GP fitting **does not use partially observed groups**; this deliberately limited rule is fully specified and may be inefficient. Pooled SD is a descriptive developmental scale, NOT calibrated laboratory noise. The pending cap is a budget-feasibility heuristic, NOT an optimized acquisition parameter. This gate is **not formal value of information or physically justified abstention**.

Features and GP/RF hyperparameters follow the cited v11 baseline where compatible: GP–ARD Matérn-5/2, bounds `[0.1,10]` for four lengthscales, one optimization initialization, variance plug-in `clip(s² / (3 * response_scale²),1e-3,1)`; RF 160 trees, min leaf 2, bootstrap. No tuning after observing v12 scores. The bundles intentionally use the same 3-measurement batches as v11 but scores may not match byte-for-byte if the original within-group order differs; compare results explicitly instead of assuming parity.

## Metrics and failure analysis

**Primary:** empirical *completed-design* final simple regret in joules against the highest **recorded** full-triplicate mean across the original 600-design pool. This is not latent optimum, independent physical truth, measured decision safety, or an expected economic payoff.

**Secondary:** completed/partially measured geometry counts, total response budget (must be exactly 48), and range of three recorded outcomes for the selected completed design (a **descriptive repeatability measure only**). Report all 5 per-seed outcomes for each method, mean results, failures, and sensitivity to replay ordering. Do not compute statistical significance from repeatedly selected development seeds. Do not conflate retrospective allocations with actual experimental time, price or safety impact.

**Critical confounding:** bundled references force measurement completion, while the evidence gate may spend responses on incomplete candidates; that is a **policy-design comparison**, not proof that replication per se causes a performance change. A fair mechanism study would also need a GP-based adaptive-repeat baseline, noise-model ablation, and domain-specific costs. A 3-repeat maximum and unknown source chronology/batch structure cannot support a prospective policy claim.

## Execution order and hard gates

1. Review protocol and code against public v10–v11 evidence and independent experimental-design literature. Commit the draft and contracts **before** score-producing v12 execution; record Git commit identifier and library versions.
2. Run only synthetic tests on push. Workflow dispatch defaults to `run_development=false`. Explicitly approve the historical replay after freezing methods/metrics.
3. On replay, validate immutable source bytes; emit **aggregates and per-policy/per-seed metric rows only**, no raw measurement values, geometry IDs or source records. Compare outcomes against the frozen protocol, then preserve and publish unfavorable results.
4. **Independent gate remains closed** pending a real domain collaborator, controlled batches/instruments, prospective new physical measurements, strong matched-risk/coverage baselines, and expert-defined action and abstention costs.

`development_only=true`  
`scored_validation_allowed=false`  
`independent_holdout_used=false`  
`physical_validation_by_bhs=false`  
`causal_identification=false`  
`calibrated_uncertainty_proven=false`  
`claim_of_superiority=false`  
`real_savings_measured=false`  
`reserved_nist_seeds_used=false`

## Pre-replay contract hardening (7 November 2026)

An additional source-independent check closes an evaluator replay loophole: a previously revealed measurement cannot be requested again, ordinals cannot be skipped, and the retrospective evaluator rejects forged or incomplete acquisition transcripts. This does **not** alter the four policy functions, frozen actions, selection thresholds, initial seeds, candidate descriptors, measurement counts, objectives or evaluation convention. The checks were added before the first outcome-scored v12 historical replay. The protected development-only and independent-evidence restrictions remain unchanged.

A synthetic two-seed baseline comparison checks that the three bundled policies reproduce the v11 selection-regret convention without touching any historical responses. Exact historical baseline parity remains a mandatory gate in the separately authorized historical replay.
