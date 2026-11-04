"""Fixed-development-task-only MCTS diagnostics. No independent holdout scoring."""
import hashlib
import json
from pathlib import Path
from scripts.mcts_puct_policy_v1 import OpenLoopPUCTPolicyV1, STATUS
from scripts.scientific_benchmark_contract_v1 import make_task, MeteredEvaluator


def run_demo():
    task = make_task('smooth', 7, n=20)  # Pre-existing development seed ONLY
    policy = OpenLoopPUCTPolicyV1(seed=13, simulations=96, horizon=3)
    result = MeteredEvaluator(task, 5).run(policy)
    return {
        'status': STATUS,
        'scenario': 'smooth', 'development_seed': 7,
        'policy_seed': 13, 'budget': 5,
        'queries': result['queries'],
        'candidate_ids': [x['candidate_id'] for x in result['trace']],
        'root_diagnostics_last_step': policy.last_diagnostics,
        'independent_holdout_run': False,
        'physical_materials_test': False,
        'scored_validation_allowed': False,
    }


def main():
    report = run_demo()
    folder = Path('runs/mcts_puct_dev_v1')
    folder.mkdir(parents=True, exist_ok=True)
    b = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    (folder/'dev_demo.json').write_bytes(b)
    (folder/'dev_demo.sha256').write_text(hashlib.sha256(b).hexdigest()+'  dev_demo.json\n')
    print(json.dumps({'status':STATUS,'queries':report['queries'],'scored_validation_allowed':False}))

if __name__ == '__main__': main()
