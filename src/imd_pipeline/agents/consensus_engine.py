# BEGIN OF COMPLETE BHS LEGACY CONSENSUS ENGINE — CHECK THIS LINE ON GITHUB
"""Descriptive summaries of caller-supplied model values, not model consensus.

The historical implementation invented CHGNet, MACE, and M3GNet predictions
and reported their spread as calibrated model uncertainty. This replacement
NEVER runs any model, invents an energy, asserts model agreement, or assigns
an uncertainty or confidence score. Values and identifiers supplied by a
caller have NOT been independently verified.

Note: potentials from different models may have incompatible energy reference
zeros. Even finite, similarly sized energies cannot establish meaningful
scientific consensus without independent reference alignment and validation.
"""

import math
from typing import Any, Dict


class MultiModelConsensusEngine:
    """Retain legacy interface but prohibit invented multi-model results."""

    @staticmethod
    def evaluate_ensemble(structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize explicitly provided per-model values, never run models.

        Required input schema:
            {
              "model_predictions": {
                "model_name": {
                  "value_ev_per_atom": <finite numeric model-potential value>,
                  "model_version": <nonempty string>,
                  "calculation_id": <nonempty string>,
                  "structure_id": <nonempty string>
                },
                ... at least two model names ...
              }
            }

        The output is descriptive arithmetic ONLY. A common string structure
        ID is not proof that the same geometry or settings were used. These
        values must not be labeled formation energies, measured uncertainties,
        DFT comparisons, CHGNet computations, or material stability metrics.
        """
        if not isinstance(structure_data, dict) or set(structure_data) != {
            "model_predictions"
        }:
            raise ValueError(
                "Explicit model_predictions are required. The legacy fake "
                "CHGNet/MACE/M3GNet ensemble is disabled; no models were run."
            )

        predictions = structure_data["model_predictions"]
        if not isinstance(predictions, dict) or len(predictions) < 2:
            raise ValueError("Provide at least two named model prediction records.")

        required = {
            "value_ev_per_atom", "model_version", "calculation_id", "structure_id"
        }
        used_calculation_ids = set()
        shared_structure_id = None
        energies = []
        validated_predictions = {}
        for model_name, record in predictions.items():
            if not isinstance(model_name, str) or not model_name.strip():
                raise ValueError("Each model needs a nonempty model name.")
            if not isinstance(record, dict) or set(record) != required:
                raise ValueError(
                    f"Model {model_name!r} must provide exactly {sorted(required)}."
                )
            for field in ("model_version", "calculation_id", "structure_id"):
                if not isinstance(record[field], str) or not record[field].strip():
                    raise ValueError(f"{model_name!r}: {field} must be nonempty text.")

            calculation_id = record["calculation_id"]
            if calculation_id in used_calculation_ids:
                raise ValueError("Calculation identifiers must be distinct.")
            used_calculation_ids.add(calculation_id)

            structure_id = record["structure_id"]
            if shared_structure_id is None:
                shared_structure_id = structure_id
            elif structure_id != shared_structure_id:
                raise ValueError("Different structure identifiers cannot be combined.")

            value = record["value_ev_per_atom"]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{model_name!r}: value_ev_per_atom must be finite.")
            value = float(value)
            energies.append(value)
            validated_predictions[model_name] = {
                "value_ev_per_atom": value,
                "model_version": record["model_version"],
                "calculation_id": calculation_id,
                "structure_id": structure_id,
            }
try:
            mean_value = math.fsum(energies) / len(energies)
            pop_spread = math.sqrt(
                math.fsum((value - mean_value) ** 2 for value in energies)
                / len(energies)
            )
            energy_range = max(energies) - min(energies)
        except (OverflowError, ValueError) as exc:
            raise ValueError("Descriptive energy summary is not numerically finite.") from exc
        if not all(math.isfinite(v) for v in (mean_value, pop_spread, energy_range)):
            raise ValueError("Descriptive energy summary is not numerically finite.")

        return {
            "model_count": len(energies),
            "input_values_ev_per_atom": validated_predictions,
            "arithmetic_mean_of_supplied_values_ev_per_atom": mean_value,
            "population_std_of_supplied_values_ev_per_atom": pop_spread,
            "range_of_supplied_values_ev_per_atom": energy_range,
            "formation_energy_ev_per_atom": None,
            "calibrated_model_uncertainty_ev_per_atom": None,
            "scientific_consensus_score": None,
            "independent_execution_verification": "NOT_VERIFIED",
            "inter_model_energy_reference_alignment": "NOT_VERIFIED",
            "scientific_interpretation": (
                "DESCRIPTIVE ARITHMETIC ONLY on caller-supplied potential energies; "
                "no models executed, no reference alignment, no formation energy, "
                "no calibrated uncertainty, and no physical stability inference."
            ),
