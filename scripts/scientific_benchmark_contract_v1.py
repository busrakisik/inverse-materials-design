"""Synthetic benchmark contracts ONLY; never execute held-out materials benchmarks."""
from __future__ import annotations
import hashlib, json, math, random
from dataclasses import dataclass

STATUS = 'SYNTHETIC_CONTRACT_ONLY_NOT_SCORED_BENCHMARK'

@dataclass(frozen=True)
class SyntheticTask:
    public: dict
    _labels: dict
    scenario: str
    seed: int

    def __post_init__(self):
        if set(self.public) != set(self._labels) or len(self.public) < 10:
            raise ValueError('invalid candidate mapping')

    def public_view(self):
        return {k: tuple(self.public[k]) for k in sorted(self.public)}

    def fingerprint(self):
        raw=json.dumps({'scenario':self.scenario,'seed':self.seed,'public':self.public},sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()


def make_task(scenario, seed, n=20):
    if scenario not in ('smooth','multimodal','uninformative','mismatched','duplicates'):
        raise ValueError('unknown scenario')
    if isinstance(seed,bool) or not isinstance(seed,int) or isinstance(n,bool) or not isinstance(n,int) or n<10:
        raise ValueError('invalid synthetic parameters')
    rng=random.Random(f'BHS-contract-v1:{scenario}:{seed}')
    public={}; labels={}
    for i in range(n):
        name=f'candidate_{i:03d}'
        x=round(rng.uniform(-1,1),6)
        if scenario=='duplicates': x=round(x,0)
        visible=0.0 if scenario=='uninformative' else x
        public[name]=(visible,)
        y= x if scenario=='smooth' else (math.sin(7*x)+0.1*x if scenario=='multimodal' else (-x if scenario=='mismatched' else rng.uniform(-1,1)))
        labels[name]=round(y,8)
    return SyntheticTask(public,labels,scenario,seed)


class MeteredEvaluator:
    """Trusted host owns labels. Policy is called with public descriptors + prior observations only."""
    def __init__(self, task, budget):
        if isinstance(budget,bool) or not isinstance(budget,int) or not 1<=budget<=len(task.public):
            raise ValueError('invalid budget')
        self._task=task;self.budget=budget;self._seen=set();self._trace=[]

    def run(self, policy):
        public=self._task.public_view()
        for step in range(self.budget):
            observations=tuple((r['candidate_id'],r['value']) for r in self._trace)
            selected=policy.choose(public,observations)
            if not isinstance(selected,str) or selected not in public or selected in self._seen:
                raise ValueError('invalid/repeated policy action')
            self._seen.add(selected)
            value=self._task._labels[selected]
            if not math.isfinite(value):raise ValueError('non-finite outcome')
            self._trace.append({'candidate_id':selected,'value':value,'step':step+1})
        return {'status':STATUS,'scenario':self._task.scenario,'seed':self._task.seed,
                'budget':self.budget,'queries':len(self._trace),
                'trace':list(self._trace),'task_public_sha256':self._task.fingerprint(),
                'real_labels_used':False,'scored_benchmark':False}


class UniformWithoutReplacement:
    def __init__(self,seed):self.rng=random.Random(seed)
    def choose(self,public,observations):
        seen={k for k,_ in observations}
        return self.rng.choice(sorted(set(public)-seen))


class DescriptorGreedy:
    def choose(self,public,observations):
        seen={k for k,_ in observations}
        return sorted((k for k in public if k not in seen),key=lambda k:(-public[k][0],k))[0]
