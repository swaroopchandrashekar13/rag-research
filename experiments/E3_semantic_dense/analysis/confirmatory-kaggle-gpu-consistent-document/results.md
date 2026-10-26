# Study 1b results — CONFIRMATORY

Queries: squad2 4744, covidqa 1771, cuad 996, qasper 1742

Inference: 95% Wald interval of the mean paired difference; cluster-robust (CR1) standard error over documents, t(G-1) critical value, applied to the point estimate and to each of 1,000 joint document-bootstrap replicates (seed 11; H2 seed 13).

## Hypotheses

| ID | Estimate | 95% CI | Threshold | Verdict |
|---|---:|---|---:|---|
| H4 | 59.0% | [51.3%, 65.0%] | 20.0% | supported |
| H4b | 65.2% | [55.4%, 67.1%] | 10.0% | supported |
| H5 | 19.4% | [16.7%, 39.6%] | 20.0% | inconclusive |
| H5b | 58.3% | [47.9%, 75.0%] | 20.0% | supported |

## H4 sensitivity (share supporting the shorter arm, budget − count)

| Analysis | Estimate | 95% CI |
|---|---:|---|
| a_bh_fdr | 56.9% | — |
| b_without_squad2 | 50.9% | [43.1%, 59.7%] |
| e_all_budgets | 56.8% | [50.7%, 62.8%] |
| f_bm25_only | 63.9% | [54.4%, 72.5%] |
| f_dense_only | 54.2% | [41.7%, 63.0%] |

## Mean chunk length (words) and the shorter arm

| Dataset | fixed-128 | fixed-256 | fixed-512 | semantic-bp | semantic-cl |
|---|---:|---:|---:|---:|---:|
| squad2 | 126 | 249 | 485 | 293 | 456 |
| covidqa | 126 | 247 | 483 | 287 | 455 |
| cuad | 127 | 252 | 495 | 320 | 458 |
| qasper | 126 | 247 | 477 | 278 | 452 |

## Semantic arm supported (descriptive, sensitivity g)

| Claim | Protocol | Universes | Supports semantic | Supports fixed | Inconclusive |
|---|---|---:|---:|---:|---:|
| S5-128 | count | 96 | 59.4% | 14.6% | 26.0% |
| S5-128 | budget | 72 | 8.3% | 75.0% | 16.7% |
| S5-256 | count | 96 | 35.4% | 2.1% | 62.5% |
| S5-256 | budget | 72 | 2.8% | 54.2% | 43.1% |
| S5-512 | count | 96 | 6.2% | 27.1% | 66.7% |
| S5-512 | budget | 72 | 70.8% | 0.0% | 29.2% |
| S6-128 | count | 96 | 51.0% | 0.0% | 49.0% |
| S6-128 | budget | 72 | 0.0% | 95.8% | 4.2% |
| S6-256 | count | 96 | 39.6% | 0.0% | 60.4% |
| S6-256 | budget | 72 | 0.0% | 83.3% | 16.7% |
| S6-512 | count | 96 | 15.6% | 17.7% | 66.7% |
| S6-512 | budget | 72 | 31.9% | 11.1% | 56.9% |

## Provenance of the input run: incomplete

- squad2: manifest records no configuration fingerprint (config_sha256)
- squad2: no code content digest (code_sha256) recorded by the run
- squad2: no input-file digests (inputs_sha256) recorded by the run
- squad2: dense retrieval without a recorded encoder revision (the code pins one)
- covidqa: manifest records no configuration fingerprint (config_sha256)
- covidqa: no code content digest (code_sha256) recorded by the run
- covidqa: no input-file digests (inputs_sha256) recorded by the run
- covidqa: dense retrieval without a recorded encoder revision (the code pins one)
- cuad: manifest records no configuration fingerprint (config_sha256)
- cuad: no code content digest (code_sha256) recorded by the run
- cuad: no input-file digests (inputs_sha256) recorded by the run
- cuad: dense retrieval without a recorded encoder revision (the code pins one)
- qasper: manifest records no configuration fingerprint (config_sha256)
- qasper: no code content digest (code_sha256) recorded by the run
- qasper: no input-file digests (inputs_sha256) recorded by the run
- qasper: dense retrieval without a recorded encoder revision (the code pins one)

## Legacy limitations of the input manifests (reported, not filled in)

- squad2: manifest has no 'error' field
- covidqa: manifest has no 'error' field
- cuad: manifest has no 'error' field
- qasper: manifest has no 'error' field
- qasper/fixed-128.npz: 1 budget-matched selection(s) below the budget; this run format does not record whether the corpus or the ranking depth ran out
- qasper/fixed-256.npz: 1 budget-matched selection(s) below the budget; this run format does not record whether the corpus or the ranking depth ran out
