"""Paired-bootstrap inference, verdicts, joint-bootstrap uncertainty, power and eta-squared.

Two verdict procedures are implemented:

- planned: the analysis plans' rule. The point estimate of a share uses percentile-bootstrap verdicts, while the
  joint-bootstrap replicates use normal-approximation verdicts with the query-level SD, also when documents are
  resampled. The point estimate and its interval therefore describe slightly different statistics.
- consistent: one rule for the point estimate and for every replicate. A universe's verdict is the sign of a 95%
  Wald interval for its mean paired difference, whose standard error is computed at the resampling unit: queries
  (z critical value) or documents (cluster-robust CR1 standard error, t critical value with G - 1 degrees of
  freedom, G = number of documents). Evaluated on the original sample, the replicate statistic equals the point
  estimate.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy import stats as _st

Z_975 = 1.959963984540054
Z_80 = 0.8416212335729143


def bootstrap_weights(n: int, reps: int, seed: int, clusters: np.ndarray | None = None) -> np.ndarray:
    """[reps, n] resampling weights. Query-level: multinomial counts summing to n.
    Cluster-level: clusters (e.g. documents) are drawn with replacement and every query inherits the count of
    its cluster, so rows sum to the number of queries in the resampled clusters."""
    rng = np.random.default_rng(seed)
    if clusters is None:
        return rng.multinomial(n, np.full(n, 1.0 / n), size=reps).astype(np.float32)
    ids, inv = np.unique(clusters, return_inverse=True)
    counts = rng.multinomial(len(ids), np.full(len(ids), 1.0 / len(ids)), size=reps).astype(np.float32)
    return counts[:, inv]


def paired_bootstrap_ci(diff: np.ndarray, reps: int = 2000, seed: int = 7, alpha: float = 0.05,
                        clusters: np.ndarray | None = None):
    """diff: [n_queries, n_universes]. Returns (mean, lo, hi, p_two_sided), each [n_universes]."""
    diff = np.asarray(diff, dtype=np.float32)
    w = bootstrap_weights(diff.shape[0], reps, seed, clusters)
    boot = (w @ diff) / w.sum(axis=1, keepdims=True)  # [reps, U]
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2], axis=0)
    p = np.minimum(1.0, 2 * np.minimum((boot <= 0).mean(axis=0), (boot >= 0).mean(axis=0)))
    return diff.mean(axis=0), lo, hi, p


def verdicts(lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """+1 supports A (CI > 0), -1 supports B (CI < 0), 0 inconclusive."""
    return np.where(lo > 0, 1, np.where(hi < 0, -1, 0)).astype(np.int8)


def normal_verdicts(mean: np.ndarray, sd: np.ndarray, n: int) -> np.ndarray:
    half = Z_975 * sd / np.sqrt(n)
    return verdicts(mean - half, mean + half)


def bh_reject(p: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg step-up procedure; returns a boolean rejection mask."""
    p = np.asarray(p, dtype=np.float64)
    order = np.argsort(p)
    thresh = q * np.arange(1, len(p) + 1) / len(p)
    passed = p[order] <= thresh
    k = passed.nonzero()[0].max() + 1 if passed.any() else 0
    out = np.zeros(len(p), dtype=bool)
    out[order[:k]] = True
    return out


def _draw(rng: np.random.Generator, n: int, inv: np.ndarray | None) -> tuple[np.ndarray, np.ndarray | None]:
    """One resample: (query weights [n], cluster draw counts [G] or None). Same random stream as the plan's code."""
    if inv is None:
        return rng.multinomial(n, np.full(n, 1.0 / n)).astype(np.float64), None
    k = int(inv.max()) + 1
    counts = rng.multinomial(k, np.full(k, 1.0 / k)).astype(np.float64)
    return counts[inv], counts


def joint_bootstrap(diffs: dict[str, np.ndarray], fn: Callable[[dict], float], reps: int = 1000, seed: int = 11,
                    clusters: dict[str, np.ndarray] | None = None) -> np.ndarray:
    """Replicates of a statistic over universes (analysis plan §3).

    Queries (or, with `clusters`, whole documents) are resampled within each dataset; one resample per dataset is
    shared by all of its universes. `fn` receives {dataset: (mean[U], sd[U], n)} computed on the resample, where n
    is the number of queries in the resample and sd the query-level SD, and returns a float.
    """
    rng = np.random.default_rng(seed)
    inv = {k: np.unique(v, return_inverse=True)[1] for k, v in clusters.items()} if clusters else {}
    out = np.empty(reps)
    for r in range(reps):
        stats = {}
        for name, d in diffs.items():
            w, _ = _draw(rng, d.shape[0], inv.get(name))
            n_eff = float(w.sum())
            m = w @ d / n_eff
            var = np.maximum(w @ (d * d) / n_eff - m * m, 0.0) * n_eff / max(n_eff - 1, 1)
            stats[name] = (m, np.sqrt(var), n_eff)
        out[r] = fn(stats)
    return out


def joint_bootstrap_shares(diffs: dict[str, np.ndarray], select, reps: int = 1000, seed: int = 11,
                           clusters: dict[str, np.ndarray] | None = None) -> np.ndarray:
    """The planned replicates: `select` receives {dataset: verdicts[U]} from normal-approximation CIs with the
    query-level SD (also when documents are resampled)."""
    return joint_bootstrap(diffs, lambda st: select({k: normal_verdicts(*v) for k, v in st.items()}), reps, seed, clusters)


