# BHS V12.20 — First 2024 Campaign Decision-Time and Missing-Counterfactual Source Audit

**13 November 2026 | Source catalog and archived software analysis only | First explicit NO-GO verdict.** This does not contain or evaluate a single original measurement from the 2024 campaign; no original `CampaignData.csv` file, recorded Instron force curve or newly selected experiment was acquired.

## 1. Why this domain might matter, and the honest first blocker

Snapp et al., *Nature Communications* **15**, 4290 (2024), DOI `10.1038/s41467-024-48534-4`, describes a self-driving laboratory for 11-parameter generalized cylindrical shell (GCS) designs over seven polymers. The article reports **25,387 attempted experiments, of which 13,250 provided valid data**. Those counts are from the published **paper**, not a file newly read or reanalyzed by BHS. The difference of **12,137** represents unsuccessful/excluded/other records as reported in the aggregate; without original source QC fields, do NOT automatically label every one of those records a single physical failure class.

The institutional source `https://open.bu.edu/items/871d47cb-a12c-4ebb-8623-92df97353ea9` (BU handle `2144/46687`) indexes `CampaignData.csv` (7.54 MB), `FilamentData.csv` (13.36 KB) and individual experiment Instron archives including `ADTS1-4999.zip` (680.37 MB), `ADTS5000-9999.zip` (625.38 MB) and `ADTS10001-14999.zip` (645.86 MB). The archive explains that `Valid` marks data accepted for model training and that **not all parts have mechanical trace files because some were never tested**. The item description also refers to `Dataset.csv` generically while the indexed inventory says `CampaignData.csv`. Neither true source header, CSV row identities, ZIP members, file checksums nor column mapping were verified in this study. **Do not silently equate filenames, invent missing curves or claim source bytes were ingested.**

Separately, the original authors' published paper documents **human interventions**, changes to available materials, changes to feature/design support, and several evolving experiment-selection policies. A globally fixed candidate set and a stable logging policy across the entire campaign are scientifically unsupported. An experiment integer `ID` is not by itself a timestamp; multiple printers and a downstream machine/queue create asynchronous decision and observation times.

## 2. Two separate kinds of originality and rights

Official MATLAB research laboratory control snapshot `KelseyEng/BEAR_ADTS` (GitHub repository numeric ID `676572978`, pinned inspected commit `621d294e2df6b7c7156f0f72dab4ec39c168fd0f`) documents:
- `selectExperiment.m` Git blob `4ca861776a81321ddbcd4b80775b46f831d252c8`: designs, printing, filament availability, calibration and changes in active printer decisions
- `savePrintInfoToDataT.m` Git blob `3b6fa2b3e40a2ed582b9107a02321027711ecdc8`: design/printer/filament metadata saved as a plan/printing entry
- `processData.m` Git blob `755f885f1577d36cd4257f924c92601d080f3330`: computes height, stress, toughness and energy-absorption information AFTER physical force–displacement observations
- `checkPrevData.m` Git blob `49ab113c7eef233062abcd4a9058bb61a851f047`: backfills some rows using earlier experiment IDs. This matters: the *final publication CSV* may reflect information that was not present in the original decision snapshot.
- `decideExperimentDispatcher.m` Git blob `b9565ec2fb719f3804c2b09ecd771127cb302312`: external GP modeling/decision tasks with temporal inputs. A published software snapshot does NOT prove actual runtime logging, original data snapshot timestamps or policy propensities for each historical decision.

The independent GCS shape library's source README, Git blob `cfff28992112224610b4b9ef49c7e876e5e8f054`, pinned inspected commit `a5b784f0fe2d93d72bd67f7390df0ca44b1279c2`, lists the **11 conceptual design recipe variables** `c4_base`, `c8_base`, `c4_top`, `c8_top`, `twist_linear`, `twist_amplitude`, `twist_cycles`, `perimeter_ratio`, `height`, `mass`, `thickness`. These are code-level geometry design field names; **we have NOT proven their exact 2024 `CampaignData.csv` column spelling, source derivation, or visibility in every historical policy snapshot**. Nominal target mass and height are different from measured as-built quantities.

**Rights:** The institutional experimental **dataset** is listed as `CC BY-NC-SA 4.0`, while the historical **MATLAB software** GitHub repository is marked `Unlicense`. These permissions do not transfer between sources. Commercial use is NOT approved by the data license, and a private customer-facing or closed redistribution plan would require rights review/permission before use. No third-party source data were redistributed.

## 3. Frozen first source-only contract and authentic run

Research protocol `research/BHS_V1220_ADTS_DECISION_TIME_PROTOCOL.md`, Git blob `e8627160d67afba65d95c21aa9f68268117483d7`, was frozen **AFTER transparent public source/code inspection and BEFORE first V12.20 implementation/tests**. This is not a blinded registration against a never-examined source and makes no claim of original data discovery.

