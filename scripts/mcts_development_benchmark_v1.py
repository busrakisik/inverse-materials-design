"""Exploratory paired MCTS development benchmark. NEVER use independent holdout seeds.

Uses already-examined task seeds 0..29 only. Results are pilot-informed and
cannot establish confirmatory scientific superiority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from pathlib import Path

from scripts.scientific_benchmark_contract_v1 import (
    make_task, MeteredEvaluator, UniformWithoutReplacement, DescriptorGreedy,
)
from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1
from scripts.mcts_puct_policy_v1 import OpenLoopPUCTPolicyV1

STATUS = "EXPLORATORY_DEVELOPMENT_MCTS_COMPARISON_NO_HOLDOUT"
SCENARIOS = ("smooth", "multimodal", "uninformative", "mismatched", "duplicates")
BUDGETS = (1, 5, 10)
VARIANTS = ("random", "greedy", "bayesian_only", "mcts_32_h1", "mcts_32_h3", "mcts_96_h3")
MAX_DEV_SEED = 29


def validate_seeds(seeds):
    seeds = tuple(seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("empty or duplicate development seeds")
    if any(type(s) is not int or not 0 <= s <= MAX_DEV_SEED for s in seeds):
        raise ValueError("only previously examined development seeds 0..29 allowed")
    return seeds


def policy_seed(scenario, seed, variant):
    # Preserve the original pilot's per-policy RNG derivation for legacy policies.
    policy = variant if variant in ("random", "greedy", "bayesian_only") else "mcts"
    material = f"policy:{seed}:{scenario}:{policy}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def create_policy(variant, seed):
    if variant == "random":
        return UniformWithoutReplacement(seed)
    if variant == "greedy":
        return DescriptorGreedy()
    if variant == "bayesian_only":
        return BayesianOnlyPolicyV1(seed)
    if variant in ("mcts_32_h1", "mcts_32_h3", "mcts_96_h3"):
        simulations, horizon = {
            "mcts_32_h1": (32, 1),
            "mcts_32_h3": (32, 3),
            "mcts_96_h3": (96, 3),
        }[variant]
        return OpenLoopPUCTPolicyV1(seed, simulations=simulations, horizon=horizon)
    raise ValueError("unknown policy variant")


def evaluate_one(scenario, seed, budget, variant):
    if scenario not in SCENARIOS or type(budget) is not int or budget not in BUDGETS or variant not in VARIANTS:
        raise ValueError("unsupported benchmark configuration")
    validate_seeds((seed,))
    task = make_task(scenario, seed, n=20)
    policy = create_policy(variant, policy_seed(scenario, seed, variant))
    start = time.perf_counter()
    result = MeteredEvaluator(task, budget).run(policy)
    elapsed = time.perf_counter() - start
    trace = result["trace"]
    if len(trace) != budget or len({r["candidate_id"] for r in trace}) != budget:
        raise RuntimeError("query count or action uniqueness violation")
    values = [r["value"] for r in trace]
    if not all(type(v) in (int, float) and math.isfinite(v) for v in values):
        raise RuntimeError("nonfinite outcome")
    best = max(values)
    # Trusted evaluator only. Never provide this oracle maximum to the policy.
    optimum = max(task._labels.values())
    if best > optimum + 1e-10:
        raise RuntimeError("observed utility exceeds oracle")
    return {
        "status": STATUS, "scenario": scenario, "seed": seed, "budget": budget,
        "variant": variant, "policy_seed": policy_seed(scenario, seed, variant),
        "best_utility": best, "simple_regret": max(0.0, optimum - best),
        "queries": len(trace), "wall_seconds": elapsed,
        "task_public_sha256": task.fingerprint(),
        "selected_ids": [r["candidate_id"] for r in trace],
        "scored_validation_allowed": False,
    }


def run_development(seeds=range(5), *, scenarios=SCENARIOS, budgets=BUDGETS, variants=VARIANTS):
    seeds = validate_seeds(seeds)
    if not scenarios or any(s not in SCENARIOS for s in scenarios) or len(set(scenarios)) != len(scenarios):
        raise ValueError("invalid scenarios")
    if not budgets or any(type(b) is not int or b not in BUDGETS for b in budgets) or len(set(budgets)) != len(budgets):
        raise ValueError("invalid budgets")
    if not variants or any(v not in VARIANTS for v in variants) or len(set(variants)) != len(variants):
        raise ValueError("invalid variants")
    rows = []
    for scenario in scenarios:
        for seed in seeds:
            for budget in budgets:
                expected_task_hash = None
                for variant in variants:
                    row = evaluate_one(scenario, seed, budget, variant)
                    if expected_task_hash is None:
                        expected_task_hash = row["task_public_sha256"]
                    elif row["task_public_sha256"] != expected_task_hash:
                        raise RuntimeError("paired tasks do not match")
                    rows.append(row)
    return rows


def summarize(rows):
    if not rows:
        raise ValueError("no rows")
    paired = {}
    for r in rows:
        k = (r["scenario"], r["seed"], r["budget"])
        if r["variant"] in paired.setdefault(k, {}):
            raise ValueError("duplicate paired row")
        paired[k][r["variant"]] = r
    required = set(VARIANTS)
    if any(set(group) != required for group in paired.values()):
        raise ValueError("missing policy in a paired task")
    out = []
    for scenario in SCENARIOS:
        for budget in BUDGETS:
            matched = [paired[k] for k in sorted(paired) if k[0] == scenario and k[2] == budget]
            if not matched:
                continue
            for variant in (v for v in VARIANTS if v.startswith("mcts_")):
                for comparator in ("random", "greedy", "bayesian_only"):
                    diffs = [group[variant]["best_utility"] - group[comparator]["best_utility"] for group in matched]
                    times = [group[variant]["wall_seconds"] for group in matched]
                    out.append({
                        "scenario": scenario, "budget": budget, "variant": variant,
                        "comparator": comparator, "n_paired": len(diffs),
                        "mean_difference": statistics.mean(diffs),
                        "median_difference": statistics.median(diffs),
                        "positive_fraction": sum(d > 0 for d in diffs) / len(diffs),
                        "mean_policy_wall_seconds": statistics.mean(times),
                        "status": STATUS,
                    })
    return out


def write_outputs(directory, rows, summary, seeds):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in (("development_raw.jsonl", rows), ("development_summary.jsonl", summary)):
        with (directory / name).open("w", encoding="utf-8") as file:
            for entry in content:
                file.write(json.dumps(entry, sort_keys=True, allow_nan=False) + "\n")
    manifest = {
        "status": STATUS, "synthetic_only": True, "exploratory": True,
        "confirmatory": False, "pilot_informed": True,
        "development_seeds": list(validate_seeds(seeds)),
        "holdout_seed_range_excluded": [10000, 10099],
        "scenarios": list(SCENARIOS), "budgets": list(BUDGETS),
        "variants": list(VARIANTS), "n_rows": len(rows),
        "n_tasks_per_variant": len(rows) // len(VARIANTS),
        "paired_policy_count": len(VARIANTS),
        "wall_time_is_environment_dependent": True,
        "same_task_inputs_per_pair": True, "uses_real_materials": False,
        "scored_validation_allowed": False,
        "caveats": [
            "All seeds used here were previously examined in the original pilot.",
            "MCTS configurations were selected after observing earlier exploratory development results.",
            "Development comparisons are descriptive; not independent confirmation.",
            "The open-loop planner does not branch on observation values.",
            "The benchmark executes trusted policies in-process, not an OS security sandbox.",
        ],
    }
    raw = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    (directory / "development_manifest.json").write_bytes(raw)
    (directory / "development_manifest.sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  development_manifest.json\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-seed-count", type=int, default=5)
    parser.add_argument("--out-dir", default="runs/mcts_development_benchmark_v1")
    args = parser.parse_args()
    if not 1 <= args.development_seed_count <= 30:
        parser.error("development-seed-count must be 1..30; holdout is forbidden")
    seeds = tuple(range(args.development_seed_count))
    rows = run_development(seeds)
    manifest = write_outputs(args.out_dir, rows, summarize(rows), seeds)
    print(json.dumps({
        "status": STATUS, "rows": manifest["n_rows"],
        "seeds": len(seeds), "scored_validation_allowed": False
    }, sort_keys=True))


if __name__ == "__main__":
    main()
