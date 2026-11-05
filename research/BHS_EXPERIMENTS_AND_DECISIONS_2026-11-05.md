# BHS — Experiment Chronicle, Decisions & Reproducibility

**As-of 2026-11-05.** The complete time-ordered ledger of facts known from repository, CI artifacts, earlier deliverables and user-provided history. These are not verbatim full transcripts. Never promote a historical package title, test count or generated document to independently validated physical science.

## A. Chronological research history

| Period | Work / decisions | Evidence level and caveats |
|---|---|---|
| Aug 2026 | Began hypothesis-centric independent materials research; created modular BHS Python architecture, Bayesian evidence update and PUCT-style research vision, steric/SOAP filters, CLI and reports; Zenodo initial v1.0.1 DOI 10.5281/zenodo.21761835. | Initial research software release, **not peer-reviewed physical discovery**. |
| Oct 2026 | README and CITATION.cff clean-up; MIT license in repo; v1.0.1 remained older than research branch; many workflow/test repairs. | Focused README demo 83 tests at Actions run 41194127747; physical tests mocked CHGNet; 20-system benchmark NOT_RUN. |
| Oct 30–Nov 4 | Optional LiFePO4 CHGNet CPU workflow explorations, Matbench acquisition/integrity/split audits, provenance, sandbox/process oracle, deadline, policy evaluation isolation; scientific benchmark preliminary declarations. | Some real compute/real dataset access, but **not** a validated end-to-end real-discovery benchmark or production sandbox. Check each run's own results. |
| Early Nov | Synthetic 3-family Bayesian search, competing hypotheses v1/v2, belief-state/MCTS open loop, math references, EIG/cost and selected synthetic stress audits; customer/research-to-value and publication readiness documents. | Conditions and repetitions were developer-known. No physical likelihood calibration; synthetic 'true family' is known to data generator. |
| Nov 5 | NIST Fe–Co–Ni source contract and `.mat` inspection, 921 inferred samples, anonymous mapping audit, six blocked physical scientific gates. | Column order still unknown. |
| Nov 5 | NIST v1 retrospective Kerr optimizer, 4 policies × 3 seeds × 15 acquisitions; 27 tests; CI 41977734103, artifact 13392975164. | GP-EI better than BHS for mean normalized simple regret on this development set. |
| Nov 5 | NIST v2 post-hoc ablation, 11 policies/conditions × 5 seeds; 28 tests; CI 41988359209, artifact 13397435952; v1 numerical reproducibility check passed. | Different noise/lengthscale choices are post-hoc; not independent. |
| Nov 5 | NIST v3 prequential model adequacy, 3 selection tracks × 5 predictive models × 5 seeds × 12 predictions = 900, 31 tests; CI 41992614426, artifact 13397919991. | BHS/GP both undercovered nominal 90%; BHS substantially worse under these adaptive data conditions. |
| Nov 5 | NIST v4 variance decomposition and distance/phase sensitivity, 3 × 3 × 5 × 12 = 540 scores, 36 tests; CI 42046318788, artifact 13425230747; v3 parity successful. | Model-family disagreement term small in random tracks; this does not prove causal source. |
| Nov 5, after v4 | New-chat continuity directive: user expressly wants no lost project goals, experiments or decisions. | This handoff records available sources and scientific limitations. No automatic full chat transfer possible. |

## B. v1–v4 exact development results and interpretation

The source of numerical truth is the **four preserved aggregate JSON reports** in `research/verified_results/` and `research/BHS_V1_V4_AGGREGATED_RESULTS_SNAPSHOT.json`. Their initial CI artifacts have ephemeral retention. For complete numeric fields and correlations, inspect original JSON; this document intentionally does not round away or omit the raw *aggregated* evidence because it is separately stored in full.

