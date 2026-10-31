"""Unit tests for baseline selection demos, not scientific speedup claims.

No empirical benchmark is executed. These checks ensure deterministic
sampling and prevent fabricated GPU-hours or convergence measurements.
"""

import pytest

from bhs.benchmarks.baselines import BenchmarkRunner, RandomSearchBaseline
from bhs.provenance.tags import DataProvenanceType


CANDIDATES = ["LiFePO4_Olivine", "LiFePO4_Spinel", "LiFePO4_NASICON"]


def test_random_baseline_selects_valid_candidate_without_claiming_gpu_cost():
    result = RandomSearchBaseline(CANDIDATES, seed=17).run_step()
    assert result["selected_candidate"] in CANDIDATES
    assert result["status"] == "SELECTION_DEMO_ONLY"
    assert result["performance_measured"] is False
    assert result["gpu_hours_used"] is None
    assert "speedup_pct" not in result
    assert "steps_to_converge" not in result


def test_selection_probability_is_derived_not_a_performance_measurement():
    probability = RandomSearchBaseline(CANDIDATES, seed=17).run_step()["probability"]
    assert probability.value == pytest.approx(1 / len(CANDIDATES))
    assert probability.provenance == DataProvenanceType.DERIVED
    assert "Uniform random policy" in probability.source_description


def test_seeded_sampling_is_reproducible():
    first = RandomSearchBaseline(CANDIDATES, seed=7)
    second = RandomSearchBaseline(CANDIDATES, seed=7)
    first_picks = [first.run_step()["selected_candidate"] for _ in range(15)]
    second_picks = [second.run_step()["selected_candidate"] for _ in range(15)]
    assert first_picks == second_picks


@pytest.mark.parametrize("candidates", [[], ["A", ""], ["A", None]])
def test_invalid_candidate_lists_are_rejected(candidates):
    with pytest.raises(ValueError, match="nonempty list"):
        RandomSearchBaseline(candidates)


def test_unimplemented_empirical_benchmark_fails_instead_of_inventing_results():
    runner = BenchmarkRunner(targets=["LiFePO4", "SrTiO3"])
    with pytest.raises(NotImplementedError, match="not implemented"):
        runner.evaluate_system("LiFePO4")


def test_unknown_benchmark_target_is_rejected():
    runner = BenchmarkRunner(targets=["LiFePO4"])
    with pytest.raises(ValueError, match="Unknown target system"):
        runner.evaluate_system("SrTiO3")


def test_empty_benchmark_targets_are_rejected():
    with pytest.raises(ValueError, match="nonempty list"):
        BenchmarkRunner(targets=[])
