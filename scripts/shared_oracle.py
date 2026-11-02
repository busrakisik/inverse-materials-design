"""BHS synthetic-only oracle contract. Not a security boundary or real benchmark."""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping

STATUS = 'SYNTHETIC_SOFTWARE_TEST_NOT_MATERIALS_BENCHMARK'

@dataclass(frozen=True)
class Observation:
    candidate_id: str
    value: float
    step: int

@dataclass(frozen=True)
class PublicView:
    candidate_ids: tuple[str, ...]
    remaining_budget: int
    observations: tuple[Observation, ...]

class ControlledOracle:
    """Trusted harness component; NEVER hand this object or underlying labels to policies.

    This class only enforces contractual access inside trusted Python code. A
    malicious policy running in the same interpreter is NOT sandboxed.
    """
    def __init__(self, labels: Mapping[str, float], *, budget: int):
        if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
            raise ValueError('budget must be a positive integer')
        if not labels or any(not isinstance(k, str) or not k for k in labels):
            raise ValueError('nonempty string IDs required')
        if budget > len(labels):
            raise ValueError('budget exceeds candidate pool')
        import math
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in labels.values()):
            raise ValueError('finite numeric labels required')
        self.__answers = MappingProxyType(dict(labels))
        self.__ids = tuple(sorted(labels))
        self.__budget = budget
        self.__observed: dict[str, Observation] = {}

    def public_view(self) -> PublicView:
        return PublicView(self.__ids, self.__budget - len(self.__observed), tuple(self.__observed.values()))

    def query(self, candidate_id: str) -> Observation:
        if not isinstance(candidate_id, str) or candidate_id not in self.__answers:
            raise ValueError('unknown candidate ID')
        if candidate_id in self.__observed:
            raise ValueError('candidate already queried')
        if len(self.__observed) >= self.__budget:
            raise ValueError('query budget exhausted')
        obs = Observation(candidate_id, float(self.__answers[candidate_id]), len(self.__observed)+1)
        self.__observed[candidate_id] = obs
        return obs


def run_synthetic_trial(*, labels: Mapping[str, float], budget: int,
                        select: Callable[[PublicView], str]) -> dict:
    """Callback gets only immutable public views; not the oracle instance.

    This function does not promise isolation from an arbitrary callback's
    closures, Python introspection, global variables, or operating system.
    """
    oracle = ControlledOracle(labels, budget=budget)
    trace = []
    for _ in range(budget):
        view = oracle.public_view()
        choice = select(view)
        obs = oracle.query(choice)
        trace.append({'candidate_id':obs.candidate_id,'step':obs.step})
    return {'status':STATUS,'budget':budget,'queries_consumed':len(trace),
            'trace':trace,'contains_labels':False,'real_dataset_used':False,
            'benchmark_run':False}
