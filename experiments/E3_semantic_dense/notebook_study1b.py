# Study 1b (E3: semantic chunking + dense retrieval) on Kaggle: run this file from one notebook cell.
#
# 1. Attach the project to the notebook as a dataset (the folder itself or a .zip of it), e.g. /kaggle/input/ragmv.
# 2. Optionally choose the split and a run name, then run it from that copy:
#      import os; os.environ["RAGMV_SPLIT"] = "confirmatory"      # default: "exploratory" (the pilot)
#      os.environ["RAGMV_RUN_NAME"] = "confirmatory-kaggle-gpu-rerun"   # default: <split>-kaggle-<gpu|cpu>
#      %run /kaggle/input/ragmv/experiments/E3_semantic_dense/notebook_study1b.py
#    The code is located and copied exactly as for Tier 2 (experiments/E2_generation/notebook_tier2.py), including the
#    optional RAGMV_SOURCE and RAGMV_CODE_SHA256 settings.
#
# Kaggle settings: Accelerator GPU T4 x2 (a GPU is needed in practice: ~5M words are embedded with bge-m3), Internet On.
# Results are written to the notebook's output folder; a dataset whose manifest already exists there is skipped, so a
# new session continues after attaching the previous output and setting RAGMV_RESUME_FROM to its ragmv_study1b folder.
# The embedding cache lives in the working directory and is not part of the output.
#
# Verification rerun of the stored confirmatory run (optional; no result depends on it): set RAGMV_SPLIT and
# RAGMV_RUN_NAME as above. After the run, the script analyses it with the consistent procedure (query and document
# unit) and the planned procedure, and compares it cell by cell with the stored run (tools/compare_rerun.py). Download
# study1b_results.zip and unpack it into experiments/E3_semantic_dense/ (runs/<name>, analysis/<name>-*).
#
# The confirmatory split runs only if research/analysis_plan_study1b.md is at version 1.0.
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SPLIT = os.environ.get("RAGMV_SPLIT", "exploratory")
DATASETS = ("squad2", "covidqa", "cuad", "qasper")


def _helpers(this_file=None):
    """Import the Tier 2 notebook helpers from the same project copy as this script."""
    here = Path(this_file).resolve().parent if this_file else None
    candidates = ([here.parent / "E2_generation"] if here else []) + \
                 [Path(os.environ.get("RAGMV_SOURCE", "")) / "experiments" / "E2_generation"]
    for c in candidates:
        if (c / "notebook_tier2.py").exists():
            sys.path.insert(0, str(c))
            import notebook_tier2

            return notebook_tier2
    raise SystemExit("Cannot find experiments/E2_generation/notebook_tier2.py next to this script; set RAGMV_SOURCE.")


def main(this_file=None):
    nb = _helpers(this_file)
    nb.OUT = Path("/kaggle/working/ragmv_study1b") if nb.KAGGLE else nb.BASE / "out1b"
    nb.log(f"Study 1b, split {SPLIT}; GPU present: {nb.gpu_present()}")
    if not nb.gpu_present():
        nb.log("WARNING: no GPU. Embedding the corpora on CPU takes many hours; enable a GPU accelerator.")
    nb.setup_code_and_venv(this_file)
    plan = (nb.CODE / "research" / "analysis_plan_study1b.md").read_text()
    if SPLIT == "confirmatory" and "| Version | **1.0**" not in plan:
        raise SystemExit("Refusing the confirmatory split: analysis_plan_study1b.md is not at version 1.0 yet.")
    nb.sh([nb.PY, "-m", "pip", "install", "-q", "-r", str(nb.CODE / "requirements" / "dense.txt")])
    nb.sh([nb.PY, "-I", "-m", "ragmv.fetch"], cwd=nb.CODE)
    run_name = os.environ.get("RAGMV_RUN_NAME") or f"{SPLIT}-{nb.PLATFORM}-{'gpu' if nb.gpu_present() else 'cpu'}"
    run_dir = nb.OUT / "runs" / run_name
    prev = os.environ.get("RAGMV_RESUME_FROM")
    if prev and not run_dir.exists():
        shutil.copytree(Path(prev) / "runs" / run_name, run_dir)
        nb.log(f"resumed from {prev}")
    run_dir.mkdir(parents=True, exist_ok=True)
    env = dict(nb.CLEAN_ENV, HF_HOME=str(nb.BASE / "hf"))
    for ds in DATASETS:
        if (run_dir / ds / "manifest.json").exists():
            nb.log(f"{ds}: already done")
            continue
        t0 = time.time()
        nb.sh([nb.PY, "-I", "-m", "ragmv.run1b", "--dataset", ds, "--split", SPLIT, "--out", str(run_dir),
               "--device", "cuda" if nb.gpu_present() else "cpu", "--batch-size", "32",
               "--cache-dir", str(nb.BASE / "emb_cache")], cwd=nb.CODE, env=env)
        nb.log(f"{ds}: done in {(time.time() - t0) / 60:.1f} min")
    label = "EXPLORATORY" if SPLIT == "exploratory" else "CONFIRMATORY"
    for suffix, extra in (("consistent-query", []), ("consistent-document", ["--unit", "document"]),
                          ("planned", ["--inference", "planned"])):
        analysis = nb.OUT / "analysis" / f"{run_name}-{suffix}"
        if not (analysis / "results.json").exists():
            nb.sh([nb.PY, "-I", "-m", "ragmv.analyze1b", "--run", str(run_dir), "--label", label, "--out", str(analysis),
                   *extra], cwd=nb.CODE, env=env)
    stored = nb.CODE / "experiments" / "E3_semantic_dense" / "runs" / f"{SPLIT}-kaggle-gpu"
    if stored.exists() and stored.resolve() != run_dir.resolve():
        cmp = nb.OUT / "analysis" / f"{run_name}-compare-with-stored"
        cmp.mkdir(parents=True, exist_ok=True)
        subprocess.run([nb.PY, "-I", "tools/compare_rerun.py", "--stored", str(stored), "--new", str(run_dir),
                        "--out-json", str(cmp / "results.json"), "--out-md", str(cmp / "results.md")],
                       cwd=nb.CODE, env=env, check=False)
    archive = shutil.make_archive(str(nb.OUT.parent / "study1b_results"), "zip", nb.OUT)
    nb.log(f"STUDY 1B RUN COMPLETE: {nb.OUT} and {archive}")


if __name__ == "__main__":
    main(globals().get("__file__"))
