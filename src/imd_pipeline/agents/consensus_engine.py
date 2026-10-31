# BEGIN OF COMPLETE BHS LEGACY CONSENSUS ENGINE — CHECK THIS LINE ON GITHUB
"""Descriptive statistics on explicitly supplied model outputs only.

No CHGNet, MACE, M3GNet or DFT calculations are executed here. Input records
are unverified, and different energy reference zeros may be incompatible.
Neither the spread nor the mean establishes scientific model consensus.
"""

import math
from typing import Any, Dict


class MultiModelConsensusEngine:
    """Reject fictional legacy predictions; never manufacture model outputs."""

    @staticmethod
    def evaluate_ensemble(structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize supplied energies, without claiming physical validation.

        Input: {"model_predictions": {
            "model-A": {
                "value_ev_per_atom": -5.0,
                "model_version": "example-version",
                "calculation_id": "example-run-A",
                "structure_id": "same-structure",
            },
            ...at least one other distinct model...
        }}
        """
        if not isinstance(structure_data, dict) or set(structure_data) != {"model_predictions"}:
            raise ValueError("Explicit model_predictions required; legacy fake ensemble disabled.")
        predictions = structure_data["model_predictions"]
        if not isinstance(predictions, dict) or len(predictions) < 2:
            raise ValueError("At least two model prediction records are required.")

        fields = {"value_ev_per_atom", "model_version", "calculation_id", "structure_id"}
        energies = []
        checked = {}
        calculation_ids = set()
        structure_id = None

        for name, record in predictions.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Model names must be nonempty strings.")
            if not isinstance(record, dict) or set(record) != fields:
                raise ValueError(f"{name}: record must have exactly {sorted(fields)}.")
            for field in ("model_version", "calculation_id", "structure_id"):
                if not isinstance(record[field], str) or not record[field].strip():
                    raise ValueError(f"{name}: {field} must be nonempty text.")

            if record["calculation_id"] in calculation_ids:
                raise ValueError("Duplicate calculation_id.")
            calculation_ids.add(record["calculation_id"])
            if structure_id is None:
                structure_id = record["structure_id"]
            elif record["structure_id"] != structure_id:
                raise ValueError("Cannot combine different structure_id values.")

            raw = record["value_ev_per_atom"]
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise ValueError(f"{name}: value_ev_per_atom must be a finite number.")
            try:
                value = float(raw)
            except (OverflowError, ValueError) as exc:
                raise ValueError(f"{name}: invalid numeric input.") from exc
            if not math.isfinite(value):
                raise ValueError(f"{name}: value_ev_per_atom must be finite.")

            energies.append(value)
            checked[name] = {
                "value_ev_per_atom": value,
                "model_version": record["model_version"],
                "calculation_id": record["calculation_id"],
                "structure_id": record["structure_id"],
            }

        try:
            mean = math.fsum(energies) / len(energies)
            variance = math.fsum((x - mean) ** 2 for x in energies) / len(energies)
            spread = math.sqrt(variance)
            value_range = max(energies) - min(energies)
        except (OverflowError, ValueError) as exc:
            raise ValueError("Energy summary cannot be computed safely.") from exc
        if not all(math.isfinite(v) for v in (mean, spread, value_range)):
            raise ValueError("Energy summary is not numerically finite.")

        return {
            "model_count": len(energies),
            "input_values_ev_per_atom": checked,
            "arithmetic_mean_of_supplied_values_ev_per_atom": mean,
            "population_std_of_supplied_values_ev_per_atom": spread,
            "range_of_supplied_values_ev_per_atom": value_range,
            "formation_energy_ev_per_atom": None,
            "calibrated_model_uncertainty_ev_per_atom": None,
            "scientific_consensus_score": None,
            "independent_execution_verification": "NOT_VERIFIED",
            "inter_model_energy_reference_alignment": "NOT_VERIFIED",
            "scientific_interpretation": (
                "DESCRIPTIVE ARITHMETIC ONLY on caller-supplied energies. "
                "No model was executed or verified. Energy references may differ; "
                "no formation energy, calibrated uncertainty or stability inference."
            ),
        }

# END OF COMPLETE BHS LEGACY CONSENSUS ENGINE — CHECK THIS LINE ON GITHUB
