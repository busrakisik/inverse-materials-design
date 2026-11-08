# BHS v12.11 — First externally sourced laboratory feasibility audit

**8 November 2026. Public university-source review only.** No external investigator has approved or accepted this study; no message has been sent and no physical measurement, Fe–Co–Ni synthesis, performance benchmark or new holdout was conducted.

## Exact provenance and software verification

- Source branch: `bhs-v1211-external-lab-evidence-gate`, implementation commit `48c28abacf5cf9daf75e210024e645441834e280`.
- Pre-recorded protocol: `research/BHS_V1211_LAB_FEASIBILITY_PROTOCOL.md`, Git blob `c8eac6886014e85cbc07112e88882138840746a5`.
- Six-source official dossier: `research/BHS_V1211_GTU_PUBLIC_CAPABILITY_DOSSIER.json`, Git blob `5dc299fccc76adc3266c53851999f35b790b9b3e`, raw SHA-256 `aabe871f11d5b1d4acdaf5808a8da42fddb2f1750623da33db1ef57be79ec687`.
- Offline checker: `scripts/bhs_v1211_external_feasibility.py`, Git blob `c1222c8c6383dcb5660476714825d7a8c6fd6c4d`.
- Adversarial CI test file: `tests/test_bhs_v1211_external_feasibility.py`, Git blob `357987792c8d7094a1ca46d56c917b6be314588c`.
- GitHub Actions https://github.com/busrakisik/inverse-materials-design/actions/runs/42487372034: **SUCCESS, 196/196 software tests** (181 inherited, 15 new). Original run artifact ID `13620480246`.
- Original result JSON SHA-256 `f49d6fe18b61e6130d7f1f8212d7ec6417be4b24f3c610338b6cbc4719d58671`, size **1,913 bytes**, Git blob `464ddd8eb9c8cd238349a0062194abdbd4262860`. The byte-identical JSON is retained in this evidence archive at `research/BHS_V1211_FIRST_EXTERNAL_LEAD_AUDIT.json`.

## Substantive findings, with source dates

**Most relevant lead:** Gebze Technical University (GTU), Gebze, Kocaeli, Türkiye.

| Evidence | Official source and date | What it does — and does not — support |
|---|---|---|
| Laboratory inventory | [GTU Nanomagnetism and Spintronics Laboratory](https://www.gtu.edu.tr/icerik/2676/758/display.aspx), updated **2025-09-29** | Lists magnetron sputtering, XRD, MOKE. Current operability, Fe–Co–Ni suitability, accessible slots and permission are unknown |
| Contemporary directory | [GTU Physics laboratory index](https://www.gtu.edu.tr/en/kategori/4270/0/display.aspx), updated **2026-07-01** | Names Erdem Demirci under the MOKE Laboratory; role ownership must be directly confirmed |
| Historical conflicting page | [Older GTU MOKE page](https://www.gtu.edu.tr/en/kategori/1658/0/display.aspx), updated **2015-06-29** | Lists Numan Akdoğan as responsible and Erdem Demirci among staff; do not infer this is the current contact chain |
| Prior experiment report | [GTU 2025 graduate symposium abstracts](https://www.gtu.edu.tr/fileman/Files/UserFiles/fbe/GTU%20Semp_Bildiri%20%C3%96zet.%20Kitap%C3%A7%C4%B1%C4%9F%C4%B1_2025%20%281%29.pdf), **2025 symposium** | Murat Kol, Erdem Demirci, Perihan Aksu and Mustafa Öztürk report sputtered **Co/Mo** bilayers characterized by XRD/XRR/XPS and VSM/MOKE. This was **not** Fe–Co–Ni validation |
| Institute contact | [GTU Nanotechnology Institute administration](https://www.gtu.edu.tr/en/kategori/2774/0/yonetim.aspx), updated **2026-04-16** | Lists Leyla Çolakerol Arslan as director and public institutional address `lcolakerol@gtu.edu.tr`; no consent or partnership established |
| Published service categories | [GTU Physics analysis services](https://www.gtu.edu.tr/kategori/3778/0/display.aspx), no explicit source date | Lists room-temperature MOKE and metal-film deposition services; actual availability and fees need direct confirmation |

Six pages from **one institution are not independent confirmatory experimental sources**. A published equipment listing and historical materials study are encouraging grounds for an inquiry, not verified performance or approved data access.

## Frozen first result and unresolved prerequisites

- **Documented public evidence entries:** 6
- **Publicly listed technical families:** MOKE; XRD; magnetron sputtering
- **Unverified external feasibility requirements:** 15, including processing assignment unit, reproducible material synthesis, Fe/Co/Ni composition and thickness, current instrument calibration/operability, independent batch preparation, supervised safety, data rights, outcome-free prospective splits, actual costs, and meaningful effect/precision
- **Historical personnel-role ambiguity:** unresolved
- **Direct inquiry sent / response received / study accepted:** **no / no / no**
- **Physical measurements performed:** no
- **Software conclusion:** `DOCUMENTED_LEAD_ONLY_NO_GO_PHYSICAL_EVALUATION`

The offline tool checks that public-source evidence has not been silently upgraded; it cannot live-query equipment or verify authentic approvals. The 196 software checks are **not** a physical discovery or calibrated uncertainty study.

## Minimum first-contact feasibility agenda

Request a brief discussion with the institute/laboratory owner, not immediate permission to conduct experiments. Ask: Can GTU presently fabricate or access **Fe–Co–Ni** thin films at composition-verified coupon positions? What physical processing parameter, if any, can be varied at coupon versus shared postprocess versus whole deposition-run level? Are current MOKE, XRD and sputtering systems operating with original trace retention, calibrated fields and scientific supervision? Can independent runs, specimen composition/thickness checks, true material/time costs, access terms and safe operating procedures be discussed? If this material system is unsupported, what *scientifically appropriate* magnetic-film system can the lab actually study?

Do not claim that the inquiry has been sent; no reply, visit, collaboration, sample ownership or source license has been obtained.

## Research decision and gates

Proceed only to **human-directed, non-operational feasibility inquiry**. If no qualified collaborator or access is confirmed, retain explicit abstention and revisit physical hypotheses without claiming progress toward independent validation. The scientific sequence is: agree a feasible materials question; verify independent treatment unit and instrument provenance; freeze the effect, uncertainty, response budget, comparator methods and group split; only then acquire prospective physical evidence under qualified supervision.

V11's negative comparator evidence, nonpassing original V12 historical replay and V12.3–V12.10 mixed/no-go findings remain untouched. The public default, previous draft review requests, historic release tags and protected seeds `10000..10099` were not modified.

**Gates:** `current_feconi_specific_feasibility_verified=false`; `lab_consent_verified=false`; `physical_validation_by_bhs=false`; `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`; `independent_physical_validation_established=false`; `real_savings_measured=false`; `claim_of_superiority=false`.
