# BHS — Reliability-Gated Cost-Aware Experimental Design v1

**Development-only interface prototype. Not certified reliability-aware optimization, physical validation, or a newly proven algorithm.**

## Actual design

- Keep the existing three-model Bayesian hypothesis posterior and EIG from `competing_hypotheses_v2` unchanged.
- A candidate must have a positive **declared observation standard deviation**, positive experiment cost, and explicit synthetic-provenance marker. Missing/unapproved metadata **raises an error** rather than being assigned an invented reliability score.
- For eligible experiments choose maximum `EIG / declared_cost`. Candidate IDs break exact ties. A pure EIG variant is available **only as a same-history descriptive comparator**.
- Observed data must carry the candidate ID, observation, standard deviation and provenance matching the declared protocol. The v2 posterior update uses these observation-specific standard deviations.
- Retrospective metrics use v1 **prequential** diagnostics; they are descriptive only. The current implementation does NOT convert empirical coverage into a binary trust gate or derive calibrated reliability weights.
- Demo uses one fixed 13-candidate synthetic quadratic scenario, five sequential actions, fixed Python RNG seed 41. The demo's generator reveals outcomes only AFTER selecting a candidate.
- Explicit EIG/cost is an **efficiency heuristic**; it is not a proven solution to finite-budget Bayesian experimental design. Costs have unspecified units in the demo.

## Scientific restrictions

1. A provenance **string cannot verify the authenticity of instrument calibration**. The `instrument_calibrated_synthetic` label denotes a controlled *illustrative convention*, not a device-certified guarantee.
2. The declared `measurement_std` is assumed accurately calibrated. Real misreported/noisy/bias-corrupted evidence is not made safe by supplying metadata.
3. The diagnostic audit is retrospective, not used to censor today's predictions. No detection threshold or false-positive rate is validated.
4. The model remains scalar, Gaussian, independent-noise, and assumes the true mechanism is among three families. It is vulnerable to misspecification, unknown biases and correlation.
5. EIG/cost and pure EIG optimize **model information**, NOT simple regret or material utility. They must not be compared on incompatible outcome metrics as claims of superiority.
6. No real materials, experiment orchestration, physical discovery, holdout seeds 10000..10099, or independent scientific validation.
7. CI tests software behavior and accounting, not correctness of declared standard deviations, scientific improvement, or external replicability.
8. All outputs keep `scored_validation_allowed = false`.

## Verification

```bash
python -m unittest discover -s tests -p 'test_reliability_gated_design_v1.py' -v
python -m scripts.reliability_gated_design_v1
```

Expected 22 tests and a deterministic five-action report with SHA-256 at `runs/reliability_gated_design_v1/`.

## Next research actions

- Evaluate EIG/cost against *precommitted* pure-EIG and cost-blind reference policies with matched development tasks and comparable budgets; report both model identification and total costs.
- Cross-check information gain numerics with independent quadrature / Monte Carlo implementations.
- Establish authentic instrument provenance and external calibration evidence before deploying the provenance gate beyond synthetic illustrations.
- Assess bad uncertainty estimates and systematic bias without false certification claims; design a prior-to-evaluation, independently reviewed protocol before any holdout.
