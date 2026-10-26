"""POST-HOC sensitivity analyses of the Tier 2 answer check (not part of its analysis plan).

1. Truncation: responses that stopped at the 256-token output cap (finish_reason "length") are scored on their
   truncated text. The pooled difference-in-differences (DiD) is recomputed without every query that has a truncated
   response in any of its eight cells.
2. Document dependence: sampled queries can share a document. The pooled DiD interval is recomputed with documents,
   not queries, resampled within each dataset (equal weight per dataset, as planned).
3. Per-dataset DiD of each measure, so the source of a pooled result is visible.

Usage: python -I tools/generation_sensitivity.py --out-json FILE [--out-md FILE] [--run RUN] [--reps 2000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragmv import analyze_generation as G  # noqa: E402

RUN = ROOT / "experiments/E2_generation/runs/qwen3-4b-kaggle-gpu"
QUERIES = ROOT / "experiments/E1_retrieval_multiverse/runs/confirmatory-20261018"
FIELDS = ("f1", "em", "coverage")


def stratified(per_ds: dict[str, np.ndarray], docs: dict[str, np.ndarray] | None, reps: int, seed: int = 7):
    """Equal-weight mean of per-dataset means and its percentile interval; queries or (with `docs`) documents are
    resampled within each dataset."""
    rng = np.random.default_rng(seed)
    names = sorted(per_ds)
    point = float(np.mean([per_ds[k].mean() for k in names]))
    boot = np.zeros(reps)
    for k in names:
        x = per_ds[k]
        if docs is None:
            w = rng.multinomial(len(x), np.full(len(x), 1.0 / len(x)), size=reps).astype(float)
        else:
            ids, inv = np.unique(docs[k], return_inverse=True)
            w = rng.multinomial(len(ids), np.full(len(ids), 1.0 / len(ids)), size=reps).astype(float)[:, inv]
        boot += (w @ x) / w.sum(axis=1)
    boot /= len(names)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    return {"did": point, "lo": float(lo), "hi": float(hi), "verdict": G.verdict(lo, hi),
            "n": int(sum(len(v) for v in per_ds.values()))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=RUN)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", type=Path)
    ap.add_argument("--reps", type=int, default=2000)
    args = ap.parse_args(argv)
    res = {"label": "POST-HOC sensitivity of the Tier 2 answer check (not part of its analysis plan)",
           "run": args.run.name, "truncated_responses": {}, "excluded_queries": {}, "pooled": {}, "by_dataset": {}}
    per = {variant: {c: {f: {} for f in FIELDS} for c in G.CLAIMS} for variant in ("all", "untruncated")}
    docs = {variant: {} for variant in per}
    for ds in G.DATASETS:
        rows = G.load_rows(args.run / ds)
        trunc = {r["qid"] for r in rows if r.get("finish_reason") == "length"}
        res["truncated_responses"][ds] = sum(r.get("finish_reason") == "length" for r in rows)
        res["excluded_queries"][ds] = len(trunc)
        q = json.loads((QUERIES / ds / "queries.json").read_text())
        doc_of = dict(zip(q["qids"], q["doc_idx"]))
        for variant, keep in (("all", rows), ("untruncated", [r for r in rows if r["qid"] not in trunc])):
            for field in FIELDS:
                qids, tab = G.table(keep, field)
                for claim in G.CLAIMS:
                    per[variant][claim][field][ds] = G.per_query_contrasts(tab, claim)["did"]
                docs[variant][ds] = np.array([doc_of[x] for x in qids])
    for variant in per:
        for claim in G.CLAIMS:
            for field in FIELDS:
                x = per[variant][claim][field]
                key = f"{claim}/{field}"
                res["pooled"].setdefault(variant, {})[key] = stratified(x, None, args.reps)
                if variant == "all":
                    res["pooled"].setdefault("document_resampling", {})[key] = stratified(x, docs["all"], args.reps)
                    res["by_dataset"][key] = {ds: float(v.mean()) for ds, v in x.items()}
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(res, indent=2) + "\n")
    lines = ["# Tier 2 answer check: post-hoc sensitivity", "",
             "Truncated responses (256-token cap) per dataset: " + ", ".join(
                 f"{d} {n} (queries excluded: {res['excluded_queries'][d]})" for d, n in res["truncated_responses"].items()),
             "", "| Claim / measure | Planned DiD [95% CI] | Without truncated queries | Document resampling |",
             "|---|---|---|---|"]

    def cell(r):
        return f"{r['did']:+.3f} [{r['lo']:+.3f}, {r['hi']:+.3f}] {r['verdict']}"
    for key in res["pooled"]["all"]:
        lines.append(f"| {key} | {cell(res['pooled']['all'][key])} | {cell(res['pooled']['untruncated'][key])} | "
                     f"{cell(res['pooled']['document_resampling'][key])} |")
    lines += ["", "Per-dataset mean DiD:", "", "| Claim / measure | " + " | ".join(G.DATASETS) + " |",
              "|---|" + "---:|" * len(G.DATASETS)]
    for key, v in res["by_dataset"].items():
        lines.append(f"| {key} | " + " | ".join(f"{v[d]:+.3f}" for d in G.DATASETS) + " |")
    if args.out_md:
        args.out_md.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
