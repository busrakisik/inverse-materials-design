# Evidence reconciliation v1 — authenticated redirect repair

## Failure verified
GitHub Actions run 41608431690: 10/10 unit tests passed. Live artifact step failed after a 302 redirect with HTTP 401. No successful live reconciliation report was produced.

## Change
`download_artifact` requests GitHub's Actions artifact API with `GITHUB_TOKEN`, blocks automatic cross-host redirects, validates the signed redirect destination, and sends a fresh request **without the token** to the GitHub-hosted artifact blob. Untrusted or insecure locations are rejected. Test code uses mocked HTTP requests and never contacts production. Failures do not expose bearer secrets or signed URLs.

No secrets or permissions are added to the repository. CI continues to require `actions: read` and `contents: read`, and existing artifact hashes are unchanged. CI runs 18 tests (the existing 10 and 8 redirect/security tests), then the actual five-artifact reconciliation.

## Limitations
The error's precise cause is not conclusively established by the 401 alone. A valid signed URL, artifact retention, and GitHub token permissions must be confirmed by a new live CI run. This change does not prove experimental independence or permit any holdout evaluation. `scored_validation_allowed` remains `false`.

## Operator instructions
Upload all four files to `bhs-scientific-audit`, using the paths within this package. Commit once; push triggers the workflow. There is no confirmation input and no need to manually rerun a successful automatic workflow. Past failed CI runs remain in history; evaluate the newest run and its artifact contents.
