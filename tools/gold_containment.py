"""POST-HOC: how often does a query's gold evidence fit inside a single chunk?

For every confirmatory query and chunking, a query counts as *contained* when at least one of its gold word spans lies
entirely inside one chunk. This is a property of the chunk boundaries and the annotations alone (no retrieval). It
measures how far each chunker's boundaries line up with the datasets' annotation units: the SQuAD, COVID-QA and CUAD
documents are assembled by joining the datasets' own contexts with blank lines, and Qasper's gold evidence consists
of whole paragraphs, so paragraph packing never splits a gold span that lies within one paragraph shorter than the cap.
Also reported: the median length (words) of each query's shortest gold span, and two multi-chunk measures: the
number of chunks the query's least-split gold span touches (1 = contained) and the largest share of a gold span that
one chunk holds. Containment is necessary for a strict hit from a single chunk, but a strict hit can also come from
several retrieved chunks that together cover a split span; the measures describe the chunk boundaries, not retrieval.

With --run (the Study 1 confirmatory run), the S3-256 comparison (paragraph-256 minus fixed-256, mean over all
budget-matched and all count-matched universes of the run) is also split by whether fixed-256 keeps the query's gold
evidence in one chunk. This is descriptive: the strata are not randomised, and queries whose evidence fixed-256
splits also differ in evidence length.

Usage: python -I tools/gold_containment.py --data-root data/raw --out-json FILE [--out-md FILE] [--run RUN_DIR]
"""
from __future__ import annotations

import argparse
import bisect
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragmv import data as D  # noqa: E402
from ragmv.chunking import ChunkSpec, chunk_document  # noqa: E402

DATASETS = ("squad2", "covidqa", "cuad", "qasper")
CHUNKINGS = [ChunkSpec(f, w) for w in (128, 256, 512) for f in ("fixed", "sentence", "paragraph")]


def contained(chunks: list[tuple[int, int]], starts: list[int], span: tuple[int, int]) -> bool:
    """True if the word span [s, e) lies inside one chunk (chunks sorted by start, non-overlapping)."""
    s, e = span
    i = bisect.bisect_right(starts, s) - 1
    return i >= 0 and chunks[i][0] <= s and e <= chunks[i][1]


def touched(chunks: list[tuple[int, int]], starts: list[int], span: tuple[int, int]) -> int:
    """Number of chunks that overlap the word span [s, e) (chunks sorted, non-overlapping)."""
    s, e = span
    lo = max(bisect.bisect_right(starts, s) - 1, 0)
    hi = bisect.bisect_left(starts, e)
    return sum(1 for a, b in chunks[lo:hi] if min(b, e) > max(a, s))


def best_fraction(chunks: list[tuple[int, int]], starts: list[int], span: tuple[int, int]) -> float:
    """Largest share of the span's words inside a single chunk."""
    s, e = span
    lo = max(bisect.bisect_right(starts, s) - 1, 0)
    hi = bisect.bisect_left(starts, e)
    return max((max(0, min(b, e) - max(a, s)) for a, b in chunks[lo:hi]), default=0) / (e - s)


