"""20-system BHS benchmark protocol (no fabricated performance results).

The current repository does not yet have a validated empirical benchmarking
pipeline. This module defines the target systems and a reproducible, explicitly
UNRUN protocol. It deliberately does not invent search-step counts, GPU usage,
or comparisons against ablation and random-search baselines.
"""

import json
from pathlib import Path

BENCHMARK_20_SYSTEMS = [
    {"formula": "LiFePO4", "space_group": "Pnma", "class": "Battery Cathode"},
    {"formula": "Na3V2(PO4)3", "space_group": "R-3c", "class": "Na-ion Cathode"},
    {"formula": "SrTiO3", "space_group": "Pm-3m", "class": "Perovskite"},
    {"formula": "BaTiO3", "space_group": "P4mm", "class": "Ferroelectric"},
    {"formula": "LiCoO2", "space_group": "R-3m", "class": "Battery Cathode"},
    {"formula": "YBa2Cu3O7", "space_group": "Pmmm", "class": "Superconductor"},
    {"formula": "TiO2", "space_group": "P42/mnm", "class": "Oxide"},
    {"formula": "CsPbI3", "space_group": "Pm-3m", "class": "Halide Perovskite"},
    {"formula": "Li10GeP2S12", "space_group": "P42/nmc", "class": "Solid Electrolyte"},
    {"formula": "NaFePO4", "space_group": "Pnma", "class": "Na-ion Cathode"},
    {"formula": "La2CuO4", "space_group": "I4/mmm", "class": "Cuprate"},
    {"formula": "MgFe2O4", "space_group": "Fd-3m", "class": "Spinel"},
    {"formula": "LiMn2O4", "space_group": "Fd-3m", "class": "Spinel Cathode"},
    {"formula": "ZnO", "space_group": "P63mc", "class": "Semiconductor"},
    {"formula": "Al2O3", "space_group": "R-3c", "class": "Ceramic"},
    {"formula": "Graphene_C", "space_group": "P6/mmm", "class": "2D Material"},
    {"formula": "MoS2", "space_group": "P63/mmc", "class": "2D Dichalcogenide"},
    {"formula": "Li3N", "space_group": "P6/mmm", "class": "Solid Electrolyte"},
    {"formula": "Bi2Se3", "space_group": "R-3m", "class": "Topological Insulator"},
    {"formula": "Cu2O", "space_group": "Pn-3m", "class": "Photovoltaic"},
]


class AblationBenchmarkSuite:
    """Define the protocol without claiming that its experiments have run."""

    @staticmethod
    def create_protocol_manifest():
        """Return 20 explicitly unexecuted study cases, not experiment results."""
        return [
            {
                "system": entry["formula"],
                "space_group": entry["space_group"],
                "class": entry["class"],
                "status": "NOT_RUN",
                "metrics": None,
                "evidence_files": [],
            }
            for entry in BENCHMARK_20_SYSTEMS
        ]

    @staticmethod
    def run_full_suite():
        """Prevent the old API from silently producing fabricated outcomes."""
        raise NotImplementedError(
            "The 20-system benchmark execution pipeline has not been implemented. "
            "No empirical performance results are available. "
            "Use create_protocol_manifest() to inspect the planned systems."
        )

    @staticmethod
    def save_protocol_manifest(path="runs/benchmark_20_protocol.json"):
        """Save a clear NOT_RUN plan that can be tracked in future experiments."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "artifact_type": "BENCHMARK_PROTOCOL",
            "status": "NOT_RUN",
            "notice": (
                "This is a study plan, NOT a benchmark result or evidence "
                "of BHS speedup, GPU savings, or predictive performance."
            ),
            "systems": AblationBenchmarkSuite.create_protocol_manifest(),
        }
        destination.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return str(destination)

    @staticmethod
    def save_benchmark_report(results, out_path="runs/benchmark_20_results.json"):
        """Fail closed until empirical run-data ingestion is implemented.

        Accepting hand-entered step counts here would allow simulated numbers
        to be mislabeled as benchmark results. The next research milestone is
        an experiment runner with recorded seeds, hardware, comparison budgets,
        success criteria, and raw per-run logs.
        """
        raise NotImplementedError(
            "Empirical benchmark report export is not implemented. "
            "No measurements are written. Use save_protocol_manifest() "
            "for the explicitly unexecuted research plan."
        )
