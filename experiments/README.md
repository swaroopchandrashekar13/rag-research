# Experiments

| ID | Directory | Status |
|---|---|---|
| E1 retrieval multiverse | `E1_retrieval_multiverse/` | confirmatory run done (`RESULTS.md`) |
| E2 generation (Tier 2, exploratory) | `E2_generation/` | done (`RESULTS.md`); analysed run `runs/qwen3-4b-kaggle-gpu` |
| E3 semantic chunking + dense retrieval (Study 1b) | `E3_semantic_dense/` | confirmatory run done (`RESULTS.md`) |

Conventions: `runs/<run_id>/<dataset>/` holds `manifest.json` (status, configuration, package versions, platform,
timings, peak memory and chunk statistics; runs created with the current runners also record a SHA-256 of the
configuration, of the code and of every input file), `queries.json` (question IDs and document indices only, no
text) and one `.npz` of per-query metric values per chunking. `analysis/<run_id>/` holds `results.json`, `results.md`
and figures written by `python -I -m ragmv.analyze` (or `analyze1b`, `analyze_generation`) and `python -I -m
ragmv.figures`. Every result file states EXPLORATORY, CONFIRMATORY, SMOKE or POSTHOC. Stored runs and analyses are
never overwritten: new analyses go to new directories; `analysis/posthoc-*` hold the post-hoc sensitivity analyses.

Analyses of the confirmatory runs come in three versions. `analysis/<run_id>/` is the computation the analysis plans
specify (`--inference planned`). `analysis/<run_id>-consistent-query/` and `analysis/<run_id>-consistent-document/`
use one Wald verdict rule for point estimates and bootstrap replicates, with queries or documents as the sampling
unit (the default `--inference consistent`, `--unit query|document`); the manuscript reports these.
`E1_retrieval_multiverse/analysis/pilot-exploratory-20261018-reconciliation/` shows how the stored pilot analysis,
computed before two logged changes to its sensitivity intervals, relates to the current code
(`tools/pilot_reconcile.py`).

Other folders: `statistical_checks/` (an independent re-implementation of the planned statistics, plus the post-hoc
checks the manuscript reports; `tools/independent_stats.py`) and `budget_underfill/` (a census of budget-matched
selections that fell short of their budget, and a post-hoc bound on their effect, for the planned computation
(`bound.json`) and the reported one (`bound-consistent.json`)). `SHA256SUMS` lists the stored run
and analysis files (`sha256sum -c SHA256SUMS` from this folder).

The Gemini (`runs/gemini36flash-20261019`, 21 rows) and CPU (`runs/qwen3-4b-20261019`, 198 rows) generation runs were
stopped before completion; they are kept and not analysed.
