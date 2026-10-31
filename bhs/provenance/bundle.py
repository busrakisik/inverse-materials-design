
"""Save BHS run artifacts without overstating reproducibility.

A saved configuration and manifest do NOT establish a reproduced or
scientifically validated result. Reproducibility must be demonstrated by
independent reruns in a specified software/hardware environment.
"""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import platform


def _jsonable(value):
    """Preserve provenance-aware objects and reject unknown non-JSON objects."""
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _jsonable(value.to_dict())
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError(f"Unsupported artifact value type: {type(value).__name__}")


def _write_json(path, value):
    serialized = json.dumps(
        _jsonable(value), ensure_ascii=False, indent=2, allow_nan=False
    ) + "\n"
    path.write_text(serialized, encoding="utf-8")
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ProvenanceBundleSaver:
    """Record run inputs and outputs; do not certify scientific reproducibility."""

    @staticmethod
    def create_run_bundle(out_dir, config, run_history, final_metrics):
        if not isinstance(config, dict):
            raise TypeError("config must be a dictionary")
        if not isinstance(run_history, list):
            raise TypeError("run_history must be a list")
        if not isinstance(final_metrics, dict):
            raise TypeError("final_metrics must be a dictionary")

        folder = Path(out_dir)
        folder.mkdir(parents=True, exist_ok=True)

        config_path = folder / "input_config.json"
        history_path = folder / "execution_history.json"
        config_sha256 = _write_json(config_path, config)
        history_sha256 = _write_json(history_path, run_history)

        manifest = {
            "artifact_type": "BHS_RUN_RECORD",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "experiment_name": config.get("experiment_name", "BHS_Run"),
            "mode": config.get("mode", "unspecified"),
            "target": config.get("target_composition", "unspecified"),
            "verification_status": "NOT_VERIFIED",
            "reproducibility_status": "NOT_VERIFIED",
            "note": (
                "This bundle records a program execution; it does NOT certify "
                "scientific validity or reproducibility. Check whether evidence "
                "and numeric metrics are measured, predicted, or illustrative. "
                "Independent reruns and environment locking remain necessary."
            ),
            "environment": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "dependencies_locked": False,
            },
            "files": {
                "input_config.json": {"sha256": config_sha256},
                "execution_history.json": {"sha256": history_sha256},
            },
            "final_metrics": _jsonable(final_metrics),
        }
        _write_json(folder / "provenance_manifest.json", manifest)
        return str(folder)

