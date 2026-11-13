# BHS V12.16 — Original author input failed strict one-row structural match

**13 November 2026 — first source experiment under a protocol frozen before numerical coordinates were inspected. This is a negative input-lineage result, NOT a prediction or performance benchmark.**

## Why the study was run

The owner requires written evidence of **(1) feature origin, (2) availability before the expensive calculation, and (3) accessibility at the scientific decision point**, for every proposed feature. Only after *all three* pass may a new fair BHS performance comparison be run. The V12.15 audit found 22 `_unrel` candidate geometry columns in 4,285/4,289 source rows but had not established even one complete input lineage. This study tests one author-archived example and refuses to generalize beyond one case.

Published third-party source: H. L. Mai et al., *Acta Materialia* **297** (2025), 121288, DOI `10.1016/j.actamat.2025.121288`. GitHub author source numeric repository ID `789358474`, frozen commit `c079fcd00cf1e085fe917d460dbc36a064155296`. Full original compressed data Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`, SHA256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`.

## Frozen protocol, chronology and reproducibility

- Frozen before original coordinate analysis: `research/BHS_V1216_SINGLE_INPUT_PROVENANCE_PROTOCOL.md`, blob `d3946774704d1701eccfaea7d38e7e2495d22a3f`. Original analysis code blob `bad06311d1867f3ee97824179d6437a5b89607f6`.
- First CI [43404994974](https://github.com/busrakisik/inverse-materials-design/actions/runs/43404994974) **FAILED before source experiment** because one synthetic test expected the sample-file hash check before the stronger CSV checksum check. The scientific code, test thresholds and preregistered protocol were never altered.
- Intermediate CI [43405134923](https://github.com/busrakisik/inverse-materials-design/actions/runs/43405134923) **FAILED** while a test/workflow source-hash update was incomplete. Preserve both failed runs.
- Corrected test-only source branch `bhs-v1216-starting-input-lineage` HEAD `1845ba91aa253f593c9da9c25fdbcd049b2a7aed`, first **actual source** CI [43405153576](https://github.com/busrakisik/inverse-materials-design/actions/runs/43405153576) **SUCCESS with 99/99 source, historical and adversarial software checks**. Scientific comparison **FAILED the strict geometric match**; a green workflow is NOT a positive scientific result.
- First original GitHub Actions evidence artifact ID `14027600031`: `bhs_v1216_first_one_input_lineage.json`, **2,007 bytes**, SHA256 `21e7a322f03bcdea9230e150a5a5a201ea5c0d5f092c2797fe8991997728ee8b`. Source files were not republished or numerically scored.

## First actual one-row experiment: negative result

Original archived input `Data/S11-RA110-S3-32-He-19/POSCAR.orig`, Git blob `c1b92f972db85ebbce5bf9cc8e58a4d356ee27be`; source input `INCAR.orig` Git blob `d0a1a818098b901317b1803eb20a4c1db95f54fd`. Exact single original CSV primitive identity `(S11_RA110_S3_32, He, 19)` was found; only its `structure_unrel` data were parsed. No energy magnitude, relaxed structure, response or score was read.

- Both structures contain **42 atoms: 41 Fe + 1 He**, with the **same lattice matrix** (maximum component difference = **0.0 Å**).
- Species-constrained periodic minimum-image linear assignment, fixed BEFORE inspecting actual positions, gave **maximum displacement = 0.4521222246251549 Å**, **mean displacement = 0.2361141947670401 Å**.
- Prespecified acceptance required **maximum lattice difference <= 0.001 Å AND maximum matched-atom distance <= 0.001 Å**. The first sample thus **did not satisfy** the strict geometric-equivalence test. **Never raise the threshold, reinterpret this as a pass or modify the original negative report.** The failure does not prove the two structures are fundamentally different physics: unresolved possible causes include different relaxation stages, coordinate transformations and starting-configuration definitions.

## Independent author-workflow evidence suggests different computation stages

At the SAME pinned author source commit, the archived `POSCAR.orig`, `POSCAR`, and starter input have the **same Git blob** `c1b92f972db85ebbce5bf9cc8e58a4d356ee27be`. The archived `INCAR.orig` specifies `NSW = 60` and `NELM = 120`; the accompanying current `INCAR` file Git blob `bfc6dd16ab43ade61d56acbff664fad6157c8fe2` specifies `NSW = 0` and `NELM = 300`. The author's sample script `StaticImage-DDEC6-custodian.py` blob `b61e48b66da316262a8aebd5304aa1889d501d05` explicitly overrides VASP inputs to `NSW = 0`, `LCHARGE = True`, `LAECHG = True` for a static charge/bond-order step. Its archived `custodian.json` blob `de4a88d63496c7b37bbd5e916cd58ace816e54f9` also records that override. This establishes that the **example folder contains a static post-processing workflow**, not necessarily the original pristine pre-relaxation geometry of every source row. The file name `POSCAR.orig` alone cannot certify timeline, decision-time access, or that the archived input preceded *all* expensive calculations. We do not infer a fully established stage order from these artifacts.

### Feature admissibility decision table

| Feature or evidence | Origin fixed? | Available before target expensive calculation? | Visible to policy when selecting candidate? | Decision |
| --- | --- | --- | --- | --- |
| Source `element`, `Z`, target `GB` selection | Yes, source identifiers and proposed action | Known when choosing a solute and boundary by definition | Can be provided equally to all policies in a frozen protocol | **Selection identity only; not sufficient physical prediction** |
| `site` and `GB_site` labels | Yes, source row identity | Geometry-site enumeration may be precomputed, but full site construction lineage unverified | Candidate ID is possible; numeric site indices not transferable geometry | **Grouping only** |
| `structure_unrel` | Yes, column present for 4,285 source rows | **NOT CERTIFIED**, one pinned sample fails strict archived-input geometry match | **NOT CERTIFIED**; publication is retrospective | **BLOCK predictive use** |
| `site_z_unrel`, `dist_GB_unrel` | Yes, source field names and coverage | **NOT CERTIFIED** derivation/coordinate convention | **NOT CERTIFIED** | **BLOCK** |
| 19 `VorNN_*_unrel` descriptors | Yes, source field names and coverage | **NOT CERTIFIED** that calculation is input-only, before feedback or cost-known | **NOT CERTIFIED** | **BLOCK** |
| `E_seg_unrel`, `E_seg` and magnetic moments | Yes, source results | Outputs of quantum calculations or post-processing, not free start inputs | Forbidden before the particular evaluation | **DENY** |
| Archived sample `POSCAR.orig` | Exact pinned Git blob | **NOT CERTIFIED** as original pre-relaxation input; static step archive is documented | A later published file is not a live decision-time trace | **Diagnostic only; sample mismatch** |

No global 4,289-row input lineage was validated. Genuine per-row original input generation and timing, DFT cost and convergence histories, training-only feature construction and policy-time access still require independent verification.

## What current BHS is fairly known to do

The source-pinned historical physical V11 experiment tested only inherited **BHS v5 kernel-portfolio EI**, not full hypothesis-centric BHS. The original study, with **600 distinct physical designs × 3 experimental results**, predeclared five DEVELOPMENT seeds and identical budgets of **16 unique designs / 48 historical responses** per method. Mean final retrospective regret (J; smaller is better): **GP–ARD EI 7.363**, **RF–UCB 8.983**, **BHS kernel portfolio 9.368**, **random 15.951**. Existing BHS component lost to both serious references on the average; no independent win was demonstrated. See unchanged `research/BHS_REPLICATE_POOL_V11_RESULTS.md`, blob `400ac9271dbf24f229a8b50823af773d1c0b6ea5` and original run `42347524338`.

A further domain-evidence check of Gongora et al., *Science Advances* **6** (2020), eaaz1708, DOI `10.1126/sciadv.aaz1708`, establishes the four candidate inputs `(n, theta, r, t)` are **parametric geometry definitions chosen before 3D printing and toughness measurement**. The V11 selector code `scripts/bhs_replicate_pool_v11.py`, blob `65044ae33514020f55fe6cb10f62b03a9e955a05`, passes those candidate descriptors and **only acquired** historical triplicate responses to a selector. This makes V11 substantially more credible for a *component-level retrospective comparison* than any new DFT-feature comparison with unverified input timing. But V11 used development seeds and has no independent prospective measurement or complete BHS hypothesis architecture.

## Non-negotiable decision / next useful research work

**NO-GO FOR ANY NEW SCORED BENCHMARK.** First resolve which pristine DFT input corresponds to `structure_unrel`, with a traceable original-generation stage for each intended candidate. The static DDEC archive is **not** evidence for that stage. For a *complete BHS* comparison, first audit actual scientific hypothesis representations, sequential updates, action semantics and matched reference policy inputs; distinguish the existing v5 statistical portfolioworker from a full scientific hypothesis engine. Choose a genuinely suitable domain and lock a separate prospectively valid protocol before a single new performance number.

Even a future perfect one-sample geometric match cannot independently certify all source records. Preserve all original negative results, NIST reserved seeds `10000..10099`, and original draft/unmerged PRs. All gates remain `development_only=true`, `scored_validation_allowed=false`, `precalculation_geometry_certified=false`, `policy_time_access_certified=false`, `full_4289_row_input_lineage_certified=false`, `real_cost_verified=false`, `independent_holdout_used=false`, `claim_of_superiority=false`, `physical_validation_by_bhs=false`, `laboratory_action_allowed=false`.
