# External concrete development v5 — fixed exploratory protocol

**Status: DEVELOPMENT-ONLY experiment; no independent scored evaluation, no physical mechanism identified.**

**Source:** I-Cheng Yeh, *Concrete Compressive Strength* (UCI dataset **165**, DOI **10.24432/C5PK67**), [official UCI record](https://archive.ics.uci.edu/dataset/165/concrete-compressive-strength), **CC BY 4.0**. Cite the author and the dataset when using source data. UCI lists 1,030 observations, 8 input features and compressive strength (MPa). The original spreadsheet is not redistributed by this project.

**Question B (property optimization; not Question A, physical hypothesis discrimination):** Under a small, fixed, retrospective acquisition budget on a new materials-related measurement dataset, does a fixed statistical kernel portfolio outperform a fixed Gaussian-process expected-improvement reference? Report negative results with equal prominence. This is not confirmation of a scientific advantage.

## Prespecified development protocol

1. Download the source via `ucimlrepo==0.0.7`, dataset ID `165` **only** when the workflow is explicitly executed. Check raw observations are 1,030, 8 predictors, one continuous target, no missing/nonfinite rows.
2. Use only rows with curing age **28 days** to reduce the trivial confounding of strength by specimen age. Choose one representative per **exactly identical eight-feature vector**, using source order and *never comparing response values* to select which row to keep. Repeats have measurement ambiguity; outcomes are not averaged. Report the pool counts.
3. Standardize candidate descriptors from unlabelled inputs only. For each predefined development seed **7, 13, 23**, choose the same six initial observations for all three policies. Each policy acquires **10** additional unobserved candidates.
4. The selector receives candidate features, only the indices of previously observed examples, and only their response values. The evaluator alone can access the complete target array; it reveals one value *after* a selection. No prospective experiment or extra source data is claimed.
5. Compare **random**, a fixed Matérn-5/2 Gaussian-process expected-improvement reference (`gp_ei`), and a kernel portfolio `kernel_portfolio_ei`: a likelihood-weighted combination of Matérn-3/2 and squared-exponential GP expected-improvement scores. Kernel families are **statistical response models**, not alternative concrete chemical mechanisms. This is only one fixed GP baseline, **not** an exhaustive tuned comparison.
6. All methods use the same initial candidate IDs and the same 10-acquisition budget. Report **simple regret** in MPa and normalized by the retrospective pool range; the optimizer never accesses that range or the globally best response. Costs are unknown; an equal count is not a laboratory cost benefit.
7. Persist only study metadata, parsed-array fingerprint, pool counts and per-campaign/aggregate metrics; no raw dataset rows or individual observation values in committed reports. The parsed table hash is **not** the hash of the original `.xls`.
8. The source is **new development data**, not an independent holdout. `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, `claimed_superiority=false`. Never use prohibited independent seeds **10000–10099**. No parameter revision after seeing results can be treated as confirmatory.

## Run

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2 pandas==2.2.3 ucimlrepo==0.0.7
python -m unittest discover -s tests -p 'test_uci_concrete_v5.py' -v
python -m scripts.uci_concrete_v5  # protocol only, NO download
python -m scripts.uci_concrete_v5 --execute --out runs/uci_concrete_development_v5.json
```

The GitHub Actions workflow isolates test and data-acquisition stages and uploads aggregate output as an artifact. If the official source is unavailable, the run fails; do **not** substitute invented measurements. Future scientific claims require prospective, independently reviewed and leakage-safe validation plus stronger baselines and scientifically justified hypotheses.
