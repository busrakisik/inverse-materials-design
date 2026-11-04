# BHS Observation-Conditioned Belief Search v1

**Status: exploratory algorithm demonstration only; no holdout, no material discovery claim.**

## Important mathematical distinction

This policy simulates a shared latent scalar Gaussian slope, draws noisy hypothetical
outcomes, and **updates the Gaussian posterior after each simulated observation**.
The search tree alternates **candidate actions** with **three standardized predictive
innovation bins (-1, 0, +1)**. Reused branches may choose different subsequent
candidate actions, so planning is observation-contingent in an approximate sense.

- Posterior update: `v' = (1/v + x²/σ²)^(-1)`, `m' = v'(m/v + xy/σ²)`.
- Root latent sampled from current posterior, retained during each trajectory.
- Simulated outcome `y = w*x + ε`, `ε ~ N(0, σ²)`.
- Tree selection uses UCT across actions; outcome nodes are coarse bins.
- Rollout uses a transparent expected-positive-improvement heuristic.
- Simulation utility = maximal **simulated** observed outcome improvement over
  baseline (zero if none observed), **not** a real performance improvement.

### Limitations and methodological risks

1. **This is NOT a validated BAMCP/POMCP or exact belief-state MCTS implementation.**
   The tree merges quantitatively different posterior states under the same
   observation bin. It is a finite-bin, observation-conditioned experimental tree.
2. Current synthetic model is a **single latent slope**. Some benchmark scenarios
   violate its assumptions and the synthetic evaluator does not inject the same
   observation noise assumed by the model.
3. The planning horizon is **not budget aware**; a five-query task still plans at
   most the configured three-step horizon.
4. No real physical evaluator, real materials labels, independent statistical
   validation, secure OS sandbox, or adversarial isolation is established.
5. This code does not automatically integrate into the existing policy worker;
   only a trusted, in-process development demo is implemented.
6. Simple tree search plus Bayesian uncertainty is **not a novel technique per se**.
   A publishable BHS research contribution must be established relative to
   existing Bayes-adaptive planning and nonmyopic BO literature.

## Literature context (not novelty claims)

- Guez et al. *Bayes-Adaptive Monte-Carlo Planning*. JAIR (2013).
  https://www.gatsby.ucl.ac.uk/~dayan/papers/guez_jair2013.pdf
- Mern et al. *Bayesian Optimized Monte Carlo Planning*. AAAI (2021).
  https://doi.org/10.1609/aaai.v35i13.17411
- Yue & Al Kontar. *Why Non-myopic Bayesian Optimization is Promising and How
  Far Should We Look-ahead?* AISTATS (2020).
  https://proceedings.mlr.press/v108/yue20b.html
- Ross et al. *A Bayesian Approach for Learning and Planning in POMDPs*.
  JMLR (2011). https://www.jmlr.org/papers/v12/ross11a.html

## Safe verification

```bash
python -m unittest discover -s tests -p 'test_belief_state_search_v1.py' -v
python -m scripts.belief_state_search_v1
```

Both test and CLI restrict the evaluator demo to **previously used development
scenario `smooth`, seed `7`, five queries**. There is **no** workflow that runs
independent seeds 10000..10099. `scored_validation_allowed = false`.

## Next scientific gate

Before integrating into a publishable experiment: (a) run unit and CI tests,
(b) test innovation-bin calibration and posterior consistency, (c) establish
budget-aware planning, (d) compare against Bayesian-only / Greedy under a matched
computational budget on prior development tasks, (e) independently review the
validation protocol and only then decide on separately frozen confirmatory tasks.
