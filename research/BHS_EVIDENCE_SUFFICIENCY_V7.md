# Evidence sufficiency and selective scientific decisions — v7

**Development software; no prospective physical validation or demonstrated decision improvement.**

## Research question

Under which observable and independently checkable conditions may a scientific system summarize data, compare observational records, or submit a proposed laboratory action for expert review? What happens when necessary evidence is unavailable or contradicted?

The earlier concrete study used a fixed refusal rule. This implementation introduces *conditional* review decisions and explicit missing-evidence requests. Its behavior has software tests; it is not yet a validated decision policy for laboratories.

## Formal review contract

Three evidence levels are implemented: descriptive reporting, observational comparison, and laboratory review. Each higher level needs more evidence, including batch identity, curing conditions, testing protocol, repeatability, controlled intervention, blocking, independent performance evaluation and external expert approval.

Evidence fields have four states: verified, missing, unknown and contradicted. A verified field needs a reference to a source record. A reference is **not proof** that an external document has been authenticated.

Contradictions cause refusal; missing fields cause an explicit request. Complete descriptive information permits **descriptive reporting only**. Even with complete laboratory records, a preliminary asymmetric loss bound may only result in **eligibility for human review**, never an automatic physical experiment.

The optional worst-case utility test is:

- `minimum_action_utility = probability_lower_bound * benefit - (1-probability_lower_bound) * harm`
- `abstain_utility = -abstention_cost`

The action is not eligible unless the first quantity strictly exceeds the second and the declared risk bound references independent performance evidence. Numerical inputs in unit tests are synthetic; the code cannot establish that reported probabilities are calibrated or costs are real.

## Existing authentic data application

The preserved UCI concrete v6 development record verifies the source accession and parsed numerical fingerprint. It lacks the necessary real-world experimental metadata and independent action outcomes. The resulting levels are:

- Descriptive: `DESCRIPTIVE_REPORT_ONLY`.
- Observational: `REQUEST_ADDITIONAL_EVIDENCE`.
- Laboratory: `REQUEST_ADDITIONAL_EVIDENCE`.

The system does not prescribe any laboratory intervention or assert a causal effect.

## What would falsify a future benefit claim?

Before evaluating a new independently collected laboratory dataset, predefine domain-expert review, error costs, a comparable fixed baseline, independent outcome assessment and the rate of consequentially wrong decisions. Evaluate selection coverage and selective risk together; a system that refuses every action is not automatically useful.

Source: `bhs/decisions/evidence_contract_v7.py`. Tests: `tests/test_evidence_contract_v7.py`. Development CI: `.github/workflows/bhs-evidence-contract-v7.yml`.

Independent holdout not used; physical validation not performed; reserved NIST evaluation seeds untouched.
