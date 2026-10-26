"""Compare a re-executed retrieval run with the stored run it repeats (Study 1 or Study 1b).

For every dataset the query lists and axes must be identical. For every chunking file present in both runs: the share
of bit-identical score cells, the largest absolute difference, the queries with any difference and, when both runs
store them, the word counts and chunk files. For the planned claim pairs: the number of universes whose verdict
(consistent rule, query unit) differs between the runs. Differences are expected where the stored run used a fixed
ranking depth and the new run fills budgets adaptively (`ragmv.budgetfill`), and where half-precision embeddings
differ across hardware; queries whose ranking the new run extended are counted separately. Nothing is modified.

Usage: python -I tools/compare_rerun.py --stored RUN_DIR --new RUN_DIR --out-json FILE [--out-md FILE]
Exit code 1 if the query lists differ or a stored chunking is missing from the new run.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragmv import stats as S  # noqa: E402


def load(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def chunk_file_equal(a: Path, b: Path) -> bool | None:
    if not (a.exists() and b.exists()):
        return None
    def read(p):
        return json.loads(gzip.decompress(p.read_bytes()))
    return read(a) == read(b)


def compare_dataset(stored: Path, new: Path) -> dict:
    out = {"queries_identical": None, "chunkings": {}, "missing_in_new": []}
    qs, qn = (json.loads((p / "queries.json").read_text()) for p in (stored, new))
    out["queries_identical"] = qs.get("qids") == qn.get("qids") and qs.get("doc_idx") == qn.get("doc_idx")
    ms, mn = (json.loads((p / "manifest.json").read_text()) for p in (stored, new))
    retr, ops = ms["config"]["retrievers"], ms["config"]["ops"]
    if mn["config"]["retrievers"] != retr or mn["config"]["ops"] != ops:
        out["axes_identical"] = False
        return out
    out["axes_identical"] = True
    for f in sorted(stored.glob("*.npz")):
        g = new / f.name
        if not g.exists():
            out["missing_in_new"].append(f.stem)
            continue
        a, b = load(f), load(g)
        sa, sb = a["scores"].astype(np.float64), b["scores"].astype(np.float64)
        if sa.shape != sb.shape:
            out["chunkings"][f.stem] = {"shape_mismatch": [list(sa.shape), list(sb.shape)]}
            continue
        diff = np.abs(sa - sb)
        rec = {"cells": int(diff.size), "identical_share": float((diff == 0).mean()), "max_abs_diff": float(diff.max()),
               "queries_with_any_difference": int((diff.max(axis=(0, 2, 3)) > 0).sum())}
        if "words" in a and "words" in b:
            rec["word_counts_identical_share"] = float((a["words"] == b["words"]).mean())
        if "expansions" in b:
            expanded = b["expansions"] > 0  # [R, n]: queries whose ranking the new run extended
            rec["queries_expanded_in_new_run"] = int(expanded.any(axis=0).sum())
            rec["max_abs_diff_outside_expanded"] = float(diff[~expanded].max()) if (~expanded).any() else 0.0
        out["chunkings"][f.stem] = rec
        cs = chunk_file_equal(stored / f"chunks_{f.stem}.json.gz", new / f"chunks_{f.stem}.json.gz")
        if cs is not None:
            rec["chunk_file_identical"] = cs
    return out


def compare_claims(stored: Path, new: Path, pairs: list[tuple[str, str]]) -> dict:
    """Per claim pair: share of universes whose verdict (consistent rule, query unit) differs between the runs."""
    out = {}
    for a, b in pairs:
        if not all((p / f"{c}.npz").exists() for p in (stored, new) for c in (a, b)):
            continue
        vs = []
        for p in (stored, new):
            d = load(p / f"{a}.npz")["scores"].astype(np.float64) - load(p / f"{b}.npz")["scores"].astype(np.float64)
            n = d.shape[1]
            m, lo, hi, _ = S.wald_test(np.moveaxis(d, 1, 0).reshape(n, -1))
            vs.append(S.verdicts(lo, hi))
        out[f"{a} vs {b}"] = {"universes": int(vs[0].size), "verdicts_differing": int((vs[0] != vs[1]).sum())}
    return out


PAIRS = [("fixed-128", "fixed-512"), ("paragraph-256", "fixed-256"), ("semantic-bp", "fixed-128"),
         ("semantic-bp", "fixed-256"), ("semantic-bp", "fixed-512"), ("semantic-cl", "fixed-128"),
         ("semantic-cl", "fixed-256"), ("semantic-cl", "fixed-512")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stored", required=True, type=Path)
    ap.add_argument("--new", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", type=Path)
    args = ap.parse_args(argv)
    res = {"stored": str(args.stored), "new": str(args.new), "datasets": {}}
    ok = True
    for ds in sorted(p.name for p in args.stored.iterdir() if (p / "manifest.json").exists()):
        if not (args.new / ds / "manifest.json").exists():
            res["datasets"][ds] = {"missing_in_new": True}
            ok = False
            continue
        r = compare_dataset(args.stored / ds, args.new / ds)
        if r.get("axes_identical"):
            r["claims"] = compare_claims(args.stored / ds, args.new / ds, PAIRS)
        ok &= bool(r["queries_identical"]) and bool(r.get("axes_identical")) and not r["missing_in_new"]
        res["datasets"][ds] = r
    res["comparable"] = ok
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(res, indent=2) + "\n")
    lines = [f"# Re-executed run versus stored run: {'comparable' if ok else 'NOT comparable'}", "",
             "| Dataset | Chunking | Identical cells | Max |Δ| | Queries differing | Expanded in new run |",
             "|---|---|---:|---:|---:|---:|"]
    for ds, r in res["datasets"].items():
        for ch, c in r.get("chunkings", {}).items():
            if "cells" in c:
                lines.append(f"| {ds} | {ch} | {100 * c['identical_share']:.2f}% | {c['max_abs_diff']:.4f} | "
                             f"{c['queries_with_any_difference']} | {c.get('queries_expanded_in_new_run', '—')} |")
    lines += ["", "| Dataset | Claim | Universes | Verdicts differing |", "|---|---|---:|---:|"]
    for ds, r in res["datasets"].items():
        for cl, c in r.get("claims", {}).items():
            lines.append(f"| {ds} | {cl} | {c['universes']} | {c['verdicts_differing']} |")
    if args.out_md:
        args.out_md.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
