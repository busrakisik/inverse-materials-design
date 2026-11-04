"""Exploratory OPEN-LOOP PUCT search on the existing scalar Bayesian synthetic model.

Every simulation samples a latent slope from the current posterior and noisy
candidate responses, then performs selection/expansion/rollout/backpropagation.
The search tree branches on candidate IDs, NOT on observed responses: it does
not plan adaptive observation-contingent policies or implement physical BHS.
Only public descriptors and previously observed results are accepted.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math
import random
from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1

STATUS = 'EXPLORATORY_OPEN_LOOP_PUCT_SYNTHETIC_ONLY_NO_HOLDOUT'

@dataclass
class Node:
    path: tuple[str, ...] = ()
    prior: float = 1.0
    visits: int = 0
    total: float = 0.0
    children: dict[str, 'Node'] = field(default_factory=dict)

    @property
    def q(self) -> float:
        return self.total / self.visits if self.visits else 0.0


class OpenLoopPUCTPolicyV1:
    """Bayesian posterior + open-loop Monte Carlo tree search.

    Remaining planning horizon can be passed at construction but does not
    automatically reflect the evaluator's total query budget. For each choose,
    effective depth is min(horizon, unobserved candidate count).
    """
    def __init__(self, seed: int, *, simulations: int = 96, horizon: int = 3,
                 c_puct: float = 1.25, prior_variance: float = 1.0,
                 noise_variance: float = 0.1):
        if type(seed) is not int or type(simulations) is not int or not 1 <= simulations <= 2000:
            raise ValueError('invalid seed or simulation count')
        if type(horizon) is not int or not 1 <= horizon <= 10:
            raise ValueError('invalid horizon')
        if isinstance(c_puct, bool) or not isinstance(c_puct, (int, float)) or not math.isfinite(c_puct) or c_puct <= 0:
            raise ValueError('invalid PUCT exploration coefficient')
        self._posterior = BayesianOnlyPolicyV1(seed, prior_variance=prior_variance,
                                                noise_variance=noise_variance)
        self._rng = random.Random(seed)
        self.simulations = simulations
        self.horizon = horizon
        self.c_puct = float(c_puct)
        self.noise_variance = float(noise_variance)
        self.last_diagnostics = None

    @staticmethod
    def _priors(remaining: list[str], xs: dict[str, float], mean: float,
                variance: float, noise: float) -> dict[str, float]:
        # Predicted positive improvement above zero; this is a planning heuristic,
        # not evidence of actual material fitness. Positive minimum protects ties.
        scores = {}
        for cid in remaining:
            mu = mean * xs[cid]
            std = math.sqrt(variance * xs[cid] ** 2 + noise)
            z = mu / std
            expected_positive = std * (math.exp(-z * z / 2) / math.sqrt(2 * math.pi) +
                                       z * 0.5 * math.erfc(-z / math.sqrt(2)))
            scores[cid] = max(1e-9, expected_positive)
        total = sum(scores.values())
        return {cid: scores[cid] / total for cid in remaining}

    def choose(self, public, observations):
        mean, variance, xs, seen = self._posterior.posterior(public, observations)
        remaining = sorted(set(xs) - seen)
        if not remaining:
            raise ValueError('all candidates already evaluated')
        depth = min(self.horizon, len(remaining))
        # A real search tree: nodes are progressively expanded, visited and backed up.
        # No hidden evaluator labels are consulted. Rollout responses are simulated.
        root = Node()
        root_priors = self._priors(remaining, xs, mean, variance, self.noise_variance)
        observed_best = max((float(y) for _, y in observations), default=0.0)
        for _ in range(self.simulations):
            latent_w = self._rng.gauss(mean, math.sqrt(variance))
            sampled = {cid: latent_w * xs[cid] + self._rng.gauss(0, math.sqrt(self.noise_variance))
                       for cid in remaining}
            node = root
            visited = [root]
            available = list(remaining)
            selected = []
            for step in range(depth):
                priors = root_priors if step == 0 else self._priors(available, xs, mean, variance, self.noise_variance)
                # Progressive expansion: one unexpanded child per simulation.
                unexpanded = [cid for cid in available if cid not in node.children]
                expanded = False
                if unexpanded:
                    # Prior-directed expansion with deterministic ID tie-breaking.
                    cid = min(unexpanded, key=lambda c: (-priors[c], c))
                    child = Node(node.path + (cid,), prior=priors[cid])
                    node.children[cid] = child
                    expanded = True
                else:
                    # PUCT = empirical value + prior-weighted exploration bonus.
                    # Parent visit count includes preceding simulations.
                    cid = min(available, key=lambda c: (-(
                        node.children[c].q + self.c_puct * priors[c] *
                        math.sqrt(max(1, node.visits)) / (1 + node.children[c].visits)), c))
                    child = node.children[cid]
                selected.append(cid)
                available.remove(cid)
                node = child
                visited.append(node)
                if expanded:
                    break
            # Model-based rollout extends the expanded path to the planned horizon.
            while len(selected) < depth:
                priors = self._priors(available, xs, mean, variance, self.noise_variance)
                cid = min(available, key=lambda c: (-priors[c], c))
                selected.append(cid)
                available.remove(cid)
            reward = max(0.0, max([sampled[c] for c in selected], default=observed_best) - observed_best)
            for v in visited:
                v.visits += 1
                v.total += reward
        # Guarantee all roots are visited for a meaningful comparison. When the
        # caller requests too few simulations, not all actions can be expanded.
        chosen = min(root.children, key=lambda c: (-root.children[c].visits,
                                                  -root.children[c].q, c))
        self.last_diagnostics = {
            'status': STATUS, 'simulations': self.simulations, 'root_visits': root.visits,
            'expanded_root_actions': len(root.children), 'remaining_candidates': len(remaining),
            'horizon': depth, 'chosen': chosen,
            'root_children': {cid: {'visits': child.visits, 'mean_reward': child.q}
                              for cid, child in sorted(root.children.items())},
            'uses_real_hidden_labels': False, 'adaptive_observation_tree': False,
            'physical_validation': False, 'scored_validation_allowed': False,
        }
        return chosen
