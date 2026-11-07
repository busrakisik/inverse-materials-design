# BHS v12.1 — Order representation contract

**Prepared 7 November 2026. Status: source-independent software verification; no outcome-scored replay.**

## Question and falsifiable contract

Does the decision rule return the same action for two acquired evidence maps containing precisely the same per-design measured response multisets, when insertion order and within-design tuple order differ? Identical candidate features, seed, step and policy must lead to identical (design ID, next ordinal). A mismatch is a software reproducibility failure, not an opportunity to retune a model.

The reference V12.0 first historical replay failed a predeclared V11 RF parity check. That failure, the full first-run artifact and the following source-order diagnostic are permanently retained in the separate replay branch. This v12.1 adapter does not retroactively correct or reinterpret the earlier experiment.

## Scope

- Canonicalize only already revealed finite responses; sort full and partial response tuples, then sort observed geometry keys.
- Forward the unchanged four V12.0 policy functions, numerical settings, seed, step, source descriptors, and 48-response budget.
- Reject malformed acquired evidence through the existing validation contract; protected seeds 10000..10099 remain rejected.
- Test response-map insertion permutations and per-design observed-value permutations on deliberately fabricated synthetic examples.
- Do **not** load the pinned historical source, execute source-scored evaluation, publish raw measurements, infer measurement chronology, or assert improvement in physical decisions.

## Critical distinction

**Representation invariance is not temporal invariance.** A response multiset (a design with fully observed triplicate measurements) is unordered for a mean-based surrogate. But a partial design may have different values available after the first observation in two hypothetical measurement sequences. Different intermediate actions in those genuinely different evidence states are permissible and do not violate this contract. The archived source lacks confirmed experiment timestamps, so no chronological model is identifiable from its row order.

Sorting a complete triplicate before floating-point fitting gives deterministic numerical presentation to the existing surrogate; it does not calibrate noise, resolve source batch effects, or make an empirical estimate equivalent to physical truth. Any comparison of changed acquisition trajectories is a **new development evaluation**, never independent confirmation.

## Required software gates

1. For all four policies and each previously explored development seed tested, permuting only observed-map representation must preserve exact next action.
2. The original source code and V12.0 negative/invalid findings remain unchanged.
3. Malformed or nonfinite observed values are rejected, with no unseen outcomes in the selection interface.
4. Rejected protected seeds and the fixed budget are retained.
5. Push verification must run only source-independent tests. No historical replay in this branch.

## Later separate study (not authorized by this protocol)

A new, expressly registered development experiment should use multiple deterministic replicate-order permutations, matched selection budgets, exact source hashes, and an adaptive-repetition GP reference. Freeze the permutation grid and statistical summary *before* observing those outcomes. Report complete-design regret, uncompleted-design fraction, order sensitivity, and abstention at equal decision coverage. Prior visits to the same archive prevent treating additional permutations as independent evidence. A new physical source with actual observation time, batch, apparatus and cost fields is required before general claims.

Research context: Binois, Huang, Gramacy and Ludkovski, *Replication or Exploration? Sequential Design for Stochastic Simulation Experiments*, Technometrics 61 (2019), DOI 10.1080/00401706.2018.1469433. Binois and Gramacy, *hetGP*, Journal of Statistical Software 98 (2021), DOI 10.18637/jss.v098.i13. These are prior methods, not validations of BHS.

## Evidence boundary

`development_only=true`  
`scored_validation_allowed=false`  
`independent_holdout_used=false`  
`physical_validation_by_bhs=false`  
`causal_identification=false`  
`calibrated_uncertainty_proven=false`  
`claim_of_superiority=false`  
`real_savings_measured=false`  
`reserved_nist_seeds_used=false`

Keep the original V11 negative results, V12 first-run parity failure, DOI lineage and evidence archive unchanged.
