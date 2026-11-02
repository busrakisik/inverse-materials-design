# BHS Independent Validation — freeze preparation v1

**PROPOSED / NOT FROZEN / NO HOLDOUT LABELS / NO SCORES / NOT PHYSICAL.**

This is a metadata-only safeguard, not independent confirmation. It prepares checksums of the current commit and research source files and a **proposed** 100-seed list (10000–10099), disjoint from the known pilot 0–29. It deliberately sets `freeze_approved=false` and `scored_validation_allowed=false`. Additional previous development/tuning seeds must be independently audited before this list is finalized. CI runs seven contract tests only; it must not access hidden labels or generate performance estimates.

Before a scored validation, audit all prior experiments and seed overlap; choose and justify one primary scenario (transparently documenting selection after inspecting pilot findings), freeze hyperparameters, policy/baseline code, environment, analysis bootstrap seed, task/generator checksums, and independently verify the information boundary. Commit a finalized manifest and lock it before any holdout results are produced. A protocol change after viewing results requires new held-out tasks. A matched-seed synthetic result is not a physical materials-discovery result.

Run locally: `python -m unittest discover -s tests -p 'test_validation_freeze_prepare_v1.py' -v` and `python -m scripts.validation_freeze_prepare_v1`. Never treat the proposal artifact as permission to run evaluation.
