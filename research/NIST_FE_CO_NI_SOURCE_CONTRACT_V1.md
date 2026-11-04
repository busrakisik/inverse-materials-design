# BHS — NIST Fe–Co–Ni Source Contract v1

**Status: verified upstream repository metadata and data dictionary, NOT a loaded dataset or a real-data benchmark.**

## Verified upstream resources (2026-11-04)
- NIST REMI: https://pages.nist.gov/remi/data/
- GitHub: https://github.com/usnistgov/remi/tree/nist-pages/data/Combinatorial%20Libraries/Fe-Co-Ni
- MATLAB file: `FeCoNi_benchmark_dataset_220501a.mat` (GitHub metadata: 289480 bytes, git blob `e506db115d522d62618042abead7df2695ccf13e`)
- Data dictionary: `data description.txt` (git blob `a2bc0f1973cefd38759d7129d5b7573ab9f53b09`)

Source dictionary fields: `C` (composition); `XRD` (X-ray diffraction); `TTH` (two-theta positions); `Coer` (magnetic coercivity, **mT**); `Kerr` (Kerr rotation, **mrad**). The dictionary states entries correspond to samples by row. It does **not** establish the dimensions, missingness, calibration, replicate error, exact composition units, time or cost metadata.

Data dictionary requests citations to Wang et al. (2022) and Yoo et al. (2006). Primary article: https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery

## Honest readiness decision
The `.mat` binary was NOT downloaded, hashed at byte level, loaded, executed, or redistributed in this phase; the source Git blob SHA is **not** a conventional SHA-256 digest. Field names are dictionary claims, not observations of actual arrays.

The current BHS scalar Gaussian models (linear/quadratic/sine) cannot meaningfully model three-component alloy composition without redesigned scientifically supported hypotheses. Real measurement errors, laboratory costs, and permission/redistribution terms are unverified. The source being public does not automatically prove downstream commercial rights.

## Next bounded task
- Retrieve the pinned upstream MAT file in a controlled environment. Record SHA-256, verify expected Git blob / immutable source commit, file magic, MATLAB variable names, shapes, NaN counts and units from source documentation.
- **Do not inspect any pre-reserved BHS independent holdout tasks**. The NIST dataset is an external candidate and is not the independent holdout, but future evaluation still needs leakage-safe splits and permissions.
- Review data terms and license; avoid bundling raw observations into this repo until rights are established.
- Involve a domain scientist in hypothesis definition; distinguish scientific model discrimination from property optimization. Consider Expected Improvement and relevant active-learning baselines, with reproducible splits and calibration.

## Run
```bash
python -m unittest discover -s tests -p 'test_nist_source_contract_v1.py' -v
python -m scripts.nist_source_contract_v1
```
`scored_validation_allowed=false`, `physical_validation=false`, no independent holdout.
