# BHS v9 — When identical observations imply opposite scientific actions

**Research status:** Exact, synthetic *constructive counterexample* to causal identifiability. The mathematical phenomenon is established causal-inference theory; this is a reproducible BHS decision-contract demonstration, **not** the discovery of a new theorem, physical mechanism, improved material, independent evaluation or practical benefit.

## Research question

A laboratory may have accurate, abundant, perfectly consistent observations but still lack the assumptions needed to infer how an intervention would affect an outcome. Could BHS incorrectly interpret signed evidence and high apparent model confidence as permission for a causal laboratory recommendation?

The new test constructs **two explicit structural causal models** that induce *exactly the same observable probability distribution*, but disagree on the **sign of the causal intervention effect**. Hence no rule using that observational law alone can tell which intervention is beneficial. This directly tests the boundary of the preceding v7/v8 evidence and integrity controls.

## Mathematical example (100% invented outcomes)

Let unrecorded context `U` take values 0 and 1, each with probability 1/2. Observed treatment/action `A = U` and observed outcome `Y = 30` in both contexts. The outcome is in **arbitrary response units**, not measured concrete MPa; the numbers 30 and 40 are purely algebraic.

Two possible worlds are consistent with these same records:

| Latent context `U` | Observed action `A` | Observed response `Y` | Positive-effect world: `Y(0), Y(1)` | Negative-effect world: `Y(0), Y(1)` |
| --- | ---: | ---: | --- | --- |
| 0 | 0 | 30 | (30, 40) | (30, 30) |
| 1 | 1 | 30 | (30, 30) | (40, 30) |

Thus the entire observable distribution in both worlds is:

`P(A=0,Y=30)=1/2`, `P(A=1,Y=30)=1/2`, and all other observable probabilities are zero.

But under interventions:

- **Positive world:** `E[Y | do(A=0)]=30`, `E[Y | do(A=1)]=35`; average effect **+5**.
- **Negative world:** `E[Y | do(A=0)]=35`, `E[Y | do(A=1)]=30`; average effect **−5**.

This is a failure of identifiability. In each latent context, only one action is observed, so `P(A=a | U=u)>0` is violated for the unobserved alternative. Because `U` is not measured, exchangeability cannot simply be asserted either. The two worlds agree on everything the observer can see yet support **opposing actions** if higher response is preferred.

For orientation, see Hernán and Robins, [*Causal Inference: What If*, Chapter 3](https://miguelhernan.org/whatifbook) for exchangeability, positivity and consistency. This repository's two-world construction is an **illustrative instance of known causal-identification limits**, not an original theorem.

## Consequence for decisions (illustrative assumptions only)

Assume greater response is preferred, wrong-action regret equals the difference from the best action in that world, and not acting incurs a **hypothetical loss of 1 response-equivalent unit**. Within exactly these two predeclared worlds:

| Decision policy | Worst-case illustrative regret |
| --- | ---: |
| Always choose A=0 | 5 |
| Always choose A=1 | 5 |
| Best randomized action, 50% for each | 2.5 |
| Abstain (assumed cost = 1) | **1** |

The abstention comparison is **conditional to this two-world set and assumed cost**. If abstention costs 3 units, it is *not* minimax-preferred over the 50/50 policy with worst regret 2.5. Therefore, BHS must **never** advertise universal advantages for abstention or assume laboratory harm weights without data.

## Implemented falsification

`bhs/decisions/causal_nonidentifiability_v9.py` performs an exact rational-arithmetic audit of finite-world models. It checks latent probability normalization, observational equivalence, counterfactual response differences, opposing signs, deterministic and randomized minimax regret and the cost of abstention.

`guarded_causal_review` conservatively wraps v8: if v8 has missing evidence or contradicting source assumptions, its previous refusal is preserved. If v8 finds an apparently complete, synthetically signed review eligible but the declared worlds show opposing causal effects, **v9 returns `ABSTAIN_CAUSAL_NONIDENTIFIABILITY`**. If no worlds are supplied, or all supplied worlds agree, it still requests causal-identification evidence rather than asserting that unlisted worlds are impossible.

**Important:** An arbitrary user-supplied witness family cannot establish that the family includes *all physically possible models*. Even a perfectly cryptographically signed packet proves no physical identification or probability calibration. Identifying assumptions require expert justification or controlled interventions.

## Reproducibility

```bash
python -m pip install cryptography==46.0.4
python -m unittest discover -s tests -p 'test_causal_nonidentifiability_v9.py' -v
python -m bhs.decisions.causal_nonidentifiability_v9 --out runs/bhs_v9_nonidentifiability.json
```

All source examples and adversarial keys are generated for software testing; no UCI source data are fetched. CI is at `.github/workflows/bhs-causal-identifiability-v9.yml`. The aggregated **synthetic proof** is an artifact; it must never be described as new empirical evidence.

## How this informs the actual BHS research program

Our concrete v6 dataset had no verified source lot, curing, intervention or repeatability metadata. v7 and v8 correctly reject an automatic laboratory action under that incomplete evidence. v9 shows, more fundamentally, why *even perfectly accurate observational associations plus signed metadata* are insufficient to establish the direction of an intervention.

A scientifically meaningful next external stage requires a precisely specified intervention, laboratory material and batch metadata, feasible comparison/support conditions, expert-reviewed identification strategy, independent outcomes, and predeclared risk–coverage comparisons. For the exact pair above, a genuine experiment assigning both actions within each relevant context would break the observational ambiguity; the current BHS project **has not** run that experiment.

**Hard gates remain:** `independent_holdout_used=false`; `scored_validation_allowed=false`; `physical_validation=false`; `claim_of_superiority=false`; reserved NIST independent seeds `10000..10099` never used. Scientific and commercial utility **remain unproven**.
