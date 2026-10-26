# Gold-span containment (POST-HOC, not part of the analysis plans)

Share of confirmatory queries with at least one gold span inside a single chunk.

| Chunking | squad2 | covidqa | cuad | qasper |
|---|---:|---:|---:|---:|
| fixed-128 | 99.0 | 89.7 | 81.9 | 50.1 |
| sentence-128 | 100.0 | 97.9 | 96.1 | 56.2 |
| paragraph-128 | 100.0 | 98.6 | 95.7 | 81.9 |
| fixed-256 | 99.5 | 95.1 | 91.1 | 75.5 |
| sentence-256 | 100.0 | 98.6 | 99.3 | 80.8 |
| paragraph-256 | 100.0 | 99.7 | 99.0 | 98.6 |
| fixed-512 | 99.8 | 97.6 | 95.9 | 89.3 |
| sentence-512 | 100.0 | 99.7 | 99.7 | 91.2 |
| paragraph-512 | 100.0 | 99.9 | 99.8 | 100.0 |

Median length of each query's shortest gold span (words): squad2 2, covidqa 9, cuad 24, qasper 72.5.

Mean largest share of a gold span held by one chunk (%):

| Chunking | squad2 | covidqa | cuad | qasper |
|---|---:|---:|---:|---:|
| fixed-128 | 99.7 | 97.3 | 95.3 | 87.3 |
| sentence-128 | 100.0 | 99.2 | 99.0 | 86.0 |
| paragraph-128 | 100.0 | 99.5 | 98.9 | 94.4 |
| fixed-256 | 99.8 | 98.7 | 97.7 | 94.4 |
| sentence-256 | 100.0 | 99.5 | 99.8 | 94.7 |
| paragraph-256 | 100.0 | 99.9 | 99.8 | 99.7 |
| fixed-512 | 99.9 | 99.3 | 98.9 | 97.5 |
| sentence-512 | 100.0 | 99.9 | 99.9 | 97.5 |
| paragraph-512 | 100.0 | 100.0 | 99.9 | 100.0 |

Share of queries whose least-split gold span touches 3 or more chunks (%):

| Chunking | squad2 | covidqa | cuad | qasper |
|---|---:|---:|---:|---:|
| fixed-128 | 0.0 | 0.0 | 1.0 | 6.0 |
| sentence-128 | 0.0 | 0.0 | 0.2 | 5.2 |
| paragraph-128 | 0.0 | 0.1 | 0.4 | 2.0 |
| fixed-256 | 0.0 | 0.0 | 0.1 | 0.2 |
| sentence-256 | 0.0 | 0.0 | 0.0 | 0.1 |
| paragraph-256 | 0.0 | 0.0 | 0.0 | 0.0 |
| fixed-512 | 0.0 | 0.0 | 0.0 | 0.0 |
| sentence-512 | 0.0 | 0.0 | 0.0 | 0.0 |
| paragraph-512 | 0.0 | 0.0 | 0.0 | 0.0 |

S3-256 (paragraph-256 minus fixed-256), mean per-query difference over the run's universes, by whether fixed-256 keeps a gold span in one chunk (descriptive):

| Dataset | Protocol | Contained: n | mean Δ | Split: n | mean Δ |
|---|---|---:|---:|---:|---:|
| squad2 | count | 4721 | +0.0127 | 23 | +0.1819 |
| squad2 | budget | 4721 | +0.0333 | 23 | +0.2270 |
| covidqa | count | 1684 | +0.0181 | 87 | +0.2286 |
| covidqa | budget | 1684 | +0.0473 | 87 | +0.2561 |
| cuad | count | 907 | -0.0042 | 89 | +0.0109 |
| cuad | budget | 907 | +0.0006 | 89 | +0.0154 |
| qasper | count | 1316 | +0.0043 | 426 | +0.0636 |
| qasper | budget | 1316 | +0.0154 | 426 | +0.0749 |
