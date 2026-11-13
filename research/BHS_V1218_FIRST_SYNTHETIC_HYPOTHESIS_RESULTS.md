# BHS V12.18 — First rival predictive-hypothesis component and zero-performance evidence

**13 November 2026. Two-model Bayesian decision mathematics with fabricated observations only; NO new experimental source results or scientific performance benchmark.**

## Source context and limitations

Gongora et al., *Science Advances* **6** (2020), eaaz1708, DOI `10.1126/sciadv.aaz1708`, describes a pre-fabrication four-parameter crossed-barrel design `(n, theta, r, t)` subsequently measured for compression toughness `U` in joules. The source reports that force–displacement traces were collected, but their complete per-sample availability and a matched failure-mode assessment have not been certified in the historical V11 dataset. The research owner's strict feature-origin, pre-expensive-computation availability and policy-time access requirements remain mandatory for any real performance experiment.

The old physical-history matched-budget V11 study tested **the v5 kernel-portfolio component**, not full hypothesis-centric BHS: average simple regret `GP–ARD EI=7.363 J`, `RF–UCB=8.983 J`, `BHS v5=9.368 J`, `random=15.951 J` on five DEVELOPMENT seeds (16 designs / 48 historical physical responses each). This remains an unfavorable result for the BHS statistical component. No fresh heldout result was created here.

## Pre-frozen implementation and scientific contract

V12.18 protocol frozen before code and tests: `research/BHS_V1218_RIVAL_PREDICTIVE_PROTOCOL.md`, exact Git blob `74e73368e202bc2ad88e5dadbae73c059a828a09`. First implementation `scripts/bhs_v1218_dual_predictive_hypotheses.py` Git blob `ea20f1e2564db6d97e94e3823508918196ed5f61`; adversarial tests `tests/test_bhs_v1218_dual_predictive_hypotheses.py` Git blob `48843b16eff1b24bbedf40cac859e6a01601c0b2`. Original source-only branch head `032beb8e74b83a9771f9452d51461f113eac1427`. Neither source nor protocol was altered after inspecting its first synthetic outcomes.

Actual new mathematical implementation:

1. `H_ADD`: a linear additive toughness predictor in predetermined dimensionless `n,theta,r,t`.
2. `H_TWIST_THICKNESS`: exactly the same additive model plus a twist-angle × wall-thickness interaction. **NESTED PREDICTIVE STRUCTURES, NOT DISTINCT PHYSICAL FAILURE MECHANISMS**; any preference does NOT prove local buckling, brittle/ductile failure or physics.
3. For each model, Gaussian coefficient prior with fixed SD 10 J, Gaussian response noise assumed SD 5 J (source paper's initial GP noise assumption; **not independently calibrated for this project**); equal prior model weights 0.5/0.5. Sequential conditional normal densities and conjugate regression updates use previously **revealed** scalar responses only.
4. Next candidate is chosen by one-step **expected information gain about the binary predictive-model identity**, using a frozen 16-point Gauss–Hermite quadrature and stable deterministic ID tie-breaking. This is **NOT** maximizing toughness, an implemented physical Bayes likelihood, closed-loop observation-contingent MCTS or actual resource budgeting. The implementation imports no source data, oracle, or real response file.

## Original first-run software and fabricated outcomes

- First GitHub Actions run [43430503540](https://github.com/busrakisik/inverse-materials-design/actions/runs/43430503540): **SUCCESS, 201 software checks** = 25 new V12.18 + 18 V12.17 + 13 old scalar Bayes + 12 old PUCT + 13 old V11 + 120 inherited legacy test cases. **No scientific benchmark**. Full original JSON artifact ID `14040400178`, source filename `bhs_v1218_first_synthetic_rival_hypotheses.json`, **3,518 bytes**, SHA-256 **`c3aa0391b2442b3441e1960fb768328e0713b5fecbff9934abb230286d538093`**.
- Original **four invented candidate designs** and **one invented 12 J response** were used solely to check sequential mathematics, not as observations from any experiment. First choice was `fabricated-b`; its initial expected model identity information gain was **`2.947743603209929e-6 nats`**. With a manufactured response of exactly 12 J for that candidate, model weights became **`P(H_ADD)=0.500009491676837`**, **`P(H_TWIST_THICKNESS)=0.4999905083231631`**.
- Next choice was `fabricated-d`, with calculated assumed information gain **`1.5591948185122995e-5 nats`** under that hypothetical posterior.
- **Critical limitation:** both expected information gains are near zero, model weights stay near 0.5/0.5. Under these assumptions and invented candidates, the proposed predictive models are practically difficult to distinguish by one observation. **Do not optimize the fake fixture after seeing these weak numbers, market this as physics discrimination, or claim improved BHS outcomes.** The first weak synthetic test is retained.
- The numerical update is a mathematical unit test; the real source does not provide a verified noise model, causal mechanistic claim, independent source holdout or decision chronology for the full scientific system.

## Scientific status and next research dependency

The two-predictive-structure inference plus action selection is a **working sequential statistical prototype** with strict public-feature and previously-revealed-outcome API boundaries. This does not yet supply scientifically distinct physical hypotheses, independently validated `P(E|H)`, reliable model calibration, a defensible real-budget experiment or full BHS with actual observation-contingent nonmyopic planning. Software test success is reproducibility evidence only.

**Decision:** `DEVELOPMENT_ONLY_SYNTHETIC_HYPOTHESIS_DISCRIMINATION`; `scored_validation_allowed=false`, `full_bhs_fair_comparison_ready=false`, `physical_mechanisms_identified=false`, `scientific_likelihood_calibrated=false`, `independent_holdout_used=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `laboratory_action_allowed=false`.

Highest-value next steps, in order:

1. Locate and authenticate whether **per-sample force–displacement curves** and failure-mode classifications can be mapped to the experimental design IDs, from original authors or a public source, without importing outcome-driven features before the decision. The publication reports local storage of traces; the current four-input + toughness replicate corpus does not prove their availability.
2. Have a mechanics-domain collaborator specify at least two genuinely distinguishable **physical** predictions, their measurement requirements and credible error/noise model. If full traces are not accessible, do not claim mechanistic hypothesis identification from toughness alone.
3. Rigorously test *identifiability and utility* of rival models under hypothetical inputs and independent-source/fair-budget constraints, with analysis frozen before any scored real data. A predictive-model posterior is not a validated physical mechanism posterior.
4. Only then assemble real source-certified observable-to-hypothesis-to-acquisition pipeline with real GP/RF baselines, prospectively independent evaluation and, if required, observation-contingent planning.

All historic negative/failed runs, unmerged draft PRs, public default, old releases/tags and protected NIST `10000..10099` remain untouched.
