# Backup scope, completeness and recovery plan

**This package is intentionally two-tier:**

1. `BHS_CONTINUITY_GITHUB_UPLOAD_2026-11-05.zip`: upload its `research/` hierarchy to the GitHub working branch. It provides compact but deep current master context, exact aggregate real-data reports, experimental history, v5 strategy, prior handoff preserved verbatim and new-chat prompt. **No YAML workflow is required:** the handoff alone does not execute a new scientific experiment.
2. `BHS_FULL_CONTINUITY_2026-11-05_BACKUP.zip`: personal archival copy of the same docs **plus all accessible prior BHS package ZIPs, standalone YAMLs and available historical CI artifact ZIPs**. Archive names may be old, superseded or contain broken pre-fix workflows. Do not commit historical backups to GitHub or blindly restore old code over newer HEAD.

**Critical non-guarantees / what's not in the ZIP:**

- Not a byte-for-byte export of the full ChatGPT transcript, hidden reasoning, every attachment from past chats, or model memory; those are not all accessible in a single context. The best documented state is included, with independent source pointers.
- Not a complete Git repository clone or Git object database. Official GitHub source snapshot `c540a3dbc05f527e4a360deecb310bde68b2c47c` has 399 Git blobs totalling 58,198,095 bytes including unrelated legacy `sample_data/` (e.g. MNIST). GitHub source is authoritative, remains online under its immutable SHA, but is **not redundantly backed up by this file**. To preserve the full source independently, do:

```bash
git clone --mirror https://github.com/busrakisik/inverse-materials-design.git BHS_repository_full_mirror.git
# Persist this mirror on your own separate storage with normal backup/versioning.
# A mirror includes all branches/tags; do not upload its .git objects to GitHub as ordinary files.
```

- The raw NIST `.mat` from a third party is intentionally **not** embedded or redistributed. It can be retrieved from the pinned source under relevant source rights/conditions. The *exact aggregate v1–v4 evidence*, which otherwise expires from GitHub Actions, **is** included.
- Some historical package ZIPs were built prior to later corrections. Their SHA-256 identifies bytes; it is not a guarantee that all old code passes modern tests.
- The Zenodo v1.0.1 release predates audit-branch experiments. The software/archive DOI is not a replacement for new CI artifacts or proof of science.

**Why use GitHub + backup + source pin:** The future ChatGPT conversation can inspect live code and master context without relying on old chat state. Personal copies of the backup and a Git mirror protect against GitHub access failure, ephemeral Actions artifact expiry and accidental branch modification.

**Upload guidance:** Extract `BHS_CONTINUITY_GITHUB_UPLOAD_2026-11-05.zip`, preserve directory `research/` exactly, upload to branch `bhs-scientific-audit`. This creates/updates `BHS_PROJECT_HANDOFF.md`, `BHS_EVIDENCE_REGISTER.json`, `BHS_NEXT_SESSION_PROMPT.md`; adds several new `research/` records. **Check current HEAD for concurrent changes before overwriting** these existing files. Full backup ZIP is for personal storage, not GitHub.
