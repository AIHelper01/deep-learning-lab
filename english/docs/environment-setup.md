# Environment setup

## Recommended: uv with Python 3.12

The repository root is the course's only uv project: `pyproject.toml` declares the
dependencies, `uv.lock` pins them, and `.python-version` asks for CPython 3.12. One
`uv sync` at the root installs every module on both language sides into the root `.venv`;
module directories no longer carry a `pyproject.toml`, `uv.lock`, or `requirements.txt`.
The lock pins Python 3.12, PyTorch 2.14.1, torchvision 0.29.1, PaddlePaddle 3.3.1, and
Ultralytics 8.4.177, the versions used for the current validation, and records macOS
arm64, manylinux x86_64, and Windows amd64 wheels (see
[One kernel for the whole course](../../docs/environment-setup.md#one-kernel-for-the-whole-course)).
There is no second environment: `~/env_dl_uv` and its `env_dl_uv` kernel are retired and
kept only as provenance, because they produced the saved outputs committed here, on the
same locked versions.

From the project root in PowerShell, start the English image-classification course with:

```powershell
.\start-notebooks.ps1 -Language en -Module vision
```

Use `-Module pytorch`, `-Module paddle`, or `-Module detection` for the other modules.
The root launcher itself defaults to the Chinese masters (`-Language zh-CN -Module vision`),
because the Chinese lessons at the repository root are the masters. The legacy
`english/start-notebooks.ps1` is now a shim that forwards here and keeps the `en` default
with `vision`.
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

The equivalent manual commands, from the repository root:

```powershell
uv sync --locked
uv run jupyter lab --notebook-dir english/01-image-classification/notebooks
```

`uv run` walks up to the root `pyproject.toml`, so `uv run python …` also works from inside a
module directory without `--project`.

The notebooks now retain actual executed output, including embedded charts. The first
code cell identifies the environment and run mode. When running them again, use the
kernel from the root `.venv`; any other kernel, including the retired `env_dl_uv` classroom
kernel, bypasses the lockfile.
Model training selects CUDA first, then Apple Silicon MPS, then CPU; see
[device selection](../../docs/environment-setup.md#device-selection). All saved outputs in this
repository were produced with that selection on the machine named in each report.

The general pip instructions below remain an alternative; uv is the reproducible local
workflow used for the current validation.

Use Python 3.12. The root lock covers the image, PyTorch NLP, Paddle NLP and detection
tracks together; `paddlenlp` and `visualdl` are left out because
their pinned `protobuf` conflicts with `paddlepaddle==3.3.1`, and the lessons that needed
them are archived. The detection environment includes Ultralytics with YOLO26 support.

## Without uv

uv is the supported path because `uv.lock` is what makes the course reproducible. On a machine
that cannot run uv, export the lock once from any machine that can, then install it with pip:

```bash
uv export --locked --no-hashes --no-emit-project -o requirements-root.txt
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-root.txt
.venv/bin/python -m jupyterlab
```

Build one environment for the whole course this way, not one per module: the root lock is a
single coherent resolution, and the exported file keeps the per-platform markers.

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

