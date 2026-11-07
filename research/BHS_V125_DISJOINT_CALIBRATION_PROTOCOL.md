# BHS v12.5 — Disjoint-group selective-decision calibration

**Prepared 7 November 2026, before any v12.5 scored output.** This is a manufactured development protocol, not an independent physical experiment. Its entire calibration and evaluation design is fixed here before model execution. Earlier v11–v12.4 negative, mixed and non-passing findings remain unchanged.

## Decision question and falsification

When an identical decision-readiness rule is fitted only on a calibration group of manufactured campaigns, does it achieve useful recommendation coverage and tolerable latent decision error on entirely disjoint evaluation groups? The important failure case is a procedure which passes calibration but accepts incorrect recommendations on evaluation data, especially under group-level batch effects and distribution shift. Report this even when one method performs well in other scenarios.

An unmodified reference method cannot be declared superior from eight related synthetic evaluation campaigns. Selective coverage, accepted-only regret, high-regret error frequency, zero-coverage, and overall abstention-adjusted loss must be reported **together**.

## Source construction and disjoint assignment

- 48 candidate geometries per campaign, four candidate descriptors per geometry, and three possible observations per geometry. All descriptors, latent qualities and measurement noise are derived deterministically from `SeedSequence` streams keyed by **source seed 12507011**, **noise seed 12507019**, and unique group ID. Distinct groups never reuse an outcome array, a geometry ID namespace, or a calibration case.
- Calibration group definitions, frozen as `(group, landscape, noise, policy seed)`:
  - `(101, ridge, constant, 17)`
  - `(103, oscillatory, varying, 37)`
  - `(107, ridge, batch, 41)`
  - `(109, oscillatory, constant, 53)`
- Evaluation-only group definitions:
  - `(211, ridge, constant, 17)`
  - `(223, oscillatory, varying, 37)`
  - `(227, ridge, batch, 41)`
  - `(229, shifted, batch, 53)`
- Two fixed within-geometry reveal orders `0, 1` per group, created from an independent deterministic stream keyed by group, policy seed, reveal-order variant and geometry ID. Two reveal orders of the same group are **correlated sensitivity scenarios**, not independent replicates.
- `ridge`: latent `3 + 1.4 exp(-6(x0-0.35)^2) + 0.9x1 - 0.6x2^2 + 0.5x0x3`.
- `oscillatory`: latent `3 + 1.1 sin(2.5πx0) cos(1.5πx1) + 0.7x2x3 - 0.4x1^2`.
- `shifted`: latent `2.6 + 1.3 cos(2πx0*x1) - 0.9x2 + 0.6x3^2`. **This landscape is absent from calibration.**
- Noise regimes: `constant` per-response SD `0.35`; `varying` geometry-dependent SD `0.15 + 0.55*(x0+1)/2`; `batch` per-response independent SD `0.30` plus a shared **group-of-eight-geometries** additive normal batch offset with SD `0.55`. Batch offsets repeat across the three measurements of each affected design; pooled within-design noise misses this between-batch variation.
- New streams are independent of the prior V12.3 and V12.4 manufactured sources. No empirical historical physical source is fetched.

## Frozen acquisition comparison

Six inherited v12.4 arms, unchanged: `random_bundled`, `gp_ard_bundled`, `gp_pooled_noise_ivr`, `gp_pooled_noise_ei`, `evidence_gate_native`, and `evidence_gate_completion`. The native gate remains an **unmatched diagnostic arm**; the other five use the earlier documented completion feasibility wrapper. This asymmetry must remain visible.

A campaign has exactly 48 response actions. Six seed-selected designs begin with three observations each, consuming 18; all later actions reveal **one** previously unseen response until the response budget is exhausted. At most three designs are partially measured. The selector receives only public geometry descriptors, already revealed response values, the permitted selection seed and the current action number. The evaluator privately holds latent qualities, future outcomes, noise amplitudes and chronological order. Only fully measured designs are eligible for final recommendations.

