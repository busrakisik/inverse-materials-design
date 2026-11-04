# BHS — Real Customer Problem and Defensibility Canvas v1

**Internal strategy hypotheses, not validated commercial claims.**

## Initial ideal partner

University or industrial materials/chemistry lab running repeated expensive
characterization/synthesis experiments, with a finite queue and structured
records of: candidate, measurement, known or estimable error, machine hours,
consumables cost, failed/missing data, and experiment constraints.

## Important problem hypotheses (ask, do not assume)

1. Do teams routinely choose between multiple scientific explanations after
   observing ambiguous experimental data?
2. What portion of campaign cost comes from measurement time, consumables,
   setup changes, or failed synthesis?
3. Can they produce historical experiment logs and costs that we are allowed to
   use in a retrospective offline evaluation?
4. Are current tools experimental-design spreadsheets, BO systems, robotic
   schedulers, or investigator intuition? How is success measured today?
5. What validated gain (less spend at equal accuracy, lower time-to-confidence,
   fewer failed experiments) would justify a pilot?

## Discovery interview — 20 minutes

- "Describe your most recent campaign where two explanations competed."
- "How did your team choose the next test? What other tests were considered?"
- "Which costs do you actually track, and which constraints dominate scheduling?"
- "What failure mode would make you stop trusting a software recommendation?"
- "Could we replay a historical campaign offline, without changing live instruments?"
- "Who owns the experiment log and can approve a pilot or budget?"

Do **not** start with the product pitch; learn the workflow and failure cost.

## Distinguish evidence from a sellable moat

- **Not a moat:** Bayesian update, one-step EIG, EIG/cost, MCTS, MIT-licensed
  copies of BHS itself. These have existing literature, competing implementations,
  and/or permissive licensing.
- **Potential defensibility, to be established:** rigorously tested domain-specific
  scientific hypothesis representations; calibration/abstention under shifts;
  clean integrations with instruments and lab metadata; reproducible audited
  experiments; secured customer workflows and measurable switching costs;
  performance on real constrained tasks confirmed by independent groups.

## Explicit business milestone gates

1. **Problem evidence:** ≥5 exploratory interviews across ≥2 labs,
   documented with consent and no misleading attribution.
2. **Usable dataset:** 1 permission-cleared offline campaign with provenance,
   costs, measurement errors, and audit-friendly evaluation agreement.
3. **Technical value:** matched-budget retrospective advantage over strong
   relevant baselines on a preregistered objective, with uncertainty estimates.
4. **Business value:** a partner estimates actual saved time or spending using
   its own audited costs; measure willingness to pilot, not invented TAM.
5. **Commercial decision:** consider pilot contract, productization or licensing
   after data ownership, software licensing, and IP counsel review.

These are planning milestones, not attained milestones or commercialization promises.
