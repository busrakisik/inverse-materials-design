# BHS v6 — Evidence sufficiency and justified abstention

**6 November 2026 — exploratory real-measurement audit, not independent validation or physical discovery.**

## Research question

When considering a laboratory recommendation about 28-day concrete compressive strength and the water-to-binder ratio, **which indispensable assumptions are actually supported by the source data, and what decision follows when they are not?**

The physically motivated expectation that increasing water relative to binder often reduces compressive strength requires comparable source materials, specimen preparation and curing/testing conditions. The UCI table does not establish these conditions. Our quantity `water/(cement + blast-furnace slag + fly ash)` is a *proxy*, not proof that each binder constituent has identical physical behavior. Thus this study measures **observational data support and failure conditions**, not a causal effect or a valid recipe recommendation.

## Source and exact experimental boundary

- Yeh, *Concrete Compressive Strength*, UCI dataset 165, DOI [10.24432/C5PK67](https://doi.org/10.24432/C5PK67), **CC BY 4.0**.
- Exactly **1,030** source observations, **425** at 28-day curing age, **416** distinct reported input profiles.
- Parsed numerical source SHA-256 **98958f558e46763cf6d5403de8784af39ebe906c4604447c188889c3e346cd87**, inherited from the reproducible v5 accession. This is **not** the hash of the original spreadsheet.
- The pairing procedure considers only *input descriptors*; it cannot see compressive-strength responses during matching. Response values are used **after** deterministic pairing for purely descriptive scoring.
- We required at least **10 kg/m³** water difference and **0.03** water-to-binder proxy difference. The six other mixture constituents must be within the stated per-variable absolute tolerance. Pair selection is disjoint within each tolerance and does not use labels.

## Real-data result

| Maximum difference permitted in each other ingredient | Eligible input-matched pairs | Disjoint comparisons | Pairs with inverse water/strength direction | Opposite direction |
| --- | ---: | ---: | ---: | ---: |
| **±5 kg/m³** | 1 | 1 | 1 | 0 |
| **±15 kg/m³** | 21 | 11 | 10 | 1 |
| **±30 kg/m³** | 140 | 52 | 46 | 6 |

The comparison count is highly sensitive to permitted differences in *other* concrete ingredients. Relaxing the rule produces more comparisons while reducing compositional comparability. Pairs across different tolerance levels overlap; percentages are descriptive and **not independent confidence evidence**. The larger-tolerance direction agreement **does not establish causality**, instrument calibration or extrapolation safety.

**Identical-input repeat audit:** Five source groups shared exactly the same recorded eight inputs, accounting for **nine additional rows**. Two groups showed more than **1 MPa** difference in reported compressive strength; the largest within-group range was **12.61 MPa**. The 1-MPa flag is an audit heuristic, **not** a validated repeatability standard. Differences cannot be ascribed to a particular cause without source/laboratory metadata.

## BHS conclusion — no laboratory recommendation

`DECISION: ABSTAIN_FROM_PHYSICAL_OR_LAB_RECOMMENDATION`

The outcome was mandated by the protocol before inspecting these results. Reasons:

1. **Material/curing context unverified:** material identity/lot, curing humidity and temperature, specimen geometry and compression-test procedures are not established by the public table.
2. **Observational comparisons are not interventions:** comparisons cannot isolate the effect of changing the water-to-binder ratio while holding all other physical conditions constant.
3. **Measurement uncertainty is unknown:** the repeated-profile discrepancies warn against treating reported strengths or predictor intervals as laboratory-calibrated probabilities.
4. **Matching sensitivity:** stricter criteria have too few comparable mixtures for a stable descriptive interpretation, while loose matching leaves substantial scope for confounding.
5. **Proxy limitations:** slag and fly ash do not necessarily contribute to hydration and strength equivalently to cement.

The system **did not** recommend a new concrete recipe, suggest a water adjustment or claim to identify the concrete strength mechanism.

## Engineering contribution

This is a reproducible **scientific assumption contract**: specify necessary evidence, validate observed fields, test comparable measurements *without label selection*, inspect contradictions in repeated observations, and issue an auditable abstention decision when critical assumptions are unavailable. Failure cases (mislabelled columns, source drift, invalid material quantities, missing 28-day support and unexpected matching thresholds) are covered by **seven contract tests**.

For a real laboratory evaluation, the next required collaboration is a **controlled, documented paired water intervention** with recorded ingredient material lots, unchanged other inputs, consistent curing and test conditions, calibrated replicates, variance and feasibility constraints. Only then may the system test a physically interpretable prediction; the actual decision policy would require independent evaluation and a defined acceptance/abstention risk rule.

## Reproducibility and scope

- [v6 method and prior fixed assumptions](CONCRETE_ASSUMPTION_AUDIT_V6.md)
- [Implementation](../scripts/uci_concrete_assumptions_v6.py) and [contract tests](../tests/test_uci_concrete_assumptions_v6.py)
- [Original real-data GitHub Actions run](https://github.com/busrakisik/inverse-materials-design/actions/runs/42229114121) (**success; 7/7 synthetic contracts**, real UCI audit run).
- [Preserved aggregate-only JSON](uci_concrete_assumptions_v6.json). Original workflow artifact ID: **13506539723**, original JSON SHA-256: `3a5486a1b081ec863c9224cbc730509def27b68bb03e9c5b0a2bb3f149f7ecc5`, ZIP SHA-256 `6da5502df9ac6e5f61166085ad21ac65d108ef3cb6685f662f2bd43736e2b166`.

No independent holdout or physical lab intervention occurred. `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation=false`; no scientific method superiority claim or use of reserved NIST seeds `10000..10099`.
