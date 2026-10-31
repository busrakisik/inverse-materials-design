<!-- BEGIN OF COMPLETE BHS README — CHECK THIS LINE ON GITHUB -->
# Bayesian Hypothesis Search (BHS)
**Hypothesis-centered research prototype for computational materials discovery**

[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21761835.svg)](https://doi.org/10.5281/zenodo.21761835)

BHS investigates whether explicit scientific hypotheses and sequential Bayesian updates could support more transparent inverse-materials research.

**Status — `bhs-scientific-audit` branch (31 October 2026):** This is a research prototype, **not a scientifically validated autonomous materials-discovery system**. The current command-line example is an **illustrative Bayesian demonstration**, not a physical experiment.

## Implemented scope

| Module | What it currently does |
| --- | --- |
| `bhs/search/bayesian_engine.py` | Validates and updates supplied hypothesis probabilities; no actual MCTS rollouts or GPU allocation |
| `bhs/cli.py` | Runs an explicit `--demo` with illustrative likelihoods; saves `NOT_VERIFIED` provenance |
| `bhs/evidence/likelihoods.py` | Computes an **uncalibrated** periodic-overlap score and transforms a supplied SOAP distance; neither is a calibrated likelihood, and SOAP descriptors are not computed |
| `bhs/physics/relaxer.py` | Optional CHGNet adapter; reports predicted potential energy in eV/atom **if run**, not formation energy or energy above hull |
| `bhs/benchmarks/suite_20.py` | Defines a 20-system study protocol with status `NOT_RUN`; **no empirical benchmark results** |
| `bhs/benchmarks/baselines.py` | Random-selection demonstration; no measured speedups |
| `bhs/provenance/bundle.py` | Records inputs, history and hashes, without claiming scientific reproducibility |
| `bhs/reports/generate_artifacts.py` | Exports the unexecuted protocol; performance-table export is disabled |

The `app.py`, `crystal_gen/`, and `legacy/` components are earlier prototype work and are **outside the focused automated test scope**.

## Bayesian formulation

For an input prior and supplied likelihoods:

\[
P(H_i\mid E)=\frac{P(E\mid H_i)P(H_i)}{\sum_j P(E\mid H_j)P(H_j)}.
\]

The update code is mathematically tested. **That does not establish that its input likelihoods are calibrated physical evidence.** Dependence between evidence sources also remains to be evaluated.

## Run the illustrative demo

```bash
git clone https://github.com/busrakisik/inverse-materials-design.git
cd inverse-materials-design
git checkout bhs-scientific-audit
python -m venv .venv
source .venv/bin/activate
python -m pip install pytest PyYAML pymatgen
python -m bhs.cli --demo \
  --config configs/reconstruction_lifepo4.yaml \
  --out-dir runs/demo_001
```

The demo writes `input_config.json`, `execution_history.json` and `provenance_manifest.json`. **No CHGNet calculation, crystal validation, MCTS search, GPU allocation, or material discovery occurs.** The sample YAML's physical constraints and budget are not executed.

## Tests

```bash
python -m pytest -q \
  tests/test_reconstruction_run.py \
  tests/test_ablation_matrix.py \
  tests/test_benchmarks.py \
  tests/test_reports.py \
  tests/test_provenance.py \
  tests/test_evidence.py \
  tests/test_physics.py
```

**83 focused tests passed** on 31 October 2026 ([GitHub Actions run](https://github.com/busrakisik/inverse-materials-design/actions/runs/41194127747)). Evidence tests use real `pymatgen`; physics-adapter tests **mock CHGNet**. Passing tests does **not** demonstrate physical accuracy or experimental search performance.

The top-level `requirements.txt` is not a locked environment and includes platform-dependent legacy packages. The setup above covers only the audited demo and tests.

## Benchmark and research status

The 20 systems are a **planned study**, not experimental outcomes. Obtain a `NOT_RUN` manifest using:

```bash
python -c "from bhs.benchmarks.suite_20 import AblationBenchmarkSuite; print(AblationBenchmarkSuite.save_protocol_manifest())"
```

Next steps: calibrate evidence likelihoods; implement and evaluate actual hypothesis selection/MCTS; test real CHGNet predictions against reference data; benchmark against fair baselines with raw run logs, fixed budgets and repeated seeds; pin dependencies and independently reproduce results.

## Citation

**Büşra Kısık**, *Bayesian Hypothesis Search (BHS)*. Archived v1.0.1: [Zenodo 10.5281/zenodo.21761835](https://doi.org/10.5281/zenodo.21761835). See [`CITATION.cff`](CITATION.cff). License: MIT.

The existing Zenodo archive predates these experimental-branch changes; **the audit branch is not automatically included in that archived release**.

<!-- END OF COMPLETE BHS README — CHECK THIS LINE ON GITHUB -->
