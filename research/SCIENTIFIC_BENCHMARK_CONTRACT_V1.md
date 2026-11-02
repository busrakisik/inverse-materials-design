# BHS Scientific Benchmark v1 — Contract Gate

**SYNTHETIC_CONTRACT_ONLY / NOT_SCORED / NO MATERIALS PERFORMANCE CLAIMS**

This checkpoint supplies deterministic synthetic generators for five preregistered scenario names, reference uniform-without-replacement and fixed descriptor-greedy policies, and a query-budgeted evaluator. It deliberately does not implement BHS or produce performance comparisons. The evaluator is a trusted **in-process Python object**, not a confidentiality or security boundary. Policies executing in the same Python interpreter could introspect the evaluator and access labels; therefore use only audited, trusted policies with fabricated task labels. No hidden materials dataset, real test labels, or external secrets may be used here.

The generators are **provisional engineering fixtures**, not a frozen scientific generator specification. They require mathematical review and version/hash freezing before any scored preregistered experiment. The 'uninformative' scenario has constant public descriptors. The 'mismatched' scenario supplies sign-reversed public and utility association. This gate intentionally returns trace outcomes and a `scored_benchmark: false` marker for test assertion, not as publication results. `public_view()` exposes no labels to policy arguments; it is not a secure isolation guarantee. Do not merge to main or create a Zenodo release based on this gate.

Next: independent design review and freeze of the exact generator, descriptor semantics, oracle interface, preprocessing, development/holdout seeds and baselines; implement genuine BHS Bayesian-only policy; then use an out-of-process host with validated sandbox for any real held-out benchmark.
