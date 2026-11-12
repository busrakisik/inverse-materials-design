# BHS V12.13 — Identifier-recovery decision protocol

**Frozen before checking whether the source's incomplete combined identifiers are reconstructible.**

First source-intake CI `43254272297` rejected the source: the archived report shows 4,179 identifier-complete records from a verified 4,289-record compressed source. No target magnitude or material prediction was evaluated. A separate diagnosis (CI `43255084351`) established exactly 110 absent `GB_element_site` values, with other required identifier columns present; 30 target strings were missing in the full source. These are original data, not errors to overwrite.

## Falsifiable recovery criterion

Perform a **metadata-only** audit of the untouched, pinned original bytes, measuring:

- Cardinality and duplicate count of the original primitive tuple `(GB, element, site)` for all 4,289 records. Keep this exact order as a typed tuple, not unsafe concatenation.
- Cardinality of `job_name`; missingness of each primitive field; duplicated `(GB, element, site)` across multiple original jobs, if any.
- Relationship of the 110 missing combined identifiers to blank `E_seg` strings (only blank/not-blank, not energies), and distribution across the six GB groups.
- Among records with nonblank `GB_element_site`, whether a primitive tuple maps to different combined identifiers. Do not assume original identifier formatting or force a guessed string value.

If every primitive key is nonblank and unique, call these 110 rows **identifiable by a separate derived key**, not repaired upstream. Preserve raw missing field and each original job. If any primitive tuple repeats, report its count and **do not collapse it**. The original combined ID is never overwritten. Missing target values are still missing; do not fill or predict them.

This exercise is not approval of an eligible acquisition dataset, a model benchmark, a validation split, any material hypothesis, or an empirical cost model. `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, and `claim_of_superiority=false` remain binding regardless of metadata findings.

Do not re-run the first failed audit with changed criteria and label its original output successful. Keep the failed and successful diagnostic runs, their source hashes and source-only record chronology.
