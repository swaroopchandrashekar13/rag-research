# Tier 2 (E2) generation on Kaggle or Google Colab: run this file from one notebook cell.
#
# 1. Attach the project to the notebook as a dataset (the folder itself or a .zip of it), e.g. /kaggle/input/ragmv.
# 2. Run it from that copy:      %run /kaggle/input/ragmv/experiments/E2_generation/notebook_tier2.py
#    The project is located from this script's own path; RAGMV_SOURCE (a folder or a .zip) overrides it. The code is
#    copied to local disk, and its content digest is printed; set RAGMV_CODE_SHA256 to refuse any other code.
# 3. To continue an unfinished run in a new session, attach the previous session's output as a dataset and set
#    RAGMV_RESUME_FROM to its ragmv_tier2 folder: finished jobs are copied in and skipped.
#
# KAGGLE: Session options -> Accelerator: GPU T4 x2 (CPU also works, just slower); Internet: On (the datasets and the
# model are downloaded and checked against their digests). Results are written to the notebook's output folder and
# zipped at the end.
#
# GPU: llama-cpp-python 0.3.36 is built with CUDA. Kaggle keeps libcuda.so in /usr/local/nvidia/lib64, outside the
# toolkit's stubs folders, so CMake's CUDA::cuda_driver target is not created unless CUDA_cuda_driver_LIBRARY is set;
# the build passes it (and links the library into the stubs folder). GPU offload is then verified with
# llama_supports_gpu_offload(); if the build or the check fails, the run falls back to CPU (same model and decoding,
# only slower). CPU and GPU rows go to differently named runs and are never mixed.
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

DATASETS = ("squad2", "covidqa", "cuad", "qasper")
JOBS_PER_DATASET = 400
MAX_HOURS = float(os.environ.get("RAGMV_MAX_HOURS", 11.5))  # stop cleanly before Kaggle's 12 h session limit

KAGGLE = Path("/kaggle/working").exists()
COLAB = "google.colab" in sys.modules or Path("/content").exists() and not KAGGLE
PLATFORM = "kaggle" if KAGGLE else "colab" if COLAB else "local"
BASE = Path(os.environ.get("RAGMV_NOTEBOOK_BASE", "/tmp/ragmv"))  # venv, code and model: local disk, not output
OUT = Path("/kaggle/working/ragmv_tier2") if KAGGLE else BASE / "out"  # notebook output (runs, analysis, zip)
CODE, VENV = BASE / "code", BASE / "venv"
PY = str(VENV / "bin" / "python")
# Kaggle's PYTHONPATH carries a sitecustomize that imports wrapt; keep it away from the venv and the build
CLEAN_ENV = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
T0 = time.time()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sh(cmd, check=True, env=None, cwd=None, capture=False):
    shown = cmd if isinstance(cmd, str) else " ".join(map(str, cmd))
    log("$ " + shown)
    r = subprocess.run(cmd, shell=isinstance(cmd, str), env=env or CLEAN_ENV, cwd=cwd, text=True,
                       capture_output=capture)
    if check and r.returncode:
        raise RuntimeError(f"command failed ({r.returncode}): {shown}")
    return r


def project_root(path) -> Path | None:
    """The project directory containing `path` (a folder with src/ragmv), or None."""
    for p in [Path(path).resolve(), *Path(path).resolve().parents]:
        if (p / "src" / "ragmv" / "__init__.py").exists():
            return p
    return None


def find_source(this_file=None) -> Path:
    """RAGMV_SOURCE if set, else the project this script belongs to."""
    src = os.environ.get("RAGMV_SOURCE")
    if src:
        return Path(src)
    root = project_root(this_file) if this_file else None
    if root is None:
        raise SystemExit("Cannot find the project: run this script from the attached project folder, or set "
                         "RAGMV_SOURCE to the project folder or a .zip of it.")
    return root


def copy_code(source, dest=None) -> Path:
    """Fresh copy of the project (a folder or a .zip) into `dest`; returns the project root inside it."""
    dest = Path(dest or CODE)
    if dest.exists():
        shutil.rmtree(dest)
    source = Path(source)
    if source.suffix == ".zip":
        with zipfile.ZipFile(source) as zf:
            zf.extractall(dest)
        root = next((p.parent.parent.parent for p in dest.rglob("src/ragmv/__init__.py")), None)
        if root is None:
            raise SystemExit(f"{source} does not contain the project (no src/ragmv)")
        if root != dest:
            tmp = dest.with_name(dest.name + ".tmp")
            shutil.move(str(root), str(tmp))
            shutil.rmtree(dest)
            shutil.move(str(tmp), str(dest))
    else:
        if project_root(source) != source.resolve():
            raise SystemExit(f"{source} is not the project folder (no src/ragmv)")
        raw = (source / "data" / "raw").resolve()

        def skip(folder, names):  # caches, version control and downloaded datasets are not copied
            return [n for n in names if n in ("__pycache__", ".git") or n.endswith(".pyc")
                    or (Path(folder).resolve() / n) == raw]

        shutil.copytree(source, dest, ignore=skip)
    got = code_digest(dest)
    log(f"code copied from {source}; content digest of src/ragmv: {got}")
    want = os.environ.get("RAGMV_CODE_SHA256")
    if want and got != want:
        raise SystemExit(f"code content digest {got} != RAGMV_CODE_SHA256 {want}; refusing to run")
    return dest


