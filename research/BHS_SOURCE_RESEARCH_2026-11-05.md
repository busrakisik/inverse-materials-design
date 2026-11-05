# NIST composition-order evidence check — 2026-11-05

- NIST data manifest `usnistgov/remi` (commit `596b04435fb577175264a70c4434f5539b809510`) documents `C` as composition but **does not explicitly identify column-to-element order**, atom fractions vs percentages, independent uncertainties, or cost metadata.
- The repository tree includes `.mat` binary and a brief `data description.txt` in the Fe–Co–Ni folder; no adjacent Fe–Co–Ni parser/readme establishing a column-order mapping was found in that immutable tree.
- The 2022 paper describes the 921-sample experimental ternary data, Kerr rotation and coercivity; it analyzes **property optimization** with Gaussian-process acquisition functions and CAMEO, not true-physical-mechanism discrimination. Expected Improvement is described as strong overall, with landscape complexity differing across properties.
- Paper: https://academic.oup.com/ooms/article/2/1/itac006/6637521
- Official NIST: https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery
- Raw dataset source: https://github.com/usnistgov/remi/tree/nist-pages/data/Combinatorial%20Libraries/Fe-Co-Ni
- **Unresolved:** authoritative `C` column mapping. Do NOT promote an inferred mapping to verified based on dataset name, visual ternary figure, or row sums. The per-row aggregates and internal shapes are in the earlier CI artifacts; prefer inspecting those rather than repeating an audit.

Next source investigation: follow the publication's code reference and supplemental material, or ask the paper's corresponding author to clarify the MATLAB `C` column order and normalization, ideally with a specific README/source code snippet. Until resolved, one may perform purely anonymous-coordinate mathematical diagnostics, expressly **not** Fe-labelled model interpretation. No real-data BHS scoring yet.
