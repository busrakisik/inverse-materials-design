# BHS v12.10 — Processing-scope and experimental-unit feasibility protocol

**Prepared 8 November 2026. Outcome-free methodological development, not a registered physical study, instrument procedure or scientific efficacy result.** The V12.9 manufactured plans and earlier negative/mixed results have already been inspected. All new examples are explicitly hypothetical, and no physical source data or independent protected seeds are used.

## Core falsifiable design assumption

V12.9's attractive within-session paired layout requires two treatments to be **independently assignable to coupons originating from one synthesis batch**. Whether this holds depends on the **processing step** chosen by the external materials investigator. It cannot be answered by matrix rank or machine-readable approvals.

**Route C — individually applied after-deposition intervention.** A laboratory might deposit comparable coupons together, then assign each coupon to an independently applied post-deposition processing event. In that *conditional* design, each coupon is the intended treatment-assignment unit and each deposition batch is a pairing block. A shared furnace cycle or common processing run may instead become the assignment unit; if that occurs, coupon-level replication is invalid and the study must be redesigned. Do not assume that all thermal or magnetic postprocessing can be performed independently.

**Route B — deposition-stage intervention.** If the proposed contrast changes a setting common to a whole deposition run, the synthesis run is the treatment-assignment unit. Having reference and modified coupons in the **same deposition run** would be inconsistent with that route. A possible alternative compares separately processed synthesis runs paired into predeclared production blocks, with each run assigned one arm. Pairing across runs is not the same control as paired coupons from one batch.

## Precommitted model-only feasibility checks

Input files contain **only** intended unit identifiers, arm labels, synthesis and matched-block IDs, independent processing-event IDs, specimen location strata, MOKE session and position, intended technical trace counts, planned original MOKE/XRD retention, and explicit false external-approval flags. No outcomes, material compositions, processing recipes, device commands or fitted model parameters are admitted.

For each route, verify:
1. Every identifier is unique at its declared level and every matched block contains one reference and one modified unit; no pseudo-replication from intended MOKE traces.
2. For Route C, each declared deposition batch must contain **both arms**, each coupon must have its own independently intended processing event, and no processing event may contain more than one coupon. Physical independence of those events remains *unverified*.
3. For Route B, each synthesis run must contain only one arm, no run may be reused across opposite arms, and the matched production block must contain **two distinct synthesis runs**, one per arm. A within-run treatment pair is **incompatible** with the physical intervention level.
4. Each MOKE measurement session must include both arms. Arm assignment must be counterbalanced across declared specimen-position strata; otherwise report an unresolved location/composition gradient confound. Co-sputtered composition spread films can exhibit spatially varying composition and thickness; a balanced label is not a substitute for measured local composition.
5. Use exact rational matrix ranks with matched-block fixed effects, session fixed effects and session-specific measurement-position trends, then add the treatment column. A one-column rank increment is only *algebraic distinguishability under the declared additive matrix*, never evidence of causal independence or adequate power.
6. Evaluate deletion of every whole **treatment-assignment event** and each complete measurement session. Return row count, named block count, complete reference/modified pair count, rank, residual row degrees of freedom and rank-based structural robustness **without selecting favorable deletions**. A lost event may break one pair; do not call a surviving complete pair independent without external provenance.
7. Record a **symbolic** uncertainty boundary rather than assuming a numerical sample size: for future independently sampled paired blocks, \(\operatorname{Var}(\bar D)=\operatorname{Var}(D_b)/B\), but within-block covariance, batch-to-batch drift, realistic loss, true assignment unit, and instrument uncertainty remain unknown. Intended traces do **not** increase \(B\). No prospective interval, power, effect size or cost is inferred.

A fully balanced design, nonzero residual row degrees of freedom, and no rank confounding **cannot authorize** processing, field measurements, physical outcomes, scientific superiority or budget claims. A domain expert must determine which route is physically applicable; both cannot be treated as independent validated options simultaneously.

## Negative scenarios to enforce

- A deposition-stage process applied to opposite-arm coupons from one synthesis run is rejected.
- Two purported coupon-level treatment units sharing the same processing event are rejected; repeating their MOKE measurements cannot repair the assignment-unit mismatch.
- A production-block pair made from only one synthesis run is rejected.
- Arm labels perfectly aligned with spatial coupon-position stratum, or instrument session, are rejected/flagged.
- A lost whole synthesis run, postprocessing event or MOKE session is counted at its true assignment level; repeated scans never restore a missing experimental unit.
- Duplicate sample/run IDs, missing measurement chronology, missing raw-trace/XRD plan, unknown approval status represented as verified, arbitrary result values and forbidden release flags are rejected.
- The original V12.9 variants and scores remain byte-identical and unmodified.

## Specific external prerequisites

An authorized Fe–Co–Ni thin-film investigator must first specify: the proposed actual physical processing contrast and whether it is independent per coupon or whole run; real synthesis and treatment batch limits; film position and verified local Fe/Co/Ni composition and thickness; thermal/instrument history and blocking; feasible specimen-splitting, measurement order, MOKE field calibration and original Kerr loops; separate diffraction scans; safety and data rights; and evidence-based uncertainty, meaningful coercive-field effect and budget. No laboratory contact, approval, physical feasibility, true composition map or new measurements have yet been established.

## Inference restrictions

- The model's nuisance columns are a *provisional additive structure*. Position counterbalancing cannot resolve an unknown nonlinear compositional gradient, and a design rank check cannot rule out unmeasured strain, texture, anneal-run or batch effects.
- Synthesis batches, processing events, MOKE sessions and multiple readings may share sources of dependence. No independent statistical group count is certified by the mere existence of names.
- Previous V11 negative comparison, first V12 historical parity failure and V12.3–V12.9 mixed and no-go results stay intact. The protected NIST seed range `10000..10099` remains unused; no released tags or historical sources are rewritten.

**Hard gates:** `development_only=true`; `physical_validation_by_bhs=false`; `independent_holdout_used=false`; `scored_validation_allowed=false`; `causal_identification=false`; `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`; `statistical_guarantee_supported=false`; `real_savings_measured=false`; `claim_of_superiority=false`.

## Scientific background

- Lazic, Clarke-Williams and Munafò (2018), *PLOS Biology*: experimental unit, independent assignment and technical repetition, DOI `10.1371/journal.pbio.2005282`.
- Review of combinatorial co-sputtered thin-film composition spreads and position-dependent constituent variation: https://onlinelibrary.wiley.com/doi/10.1002/mgea.87.
- Original V12.9 audited manufactured data: `research/BHS_V129_FIRST_DESIGN_ATTRITION_REPORT.md`.

