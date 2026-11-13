# BHS V12.17 — Frozen implementation-scope and fair-comparison readiness protocol

**13 November 2026. Frozen before running this contract and publishing its first machine-checked implementation map.** Initial source inspection was already performed: this is a transparent capability audit, **not** a blinded preregistration of unseen scientific outcomes. No source target, scientific utility or new benchmark score may be read in this stage.

## Why this audit is necessary

The research goal is a genuinely falsifiable *full* scientific hypothesis-selection system, with credible independent evidence updates, meaningful lookahead and defensible real laboratory decisions. The existing true-measurement V11 result is a legitimate negative **COMPONENT-LEVEL retrospective development comparison** of the old statistical two-kernel selection policy: GP–ARD EI mean regret 7.363 J, RF–UCB 8.983 J, inherited BHS v5 kernel-portfolio EI 9.368 J, uniform random 15.951 J, all at 16 design / 48 historical response budget per seed. Never call that comparison an evaluation of the complete hypothesis-centric architecture, and never rewrite the unfavorable result or reuse its development seeds as a fresh holdout.

The current published DFT source **FAILED** V12.16's original sample structural-equivalence prerequisite: same 42-atom 41 Fe + 1 He composition and identical lattice, but maximum species-aware matched displacement 0.4521222246251549 Å versus a frozen 0.001 Å threshold. The author's sample folder contains an `NSW=0` static analysis stage; original candidate generation chronology, physical cost, and policy-time access remain unverified. The owner's mandatory three-part test remains **per feature: origin; availability BEFORE expensive calculation; information available to each policy AT DECISION TIME**. No full BHS-vs-GP/RF scored run may proceed without that and a complete runnable policy.

## Fixed inspected implementation surface

Pin and examine these precise source implementations from immutable historical default commit `af882913f867c42bbc16794e4e53ffe2fea4fbba`, and ensure the later V12.16 evidence branch still has identical source blobs:

1. `src/imd_pipeline/agents/hypothesis_engine.py` Git blob `0ac39a960fecff27031769589ae5b467be526f84`: current illustrative family registry; no physical hypothesis choice.
2. `bhs/search/bayesian_engine.py` blob `f656a5f66f27048ff564b53ce36e30508800d555`: mathematical sequential Bayes posterior with caller-supplied, not independently authenticated likelihoods; `compute_uct` not implemented.
3. `src/imd_pipeline/agents/bayesian_reasoner.py` blob `771dfc6482d2e77f4b0f91d3a8ae2e59286cd48f`: compatibility adapter; no executed physical validation or MCTS.
4. `bhs/evidence/likelihoods.py` blob `8453b20c02527f55e357ef66d9a3ac100565ce47`: heuristic uncalibrated structural scores, not verified scientific likelihoods.
5. `scripts/mcts_puct_policy_v1.py` blob `7dfcbe6a18f4d459f691406adb79b29a54fc99dc`: *open-loop* scalar synthetic PUCT using Bayesian linear regression; tree branches on candidate ID, not possible received observations.
6. `src/imd_pipeline/agents/search_planner.py` blob `e5152ac9bbf49f8f011832aa94ada371568ecbbc`: no real experiment/compute allocation.
7. `scripts/policy_worker_v1.py` blob `1f3f55aeaf27fea41156e02678dfb267c262d5c9`: runner for scalar Bayesian-only toy policy, not full hypothesis-centric BHS.
8. `scripts/synthetic_policy_worker.py` blob `c2bd437930dd900672bcf4ddcdcc85fd5ec8863e`: software placeholder choosing first unqueried ID. This is **not** BHS.
9. `scripts/bhs_replicate_pool_v11.py` blob `65044ae33514020f55fe6cb10f62b03a9e955a05`: real physical retrospective component comparison, calls the kernel portfolio from `scripts/uci_concrete_v5.py`, not the hypothesis registry.
10. `scripts/uci_concrete_v5.py` blob `5f98093426ac9cf4c4fc431f0d4f9aeada6d462f`: previously exposed statistical kernel chooser.
11. `src/imd_pipeline/agents/consensus_engine.py` blob `410cba88136764aefd4bb79f300485ab21ebfb5f`: summarizes supplied energies; does not run independent model calculations.

Audit these **specific evaluated entrypoints**, do not assume this list exhausts every other possible source branch or independent prototype. No full-system absence claim can be generalized to code that was not inspected.

## Frozen questions and tests

A. **Executable mathematical update:** with explicitly synthetic priors `H0=H1=0.5` and supplied likelihoods `H0=0.75,H1=0.25`, confirm posterior `(0.75,0.25)`; reject invalid likelihood and do not call this physical evidence.

B. **Hypothesis registry truth:** illustrative `evaluate_competing_hypotheses` must return `selection_status=NOT_EVALUATED`, `chosen_hypothesis=None` and no validated candidate selection; fail if fabricated physical hypothesis outcomes appear.

C. **Planning and cost honesty:** legacy `compute_uct` must raise `NotImplementedError` on a hypothesis node; budget planner must return `NOT_ALLOCATED` and no simulated compute. Open-loop PUCT is an actual prototype but cannot be called observed-outcome-contingent scientific planning. Trace the *concrete* worker and V11 import/selection chains using pinned source rather than module labels.

D. **Likelihood provenance:** current source's hardness/novelty scores explicitly say uncalibrated. No authenticated physical `P(E|H)` generative likelihood, calibration, posterior coverage or independent verifier is asserted.

E. **Real component negative:** V11 read-only report and original entrypoint hashes frozen. Record GP and RF beats old BHS v5 mean regret by 2.005 J and 0.385 J, respectively; descriptive sample comparisons only. Do **not** run or tune a performance experiment under this architecture audit.

F. **Three-part input passport:** old DFT geometry fields remain unapproved. For hypothetical crossed-barrel domain, `n,theta,r,t` are printed-design parameters before mechanical measurement and passed as public unlabeled candidate descriptors in the V11 runner, but full BHS has not been implemented on that domain and this archive has no independent future holdout.

## Fail-closed transition requirements

A complete BHS policy requires *operational falsifiable scientific hypotheses*, justified evidence likelihoods conditioned only on acquired results, posterior updates coupled to candidate action utility, an observation-contingent lookahead or an accurately labeled noncontingent method, a defined budget and reproducible reference implementations. Require an identical information set and chronological view for BHS, optimized GP/RF and simple expert references, equal outcome/budget access, no train-test candidate overlap of physical independence units, and separate development/independent evaluation. If any item is absent, label it `NOT_IMPLEMENTED`, `NOT_VERIFIED` or `NOT_EVALUABLE`; do not fill with dummy values or silently call a kernel ensemble full BHS.

No scoring authorization is created by a passing code audit, new synthetic fixture or completed document. Global flags: `development_only=true`, `scored_validation_allowed=false`, `full_bhs_fair_comparison_ready=false`, `per_feature_origin_timing_access_certified=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `laboratory_action_allowed=false`.

Prior negative findings, unmerged draft PRs, untouched default branch and old release/tag history remain unchanged; protected NIST seeds `10000..10099` still unused.
