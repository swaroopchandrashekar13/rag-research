# Study 1 results — CONFIRMATORY

Datasets: squad2, covidqa, cuad, qasper; queries: squad2 4744, covidqa 1771, cuad 996, qasper 1742

Inference: 95% Wald interval of the mean paired difference; cluster-robust (CR1) standard error over documents, t(G-1) critical value, applied to the point estimate and to each of 1,000 joint document-bootstrap replicates (seed 11; H2 seed 13).

## Hypotheses

| ID | Estimate | 95% CI | Threshold | Verdict |
|---|---:|---|---:|---|
| H1 | 68.9% | [61.6%, 80.9%] | 20.0% | supported |
| H1b | 26.4% | [15.0%, 34.4%] | 10.0% | supported |
| H2 | dataset η² largest in 100.0% of replicates | — | 95% | supported |
| H3 | 85.4% of universes need n > 500 (median n = 1256) | — | > 50% | supported |

H2 point estimates (η²): dataset 0.614, retriever 0.044, budget 0.096, metric 0.032

## H1 sensitivity analyses (P1: share supporting fixed-512, count − budget)

| Analysis | Estimate | 95% CI |
|---|---:|---|
| a_bh_fdr | 64.1% | — |
| b_without_squad2 | 58.6% | [49.1%, 75.5%] |
| c_default_retriever | 68.8% | [60.4%, 85.4%] |
| e_all_budgets | 72.0% | [64.9%, 84.0%] |

## Verdict shares per claim and protocol

| Claim | Role | A vs B | Protocol | Universes | Supports A | Supports B | Inconclusive |
|---|---|---|---|---:|---:|---:|---:|
| P1 | primary | fixed-128 vs fixed-512 | count | 768 | 0.0% | 76.6% | 23.4% |
| P1 | primary | fixed-128 vs fixed-512 | budget | 576 | 81.2% | 7.6% | 11.1% |
| S1-64 | secondary | fixed-64 vs fixed-128 | count | 768 | 0.0% | 83.3% | 16.7% |
| S1-64 | secondary | fixed-64 vs fixed-128 | budget | 960 | 18.4% | 39.8% | 41.8% |
| S1-128 | secondary | fixed-128 vs fixed-256 | count | 768 | 0.0% | 72.9% | 27.1% |
| S1-128 | secondary | fixed-128 vs fixed-256 | budget | 768 | 58.3% | 6.0% | 35.7% |
| S1-256 | secondary | fixed-256 vs fixed-512 | count | 768 | 0.0% | 61.3% | 38.7% |
| S1-256 | secondary | fixed-256 vs fixed-512 | budget | 576 | 75.5% | 2.1% | 22.4% |
| S2-64 | secondary | fixed-64-o25 vs fixed-64 | count | 768 | 52.2% | 1.8% | 46.0% |
| S2-64 | secondary | fixed-64-o25 vs fixed-64 | budget | 960 | 55.4% | 1.6% | 43.0% |
| S2-128 | secondary | fixed-128-o25 vs fixed-128 | count | 768 | 52.3% | 1.8% | 45.8% |
| S2-128 | secondary | fixed-128-o25 vs fixed-128 | budget | 960 | 54.8% | 1.9% | 43.3% |
| S2-256 | secondary | fixed-256-o25 vs fixed-256 | count | 768 | 35.8% | 4.0% | 60.2% |
| S2-256 | secondary | fixed-256-o25 vs fixed-256 | budget | 768 | 38.0% | 2.7% | 59.2% |
| S2-512 | secondary | fixed-512-o25 vs fixed-512 | count | 768 | 9.4% | 7.3% | 83.3% |
| S2-512 | secondary | fixed-512-o25 vs fixed-512 | budget | 576 | 11.1% | 6.8% | 82.1% |
| S3-64 | secondary | paragraph-64 vs fixed-64 | count | 768 | 62.2% | 5.2% | 32.6% |
| S3-64 | secondary | paragraph-64 vs fixed-64 | budget | 960 | 75.6% | 0.0% | 24.4% |
| S3-128 | secondary | paragraph-128 vs fixed-128 | count | 768 | 59.1% | 0.5% | 40.4% |
| S3-128 | secondary | paragraph-128 vs fixed-128 | budget | 960 | 79.8% | 0.0% | 20.2% |
| S3-256 | secondary | paragraph-256 vs fixed-256 | count | 768 | 50.5% | 2.5% | 47.0% |
| S3-256 | secondary | paragraph-256 vs fixed-256 | budget | 768 | 77.0% | 0.4% | 22.7% |
| S3-512 | secondary | paragraph-512 vs fixed-512 | count | 768 | 14.1% | 1.6% | 84.4% |
| S3-512 | secondary | paragraph-512 vs fixed-512 | budget | 576 | 61.3% | 1.7% | 37.0% |
| S4-64 | exploratory | sentence-64 vs fixed-64 | count | 768 | 59.1% | 6.4% | 34.5% |
| S4-64 | exploratory | sentence-64 vs fixed-64 | budget | 960 | 68.9% | 0.4% | 30.7% |
| S4-128 | exploratory | sentence-128 vs fixed-128 | count | 768 | 47.3% | 1.0% | 51.7% |
| S4-128 | exploratory | sentence-128 vs fixed-128 | budget | 960 | 58.1% | 0.1% | 41.8% |
| S4-256 | exploratory | sentence-256 vs fixed-256 | count | 768 | 19.1% | 1.6% | 79.3% |
| S4-256 | exploratory | sentence-256 vs fixed-256 | budget | 768 | 37.4% | 0.0% | 62.6% |
| S4-512 | exploratory | sentence-512 vs fixed-512 | count | 768 | 5.9% | 0.3% | 93.9% |
| S4-512 | exploratory | sentence-512 vs fixed-512 | budget | 576 | 19.8% | 0.3% | 79.9% |

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
