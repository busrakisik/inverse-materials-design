# BHS — MASTER PROJECT CONTINUITY / COMPLETE RESEARCH CONTEXT

**Snapshot date:** 5 November 2026 (Europe/Istanbul)  
**User request:** preserve as much of the project's factual history, mission, vision, goals, proof, decisions, source inventory and next action as possible when opening a new ChatGPT chat. This is **not a verbatim export** of every former chat message; availability of memories, external files and connectors varies. Unverified details are marked, not invented.  
**Author / independent researcher:** Büşra Kısık  
**Repository:** https://github.com/busrakisik/inverse-materials-design  
**Working branch:** `bhs-scientific-audit`  
**Last confirmed HEAD:** `c540a3dbc05f527e4a360deecb310bde68b2c47c` (this SHA is an immutable point-in-time source reference)  
**Reference Zenodo initial release:** https://doi.org/10.5281/zenodo.21761835 (v1.0.1, earlier than the current research branch)  
**License in repository:** MIT; reconcile published archives' separate metadata if necessary.  
**Last verified CI:** https://github.com/busrakisik/inverse-materials-design/actions/runs/42046318788; 36/36 v4 tests, real NIST post-hoc 540 scores, artifact 13425230747.  

## 0. Highest-priority read-first instructions for the next ChatGPT conversation

