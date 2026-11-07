# BHS — External laboratory evidence intake and controlled-pilot requirements (draft v1)

**Status:** Proposed research-collaboration specification, not an accepted study, operational laboratory procedure, procurement request, signed partnership or validated safety system.

## The concrete research value proposition

Before BHS can legitimately advise a laboratory to repeat, modify or abandon an experiment, it must be able to trace the source of each measurement, identify the scientific assumptions behind its proposed action, and know when independent evidence is insufficient.

**Research question for a partner laboratory:** Compared at the same fraction of cases receiving an actionable recommendation, does evidence-aware abstention lower erroneous-decision risk or real decision cost versus a simple metadata-completeness rule and a domain expert's established workflow?

A partner should also be able to find that the approach **does not** help or is too costly. Those outcomes are essential research results, not project failures to conceal.

## Required information before a pilot can be designed

| Evidence category | Minimum records to request | Why it is required |
| --- | --- | --- |
| Intended decision | A precisely defined, scientifically feasible proposed change or measurement, plausible alternatives, outcome, units and forbidden actions | Avoid an ill-defined intervention and unsupported physical claims |
| Materials | Source lots, batch IDs, composition, moisture/conditioning corrections, purity or comparable attributes as applicable | Identify material changes that could confound a comparison |
| Preparation | Mixing/processing order, equipment, operator/session information where legally shareable, conditioning and processing timestamps | Establish process repeatability and temporal dependencies |
| Test environment | Temperature, humidity, curing or other domain conditions, durations, sample geometry and applicable laboratory-approved method | Establish whether observed records are physically comparable |
| Instrumentation | Instrument model/identifier, actual calibration and maintenance records, detection limits and uncertainty/precision documentation | Avoid treating uncalibrated responses as known truths |
| Experimental design | Treatment/control definitions, randomization or blocking, feasible ranges, baseline, replicate and repeated-measures structure | Establish exchangeability, overlap/support and a well-defined intervention where possible |
| Observations | Measured responses in original units, replicate IDs, timestamps, missingness, censored values, unsuccessful trials and reasons | Prevent success-only selection and unjustified uncertainty estimates |
| Cost and consequences | Actual measurement time, material/energy/labor use, review delay, loss from wrong action and cost of abstaining | Evaluate practical usefulness rather than speculative savings |
| Source rights and review | Data owner, reuse terms, access controls, review responsibility, versioned data fingerprint, authorized decision level | Preserve privacy, provenance and oversight |

**No fabricated replacement values:** Unavailable information should be recorded explicitly as *unknown*, *unmeasured* or *contradicted*, not converted to a plausible default. A filename, certificate reference or signed metadata packet is insufficient without independently inspecting the relevant source.

## Pilot design gates

**Gate 0 — Collaboration and governance.** Obtain authorized data access, stated legal reuse scope and an actual domain expert. Never upload partner-sensitive raw records to a public repository.

**Gate 1 — Domain and intervention validity.** A laboratory specialist defines a physically feasible intervention, the relevant competing explanations, variable units, manufacturing/process constraints and a primary causal estimand. Changing one mixture component can force adjustments to total volume, workability, balance or other coupled variables; no artificial claim that everything else is held constant.

**Gate 2 — Measurement quality.** Verify batch-level grouping, instrument calibration, replicate variances, outliers, failures and any measurement censoring. Define how disagreements and inaccessible raw evidence are handled.

**Gate 3 — Predeclare the study.** Specify acceptable action set, evidence-abstention triggers, prospective or otherwise independently collected outcome labels, baseline policies, risk/cost weights, evaluation population, confidence intervals and sample-size/precision analysis **before** viewing evaluation outcomes.

**Gate 4 — Data partition and leakage controls.** Keep development/calibration groups distinct from the untouched evaluation groups at the material batch, operator, instrument, laboratory or calendar level as the scientific question requires. Do not recycle the earlier NIST/UCI research measurements as an independent validation set.

**Gate 5 — Independent outcome and decision review.** Compare: (i) an existing expert workflow; (ii) an always-defer reference; (iii) a simple evidence completeness rule; (iv) appropriate fixed statistical/model baseline; and (v) BHS's assumption-aware decision pathway. No physical experiment may be triggered autonomously by the prototype.

**Gate 6 — Publish all results and limitations.** Record coverage, wrong-action frequency and severity at matched coverage, selective risk with uncertainty, false reassurance under missing or shifted data, extra measurements, delay and **actual** resource cost. Report non-inferiority, no advantage, missed opportunities and complete abstention where observed.

## How a pilot can falsify BHS's value

- When matched at the same decision coverage, a simpler policy has the same or lower error at lower review/measurement cost.
- BHS's apparent benefit disappears on a new batch, instrument, site or time period.
- Required evidence is nearly always unavailable, so BHS defers almost every case and provides little decision value.
- Metadata signatures are valid but original measurements or calibration are unreliable.
- Safety, time, financial or operational trade-offs negate potential improvements.
- Independent external replication fails.

In any of these cases, the scientific conclusion must state that BHS has **not yet shown** the claimed advantage.

## Intended confidential versus public artifacts

- **Public:** approved protocol, data dictionary without personal/confidential identifiers, exact code commit, test fixtures with synthetic values, summary statistics authorized for publication, source/citation policy, all negative results.
- **Access-controlled:** raw measurements, detailed formulas or proprietary material identities when restricted, instrument logs, internal identifiers, validation outcomes prior to a locked release, and actual reviewer evidence.
- **Never commit:** credentials, signing private keys, unauthorized partner records, personal contact details or invented performance guarantees.

## Current evidence and next concrete task

The v6 UCI exercise exposes unavailable curing, batch, test and replicate context. The v7–v8 contracts verify failure behavior and cryptographic linkage of declared metadata. The [v9 two-world counterexample](BHS_CAUSAL_NONIDENTIFIABILITY_V9.md) proves that even identical observed data and signed metadata can remain consistent with opposite effects. None of these results establish decision superiority or a successful laboratory pilot.

**Next external prerequisite:** Recruit an appropriate laboratory/domain collaborator and jointly specify an intervention and actual data-collection feasibility. Only afterward freeze a statistically justified independent pilot protocol.

Scientific background: Hernán & Robins, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook) (identifiability); see also [the BHS decision reliability study proposal](BHS_PROSPECTIVE_DECISION_RELIABILITY_STUDY_DESIGN.md).

Research gates: `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, no superiority or savings claims, no use of reserved NIST independent seed range `10000..10099`.
