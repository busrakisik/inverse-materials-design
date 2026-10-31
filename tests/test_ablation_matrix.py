"""Tests for the honest 20-system benchmark protocol (not a speedup claim)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from bhs.benchmarks.suite_20 import AblationBenchmarkSuite


def test_20_system_protocol_is_explicitly_unrun():
    cases = AblationBenchmarkSuite.create_protocol_manifest()
    assert len(cases) == 20
    assert len({case["system"] for case in cases}) == 20
    assert all(case["status"] == "NOT_RUN" for case in cases)
    assert all(case["metrics"] is None for case in cases)


def test_unimplemented_benchmark_refuses_to_fabricate_data():
    try:
        AblationBenchmarkSuite.run_full_suite()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("Benchmark must not invent experimental results")


def test_unrun_protocol_can_be_saved_without_false_metrics():
    with TemporaryDirectory() as directory:
        file_path = Path(directory) / "protocol.json"
        AblationBenchmarkSuite.save_protocol_manifest(file_path)
        data = json.loads(file_path.read_text(encoding="utf-8"))
        assert data["status"] == "NOT_RUN"
        assert len(data["systems"]) == 20
        assert all(case["metrics"] is None for case in data["systems"])


def test_measured_report_requires_an_actual_experiment_pipeline():
    try:
        AblationBenchmarkSuite.save_benchmark_report([])
    except NotImplementedError:
        pass
    else:
        raise AssertionError("Must reject unverified measurement exports")


if __name__ == "__main__":
    test_20_system_protocol_is_explicitly_unrun()
    test_unimplemented_benchmark_refuses_to_fabricate_data()
    test_unrun_protocol_can_be_saved_without_false_metrics()
    test_measured_report_requires_an_actual_experiment_pipeline()
    print("OK: benchmark protocol tests passed (no empirical benchmarks run).")
