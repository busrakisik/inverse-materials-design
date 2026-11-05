# BHS — Project Handoff / Single Source of Continuity

**As of:** 2026-11-05 (Europe/Istanbul)  
**Repository:** https://github.com/busrakisik/inverse-materials-design  
**Working branch:** `bhs-scientific-audit`  
**Last confirmed HEAD (before v3 upload):** `3a6762c7a5de1ecab7587ab1b938108bb5d9f8f5`  
**Latest verified workflow (before v3 upload):** NIST Diagnostics & Ablation v2, https://github.com/busrakisik/inverse-materials-design/actions/runs/41988359209 — **28/28 passed**, artifact ID `13397435952`. **v3 locally prepared, not yet run in GitHub CI.**

This file captures the verifiable state as of the date above; later repository changes must be rechecked rather than inferred from these notes.

## Project thesis

Bayesian Hypothesis Search (BHS) is an exploratory hypothesis-centric framework for selecting observations and updating competing Bayesian beliefs. Ultimate ambition: (1) publishable scientific results, (2) validated real laboratory/user problem, and (3) defensible technological advantage. It is **not yet** demonstrated to identify real material mechanisms, discover physically validated materials, beat standard Bayesian optimization, or save real experimental money.

Initial research release: Zenodo DOI `10.5281/zenodo.21761835` (may predate current branch).

## What demonstrably works

1. Synthetic Bayesian inference, hypothesis-model probabilities and selected numerical-reference checks; tests across several independently checked work packages.
2. Three multivariate *phenomenological* composition–response families (not verified physical explanations): `linear`, `fe_co_interaction`, `localized_response`, with sequential conjugate Gaussian posterior and independent batch comparison; CI 20/20 at https://github.com/busrakisik/inverse-materials-design/actions/runs/41969276576 (commit `ede543d220e9b86c24d4f3ed997d9e8028f7d830`).
3. Real NIST Fe–Co–Ni `*.mat` file can be downloaded/pinned/parsed in CI; **921 inferred samples**; descriptive inspection CI 20/20 at https://github.com/busrakisik/inverse-materials-design/actions/runs/41968361627.
4. Real-source mapping audit checks array shapes and plausible fraction/percent scaling; **does not certify chemical element column order**. CI 23/23 at https://github.com/busrakisik/inverse-materials-design/actions/runs/41970917911.
5. Written hypothesis specification: primary development target `Kerr` (mrad); secondary `Coer` (mT); 3 candidate *mathematical response* families; 6 unresolved gates. CI 16/16 at https://github.com/busrakisik/inverse-materials-design/actions/runs/41973466044.
6. Prior synthetic policy comparisons, mathematical reference, reliability tests, calibration and other audit modules, with no scored holdout or real performance claim.


## Verified empirical development results and next prepared step (2026-11-05)

**v1 offline Kerr replay:** Commit `aaa70761cf97b8d5ed5360ed5991ac73669b746b`, run `41977734103`, artifact `13392975164`, tests 27/27, 921 eligible rows, 4 policies × 3 development seeds × 15 acquisitions. Developer-only mean final normalized regret: GP-EI .025001283117256388, GP-UCB .07450292037487553, BHS-BMA-EI .13924593765076626, random .19775608454202978.

**v2 post-hoc diagnostic ablation:** Commit `3a6762c7a5de1ecab7587ab1b938108bb5d9f8f5`, run `41988359209`, artifact `13397435952`, tests 28/28, 11 conditions × 5 explored seeds × 15 acquisitions. Five-seed mean final normalized regret: GP-EI fixed .22 ~.015001; GP-EI post-hoc .40 = 0.0; BHS-BMA-EI sigma=.15 ~.083548; BHS-BMA-EI sigma=.05 ~.053906; random ~.183993. Original v1 3-seed results were reproduced with error below 1e-9. **These parameters and seeds are all development-only. No independent performance conclusions.** The complete v2 artifact is source of truth for all other variants and paired budgets.

**Next v3 prepared (NOT YET verified by GitHub):** `scripts/nist_model_adequacy_v3.py`, `tests/test_nist_model_adequacy_v3.py`, `research/NIST_MODEL_ADEQUACY_V3.md`, workflow `bhs-nist-model-adequacy-v3.yml`. Synthetic local tests 31/31. The CI is designed to run 3 fixed acquisition histories (`random`, `gp_ei`, `bhs_bma_ei`) × 5 predictive models × 5 already-seen development seeds, reporting one-step-ahead NLPD, RMSE, 90% mixture predictive interval coverage and PIT diagnostics. It must not use independent holdout or raw labels in artifact. **After user uploads, verify HEAD, GitHub Actions status, report checksum, numeric results, limitations and archive. Never claim a v3 real-data outcome before seeing CI artifact.**

**Research decision:** We have a working real-data retrospective *optimization* sandbox, not established physical hypothesis identification. Test whether BHS predictive distributions are misspecified or overconfident under the original GP baseline and adaptive trajectories. Avoid endless post-hoc tuning to make BHS appear superior; if BHS loses, state so. Retain external expert review and separate evaluation data as scientific prerequisites.

## Source pinned exactly

