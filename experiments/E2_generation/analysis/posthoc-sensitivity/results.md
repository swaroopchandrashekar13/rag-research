# Tier 2 answer check: post-hoc sensitivity

Truncated responses (256-token cap) per dataset: squad2 0 (queries excluded: 0), covidqa 0 (queries excluded: 0), cuad 65 (queries excluded: 26), qasper 2 (queries excluded: 2)

| Claim / measure | Planned DiD [95% CI] | Without truncated queries | Document resampling |
|---|---|---|---|
| P1/f1 | -0.017 [-0.065, +0.033] inconclusive | -0.015 [-0.061, +0.031] inconclusive | -0.017 [-0.062, +0.024] inconclusive |
| P1/em | -0.055 [-0.100, -0.010] opposite | -0.055 [-0.105, -0.010] opposite | -0.055 [-0.095, -0.020] opposite |
| P1/coverage | +0.089 [+0.050, +0.132] carries over | +0.090 [+0.048, +0.136] carries over | +0.089 [+0.049, +0.135] carries over |
| S3-256/f1 | +0.004 [-0.024, +0.036] inconclusive | +0.002 [-0.026, +0.031] inconclusive | +0.004 [-0.028, +0.039] inconclusive |
| S3-256/em | -0.015 [-0.050, +0.020] inconclusive | -0.015 [-0.045, +0.020] inconclusive | -0.015 [-0.047, +0.025] inconclusive |
| S3-256/coverage | +0.035 [+0.015, +0.060] carries over | +0.030 [+0.010, +0.055] carries over | +0.035 [+0.013, +0.064] carries over |

Per-dataset mean DiD:

| Claim / measure | squad2 | covidqa | cuad | qasper |
|---|---:|---:|---:|---:|
| P1/f1 | -0.122 | -0.006 | -0.001 | +0.060 |
| P1/em | -0.160 | -0.060 | +0.000 | +0.000 |
| P1/coverage | +0.120 | +0.110 | +0.020 | +0.106 |
| S3-256/f1 | -0.027 | +0.005 | -0.008 | +0.045 |
| S3-256/em | -0.060 | -0.020 | +0.000 | +0.020 |
| S3-256/coverage | +0.060 | +0.060 | +0.000 | +0.020 |
