# BHS MCTS Development Benchmark v1

**STATUS: EXPLORATORY / SYNTHETIC ONLY / NO INDEPENDENT HOLDOUT / NO REAL MATERIALS CLAIM.**

## Research question
Does the open-loop PUCT candidate-selection policy find larger best-observed utility than
Bayesian-only Thompson sampling on the exact same previously examined development tasks,
and what are the runtime costs and sensitivity to tree depth and simulation count?

## Setup
- Reuses existing `make_task`, `MeteredEvaluator`, `BayesianOnlyPolicyV1`, `OpenLoopPUCTPolicyV1`,
  `DescriptorGreedy`, and `UniformWithoutReplacement` WITHOUT modifications.
- Five synthetic scenarios: smooth, multimodal, uninformative, mismatched, duplicates.
- Default seeds: 0,1,2,3,4; CLI accepts only prefixes of 0..29, all previously observed in the pilot.
- Budgets: 1,5,10; candidates per task: 20.
- Six policies: random, greedy, Bayesian-only, PUCT(32,h1), PUCT(32,h3), PUCT(96,h3).
- Primary descriptive measurement: best observed synthetic utility; secondary: simple regret,
  wall-clock seconds, win fraction, and paired means and medians.
- RNG seed for original policies matches the existing pilot's `policy:<seed>:<scenario>:<policy>`
  derivation; PUCT configurations share a stable per-task MCTS random seed.
- No statistical significance, preregistered superiority claim, model calibration claim,
  or selection of a new confirmatory primary scenario follows from these analyses.

## How to run
```bash
python -m unittest discover -s tests -p 'test_mcts_development_benchmark_v1.py' -v
python -m scripts.mcts_development_benchmark_v1 --development-seed-count 5
```

Artifact contains `development_raw.jsonl`, `development_summary.jsonl`,
`development_manifest.json`, and checksum file. The deterministic values and candidate
IDs are reproducible; `wall_seconds` depends on runner load and environment.

## Interpretation limits
All task seeds are exploratory pilot seeds; comparisons are *not independent*. The policies
are executed **in-process** through trusted `MeteredEvaluator`. The PUCT tree branches on
candidate IDs, not hypothetical observations, so this does not demonstrate adaptive
value-of-information planning. Models are scalar, Gaussian, synthetic; no physical validation.

The negative-result question is scientifically meaningful. If PUCT is slower with no
improvement over Greedy or Bayesian-only, report the result and investigate whether the
synthetic task structure offers any benefit to longer-horizon planning rather than tuning
to produce a positive result.

`scored_validation_allowed = false` must not be changed as a result of this experiment.
