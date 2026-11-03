# BHS Validation Freeze Evidence Manifest v1

**STATUS: EVIDENCE ASSEMBLY ONLY / NOT FROZEN / NOT APPROVED / NO HOLDOUT.**

This stage records the **current** Git SHA, SHA-256 digests of five benchmark/protocol source files, the proposed holdout seed set `10000–10099`, previously documented pilot seeds `0–29`, and explicit candidate model parameters. These are candidate freeze details, **not a frozen preregistration**.

The optional `--evidence-json PATH` argument accepts existing metadata JSON files and records their hashes and declared commit IDs. It **never** turns self-reported JSON into an independent review or authorizes validation. Cross-commit evidence records are flagged for reconciliation. The tool never instantiates a synthetic task, calls an Oracle, or accesses hidden outcomes.

## Reproduce locally

From repo root (any Python 3.11+ compatible runtime for *this metadata-only script*):

```bash
python -m unittest discover -s tests -p 'test_validation_freeze_manifest_v1.py' -v
python -m scripts.validation_freeze_manifest_v1 --out-dir runs/validation_freeze_manifest_v1
```

Workflow uses Ubuntu 24.04 and Python 3.11.9. Outputs are `freeze_evidence_manifest.json` and `freeze_evidence_manifest.sha256`; upload only as workflow artifact, **not to be confused with approval**. This workflow deliberately does not run a scored evaluation.

## Remaining required independent evidence

1. Confirm all previous experiments, including manual/off-repo/deleted artifacts, did not use candidate holdout seeds. Preserve a reviewed inventory and limitations.
2. Reconcile evidence provenance with frozen source commit and checksums; lock Python interpreter, runner image and Actions digests as appropriate.
3. Freeze primary scenario (the `smooth` proposal is explicitly pilot-informed), bootstrap RNG seed, analysis and failure handling *before* new outcomes.
4. Independently audit hidden-label access and document reviewer approval and immutable preregistration.
5. Only after these stages, a **separate, explicitly authorized** holdout evaluator can be designed.

**Never change `scored_validation_allowed` to true merely because CI tests pass.**
