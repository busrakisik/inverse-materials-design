# BHS MCTS Ablation Audit v1 — actual 450 development records

**Exploratory-only, pilot-informed and non-confirmatory.** This is a reanalysis of an **existing** GitHub Actions artifact from run `41810700077`, artifact `13312032670`. It does not evaluate any new tasks or holdout seeds.

## Scientific objective

Separate two potential drivers of the open-loop MCTS policy:

1. `mcts_32_h3 − mcts_32_h1`: horizon effect at fixed 32 simulations.
2. `mcts_96_h3 − mcts_32_h3`: simulation count effect at fixed horizon 3.
3. `mcts_32_h3` and `mcts_96_h3` against Bayesian-only and Greedy at the exact same (scenario, task seed, query budget).

This preserves task-level pairing and avoids inadvertently treating policy outputs as independent samples. Descriptive mean and median deltas are calculated within each scenario and budget; no incompatible utility scales are pooled. Wins/ties/losses use a tolerance of 1e-12. All five task seeds 0–4 were previously inspected and therefore are not a clean test set.

## Provenance and failure behavior

The script refuses any archive whose SHA-256 differs from the pinned artifact. It checks the internal manifest SHA-256, five development seed IDs, five scenarios, three budgets, six policies, 450 rows and 75 fully paired task/budget/scenario groups. It requires unique action lists and a shared public-task fingerprint across policy variants. Any missing, changed or malformed evidence fails the workflow.

It records policy runtime only as a descriptive measurement: the GitHub Actions runner environment affects timing. The analyzer is stdlib-only and does not import an evaluator or generator. This is an advantage: auditing existing evidence cannot accidentally invoke the holdout generator.

## Reproduction

```bash
python -m unittest discover -s tests -p 'test_mcts_ablation_audit_v1.py' -v
python -m scripts.mcts_ablation_audit_v1 --archive mcts_development_artifact.zip
```

The workflow downloads the pinned historic artifact using the repository's already verified GitHub artifact download helper, which handles authentication redirects. If the original artifact has expired or changed, the audit must fail instead of fabricating results.

## Limits

- One existing development run, only n=5 previously seen seeds per cell; **no independent statistical generalization**.
- An improvement against Bayesian-only does not imply superiority over Greedy.
- More simulation steps or greater horizon may be slower and worse.
- The MCTS implementation is still open-loop, with no simulated belief updates per observation.
- This is *not* a physical materials benchmark or proof of novel scientific discovery.

`scored_validation_allowed = false` remains mandatory.
