
# BEGIN OF COMPLETE BHS LEGACY SEARCH PLANNER — CHECK THIS LINE ON GITHUB
"""Fail-closed legacy compute-budget interface for the BHS research prototype.

NO GPU allocation, MLFF/DFT inference, resource booking, calibrated
uncertainty assessment, or adaptive tree search occurs in this module.
Calling the method cannot reserve compute resources or execute any engine.
The legacy method name is retained for compatibility with older imports.
"""

import math
from typing import Any, Dict


class AdaptiveBudgetPlanner:
    """Expose caller-supplied inputs without manufacturing compute results."""

    @staticmethod
    def allocate_and_evaluate(candidate_uncertainty: float) -> Dict[str, Any]:
        """Describe a *non-executed* budget decision safely.

        This API receives only a numeric uncertainty value. It does not
        receive its unit, model calibration, provenance, available GPUs,
        measured runtimes, model versions, or objective constraints.
        It therefore cannot justify an execution tier or GPU-hour estimate.
        """
        raw = candidate_uncertainty
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError("candidate_uncertainty must be a finite nonnegative number.")
        try:
            value = float(raw)
        except (OverflowError, ValueError) as exc:
            raise ValueError("candidate_uncertainty cannot be represented safely.") from exc
        if not math.isfinite(value) or value < 0:
            raise ValueError("candidate_uncertainty must be finite and nonnegative.")

        return {
            "input_candidate_uncertainty": value,
            "uncertainty_provenance": "CALLER_SUPPLIED_NOT_VERIFIED",
            "uncertainty_calibration_status": "NOT_VERIFIED",
            "uncertainty_unit": None,
            "execution_tier": None,
            "tier_selection_status": "NOT_EVALUATED",
            "active_engines": [],
            "model_execution_status": "NOT_RUN",
            "allocated_compute": None,
            "allocated_gpu_hours": None,
            "budget_status": "NOT_ALLOCATED",
            "compute_reservation_status": "NOT_REQUESTED",
            "resource_estimate_status": "NOT_EVALUATED",
            "reasoning": (
                "NO COMPUTE WAS ALLOCATED OR EXECUTED. The supplied uncertainty "
                "has no verified unit or calibration and is not sufficient "
                "to select CHGNet, MACE, M3GNet, DFT, or a GPU-hour budget. "
                "Resource allocation requires a documented policy, actual "
                "available resources, valid model provenance, and measured "
                "or independently justified runtime estimates."
            ),
        }

# END OF COMPLETE BHS LEGACY SEARCH PLANNER — CHECK THIS LINE ON GITHUB

