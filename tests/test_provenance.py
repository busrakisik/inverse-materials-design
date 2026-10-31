"""Mathematical and provenance tests for the BHS Bayesian *prototype*.

These tests check probabilities and defensive behavior. They do NOT establish
that the supplied likelihoods are calibrated scientific evidence or that
physical experiments, MCTS rollouts, or materials discovery occurred.
"""

import math

import pytest

from bhs.provenance.tags import DataProvenanceType
from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine


def test_single_bayes_update_matches_analytic_result():
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.3, "C": 0.2})
    result = engine.accumulate_evidence(
        "illustrative likelihoods", {"A": 0.95, "B": 0.32, "C": 0.15}
    )
    normalizer = 0.5 * 0.95 + 0.3 * 0.32 + 0.2 * 0.15
    expected = {"A": 0.5 * 0.95 / normalizer,
                "B": 0.3 * 0.32 / normalizer,
                "C": 0.2 * 0.15 / normalizer}
    for hypothesis, probability in expected.items():
        assert result["posteriors"][hypothesis].value == pytest.approx(probability)
        assert engine.priors[hypothesis] == pytest.approx(probability)
    assert sum(engine.priors.values()) == pytest.approx(1.0)
    assert result["winning_hypothesis"] == "A"


def test_two_updates_agree_with_direct_sequential_bayes_rule():
    priors = {"A": 0.4, "B": 0.6}
    first = {"A": 0.3, "B": 0.8}
    second = {"A": 0.9, "B": 0.2}
    engine = BayesianHypothesisSearchEngine(priors)
    engine.accumulate_evidence("first example", first)
    engine.accumulate_evidence("second example", second)
    weights = {h: priors[h] * first[h] * second[h] for h in priors}
    for h in priors:
        assert engine.priors[h] == pytest.approx(weights[h] / sum(weights.values()))
    assert len(engine.history) == 2


def test_extremely_small_likelihoods_do_not_underflow():
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.5})
    output = engine.accumulate_evidence(
        "tiny illustrative probabilities", {"A": 1e-300, "B": 2e-300}
    )
    assert output["posteriors"]["A"].value == pytest.approx(1 / 3)
    assert output["posteriors"]["B"].value == pytest.approx(2 / 3)


def test_zero_likelihood_eliminates_hypothesis_without_false_results():
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.5})
    engine.accumulate_evidence("example", {"A": 0.0, "B": 0.5})
    assert engine.priors == pytest.approx({"A": 0.0, "B": 1.0})


def test_zero_prior_cannot_be_revived_by_likelihood():
    engine = BayesianHypothesisSearchEngine({"A": 1.0, "B": 0.0})
    engine.accumulate_evidence("example", {"A": 0.4, "B": 1.0})
    assert engine.priors == pytest.approx({"A": 1.0, "B": 0.0})


def test_impossible_evidence_raises_without_changing_state():
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.5})
    old_priors = engine.priors.copy()
    with pytest.raises(ValueError, match="zero probability"):
        engine.accumulate_evidence("impossible example", {"A": 0.0, "B": 0.0})
    assert engine.priors == old_priors
    assert engine.history == []


@pytest.mark.parametrize("likelihoods", [
    {"A": 0.5},
    {"A": 0.5, "B": 0.4, "C": 0.1},
])
def test_missing_or_extra_hypotheses_rejected(likelihoods):
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.5})
    with pytest.raises(ValueError, match="exactly"):
        engine.accumulate_evidence("incomplete", likelihoods)
    assert not engine.history


@pytest.mark.parametrize("bad_value", [-0.01, 1.01, float("nan"), float("inf"), True, "0.5"])
def test_invalid_likelihood_value_rejected(bad_value):
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.5})
    with pytest.raises(ValueError, match="Likelihood"):
        engine.accumulate_evidence("bad likelihood", {"A": bad_value, "B": 0.5})
    assert engine.priors == {"A": 0.5, "B": 0.5}
    assert engine.history == []


@pytest.mark.parametrize("bad_priors", [
    {}, {"A": 0.2, "B": 0.2},
