# BHS — prospective decision reliability study: preregistration outline

**Status: PROPOSED DESIGN, not an executed experiment, registered trial, validated improvement or signed collaboration.**

## Objective

The doctoral-level question is not simply whether an automated rule can refuse an unsafe-looking action. It is:

**At a matched rate of actionable decisions, does evidence-aware abstention reduce the frequency and expected harm of *incorrect* laboratory recommendations compared with simpler decision policies, without creating unreasonable measurement or review burden?**

The result may be negative. Software-contract success from v6–v8 does **not** answer this question.

## Connection to established work

Selective prediction studies the trade-off between accepting decisions and the error rate among accepted cases. See El-Yaniv & Wiener (2010), *On the Foundations of Noise-free Selective Classification*, [JMLR](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf), and Geifman & El-Yaniv (2017), *Selective Classification for Deep Neural Networks*, [NeurIPS](https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html).

Angelopoulos, Bates, Fisch, Lei & Schuster (2024), *Conformal Risk Control*, [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html), provides a framework for risk control under specific mathematical assumptions. **BHS currently does not implement or qualify for those formal risk guarantees**. Independence/exchangeability, loss monotonicity, calibration sample design and any shift adjustment must be justified before attempting such a claim.

## Study unit and reference truth

A decision episode is a single proposed physical measurement/intervention, its available evidence **at the moment of decision**, and its subsequently observed outcome. The unit of independence and grouping (material batch, instrument, operator, calendar period, laboratory) must be agreed with a scientific collaborator **before data access**.

The reference evaluation must independently document feasibility, safety constraints and an objective response; all candidates and failures must be retained to avoid publication and survivorship bias. A label cannot be treated as truth if the measurement has not been performed or its protocol is unknown.

## Comparator policies

1. **Always recommend** among eligible feasible proposals (no abstention baseline; never physically execute a proposal without authorized lab approval).
2. **Always abstain** (coverage 0; selective risk **undefined**, not automatically zero).
3. **Simple evidence completeness rule**, e.g. all required metadata fields nonempty; fixed before evaluation.
4. **Domain expert review policy**, defined before access to study outcomes.
5. **Fixed model-confidence threshold** / GP reference where a calibrated model and outcome are available.
6. **BHS v8 contract** with source integrity, compatible units, out-of-band reviewer trust, missing-evidence requests and explicit expert review.

Do not treat the expert as the single indisputable ground truth when laboratory measurements disagree. Record disagreements and adjudication procedures.

## Measures

- **Coverage:** fraction of proposed cases passed to the predeclared review/action stage. Define denominator carefully and include excluded/invalid cases in a separate accounting.
- **Selective risk:** proportion or severity-weighted loss for wrong recommendations among cases the policy actually accepts, with appropriate uncertainty intervals. It is undefined if a policy accepts zero cases.
- **Risk–coverage curve:** evaluate each eligible policy over thresholds frozen on a *distinct development/calibration set*, not on the test outcomes.
- **Weighted decision cost:** separately record experimental cost, delay, human review effort and loss from a wrong recommendation. Cost weights and units must be prespecified by the laboratory; no fabricated savings.
- **Abstention burden:** requests for additional records and trials, proportion later resolved, delay, unavailable-metadata rate and risk of permanent rejection.
- **Stress performance:** falsified/contradictory or expired evidence, altered evidence after review, unit mismatch, out-of-domain mixtures and batch/instrument shift. Use clearly marked *synthetic fault injection* distinct from natural physical failures.

## Design safeguards

- Freeze measurement protocol, physical contrasts, feasible ranges, stopping rules and loss/utility model **before** independent results.
- Respect natural dependency: split or block at material-batch/site/time level as required; do not leak same mixtures/replicates across calibration and evaluation.
- Define a locked development/calibration cohort and a separate untouched independent evaluation cohort. Earlier UCI concrete v5–v6/NIST studies are **development**, not an external holdout.
- Domain experts should inspect causal assumptions, experimental ethics, calibration, measurement uncertainty, actual material safety and laboratory operations.
- Predefine false-recommendation risk at **matched coverage** as the primary comparison, with sensitivity analyses for coverage, unit cost, batch dependence, missing data and domain shift.
- Select sample size and statistical decision thresholds from a pre-experiment power/precision analysis performed with the partner laboratory. Do not invent significance or promise a guarantee based on available software tests.
- Report all outcomes, including **failure to improve**, policy coverage collapse, excessive evidence cost and conditions where formal risk-control assumptions are not met.

## Falsification criteria

Claims of value are **not supported** if the system's apparent low error is achieved only by refusing essentially everything; if source attestations fail to reflect independent provenance; if uncertainty bounds are not calibrated; if results are driven by one laboratory/batch; or if at matched coverage the simpler expert/completeness policy is equally reliable at lower cost.

## Current boundary

No prospective lab partner or physical intervention is asserted here. BHS v8 provides a tested **software integrity contract**, not laboratory performance evidence. Current hard restrictions: `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, `claim_of_superiority=false`. Reserved NIST independent seeds `10000..10099` remain unused.

**Next external prerequisite:** a documented collaborator, measurement protocol, valid evidence chain, real cost definitions, independent test setting and explicit authorization before any experiment involving laboratory action.
