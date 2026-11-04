"""Exploratory observation-conditioned Bayesian planning on public synthetic descriptors.

NOT a verified BAMCP/POMCP implementation. This finite outcome-bin tree is a
non-myopic prototype and is not confirmatory, secure, or physically validated.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import math
import random
from typing import Dict
from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1

STATUS = 'OBSERVATION_CONDITIONED_SYNTHETIC_SEARCH_EXPLORATORY_NO_HOLDOUT'

@dataclass
class Edge:
    visits: int = 0
    total: float = 0.0
    outcomes: Dict[int, 'TreeNode'] = field(default_factory=dict)

@dataclass
class TreeNode:
    visits: int = 0
    actions: Dict[str, Edge] = field(default_factory=dict)


def bayes_update(mean: float, variance: float, x: float, y: float, noise_variance: float):
    """Analytic scalar conjugate Gaussian posterior update."""
    if not all(math.isfinite(v) for v in (mean, variance, x, y, noise_variance)):
        raise ValueError('nonfinite Bayesian update')
    if variance <= 0 or noise_variance <= 0:
        raise ValueError('nonpositive variance')
    updated_variance = 1.0 / (1.0 / variance + x*x / noise_variance)
    updated_mean = updated_variance * (mean / variance + x*y / noise_variance)
    if not all(math.isfinite(v) for v in (updated_mean, updated_variance)):
        raise ValueError('numerical posterior failure')
    return updated_mean, updated_variance


def outcome_bin(y: float, mean: float, predictive_std: float) -> int:
    """Three innovation bins, conditional on the predictive belief BEFORE update."""
    if not all(math.isfinite(z) for z in (y, mean, predictive_std)) or predictive_std <= 0:
        raise ValueError('invalid predictive outcome')
    z = (y - mean) / predictive_std
    return -1 if z < -0.5 else (1 if z > 0.5 else 0)


class BeliefStateSearchV1:
    """Finite observation-bin action/chance tree; diagnostics intentionally honest.

    A simulation samples one latent slope from the *root* Gaussian posterior and
    noisy future outcomes conditionally on that slope. The in-simulation belief
    is updated after every imaginary observation. Outcomes are binned for tree
    sharing; the exact sampled posterior is NOT represented by the bin node.
    """
    def __init__(self, seed: int, *, simulations=96, horizon=3, c_uct=1.0,
                 prior_variance=1.0, noise_variance=0.1):
        if type(seed) is not int or type(simulations) is not int or not 1 <= simulations <= 2000:
            raise ValueError('invalid seed/simulations')
        if type(horizon) is not int or not 1 <= horizon <= 8:
            raise ValueError('invalid horizon')
        if type(c_uct) not in (int, float) or not math.isfinite(c_uct) or c_uct <= 0:
            raise ValueError('invalid UCT coefficient')
        self._model = BayesianOnlyPolicyV1(seed, prior_variance=prior_variance,
                                            noise_variance=noise_variance)
        self._rng = random.Random(seed)
        self.simulations = simulations
        self.horizon = horizon
        self.c_uct = float(c_uct)
        self.noise_variance = float(noise_variance)
        self.last_diagnostics = None

    @staticmethod
    def _rank(remaining, xs, mean, variance, noise):
        # Transparent expected-positive-improvement heuristic; no oracle labels.
        def score(cid):
            mu = mean * xs[cid]
            sd = math.sqrt(variance * xs[cid]**2 + noise)
            z = mu / sd
            return sd * math.exp(-z*z/2) / math.sqrt(2*math.pi) + mu * 0.5 * math.erfc(-z/math.sqrt(2))
        return sorted(remaining, key=lambda cid: (-score(cid), cid))

    def _select(self, node, remaining, xs, mean, variance):
        unexpanded = [cid for cid in self._rank(remaining, xs, mean, variance, self.noise_variance)
                      if cid not in node.actions]
        if unexpanded:
            cid = unexpanded[0]
            node.actions[cid] = Edge()
            return cid, True
        # UCT on action edges; tree alternates action and discrete observation nodes.
        cid = min(remaining, key=lambda c: (-(node.actions[c].total / node.actions[c].visits +
                          self.c_uct * math.sqrt(math.log(max(2, node.visits + 1)) /
                                                 node.actions[c].visits)), c))
        return cid, False

    def choose(self, public, observations):
        mean0, variance0, xs, seen = self._model.posterior(public, observations)
        remaining0 = sorted(set(xs) - seen)
        if not remaining0:
            raise ValueError('pool exhausted')
        root = TreeNode()
        depth_limit = min(self.horizon, len(remaining0))
        observed_best = max((float(y) for _, y in observations), default=0.0)
        outcome_edges = 0
        for _ in range(self.simulations):
            latent = self._rng.gauss(mean0, math.sqrt(variance0))
            node = root
            mean, variance = mean0, variance0
            available = list(remaining0)
            best = observed_best
            path = []
            new_branch = False
            for _step in range(depth_limit):
                if node is None:
                    cid = self._rank(available, xs, mean, variance, self.noise_variance)[0]
                    edge = None
                else:
                    cid, expanded = self._select(node, available, xs, mean, variance)
                    edge = node.actions[cid]
                    path.append((node, edge))
                x = xs[cid]
                predicted_mean = mean * x
                predictive_std = math.sqrt(variance * x*x + self.noise_variance)
                outcome = latent*x + self._rng.gauss(0, math.sqrt(self.noise_variance))
                branch = outcome_bin(outcome, predicted_mean, predictive_std)
                mean, variance = bayes_update(mean, variance, x, outcome, self.noise_variance)
                best = max(best, outcome)
                available.remove(cid)
                if edge is not None:
                    if branch not in edge.outcomes:
                        edge.outcomes[branch] = TreeNode()
                        outcome_edges += 1
                        new_branch = True
                    node = edge.outcomes[branch]
                    if new_branch:
                        # Rollout after first newly created chance branch.
                        node = None
                else:
                    node = None
            reward = max(0.0, best - observed_best)
            for visited, edge in path:
                visited.visits += 1
                edge.visits += 1
                edge.total += reward
        # Every expanded root edge has at least one visit.
        chosen = min(root.actions, key=lambda c: (-root.actions[c].visits,
                            -root.actions[c].total / root.actions[c].visits, c))
        self.last_diagnostics = {
            'status': STATUS, 'root_visits': root.visits,
            'root_actions_expanded': len(root.actions),
            'root_children': {k: {'visits': v.visits, 'mean_reward': v.total/v.visits,
                                  'outcome_bins_visited': sorted(v.outcomes)}
                              for k, v in sorted(root.actions.items())},
            'observation_branches_created': outcome_edges,
            'posterior_updates_during_simulation': True,
            'observation_contingent_tree': True,
            'observation_nodes_are_approximate_bins': True,
            'formal_bamcp_correctness_established': False,
            'uses_hidden_labels': False,
            'scored_validation_allowed': False,
            'physical_validation': False,
            'simulations': self.simulations,
            'horizon': depth_limit,
            'chosen': chosen,
        }
        return chosen


def run_fixed_development_demo():
    from scripts.scientific_benchmark_contract_v1 import make_task, MeteredEvaluator
    task = make_task('smooth', 7, n=20)
    policy = BeliefStateSearchV1(13, simulations=96, horizon=3)
    result = MeteredEvaluator(task, 5).run(policy)
    return {'status': STATUS, 'queries': result['queries'],
            'trace': result['trace'], 'last_diagnostics': policy.last_diagnostics,
            'development_task': 'smooth/7', 'independent_holdout_used': False,
            'scored_validation_allowed': False}


def main():
    import argparse
    import hashlib
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='runs/belief_state_search_v1')
    args = parser.parse_args()
    result = run_fixed_development_demo()
    folder = Path(args.out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    (folder/'development_demo.json').write_bytes(data)
    (folder/'development_demo.sha256').write_text(hashlib.sha256(data).hexdigest()+'  development_demo.json\n')
    print(json.dumps({'status': STATUS, 'queries': result['queries'],
                      'scored_validation_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