def stratified_s3(run_ds: Path, docs, conf) -> dict:
    """Mean per-query S3-256 difference (all universes of a protocol), split by fixed-256 containment."""
    q = json.loads((run_ds / "queries.json").read_text())
    m = json.loads((run_ds / "manifest.json").read_text())["config"]
    by_id = {x.qid: x for x in conf}
    if sorted(q["qids"]) != sorted(by_id):
        raise SystemExit(f"{run_ds}: the run's queries differ from the confirmatory queries rebuilt from the data")
    spec = ChunkSpec("fixed", 256)
    cache, flag = {}, []
    for qid in q["qids"]:
        x = by_id[qid]
        if x.doc_idx not in cache:
            c = sorted(chunk_document(docs[x.doc_idx], spec))
            cache[x.doc_idx] = (c, [a for a, _ in c])
        c, starts = cache[x.doc_idx]
        flag.append(any(contained(c, starts, g) for g in x.gold))
    flag = np.asarray(flag)
    with np.load(run_ds / "paragraph-256.npz") as a, np.load(run_ds / "fixed-256.npz") as b:
        delta = a["scores"].astype(np.float64) - b["scores"].astype(np.float64)  # [R, n, ops, M]
    out = {}
    for prot, kind in (("count", "k"), ("budget", "B")):
        ops = [i for i, lab in enumerate(m["ops"]) if lab[0] == kind and (kind == "k" or int(lab[1:]) >= 256)]
        per_q = delta[:, :, ops, :].mean(axis=(0, 2, 3))
        out[prot] = {name: {"n": int(sel.sum()), "mean_delta": float(per_q[sel].mean()) if sel.any() else None}
                     for name, sel in (("contained", flag), ("split", ~flag))}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", type=Path)
    ap.add_argument("--run", type=Path, help="Study 1 run directory for the stratified S3-256 comparison")
    args = ap.parse_args(argv)
    res = {"label": "POST-HOC (not part of the analysis plans)", "split": "confirmatory", "contained_share": {},
           "median_shortest_gold_words": {}, "n_queries": {}, "chunks_touched_share": {},
           "mean_best_single_chunk_fraction": {}}
    strata = {}
    for d in DATASETS:
        docs, queries = D.load(d, args.data_root)
        exploratory = D.split_documents(len(docs))
        conf = [q for q in queries if not exploratory[q.doc_idx]]
        if args.run:
            strata[d] = stratified_s3(args.run / d, docs, conf)
        res["n_queries"][d] = len(conf)
        res["median_shortest_gold_words"][d] = float(np.median([min(e - s for s, e in q.gold) for q in conf]))
        for spec in CHUNKINGS:
            chunks = {}
            hits = 0
            n_touch, frac = [], []
            for q in conf:
                if q.doc_idx not in chunks:
                    c = sorted(chunk_document(docs[q.doc_idx], spec))
                    chunks[q.doc_idx] = (c, [a for a, _ in c])
                c, starts = chunks[q.doc_idx]
                hits += any(contained(c, starts, g) for g in q.gold)
                n_touch.append(min(touched(c, starts, g) for g in q.gold))
                frac.append(max(best_fraction(c, starts, g) for g in q.gold))
            key = f"{d}/{spec.name}"
            res["contained_share"][key] = hits / len(conf)
            n_touch = np.asarray(n_touch)
            res["chunks_touched_share"][key] = {"1": float((n_touch == 1).mean()), "2": float((n_touch == 2).mean()),
                                                "3+": float((n_touch >= 3).mean())}
            res["mean_best_single_chunk_fraction"][key] = float(np.mean(frac))
    if args.run:
        res["s3_256_by_fixed_containment"] = strata
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(res, indent=2) + "\n")
    lines = ["# Gold-span containment (POST-HOC, not part of the analysis plans)", "",
             "Share of confirmatory queries with at least one gold span inside a single chunk.", "",
             "| Chunking | " + " | ".join(DATASETS) + " |", "|---|" + "---:|" * len(DATASETS)]
    for spec in CHUNKINGS:
        lines.append(f"| {spec.name} | " + " | ".join(f"{100 * res['contained_share'][f'{d}/{spec.name}']:.1f}"
                                                     for d in DATASETS) + " |")
    lines += ["", "Median length of each query's shortest gold span (words): "
              + ", ".join(f"{d} {res['median_shortest_gold_words'][d]:g}" for d in DATASETS) + ".", "",
              "Mean largest share of a gold span held by one chunk (%):", "",
              "| Chunking | " + " | ".join(DATASETS) + " |", "|---|" + "---:|" * len(DATASETS)]
    for spec in CHUNKINGS:
        lines.append(f"| {spec.name} | " + " | ".join(
            f"{100 * res['mean_best_single_chunk_fraction'][f'{d}/{spec.name}']:.1f}" for d in DATASETS) + " |")
    lines += ["", "Share of queries whose least-split gold span touches 3 or more chunks (%):", "",
              "| Chunking | " + " | ".join(DATASETS) + " |", "|---|" + "---:|" * len(DATASETS)]
    for spec in CHUNKINGS:
        lines.append(f"| {spec.name} | " + " | ".join(
            f"{100 * res['chunks_touched_share'][f'{d}/{spec.name}']['3+']:.1f}" for d in DATASETS) + " |")
    if args.run:
        lines += ["", "S3-256 (paragraph-256 minus fixed-256), mean per-query difference over the run's universes, by "
                  "whether fixed-256 keeps a gold span in one chunk (descriptive):", "",
                  "| Dataset | Protocol | Contained: n | mean Δ | Split: n | mean Δ |", "|---|---|---:|---:|---:|---:|"]
        for d, v in strata.items():
            for prot in ("count", "budget"):
                a, b = v[prot]["contained"], v[prot]["split"]
                fmt = (lambda x: "—" if x is None else f"{x:+.4f}")
                lines.append(f"| {d} | {prot} | {a['n']} | {fmt(a['mean_delta'])} | {b['n']} | {fmt(b['mean_delta'])} |")
    if args.out_md:
        args.out_md.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
