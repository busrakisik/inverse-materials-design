# BHS — External Scientific Validation Strategy v5 / action-ready research plan

**STATUS: PLAN ONLY. Nothing in this document is evidence of a completed v5 experiment.** New ChatGPT should prioritize validated, substantive scientific progress, not another circular static gate. No external candidate dataset has been confirmed by this handoff.

## Research pivot

NIST Kerr shows that current BHS regression-family averaging is systematically underdispersed and inferior to a strong fixed GP–EI reference in the explored protocol. Repeating the same NIST test while changing hyperparameters *cannot establish independent scientific advantage*. The project has two different potential contributions:

**A. Hypothesis discrimination** (mission-aligned): Given physical, domain-expert-reviewed rival hypotheses, does adaptive evidence allocation distinguish them reliably and at lower validated experiment cost (or with fewer observations), accounting for unknown/invalid theories, censored/failed measurements, calibration, changing experimental conditions and abstention? Candidate baselines: one-step EIG and EIG/cost, relevant sequential design/knowledge-gradient/entropy methods; strong matched baselines, not only random/cheapest.

**B. Property optimization** (existing NIST research): Can an explicit model-family portfolio improve sample efficiency under matched constraints relative to *strong, tuned* GP–EI, GP–UCB/TS, etc., on fresh external datasets? This is a separate hypothesis and should be abandoned or honestly reported negative if no externally demonstrated gain.

## Next concrete steps (do these in order, can make research deliveries)

1. **Scope one falsifiable external question**, with physical domain collaborator if possible; document observable, intervention, candidate feasibility, competing hypothesis falsifiability, uncertainty and 'failure' semantics. Do not pretend anonymous mathematical response shape is a real mechanism.
2. **Source/license research**: identify at least two external dataset possibilities and document original license (not merely GitHub repository license), downloadability, provenance/version, sample count, target/descriptor alignment, missingness, independently recorded measurement uncertainty, actual cost/time/feasibility, temporal/lab/batch partition, and possible negative results. A source without known legal reuse constraints is not ready for export.
3. **Choose and record *one* primary task** A or B and a precise estimand. Include no-good result outcome, a priori stopping and abstention rules, and a legitimate missing/failed experiment policy. Only then choose baselines and fixed budgets.
4. **Revisit BHS probability model** on a distinct *development* dataset: hierarchical discrepancy / heavy-tailed alternatives / heteroscedasticity / out-of-model detection are hypotheses to test; choose independently justified priors and non-oracle calibration. Report fail-to-calibrate cases, not merely inflated nominal 90% intervals.
5. **Fully freeze evaluation** before seeing independent labels or defining final scores; ensure secure label isolation and expert consent. Prior independent seed IDs 10000..10099 are reserved/prohibited: do NOT touch them based on this plan. External, separately reviewed holdout design is necessary. No statistical claims until appropriate independent replication.
6. **Publishable output candidate**: a conservative, fully evidenced performance/uncertainty paper or reproducible negative result plus cross-domain validation; real lab ROI or technology moat claim only after business evidence.

## Explicit v4→v5 handoff question

"What is BHS actually trying to infer about physical reality, rather than maximize a property on one retrospective anonymous-coordinate matrix; and what new permitted evidence could falsify its method advantage?" The answer determines next code, benchmark and outreach.

## Evidence-only milestone checklist (not administrative loops)

- [ ] At least one permission-cleared, semantically aligned **new** dataset with source and version pinned.
- [ ] Domain expert and scientific physical hypothesis validity reviewed (if Task A).
- [ ] Measurement variance/missingness/cost uncertainty treatment predeclared.
- [ ] Strong baselines and paired-budget protocol frozen before accessing independent labels.
- [ ] New experimental code, synthetic tests, CI and aggregate-only reports; no hidden-label leakage.
- [ ] Honest independent outcome, negative or positive, with implications for product and scientific claims.

Potential lab customer-interview preparation is covered in `research/CUSTOMER_DISCOVERY_AND_MOAT_V1.md` in GitHub; it is **not** evidence of completed interviews.
