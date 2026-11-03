# BHS Pinned Evidence Reconciliation v1

**Status: HISTORICAL_EVIDENCE_RECONCILED_PARTIAL_NO_HOLDOUT.** No held-out evaluation; no research superiority claims.

This tool downloads five **specific** GitHub Actions artifact archives, verifies their ZIP SHA-256 byte digests against the pinned values in the code, reads selected JSON manifests, validates recorded source commits where present, and compares the three shared synthetic core-module hashes between the environment record and freeze manifest. The CI job also reads the **actual 1,800-row pilot JSONL** and verifies the 30 task seeds are exactly 0–29 and disjoint from the 100 proposed seeds (10000–10099).

Sources: CI artifact IDs 13213742932 (freeze), 13211390930 (environment), 13161561259 (Actions metadata), 13146289436 (pilot raw results), and 13160318234 (static seed inventory). These artifacts originate from **different commits**; matching three source hashes is not equivalent to the entire repository being frozen on one commit. An artifact checksum proves byte identity, not that the contents were independently certified.

Requires Actions `actions: read`; downloads archives in CI with a repository-scoped ephemeral `GITHUB_TOKEN`. Uses bounded reads and archive checks, and does not execute artifact content. If archived ZIP contents differ, are expired, or permissions block download, the run **fails closed** rather than reporting success. A local offline reproduction can use `--local-dir` with files named `artifact-<id>.zip`.

**Outstanding requirements:** all previously executed seeds (including off-repository/local), independent label-boundary review, locked whole environment, frozen pre-outcome analysis plan, and external review. `scored_validation_allowed` stays `false` by design. Do not merge to main or claim scientific confirmation from this gate.
