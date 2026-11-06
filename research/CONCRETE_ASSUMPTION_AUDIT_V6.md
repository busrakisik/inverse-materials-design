# BHS v6 — When should a laboratory decision be withheld?

**Study designation:** Predeclared exploratory *assumption audit*, not a new predictive-model contest, causal discovery, or independently held-out experiment.

## Physically meaningful research question

> Does the available evidence justify recommending that a real laboratory alter a concrete mixture's water-to-binder ratio to achieve a stronger **28-day compressive strength**?

The conventional water-to-cement ratio relationship is scientifically grounded **under specified comparable materials and curing conditions**. Modern binders may incorporate slag and fly ash, whose reactivity makes `water / (cement + slag + fly ash)` only a declared **proxy**, not a universally valid mechanistic law.

Prior literature:
- Yeh, I. (1998), *Concrete Compressive Strength*, UCI accession 165, DOI [10.24432/C5PK67](https://doi.org/10.24432/C5PK67), source licensed CC BY 4.0.
- *Abrams law, air and high water-to-cement ratios* (1996), [DOI 10.1016/0950-0618(95)00079-8](https://doi.org/10.1016/0950-0618(95)00079-8). Validity of simplified ratio laws varies with unmeasured air content and different ratio regimes.
- Popovics and Ujhelyi (2008), *Contribution to the Concrete Strength versus Water-Cement Ratio Relationship*, [DOI 10.1061/(ASCE)0899-1561(2008)20:7(459)](https://doi.org/10.1061/(ASCE)0899-1561(2008)20:7(459)). Physical assumptions and limits of the strength–water/cement relationship.

This **does not** assert the UCI observations identify a causal mechanism. The immediate falsifiable *data-support question* is narrower: Are there sufficiently comparable 28-day mixtures with different water amounts in this historic table to even evaluate an inverse *descriptive* trend without assuming all mixing conditions equal?

## Required assumption contract

| Assumption | Evidence available in UCI? | Failure behavior |
| --- | --- | --- |
| Known eight input columns and units | Described by UCI; enforce feature order, nonnegative constituents, positive age | Stop on unexpected schema or invalid units |
| Fixed 28-day specimens | Numeric age recorded; select exactly age 28 | Stop if no valid 28-day rows |
| Positive cementitious binder and cement | Numeric composition recorded | Stop when denominator invalid |
| Original numerical source unchanged | Pin parsed numerical-table SHA-256 from independently recorded v5 development | Stop if source fingerprint changes |
| Comparable other six ingredients | Screen exact measured amounts at **5, 15, 30 kg/m³** tolerances | Count pair support and sensitivity; **never** assume matching proves exchangeability |
| Observable water difference | Require at least **10 kg/m³** water and **0.03** ratio difference | Exclude insufficient contrasts |
| Measured repeatability | Not established; report response spread of exact-feature repeats, flag spans over **1 MPa** as *heuristic* | Warn; no calibrated error interval |
| Same material lots, curing humidity/temperature, specimen and test protocol | **Not established** by the nine-column UCI table | **ABSTAIN FROM PHYSICAL/LAB RECOMMENDATION** |
| Randomized intervention / independent physical replication | **Unavailable** | **ABSTAIN from causal attribution** |

**Stopping/abstention decision is fixed before the run:** Even if descriptive pairs appear directionally consistent with water-ratio expectations, the system must return `ABSTAIN_FROM_PHYSICAL_OR_LAB_RECOMMENDATION` because critical physical context is unobserved. Failure reasons, missing measurement metadata, repeat conflicts and sensitivity to matching tolerance must accompany the decision.

## Experimental protocol

1. Retrieve only UCI 165 via existing `scripts/uci_concrete_v5.py` source path. Require exactly **1030** observations, original eight feature identities, no negative ingredient quantities, and parsed SHA-256 `98958f558e46763cf6d5403de8784af39ebe906c4604447c188889c3e346cd87`. This fingerprint is *not* the source `.xls` checksum.
2. Select 28-day rows and retain one row per identical eight-feature vector **without consulting target values for selection**. Examine exact-feature repeats in the source separately to identify whether identical reported ingredients can have discordant response measurements.
3. Define the ratio `water / (cement + blast furnace slag + fly ash)`. Positive binder required. **This is an operational proxy**; equal contribution of these three ingredients to strength is not assumed or established.
4. Enumerate pairs of candidate mixtures with all six nonwater ingredient amounts within each *predeclared* tolerance `5, 15, 30 kg/m³`, with water amount difference at least `10 kg/m³` and ratio difference at least `0.03`. Select **disjoint pairs using inputs only** and deterministic stable tie-breaking; do not use strength values when choosing pairs.
5. Only after matching, count how often the higher water/binder proxy co-occurs with lower observed strength versus the opposite, plus ties. Report eligible pair counts, disjoint-pair counts and descriptive direction agreement at each tolerance. The threshold of **20 disjoint pairs** is a heuristic descriptive-support indicator, **not** a power calculation or permission for causal claims.
6. Always log the unverified assumptions and explicit `ABSTAIN` decision. Save **aggregate counts only**, never individual compositions or original response values. Keep dataset attribution intact.
7. Synthetic tests must demonstrate failure on missing/mislabelled columns, invalid materials/age, data drift and forbidden tolerance; and label-isolated pair construction, conflicting replicate flagging and **fail-closed** decision behavior.

## Why this is a useful negative or positive outcome

If few comparable mixtures exist, BHS should report **insufficient support**, not invent a mechanistic conclusion. If there are many pairs but the sign differs with matching tolerance, it should report **confounding sensitivity**. Even if signs agree, lack of curing/batch/measurement context means *descriptive association*, not a valid causal laboratory recommendation.

This case defines an actionable specification for the next lab collaboration: preserve material batch identity, curing/test conditions, replicate variance and **controlled** water interventions before committing to an optimization recommendation.

## Reproduction

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2 pandas==2.2.3 ucimlrepo==0.0.7
python -m unittest discover -s tests -p 'test_uci_concrete_assumptions_v6.py' -v
python -m scripts.uci_concrete_assumptions_v6  # prints protocol only, NO download
python -m scripts.uci_concrete_assumptions_v6 --execute --out runs/uci_concrete_assumptions_v6.json
```

Research gates are unchanged: `development_only=true`, `independent_holdout_used=false`, `scored_validation_allowed=false`, `physical_validation=false`, no hypothesis-discrimination superiority claim, and no use of reserved seeds `10000..10099`. This protocol uses a previously examined UCI development dataset and **cannot** be represented as independent validation.
