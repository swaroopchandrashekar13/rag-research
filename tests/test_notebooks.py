"""The Kaggle notebook scripts copy the code from a local folder or .zip, check its content digest on request, and
resume only from an explicitly attached earlier output. No network, no model download."""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "experiments" / "E2_generation" / "notebook_tier2.py"


def _load(monkeypatch, tmp_path):
    monkeypatch.setenv("RAGMV_NOTEBOOK_BASE", str(tmp_path / "base"))
    for k in ("RAGMV_SOURCE", "RAGMV_CODE_SHA256", "RAGMV_RESUME_FROM", "RAGMV_CODE_READY"):
        monkeypatch.delenv(k, raising=False)
    spec = importlib.util.spec_from_file_location("notebook_tier2_under_test", NB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def project(tmp_path):
    """A minimal project copy: the package's integrity module, a manifest and a downloaded-data folder."""
    src = tmp_path / "project"
    (src / "src" / "ragmv").mkdir(parents=True)
    (src / "src" / "ragmv" / "__init__.py").write_text("")
    shutil.copy(ROOT / "src/ragmv/integrity.py", src / "src/ragmv/integrity.py")
    (src / "data" / "raw").mkdir(parents=True)
    (src / "data" / "MANIFEST.yaml").write_text("datasets: {}\n")
    (src / "data" / "raw" / "big.json").write_text("{}")
    (src / "experiments" / "E2_generation").mkdir(parents=True)
    shutil.copy(NB, src / "experiments" / "E2_generation" / "notebook_tier2.py")
    return src


def test_project_is_found_from_the_script_location(monkeypatch, tmp_path, project):
    nb = _load(monkeypatch, tmp_path)
    assert nb.find_source(project / "experiments" / "E2_generation" / "notebook_tier2.py") == project.resolve()
    monkeypatch.setenv("RAGMV_SOURCE", str(tmp_path / "elsewhere"))
    assert nb.find_source(None) == tmp_path / "elsewhere"
    monkeypatch.delenv("RAGMV_SOURCE")
    with pytest.raises(SystemExit, match="Cannot find the project"):
        nb.find_source(tmp_path / "not-a-project" / "x.py")


def test_folder_copy_keeps_the_manifest_and_skips_downloaded_data(monkeypatch, tmp_path, project):
    nb = _load(monkeypatch, tmp_path)
    dest = nb.copy_code(project, tmp_path / "code")
    assert (dest / "data" / "MANIFEST.yaml").exists() and not (dest / "data" / "raw").exists()
    assert (dest / "src" / "ragmv" / "integrity.py").read_bytes() == (ROOT / "src/ragmv/integrity.py").read_bytes()


def test_zip_copy_and_digest_check(monkeypatch, tmp_path, project):
    nb = _load(monkeypatch, tmp_path)
    archive = shutil.make_archive(str(tmp_path / "ragmv"), "zip", tmp_path, "project")
    dest = nb.copy_code(archive, tmp_path / "code-zip")
    assert (dest / "src" / "ragmv" / "__init__.py").exists() and (dest / "data" / "MANIFEST.yaml").exists()
    digest = nb.code_digest(dest)
    monkeypatch.setenv("RAGMV_CODE_SHA256", digest)
    nb.copy_code(project, tmp_path / "code-ok")  # matching digest: accepted
    monkeypatch.setenv("RAGMV_CODE_SHA256", "0" * 64)
    with pytest.raises(SystemExit, match="content digest"):
        nb.copy_code(project, tmp_path / "code-bad")


def test_resume_copies_only_an_explicit_earlier_output(monkeypatch, tmp_path):
    nb = _load(monkeypatch, tmp_path)
    run_dir = tmp_path / "out" / "runs" / "qwen3-4b-kaggle-gpu"
    nb.resume_from("qwen3-4b-kaggle-gpu", run_dir)  # nothing attached: nothing happens
    assert not run_dir.exists()
    prev = tmp_path / "previous" / "ragmv_tier2"
    rows = prev / "runs" / "qwen3-4b-kaggle-gpu" / "squad2"
    rows.mkdir(parents=True)
    (rows / "generations.jsonl").write_text(json.dumps({"job_id": "a", "status": "ok"}) + "\n")
    monkeypatch.setenv("RAGMV_RESUME_FROM", str(prev))
    nb.resume_from("qwen3-4b-kaggle-gpu", run_dir)
    assert nb.ok_count(run_dir / "squad2" / "generations.jsonl") == 1
    with pytest.raises(SystemExit, match="does not exist"):
        nb.resume_from("another-run", tmp_path / "out" / "runs" / "another-run")


def test_notebooks_do_not_clone_or_push():
    for path in (NB, ROOT / "experiments" / "E3_semantic_dense" / "notebook_study1b.py"):
        code = "\n".join(line for line in path.read_text().splitlines() if not line.lstrip().startswith("#"))
        assert '"git"' not in code and "GITHUB_TOKEN" not in code and "wget" not in code
