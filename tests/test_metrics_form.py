"""Metrics-only form of the generation logs: what is removed, what is kept, and that the analysis is unchanged."""
import json
import shutil
from pathlib import Path

import pytest

from ragmv import analyze_generation as AG
from ragmv import metrics_form as MF

ROOT = Path(__file__).resolve().parents[1]
E2 = ROOT / "experiments" / "E2_generation" / "runs" / "qwen3-4b-kaggle-gpu"
ANSWER = "the forty-two numbered passages of the treaty"
ROW = {"job_id": "squad2:q1|fixed-128|count5", "qid": "squad2:q1", "chunking": "fixed-128", "op": "count5",
       "answers": [ANSWER], "prompt_sha256": "0" * 64, "context_words": 640,
       "retrieval": {"hit_strict": 1.0, "hit_lenient": 1.0, "coverage": 0.5}, "status": "ok",
       "response": "Unanswerable.", "latency_s": 1.2, "model_version": "m@r/f.gguf", "finish_reason": "stop",
       "usage": {"prompt_token_count": 10, "candidates_token_count": 2}, "model": "m", "hardware": "cpu",
       "called_utc": "2026-10-19T00:00:00Z", "em": 0.0, "f1": 0.0}
needs_logs = pytest.mark.skipif(not (E2 / "squad2" / "generations.jsonl").exists(),
                                reason="needs the full generation logs")


def test_metrics_row_drops_text_and_keeps_metrics():
    m = MF.to_metrics(ROW)
    assert not set(m) & set(MF.DROP) and m["response_unanswerable"] is True
    assert {k: m[k] for k in ("qid", "em", "f1", "retrieval", "usage")} == {k: ROW[k] for k in ("qid", "em", "f1", "retrieval", "usage")}
    MF.check_row(m)


@pytest.mark.parametrize("change", [lambda r: r.update(question="What?"), lambda r: r.update(extra=1)])
def test_unreviewed_field_stops_the_conversion(change):
    row = dict(ROW)
    change(row)
    with pytest.raises(MF.MetricsFormError, match="unreviewed"):
        MF.to_metrics(row)


def test_schema_rejects_text_in_a_metrics_row():
    m = MF.to_metrics(ROW)
    for bad in ({**m, "response": "x"}, {**m, "retrieval": {"hit_strict": 1.0}}, {**m, "em": "1"},
                {**m, "usage": {"prompt_token_count": 1, "note": "x"}}):
        with pytest.raises(MF.MetricsFormError):
            MF.check_row(bad)


def test_incomplete_log_is_not_converted(tmp_path):
    p = tmp_path / "generations.jsonl"
    p.write_text(json.dumps(ROW) + "\n" + json.dumps(ROW)[:20])
    with pytest.raises(MF.MetricsFormError, match="incomplete"):
        MF.convert_log(p)


@needs_logs
def test_analysis_of_the_metrics_form_equals_the_analysis_of_the_logs(tmp_path):
    run = tmp_path / "run"
    for d in ("squad2", "cuad"):
        (run / d).mkdir(parents=True)
        (run / d / "generations.metrics.jsonl").write_text(MF.convert_log(E2 / d / "generations.jsonl"))
    full = tmp_path / "full"
    for d in ("squad2", "cuad"):
        (full / d).mkdir(parents=True)
        shutil.copy(E2 / d / "generations.jsonl", full / d / "generations.jsonl")
    a, b = AG.analyse(full, reps=50), AG.analyse(run, reps=50)
    assert a == b and a["datasets"]["squad2"]["diagnostics"]["integrity"]["segments"] == ["generations.jsonl"]


def test_export_run_writes_one_metrics_file_per_log(tmp_path):
    run = tmp_path / "run" / "squad2"
    run.mkdir(parents=True)
    (run / "generations.jsonl").write_text(json.dumps(ROW) + "\n")
    (run / "jobs_meta.json").write_text("{}")
    assert MF.main(["--run", str(run.parent), "--out", str(tmp_path / "out")]) == 0
    rows = (tmp_path / "out" / "squad2" / "generations.metrics.jsonl").read_text().splitlines()
    assert len(rows) == 1 and ANSWER not in rows[0] and (tmp_path / "out" / "squad2" / "jobs_meta.json").exists()
    assert MF.main(["--run", str(run.parent), "--out", str(tmp_path / "out")]) == 2  # never into a non-empty folder