- Official NIST REMI repo: https://github.com/usnistgov/remi
- Branch `nist-pages`, commit `596b04435fb577175264a70c4434f5539b809510`.
- File `data/Combinatorial Libraries/Fe-Co-Ni/FeCoNi_benchmark_dataset_220501a.mat`.
- Git blob SHA-1 `e506db115d522d62618042abead7df2695ccf13e`; bytes `289480`.
- Metadata `data/Combinatorial Libraries/Fe-Co-Ni/data description.txt`: `C`=composition; `XRD`=diffraction; `TTH`=two-theta; `Coer`=coercivity mT; `Kerr`=Kerr rotation mrad.
- Required citations: Wang et al. (2022), *Benchmarking Active Learning Strategies for Materials Optimization and Discovery*, doi:10.1093/oxfmat/itac006; Yoo et al. (2006), *Identification of amorphous phases in the Fe–Ni–Co ternary alloy system using continuous phase diagram material chips*, *Intermetallics* 14, 241–247.
- Paper: https://academic.oup.com/ooms/article/2/1/itac006/6637521
- NIST publication: https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery

## Strong scientific cautions

- **Never assume `C[:,0] = Fe`, `C[:,1] = Co`, `C[:,2] = Ni` without independent source documentation.** Row sums near 1 or 100 do not establish element order or atomic-percent semantics.
- The dataset is a **retrospective property-optimization benchmark** of magnetic properties, not labels of true causal physical hypotheses. BHS's model probabilities compare chosen functional forms; do not market them as discovery of physical mechanisms.
- The original paper benchmarks Gaussian-process acquisition methods and reports Expected Improvement strong overall performance. New work needs genuinely competitive EI/GP and other baselines, not only random/greedy or weak toy baselines.
- Per-sample experimental measurement uncertainties, real per-experiment costs and data redistribution permissions are not verified. Any fixed Gaussian sigma and cost values must be openly *hypothetical sensitivity assumptions*, never measured facts.
- Treat the six gates in `research/NIST_SCIENTIFIC_HYPOTHESIS_SPEC_V1.json` as unresolved unless confirmed in new evidence. Actual tests do not resolve a gate automatically.
- Do not redistribute raw NIST data in committed files/artifacts while reuse review is unresolved.

## Hard no-overclaim rules

`scored_validation_allowed = false`  
`independent_holdout_used = false`  
`physical_validation = false`  
`dataset_ready_for_bhs = false` (until explicitly supported)  
Never use BHS independent holdout seeds **10000–10099**. No claims of physically validated materials discovery, outperforming baselines, calibrated instrument uncertainty or real monetary savings. CI pass = execution/testing, not scientific superiority.

## Research priority: avoid endless 'gates' and redundant modules

**A. Resolve the highest-impact data blocker.** Look for definitive author-provided mapping of the three `C` columns to Fe/Co/Ni (paper supplement, original code, author response). Cite line/figure/code evidence. If none, mark *unresolved*, prepare concise author inquiry, and do not guess. In parallel extract *only aggregate* target and composition missingness from the existing CI artifact to quantify usable data.

**B. Choose the empirical task explicitly.** Recommended first defensible empirical task: *retrospective composition→Kerr property-optimization benchmark*, while preserving BHS hypothesis-discrimination as a longer-range aim. Do not describe purely mathematical shape families as rival physical mechanisms.

**C. Pre-register a leak-proof development protocol** (not independent holdout): fixed candidate pool; transparent seed partition without 10000–10099; fixed initialization, budgets, missing-value policy, noise-sensitivity grid, target transformation; same measured values for all policies; labels hidden until each query; direct comparisons to GP-Expected Improvement, random, GP-UCB, and potentially GP Thompson sampling; use regret/sample efficiency and predictive prequential metrics. Distinguish selection-bias from physical measurement uncertainty. Non-independent development results must be marked exploratory.

**D. Implement one integrated offline experiment**, not another static metadata-checking module, **only after** verifying proper column semantics or finding a scientifically safe anonymous-composition task clearly separated from element-named physical claims. Check suite and artifact from actual CI and report effect sizes and limitations.

**E. Seek external scientific review** of hypothesis meaning, model misspecification, uncertainty calibration and practical use. Publication/manuscript is conditional on independently reproducible substantive results.

## Workflow when continuing with ChatGPT

1. Read `BHS_PROJECT_HANDOFF.md`, `BHS_NEXT_SESSION_PROMPT.md`, `BHS_EVIDENCE_REGISTER.json`.
2. Verify current branch HEAD, latest workflow status + artifact before making claims.
3. Read relevant actual GitHub source, not just past assistant summaries.
4. Make a specific scientific advance or prepare one compact code+tests+workflow+research-note ZIP; test locally and provide exact artifact paths. If the user says “dosyaları yükledim,” check GitHub files and Actions before new development.
5. If source verification is blocked, identify the blocker and propose an independent alternative, not a fictitious successful analysis.

## Conversation continuity

A new ChatGPT conversation can restart from the live GitHub repository plus these files; the chat history need not be replayed. Keep this handoff in the repo under `research/BHS_PROJECT_HANDOFF.md` and update after milestones. Current-session user asked whether chat limit is near; actual remaining chat-context or message quota cannot be determined precisely from the conversation.
