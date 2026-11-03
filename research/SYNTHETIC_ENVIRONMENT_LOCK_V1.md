# BHS Synthetic Benchmark Environment Provenance v1

**STATUS: PARTIAL_ENVIRONMENT_PIN / METADATA_ONLY / HOLDOUT_NOT_RUN / NOT_HERMETIC.**

## Scope
The three modules `scientific_benchmark_contract_v1.py`, `bayesian_only_policy_v1.py` and `paired_benchmark_pilot_v1.py` use Python standard-library imports and local BHS modules only. The repository-wide `requirements.txt` is intentionally **not** used for this subset. No Matbench, CHGNet, torch, pymatgen or physical-material labels are fetched or evaluated.

## Captured and enforced
- Exact Python patch: 3.11.9, Linux x86_64 in a GitHub `ubuntu-24.04` runner.
- Git commit, scoped-source SHA-256 digests, Python patch, platform and architecture.
- Static import allowlist. Raises on unexpected direct imports or certain obvious dynamic execution calls; **not** a sandbox or complete dependency analyzer.
- A machine-readable manifest and its SHA-256 digest.

## Explicitly not frozen
- The exact operating system runner image digest and Python interpreter build hash.
- GitHub Action dependencies by immutable commit SHA; these currently use release tags.
- Hidden runtime environment, locale, CPU, threading, or all system libraries.
- Historical seeds and independent reviewer approval.

`environment_fully_hermetic=false` and `scored_validation_allowed=false` MUST remain false. The next provenance gate should capture runner image and action SHAs and then obtain an independently reviewed full freeze before any validation evaluation. A green CI means metadata and scoped-import contract checks passed, not that holdout is approved.

## Reproduction
From repository root: `python -m unittest discover -s tests -p 'test_synthetic_environment_lock_v1.py' -v`. The workflow uses a pinned interpreter patch and invokes `python -m scripts.synthetic_environment_lock_v1`. The script refuses to run on non-matching interpreter patches.
