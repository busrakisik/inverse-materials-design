# BHS — Real-World Benchmark Feasibility v1

**Decision: Prioritize NIST REMI Fe–Co–Ni for a permission-checked, offline feasibility pilot. NOT a scored benchmark or a validated scientific result.**

## Scope and sources (verified 2026-11-04)

| Candidate | Evidence | Fit judgment | Unresolved |
| --- | --- | --- | --- |
| NIST REMI Fe–Co–Ni | NIST open access compositional thin-film data; published active learning study with coercivity and Kerr rotation | **First pilot feasibility candidate** | Per-row records, measured-error metadata, true experiment costs, reuse rights, and valid scientific hypotheses |
| MADE (ICML 2026) | MIT-licensed framework, modular discovery oracle and budgeted agents, convex-hull objectives | **Later methods benchmark**; no adapter yet | Agent/oracle interface; different outcome (stable material discovery vs identification of known hypothesis) |
| Matbench | Experimental and computed property prediction tasks, standardized splits | **Predictive reference**, not current identification benchmark | Task-level provenance/license and target/uncertainty mapping |
| Materials Project | Computed materials property repository and API | **Domain reference**, not automatically physical measurement data | API/usage terms, contributed data rights and data-version locking |

Source URLs are recorded in `research/REAL_WORLD_DATASET_CANDIDATES_V1.json`.
Primary supporting publications:
- NIST data: https://pages.nist.gov/remi/data/
- Wang et al. (2022), NIST active learning study: https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery
- MADE, ICML 2026: https://proceedings.mlr.press/v306/malik26a.html
- MADE code/license: https://github.com/diffractivelabs/MADE
- Matbench scope: https://docs.materialsproject.org/services/ml-and-ai-applications/matbench
- Materials Project terms signpost: https://registry.opendata.aws/materials-project/

## Scientific compatibility decision
Current BHS v2 models scalar y=a*phi(x)+Gaussian independent noise with the fixed feature families linear/quadratic/oscillatory. Real composition datasets have multi-dimensional composition features. **Do not silently normalize a 3-component composition into one scalar and call this physically meaningful.** The central research question is scientific model discrimination. Need domain-supported competing mechanisms and measurement errors; otherwise label the first task as *property optimization* and explicitly redesign model and baselines.

## Pilot gates before running any real data
1. Inspect exact NIST CSV/files and accompanying data dictionaries; record source, version and SHA-256. Data has **not been downloaded in this package**.
2. Confirm terms for each selected dataset/file, including commercial reuse and redistribution rights. "Open access" alone is not a legal clearance; do not redistribute raw rows yet.
3. Determine meaning, units and missingness for measured targets; confirm per-measurement uncertainty or document that it is unknown.
4. Replace toy arbitrary cost units with measured time and consumables if available; otherwise separate labeled hypothetical cost scenarios from evidence of savings.
5. Propose scientifically defensible competing hypotheses for the material response; involve a domain researcher; freeze features and priors before evaluation.
6. Build offline oracle boundary: policy sees public candidates, permitted metadata and previously acquired labels only. Test forbidden future-label access.
7. Compare matched budgets against random, cost-only, EIG, well-implemented BO/EI, and relevant active-learning baselines. Use same target and account for unsuccessful experiments.
8. Use predeclared group/split rules (composition family, film batch, timestamp if applicable), uncertainty intervals and paired campaigns. Never use independent BHS holdout seeds 10000..10099 or assert scored validation before external approval.

## Publication vs commercial relevance
**Publication candidate**: report mathematically defined hypothesis-discrimination accuracy/cost with transparent baselines and failure cases. Real-data feasibility does not imply a publication-ready result.
**Potential customer**: laboratories with costly characterization queues and trackable outcomes, uncertainty, scheduling constraints and spending. Do not claim measured savings without audited real costs.
**Defensibility**: domain-specific hypothesis specification, leakage-safe oracle integration and verified uncertainty behavior—not the generic EIG/cost ratio.

## Code contract
This release is intentionally static: no data collection, no external dependencies, no material labels, no benchmarking. It only validates that feasibility metadata, limitations and claim gates remain explicit.

Run:
```bash
python -m unittest discover -s tests -p 'test_real_world_feasibility_v1.py' -v
python -m scripts.real_world_feasibility_v1
```

All output must report `scored_validation_allowed=false`, `physical_validation=false` and `independent_holdout_used=false`.
