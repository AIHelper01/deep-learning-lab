# Environment setup

## Recommended: uv with Python 3.12

The locally validated projects pin Python 3.12.15. PyTorch is 2.14.1, torchvision is
0.29.1, and PaddlePaddle is 3.3.1, the stable versions checked for this update.
Each module has its own `.venv` and generated `uv.lock`.

From the project root in PowerShell, start the Paddle notebooks with:

```powershell
.\english\start-notebooks.ps1 -Module paddle
```

Use `-Module pytorch`, `-Module vision`, or `-Module detection` for the other modules.
The launcher uses `uv` when available on PATH and otherwise uses `python -m uv`.
Before the detection class, prepare the hand-gesture data with
`02-object-detection\.venv\Scripts\python.exe scripts\fetch_rps.py` from this directory;
see the [dataset guide](datasets.md). Detection then runs the real experiment like the other
modules, so set `COURSE_SMOKE=1` only for a deliberate COCO8 pipeline check.

From an individual module directory, the equivalent commands are:

```powershell
python -m uv sync --locked
python -m uv run --locked jupyter lab --notebook-dir notebooks
```

The notebooks now retain actual executed output, including embedded charts. The first
code cell identifies the environment and run mode. When running them again, use the
module's Python 3.12 kernel; selecting a different global kernel bypasses the lockfile.
Model training uses CPU when no supported GPU is available.

The general pip instructions below remain an alternative; uv is the reproducible local
workflow used for the current validation.

Use Python 3.12 and independent virtual environments. The PyTorch image and NLP modules
can share an environment when their dependency versions agree. Keep Paddle separate.
The detection environment includes Ultralytics with YOLO26 support.

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

The standard setup starts with CPU-compatible code. For GPU training, install the matching
framework build for your platform before installing the remaining dependencies. The course
does not change system Python, drivers, global locale, or your original course environments.
Use an English Jupyter/OS language setting if system-generated messages must also be English.

## A short verification run

In PowerShell, set `$env:COURSE_SMOKE='1'` before starting Jupyter. In Bash, use
`export COURSE_SMOKE=1`. Restart the kernel after changing this environment variable.
Unset it for classroom experiments. Smoke mode reduces samples/epochs; ResNet uses random
weights and detection uses COCO8, so these checks do not demonstrate model quality.

The authoring script builds notebooks from templates and now refuses to overwrite executed
notebooks. Edit existing notebooks in place to preserve their results. Saved outputs are
from actual local execution, not copied historical results. See reports/ for validation scope.

