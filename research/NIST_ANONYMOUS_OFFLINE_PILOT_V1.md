# BHS — NIST Anonymous-Coordinate Offline Development Pilot v1

**Research goal:** Run the first *integrated*, reproducible, offline historical-data replay on NIST Fe–Co–Ni Kerr rotation while the exact Fe/Co/Ni column order is unresolved. This is **NOT scored independent validation**, **NOT a causal/physical mechanism test**, and **NOT a prospective experimental campaign**.

## Provenance and references

- Pinned public dataset (do not redistribute): NIST `usnistgov/remi` commit `596b04435fb577175264a70c4434f5539b809510`, Git blob SHA-1 `e506db115d522d62618042abead7df2695ccf13e`, exactly 289480 bytes. Existing `scripts.nist_dataset_inspection_v1.fetch_source` validates bytes before use.
- NIST data dictionary confirms `C`, `Kerr` (mrad), `Coer` (mT), `XRD`, and `TTH`, but *not* composition column element order or measurement std.
- Wang et al. (2022), *Benchmarking Active Learning Strategies for Materials Optimization and Discovery*, doi:10.1093/oxfmat/itac006; paper and published code: https://academic.oup.com/ooms/article/2/1/itac006/6637521 and https://github.com/alex-aa-wang/Benchmarking-Active-Learning-Starter. Published code supports the GP–EI comparator design but is **not reused/copied** (different stack and data contract). Its code does **not** independently establish the `C` column–element mapping. It is MIT licensed, but this does not grant identical rights for the dataset itself.
- Yoo et al. 2006, *Identification of amorphous phases in the Fe–Ni–Co ternary alloy system using continuous phase diagram material chips*, *Intermetallics* 14, 241–247.

## Exact scientific scope

This exploratory run treats columns in `C` as **three anonymous coordinate axes**, `source_col_0/1/2`, and normalizes each finite nonnegative row by its sum ONLY if raw sum is near 1 (±.02) or 100 (±2). A sum check is numeric, **not proof of atomic fraction units**. All functional models—including the source BHS model internally named `fe_co_interaction`—must be interpreted purely as `source_col_0 * source_col_1`; **no Fe–Co mechanism or element label is asserted**. Result depends on coordinate ordering and the fixed arbitrary bump basis. `Kerr` scalar response units are mrad; no log/abs transforms. The eligible offline set is defined by having a finite Kerr label: **this is retrospective target availability conditioning**, and does *not* prove a real prospective candidate sampling policy could know eligibility.

No raw rows, indices, target values or per-step observations are included in artifacts, only aggregated exploration diagnostic and source SHA-256.

## Closed replay and policy comparison

- Each policy sees anonymous coordinates and previously *selected* Kerr labels only. An evaluation wrapper holds the complete historical label vector for lookup and end-of-campaign regret, not for selection. Test the selector's no-hidden-label API and no repeated acquisition.
- All policies share the same three random initial points for each seed; new observations are standardized **only using these common initial selected labels** (no full-dataset normalization). Seeds: 7, 13, 23. Total 15 samples per campaign, 4 policies × 3 seeds = 12 retrospective campaigns.
- `random`: uniform without replacement.
- `gp_ei`: scikit-learn 2D (first two anonymous axes, third implicit) Gaussian Process; fixed RBF lengthscale 0.22, fixed observation-noise alpha 0.15² on initial-standardized labels; EI for maximization. Hyperparameters **not fitted or optimized**, and no claim to fully reproduce the publication's GP baseline.
- `gp_ucb`: identical GP, acquisition μ+2σ. This is a fixed exploration coefficient, not the original paper's dynamic-UCB scheme.
- `bhs_bma_ei`: integration of existing `MultivariateBelief`'s three **phenomenological shape** families via posterior-probability-weighted Expected Improvement. This is **Bayesian model-average EI (BMA-EI)**, a simple research candidate, *not* proof of novel hypothesis identification. Assumed Gaussian noise std .15 in standardized units, not measured uncertainty. The code's third-feature label remains inherited from the older module and does not certify which element corresponds to each axis.
- Each policy is compared at the **same number of selected measurements**. All have equal hypothetical unit cost; there are no empirical instrument costs.
- The evaluator computes normalized final *simple regret* `(eligible_pool_max - best_observed)/eligible_pool_range` **only after** a policy has finished; the policy never accesses full-pool max, unselected labels, target normalization based on unseen labels, or test/holdout seeds.

## Limitations that must remain in every conclusion

1. Sample-level repeated compositions/batch associations, missingness not missing-at-random, metadata and permissions are unresolved; the eligible pool can be selection-biased.
2. True per-measurement uncertainty is unknown; prior/noise/kernel/feature choices are hypothetical. No predictive calibration claimed.
3. Fixed GP hyperparameters and tiny three-seed comparison are development checks, *not* robust or competitive final baselines. Later optimize/tune GP appropriately and compare with strong BO packages using a frozen development protocol, without leakage.
4. Results (whether favorable or unfavorable to BHS) are **exploratory development diagnostics**, not evidence of superiority, independent scored validation, or achieved savings.
5. Domain-validated Fe/Co/Ni columns and scientifically mechanistic hypotheses remain unverified; no physical materials conclusions allowed.
6. Separate `research/BHS_PROJECT_HANDOFF.md` should be updated with verified CI evidence *after* the workflow actually succeeds, not in advance.

## Reproduction (Python 3.11)

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2
python -m unittest discover -s tests -p 'test_nist_anonymous_offline_pilot_v1.py' -v
python -m scripts.nist_anonymous_offline_pilot_v1 --fetch
```

The fetch uses exact pinned bytes at NIST, no original data is committed or uploaded. Only aggregated `runs/nist_anonymous_offline_pilot_v1/aggregate_dev_report.json` and its SHA-256 are uploaded in CI. No exact performance result is known until that workflow succeeds.

**Mandatory flags**: `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, `claim_of_superiority=false`; independent BHS holdout seeds **10000–10099** never used.
