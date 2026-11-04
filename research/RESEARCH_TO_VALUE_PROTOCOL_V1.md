# BHS Research-to-Value — Paired Development Protocol v1

**Status: Exploratory, post-selection, synthetic; NOT independent validation or evidence of performance superiority.**

## Research question

Under a fixed *spent-cost cap* (8 arbitrary synthetic units), how do (a) random selection,
(b) cheapest-first, (c) one-step expected information gain (EIG), and
(d) one-step EIG per cost compare on **model identification** (negative log
posterior probability of the known synthetic generating family)?

Crucially, this question is NOT "Which discovers the best material?" and not
"Does BHS outperform Bayesian optimization?" No real physical data are used.

## Comparison grid — explicitly development-only

- 3 fixed true functional families: linear, quadratic, oscillatory;
- 2 fixed cost profiles: uniform 1 or heterogeneous 1/3 units;
- 2 known synthetic noise profiles: 0.12 or 0.24 base standard deviation,
  multiplied by 1.2 on alternating candidate indices;
- 2 developer-known deterministic repetitions (IDs 0 and 1);
- 4 policies per case; 24 paired cases, 96 campaign records, 72 comparisons to EIG.
- 13 public scalar candidate descriptors per case; all policies share the same
  candidate-specific synthetic measurements regardless of acquisition order.
- All policies have the same spending cap, 8 synthetic units; unused funds and
  number of measurements are reported (not silently equated).
- A trusted local test simulator generates all outcomes but discloses only
  the chosen measurement after selection. A hypothesis policy cannot access
  unselected outcomes.

Outcome: **true-family log loss** `-log p(H_true | observed data)`, spent cost,
number of measurements, and descriptive posterior entropy. Lower log loss is
better for the *specified model-identification task*, but it does not measure
real-world scientific fitness.

## Critical limitations

1. All the functional families are present in the learner's assumed set;
   no misspecification stress tests or calibrated detection are performed here.
2. Measurement noise is assumed known. Synthetic metadata provenance is an
   explicit development-only convention, NOT real laboratory calibration.
3. EIG/cost is a heuristic. The optimum over whole experiment sequences is not
   computed. Random and cheapest-first are weak baselines; strong literature
   baselines and expert review remain mandatory.
4. The sample grid, model family, acquisition rules, quadrature resolution, and
   costs were designed with access to earlier development results. **No**
   statistical significance tests, p-values, or confirmatory confidence claims.
5. Comparison to prior max-utility/simple-regret BHS results is **invalid**:
   model identification is a different optimization objective.
6. The fixed repetition IDs 0 and 1 are NOT hidden benchmark task seeds. The
   independent holdout range 10000..10099 is neither touched nor generated.
7. In-process policies are trusted code, not protected by OS-level sandboxing.
8. No customer contract, instrument integration, verified monetary savings,
   patent, standalone proprietary novelty, or commercial fit is established.
9. `scored_validation_allowed` remains `false` in all reports.

## Publication-facing decision gates (not yet passed)

- Freeze an **out-of-family** challenge specification, calibration targets,
  and action-cost semantics before future independent evaluation.
- Independently rederive conjugate marginal evidence and EIG quadrature;
  measure approximation and run-time error against other implementations.
- Add appropriate BO, uncertainty-aware and resource-constrained baselines;
  evaluate under matched protocols and objective functions.
- Adopt *real* publicly licensed offline lab data/realistic candidate/measurement
  contracts; use a permission-safe sealed label provider.
- Ask domain experts to validate candidate descriptors, real measurement
  uncertainty, cost/time units, and whether a selected experiment is executable.
- Only consider a frozen independent evaluation after external methodological
  review. No benchmark holdout opened as part of this artifact.

## Related current research

- MADE: Benchmark Environments for Closed-Loop Materials Discovery (ICML 2026):
  https://proceedings.mlr.press/v306/malik26a.html
- Cost-Aware Recovery-Pathway Identification and Bayesian Optimization for
  Autonomous Materials Discovery (July 2026 preprint): https://arxiv.org/abs/2607.23896
- Cost-informed Bayesian reaction optimization (Digital Discovery, 2024):
  https://pubs.rsc.org/en/content/articlehtml/2024/dd/d4dd00225c
- Benchmarking Active Learning Strategies for Materials Optimization and Discovery
  (NIST, 2022): https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery

## Commands

```bash
python -m unittest discover -s tests -p 'test_bhs_research_to_value_v1.py' -v
python -m scripts.bhs_research_to_value_v1
```

`runs/bhs_research_to_value_v1/development_comparison.json` includes rows,
paired comparisons, and a manifest. It is explicitly exploratory.
