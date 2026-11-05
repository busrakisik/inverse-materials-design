# BHS — NIST Composition-to-Model Mapping v1

**Status: real-file descriptive readiness inspection; NO model fit, no scoring, no discovery claim.**

## Scientific question and stopping rule

NIST REMI's pinned Fe–Co–Ni data contains `C` (composition), `Coer` (magnetic coercivity, mT), `Kerr` (Kerr rotation, mrad), `XRD`, and `TTH`. The source description DOES NOT specify composition column-to-element ordering, fraction-versus-percent unit, per-row measurement uncertainty, experiment cost, or whether rows encode replicates. Therefore do NOT map `C[:,0]` to Fe, `C[:,1]` to Co, and `C[:,2]` to Ni based solely on the file's name. Even if rows sum to 1 or 100, this is numeric evidence of scale, NOT authoritative unit provenance. No model receives unverified data.

Source: `usnistgov/remi` NIST branch `nist-pages`, immutable commit `596b04435fb577175264a70c4434f5539b809510`; `.mat` Git blob `e506db115d522d62618042abead7df2695ccf13e`, 289480 bytes.

- NIST data: https://pages.nist.gov/remi/data/
- NIST documentation: https://github.com/usnistgov/remi/blob/nist-pages/data/Combinatorial%20Libraries/Fe-Co-Ni/data%20description.txt
- Wang et al. 2022: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=934371
- Yoo et al. 2006: *Identification of amorphous phases in the Fe–Ni–Co ternary alloy system using continuous phase diagram material chips*.

## What is checked

- Independently revalidate immutable source byte count and Git blob SHA-1 before parsing MATLAB.
- Require unambiguous numeric `N x 3` or `3 x N` composition; retain **anonymous** source column IDs.
- Identify fraction-like and percentage-like numeric rows by nonnegativity and sum tolerance, but **do not certify** physical atomic fractions.
- Require each magnetic measurement to be one scalar per sample, not silently flatten multi-column matrices; report counts jointly finite with compositions, without saving raw rows.
- Report XRD and TTH shapes, but **do not** assume diffraction peak labels or sample alignment from matching dimensions.
- Mark missing authoritative element ordering, scale, sample IDs, measurement error, lab costs and domain-reviewed hypothesis mechanisms as blockers.

## Scientific outcome selection

The NIST active-learning paper uses the data for **property optimization** (coercivity or Kerr), with contrasting landscape complexity. This differs from the present BHS claim of discriminating among **true** physical mechanisms; the three multivariate BHS basis families are phenomenological and not validated explanations of Fe–Co–Ni magnetic behavior. We MUST obtain a materials-domain-reviewed hypothesis definition, or explicitly switch the objective and comparators to property optimization. No retrospective target labels are disclosed to a policy in this module.

## Research use and licensing

The public upstream data is fetched only inside CI; no raw measurements are committed or uploaded as artifacts. NIST requests citation of Wang et al. and Yoo et al. Exact reuse, redistribution and commercial permissions for this file remain under review; public availability alone is not an explicit commercial license determination.

## Before training or evaluation

1. Verify **column-to-element order and fraction/percent semantics** using source authors, supplemental documentation or authoritative source code.
2. Verify target sample alignment and any missing/invalid target policies against domain documentation; distinguish NaN from physical zero.
3. Establish a domain-supported scientific question and candidate hypothesis families. Predeclare transformations, priors, data splits, model checks and baselines before label-bearing evaluation.
4. Obtain empirically supported per-row uncertainty where feasible; otherwise label assumptions and run sensitivity analyses, NOT 'calibrated' inference.
5. Use actual costs only when documented; otherwise clearly label synthetic costs and DO NOT claim financial savings.
6. Establish lawful reuse and privacy/IP review, leakage-safe oracle and independent approval before any scored holdout.

## Run

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1
python -m unittest discover -s tests -p 'test_nist_composition_mapping_v1.py' -v
python -m scripts.nist_composition_mapping_v1 --fetch
```

Result: `runs/nist_composition_mapping_v1/mapping_readiness.json` and SHA-256, aggregations only. `scored_validation_allowed=false`; independent BHS holdout seeds 10000..10099 are never used. **CI success confirms parsing and checks, not BHS fitness, scientific validity or physical prediction.**
