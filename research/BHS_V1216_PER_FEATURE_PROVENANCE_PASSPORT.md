# BHS V12.16 — Candidate feature-by-feature provenance passport

**Frozen decision on 13 November 2026. This is an eligibility record, not a learned feature set.**

Reference source: Mai et al., *Acta Materialia* **297** (2025) 121288, DOI `10.1016/j.actamat.2025.121288`; author GitHub repository numeric ID `789358474`, exact source commit `c079fcd00cf1e085fe917d460dbc36a064155296` and compressed CSV SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`.

The columns below exist in the **original published CSV** and **each** contains 4,285 nonblank strings and 4 blank strings of 4,289 source rows. This verifies published-field existence only. It does **not** establish when the field was computed, what transformation produced it, whether the initial configuration was generated without target feedback, or whether a selector actually had the field when deciding which run to request.

| Candidate field | Published field origin | Source presence | Before expensive target DFT | Available to policy at decision | Approved |
| --- | --- | ---: | --- | --- | --- |
| `structure_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `site_z_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `dist_GB_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_CoordNo_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_tot_vol_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_tot_area_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_volumes_std_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_volumes_mean_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_volumes_min_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_volumes_max_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_vertices_std_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_vertices_mean_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_vertices_min_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_vertices_max_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_areas_std_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_areas_mean_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_areas_min_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_areas_max_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_distances_std_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_distances_mean_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_distances_min_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |
| `VorNN_distances_max_unrel` | Pinned author's CSV; field-generation timeline unverified | 4,285/4,289 | **UNVERIFIED** | **UNVERIFIED** | **NO** |

## Separate nonpredictive identities

**`GB`, `element`, `Z`** are intended *action definitions* (selected boundary/solute and elemental atomic number). They can be known before specifying a calculation and passed to all policies in an intentionally frozen experiment, but this is not proof that a historical adaptive schedule recorded such access. They alone are insufficient evidence for predictive material generalization, especially on held-out boundaries or solutes. **`site`, `GB_site`, `job_name`, `GB_element_site`** are group/row identifiers; site enumeration and input construction chronology remain unverified. `GB_element_site` has 110 missing original entries. None is accepted as an arbitrary continuous transfer descriptor.

## Explicit outputs excluded from the candidate set

`E_seg` is the expensive relaxed DFT target; `E_seg_unrel` is another computed energy, **not a free input**. Relaxed structure, DDEC6 outputs, work of separation, magnetic moments including `magmoms_unrel`, convergence or post-calculation data may not be exposed before their own calculation. All other original columns not independently approved remain DENIED, as documented in the 90-column V12.15 original source audit.

## Three-part mandatory admission and the first negative source test

1. **Origin:** published field and original primitive identity are recorded, but every derived-field creation procedure and original input lineage require more evidence.
2. **Before computation:** published `_unrel` suffix alone is insufficient. First preregistered original input versus exact `structure_unrel` example had equal cell and 41 Fe + 1 He but an atomic displacement of **0.4521222246251549 Å**, exceeding frozen **0.001 Å** matching tolerance. One archive has a separate `NSW=0` static DDEC6 workflow. No global pristine-input chronology is proven.
3. **At decision time:** complete prospective selection log and source candidate chronology are missing. Incomplete provenance cannot be patched using test outcome values.

**Decision:** all 22 conditional geometry fields remain **NOT APPROVED FOR SCORING**. No DFT BHS/GP/RF numerical benchmark, no post-result descriptor adjustment, no independent-materials performance or cost claims. The previous honest V11 kernel-only negative result remains the strongest documented component-level reference, but is not the full BHS architecture.
