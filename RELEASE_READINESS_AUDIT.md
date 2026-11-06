# Release readiness — historical checkpoint

> **Historical document (31 October 2026).** The audit below records the state at that date, not the current project's full testing or publication status. For the latest evidence, see [research overview](research/RESEARCH_OVERVIEW.md), [NIST aggregated results](research/) and [current README](README.md). In particular, the older `CITATION.cff` values discussed below were revised on 6 November 2026 so the earlier Zenodo release is not presented as the archive for subsequent experiments.

---

BHS — Release Readiness and Scientific Audit Notes

Audit date: 2026-10-31

Repository: https://github.com/busrakisik/inverse-materials-design

Development branch: bhs-scientific-audit

Archived historical release: v1.0.1 (2026-08-02)

Archived DOI: https://doi.org/10.5281/zenodo.21761835

Status: NOT READY TO CLAIM EMPIRICAL SCIENTIFIC VALIDATION

This document describes the audited development branch. It does not amend
the historical Zenodo archive or certify an independent scientific result.

1. Verified engineering checkpoint
GitHub Actions check on bhs-scientific-audit: 83 passed (2026-10-31).
CI run: https://github.com/busrakisik/inverse-materials-design/actions/runs/41194646316
CI uses Python 3.11, PyYAML, pytest, and actual pymatgen package.
Evidence tests exercise real pymatgen structures.
Physics-adapter tests mock CHGNet; no CHGNet model was run.
The CI targets seven named test files rather than the entire repository.
These tests do not establish material-discovery performance or real-world reproducibility.
2. Component status
Area	Current status	Publication caveat
Discrete Bayesian updates	Tested	Inputs are supplied illustrative likelihoods, not calibrated physical evidence
Structural overlap score	Tested with pymatgen	Uncalibrated heuristic; not a Wyckoff-likelihood or stability measure
SOAP score transformation	Tested	Does not calculate SOAP descriptors
CHGNet adapter	Mock-tested	True model accuracy, real inference, and reference validation not tested
MCTS / PUCT	Not implemented in audited engine	No real rollouts, visit counts or evaluated rewards
20-system comparison	NOT_RUN protocol	No speedup, GPU cost or baseline outcome can be claimed
Provenance bundle	Tested	NOT_VERIFIED is not a reproducibility certificate
Legacy UI and pipeline	Outside focused CI	Needs separate audit before being presented as runnable
3. Citation and archive reconciliation
GitHub release v1.0.1 is the existing archived software release.
CITATION.cff currently references version: "1.0.1", date
2026-08-02, and the Zenodo DOI 10.5281/zenodo.21761835.
The Zenodo record title is "busrakisik/inverse-materials-design: v1.0.1 —
Academic Citation & Provenance Framework"; its displayed creator is
"busrakisik". The CFF instead names Büşra Kısık and has the
research-project title "Bayesian Hypothesis Search (BHS) for Autonomous
Materials Discovery".
These title/creator-display differences should be reconciled when preparing
the next archived release. They do not authorize changing the existing DOI.
Do not label the experimental audit branch v1.0.1 as though its updated
code were already included in the archived v1.0.1 snapshot.
When an audited release is ready, choose a new version, create a GitHub
release from an approved commit, update citation metadata for that release,
and verify the resulting archive DOI and creator/title fields.
4. Remaining work before an audited software release
Verify source and imports across the whole repository, including
app.py, run_pipeline.py, src/, crystal_gen/, and legacy modules.
Add a documented, platform-tested dependency environment; the current
top-level requirements.txt is not pinned and includes legacy packages.
Confirm the sample demo runs from a fresh clone using only documented
commands and produces correctly labeled NOT_VERIFIED outputs.
Remove unintended tracked build artifacts, including existing
__pycache__/ paths, if present; a .gitignore does not untrack files
already committed.
Review the unexpected root-level =0.46.1 file before removing it.
Decide how research-demo and legacy UI components will be separated or
prominently labeled in the default branch.
Review the default-branch changes in a pull request and rerun appropriate
checks before merging.
Update the version/release date and citation metadata only in the
context of an actual new release; verify archived metadata afterward.
5. Research milestones beyond a software-only release
Calibrate likelihood models on defined reference datasets and check
conditional-dependence assumptions.
Implement a real hypothesis-selection/search loop and collect raw logs.
Run actual CHGNet/other physics predictions with numerical checks and
suitable reference comparisons.
Execute fair baselines with matched budgets, seeds, success criteria,
uncertainty estimates, and complete provenance.
Independently reproduce the measurements in a pinned environment.
Recommended current public description: "Open-source research prototype
exploring Bayesian hypothesis updates and provenance-aware materials-search
components; experimental scientific validation remains future work."

Non-claim: The 83 passing tests are engineering evidence for the tested
behaviors, not proof of improved materials discovery, scientific
breakthroughs, reduced GPU hours, or benchmark superiority.

