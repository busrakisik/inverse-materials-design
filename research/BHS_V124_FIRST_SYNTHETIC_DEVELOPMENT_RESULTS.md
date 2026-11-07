# BHS v12.4 — First frozen completion-cost and abstention development results

**7 November 2026. Completed first source-locked manufactured study; no real physical experiments and no independent materials validation.**

## Outcome and scientific conclusion

The new completion-feasibility filter removed stranded partial observations from the original evidence gate under the fixed 48-response budget. **It did not improve the predeclared mean abstention-adjusted loss.** The unrestricted native gate, completion-constrained gate and bundled GP–ARD each returned the *same primary loss in every one of the 16 paired synthetic cases*. Their acquisition trajectories and raw latent recommendation regrets were not generally identical. The fixed decision threshold frequently withheld recommendations, compressing differences between methods.

A completion constraint is therefore useful as **an accounting invariant**, but this first constructed comparison does **not** show that it improves scientific decisions. The evidence gate did not establish superiority over GP–ARD, nor is its repeat-selection mechanism separately causally identified.

## Exact locked experiment and provenance

- [Frozen pre-outcome protocol](BHS_V124_MATCHED_COMPLETION_PROTOCOL.md): first committed in `87740d030bde11dd132cd44e3f98bad9f8a41406`.
- Reviewed source and tests: commit `220d45cbe5271092116892f9e792d9017c5c7cba`.
- First pinned-library scored run: [GitHub Actions 42371341316](https://github.com/busrakisik/inverse-materials-design/actions/runs/42371341316), **success** with all strict budget, source and paired-study checks passing. The action runner used Python 3.11, NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.2 and pandas 2.2.3.
- First successful full software contract run: [42371140080](https://github.com/busrakisik/inverse-materials-design/actions/runs/42371140080), **69 of 69**. The earlier CI failure [42370963539](https://github.com/busrakisik/inverse-materials-design/actions/runs/42370963539) detected invalid pooled variance handling and remains visible; it was fixed before the 96-campaign run without tuning acquisition scores or outcome thresholds.
- Original first-run Actions output artifact: `bhs-v124-first-frozen-synthetic-development-only`, ID `13574405099`. Its ZIP SHA-256: `2d995cbef1c2fae2e504881a2f55367680e6bb5ea42702727dcd46d8b82a7c01`. The JSON **uncompressed byte-exact SHA-256** is `dda6dbd238305c193108caeac53337c920c9ab89850734ad66e7f66f71d53dd4` (148,723 bytes).
- Permanent lossless XZ copy of **those identical JSON bytes**: [`research/bhs_v124_first_frozen_study.json.xz`](bhs_v124_first_frozen_study.json.xz), XZ SHA-256 `d865487bc49871be34eec6d3ea0dcdf1a584bb039f65de84c3d255ccc88541fe`. Re-extract and hash the JSON before using. No raw source measurements or selected geometry IDs are included in the aggregate.
- All input construction is deterministic from the frozen descriptors/noise seeds, with four source digests inside the JSON. No historical physical source was accessed and no new physical responses were measured.

## Fixed comparison

Two manufactured latent landscapes (`ridge`, `oscillatory`), two measurement-noise regimes (`constant`, `varying`), decision seeds `19,29`, response order variants `0,1`, six policies: **96 campaign outcomes**, or 16 for each policy. Each consumes exactly **48 individual responses** including the same six initial completed designs. All methods use a strict private source ledger, can observe only previously released measurements, and select a fully measured design for the final raw recommendation.

**Predeclared primary loss:** If the observed top-two completed means differ by more than `1.0 ×` the estimated pooled standard error, report evaluator-only latent simple regret; otherwise abstain and incur fixed loss `0.50`. All values below are in **manufactured latent-quality units**, not joules.

| Method | Primary mean loss (lower better) | Primary coverage | Raw mean latent regret | Mean completed designs | Mean stranded responses |
| --- | ---: | ---: | ---: | ---: | ---: |
| Bundled GP–ARD | 0.3181 | 37.50% | 0.1501 | 16.00 | 0.00 |
| Native evidence gate (unmatched diagnostic) | 0.3181 | 37.50% | 0.1045 | 15.00 | 3.00 |
| Evidence gate + shared completion filter | 0.3181 | 37.50% | 0.1284 | 16.00 | 0.00 |
| Adaptive GP–EI | 0.3209 | 37.50% | 0.0654 | 16.00 | 0.00 |
| Adaptive GP–IVR | 0.3760 | 31.25% | 0.2375 | 16.00 | 0.00 |
| Bundled random | 0.4403 | 12.50% | 0.2669 | 16.00 | 0.00 |

The completion-constrained gate required **2.6875 feasibility interventions per campaign on average**, versus zero for its unmodified diagnostic arm. It removed approximately 2.69 incomplete designs and 3 stranded responses per campaign, but the raw latent regret *increased* from 0.1045 to 0.1284. This is not a favorable independent finding for the proposed acquisition mechanism.

### Pairing and sensitivity of the primary metric

Relative to bundled GP–ARD across the same 16 source/noise/seed/order cases:
- Native evidence gate: **0 better, 16 equal, 0 worse**.
- Completion-constrained gate: **0 better, 16 equal, 0 worse**.
- GP–EI: **2 better, 12 equal, 2 worse**.
- GP–IVR: **2 better, 11 equal, 3 worse**.
- Random: **0 better, 12 equal, 4 worse**.

This is a descriptive small constructed grid, **not** a significance test. The four contexts and two orders per seed reuse the same candidate descriptors and noise table. They are correlated and not independent empirical replication.

### Coverage versus recommendation quality must remain separate

At the predeclared descriptive threshold `z=0` (all methods recommend in this constructed study), GP–EI had the lowest mean raw latent regret at approximately **0.0654**. At the frozen primary threshold `z=1.0`, GP–EI had slightly **higher** mean abstention-adjusted loss than bundled GP–ARD (0.3209 vs 0.3181) despite its better raw recommendation score. At `z=1.645`, most methods abstained on **every** campaign, while GP–IVR accepted 3 of 16. A method that abstains more is not automatically safer; the threshold is a pooled-noise heuristic, not a calibrated error probability.

The primary z and penalty were specified **before** seeing the 96 results. Alternative thresholds and penalties remain descriptive, not post-hoc replacements for the frozen primary endpoint.

## Scientific limitations and next research gate

1. Complete-design accounting is enforced, but methods differ in surrogate construction, action scores, stopping preferences and treatment of partial evidence. Matched budgets alone do not establish a causal effect of replication.
2. The pooled standard-error abstention rule is uncalibrated. Repeated use of the same source designs and synthetic noises cannot validate real-world confidence.
3. Two manufactured functions and two paired decision seeds are far too small for reliable generalization. The first V12 historical replay's failed parity check and V11's unfavorable portfolio results remain unchanged and publicly traceable.
4. **Do not retune the existing synthetic grid and call it independent confirmation.** A separate decision-calibration study needs untouched source problems, explicit sample/batch provenance, matched coverage and loss, and separate calibration/evaluation partitions.
5. Before use by independent researchers or laboratory automation, obtain genuinely prospective experimental observations, human domain review, justified physical acquisition and abstention costs, equipment chronology and uncertainty checks.

## Hard evidence flags

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `causal_identification=false`; `calibrated_uncertainty_proven=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `reserved_nist_seeds_used=false`. Protected NIST seeds `10000..10099` remain unused.

**Conclusion:** Better completion accounting, no demonstrated improvement in the primary scientific decision-loss objective. Preserve the negative and mixed evidence.