- v1 fixed seeds 7, 13, 23; 15 total per campaign; average normalized regret GP-EI 0.025001283117256388, GP-UCB 0.07450292037487553, BHS-BMA-EI 0.13924593765076626, random 0.19775608454202978.
- v2 fixed seeds 7, 13, 23, 31, 41; v1 parity <1e-9; GP-EI(.22) ~0.0150, GP-EI(.40 posthoc) 0.0, BHS-BMA(.15) ~0.08355, BHS-BMA(.05 posthoc) ~0.05391. Other variants preserved verbatim in JSON.
- v3 coverage for GP(.22) vs BHS-BMA(.15): random 43.3% vs 28.3%; GP-EI track 43.3% vs 16.7%; BHS-EI track 48.3% vs 33.3%, all from n=60 adaptive one-step forecasts/cell. Their NLPD values are in the exact JSON; no population inference.
- v4 random-track BHS-BMA variance terms noise 0.02250; within 0.01987; between 0.00167; total 0.04404 (standardized response variance). Random-track BHS NLPD grows with distance near 12.82 / middle 147.23 / far 449.55; unequal adaptive bins. Additional discrepancy SD 0/0.5/1/2 → coverage 28.3%/55.0%/68.3%/76.7% on random track. These are sensitivity interventions, not actual calibrated measurement-error estimates.

## C. Reproducibility commands (current GitHub branch, CPU numerical requirements)

```bash
git clone https://github.com/busrakisik/inverse-materials-design.git
cd inverse-materials-design
git checkout bhs-scientific-audit
# To reconstruct exact 2026-11-05 snapshot instead of a newer branch:
git checkout c540a3dbc05f527e4a360deecb310bde68b2c47c
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2
python -m unittest discover -s tests -p 'test_nist_anonymous_offline_pilot_v1.py' -v
python -m unittest discover -s tests -p 'test_nist_diagnostics_ablation_v2.py' -v
python -m unittest discover -s tests -p 'test_nist_model_adequacy_v3.py' -v
python -m unittest discover -s tests -p 'test_nist_miscalibration_rootcause_v4.py' -v
# Real pinned NIST data fetch only if use terms permit:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m scripts.nist_miscalibration_rootcause_v4 --fetch
```

CI configurations and pinned source-blob checks are in `.github/workflows/`. Do not reproduce real source rows in shareable ZIPs. Workflow tests run appropriate dependencies; `requirements.txt` covers broader/legacy features and is not the pinned evaluation environment.

## D. Decisions we MUST keep

1. Always contrast model identification vs material-property optimization; they are different tasks with different baselines and estimands.
2. Real NIST 'C' columns are anonymous; never label them Fe, Co, Ni without author evidence.
3. Scored independent validation is LOCKED: do not use seeds 10000–10099; `scored_validation_allowed=false`.
4. Prior 5 NIST seeds and test material already influenced method choice; all NIST optimization and prequential metrics are exploratory developer data.
5. CI passing is implementation quality, not proof of science, efficacy, physical constraints, security, academic publication or commercial moat.
6. GP-EI currently a strong standard reference, and BHS has not beaten it on original protocol; don't exaggerate competitiveness.
7. v3/v4 reveal serious probability calibration/misspecification concerns and weak among-model posterior variance. Do not 'fix' merely by arbitrary variance inflation without separate evaluation.
8. Future priority: find domain-reviewed competing hypotheses and a new legally usable dataset with uncertainty/cost/feasibility; freeze a meaningful external test and strong baseline before looking at outcomes. Actual lab partnership is a strategic dependency, not yet a fact.
9. Keep all numerical reports and run IDs in durable storage before Actions artifacts expire. Back up repo source separately if absolute source preservation is required.
10. Keep branches/main/Zenodo release differentiated; changes on `bhs-scientific-audit` are not automatically published in release v1.0.1.

## E. Further source documents

- `research/BHS_PROJECT_HANDOFF.md` — inherited chronology and current decision.
- `research/BHS_MASTER_CONTEXT_2026-11-05.md` — master mission, architecture and guardrails.
- `research/BHS_EVIDENCE_REGISTER.json` — workflow IDs and exact aggregated result refs.
- `research/BHS_EXTERNAL_VALIDATION_V5_RESEARCH_PLAN.md` — future actual decision.
- `research/CUSTOMER_DISCOVERY_AND_MOAT_V1.md` and `research/PUBLICATION_READINESS_AUDIT_V1.md` in GitHub — commercial and publishing gates.
- `README.md` in GitHub — precise scope of focused CLI demo, 83 focused tests, NOT_RUN 20-system benchmark.