def code_digest(root) -> str:
    return subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, 'src'); "
                           "from ragmv.integrity import source_digest; print(source_digest()['sha256'])"],
                          cwd=str(root), capture_output=True, text=True, check=True).stdout.strip()


# ----------------------------------------------------------------------------- environment
def setup_code_and_venv(this_file=None):
    BASE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if not ((CODE / "src" / "ragmv").exists() and os.environ.get("RAGMV_CODE_READY") == "1"):
        copy_code(find_source(this_file))
    if not Path(PY).exists():
        sh([sys.executable, "-m", "pip", "install", "-q", "virtualenv"])
        sh([sys.executable, "-m", "virtualenv", "-q", str(VENV)])  # seeds its own pip (no ensurepip needed)
    reqs = [line for line in (CODE / "requirements" / "core.txt").read_text().splitlines()
            if line.strip() and not line.startswith("#")]
    reqs += [line for line in (CODE / "requirements" / "generation.txt").read_text().splitlines()
             if line.strip() and not line.startswith(("#", "llama-cpp-python", "google-genai"))]
    (BASE / "reqs.txt").write_text("\n".join(reqs) + "\n")
    sh([PY, "-m", "pip", "install", "-q", "-r", str(BASE / "reqs.txt")])
    sh([PY, "-m", "pip", "install", "-q", "--no-deps", "-e", str(CODE)])


def gpu_present():
    return subprocess.run("nvidia-smi -L", shell=True, capture_output=True).returncode == 0


def cuda_build_env():
    """CMAKE_ARGS that let CMake create CUDA::cuda_driver on Kaggle/Colab images."""
    candidates = ["/usr/local/nvidia/lib64/libcuda.so", "/usr/lib/x86_64-linux-gnu/libcuda.so",
                  "/usr/lib64/libcuda.so", *glob.glob("/usr/local/cuda*/lib64/stubs/libcuda.so"),
                  *glob.glob("/usr/local/nvidia/lib64/libcuda.so.*")]
    libcuda = next((c for c in candidates if Path(c).exists()), None)
    cap = subprocess.run(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"], capture_output=True,
                         text=True).stdout.split()
    arch = cap[0].replace(".", "") if cap else "75"
    args = ["-DGGML_CUDA=on", f"-DCMAKE_CUDA_ARCHITECTURES={arch}"]
    env = dict(CLEAN_ENV)
    if libcuda:
        args.append(f"-DCUDA_cuda_driver_LIBRARY={libcuda}")
        libdir = str(Path(libcuda).parent)
        args.append(f"-DCMAKE_LIBRARY_PATH={libdir}")
        env["LIBRARY_PATH"] = libdir + os.pathsep + env.get("LIBRARY_PATH", "")
        env["LD_LIBRARY_PATH"] = libdir + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        for stubs in glob.glob("/usr/local/cuda*/lib64") + glob.glob("/usr/local/cuda*/targets/x86_64-linux/lib"):
            try:  # second route for FindCUDAToolkit, which searches <toolkit>/lib64/stubs
                Path(stubs, "stubs").mkdir(exist_ok=True)
                if not Path(stubs, "stubs", "libcuda.so").exists():
                    os.symlink(libcuda, Path(stubs, "stubs", "libcuda.so"))
            except OSError:
                pass
    log(f"CUDA build: arch {arch}, libcuda {libcuda}")
    env["CMAKE_ARGS"] = " ".join(args)
    env["CMAKE_BUILD_PARALLEL_LEVEL"] = str(os.cpu_count() or 4)
    return env


def install_llama(flavour):
    """Build and install llama-cpp-python 0.3.36; returns True if GPU offload works (for flavour 'gpu')."""
    wheel_dir = BASE / "wheels" / flavour
    wheel_dir.mkdir(parents=True, exist_ok=True)
    if not glob.glob(str(wheel_dir / "llama_cpp_python-0.3.36-*.whl")):
        env = cuda_build_env() if flavour == "gpu" else dict(CLEAN_ENV, CMAKE_ARGS="-DGGML_CUDA=off")
        build_log = OUT / f"build_{flavour}.log"
        log(f"building llama-cpp-python ({flavour}); GPU builds take ~15-25 min; log: {build_log}")
        with open(build_log, "w") as f:
            r = subprocess.run([PY, "-m", "pip", "wheel", "-v", "--no-deps", "llama-cpp-python==0.3.36",
                                "-w", str(wheel_dir)], env=env, stdout=f, stderr=subprocess.STDOUT)
        if r.returncode:
            tail = build_log.read_text().splitlines()[-25:]
            log(f"{flavour} build FAILED; last lines:\n" + "\n".join(tail))
            return False
    sh([PY, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps",
        glob.glob(str(wheel_dir / "llama_cpp_python-0.3.36-*.whl"))[0]])
    sh([PY, "-m", "pip", "install", "-q", "typing-extensions", "diskcache", "jinja2"])
    check = sh([PY, "-c", "import llama_cpp; print(llama_cpp.__version__, llama_cpp.llama_supports_gpu_offload())"],
               capture=True, check=False)
    log(f"llama_cpp check: {check.stdout.strip()} {check.stderr.strip()[-300:]}")
    if flavour == "gpu":
        return check.returncode == 0 and check.stdout.strip().endswith("True")
    return check.returncode == 0


