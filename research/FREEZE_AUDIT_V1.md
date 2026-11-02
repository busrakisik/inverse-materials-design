# BHS Validation Freeze Audit v1

**AUDIT_ONLY / NOT_FROZEN / NO_HOLDOUT_EXECUTION / SYNTHETIC_ONLY**

Checks SHA-256 of six known repository sources, verifies Git commit identity, and statically checks the pilot's documented default `range(30)` against proposed holdout `10000..10099`. Produces a manifest with `scored_validation_allowed: false`. Does **not** generate candidate utilities, access proposed seed labels, execute benchmark policies, approve the freeze, or claim all historical experiments were searched. A developer may have run additional seeds through manual CLI invocations. Audit the full Git history, notebooks, external artifacts, and local runs separately. Do not automatically approve on green CI.

The `smooth` primary scenario is a **pilot-informed proposal**, NOT an approved preregistration. Prior publication of test results means it cannot be retrospectively called blinded. Keep every other scenario exploratory and use untouched validation seeds only after independent review of previous seed exposure. The same-process evaluator remains suitable for *trusted synthetic policy code only*, and should not be used to claim a secure held-out label boundary.

After CI: inspect `bhs-freeze-audit-v1` artifact; obtain external development seed inventory, pin exact environment and complete independent leakage review; record independent reviewer approval before introducing a separate holdout execution workflow.
