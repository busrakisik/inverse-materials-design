# BHS v12 — Pre-replay measurement integrity and scientific limitations

**Status:** Development protocol review; prepared on 7 November 2026 before the first outcome-scored v12 historical replay. This note does not report new historical measurements or score results.

## 1. Fixed historical context

V11 used 600 distinct historical 3D-printed geometries with three responses each. The existing statistical kernel-portfolio EI selector did not outperform the GP–ARD EI or RF–UCB references on mean five-seed retrospective simple regret. V12 is not a new independent study of that source: the same dataset and development seeds were already examined in prior stages. A favorable result, if any, is hypothesis-generating rather than confirmatory. The original records do not provide trustworthy within-geometry measurement chronology, batch, printer or environmental covariates.

## 2. Pre-scoring implementation corrections

The measurement oracle now tracks which historical observations have been revealed. Requests that skip ordinals, repeat an observation or attempt more than three measurements for one design fail closed. At evaluation, the private oracle cross-checks the reported observation transcript against its reveal ledger, including both the geometry IDs and observed values. No private outcomes or ledger records are passed to the policy. These are measurement-accounting safeguards: the four frozen policy definitions and scoring conventions have **not** changed.

The expanded synthetic tests exercise duplicate-reveal rejection, out-of-order rejection, exact transcript integrity, oracle input copying and the prior V11 bundled-reference scoring convention. Successful tests are *software evidence only*. GitHub Actions with pinned numerical libraries is the authoritative verification environment; local libraries need not match the pinned versions.

## 3. Quantitative estimand and known limitations

The primary endpoint is the full source-pool's highest *historical triplicate mean* less the highest full-triplicate mean of a completed design acquired by the policy, measured in joules. In particular, an incomplete design is ineligible for the primary final recommendation. This is a decision convention, not a claim about real laboratories or a latent optimum. The five previously explored seeds do not support confidence intervals, significance claims or independent generalization. The random historical within-design permutation is deterministic for the published seed but is not measured real-world experiment order. GP variance plug-ins and RF tree spread are neither externally calibrated nor validated physical uncertainty.

The experiment tests four predeclared *policies*, not a pure replication mechanism. Three references use bundled triplicates; one gate can spend budget on incomplete designs. Any difference combines exploration, completion and repetition effects and cannot support causal attribution to replication. Existing experimental-design methods already consider allocation between new experiments and replicates, so a novel research contribution must be established against matched adaptive-replication references, not bundled GP alone.

## 4. Literature anchors for the next independent study

- Binois and Gramacy, **Replication or Exploration? Sequential Design for Stochastic Simulation Experiments**, *Technometrics*, DOI: [10.1080/00401706.2018.1469433](https://doi.org/10.1080/00401706.2018.1469433): lookahead-based selection between replicates and new input sites with noise-aware Gaussian-process surrogates.
- Binois and Gramacy, **hetGP: Heteroskedastic Gaussian Process Modeling and Sequential Design in R**, *Journal of Statistical Software* 98(13), 2021, DOI: [10.18637/jss.v098.i13](https://doi.org/10.18637/jss.v098.i13): input-dependent noise, replication and sequential design.
- Russo, **Simple Bayesian Algorithms for Best-Arm Identification**, *Operations Research*, 2020, DOI: [10.1287/opre.2019.1911](https://doi.org/10.1287/opre.2019.1911): fixed-budget allocation for reliable identification of the best option from noisy experiments.
- Slautin et al., **Measurements with noise: Bayesian optimization for co-optimizing noise and property discovery in automated experiments**, *Digital Discovery* 4, 2025, DOI: [10.1039/D4DD00391H](https://doi.org/10.1039/D4DD00391H): practical experimental noise/measurement-time tradeoffs.

These references motivate stricter controls, but do not validate the BHS gate or establish equivalence among experimental cost definitions.

## 5. Post-replay decision rules (no retroactive score tuning)

- **Gate worse than or equal to GP–ARD bundled:** report the negative finding, preserve the original source-locked record, and do not tune the same evaluation and present it as fresh confirmation.
- **Gate better than GP–ARD bundled:** describe an exploratory advantage on this already-examined archive only; separately test measurement-order sensitivity, equal-budget adaptive-repeat GP, decision loss, and fresh laboratory sources before any superiority claim.
- **Any broken source checksum, budget, transcript or baseline-parity test:** keep an audit trail and aggregate artifact if produced; report the run as invalid, not as a negative or positive scientific result.
- **Unexpectedly high incomplete-design rate or order dependence:** treat as evidence of policy fragility; analyze prospectively under a separately named protocol with an untouched dataset.

The prospective research question should compare calibrated decision loss and abstention at equal measurement cost and coverage, not only minimum recorded regret. A viable future hypothesis-centered architecture will additionally need scientifically specified hypotheses, valid likelihood models, independent physical tests and investigator-supervised stopping rules.

## 6. Hard restrictions

`development_only=true`  
`scored_validation_allowed=false`  
`independent_holdout_used=false`  
`physical_validation_by_bhs=false`  
`causal_identification=false`  
`calibrated_uncertainty_proven=false`  
`claim_of_superiority=false`  
`real_savings_measured=false`  
`reserved_nist_seeds_used=false`

Protected NIST seeds `10000..10099` must remain untouched. Keep V11 negative results and all historical version/DOI provenance. Do not rewrite the public history or delete tags as part of V12 development.
