# Licence for results, documents and figures

Copyright (c) 2026 Swaroop Chand J C

- **Code** (`src/`, `tools/`, `tests/`, `manuscript/*.py`, `experiments/**/*.py`, `.github/workflows/`): MIT, see
  [`LICENSE`](LICENSE).
- **Material produced in this project** (analysis plans and deviation logs, run manifests, per-query metric values,
  analyses, tables, figures, manuscript sources, literature notes): Creative Commons Attribution 4.0 International
  (CC BY 4.0, <https://creativecommons.org/licenses/by/4.0/legalcode>), except the third-party material below.

## Third-party material (not covered by the licences above)

| Material | Where | Terms |
|---|---|---|
| Gold answer strings (`answers`) and model answers (`response`), which often reproduce passage wording | `experiments/E2_generation/runs/**/generations.jsonl` | the source datasets' terms: SQuAD 2.0 (Rajpurkar et al., 2018) CC BY-SA 4.0; COVID-QA (Möller et al., 2020) Apache-2.0; CUAD (Hendrycks et al., 2021) and Qasper (Dasigi et al., 2021) CC BY 4.0. ShareAlike applies to adaptations of SQuAD text. CUAD's creators make no representation about the licence status of the underlying EDGAR contracts |
| Dataset question identifiers (CUAD's contain the contract's EDGAR file name, title and clause category) | query lists, job metadata, generation logs, analysis outputs | the datasets' terms |
| Model outputs | generation logs | produced with Qwen3-4B (`Qwen/Qwen3-4B-GGUF`, Apache-2.0) and, in one stopped run, the Gemini API (Google's terms); dense retrieval used BAAI/bge-m3 (MIT). No model weights are included |
| Bibliographic records and short quotations | `literature/` | ACL Anthology records CC BY 4.0 (2016 onwards); arXiv metadata CC0; Semantic Scholar API responses under its API licence; quoted works remain under their authors' or publishers' terms |

The source datasets are not redistributed: `python -I -m ragmv.fetch` downloads them from their publishers and checks
the SHA-256 digests in [`data/MANIFEST.yaml`](data/MANIFEST.yaml), which also records each licence and where it was
read. To share the generation results without any dataset or model text, export the metrics-only form:
`python -I -m ragmv.metrics_form --run experiments/E2_generation/runs/<run> --out <new directory>`. It keeps every
score, flag and identifier needed by the analysis and drops the answer, response and prompt text; the analysis reads
it unchanged. COVID-QA's Apache-2.0 licence asks that its licence text accompany redistributed material; the COVID-QA
repository's licence file is included as [`licenses/COVID-QA-Apache-2.0.txt`](licenses/COVID-QA-Apache-2.0.txt)
(the repository has no NOTICE file). The CC licences require attribution and a link to the licence, given above and
in the citations; SQuAD-derived strings remain under CC BY-SA 4.0. Because CUAD's creators make no representation
about the contracts' licence status, the metrics-only form is the safer choice for any public redistribution of the
generation logs. These notes describe the files; they are not legal advice.
