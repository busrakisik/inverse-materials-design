
    assert "No MCTS visits" in result["scientific_interpretation"]


def test_sequential_updates_use_previous_posterior_as_next_prior():
    engine = BayesianHypothesisSearchEngine()
    first = engine.accumulate_sequential_evidence("E1", _likelihoods())
    second_likelihoods = _likelihoods(0.3, 0.7, 0.5)
    second = engine.accumulate_sequential_evidence("E2", second_likelihoods)
    expected = _reference_posterior(first["updated_posteriors"], second_likelihoods)
    for name, probability in expected.items():
        assert second["updated_posteriors"][name] == pytest.approx(probability)
    assert second["prev_priors"] == first["updated_posteriors"]
    assert len(engine.history) == 2
    assert engine.history[0]["posteriors"] == first["updated_posteriors"]
    assert engine.history[1]["posteriors"] == second["updated_posteriors"]


def test_update_preserves_zero_visits_and_missing_action_values():
    engine = BayesianHypothesisSearchEngine()
    engine.accumulate_sequential_evidence("Step", _likelihoods())
    assert all(node["N"] == 0 and node["Q"] is None for node in engine.mcts_nodes.values())
    assert all(node["P"] == pytest.approx(engine.priors[name]) for name, node in engine.mcts_nodes.items())


def test_missing_mcts_implementation_fails_closed():
    engine = BayesianHypothesisSearchEngine()
    with pytest.raises(NotImplementedError, match="PUCT/MCTS scoring is not implemented"):
        engine.compute_uct("H1_NASICON")


def test_unknown_mcts_hypothesis_fails_clearly():
    with pytest.raises(KeyError):
        BayesianHypothesisSearchEngine().compute_uct("no-such-hypothesis")


def test_caller_defined_prior_has_unverified_provenance():
    engine = BayesianHypothesisSearchEngine({"A": 0.8, "B": 0.2})
    result = engine.accumulate_sequential_evidence("Example", {"A": 0.1, "B": 0.4})
    assert result["prior_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"
    assert result["updated_posteriors"]["A"] == pytest.approx(0.5)
    assert result["updated_posteriors"]["B"] == pytest.approx(0.5)
    assert result["allocated_budget"] is None


def test_tiny_positive_likelihoods_are_numerically_stable():
    engine = BayesianHypothesisSearchEngine({"A": 0.4, "B": 0.6})
    result = engine.accumulate_sequential_evidence(
        "Very unlikely evidence", {"A": 1e-200, "B": 2e-200}
    )
    assert result["updated_posteriors"]["A"] == pytest.approx(0.25)
    assert result["updated_posteriors"]["B"] == pytest.approx(0.75)


def test_valid_zero_likelihood_disables_only_that_hypothesis():
    engine = BayesianHypothesisSearchEngine({"A": 0.5, "B": 0.5})
    result = engine.accumulate_sequential_evidence("One impossible model", {"A": 0, "B": 0.8})
    assert result["updated_posteriors"] == {"A": 0.0, "B": 1.0}


@pytest.mark.parametrize("invalid_likelihoods", [
    {},
    {"H1_NASICON": 0.92},
    {**_likelihoods(), "unknown": 0.5},
    _likelihoods(True, 0.5, 0.5),
    _likelihoods(-0.1, 0.5, 0.5),
    _likelihoods(1.01, 0.5, 0.5),
    _likelihoods(float("nan"), 0.5, 0.5),
    _likelihoods(float("inf"), 0.5, 0.5),
    _likelihoods(0, 0, 0),
    None,
    [],
])
def test_invalid_evidence_fails_without_state_mutation(invalid_likelihoods):
    engine = BayesianHypothesisSearchEngine()
    before = dict(engine.priors)
    with pytest.raises(ValueError):
        engine.accumulate_sequential_evidence("Invalid example", invalid_likelihoods)
    assert engine.priors == before
    assert engine.history == []
    assert all(node["N"] == 0 for node in engine.mcts_nodes.values())


@pytest.mark.parametrize("invalid_step", ["", "   ", None, 123])
def test_invalid_step_name_rejected_without_mutating_state(invalid_step):
    engine = BayesianHypothesisSearchEngine()
    original = dict(engine.priors)
    with pytest.raises(ValueError):
        engine.accumulate_sequential_evidence(invalid_step, _likelihoods())
    assert engine.priors == original
    assert engine.history == []


@pytest.mark.parametrize("invalid_priors", [
    {},
    {"A": 0.4, "B": 0.4},
    {"A": True, "B": 0.0},
    {"A": float("nan"), "B": 0.5},
    {"A": -0.1, "B": 1.1},
    {"": 0.5, "B": 0.5},
])
def test_invalid_initial_priors_fail_explicitly(invalid_priors):
    with pytest.raises(ValueError):
        BayesianHypothesisSearchEngine(invalid_priors)


def test_history_snapshot_not_overwritten_by_later_updates():
    engine = BayesianHypothesisSearchEngine()
    first = engine.accumulate_sequential_evidence("E1", _likelihoods())
    snapshot = dict(first["updated_posteriors"])
    engine.accumulate_sequential_evidence("E2", _likelihoods(0.2, 0.5, 0.9))
    assert engine.history[0]["posteriors"] == snapshot
    assert engine.history[0]["budget_status"] == "NOT_ALLOCATED"
    assert engine.history[0]["mcts_status"] == "NOT_RUN"

# END OF COMPLETE BHS LEGACY BAYESIAN TESTS — CHECK THIS LINE ON GITHUB

