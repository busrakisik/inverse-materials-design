# BHS Matbench expt_gap — benchmark objective and baselines, v1

**Status: PROPOSED / NOT FROZEN / NO HELD-OUT LABELS READ / NO REAL BENCHMARK RUN.**
Date: 2026-11-02. Research branch: `bhs-scientific-audit`.

## Scope and provenance
- Matbench v0.1 `matbench_expt_gap`, experimental band gap in **eV**, 4,604 composition rows.
- Raw `.json.gz` SHA-256: `783e7d1461eb83b00b2f2942da4b95fda5e58a0d1ae26b581c24cf8a82ca75b2` (reverified twice).
- Frozen chemical-system split v1: train 3,282 rows / 2,640 chemical systems; validation 647 / 523; test 675 / 542. Original row IDs in the manifest; test labels never part of splitter.
- No overlap in unordered element-set chemical systems across partitions. Train and test share 80 chemical elements (Jaccard 80/81); **not an element-disjoint / family-disjoint / structure-disjoint holdout**.
- Upstream source-data redistribution/licensing review remains open. Do not commit raw labels or raw dataset to repository or artifacts.
- This is *offline selection of known materials in a fixed pool*; not structure generation, crystal stability, DFT, or discovery of previously unknown matter.

## Proposed scientific question
At equal query budgets and permitted information, can a hypothesis-conditioned sequential policy acquire **experimentally labeled compositions with band gaps near a preregistered target** sooner than non-hypothesis and adaptive baselines, on held-out chemical systems?

## Proposed task (not frozen; must approve before unblinding)
- Application motivating a target band gap: illustrative light-absorber candidate screening. Optical/electronic suitability cannot be inferred from band gap alone.
- **Proposed target:** 1.5 eV; value must be justified by citations and *fixed before examining held-out target distribution*. Do not change to favor a method.
- One-query reward: `r_i = -abs(Eg_i - 1.5 eV)`; larger is better. Invalid/missing values: prespecify exclusion from candidate pool using label-free validity metadata, or charge query and return failure; never silently remove difficult test points after revealing labels.
- Primary endpoint per independent evaluation problem: best observed reward after **K=10 distinct queries**; first-query performance and the full best-so-far curve are secondary. Use the same budget K and same eligible pool per policy.
- Secondary threshold: `abs(Eg - 1.5 eV) <= 0.2 eV` as *proposed*, not scientifically validated by itself; report success@K, area under best-so-far curve, wall-clock overhead.
- Use validation alone to assess whether K=10 is a meaningful affordable protocol *without inspecting test labels*. Any changes go into a new version, never a post hoc edit.

## Problems, replication, and uncertainty
- **Proposed**: deterministically allocate whole *test chemical systems* to five non-overlapping evaluation pools using a second fixed hash namespace, independent of labels. This is not a new train/test split. Use original held-out test membership and ensure pools have >K candidates.
- Pair policies on the same pool and predeclared random seeds `0..9`. Ten seeds on one pool are *not* ten independent scientific datasets.
- Report five per-pool policy differences and their uncertainty; clearly label small number of independent pools (n=5), and do not overclaim significance. Consider additional external independent datasets for real generalization evidence.
- Do not inspect test outcomes before freezing pool construction, policies, objective, features, seeds, and analysis code. The measured test label is revealed only after a query through a shared oracle; future candidate outcomes are inaccessible.

## Pre-registered comparison policies (implementation pending)
1. **Random without replacement**: seeded uniform selection, no label-informed adaptation.
2. **Static learned composition-only surrogate**: train a fixed feature pipeline and ridge/other predeclared regression model on **training** labels only; choose lowest predicted `abs(Eg - target)` once, no updating on test observations. Select model/hyperparameters using **validation** only. Prefer a defensible fixed composition descriptor and document dependencies.
3. **Adaptive non-hypothesis surrogate**: same eligible features, incrementally refit/update with labels of **queried candidates only**; predeclare a simple acquisition score, uncertainty estimation, and computational budget. Must not use held-out labels except queried observations. A trivial model must not be described as a strong baseline.
4. **BHS hypothesis-conditioned policy**: **DO NOT RUN OR CLAIM RESULTS YET**. Requires explicit chemical hypothesis representation, mathematically specified prior/likelihood and calibration, legal evidence-update protocol, and end-to-end executable candidate selection. Existing code is insufficient.

## Information firewall and integrity requirements
- Split uses compositions only and a verified SHA. Train/validation labels can be accessed for model training / selection, but test labels are loaded only by the isolated oracle process.
- Policies receive candidate IDs, public formula-derived descriptors, query history, and previously revealed labels, never the oracle's full answer map or arrays derived from unrevealed labels.
- Every call must consume one unit budget, forbid replacement, and log policy name/version, candidate ID, reveal, seed, problem ID, step index, and wall time without publishing copyrighted upstream data.
- Leakage tests: adversarial policy attempts to access oracle internals, order invariance, re-query refusal, identical eligible candidate lists, seed reproducibility, no training on validation/test labels, group/pool disjointness.
- Before any real test evaluation, document data rights, target validity, missingness handling, descriptor and hyperparameter selection, frozen Git commit, Python environment, source hashes, and uncertainty plan.

## Decision gates and claims
**Gate A — Prereg review:** rationale for target; realistic application, pools, K, baselines, statistical units, license; record independent review comments.
**Gate B — Synthetic interface tests:** shared oracle, test-label firewall, deterministic pools, budget accounting, adversarial leakage, correct metrics. No material scores.
**Gate C — Validation-only dry run:** train + validation evaluation and diagnostic plots; refine only under new protocol version. No test-score peeking.
**Gate D — Freeze:** immutable commit + hash, objective, budget, seeds, policies, exclusion rules and analysis code; then one clearly designated blind test evaluation.
**Gate E — Interpretation:** report all baselines, negative results, limitations and per-pool uncertainty; never reinterpret CHGNet potential energies as experimental gaps or formation energies.

**Current status:** completed data integrity and chemical-system split audit only. No baseline model, real selection curve, calibrated hypothesis-conditioned BHS, or empirical superiority result exists yet.
