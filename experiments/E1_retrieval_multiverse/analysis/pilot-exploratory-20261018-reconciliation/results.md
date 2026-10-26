# Pilot sensitivity intervals: stored versus current settings

Earlier settings: 200 joint-bootstrap replicates for sensitivity intervals; sensitivity (d) interval from query resampling. Current settings: 1,000 joint-bootstrap replicates; sensitivity (d) interval from document resampling.

| Analysis | Estimate | Stored 95% CI | Earlier settings reproduce it | Current 95% CI | Max |Δ| (pp) |
|---|---:|---|---|---|---:|
| b_without_squad2 | 62.4 | [50.97, 76.28] | yes | [51.79, 76.27] | 0.82 |
| c_default_retriever | 66.7 | [54.13, 79.17] | yes | [54.17, 79.20] | 0.03 |
| d_cluster_bootstrap | 71.1 | [62.26, 81.04] | yes | [60.41, 81.51] | 1.85 |
| e_all_budgets | 72.7 | [63.38, 81.21] | yes | [63.20, 81.67] | 0.46 |
