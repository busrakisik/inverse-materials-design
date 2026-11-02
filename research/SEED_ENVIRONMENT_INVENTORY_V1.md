# BHS Seed & Environment Inventory v1

**STATIC_INVENTORY / NOT_FROZEN / NO_HOLDOUT / NO_PHYSICAL_CLAIMS**

This is a **read-only, metadata-only static inspection** of tracked text files. It records probable hard-coded `seed`, `seeds`, `rng_seed`, `random_state`, and `range(...)` expressions, and flags literal overlaps with proposed validation IDs 10000–10099. An overlap can be a harmless mention in documentation. Conversely, no overlap is **not evidence** of seed independence.

## Reproduce
`python -m unittest discover -s tests -p 'test_seed_environment_inventory_v1.py' -v`
`python -m scripts.seed_environment_inventory_v1 --out-dir runs/seed_environment_inventory_v1`

The artifact includes inventory.json and inventory.sha256. It does **not** execute `make_task`, evaluate Bayesian or baseline policies, read hidden outcomes, lock dependencies, or approve validation. An independent reviewer still needs all old CI artifacts, manually executed seeds, untracked files, historical commits, off-repo notebooks and tuning logs. If any proposed seed was previously seen, discard the set before validation. For reproducibility, create an externally reviewed dependency lock or pinned digest and document runtime hardware before confirming the freeze.

The inventory is **not** an independent security audit. The synthetic same-process evaluator must not be used as a sandbox for untrusted code.
