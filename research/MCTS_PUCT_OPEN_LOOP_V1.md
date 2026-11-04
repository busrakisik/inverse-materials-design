# BHS MCTS/PUCT v1 — Open-Loop Synthetic Research Prototype

**Status: EXPLORATORY / DEVELOPMENT ONLY / NO HOLDOUT / NO MATERIALS CLAIM.**

## What's implemented

- True Monte Carlo tree **selection, expansion, rollout and backpropagation**, with PUCT action selection.
- Candidate-ID action tree with sampled latent linear-model slope and sampled noisy outcomes for each simulation.
- Conjugate Gaussian posterior inferred exclusively from scalar *public descriptors* and *previously observed* outcomes via `BayesianOnlyPolicyV1.posterior`.
- Root action chosen by visit count; deterministic seeded simulation and stable tie-breaking.
- No hidden label map is passed into the policy.
- Test coverage for PUCT root accounting, reproducibility, failed inputs, and existing development task integration.

## Crucial scientific limitations

This is **open-loop candidate planning**. The tree branches on action IDs **not observation outcomes**, and it does not update a simulated posterior at each imagined node. It is **not** a full belief-state MCTS/POMDP planner, not a scientific-hypothesis graph, and not an implementation of a real materials physical evaluator.

The synthetic belief model is **single-dimensional, linear, Gaussian and knowingly misspecified** for some tasks. Reward is simulated improvement over the current observed best (zero before any measurements); these are *model rewards* and cannot be described as experimentally measured improvements.

The current `MeteredEvaluator` remains an in-process trusted-host evaluation; it is not an adversarial sandbox. Process separation demonstrated in v1 is a separate interface and has **not yet integrated this PUCT policy**.

## Reproducibility and safeguards

- Run Python 3.11.9; stdlib only for these files.
- Development demo fixed to `scenario=smooth`, task seed `7`, policy seed `13`, query budget `5`.
- No independent seeds `10000..10099` may be evaluated at this stage.
- No replacement of Bayesian-only baseline and no confirmatory comparisons; any tuning against pilot tasks would require new preregistered validation.
- `scored_validation_allowed=false` remains the gating decision.

## Next research directions

1. Inspect actual root visit/Q diagnostics on development tasks; compare against transparent heuristics without claiming superiority.
2. Introduce a **belief-state / observation-conditioned** search tree and richer hypothesis families; test calibration on development data.
3. Integrate a controlled policy worker protocol, timeouts, input schemas, and a real OS sandbox before evaluating untrusted policies.
4. Freeze the updated algorithm version and independent validation design only after the evidence and reviewer gates have passed.
