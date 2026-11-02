# Historical Artifact Evidence v1

**Status: PARTIAL / NOT FROZEN / HOLDOUT NOT RUN.**

Metadata inventory uses paginated GitHub Actions artifact listings with read-only `actions: read` access. The local ZIP scanner reads only supplied archives and extracts integer `seed`/`task_seed`/`random_seed`/`rng_seed`/`random_state` fields from structured JSON, JSONL and CSV. Unstructured text, dynamic seed derivation, missing/expired artifacts, manual runs, and all other external jobs remain unverified.

Never infer that an observed 10000-10099 literal was used for a scored experiment without inspecting its context. Never infer safety from an absent match. No validation run is authorized. The workflow inventories metadata only and **does not automatically download or inspect archive content**. Download individual trusted ZIP artifacts separately and pass `--zip /path/to/file.zip --skip-api` for local inspection. Zip size caps protect from incidental oversized data but not arbitrary malicious archives; use trusted artifacts on a disposable machine.

No code in this package evaluates synthetic or real held-out labels. Freeze still needs complete history, dependency environment lock and independent review. `scored_validation_allowed` is unconditionally false.
