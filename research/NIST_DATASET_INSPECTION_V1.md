# BHS — NIST Fe-Co-Ni Real File Descriptive Inspection v1

**Purpose:** Verify the exact source file and inspect shape, missingness and basic physical-data plausibility. **Not** a BHS model run, material discovery, benchmark result, or license clearance.

## Verified source provenance

- Publisher: NIST REMI, https://pages.nist.gov/remi/data/
- Repository: `usnistgov/remi`, `nist-pages` branch; pinned immutable commit `596b04435fb577175264a70c4434f5539b809510`.
- File: `data/Combinatorial Libraries/Fe-Co-Ni/FeCoNi_benchmark_dataset_220501a.mat`.
- Expected Git blob SHA-1: `e506db115d522d62618042abead7df2695ccf13e`, expected exact size: 289480 bytes.
- NIST documentation identifies `C` (composition), `XRD` (X-ray diffraction), `TTH` (two theta coordinates), `Coer` (magnetic coercivity, mT), `Kerr` (Kerr rotation, mrad). The documentation does **not** identify independent per-row measurement standard deviations, actual experiment costs, or a calibrated hypothesis family.
- Papers requested by NIST data description: Wang et al., *Benchmarking Active Learning Strategies for Materials Optimization and Discovery* (2022), and Yoo et al., *Identification of amorphous phases in the Fe–Ni–Co ternary alloy system using continuous phase diagram material chips*, Intermetallics 14, 241–247 (2006).

## Data protection and inspection

The GitHub workflow downloads the **pinned public NIST binary at execution time**, checks byte length and Git blob SHA-1, parses the MATLAB file using SciPy, and emits ONLY aggregated statistics and schema information. It does not upload or commit the original data or any individual measurements. The report includes a bytewise SHA-256 digest for independently verifying the input. The workflow requires network access. A changed source file causes a fail-closed error.

Counts and proportions are **not known** until the workflow executes successfully against the pinned binary. Do not repeat the published 921 count as if obtained independently through our parser.

Composition column ordering (Fe/Co/Ni), normalization and consistency with measurement keys require review even if numeric summaries appear plausible. XRD and TTH shapes are inspected, not interpreted automatically. `C` has three-dimensional composition and cannot be silently mapped into the existing 1D x-linear/quadratic/oscillatory model.

## Run

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1
python -m unittest discover -s tests -p 'test_nist_dataset_inspection_v1.py' -v
python -m scripts.nist_dataset_inspection_v1 --fetch --out-dir runs/nist_dataset_inspection_v1
```

**Scientific restriction:** `scored_validation_allowed=false`, `independent_holdout_used=false`, `dataset_ready_for_bhs=false`, `physical_validation=false`, `real_data_experiment_executed=false`. This is a descriptive pilot readiness check, not a laboratory pilot. Do not enable scored independent validation or touch independent BHS holdout seeds.

## Publication/commercial milestones

After inspecting actual shapes/missingness, independently verify composition semantics, nonnegative coercivity handling, uncertainty measurements, costs and availability of meaningful discriminable hypotheses with a domain expert. Then build a leakage-safe offline evaluation environment, define strong baselines and freeze the protocol before any independent scoring. No saved cost is inferred from hypothetical budgets.
