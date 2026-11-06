# BHS v8 — Evidence integrity before scientific review

**Status: preclinical-style software integrity analogy is not a claim of clinical or laboratory validation. No prospective physical experiment has been performed.**

## The weakness this stage tests

The v7 decision contract accepts a user-declared `verified` evidence field once a nonempty source reference has been supplied. It also allows a risk calculation when numeric benefit, harm and abstention values have no strictly checked shared measurement unit. Those are *logical and provenance gaps*, not evidence of a laboratory safety incident. Neither a probability number nor a document pointer should be interpreted as independently verified just because the software accepted it.

v8 addresses two narrow *computer-verifiable* preconditions: **risk quantity comparability** and **tamper-evident independent-review packets**. It does not authenticate the underlying physical measurements or establish predictive calibration.

## Implemented boundary

- Preserve v7 decisions when data are missing, contradicted, invalid or insufficient; v8 must **never elevate** those responses.
- For a would-be laboratory expert-review candidate, require three explicitly identical nonempty utility units (benefit, harm and abstention) and a documented source population and method for the lower success-probability bound.
- Require a review packet signed using Ed25519, associated with an **independently configured reviewer public key**, not a key accepted from the same untrusted evidence submission.
- Bind the signature to exact canonical JSON of the *declared evidence metadata* and *declared risk numbers*. Mutating either after review invalidates the packet.
- Bound reviewer approval by a strictly parsed, timezone-aware validity window of at most **30 days**. Unknown reviewer, malformed packet, expired packet, mismatched signature and risk-unit mismatch all fail closed.
- A passing packet means **eligible for additional human expert review only**. The code still sets `automatic_laboratory_action_authorized=false`, `actual_measurement_validity_verified_by_code=false`, and `probability_calibration_verified_by_code=false`.

**Critical trust assumption:** The organization must configure and protect reviewer trust anchors *out of band*. Supplying both a fabricated reviewer key and a self-signed packet as ordinary user input is **not independent attestation** and must never qualify in a real deployment. Private signing keys are not included here. Tests generate fresh disposable signing keys and invented evidence for software-contract purposes.

**Important scientific limitation:** A signature here binds submitted **metadata**, not the physical source document bytes, measurement instruments, lab operator, calibration algorithm or outcome data. It is not a substitute for authorized source retrieval, trustworthy source-file hashing, laboratory chain of custody, external statistical review, or independent data. The prototype makes no claim to implement full regulated records management.

## Counterexample-driven testing

The synthetic tests explicitly inject: missing material context, contradicting source status, missing units, mixed currency units, unspecified units, missing bound methodology, absent reviewer, self-provided/untrusted reviewer, post-signing risk changes, post-signing evidence changes, forged signatures, expired/future/overlong review windows and apparently valid signatures that nevertheless cannot authorize autonomous action.

These tests are **software regression contracts**. They are not measured selective-risk improvement, fewer erroneous laboratory recommendations or evidence of commercial performance.

## Reproducibility

```bash
python -m pip install cryptography==46.0.4
python -m unittest discover -s tests -p 'test_verified_review_v8.py' -v
```

Code: `bhs/decisions/verified_review_v8.py`  
Tests: `tests/test_verified_review_v8.py`  
CI: `.github/workflows/bhs-provenance-integrity-v8.yml`

Original public NIST v1–v4, UCI v5–v6, and v7 result files remain untouched. No independent holdout, physical validation, proof of superiority or reserved NIST evaluation seeds are used.

## Next decisive research question

Once an actual laboratory independently establishes its evidence sources and review authority, does this workflow improve **selective error rate at fixed coverage**, lower the rate of misleading recommendations under missing/shifted data, and reduce the net cost of extra measurements compared with simple record-completeness rules and an expert decision baseline? Answer this only with an untouched, predeclared, real independent evaluation.
