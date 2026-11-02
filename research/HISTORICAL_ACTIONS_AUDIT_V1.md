# BHS Historical Actions Audit v1

**READ-ONLY METADATA / NOT A SEED AUDIT COMPLETION / HOLDOUT NOT RUN**

Fetches paginated GitHub Actions *run metadata*, records workflow IDs, commits, timestamps and conclusions, and checks complete pagination against the API's reported total. It does **not** read historical log/artifact contents, run any candidate tasks, certify absence of seed collisions, lock the environment or approve independent validation.

Usage: `python -m unittest discover -s tests -p 'test_historical_actions_audit_v1.py' -v` and `GITHUB_TOKEN=... python -m scripts.historical_actions_audit_v1` (GitHub Actions provides a read-only token). Do not put tokens in committed files.

The historical seed audit remains **incomplete** until available pilot artifacts/logs are inventoried, external/local experiments are reviewed, and seed exclusions are independently documented. No algorithm or physics benchmark results are generated.

The current repository's root `requirements.txt` has open ranges and legacy platform-dependent dependencies; it is **not** an environment lock. A separate stdlib-only validation runner environment with exact interpreter/container digest and source SHA record is required before freeze.

Commit: `test(validation): inventory GitHub Actions history without accessing holdout`

Manual workflow dispatch: branch `bhs-scientific-audit`; **no confirmation input defined**. Push on the branch also triggers this workflow.