1. Do not restart the project as a greenfield toy; **continue BHS at the GitHub HEAD**, checking newer changes first. Read `research/BHS_MASTER_CONTEXT_2026-11-05.md` (this file), `research/BHS_PROJECT_HANDOFF.md`, `research/BHS_EVIDENCE_REGISTER.json`, `research/BHS_EXPERIMENTS_AND_DECISIONS_2026-11-05.md`, `research/BHS_NEXT_CHAT_START_HERE.md`, and latest research `.md` files. The user's long-term aims and no-overclaim rules must persist.
2. Verify the current GitHub branch HEAD, relevant files, CI jobs and **actual CI artifact JSON** before citing results. If a workflow failed while files were uploaded sequentially, inspect latest *complete* HEAD run, not transient earlier failures.
3. The user typically uploads ZIP contents to the working branch manually and reports "Dosyaları yükledim". Check actual repository files and GitHub Actions/artifacts. When continuing substantive R&D, deliver real code, tests, workflow `.yml` **inside the ZIP and separately**, plus meaningful scientific research note; avoid filler documents and endless protocol gates. Prior direct YAML download links did fail; always provide code as copyable fallback if necessary.
4. Preserve `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, no physical-superiority or discovery claim; **NEVER use reserved seeds `10000..10099`** until a separately authorized, scientifically reviewed independent evaluation. Do not silently unlock or relabel results.
5. Future work must make a **scientific advance** (well-specified external test, new evidence, domain-reviewed hypotheses, meaningful differentiation) and not overfit the same NIST Kerr dataset with ever more after-the-fact tuning.

## 1. Enduring mission — WHY the project exists

**Bayesian Hypothesis Search (BHS)** is the user's independent, hypothesis-centered scientific computing research effort. The motivating question: *Can an AI-assisted scientific system represent explicit competing hypotheses, select information-rich feasible next experiments, update beliefs using evidence, and preserve an auditable explanation of why each experiment was chosen?* The first application domain is inverse materials design, with a longer-term ambition to generalize a validation-first scientific-reasoning workflow to other scientific domains.

Its desired system is a **closed loop**: (i) define candidate, falsifiable scientific hypotheses; (ii) attach provenance and evaluable priors/likelihood models; (iii) propose useful experiments/compute steps, possibly via MCTS/PUCT or Bayesian expected information gain; (iv) obtain actual computational or laboratory observations; (v) update hypotheses Bayesianly; (vi) detect model misspecification and abstain when uncertainty is unreliable; (vii) retain reproducible decisions, inputs and evidence. *This is the vision, not a claim that all parts already work end-to-end or are scientifically validated.*

**Three strategic success criteria** (simultaneously desired, not yet met):

1. **Publishable scientific evidence**: convincing falsifiable question, rigor, independently reproducible comparisons, transparent error bars and negative results, external expert review.
2. **Real customer / laboratory problem**: a partner with a consequential costly experiment-selection or hypothesis-discrimination workflow, permission-cleared data and measured costs/uncertainties.
3. **Defensible technological advantage**: domain-specific faithful hypotheses; robust uncertainty and abstention; trustworthy evidence integration; efficient experiment suggestions; auditable scientific operations and integration. Generic Bayes/MCTS/EIG algorithms are **not by themselves** a defensible commercial moat.

Long-run outcomes include an honest preprint/paper, software release with DOI, strong portfolio evidence for PhD/research group applications, and *conditional* commercial exploration with a real lab. **No patent, paid customer, physical discovery, peer-reviewed paper or measurable cost saving has yet been established.**

## 2. User's academic/research context — only what changes project decisions

- Independent research developer; Beykoz University Industrial Engineering (English-medium), planned completion around **May 2027**. Interests: AI for Science, Bayesian decision-making, operations research, sequential experiments, active learning, uncertainty and scientific software. The BHS project is self-directed, and the user values demonstrated learning-by-building and rigorous independent study.
- Project may support **2027 US/Europe PhD/research outreach**. Avoid exaggerating real-world or supervised research credentials. An industrial-engineering capstone on sustainable capacitated facility location (TBL, carbon policies) is a **separate** academic project, not proof of BHS materials experimentation.
- Related independent work: **Evidence-Guided Computation (EGC)** — Bayesian evidence allocation and dynamic-programming experiments, separate from BHS. Cross-reference only where the methods genuinely overlap.
- Preferred working language Turkish. Workflow style: concise but substantive, code first, downloadable upload ZIP, YAML separately, GitHub CI verification, thoughtful account of scientific meaning, no repeatedly asking for facts already known.

## 3. Architecture and what is *actually* implemented

Historical research prototype components (see live GitHub sources, not old verbal summaries):

- `bhs/search/bayesian_engine.py`: deterministic/probabilistic belief updates on supplied prior and likelihoods; mathematically tested, not independently calibrated physical evidence.
- `bhs/evidence/likelihoods.py`: exploratory overlap / SOAP-distance transforms, not a measured calibrated physical likelihood; need validation of evidence dependence.
- `bhs/cli.py`, provenance bundles, `bhs/reports/generate_artifacts.py`, 20-system benchmark protocol, baseline utilities; the focused demo is illustrative and marks **NOT_VERIFIED**. The 20-system protocol is **NOT_RUN** and must not be represented as an executed material-discovery study.
- `bhs/physics/relaxer.py`: optional CHGNet adapter. Some later independent CPU workflows involving actual LiFePO4/CHGNet were run, but that is not a fully validated 20-system benchmarking campaign, and a CHGNet model evaluation is not CHGNet training, experimental material validation or formation-energy certification.
- Earlier `app.py`, `crystal_gen/`, `legacy/` are old prototypes outside the focused README demo evidence.
- Experimental `scripts/` and `tests/` contain **separate, real implemented** Bayesian methods, approximate MCTS/PUCT and belief-state prototypes, EIG/cost and paired synthetic comparisons, mathematical verification, Oracle/deadline/isolation contract checks, and NIST retrospective offline studies. Their statuses differ — many are synthetic development or contract checks, not a unified physical discovery system.
- Evidence/provenance workflow includes Matbench acquisition and split-quality checks, process oracle, deadline, sandbox/adversarial isolation, independent math references, hypothesis-family models, likelihood/uncertainty diagnostics. CI success proves specified checks execute, **not** overall science or secure adversarial isolation.

**README discrepancy:** `README.md` accurately warns that `bhs.cli --demo` has no actual MCTS rollouts; other experimental `scripts/` do implement development variants of search. Distinguish the demo path and experimental code. README's as-of date (31 Oct 2026) predates v1–v4 NIST experiments; do not assume current research branch is represented in archived Zenodo v1.0.1.

## 4. Main scientific paths — NEVER confuse their objectives

**Path A: hypothesis identification / evidence-guided experimentation**. Synthetic ground-truth mathematical families (linear, quadratic, oscillatory, etc.), Bayes posteriors, EIG and EIG/cost vs strong baselines; objective often `-log posterior P(true generating family)`, *not* material-property maximum. The development grid used 24 paired scenario configurations, four policies, 96 campaign records with synthetic cost budget 8 arbitrary units. No physical mechanisms, measured laboratory costs, independent superiority or real user ROI.

**Path B: retrospective property optimization on real measured NIST Fe–Co–Ni**. Anonymized three-dimensional composition coordinates; choose an unobserved historical Kerr measurement, forecast first, reveal only after selection, and compute normalized simple regret or prequential prediction diagnostics. **This does not identify true physical hypotheses**; the mathematical response shapes are phenomenological alternatives. The NIST repo column-to-element mapping and source-specific usage clearance remain unresolved.

**Path C: materials search / physical simulation**. CHGNet and feasible candidate screening are separate potential downstream checks; no end-to-end prospective physical validation. Do not conflate workflow names or smoke tests with real verified discoveries.

## 5. Real NIST immutable source and scientific constraints

- Official repo: https://github.com/usnistgov/remi; `nist-pages` commit `596b04435fb577175264a70c4434f5539b809510`.
- Source `.mat` path: `data/Combinatorial Libraries/Fe-Co-Ni/FeCoNi_benchmark_dataset_220501a.mat`; Git blob SHA-1 `e506db115d522d62618042abead7df2695ccf13e`; length `289480` bytes.
- Fields documented: `C` anonymous composition; `XRD` diffraction; `TTH` two-theta axis; `Coer` coercivity (mT); `Kerr` Kerr rotation (mrad). NIST 921 eligible historical Kerr samples in v1–v4 development. `C` column order **NOT AUTHORITATIVELY mapped** to Fe/Co/Ni; atomic fraction vs percentage provenance, per-row instrument uncertainty, costs, row identities, physical experiment constraints and reuse permission need independent verification. Within-pool relative normalization to simplex is a mathematical operation, not a source-certified chemical assertion.
- Primary literature: Wang et al. (2022), DOI `10.1093/oxfmat/itac006`, and Yoo et al. (2006), *Intermetallics* 14, 241–247. Source manifest says to cite both.
- Source binary is NOT included in this continuity package and should not be republished while rights are unsettled. CI retrieves exact pinned bytes with integrity checks; this master ZIP preserves aggregate evidence only, not raw third-party material rows.

## 6. Empirical milestones already VERIFIED (as of this snapshot)

| Milestone | Run / artifact | Execution proof | Main scientific interpretation |
|---|---|---|---|
| NIST source inspection | 41968361627 | 20/20 tests; inferred 921 rows | Access/pinning and descriptive array inspection, not physical semantic mapping |
| Multivariate response models | 41969276576 | 20/20 synthetic tests | Gaussian-regression model family prototype, not true physical mechanisms |
| NIST anonymous mapping audit | 41970917911 | 23/23 tests | Source mapping remains unresolved; disabled scored validation |
| NIST scientific hypothesis spec | 41973466044 / 13390463373 | 16/16 tests | Six unresolved scientific gates |
| **NIST v1 optimization** | **41977734103 / 13392975164** | **27/27; 4 policies × 3 seeds** | GP–EI outperforming BHS on these development campaigns, no significance claim |
| **NIST v2 ablation** | **41988359209 / 13397435952** | **28/28; 11 conditions × 5 seeds** | Sensitivity to BHS noise, response family and GP lengthscale; v1 reproduced |
| **NIST v3 model adequacy** | **41992614426 / 13397919991** | **31/31; 900 one-step forecasts** | Severe undercoverage of nominal 90% intervals in BOTH BHS and GP, worse in BHS |
| **NIST v4 miscalibration decomposition** | **42046318788 / 13425230747** | **36/36; 540 prequential diagnostics** | Variance components, distance/phase error and hypothetical extra dispersion; v3 reproduced |

### v1 fixed (3 development seeds, 15 acquisitions; mean normalized final simple regret, smaller better)

| Policy | Real NIST development regret |
|---|---:|
| gp_ei | 0.025001283 |
| gp_ucb | 0.074502920 |
| bhs_bma_ei | 0.139245938 |
| random | 0.197756085 |

### v2 fixed (5 already-explored development seeds; 15 acquisitions)

| Policy / post-hoc condition | Mean normalized final simple regret |
|---|---:|
| gp_ei_length_0p40 | 0.000000000 |
| gp_ei | 0.015000770 |
| gp_ucb | 0.044701752 |
| bhs_bma_sigma_0p05 | 0.053905706 |
| bhs_bma_ei | 0.083547563 |
| bhs_interaction_ei | 0.095860561 |
| gp_ei_length_0p12 | 0.099991993 |
| bhs_bma_sigma_0p30 | 0.144989376 |
| random | 0.183992856 |
| bhs_localized_ei | 0.212957226 |
| bhs_linear_ei | 0.214775352 |

**Interpretation:** GP–EI lengthscale 0.40 scored 0 on these five *already-developed* trajectories, but was considered after v1 and therefore is **not** independent state-of-art validation. Single BHS `interaction` model did better than the `linear` and `localized` alternatives; original BMA did not beat GP–EI. BHS sigma=.05 lowered regret but worsened probabilistic coverage; none of these are measured instrument sigmas.

### v3 — prequential predictive distribution quality

- 3 selector policies (`random`, `gp_ei`, `bhs_bma_ei`) × 5 forecasters × 5 developer seeds × 12 *pre-reveal* forecasts = **900** score records, aggregate-only. Each cell: n=60. This is adaptive development, no independent holdout.
- Nominal 90% predictive interval *empirical coverage* for original GP(.22) vs BHS-BMA(sigma .15):

| Acquisition trajectory | GP(.22) | BHS–BMA(.15) | GP NLPD | BHS NLPD |
|---|---:|---:|---:|---:|
| bhs_bma_ei | 0.483 | 0.333 | 14.578 | 67.786 |
| gp_ei | 0.433 | 0.167 | 47.561 | 232.048 |
| random | 0.433 | 0.283 | 57.629 | 242.955 |

- Both undercovered the adaptive evaluated points; BHS more severely. Strong residuals on a standardized response scale; normalized using first three observations only. GP(.22) is not perfect; BHS has major model-adequacy issue. For BHS sigma=.05, 90% coverage only ~5–8.3% on these tracks. A strong posterior on a functional family is not evidence for a physical mechanism.

### v4 — variance decomposition and exposure to distributional shift

- 3 acquisition trajectories × 3 forecasts × 5 existing seeds × 12 acquisitions = **540** diagnostics; verified 36 tests and v3 parity.
- On **random** trajectories, original BHS–BMA average predictive variance components in initial-observation-standardized response squared units: nominal noise **0.02250000**, within-family **0.01986554**, between-family **0.00167423** = total **0.04403976**. A small between-family term is a *diagnostic observation*, not a proven causal explanation.
- In random trajectories, BHS–BMA (sigma .15) NLPD by nearest *anonymous composition* distance: near **12.82**; middle **147.23**; far **449.55**. Unequal bin sizes and adaptive selection matter.
- On random tracks, *post-hoc* additive discrepancy SD 0 / .5 / 1 / 2 raised BHS–BMA empirical 90%-interval coverage from **28.3% / 55.0% / 68.3% / 76.7%**. **Do not treat arbitrary interval widening as calibration success**; this is sensitivity analysis.
- Diagnostics do not identify true lab noise. The modeling ingredients, posterior selection and misspecification are intertwined; no independent statistical confirmation or physical causality.

**Exact aggregate JSON archives:** `research/verified_results/*.json` (one per real CI run); combined immutable-context copy `research/BHS_V1_V4_AGGREGATED_RESULTS_SNAPSHOT.json`. These safeguard against the 30-day GitHub Actions artifact retention interval. Keep raw material data out.

## 7. Scientific truths, unknowns and hard rules

- **Verified:** source-pinned real data load, actual retrospective historical replay on 921 eligible candidates, 4 successful GitHub experiment workflows v1–v4, tests and exact preserved aggregated metrics; v1 parity in v2; v3 parity in v4; no explicit policy access to undisclosed labels.
- **Not verified:** Fe/Co/Ni column order, source reuse terms, true measurement uncertainty, instrument cost, laboratory action feasibility, physical mechanisms, physical materials discovery, superiority to standard BO, calibration on independently collected observations, usefulness to a paying lab, commercially defendable moat.
- **Hard prohibited:** claiming dataset physically mapped, sending original NIST rows or sampling indices to logs/artifacts, pretending an artificial cost is USD, claiming CHGNet trained, claiming external validation; operating independent holdout seed IDs **10000–10099**; changing `scored_validation_allowed` to true without reviewed authorization.
- **On results:** report unfavorable findings as carefully as favorable ones. Dataset has repeatedly influenced model/parameter selection; future in-dataset accuracy can only be *developer exploratory*.

## 8. Research history, strategic positioning and experimental principles

Originally work started in summer 2026, progressed through a packaged Python prototype and Zenodo v1.0.1 archive, README/CITATION repair, legacy tests and provenance, optional CHGNet CPU workflows, Matbench integrity/split checks, oracle/process/deadline isolation, PUCT/MCTS developments, synthetic hypothesis/belief selection/EIG cost studies, then real NIST 921-sample property optimization and model-miscalibration diagnostics. All historical claims need audit status; do **not** turn a planned experiment into an accomplished result.

Critical research pivot: **Stop indefinitely tuning the same Kerr pool after v4**. Instead identify a new permission-cleared data source **or** domain scientist with real competing physical hypotheses and physical uncertainty/costs; define the actual research objective *before inspecting fresh test labels* and strong matched baseline. Predeclare all gates and scoring metrics, retain negative results and uncertainty; then pursue genuinely separated independent evaluation after methodology review, never casually 'burn' the protected seed range. A prior candidate external-data search, source licensing and source-to-physical-feature mapping should be independently verified, not asserted from old chat excerpts.

**Research-to-value** interview milestone hypotheses are *not achieved*: ≥5 discovery interviews across ≥2 labs, one permission-cleared offline campaign, credible technical comparative advantage over strong baselines, real cost/benefit evidence and due diligence. See `research/CUSTOMER_DISCOVERY_AND_MOAT_V1.md` and `research/PUBLICATION_READINESS_AUDIT_V1.md` in the repo.

## 9. Next meaningful experiment / v5 staging, without pretending to have done it

**BHS External Scientific Validation Strategy v5** should not merely add a static check. First deliver a verified *dataset and scientific-question feasibility matrix*, including license, candidate+label semantics, physical rival hypotheses if relevant, measurement error, costs, real-world expert utility and stronger baselines. Decide explicitly whether v5 tests (A) model identification/experiment discrimination or (B) property optimization; never confuse these objectives. Once a fit-for-purpose **unseen external source** and domain-expert validation are available, freeze protocol **before any source labels are used for tuning**. Use held-out external entities/labs/batches where feasible, not repeatedly recycled seeds. Include uncertainty adequacy and abstention as first-class metrics; separate acquisition utility and prediction accuracy; distinguish predictive interval widening from legitimately calibrated probability.

Possible paper framing is a *hypothesis-centric experimental decision framework with robustness and honest failure analysis* — conditional on actual positive, externally meaningful evidence; an equally valuable research outcome might be a well-supported negative result or limitation study. Commercialization and PhD outreach should reflect true scope.

## 10. New-chat operation and source of truth

- Suggested new chat: paste or attach `research/BHS_NEXT_SESSION_PROMPT.md` or `research/BHS_NEXT_CHAT_START_HERE.md`; have the assistant open this exact GitHub repository via the GitHub connector and read this master file; upload the backup archive as fallback when connector not present. **The new chat will not automatically inherit every old message or hidden reasoning.** A transparent, source-pinned handoff can preserve the actionable project state, not an impossible guarantee of literal zero conversational loss.
- GitHub branch is authoritative for actual code, current tests and workflows. Current historical pin is `c540a3dbc05f527e4a360deecb310bde68b2c47c`. Newer commits require new verification.
- Every verified CI scientific milestone: update `research/BHS_PROJECT_HANDOFF.md`, `research/BHS_EVIDENCE_REGISTER.json`, archive aggregate result JSON and hashes, check safety flags, and make next research decision explicit.
- Full project source at GitHub includes many old/legacy files. This backup is **not** a substitute for a full `git clone --mirror` and is deliberately not repackaging third-party raw benchmark material. See `BHS_BACKUP_SCOPE_AND_VERIFICATION.md` for limits and instructions.
