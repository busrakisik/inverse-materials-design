# Bayesian Hypothesis Search (BHS)
### A hypothesis-centered research prototype for computational materials discovery

[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21761835.svg)](https://doi.org/10.5281/zenodo.21761835)
[![Research software](https://img.shields.io/badge/status-research%20prototype-blue)](https://github.com/busrakisik/inverse-materials-design)

**Bayesian Hypothesis Search (BHS)** explores a hypothesis-centered alternative to directly generating crystal structures. The central research idea is to maintain competing structural hypotheses, update their relative plausibility as evidence is evaluated, and prioritize further computation using an adaptive search policy.

**Project status:** Open-source research prototype. The repository contains working ideas and implementation components, but it is **not yet a validated autonomous materials-discovery system**. Benchmark figures currently included in the source are *simulated examples*, not measured evidence of performance gains.

## Research question

Can explicit scientific hypotheses, sequential evidence updates, and search-budget allocation make candidate evaluation more transparent and resource-aware in inverse materials design?

Rather than immediately committing resources to a single generated structure, BHS investigates a process in which a set of candidate hypotheses is evaluated and revised over multiple evidence stages.

## Approach

The intended workflow is:

1. **Initialize hypotheses:** Define candidate structural explanations and prior probabilities.
2. **Evaluate evidence:** Estimate likelihoods using physical and structural criteria.
3. **Update beliefs:** Apply sequential Bayesian updates to hypothesis probabilities.
4. **Allocate search effort:** Use a PUCT-style exploration/exploitation score to prioritize candidates.
5. **Record provenance:** Save the configuration, evidence history, selected hypotheses, and output metadata.

Under an explicitly stated conditional-independence assumption, a sequential update has the form

$$
P(H_i \mid E_{1:k}) \propto P(H_i)\prod_{j=1}^{k} P(E_j\mid H_i).
$$

The validity and calibration of evidence likelihoods remain important research questions.

## Components in the repository

| Component | Description |
| --- | --- |
| `bhs/search/bayesian_engine.py` | Hypothesis probability updates and PUCT-style scoring |
| `bhs/evidence/likelihoods.py` | Structural-clash and novelty-related likelihood functions |
| `bhs/physics/relaxer.py` | Experimental integration point for CHGNet-based relaxation |
| `bhs/provenance/` | Provenance value types and run-output bundles |
| `bhs/cli.py` | Configuration-driven reconstruction demonstration |
| `bhs/benchmarks/suite_20.py` | **Illustrative/simulated** 20-system benchmark scaffold |
| `bhs/reports/generate_artifacts.py` | LaTeX table generation from benchmark JSON |
| `tests/` | Unit and demonstration tests |
| `app.py` and `crystal_gen/` | Earlier interactive inverse-design prototype components; require separate cleanup |

The repository also preserves earlier work on an LLM-assisted inverse materials-design interface. That prototype is related to, but distinct from, the BHS hypothesis-search research direction.

## Getting started (development)

Clone the repository:

```bash
git clone https://github.com/busrakisik/inverse-materials-design.git
cd inverse-materials-design
```

Create a Python virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pyyaml
```

> **Installation note:** The current dependency list is not yet fully locked or verified across platforms. CHGNet integration requires additional setup. These commands are development starting points, not a tested reproducibility guarantee.

A sample CLI entry point is included:

```bash
python -m bhs.cli \
  --config configs/reconstruction_lifepo4.yaml \
  --out-dir runs/example_run
```

The example uses predefined hypotheses and likelihood inputs. Successful completion should **not** be interpreted as discovering or validating a new material.

Tests can be explored individually, for example:

```bash
python -m tests.test_evidence
python -m tests.test_reconstruction_run
```

Test execution and scientific validity are separate questions; full-environment execution has not been independently verified for this release.

## Benchmark status: illustrative, not experimental

The current `bhs/benchmarks/suite_20.py` defines 20 example material systems, but its search-step and compute-budget values are **hard-coded simulations**. They should not be reported as measured speedups, validated GPU-hour reductions, or evidence that BHS outperforms random search or other baselines.

A future empirical benchmark should compute results from actual runs, record the hardware and software environments, use comparable computational budgets, include repeated trials, and report uncertainty and failure cases.

## Scientific limitations and next steps

- **Evidence modeling:** Establish calibrated likelihoods and test their assumptions.
- **Physical validation:** Distinguish actual MLFF calculations from placeholder/fallback values. The current relaxation fallback uses a fixed proxy energy and its provenance labeling needs correction.
- **Search experiments:** Replace simulated benchmark metrics with observed outputs and independent baselines.
- **Reproducibility:** Pin dependencies, validate environment setup, and archive exact experiment configurations and artifacts.
- **Legacy application:** Resolve merge-conflict markers in `app.py` and test the interactive demonstration before presenting it as runnable.
- **Documentation and citation:** Reconcile the author's name and version metadata across GitHub, `CITATION.cff`, and Zenodo.

These are active engineering and research tasks, not completed results.

## Research artifact and citation

- **Source repository:** https://github.com/busrakisik/inverse-materials-design
- **Zenodo archived release (v1.0.1):** https://doi.org/10.5281/zenodo.21761835

For a formal citation, use the authoritative information on the Zenodo record after confirming that the author and release metadata are correct.

## Project contact

Maintained at [@busrakisik](https://github.com/busrakisik). Research discussions, reproducibility feedback, and technical suggestions are welcome.
