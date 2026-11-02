# BHS Paired Benchmark Pilot v1

**STATUS: SYNTHETIC_ONLY / EXPLORATORY / NOT_CONFIRMATORY / NOT_REAL_MATERIALS.**

This pilot runs existing Random-without-replacement, DescriptorGreedy, and BayesianOnlyPolicyV1 against identical synthetic task/seed/budget pools (5 scenarios × 30 seeds × 4 budgets × 3 policies = 1800 rows). Only previous observations reach the policy. Hidden utilities remain evaluator-side; the evaluator can calculate simple regret after the run. Pairing is by identical scenario, task seed, and budget. Python RNG policy seeds are deterministically derived from the task/policy identifiers.

Use `python -m unittest discover -s tests -p 'test_paired_benchmark_pilot_v1.py' -v` to verify the contracts; `python -m scripts.paired_benchmark_pilot_v1 --out-dir runs/paired_pilot_v1` generates pilot logs. The artifact contains query traces and numeric synthetic outcomes: do not publish it as an experimental materials result.

**Major caveats:** This is NOT an OS sandbox; policies execute in the evaluator process, so these contracts are appropriate only for trusted local code and synthetic labels. The model is a one-dimensional Gaussian regression policy, not MCTS or calibrated physical evidence. The generator and parameters are not yet frozen; CI tests are functional tests and not a confirmatory study. Wall times are descriptive and not suitable for cross-machine comparison. The pilot has no bootstrap confidence intervals yet, and no primary superiority claim should be made. Do not inspect pilot outcomes to retroactively tune the model and then call those same seeds held-out results. If tuning occurs, freeze code, data, protocol, and use fresh held-out seeds with a separate independent evaluator.

Do not merge to `main`, mint a Zenodo release, or use real held-out material labels based on this CI.