# ------------------------------------------------------------------------------------------ consistent procedure
class WaldUnits:
    """Sufficient statistics of one dataset's per-query differences [n, U] for Wald verdicts at the resampling unit.

    With `clusters` the unit is the cluster (document): per-cluster sums S [G, U], squared sums and sizes are kept,
    and the standard error of the mean is the cluster-robust CR1 estimator
        var(m) = G / (G - 1) * sum_c (S_c - m n_c)^2 / N^2,
    with the t(G - 1) critical value. Without clusters the unit is the query: var(m) = s^2 / N with the z value.
    Both accept resampling counts (per query, or per cluster), so a bootstrap replicate is evaluated exactly like the
    original sample (all counts 1)."""

    def __init__(self, diff: np.ndarray, clusters: np.ndarray | None = None, alpha: float = 0.05):
        d = np.asarray(diff, dtype=np.float64)
        self.alpha = alpha
        if clusters is None:
            self.inv = None
            self.d, self.d2 = d, d * d
            self.units = d.shape[0]
            self.crit = float(_st.norm.ppf(1 - alpha / 2))
            return
        ids, inv = np.unique(np.asarray(clusters), return_inverse=True)
        g = len(ids)
        if g < 2:
            raise ValueError("cluster-robust standard errors need at least two clusters")
        self.inv, self.units = inv, g
        self.sums = np.zeros((g, d.shape[1]))
        np.add.at(self.sums, inv, d)
        self.sq = self.sums * self.sums
        self.size = np.bincount(inv, minlength=g).astype(np.float64)
        self.crit = float(_st.t.ppf(1 - alpha / 2, g - 1))

    def moments(self, counts: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
        """(mean[U], standard error[U]) for resampling counts (None = the original sample)."""
        if self.inv is None:
            w = np.ones(self.d.shape[0]) if counts is None else counts
            n = float(w.sum())
            m = w @ self.d / n
            var = np.maximum(w @ self.d2 / n - m * m, 0.0) * n / max(n - 1, 1)
            return m, np.sqrt(var / n)
        k = np.ones(self.units) if counts is None else counts
        n = float(k @ self.size)
        m = k @ self.sums / n
        q = k @ self.sq - 2 * m * ((k * self.size) @ self.sums) + m * m * float(k @ (self.size * self.size))
        g = float(k.sum())
        return m, np.sqrt(np.maximum(q, 0.0) * g / (g - 1)) / n

    def verdicts(self, counts: np.ndarray | None = None) -> np.ndarray:
        m, se = self.moments(counts)
        half = self.crit * se
        return verdicts(m - half, m + half)

    def test(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """(mean, lo, hi, two-sided p) on the original sample, p from the same reference distribution."""
        m, se = self.moments()
        half = self.crit * se
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.abs(m) / se
        dist = _st.norm if self.inv is None else _st.t(self.units - 1)
        p = np.where(se > 0, 2 * dist.sf(t), np.where(m == 0, 1.0, 0.0))
        return m, m - half, m + half, p


def wald_test(diff: np.ndarray, clusters: np.ndarray | None = None, alpha: float = 0.05):
    """(mean, lo, hi, p) per universe from the consistent rule; see `WaldUnits`."""
    return WaldUnits(diff, clusters, alpha).test()


def joint_bootstrap_wald_shares(diffs: dict[str, np.ndarray], select, reps: int = 1000, seed: int = 11,
                                clusters: dict[str, np.ndarray] | None = None) -> np.ndarray:
    """Consistent replicates: the resampling draws of `joint_bootstrap` (same seed, same stream), and verdicts from
    `WaldUnits` at the same unit that is resampled. `select` receives {dataset: verdicts[U]}."""
    rng = np.random.default_rng(seed)
    units = {k: WaldUnits(d, None if not clusters else clusters[k]) for k, d in diffs.items()}
    out = np.empty(reps)
    for r in range(reps):
        v = {}
        for name, d in diffs.items():
            u = units[name]
            w, counts = _draw(rng, d.shape[0], u.inv)
            v[name] = u.verdicts(w if counts is None else counts)
        out[r] = select(v)
    return out


def required_n(sd: np.ndarray, delta: float = 0.02) -> np.ndarray:
    """Paired n to detect |delta| at alpha=0.05 (two-sided), power 0.8, normal approximation."""
    return np.ceil(((Z_975 + Z_80) * np.asarray(sd, dtype=np.float64) / delta) ** 2)


def eta_squared(y: np.ndarray, factors: dict[str, np.ndarray]) -> dict[str, float]:
    """Main-effect eta^2 = SS_factor / SS_total (equals type-II for a balanced full factorial)."""
    y = np.asarray(y, dtype=np.float64)
    grand = y.mean()
    ss_total = float(((y - grand) ** 2).sum())
    out = {}
    for name, levels in factors.items():
        ss = 0.0
        for lv in np.unique(levels):
            sel = levels == lv
            ss += sel.sum() * (y[sel].mean() - grand) ** 2
        out[name] = ss / ss_total if ss_total > 0 else 0.0
    return out
