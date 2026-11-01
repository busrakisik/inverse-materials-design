# BHS Matbench expt_gap — chemical-system split gate v1

**Status:** CODE_VALIDATED_ON_SYNTHETIC_FIXTURES / REAL_SPLIT_NOT_RUN / BENCHMARK_NOT_RUN.

- Dataset: Matbench v0.1 `matbench_expt_gap`; expected compressed SHA-256 `783e7d1461eb83b00b2f2942da4b95fda5e58a0d1ae26b581c24cf8a82ca75b2` from two November 1, 2026 GitHub Actions acquisitions.
- Only compositional strings enter the split function. The output does **not** contain experimental band-gap measurements.
- Leakage grouping: unordered **element-set** chemical system (e.g., Li–Fe–O–P); all samples sharing one element set remain in one partition. This is stronger than a random-row split, but NOT a guarantee of independent material families, nor a universally accepted split for every scientific question. Element overlap across distinct chemical systems is possible.
- Fixed hash assignment with salt `BHS-MATBENCH-EXPT-GAP-CHEMSYS-SPLIT-V1-2026-11-01`: train [0,.70), validation [.70,.85), test [.85,1), based on SHA-256's first 64 bits of `salt|chemical_system`. These are assignment probabilities over groups, **not guaranteed row proportions**.
- Fail closed if source hash differs, formula fails parsing, duplicate reduced compositions are detected, or any split has zero chemical systems. Duplicates must be audited, not silently discarded.
- The manifest lists original row indices and hash pseudonyms, but not targets. It MUST NOT be interpreted as safe-to-train or frozen benchmark unless endpoint, query budget, metrics, uncertainty methodology and license review are finalized.
- Test-label secrecy needs its own later execution firewall and controlled oracle; this module **does not independently enforce data access control**.
- Copyright/license: Matbench repository MIT software license is not automatic permission for all upstream experimental-data redistribution. Raw dataset remains out of GitHub artifacts until rights reviewed.
- The BHS hypothesis-conditioned selection policy and calibrated evidence model remain unimplemented. No search advantage is claimed.

## Next stage
1. Upload the two Python files and this protocol document to research branch.
2. Independently run the 10 synthetic unit tests in CI; do not trigger real data split until passing.
3. Run a manual controlled split creation on the verified dataset, inspect group sizes, class/family imbalance, and any failures. Reassess family hold-out before releasing a benchmark split.
