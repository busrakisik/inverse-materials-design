# BHS V12.17 — Independent mechanism-identifiability limitation in the V11 physical source

**13 November 2026. Source schema and scientific-paper provenance only; no new material outcomes or model scores. This document supplements, but does not modify, the frozen original architecture-readiness result.**

## Verified five-column dataset boundary

The original recorded crossed-barrel mechanical testing dataset, independently published by `PV-Lab/Benchmarking`, is pinned at Git commit `7585c517ad88e676c42c6bf24a8ad278e01ddb21`, path `datasets/Crossed barrel_dataset.csv`, Git blob `b007fe5d8762233bbd23c8cf83858b169f05492a`, raw SHA-256 `2c01f875f3c210e986ca6142bf20f417884c2ad7d6f008c2fc574b44a3d5f606`. Its *original header* is exactly:

`n,theta,r,t,toughness`

The four design parameters `n`, `theta`, `r`, `t` specify the number of hollow struts, twist angle, outside strut radius and wall thickness **before fabrication and compression testing**, as demonstrated by Gongora et al., *Science Advances* **6** (2020), eaaz1708, DOI `10.1126/sciadv.aaz1708`. The fifth field `toughness` is **an experimental result**, not a pre-measurement input. In the actual V11 retrospective code, those four public design inputs are given to all policies and only triplicate outcomes of previously acquired geometries are revealed to each selector.

The source study physically distinguished brittle, ductile and strength-limited mechanical responses and described force–displacement curves. But the **pinned five-column benchmark file does not contain individual force–displacement traces, mass measurements, fracture-mode annotations, printer identifiers, or batch timestamps**. Those data might exist elsewhere; their availability, row-level mapping, licensing and independent provenance are **not established for BHS**.

## Why this matters for a *scientific hypothesis* engine

A toughness scalar can be identical for two very different force–displacement curves. Neither the four design parameters nor the one toughness value uniquely identifies whether an individual physical sample failed in a brittle, ductile or strength-limited mode. Thus a hypothesis such as "this design increases toughness because of progressive yielding" cannot be **falsifiably distinguished at the claimed mechanism level** using only the pinned five-column table. It can be used as a statistical conditional predictor of toughness but must not be marketed as a verified mechanical mechanism.

Consequently, this physical source is **good for retrospective component-level design-selection evaluation**, as V11 actually did, but insufficient by itself for a full hypothesis-centric physical-mechanism benchmark. The unresolved need is a traceable candidate-by-candidate supplementary source of raw compression curves, sample processing/batch identities, failure categories and realistically measured response costs, plus qualified domain review and a new independent time-ordered evaluation.

## Decision

Do not relabel kernel families as physical mechanisms or convert the absence of raw traces into a positive physical interpretation. A future BHS system can honestly run *statistical rival predictive models* of the scalar toughness observable if explicitly labeled as such, but that is not the same research claim as discovering, comparing and falsifying rival mechanical mechanisms.

No new performance experiment is authorized by these source-schema observations; all V11 negative component results, V12.16 DFT original-input mismatch, and V12.17 `FULL_BHS_NOT_EVALUABLE_YET_EXISTING_COMPONENT_RESULT_NEGATIVE` remain unchanged. The three-part feature-origin, before-action and decision-time-access contract remains mandatory. Source DOI and official article: `https://doi.org/10.1126/sciadv.aaz1708`. Peer-reviewed BO benchmark: `https://doi.org/10.1038/s41524-021-00656-9`.
