# BHS Freeze Readiness v1

**METADATA-ONLY / NOT FROZEN / NO HOLDOUT RUN.**

This stage checks whether mandatory fields have been recorded and hashes match the checked-out revision. **It never grants approval**, even when all fields are asserted true: an independent reviewer must inspect actual historical seed inventories, public/hidden label interface, protocol and code against the frozen revision. Self-declarations do not constitute independent evidence.

## What the automated gate checks

* Proposed seed set 10000–10099 and SHA256; it verifies disjointness only against documented default pilot seeds 0–29, not unpublished experiments.
* SHA256 for generator, baseline/evaluator, Bayesian-only model, paired runner, preparation/audit scripts and protocol documents.
* Fields for pilot-informed primary scenario, current Gaussian policy hyperparameters, dependency lock and bootstrap RNG seed.
* Declarations of reviewed historical-seed inventory and label-boundary audit, with source and seed hash equality.
* Always returns `scored_validation_allowed: false`. Does **not** generate tasks, hidden values or scores.

## Critical constraints

The proposed validation seeds have not been certified as untouched by every prior development run. Avoid running `make_task` on these seeds before freeze approval. `MeteredEvaluator` is same-process; this is not malicious worker isolation. Environment lock must cover versioned dependencies and platform if relevant.

To advance, commit actual seed inventory, reproduce exact SHA256 and locked environment, arrange independent inspection, and then implement a **separate, explicitly reviewed** approval procedure. Do not flip this gate to true by editing a JSON flag.
