"""Report-safety tests for the BHS benchmark prototype.

These tests validate the NOT_RUN study manifest. They do not execute materials
simulations, calculate performance, or certify scientific results.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from bhs.benchmarks.suite_20 import AblationBenchmarkSuite


def test_protocol_export_is_explicitly_not_a_results_report():
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "benchmark_20_protocol.json"
        saved = AblationBenchmarkSuite.save_protocol_manifest(target)
        assert Path(saved) == target
        document = json.loads(target.read_text(encoding="utf-8"))
        assert document["artifact_type"] == "BENCHMARK_PROTOCOL"
        assert document["status"] == "NOT_RUN"
        assert "NOT a benchmark result" in document["notice"]
        assert len(document["systems"]) == 20
        assert all(item["status"] == "NOT_RUN" for item in document["systems"])
        assert all(item["metrics"] is None for item in document["systems"])
        assert all(item["evidence_files"] == [] for item in document["systems"])


def test_unimplemented_empirical_report_cannot_be_written():
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "benchmark_20_results.json"
        try:
            AblationBenchmarkSuite.save_benchmark_report([], str(target))
        except NotImplementedError as error:
            assert "not implemented" in str(error)
        else:
            raise AssertionError("Empirical report export must be disabled")
        assert not target.exists()


def test_unexecuted_protocol_is_not_claimed_to_be_a_paper_table():
    with TemporaryDirectory() as tmp:
        folder = Path(tmp)
        AblationBenchmarkSuite.save_protocol_manifest(folder / "protocol.json")
        assert not (folder / "benchmark_20_results.json").exists()
        assert not (folder / "table1_benchmark.tex").exists()


if __name__ == "__main__":
    test_protocol_export_is_explicitly_not_a_results_report()
    test_unimplemented_empirical_report_cannot_be_written()
    test_unexecuted_protocol_is_not_claimed_to_be_a_paper_table()
    print("PASS: 3 report safety tests (no empirical benchmark run)")
