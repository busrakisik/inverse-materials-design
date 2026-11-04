# BHS — Competing Fixed Scientific Hypotheses v1

**Experimental mathematical reference implementation. NOT validated materials discovery. NO independent holdout.**

## Mathematical problem

Three deliberately *fixed* synthetic response hypotheses for scalar descriptor x ∈ [-1,1]:

- H1: f1(x) = x
- H2: f2(x) = x²
- H3: f3(x) = sin(3x)

Observation likelihood under model i is Normal(f_i(x), σ²), with known σ=0.15 and equal model priors. These are *illustrative mechanisms* — no fit parameters, no physical interpretation, and no claim of model completeness.

Given observations D={(x_j,y_j)}, posterior model probability is
p(H_i | D) ∝ p(H_i) ∏_j Normal(y_j | f_i(x_j), σ²).
Implementation accumulates log likelihoods and uses log-sum-exp normalization.

Experiment x maximizes approximate expected information gain (EIG):
I(H;Y | x,D) = H[p(H|D)] - E_{Y|x,D} H[p(H|D,x,Y)].
The expectation is approximated by **64 deterministic midpoint quantiles per model** under each predictive Gaussian, weighted by current model probabilities. This is *one-step* EIG, not full belief-tree planning, and midpoint quadrature has numerical error. Candidate ties use stable ID order.

## Strict limitations

1. Fixed mechanisms and known Gaussian noise; parameter uncertainty, scientific semantics, evidence quality and experiment cost are not modeled.
2. One-step information gain is an established Bayesian experimental design technique, not novel by itself.
3. No claim that this policy exceeds random, greedy, Bayesian-only, open-loop PUCT or belief-state search. Comparative evaluation requires a specified development protocol followed by independent review.
4. This code accepts only public scalar descriptors and previous observations. There is no real materials evaluator or physical discovery.
5. Running this code does not evaluate benchmark tasks, let alone holdout tasks 10000..10099.
6. CI passing is software consistency only, not publication-quality validation.
7. `scored_validation_allowed = false` always.

## Development-only demonstration

`python -m unittest discover -s tests -p 'test_competing_hypotheses_v1.py' -v`

`python -m scripts.competing_hypotheses_v1`

This fixed demo uses 13 prespecified public candidate descriptors, generates five synthetic observations from the designated quadratic mechanism, and reports posterior model probabilities. `make_task` is NOT invoked.

## Scientific next steps

- Exact small-case quadrature and model-discrimination sanity checks; posterior predictive calibration under misspecification.
- Compare one-step EIG against simple alternatives and an observation-conditioned planner on *previously seen development tasks only* with a new consistent objective: model identification rather than max response. Do not reinterpret earlier simple-regret results as model-discrimination evidence.
- Build multi-parameter, evidence-reliability-aware scientific models with explicit provenance and realistic experiment costs.
- Only after independent scientific review, frozen code/data/protocol, and strong baseline results consider confirmatory validation with non-overlapping tasks.

## Related established methods

- Optimal Bayesian design for model discrimination via classification, *Statistics and Computing*, 2022: https://pmc.ncbi.nlm.nih.gov/articles/PMC8924111/
- Bayesian active learning with model selection for spectral experiments, *Scientific Reports*, 2024: https://www.nature.com/articles/s41598-024-54329-w
