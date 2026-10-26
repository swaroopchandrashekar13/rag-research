# Study 1b results — CONFIRMATORY

Queries: squad2 4744, covidqa 1771, cuad 996, qasper 1742

Inference: 95% Wald interval of the mean paired difference; query-level standard error, z critical value, applied to the point estimate and to each of 1,000 joint query-bootstrap replicates (seed 11; H2 seed 13).

## Hypotheses

| ID | Estimate | 95% CI | Threshold | Verdict |
|---|---:|---|---:|---|
| H4 | 55.6% | [50.8%, 63.1%] | 20.0% | supported |
| H4b | 65.3% | [56.5%, 68.3%] | 10.0% | supported |
| H5 | 21.5% | [16.7%, 41.7%] | 20.0% | supported |
| H5b | 58.3% | [45.1%, 64.6%] | 20.0% | supported |

## H4 sensitivity (share supporting the shorter arm, budget − count)

| Analysis | Estimate | 95% CI |
|---|---:|---|
| a_bh_fdr | 54.3% | — |
| b_without_squad2 | 48.1% | [42.7%, 58.3%] |
| d_cluster_bootstrap | 59.0% | [51.3%, 65.0%] |
| e_all_budgets | 53.6% | [49.7%, 60.9%] |
| f_bm25_only | 61.1% | [57.2%, 72.5%] |
| f_dense_only | 50.0% | [39.1%, 58.1%] |

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
| S5-128 | count | 96 | 60.4% | 16.7% | 22.9% |
| S5-128 | budget | 72 | 8.3% | 75.0% | 16.7% |
| S5-256 | count | 96 | 39.6% | 4.2% | 56.2% |
| S5-256 | budget | 72 | 2.8% | 52.8% | 44.4% |
| S5-512 | count | 96 | 8.3% | 26.0% | 65.6% |
| S5-512 | budget | 72 | 68.1% | 0.0% | 31.9% |
| S6-128 | count | 96 | 54.2% | 2.1% | 43.8% |
| S6-128 | budget | 72 | 0.0% | 97.2% | 2.8% |
| S6-256 | count | 96 | 46.9% | 0.0% | 53.1% |
| S6-256 | budget | 72 | 0.0% | 86.1% | 13.9% |
| S6-512 | count | 96 | 18.8% | 17.7% | 63.5% |
| S6-512 | budget | 72 | 33.3% | 11.1% | 55.6% |

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
