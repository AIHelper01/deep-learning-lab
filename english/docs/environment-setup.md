# Environment setup

## Recommended: uv with Python 3.12

Historical image/NLP runs pin Python 3.12.15; the current shared English/Chinese
detection project pins locally available Python 3.12.12. PyTorch is 2.14.1, torchvision is
0.29.1, and PaddlePaddle is 3.3.1, the stable versions checked for this update.
The classroom runs every module in one interpreter, `~/env_dl_uv`, whose Jupyter kernel is
also named `env_dl_uv` (see
[One kernel for the whole course](../../docs/environment-setup.md#one-kernel-for-the-whole-course-macoslinux)).
Each module still keeps its own `pyproject.toml` and committed `uv.lock`, so an isolated
module `.venv` can be rebuilt with `uv sync --locked --project <module>` when preferred.

From the project root in PowerShell, start the default English image-classification course with:

```powershell
.\start-notebooks.ps1
```

Use `-Module pytorch`, `-Module paddle`, or `-Module detection` for the other modules.
The existing `english/start-notebooks.ps1` also defaults to `vision`.
For the separate Chinese course, see the [language-aware launcher guide](../../docs/environment-setup.md).
The launcher uses `uv` when available on PATH and otherwise uses `python -m uv`.
It explicitly selects the PyPI index recorded by the lockfile, avoiding a machine-specific
default mirror changing the locked resolution. Direct uv commands may also need
`--default-index https://pypi.org/simple` if your global default differs.
Before detection, import the official v1 YOLO26 archive as shown in the
[dataset guide](datasets.md#rock-paper-scissors-detection). The importer requires
`--archive` (or an unpacked `--export-dir`) and the verified class mapping.
The Chinese detection launcher uses this same locked environment with a separate
notebook/output directory. Set `COURSE_SMOKE=1` only for a deliberate COCO8 check.

From an individual module directory, the equivalent commands are:

```powershell
python -m uv sync --locked
python -m uv run --locked jupyter lab --notebook-dir notebooks
```

The notebooks now retain actual executed output, including embedded charts. The first
code cell identifies the environment and run mode. When running them again, use the
`env_dl_uv` kernel, or the rebuilt module kernel; selecting a different global kernel
bypasses the lockfile.
Model training selects CUDA first, then Apple Silicon MPS, then CPU; see
[device selection](../../docs/environment-setup.md#device-selection). All saved outputs in this
repository were produced with that selection on the machine named in each report.

The general pip instructions below remain an alternative; uv is the reproducible local
workflow used for the current validation.

Use Python 3.12. The validated `~/env_dl_uv` interpreter covers the image, PyTorch NLP,
Paddle NLP and detection tracks together; `paddlenlp` and `visualdl` are left out because
their pinned `protobuf` conflicts with `paddlepaddle==3.3.1`, and the lessons that needed
them are archived. The detection environment includes Ultralytics with YOLO26 support.

## Windows PowerShell

From a module directory containing requirements.txt:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m jupyterlab
```

## Linux or macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m jupyterlab
```

Open the notebook with the kernel from that environment. The first cell finds the English
course root, so opening notebooks at different depths does not change data paths. Course
data and caches remain inside english/. No AI Studio directory, Chinese font, Bash copy
command, Chinese tokenizer, or Chinese pretrained model is required.

The standard setup runs on CPU and on Apple Silicon MPS with the same pinned wheels, so no
extra framework build is needed there. NVIDIA CUDA training needs the matching CUDA build of
the framework for your platform, installed before the remaining dependencies. The course
does not change system Python, drivers, global locale, or your original course environments.
Use an English Jupyter/OS language setting if system-generated messages must also be English.

## Reproduction and determinism

Device selection is documented once, in the course-wide [environment guide](../../docs/environment-setup.md#device-selection): CUDA first, then MPS on
Apple silicon, then CPU, and Paddle lessons stay on CPU on macOS because the pinned wheel has no
MPS backend.

Ultralytics turns on warn-only determinism through
`torch.use_deterministic_algorithms(True, warn_only=True)` and keeps `seed=42`. On Apple Silicon
the autograd kernel `index_put_with_accumulate_mps` has no deterministic implementation, so that
warning repeats once per epoch and buries the training log; the detection notebooks silence it and
state the consequence instead - a rerun matches the recorded metrics in aggregate, not bit for bit.

## A short verification run

In PowerShell, set `$env:COURSE_SMOKE='1'` before starting Jupyter. In Bash, use
`export COURSE_SMOKE=1`. Restart the kernel after changing this environment variable.
Unset it for classroom experiments. Smoke mode reduces samples/epochs; ResNet uses random
weights and detection uses COCO8, so these checks do not demonstrate model quality.

The authoring script builds notebooks from templates and now refuses to overwrite executed
notebooks. Edit existing notebooks in place to preserve their results. Saved outputs are
from actual local execution, not copied historical results. See reports/ for validation scope.

