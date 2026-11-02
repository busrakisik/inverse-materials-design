# BHS Independent Validation v1 — Freeze and Holdout Protocol

**STATUS: PROPOSED / NOT_FROZEN / NOT_RUN / SYNTHETIC_ONLY.**

## Purpose
Independently assess the locked Bayesian-only policy against seeded random-without-replacement and descriptor greedy after the exploratory 30-seed pilot. A positive exploratory finding must not be presented as independent confirmation.

## Pre-freeze checklist
1. Record the exact Git commit SHA for the generator, policy, evaluator and baselines. Archive a checksum for each and a locked Python environment.
2. Preserve and archive the exploratory pilot artifact and the full list of all seeds examined in pilot or tuning.
3. Document the five generator scenarios and identify the primary comparison scenario **before** validation outcomes are inspected. If none is chosen, label all analyses exploratory.
4. Fix policy hyperparameters (prior variance, observation noise, exploration scale), tie rules, and per-policy random-seed derivation. No changes after validation results are viewed.
5. Independent audit of public-descriptor and hidden-label interfaces; ensure that test labels are never exposed to policy objects. Synthetic evaluator may run trusted code in-process; this is not a sandbox.
6. Commit this protocol with its exact frozen revision, date, and machine-readable manifest before generating held-out test outputs.

## Design
- Policies: random-without-replacement, descriptor greedy, Bayesian-only v1.
- Tasks: five existing synthetic scenarios, 20 candidates per task unless a frozen specification says otherwise.
- Budgets: 1, 2, 5, 10 selections without replacement.
- Holdout: at least 100 fresh paired task seeds per scenario, independently sampled and disjoint from every seed used for development, pilot, calibration or model selection. Freeze the seed list and its SHA-256 prior to outcomes.
- Same candidates, descriptors and hidden utilities across the three policies for each (scenario, task seed, budget).
- Policies see only descriptors, budget context where applicable, and their own previously observed responses.
- Primary outcome: best observed utility (larger is better) after budget 10. Primary estimand: paired mean (Bayesian-only minus seeded random) on one preselected primary scenario. Declare the primary scenario *before* any held-out results.
- Secondary: regret, area under the best-so-far curve, invalid actions, wall time. Other scenarios/budgets and comparisons are exploratory.

## Analysis and reporting
- Paired bootstrap: resample matched task-seed units, never individual policy rows, with 10,000 resamples and a predeclared fixed bootstrap seed; report 95% percentile interval and paired mean/median.
- Report all tasks, failures, missing values and all scenarios, including negative and zero results. Do not pool incompatible scenario utility scales.
- Predeclare how to handle ties and any invalid/missing run: fail closed rather than silently dropping results. No tuning against held-out outcomes.
- If any code or hyperparameter is revised after viewing outcomes, rename that experiment as exploratory and reserve a new, untouched validation set.

## Stage gates
Gate A: Freeze manifest and seed exclusions. Gate B: Independent leakage and deterministic reproducibility audit. Gate C: Held-out synthetic validation, one run per locked version. Gate D: Interpretation and ablations (on separate development data). Gate E: External physical materials evaluation only after separate dataset permission, trusted held-out host and genuine worker sandbox integration.

## Freeze manifest template
- Frozen commit SHA: TBD
- Generator SHA-256: TBD
- Baseline SHA-256: TBD
- Bayesian policy SHA-256: TBD
- Evaluator SHA-256: TBD
- Python/dependency lock SHA-256: TBD
- Excluded development/pilot seeds: TBD
- Held-out seed list SHA-256: TBD
- Primary scenario and rationale: TBD
- Policy hyperparameters: TBD
- Analysis/bootstrap seed: TBD
- Freeze timestamp: TBD

**Do not run or claim independent validation until all TBD fields have been resolved and frozen before viewing any held-out labels.**