First source-only stage contract `scripts/bhs_v1220_campaign_decision_time_gate.py`, Git blob `1ea9891b554668076ffe4bd8edc799b20eee6031`; 28 new adversarial tests `tests/test_bhs_v1220_campaign_decision_time_gate.py`, Git blob `aea4619cb7c1ddc30ddd3ede079764aeee1a944f`.

First GitHub CI [43443412679](https://github.com/busrakisik/inverse-materials-design/actions/runs/43443412679) **SUCCESS: 228/228 software checks**, comprising 28 new +24 V12.19 +25 V12.18 +18 V12.17 +13 original V11 +120 inherited source contracts. No external data download and no candidate response scoring occurred.

First produced source-only JSON `bhs_v1220_first_campaign_decision_time_no_go.json` **4,338 bytes**, original GitHub artifact ID `14047825214`, SHA-256 **`40d81c21930a43869c1d0d4e1d1024b15f8cd004f573d124381225b7cd411341`**. That exact source-only report carries NO 2024 measured values and keeps the original status `NO_GO_ADTS_2024_POLICY_TIME_AND_COUNTERFACTUALS_UNVERIFIED`.

## 4. Distinguish decision stages and forbid future outcomes as inputs

At the experiment *selection* moment, the 11 geometry recipe choices and preexisting loaded printer/filament could in principle be known from a time-stamped selection snapshot. The present source only documents that general process; it does NOT independently authenticate access for each recorded historic action. Prior filament calibration may be known **only to later decisions after its genuine earlier measurement**.

After committing to printing, actual mass becomes measurable, but is not a free feature of the initial candidate. After Instron testing, force–displacement, height inferred from the trace, toughness, maximum stress and energy efficiency become observations; only a **finished/previously revealed** test's values may update the next posterior. After quality review, `Valid` and failure/exclusion status are known; the experimental action and resource expense must remain in the ledger even if the final label is unusable. An all-success-only evaluation that silently filters invalid records is selection bias.

The first stage gate rejects future `toughness_j`, `efficiency_ks`, `force_displacement_trace`, `valid`, future calibration data, post-campaign ranks and physically irrelevant decision-policy IDs in candidate design views. It also checks strictly timezone-aware chronology in **manufactured** events, rejecting a result visible before its actual synthetic reveal time. Even a well-formed synthetic timestamp has **no independently authenticated real source chronology**; there is no automatic promotion to scoring.

## 5. The fundamental obstacle remains even after a future CSV download

A historic adaptive lab records outcomes for the **specific designs it actually tested**, not the physical responses to all other designs that a new BHS, GP or RF policy might have chosen. This is the **missing-counterfactual problem**. A new policy selection cannot be credited with the true experimental response of a design the laboratory did not perform.

The published laboratory policies and candidate ranges changed during the study, with human interventions, material constraints and printer availability. The action support and historical action probabilities are not independently authenticated. Thus even after valid source file access, arbitrary **offline policy acquisition regret** is not identifiable without a defensible prospective experiment, or a scientifically valid logged policy evaluation scheme whose support, propensities and assumptions are verified. A retrospective surrogate trained on final outcomes cannot prove true physical savings. A future independently disjoint **prediction** study is a different potential claim, NOT a prospective sequential BHS selection benchmark.

No new physical failure mechanism, actual material gain, autonomous research superiority, calibrated scientific likelihood or economic benefit was established.

## 6. Previous negative outcomes remain unchanged

Original 2020 V11 physical historical, **statistical component only**: equal 16 designs/48 acquired responses per developmental campaign; mean regret GP–ARD EI **7.363 J**, RF–UCB **8.983 J**, inherited BHS v5 portfolio **9.368 J**, random **15.951 J**. Old BHS component was worse than both strong references, not an independent full BHS assessment. V12.18 initial mathematically weak synthetic model discrimination (**2.947743603209929e-6 nats**) remains unchanged; V12.19 original 2020 trace mapping remains NOT VERIFIED. No old results revised or hidden.

## 7. Outcome and next useful source dependency

**`NO_GO_ADTS_2024_POLICY_TIME_AND_COUNTERFACTUALS_UNVERIFIED`**; all scoring, source-file admission, physical mechanism, independent holdout and commercial-rights gates remain FALSE. Do not merge previous draft pull requests, change default public main, rewrite first test histories or use protected NIST seeds `10000..10099`.

Next source evidence with genuine value: obtain exactly versioned `CampaignData.csv` and `FilamentData.csv` bytes with official archive digest; examine column NAMES and per-record experiment ID/chronology in a newly frozen source audit before ever using outcomes; confirm mapping to raw `ADTS#.csv` files and which events were selected, printed, weighed, tested and reviewed. Ask source authors for **historical decision snapshots, candidate support/eligibility, changes of policy, policy propensities if recorded, and origin of target-mass/filament-calibration fields**. Independently vet the non-commercial dataset terms. Only then can a scientifically defensible first research question (possibly prediction rather than acquisition) be designed. No email has been sent in this phase.
