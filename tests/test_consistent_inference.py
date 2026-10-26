"""The consistent verdict procedure (ragmv.stats.WaldUnits and joint_bootstrap_wald_shares)."""
import numpy as np
import pytest

from ragmv import stats as S


def clustered(rng, g=30, size=12, u=5, icc=0.4, shift=0.0):
    """Per-query differences [g*size, u] with a shared document effect, and the document index of each query."""
    doc = np.repeat(np.arange(g), size)
    effect = rng.normal(0, np.sqrt(icc), (g, u))[doc]
    return shift + effect + rng.normal(0, np.sqrt(1 - icc), (g * size, u)), doc


def test_query_unit_matches_normal_approximation():
    rng = np.random.default_rng(1)
    x = rng.normal(0.05, 1, (400, 7))
    m, lo, hi, p = S.wald_test(x)
    sd = x.std(axis=0, ddof=1)
    assert np.allclose(m, x.mean(axis=0))
    assert np.allclose(hi - m, S.Z_975 * sd / np.sqrt(len(x)))
    assert (S.verdicts(lo, hi) == S.normal_verdicts(x.mean(axis=0), sd, len(x))).all()
    from scipy import stats
    assert np.allclose(p, 2 * stats.norm.sf(np.abs(m) / (sd / np.sqrt(len(x)))))


def test_cluster_se_matches_statsmodels():
    sm = pytest.importorskip("statsmodels.api")
    rng = np.random.default_rng(2)
    x, doc = clustered(rng, g=25, size=9, u=3)
    keep = rng.random(len(doc)) > 0.3  # unequal cluster sizes
    x, doc = x[keep], doc[keep]
    m, lo, hi, p = S.wald_test(x, doc)
    for j in range(x.shape[1]):
        fit = sm.OLS(x[:, j], np.ones(len(x))).fit(cov_type="cluster", cov_kwds={"groups": doc}, use_t=True)
        ci = fit.conf_int()[0]
        assert np.isclose(lo[j], ci[0]) and np.isclose(hi[j], ci[1])
        assert np.isclose(p[j], fit.pvalues[0])


def test_resample_counts_equal_expanded_data():
    """A bootstrap replicate given as cluster counts is evaluated exactly like the explicitly resampled data, in which
    every drawn copy of a document is a separate cluster."""
    rng = np.random.default_rng(3)
    x, doc = clustered(rng, g=15, size=6, u=4)
    units = S.WaldUnits(x, doc)
    counts = rng.multinomial(15, np.full(15, 1 / 15)).astype(float)
    rows, ids = [], []
    for c, k in enumerate(counts):
        for copy in range(int(k)):
            rows.append(x[doc == c])
            ids += [c * 100 + copy] * int((doc == c).sum())
    m1, se1 = units.moments(counts)
    m2, se2 = S.WaldUnits(np.vstack(rows), np.array(ids)).moments()
    assert np.allclose(m1, m2) and np.allclose(se1, se2)
    w = rng.multinomial(len(x), np.full(len(x), 1 / len(x))).astype(float)
    m3, se3 = S.WaldUnits(x).moments(w)
    m4, se4 = S.WaldUnits(np.repeat(x, w.astype(int), axis=0)).moments()
    assert np.allclose(m3, m4) and np.allclose(se3, se4)


def test_point_estimate_is_the_identity_replicate():
    rng = np.random.default_rng(4)
    x, doc = clustered(rng, shift=0.15)
    for cl in (None, doc):
        u = S.WaldUnits(x, cl)
        m, lo, hi, _ = u.test()
        assert (u.verdicts() == S.verdicts(lo, hi)).all()
        assert (u.verdicts(np.ones(u.units)) == u.verdicts()).all()


def test_query_level_replicates_equal_the_planned_replicates():
    """Same draws and, at the query level, the same verdict rule: only the point estimate differs between procedures."""
    rng = np.random.default_rng(5)
    diffs = {"a": rng.normal(0.03, 1, (300, 6)), "b": rng.normal(-0.02, 1, (200, 6))}

    def share(v):
        return float(np.concatenate(list(v.values())).mean())

    planned = S.joint_bootstrap_shares(diffs, share, reps=60, seed=11)
    consistent = S.joint_bootstrap_wald_shares(diffs, share, reps=60, seed=11)
    assert np.array_equal(planned, consistent)


def test_cluster_replicates_use_cluster_variance():
    """With documents resampled, the planned replicates keep the query-level SD; the consistent ones do not."""
    rng = np.random.default_rng(6)
    x, doc = clustered(rng, g=20, size=15, u=8, icc=0.6, shift=0.12)
    diffs, cl = {"a": x}, {"a": doc}

    def share(v):
        return float((v["a"] != 0).mean())

    planned = S.joint_bootstrap_shares(diffs, share, reps=200, seed=11, clusters=cl)
    consistent = S.joint_bootstrap_wald_shares(diffs, share, reps=200, seed=11, clusters=cl)
    assert consistent.mean() < planned.mean()  # wider cluster-robust intervals: fewer decisive verdicts


def test_cluster_robust_interval_coverage():
    """Monte-Carlo check of the per-universe interval under document dependence: the CR1/t interval keeps close to
    nominal coverage, the query-level interval does not."""
    rng = np.random.default_rng(7)
    hits_cr, hits_iid = 0, 0
    sims = 400
    for _ in range(sims):
        x, doc = clustered(rng, g=30, size=10, u=1, icc=0.3)
        _, lo, hi, _ = S.wald_test(x, doc)
        hits_cr += int(lo[0] <= 0 <= hi[0])
        _, lo, hi, _ = S.wald_test(x)
        hits_iid += int(lo[0] <= 0 <= hi[0])
    assert 0.91 <= hits_cr / sims <= 0.99
    assert hits_iid / sims < 0.85


def test_degenerate_universes():
    x = np.zeros((50, 3))
    x[:, 1] = 0.2  # constant non-zero difference
    m, lo, hi, p = S.wald_test(x)
    assert list(S.verdicts(lo, hi)) == [0, 1, 0]
    assert p[0] == 1.0 and p[1] == 0.0
    with pytest.raises(ValueError):
        S.WaldUnits(x, np.zeros(50))