def ok_count(path):
    """Successful jobs in a dataset's log (all segments). A half-written final line from an interrupted session is
    tolerated here explicitly (progress counting only); the generator handles it with --recover-incomplete-tail."""
    n = set()
    seg_dir = Path(path).parent
    paths = ([Path(path)] if Path(path).exists() else []) + sorted(seg_dir.glob("generations.seg-[0-9][0-9][0-9].jsonl"))
    for p in paths:
        lines = p.read_text().split("\n")
        for i, line in enumerate(lines):
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                if i == len(lines) - 1:  # unterminated final line only
                    continue
                raise
            if row.get("status") == "ok":
                n.add(row["job_id"])
    return len(n)


def resume_from(run_name, run_dir):
    """Copy an earlier session's rows of the same run (RAGMV_RESUME_FROM) into run_dir; the generator then skips them."""
    prev = os.environ.get("RAGMV_RESUME_FROM")
    if not prev:
        return
    src = Path(prev) / "runs" / run_name
    if not src.exists():
        raise SystemExit(f"RAGMV_RESUME_FROM: {src} does not exist (the run name must match: {run_name})")
    if run_dir.exists() and any(run_dir.iterdir()):
        log(f"{run_dir} already has rows; not copying from {src}")
        return
    shutil.copytree(src, run_dir, dirs_exist_ok=True)
    log(f"resumed from {src}: {sum(ok_count(run_dir / d / 'generations.jsonl') for d in DATASETS)} jobs already done")


# ----------------------------------------------------------------------------- main
def main(this_file=None):
    log(f"platform {PLATFORM}; GPU present: {gpu_present()}")
    setup_code_and_venv(this_file)
    flavour = "gpu" if gpu_present() and install_llama("gpu") else "cpu"
    if flavour == "cpu":
        if gpu_present():
            log("GPU build/offload not available -> CPU build (same model and decoding; slower)")
        if not install_llama("cpu"):
            raise RuntimeError("CPU build failed too; see the build log in the output folder")
    run_name = f"qwen3-4b-{PLATFORM}-{flavour}"
    run_dir = OUT / "runs" / run_name
    resume_from(run_name, run_dir)
    sh([PY, "-I", "-m", "ragmv.fetch"], cwd=CODE)
    log(f"run {run_name}: {run_dir}")
    timed_out = False
    try:
        for ds in DATASETS:
            done = ok_count(run_dir / ds / "generations.jsonl")
            log(f"{ds}: {done}/{JOBS_PER_DATASET} done")
            if done >= JOBS_PER_DATASET:
                continue
            cmd = [PY, "-I", "-m", "ragmv.generate", "--backend", "llama", "--model", "qwen3-4b-q4_k_m",
                   "--model-dir", str(BASE / "models"), "--n-gpu-layers", "-1" if flavour == "gpu" else "0",
                   "--threads", str(os.cpu_count() or 4), "--dataset", ds, "--out", str(run_dir),
                   "--recover-incomplete-tail"]  # explicit: sessions can be killed mid-write; reported per session
            proc = subprocess.Popen(cmd, cwd=CODE, env=CLEAN_ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True)
            for line in proc.stdout:  # stream progress lines (s/job, time left)
                print(line, end="", flush=True)
                if time.time() - T0 > MAX_HOURS * 3600:
                    timed_out = True
                    proc.terminate()
                    break
            proc.wait()
            if timed_out:
                log(f"reached {MAX_HOURS} h; stopping before the session limit")
                break
            if proc.returncode == 2:
                raise RuntimeError(f"{ds}: generator could not start (exit 2); see the message above")
            if proc.returncode:
                log(f"{ds}: generator exited with {proc.returncode} (3 = incomplete); continuing with the next dataset")
    finally:
        counts = {ds: ok_count(run_dir / ds / "generations.jsonl") for ds in DATASETS}
        total = sum(counts.values())
        log(f"completed jobs: {counts} ({total}/1600)")
        if total >= 1600:
            analysis = OUT / "analysis" / f"{run_name}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
            sh([PY, "-I", "-m", "ragmv.analyze_generation", "--run", str(run_dir), "--out", str(analysis)], cwd=CODE,
               check=False)
        archive = shutil.make_archive(str(OUT.parent / "tier2_results"), "zip", OUT)  # outside OUT: never zips itself
        if total >= 1600:
            log(f"ALL 1600 JOBS DONE. Results: {OUT} and {archive}")
        else:
            log(f"NOT FINISHED ({total}/1600). Save the notebook output, attach it to a new session and set "
                f"RAGMV_RESUME_FROM to its ragmv_tier2 folder to continue.")


if __name__ == "__main__":
    main(globals().get("__file__"))
