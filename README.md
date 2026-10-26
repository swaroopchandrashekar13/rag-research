# Chunking verdicts depend on the evaluation protocol

Code, data manifests, stored results and the manuscript for a multiverse analysis of chunking comparisons in
retrieval-augmented generation (RAG).

**Question.** Chunking studies often retrieve a fixed number of chunks (top-*k*), so a longer chunk also brings more
text. Does the verdict of a chunking comparison change when retrieval is matched on a word budget instead?

**Studies.**

| Study | Directory | What it does |
|---|---|---|
| Study 1 (E1) | `experiments/E1_retrieval_multiverse/` | 16 chunkers (fixed, overlapping, sentence and paragraph packing; 64–512 words) × 16 BM25 configurations × count- and budget-matched selection × 3 evidence-span metrics, on SQuAD 2.0, COVID-QA, CUAD and Qasper |
| Study 1b (E3) | `experiments/E3_semantic_dense/` | semantic breakpoint and clustering chunkers, BM25 and BGE-M3 dense retrieval, same queries and metrics |
| Answer check (E2) | `experiments/E2_generation/` | exploratory: Qwen3-4B answers at top-5 and at a 1,024-word budget, 50 queries per dataset |

Both retrieval studies use 9,253 held-out (confirmatory) queries. The planned hypotheses, thresholds and deviation logs
are in `research/`; the results summaries are `experiments/*/RESULTS.md`; the manuscript is `manuscript/main.tex`.

**Inference.** A universe's verdict is the sign of a 95% Wald interval for its mean paired difference, with the
standard error computed at the sampling unit (queries, or documents with a cluster-robust standard error). The same
rule defines every point estimate and every joint-bootstrap replicate. The analysis plans specified a mixed
computation (percentile-bootstrap verdicts for estimates, normal-approximation verdicts in the replicates); it is kept
as `--inference planned`, and both are reported (`experiments/README.md`).

## Layout

| Path | Contents |
|---|---|
| `src/ragmv/` | data loaders, chunking, retrieval, budget selection, metrics, statistics, analyses, figures, generation |
| `experiments/` | runs (`runs/`), analyses (`analysis/`), Kaggle notebook scripts, results summaries; `statistical_checks/`, `budget_underfill/`, `SHA256SUMS` |
| `research/` | problem statement, analysis plans for Study 1 and Study 1b, errata |
| `data/MANIFEST.yaml` | dataset sources, SHA-256 digests and licences (the data themselves are downloaded, not stored) |
| `manuscript/` | LaTeX source, generated macros (`numbers.tex`), tables, figures and bibliography, build scripts |
| `literature/` | bibliography with verification levels, search log, evidence matrix |
| `tools/` | validation, result comparison, independent statistics, claim tracing, post-hoc analyses, rerun comparison, bibliography checks |
| `licenses/` | licence texts of third-party material that must accompany it (COVID-QA, Apache-2.0) |
| `tests/` | test suite |
| `requirements/`, `env/` | dependency sets; the recorded and validation environments |

## Setup

