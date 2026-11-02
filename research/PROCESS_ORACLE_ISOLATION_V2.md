# BHS Process Oracle Isolation Gate v2 — synthetic contract only

**SYNTHETIC ONLY. NOT A SECURITY SANDBOX. NO REAL LABELS. NO BENCHMARK.**

The POSIX worker starts in a separate process session. A selector multiplexes nonblocking stdin writes and stdout reads under a single monotonic per-exchange deadline. Cleanup sends SIGTERM then SIGKILL to the worker process group, even if the group leader already exited. The worker still runs as the same OS user, may access ambient files/network, and can create detached descendants. No least-privilege filesystem, cgroup, seccomp, uid, namespace or network boundary is provided. This code cannot safely process real hidden benchmark labels if accessible to the worker through host files/network. No attempt is made to defend against a malicious worker sending signals, creating setsid descendants, or flooding stderr (stderr is discarded). Do not use on Windows.

CI gate runs 10 deterministic synthetic tests. Keep the original 12-test Process Oracle and 8-test Deadline Gate untouched. Do not merge to main or publish a new release until reviewing logs and security threat model.

Further steps: design actual isolation using a container/OS sandbox with independent unprivileged identity, no accessible held-out labels, network disabled, read-only allowlisted filesystem, enforced resource quotas, supervision, and independent red-team tests. Only then evaluate frozen benchmark protocols.
