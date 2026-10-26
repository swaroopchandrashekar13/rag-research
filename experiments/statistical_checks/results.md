| Status | Check | Detail |
|---|---|---|
| PASS | Study 1 verdict shares (21 claims x 2 protocols x 4 datasets + pooled) | 480 quantities compared, 0 mismatches |
| PASS | Study 1 H1: estimate, joint-bootstrap CI and verdict rule | independent 71.1 pp [64.8, 81.9] -> supported; stored 71.1 [64.8, 81.9] supported |
| PASS | Study 1 H1b: estimate, joint-bootstrap CI and verdict rule | independent 26.7 pp [15.4, 33.9] -> supported; stored 26.7 [15.4, 33.9] supported |
| PASS | Study 1 H2 eta^2 (statsmodels OLS type II on universe means) | dataset 0.6143 (stored 0.6143), retriever 0.0444 (stored 0.0444), budget 0.0956 (stored 0.0956), metric 0.0319 (stored 0.0319); dataset largest in 100.0% of stored replicates |
| PASS | Study 1 H3 required n (formula, ddof=1) and verdict rule | 85.4% > 500, median 1256 (6528 universes) |
| PASS | Study 1 sensitivity (a) BH as implemented (family = claim x protocol x dataset) | independent 68.0 pp, stored 68.0 pp |
| PASS | Study 1b shorter-arm orientation from manifest chunk statistics | 0 mismatches |
| PASS | Study 1b semantic-arm shares (6 claims x 2 protocols) | 24 compared, 0 mismatches |
| PASS | Study 1b H4 point estimate and verdict rule | independent 55.4 pp (9.4% -> 64.8%); stored 55.4 supported |
| PASS | Study 1b H4b point estimate and verdict rule | independent 64.4 pp (6.9% -> 71.3%); stored 64.4 supported |
| PASS | Study 1b H5 point estimate and verdict rule | independent 19.4 pp; stored 19.4 [16.7, 41.7] inconclusive |
| PASS | Study 1b H5b point estimate and verdict rule | independent 58.3 pp; stored 58.3 [45.1, 64.6] supported |
| PASS | Study 1 H1 sensitivity analyses (b)-(e): estimates and joint-bootstrap CIs | b_without_squad2 61.5 [53.2, 74.8]; c_default_retriever 70.8 [64.6, 85.4]; d_cluster_bootstrap 69.7 [63.8, 82.0]; e_all_budgets 74.2 [68.3, 84.8] |
| PASS | Study 1 H2: bootstrap fraction (seed 13) and verdict rule | independent 100.0% -> supported; stored 100.0% supported |
| PASS | Study 1b H4: estimate, shares, joint-bootstrap CI and verdict | independent 55.4 pp [50.8, 63.1] -> supported |
| PASS | Study 1b H4b: estimate, shares, joint-bootstrap CI and verdict | independent 64.4 pp [56.5, 68.3] -> supported |
| PASS | Study 1b H5b: estimate, shares, joint-bootstrap CI and verdict | independent 58.3 pp [45.1, 64.6] -> supported |
| PASS | Study 1b H5: estimate, joint-bootstrap CI and verdict (and equal to the recorded values) | independent 0.19444444444444445 [0.16666666666666669, 0.41684027777777766] -> inconclusive |
| PASS | Study 1b CUAD dense P1 subset (10 fields): stored and independent values equal the recorded ones | 0 mismatches |
| PASS | Study 1b H4 sensitivity analyses (a), (b), (d), (e), (f): estimates and CIs | a_bh_fdr 54.3; b_without_squad2 48.0 [42.7, 58.3]; d_cluster_bootstrap 58.7 [50.0, 63.3]; e_all_budgets 53.7 [49.7, 60.9]; f_bm25_only 61.1 [57.2, 72.5]; f_dense_only 49.8 [39.1, 58.1] |
| PASS | Tier 2 pooled DiD, stratified bootstrap CI and reading rule (2 claims x 3 measures) | 0 mismatches; complete cases per dataset: squad2 50, covidqa 50, cuad 50, qasper 50 |
| PASS | Tier 2 per-dataset contrasts, cell means and complete-case counts | 236 quantities compared, 0 mismatches |
| PASS | Consistent procedure (query unit): H1 estimate, interval and verdict | independent 70.9 [64.8, 81.9] supported; stored 70.9 [64.8, 81.9] supported |
| PASS | Consistent procedure (query unit): H1b estimate, interval and verdict | independent 27.1 [15.4, 33.9] supported; stored 27.1 [15.4, 33.9] supported |
| PASS | Consistent procedure (query unit): H5 estimate, interval and verdict | independent 21.5 [16.7, 41.7] supported; stored 21.5 [16.7, 41.7] supported |
| PASS | Consistent procedure (query unit): H4 estimate, interval and verdict | independent 55.6 [50.8, 63.1] supported; stored 55.6 [50.8, 63.1] supported |
| PASS | Consistent procedure (query unit): H4b estimate, interval and verdict | independent 65.3 [56.5, 68.3] supported; stored 65.3 [56.5, 68.3] supported |
| PASS | Consistent procedure (query unit): H5b estimate, interval and verdict | independent 58.3 [45.1, 64.6] supported; stored 58.3 [45.1, 64.6] supported |
| PASS | Consistent procedure (document unit): H1 estimate, interval and verdict | independent 68.9 [61.6, 80.9] supported; stored 68.9 [61.6, 80.9] supported |
| PASS | Consistent procedure (document unit): H1b estimate, interval and verdict | independent 26.4 [15.0, 34.4] supported; stored 26.4 [15.0, 34.4] supported |
| PASS | Consistent procedure (document unit): H5 estimate, interval and verdict | independent 19.4 [16.7, 39.6] inconclusive; stored 19.4 [16.7, 39.6] inconclusive |
| PASS | Consistent procedure (document unit): H4 estimate, interval and verdict | independent 59.0 [51.3, 65.0] supported; stored 59.0 [51.3, 65.0] supported |
| PASS | Consistent procedure (document unit): H4b estimate, interval and verdict | independent 65.2 [55.4, 67.1] supported; stored 65.2 [55.4, 67.1] supported |
| PASS | Consistent procedure (document unit): H5b estimate, interval and verdict | independent 58.3 [47.9, 75.0] supported; stored 58.3 [47.9, 75.0] supported |
| PASS | Consistent procedure: sensitivity (a) Benjamini-Hochberg (family claim x protocol x dataset) | independent 67.6 pp, stored 67.6 pp |