Python 3.12 or 3.13 on Linux or macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements/core.txt -r requirements/test.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pytest -q -rs          # data-dependent tests are skipped until the data are downloaded
```

`env/validation/lock-py3.13.txt` pins every transitive package of a tested environment. Generation needs
`requirements/generation.txt` (llama-cpp-python is built from source) and dense retrieval `requirements/dense.txt`.

## Data

```bash
.venv/bin/python -I -m ragmv.fetch                    # downloads into data/raw/ and checks every digest
.venv/bin/python -I -m ragmv.fetch --verify-only
RAGMV_DATA_ROOT=data/raw .venv/bin/python -m pytest -q -rs
.venv/bin/python -I tools/validate_artifacts.py --data-root data/raw
```

The validator checks the stored runs (manifests, query lists, arrays, chunk files, generation logs, the checksums in
`experiments/SHA256SUMS`) and, with the data, rebuilds the splits, gold spans, chunk partitions and Tier 2 inputs.

## Running the experiments

New runs always go to new directories; the stored runs are never overwritten.

```bash
python -I -m ragmv.run   --dataset squad2 --split confirmatory --out experiments/E1_retrieval_multiverse/runs/<new>
python -I -m ragmv.run1b --dataset squad2 --split confirmatory --out experiments/E3_semantic_dense/runs/<new> --device cuda
python -I -m ragmv.generate --backend llama --model qwen3-4b-q4_k_m --dataset squad2 --out experiments/E2_generation/runs/<new>
```

Study 1 runs on a CPU in minutes. Study 1b (BGE-M3 embeddings) and the answer check (Qwen3-4B) need a GPU in practice.
On Kaggle, attach this project as a dataset (the folder or a .zip) and run, from one notebook cell,
`%run /kaggle/input/<dataset>/experiments/E3_semantic_dense/notebook_study1b.py` or
`.../experiments/E2_generation/notebook_tier2.py` with a T4 GPU and internet access. The scripts copy the code to
local disk, print its content digest, write everything to the notebook output and can resume from an earlier
session's output (`RAGMV_RESUME_FROM`). `experiments/E2_generation/run_tier2.py` runs the answer check on a local
machine.

## Analyses, tables, figures and the manuscript

```bash
python -I -m ragmv.analyze   --run experiments/E1_retrieval_multiverse/runs/confirmatory-20261018 --label CONFIRMATORY --out W/e1      # add --unit document, or --inference planned
python -I -m ragmv.analyze1b --run experiments/E3_semantic_dense/runs/confirmatory-kaggle-gpu --label CONFIRMATORY --out W/e3
python -I -m ragmv.analyze_generation --run experiments/E2_generation/runs/qwen3-4b-kaggle-gpu --out W/e2
python -I tools/compare_results.py experiments/E1_retrieval_multiverse/analysis/confirmatory-20261018-consistent-query/results.json W/e1/results.json
python -I tools/independent_stats.py --out-json W/stats.json --out-md W/stats.md
python -I manuscript/build_displays.py --out W/displays --compare manuscript   # numbers.tex, tables, figures, refs.bib
python -I tools/trace_claims.py                                                # recomputes every number used in main.tex
python -I manuscript/build_pdf.py --workdir W/build                            # TeX Live, latexmk; named and anonymous PDF
```

`W` is any new directory. `compare_results.py` fails on any changed scientific value. Post-hoc analyses:
`ragmv.posthoc` (character-based metrics on re-executed BM25 selections), `tools/budget_underfill_census.py` and
`tools/underfill_bound.py`, `tools/gold_containment.py` (needs the data), `tools/generation_sensitivity.py`
(truncated answers, document resampling). `tools/pilot_reconcile.py` reproduces the stored pilot intervals.

## Re-running the GPU experiments (optional)

No reported result needs a new GPU run. To check that the stored dense-retrieval run reproduces on new hardware, run
`experiments/E3_semantic_dense/notebook_study1b.py` on Kaggle with `RAGMV_SPLIT=confirmatory` and
`RAGMV_RUN_NAME=confirmatory-kaggle-gpu-rerun` (instructions at the top of the file; the stored manifests record
about 7 minutes of sentence embedding on a T4 but not the chunk-embedding time; the run resumes across sessions). The notebook analyses the new run with both procedures and compares it cell by cell with the stored run
(`tools/compare_rerun.py`). Unpack the downloaded `study1b_results.zip` into `experiments/E3_semantic_dense/`
(`runs/<name>`, `analysis/<name>-*`), then run `tools/validate_artifacts.py` and the comparison locally.

## Known limitations

- The stored runs predate the run format that records digests of the code and inputs; their provenance rests on the
  manifests and on re-execution. BM25 retrieval re-executed from the public data reproduces every stored score and
  word count. Dense retrieval and generation were not re-executed (GPU), and half-precision embeddings and greedy
  generation can differ across hardware.
- The stored analysis of the Study 1 pilot predates two logged changes (sensitivity intervals from 200 joint
  replicates instead of 1,000; query resampling inside the document-cluster interval). `tools/pilot_reconcile.py`
  reproduces its 8 affected bounds exactly with those settings; the current code moves them by at most 1.85 points
  and changes no estimate or verdict. The confirmatory analyses recompute exactly.
- H5 (dense P1) sits at its threshold: 21.5 points (supported) at the query unit and 19.4 points (inconclusive) at
  the document unit and under the planned computation. It is reported as unresolved.
- The evidence metrics are computed on words; the plans define them on characters (see `research/ERRATA_analysis_plans.md`).
- Two budget-matched dense selections fell short of their budget; `experiments/budget_underfill/` bounds their effect.

## Licence

Code: MIT (`LICENSE`). Results, documents and figures: CC BY 4.0, except third-party material described in
`LICENSE-DATA.md`. The source datasets are not redistributed.
