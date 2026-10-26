# Dependency sets

| File | For | Notes |
|---|---|---|
| `core.txt` | analyses, retrieval runs, figures, tables | the versions recorded in the run manifests |
| `test.txt` | the test suite | |
| `generation.txt` | answer generation (`ragmv.generate`) | `llama-cpp-python` is built from source |
| `dense.txt` | Study 1b dense retrieval and semantic chunkers | a GPU is needed in practice |

Supported interpreters: Python 3.12 and 3.13 (`numpy==2.5.3` and `scipy==1.18.1` need Python 3.12 or newer). The
stored results were produced with Python 3.13.16 (Study 1, `env/environment.json`) and 3.13.15 (Study 1b, Kaggle
manifests). The combined pin lists used at the time are kept in `env/historical/`; a complete lock of a tested
environment is in `env/validation/`.
