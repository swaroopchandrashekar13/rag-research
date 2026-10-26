"""Tests of the research tools: bibliography validator and gold-span containment measures."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_bibliography as bib  # noqa: E402


def test_bibliography_file_is_valid():
    entries = bib.load(ROOT / "literature" / "bibliography.yaml")
    assert bib.validate(entries) == []


def test_validator_rejects_l0_duplicates_and_missing_fields():
    entries = [
        {"key": "a", "title": "t", "year": 2024, "venue": "v", "verification": "L0", "directions": ["C1"], "url": "u"},
        {"key": "a", "title": "t", "year": 2024, "venue": "v", "verification": "L1", "directions": ["C1"]},
    ]
    errors = " ".join(bib.validate(entries))
    assert "L0 entries" in errors and "duplicate key" in errors and "url or an id" in errors


def test_citation_gate_blocks_under_verified_sources():
    entries = [{"key": "x", "verification": "L1"}, {"key": "y", "verification": "L3"}]
    assert bib.citable(entries, ["y"], "L2") == []
    assert "verified only to L1" in bib.citable(entries, ["x"], "L2")[0]
    assert "not in bibliography" in bib.citable(entries, ["z"], "L2")[0]


def test_gold_containment_measures_match_brute_force():
    """contained/touched/best_fraction against a set-based reference on random partitions and spans."""
    import importlib.util
    import random

    spec = importlib.util.spec_from_file_location("gold_containment", Path(__file__).resolve().parents[1] / "tools/gold_containment.py")
    gc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gc)
    rnd = random.Random(0)
    for _ in range(300):
        n = rnd.randint(1, 60)
        cuts = sorted(rnd.sample(range(1, n), rnd.randint(0, min(8, n - 1)))) if n > 1 else []
        bounds = [0] + cuts + [n]
        chunks = list(zip(bounds[:-1], bounds[1:]))
        starts = [a for a, _ in chunks]
        s = rnd.randrange(n)
        e = rnd.randint(s + 1, n)
        words = set(range(s, e))
        ref_touch = sum(1 for a, b in chunks if words & set(range(a, b)))
        ref_frac = max(len(words & set(range(a, b))) for a, b in chunks) / len(words)
        assert gc.touched(chunks, starts, (s, e)) == ref_touch
        assert gc.best_fraction(chunks, starts, (s, e)) == ref_frac
        assert gc.contained(chunks, starts, (s, e)) == (ref_touch == 1)


def test_planned_chunkers_partition_documents():
    """The containment measures assume sorted, contiguous, non-overlapping chunks covering the document."""
    from ragmv.chunking import ChunkSpec, chunk_document
    from ragmv.data import make_document

    text = "\n\n".join(" ".join(f"w{p}x{i}." if i % 7 == 6 else f"W{p}x{i}" for i in range(n))
                       for p, n in enumerate([3, 40, 1, 130, 600, 9]))
    doc = make_document("d", text)
    for fam in ("fixed", "sentence", "paragraph"):
        for w in (64, 128, 256, 512):
            c = chunk_document(doc, ChunkSpec(fam, w))
            assert c[0][0] == 0 and c[-1][1] == doc.n_words
            assert all(a < b and b - a <= w for a, b in c)
            assert all(c[i][1] == c[i + 1][0] for i in range(len(c) - 1))


def test_compare_rerun_identical_and_changed(tmp_path):
    import importlib.util
    import shutil

    import numpy as np

    from test_run_validation import write_run

    spec = importlib.util.spec_from_file_location("compare_rerun", ROOT / "tools/compare_rerun.py")
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    stored = write_run(tmp_path / "stored", datasets=("squad2",), chunkings=["fixed-128", "fixed-512"])
    new = tmp_path / "new"
    shutil.copytree(stored, new)
    assert cr.main(["--stored", str(stored), "--new", str(new), "--out-json", str(tmp_path / "a.json")]) == 0
    res = json.loads((tmp_path / "a.json").read_text())["datasets"]["squad2"]
    assert res["chunkings"]["fixed-128"]["identical_share"] == 1.0
    assert res["claims"]["fixed-128 vs fixed-512"]["verdicts_differing"] == 0
    z = dict(np.load(new / "squad2" / "fixed-128.npz"))
    z["scores"] = (z["scores"].astype(np.float32) * 0.5).astype(np.float16)
    np.savez_compressed(new / "squad2" / "fixed-128.npz", **z)
    assert cr.main(["--stored", str(stored), "--new", str(new), "--out-json", str(tmp_path / "b.json")]) == 0
    res = json.loads((tmp_path / "b.json").read_text())["datasets"]["squad2"]
    assert res["chunkings"]["fixed-128"]["identical_share"] < 1.0 and res["chunkings"]["fixed-512"]["identical_share"] == 1.0
    (new / "squad2" / "fixed-512.npz").unlink()
    assert cr.main(["--stored", str(stored), "--new", str(new), "--out-json", str(tmp_path / "c.json")]) == 1
