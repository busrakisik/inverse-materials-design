# BHS v12.7 — Fe–Co–Ni hypothesis-to-measurement pilot specification

**Prepared 7 November 2026. Status: proposed collaborator-facing research design, not an approved physical study, registered prospective trial, new experimental dataset, or demonstrated materials discovery.**

## Why this scientific question

The project already has a mathematical rival-hypothesis module and a robust source-intake contract. The missing connection is a scientifically defensible *physical* question whose rival explanations could be examined through actual observations.

**Candidate system:** Fe–Co–Ni magnetic thin films. **Candidate primary observable:** coercive magnetic field inferred from a laboratory-approved magneto-optical Kerr hysteresis measurement, recorded in A/m using a verified field calibration. **Separate structural observable:** diffraction-based texture/phase descriptors from laboratory-approved X-ray characterization. Measurement wavelength, geometry, field sweep, film thickness range, processing route, substrate, composition verification and instrument tolerances remain unspecified until the responsible laboratory confirms them.

Prior work establishes the relevance of composition, microstructure, texture and Kerr measurements for related magnetic films. This is scientific background, not evidence that BHS has discovered a new relationship.

- NIST REMI open materials resources, Fe–Co–Ni composition-spread data, with Wang et al. (2022) and Yoo et al. (2006) cited by the source: https://pages.nist.gov/remi/data/
- Cooke and colleagues, texture and magnetic properties of FeCo films, *Journal of Physics D* (2000): https://doi.org/10.1088/0022-3727/33/12/304
- Sato and colleagues, magneto-optical properties of Fe–Ni, Ni–Co and Fe–Co alloy films (1991): https://doi.org/10.3379/jmsjmag.15.S1_113
- Fe–Co–V combinatorial film study measuring diffraction and Kerr magnetic response (2017): https://doi.org/10.1080/14686996.2017.1287520

The older NIST composition library is **development context only**. Its column mapping, experimental alignment and per-response uncertainty were not independently verified by BHS, and it may not be presented as a fresh physical validation source.

## Two provisional, competing scientific explanations

These are **test candidates for a physical expert to refine**, not established microscopic mechanisms.

**H0 — Matched-condition invariance.** At fixed verified composition, film thickness, substrate and measurement configuration, the proposed processing contrast does not yield a reproducible change in coercive field larger than a laboratory-defined minimum meaningful difference. A reproducible cross-batch difference exceeding that precommitted threshold would count against H0.

**H1 — Processing-associated structure and response.** At otherwise matched verified conditions, the proposed processing contrast produces a reproducible diffraction-observed structure/texture change *and* a coercive-field difference larger than the same laboratory-defined minimum. If adequate, independently replicated structural and magnetic measurements do not meet this dual criterion, that observation counts against H1.

These are neither logically exhaustive nor proof of texture causality. Processing can change strain, roughness, defects and other unmeasured factors together. X-ray diffraction alone does not isolate a microscopic cause. No mechanism-specific causal attribution is allowed without a suitable design and domain review. The effect direction, intervention details, acceptance tolerance, and precision are **unresolved**, never silently assigned plausible values.

## Proposed independent study structure (not yet authorized)

1. Obtain a confirmed lab collaborator, institutional source rights, material-handling review and an approved operating procedure. No program-triggered physical operation is allowed.
2. Laboratory scientist fixes the two allowable processing conditions, composition preparation and independent composition measurement, substrate and thickness controls, field calibration, temperature, orientation and reading procedure. Predefine all exclusions and unsuccessful fabrication records.
3. Identify independent **synthesis batches** as the preliminary grouping unit. Randomize approved processing assignments within appropriate blocks if scientifically feasible. Measurement-order changes from the same specimen are repeated observations, **not independent batches**.
4. Record original MOKE measurement traces and raw diffraction scans, not only extracted maxima and convenient summaries. Keep operator/session, instrument, time zone, measurement batch, sample ID, replicate and material lot identities. Film-thickness verification is required to interpret composition and structure effects.
5. Before the first qualifying observation, obtain the primary contrast and its **minimum meaningful effect in A/m**, actual uncertainty model, handling of nondetections/outliers, sample size/precision analysis, budget and cost of abstaining, independent calibration/evaluation split, comparator policies and bounded operating conditions.
6. The BHS hypothesis-specific evidence update must have an explicit, scientifically justified likelihood and an independently assessed noise model. The existing toy linear/quadratic/oscillatory bases are **not** the physical H0/H1 models. It is invalid to call a high posterior model weight proof of physical truth.
7. Judge the final method against a predeclared expert-reviewed fixed design, a composition-only reference, an appropriate structure-aware reference and a do-not-recommend comparator, at matched actual experimental costs and decision coverage. Assess predictive loss, effect-discrimination error, uncertainty calibration, failed/abstained decisions and resource use **separately**.
8. Prospectively acquired groups must not be mixed with the previously viewed V11–V12.6 historical and manufactured results or selected after learning the outcomes. A true partner lab determines admissible actions and measurement safety independently.

## Machine-readable pilot passport

`research/BHS_V127_FECONI_PILOT_PASSPORT.json` deliberately records all missing approval, calibration, feasible-action and resource items as `null` or `false`. `scripts/bhs_v127_hypothesis_readiness.py` checks the passport and reports specific scientific blockers. An unchanged, approved-looking string cannot authenticate a signature, apparatus state, actual measurements or legal reuse rights.

### Required rejection cases

- Duplicate model hypotheses; incompatible observable or units; contradictory or empty falsification criteria; absent minimum effect definition.
- Any cross-partition reuse of a batch, specimen or measurement group; unknown independent unit; false declaration of prospective data.
- Missing instrument calibration, preparation/conditioning logs, replicate chronology, investigator review, source rights, safety clearance or actual measurement costs.
- Treating an old composition dataset as an independent physical test or a previous negative experiment as a success.
- Any direct action, release, guaranteed risk or measured savings claim without new independent physical evidence.

Even a structurally complete passport **cannot automatically authorize** laboratory action or a claim of independent validation. External verification is an additional investigator-controlled process outside this module.

## Stop conditions and scientific accountability

Stop and abstain if no qualified partner, no safe feasible measurement, no calibrated uncertainty, insufficient independent groups, unregistered scientific contrast, unavailable original raw data or unverified source permissions. Report noncompletion, negative hypotheses, ambiguous evidence and costs without selecting favorable cases.

Source-integrity, computational code tests and reviewer metadata do not themselves show useful physical discovery. V11 inferior comparator results; the nonpassing first V12 historical replay; and the mixed V12.3–V12.6 results remain unaltered. Protected NIST seed range 10000–10099 remains unused. No source response or latent label is imported by this v12.7 work.

**Development gates:** `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `calibrated_uncertainty_proven=false`, `real_savings_measured=false`, `physical_recommendation_allowed=false`.

