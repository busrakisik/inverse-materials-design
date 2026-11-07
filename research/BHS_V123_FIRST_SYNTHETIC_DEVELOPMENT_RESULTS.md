# BHS v12.3 — First frozen manufactured development study

**7 November 2026 — completed protocol-first, source-independent developmental study.**

**Primary conclusion:** The frozen evidence gate was weaker than the strongest GP reference on both fixed manufactured noise regimes. All selected methods passed source-isolation and budget contracts, but the evidence gate consistently ended with three partially measured geometries. These observations are descriptive software research findings, **not** external validation, new physical experiments, causal proof, or a general ranking of scientific algorithms.

## Exact provenance

- [Protocol, committed before any v12.3 outcome scoring](BHS_V123_CONTROLLED_SYNTHETIC_PROTOCOL.md), commit `c01b4ec9fe5e8bdc9a6096d6b68aac7915717296`.
- Fixed implementation commit `52ba638843bbedf16f1cdbc54e9ecc2cdc90bd6e`; Python source Git blob `c467dd6b1c7ae22b3bb2ae37da61d4f857a8cbae`.
- [Contract verification](https://github.com/busrakisik/inverse-materials-design/actions/runs/42367700933): successful, 52 tests covering v12 to v12.3.
- [First source-locked manufacturing study](https://github.com/busrakisik/inverse-materials-design/actions/runs/42367879774): successful, pinned `numpy==1.26.4`, `scipy==1.13.1`, `scikit-learn==1.5.2`, `pandas==2.2.3`.
- Exact aggregate-only report SHA-256 `499f7660499c3c7708e387d651da848fc9593ab0139c45ecc8c093bdd5af4483`; first GitHub Actions ZIP SHA-256 `5bc4a96a5c0e24d88d4902f52bdaa6522f990918482addcbe8e95eb8666237d1`.
- Permanent byte-exact development archive: [first frozen report ZIP](bhs_v123_first_frozen_synthetic_2026-11-07.zip). Contains no historical physical measurements, private experiment traces, or selected design IDs.

## Source and matching rules

The simulator contains exactly 48 manufactured 4D designs, three preassigned responses per design, and a known but private latent-response function. Decision seeds are 7 and 13; order variants are 0 and 1; regimes are constant and geometry-dependent noise. Each of five methods received the same six initial completed geometries, descriptors, source table, and **48 individual-response measurement budget**. The deterministic permutations changed the order in which a design's three responses were disclosed, not their multiset. Every policy saw only acquired values, never the latent function, hidden measurement values, or the true optimum.

- Fixed source digest, constant noise: `23f13a72af2f86369405c50b082eebe5f594d9000a5b77f8792e32c33e59e0dd`.
- Fixed source digest, varying noise: `fd425925720d0a5ea7b823d286a30e36e9f99904b0cfc47b93bc6344c884f8f2`.

The primary metric is **latent simple regret** of the selected fully measured design against the best latent design among these 48 candidate locations, in manufactured response units (not joules). The evaluator alone calculated it after acquisition.

## All first-run primary aggregates

| Method | Mean latent regret: constant noise | Mean latent regret: varying noise | Mean finished designs | Mean partial designs |
| --- | ---: | ---: | ---: | ---: |
| GP–ARD bundled | **0.000000** | 0.020050 | 16 | 0 |
| GP pooled-noise EI | 0.010025 | **0.000000** | 16 | 0 |
| GP pooled-noise IVR | 0.245064 | 0.122532 | 16 | 0 |
| Random bundled | 0.225014 | 0.225014 | 16 | 0 |
| BHS v12 evidence gate | 0.310326 | 0.155163 | 15 | 3 |

Each mean combines exactly four dependent developmental campaigns (two previously explored decision seeds times two reveal-order variants). An average of zero denotes finding the best latent design **in these specific constructed campaigns**, not a verified zero error rate or physical optimum.

### Reveal-order sensitivity

Under **constant** noise, the GP pooled-noise EI method changed final latent regret by 0.040099 in seed 7 when the within-design response order changed; the other methods had zero change in their final regret for both decision seeds, though this does not prove identical acquisition paths.

Under **varying** noise, the evidence gate's regret changed by 0.620653 in seed 13 and the GP pooled-noise IVR method's by 0.409928 in seed 7. The other final-regret differences were zero. **Equal regret does not establish equal design trajectories.** Order sensitivity of partly revealed evidence remains a meaningful research concern.

## Restrictions and inference

- No statistical significance, confidence interval or generalized superiority claim can be supported by these tiny, engineered, dependent development samples.
- The gate's three unfinished geometries reveal a completion weakness **under this particular budget convention**, but method differences also reflect acquisition heuristics, noise models and completion rules. This is not a causal attribution to repetition alone.
- The varying-noise source intentionally violates the pooled-variance assumption of the adaptive GP models; there is no externally calibrated uncertainty or laboratory provenance.
- The test source and historical physical archive are distinct. The earlier V11 negative result and the first V12 failed historical parity gate were not changed, reinterpreted or cleared by these runs.
- No hidden response, seed 10000–10099, physical experiment, or independent validation was used.

## Future research decision

Do **not** tune the current manufactured case until it produces a favorable gate score. Freeze a separately identified next protocol focused on (1) completion-aware reservation with decision coverage at equal budget, (2) comparisons to genuine adaptive repetition baselines with matched completion constraints, (3) more diverse simulated landscapes and noise models before fixing a candidate for real evaluation, and (4) prospective new laboratory data with actual chronology, batch provenance, costs, expert supervision and independent validation. A v12.4 method change must be reported as a new exploratory version, never as retroactive validation of v12.3.

## Mandatory evidence flags

`development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `causal_identification=false`, `calibrated_uncertainty_proven=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `reserved_nist_seeds_used=false`.