## Calibration target and exact selection rule

The shared decision evidence score is `s = (largest observed completed mean − second-largest completed mean) / max(estimated pooled standard error, 1e−8)`, with a pooled within-completed-design variance using sample degrees of freedom. This is a **heuristic margin**, not a calibrated posterior error probability.

For **each policy separately**, fit a deterministic *strict* acceptance threshold **only from that policy's eight calibration cases** (four calibration groups × two within-group order variants). The threshold may use only the calibration evidence score and the evaluator-only calibration latent regret; none of the evaluation group outcomes, scores or errors may be supplied to fitting. Threshold selection enumerates each distinct observed calibration score, plus predetermined all-accept and none-accept sentinels. Choose the candidate accepting the most calibration cases subject to BOTH: (i) accepted calibration fraction ≤ **0.50**, and (ii) empirical calibration failure fraction ≤ **0.25**, where a failure is latent recommendation regret **> 0.35**. Ties use the largest threshold (most conservative); if no nonempty set qualifies, the result is **abstain always**. Acceptance is strictly `score > threshold`. All chosen thresholds and exact calibration denominators must be serialized before generating any evaluation group.

Primary fixed values: **target calibration coverage 0.50**, **empirical accepted failure cap 0.25**, **latent regret tolerance 0.35**, **abstention cost 0.50** (all quality differences are manufactured latent units). These were set without examining v12.5 outcome scores; they are heuristic development choices, not justified physical action costs. For a decision that is accepted, loss is evaluator-only latent recommendation regret; for an abstention, loss is 0.50.

A diagnostic grid with calibration coverage caps `0.25, 0.50, 0.75` and the same failure cap and abstention cost is fixed. The **0.50** cap is the only primary comparison. Recalibrating on evaluation results, selecting the best diagnostic target after seeing results, or masking zero-coverage policies is forbidden.

## Reporting and acceptance gates

Each group, reveal order and policy must report exact response budget, completed design count, partially measured design count, stranded partial responses, intervention count, evidence score and evaluator-only latent regret. Final evaluation must additionally report:

1. Accepted recommendation fraction and total numerator/denominator; zero acceptance is explicitly a result, not a missing score.
2. Accepted-only latent regret (or `null` if no accepted case), worst accepted latent regret (or `null`), empirical high-regret error fraction among accepted cases (or `null`), and unconditional abstention-adjusted loss.
3. Calibration-versus-evaluation coverage gap, accepted error gap, and per-group/per-noise diagnostics, including the never-calibrated `shifted` case.
4. Paired campaign-level differences in loss at equal response budgets; measurement-order variants must not be counted as independent physical trials.
5. Source fingerprints, exact immutable code/protocol commit references, numerical library versions, all failing tests and cryptographic SHA-256 for calibration and evaluation output files.

The source-independent contract suite must pass before the **two-stage** scored workflow starts. Stage 1 emits a source-locked calibration JSON with thresholds. Stage 2 reads that serialized calibration file, recomputes its thresholds for tamper detection, then and only then creates any evaluation groups. A separate branch must explicitly trigger scored computation; routine pushes must run only software tests. A passing software test is not evidence of recommendation effectiveness.

A threshold that meets the empirical cap on eight calibration observations provides **no distribution-free guarantee** at evaluation time. Model uncertainty is not demonstrated to be calibrated; 0.25 is an empirical development cap, not a significance or confidence statement. Any unmet calibration target, low evaluation coverage, high accepted error or distribution-shift failure must be preserved without changing the frozen threshold rule.

## Scientific boundaries

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `causal_identification=false`; `calibrated_uncertainty_proven=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `reserved_nist_seeds_used=false`.

Protected source seeds `10000..10099` remain unavailable. No old version tags are deleted, no history is rewritten, and no machine recommendation is permitted to initiate physical laboratory operations. Prospective physical validation requires actual measurement timestamps, replicate identity, equipment and batch provenance, measured costs, domain-expert review and predeclared decision losses.
