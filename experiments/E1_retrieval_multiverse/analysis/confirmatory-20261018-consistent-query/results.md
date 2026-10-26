# Study 1 results — CONFIRMATORY

Datasets: squad2, covidqa, cuad, qasper; queries: squad2 4744, covidqa 1771, cuad 996, qasper 1742

Inference: 95% Wald interval of the mean paired difference; query-level standard error, z critical value, applied to the point estimate and to each of 1,000 joint query-bootstrap replicates (seed 11; H2 seed 13).

## Hypotheses

| ID | Estimate | 95% CI | Threshold | Verdict |
|---|---:|---|---:|---|
| H1 | 70.9% | [64.8%, 81.9%] | 20.0% | supported |
| H1b | 27.1% | [15.4%, 33.9%] | 10.0% | supported |
| H2 | dataset η² largest in 100.0% of replicates | — | 95% | supported |
| H3 | 85.4% of universes need n > 500 (median n = 1256) | — | > 50% | supported |

H2 point estimates (η²): dataset 0.614, retriever 0.044, budget 0.096, metric 0.032

## H1 sensitivity analyses (P1: share supporting fixed-512, count − budget)

| Analysis | Estimate | 95% CI |
|---|---:|---|
| a_bh_fdr | 67.6% | — |
| b_without_squad2 | 61.2% | [53.2%, 74.8%] |
| c_default_retriever | 70.8% | [64.6%, 85.4%] |
| d_cluster_bootstrap | 68.9% | [61.6%, 80.9%] |
| e_all_budgets | 73.9% | [68.3%, 84.8%] |

## Verdict shares per claim and protocol

| Claim | Role | A vs B | Protocol | Universes | Supports A | Supports B | Inconclusive |
|---|---|---|---|---:|---:|---:|---:|
| P1 | primary | fixed-128 vs fixed-512 | count | 768 | 0.0% | 78.5% | 21.5% |
| P1 | primary | fixed-128 vs fixed-512 | budget | 576 | 81.2% | 7.6% | 11.1% |
| S1-64 | secondary | fixed-64 vs fixed-128 | count | 768 | 0.0% | 83.9% | 16.1% |
| S1-64 | secondary | fixed-64 vs fixed-128 | budget | 960 | 20.0% | 42.5% | 37.5% |
| S1-128 | secondary | fixed-128 vs fixed-256 | count | 768 | 0.0% | 75.4% | 24.6% |
| S1-128 | secondary | fixed-128 vs fixed-256 | budget | 768 | 60.8% | 6.5% | 32.7% |
| S1-256 | secondary | fixed-256 vs fixed-512 | count | 768 | 0.0% | 63.5% | 36.5% |
| S1-256 | secondary | fixed-256 vs fixed-512 | budget | 576 | 78.0% | 2.1% | 20.0% |
| S2-64 | secondary | fixed-64-o25 vs fixed-64 | count | 768 | 52.5% | 1.7% | 45.8% |
| S2-64 | secondary | fixed-64-o25 vs fixed-64 | budget | 960 | 55.3% | 1.7% | 43.0% |
| S2-128 | secondary | fixed-128-o25 vs fixed-128 | count | 768 | 52.0% | 1.8% | 46.2% |
| S2-128 | secondary | fixed-128-o25 vs fixed-128 | budget | 960 | 54.8% | 1.9% | 43.3% |
| S2-256 | secondary | fixed-256-o25 vs fixed-256 | count | 768 | 36.2% | 3.3% | 60.5% |
| S2-256 | secondary | fixed-256-o25 vs fixed-256 | budget | 768 | 39.8% | 2.9% | 57.3% |
| S2-512 | secondary | fixed-512-o25 vs fixed-512 | count | 768 | 9.6% | 8.3% | 82.0% |
| S2-512 | secondary | fixed-512-o25 vs fixed-512 | budget | 576 | 12.0% | 7.1% | 80.9% |
| S3-64 | secondary | paragraph-64 vs fixed-64 | count | 768 | 62.2% | 5.7% | 32.0% |
| S3-64 | secondary | paragraph-64 vs fixed-64 | budget | 960 | 75.7% | 0.0% | 24.3% |
| S3-128 | secondary | paragraph-128 vs fixed-128 | count | 768 | 60.0% | 1.2% | 38.8% |
| S3-128 | secondary | paragraph-128 vs fixed-128 | budget | 960 | 80.4% | 0.0% | 19.6% |
| S3-256 | secondary | paragraph-256 vs fixed-256 | count | 768 | 50.1% | 2.5% | 47.4% |
| S3-256 | secondary | paragraph-256 vs fixed-256 | budget | 768 | 77.2% | 0.5% | 22.3% |
| S3-512 | secondary | paragraph-512 vs fixed-512 | count | 768 | 14.7% | 1.6% | 83.7% |
| S3-512 | secondary | paragraph-512 vs fixed-512 | budget | 576 | 60.9% | 1.6% | 37.5% |
| S4-64 | exploratory | sentence-64 vs fixed-64 | count | 768 | 58.9% | 6.1% | 35.0% |
| S4-64 | exploratory | sentence-64 vs fixed-64 | budget | 960 | 69.4% | 0.3% | 30.3% |
| S4-128 | exploratory | sentence-128 vs fixed-128 | count | 768 | 49.9% | 0.9% | 49.2% |
| S4-128 | exploratory | sentence-128 vs fixed-128 | budget | 960 | 58.2% | 0.0% | 41.8% |
| S4-256 | exploratory | sentence-256 vs fixed-256 | count | 768 | 19.4% | 1.3% | 79.3% |
| S4-256 | exploratory | sentence-256 vs fixed-256 | budget | 768 | 39.1% | 0.0% | 60.9% |
| S4-512 | exploratory | sentence-512 vs fixed-512 | count | 768 | 6.4% | 0.5% | 93.1% |
| S4-512 | exploratory | sentence-512 vs fixed-512 | budget | 576 | 21.4% | 0.3% | 78.3% |

## Provenance of the input run: incomplete

- squad2: manifest records no configuration fingerprint (config_sha256)
- squad2: no code content digest (code_sha256) recorded by the run
- squad2: no input-file digests (inputs_sha256) recorded by the run
- covidqa: manifest records no configuration fingerprint (config_sha256)
- covidqa: no code content digest (code_sha256) recorded by the run
- covidqa: no input-file digests (inputs_sha256) recorded by the run
- cuad: manifest records no configuration fingerprint (config_sha256)
- cuad: no code content digest (code_sha256) recorded by the run
- cuad: no input-file digests (inputs_sha256) recorded by the run
- qasper: manifest records no configuration fingerprint (config_sha256)
- qasper: no code content digest (code_sha256) recorded by the run
- qasper: no input-file digests (inputs_sha256) recorded by the run

## Legacy limitations of the input manifests (reported, not filled in)

- squad2: manifest config has no 'study' field (historical Study 1 format); treated as '1'
- covidqa: manifest config has no 'study' field (historical Study 1 format); treated as '1'
- cuad: manifest config has no 'study' field (historical Study 1 format); treated as '1'
- qasper: manifest config has no 'study' field (historical Study 1 format); treated as '1'
