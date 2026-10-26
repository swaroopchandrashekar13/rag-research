"""Reconcile the stored Study 1 pilot analysis with the current analysis code.

The stored pilot analysis (analysis/pilot-exploratory-20261018) was produced before two changes recorded in the
Study 1 plan's deviation log: sensitivity-analysis intervals were computed from 200 joint-bootstrap replicates instead
of 1,000, and the document-cluster sensitivity (d) resampled queries instead of documents in its interval. This
script recomputes every H1 sensitivity interval of the pilot (planned procedure) three ways: with the earlier
settings, which must reproduce the stored bounds exactly; and with the current settings, which give the bounds of a
fresh analysis. Estimates and verdicts do not depend on these settings. The stored analysis is only read.

Usage: python -I tools/pilot_reconcile.py --out-json FILE [--out-md FILE]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragmv import analyze as A  # noqa: E402
from ragmv import stats as S  # noqa: E402

RUN = ROOT / "experiments/E1_retrieval_multiverse/runs/pilot-exploratory-20261018"
STORED = ROOT / "experiments/E1_retrieval_multiverse/analysis/pilot-exploratory-20261018/results.json"


def interval(run, kw: dict, joint_reps: int, clusters) -> list[float]:
    p1 = A.planned_claims()[0]
    dc = A.claim_diffs(run, p1, "count", True, kw.get("retrievers"), kw.get("datasets"))
    db = A.claim_diffs(run, p1, "budget", kw.get("admissible", True), kw.get("retrievers"), kw.get("datasets"))
    combined = {d: np.hstack([dc[d][0], db[d][0]]) for d in dc}
    split = {d: dc[d][0].shape[1] for d in dc}

    def stat(v):
        return float((np.concatenate([v[d][: split[d]] for d in v]) == -1).mean()
                     - (np.concatenate([v[d][split[d]:] for d in v]) == -1).mean())
    boot = S.joint_bootstrap_shares(combined, stat, reps=joint_reps, seed=A.SEEDS["joint_bootstrap"], clusters=clusters)
    return [float(x) for x in np.quantile(boot, [0.025, 0.975])]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", type=Path)
    args = ap.parse_args(argv)
    run = A.Run(RUN)
    run.validate("EXPLORATORY")
    stored = json.loads(STORED.read_text())["H1_sensitivity"]
    clusters = {d: run.meta[d]["doc_idx"] for d in run.datasets}
    cases = {"b_without_squad2": {"datasets": [d for d in run.datasets if d != "squad2"]},
             "c_default_retriever": {"retrievers": [A.DEFAULT_RETRIEVER]},
             "d_cluster_bootstrap": {"cluster": True}, "e_all_budgets": {"admissible": False}}
    out = {"label": "Reconciliation of the stored pilot analysis (planned procedure)", "sensitivity": {}}
    for name, kw in cases.items():
        earlier = interval(run, kw, 200, None)
        current = interval(run, kw, 1000, clusters if kw.get("cluster") else None)
        out["sensitivity"][name] = {
            "estimate": stored[name]["estimate"], "stored_ci95": stored[name]["ci95"],
            "earlier_settings_ci95": earlier, "reproduces_stored": bool(np.allclose(earlier, stored[name]["ci95"],
                                                                                    rtol=0, atol=1e-12)),
            "current_ci95": current,
            "max_abs_difference_current_vs_stored": float(np.max(np.abs(np.subtract(current, stored[name]["ci95"]))))}
    out["earlier_settings"] = ("200 joint-bootstrap replicates for sensitivity intervals; sensitivity (d) interval "
                               "from query resampling")
    out["current_settings"] = "1,000 joint-bootstrap replicates; sensitivity (d) interval from document resampling"
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2) + "\n")
    lines = ["# Pilot sensitivity intervals: stored versus current settings", "",
             f"Earlier settings: {out['earlier_settings']}. Current settings: {out['current_settings']}.", "",
             "| Analysis | Estimate | Stored 95% CI | Earlier settings reproduce it | Current 95% CI | Max |Δ| (pp) |",
             "|---|---:|---|---|---|---:|"]
    for name, v in out["sensitivity"].items():
        def ci(x):
            return f"[{100 * x[0]:.2f}, {100 * x[1]:.2f}]"
        lines.append(f"| {name} | {100 * v['estimate']:.1f} | {ci(v['stored_ci95'])} | "
                     f"{'yes' if v['reproduces_stored'] else 'NO'} | {ci(v['current_ci95'])} | "
                     f"{100 * v['max_abs_difference_current_vs_stored']:.2f} |")
    if args.out_md:
        args.out_md.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if all(v["reproduces_stored"] for v in out["sensitivity"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
