# Environment setup

English mirror · [中文课程环境（母本）](environment-setup.zh-CN.md)

The whole course is **one uv project: the repository root** (`pyproject.toml` + `uv.lock` + `.python-version`). `uv sync` once at the root installs every module on both language sides into one `.venv`; module directories no longer carry their own `pyproject.toml`, `uv.lock`, or `requirements.txt`. See the [full English environment guide](../english/docs/environment-setup.md) for versions, alternate platforms, and smoke mode.

From the repository root in PowerShell:

```powershell
.\start-notebooks.ps1                         # English / vision
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Module paddle
.\start-notebooks.ps1 -Module detection
```

The launcher runs `uv sync --locked` in the repository root, then `uv run jupyter lab --notebook-dir <module>/notebooks`. It falls back to `python -m uv` when uv is not on PATH. First setup requires network access if dependencies are not cached, and the JupyterLab server offers exactly the one root kernel.

To inspect the selection without installing packages or starting Jupyter:

```powershell
.\start-notebooks.ps1 -DryRun
.\start-notebooks.ps1 -Language zh-CN -Module pytorch -DryRun
```

Chinese notebooks need no separate environment on any platform: the single root environment described in [`One kernel for the whole course`](#one-kernel-for-the-whole-course) runs both languages. Sync the root project once (see the [Chinese setup guide](environment-setup.zh-CN.md)), then launch:

```powershell
.\start-notebooks.ps1 -Language zh-CN -Module vision
```

Notebooks locate the course root through the `CHINESE_COURSE_ROOT` and `english/COURSE_ROOT` marker files, so a kernel whose working directory is either the notebook directory or the repository root works. For extensions or archived notebooks, start Jupyter from that notebook's directory as described in the Chinese guide. Chinese YOLO26 detection uses the same pinned dependencies and the official RPS v1 dataset as the English lesson, and both languages run in the one root interpreter. Launch it with `.\start-notebooks.ps1 -Language zh-CN -Module detection`; outputs remain in the Chinese module.

The legacy `english/start-notebooks.ps1` remains available as a thin shim that forwards to the root launcher, and also defaults to image classification.

The [dataset-format topic](../english/02-object-detection/dataset-formats/README.md) reuses the root environment for its conversion scripts; training does not require conversion.

## One kernel for the whole course

The `.venv` created at the repository root is that single interpreter: after `uv sync` it covers
image classification, object detection (including the vehicle-counting notebook), the
dataset-format topic, the PyTorch NLP track, and the classical-ML Titanic lesson
`00-machine-learning/` (a CPU scikit-learn/XGBoost/LightGBM stack), for both language editions:

```bash
cd /path/to/deep-learning-lab
uv sync --locked
uv run jupyter lab --notebook-dir english/01-image-classification/notebooks
```

`uv run` starts JupyterLab with only this environment's own kernel. To select it from another
Jupyter installation, register it once:

```bash
uv run python -m ipykernel install --user --name deep-learning-lab --display-name deep-learning-lab
```

The uv project `~/env_dl_uv` outside the repository (kernel name `env_dl_uv`) is retired: it is
the interpreter that actually produced every saved `Expected output` block and run report now
committed here, on the same locked versions. Nothing executes there any more, and a new machine
does not need it.
English notebooks resolve `english/COURSE_ROOT` and Chinese notebooks resolve
`CHINESE_COURSE_ROOT` at the repository root, so opening the course from either directory works.

`paddlenlp` and `visualdl` are deliberately not in the root manifest or installed: they pin `protobuf 3.20.x`
and target Paddle 2.x, which conflicts with the pinned `paddlepaddle==3.3.1` used by the
validated runs. The current Chinese Paddle lessons (`03-sentiment-analysis/paddle/notebooks/`)
only need `paddlepaddle` plus `gensim` and run in this environment; the old `paddlenlp`/ERNIE
version is archived under `03-sentiment-analysis/paddle/archive/legacy-notebooks/`.

## Device selection

Every PyTorch lesson selects its accelerator the same way, in this order: CUDA, then Apple
Silicon MPS, then CPU.

```python
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
```

The two detection notebooks keep `DEVICE` as a plain string because Ultralytics takes the same
three names (`"cuda"`, `"mps"`, `"cpu"`) directly, and the pretrained-transformers cells pass the
same value to `pipeline(..., device=DEVICE)`. An Apple Silicon Mac therefore trains on MPS with no
code change, and every report still states which device actually ran. The Paddle lessons keep
`paddle.set_device("gpu" if paddle.is_compiled_with_cuda() else "cpu")` because the pinned
`paddlepaddle==3.3.1` wheel has no MPS backend (`paddle.set_device("mps")` raises), so Paddle
lessons run on CPU on macOS.

Ultralytics turns on warn-only determinism through
`torch.use_deterministic_algorithms(True, warn_only=True)` and keeps `seed=42`. On Apple Silicon
the autograd kernel `index_put_with_accumulate_mps` has no deterministic implementation, so that
warning repeats once per epoch and buries the training log; the detection notebooks silence it and
state the consequence instead - a rerun matches the recorded metrics in aggregate, not bit for bit.

## Running and checking lessons

| Purpose | Command (repository root) |
|---|---|
| Execute a notebook and keep real outputs | `uv run python english/scripts/execute_and_save.py --group vision\|pytorch\|paddle\|detection\|ml [--language zh-CN] [--notebook <name>] [--cwd root\|notebook\|module] [--include-legacy]` |
| Quote executed results back into the notebook (`Expected output` + `assets` figures) | `uv run python scripts/embed_expected_outputs.py [--module <module>] [--notebook <name>] [--include-archive] [--include-legacy]` |
| Derive the English mirror from a Chinese master | `uv run python scripts/build_english_course.py [--check] [--force]` |
| Regenerate the Chinese mirrors (vision/NLP, still English -> Chinese) | `uv run python scripts/build_chinese_course.py` |
| Keep the Chinese detection lesson's console text Chinese | `uv run python scripts/localize_chinese_detection.py` |
| Chinese/English pairing and output-language audit | `uv run python scripts/check_parity.py` |
| English course static checks (no CJK inside `english/`) | `uv run python english/scripts/check_course.py` |
| Repository-wide link, image-localisation and `assets` naming checks | `uv run python scripts/check_docs_assets.py` |
| Saved outputs still match their code | `uv run python english/scripts/verify_saved_outputs.py` |

`COURSE_SMOKE=1` swaps in a pipeline check (COCO8 for detection, random weights for ResNet) and
`COURSE_EPOCHS=<n>` shortens training; neither score describes model quality, and reports must
state the run configuration.

Course notebooks run with the repository root as the working directory (`--cwd root`, the default).
The Copy1 comparison notebook in `01-image-classification/archive/` follows the convention written
at the top of the file itself and is executed with `--cwd notebook`, so `../data` and `../outputs`
land in `01-image-classification/` while `assets/` stays inside `archive/`. Its `Expected output`
blocks need `--include-archive` to be refreshed. The pre-rebuild lessons in
`archive/legacy-notebooks/` stay out of default course runs and output verification; `--include-legacy`
re-executes them with the same `--cwd notebook` convention and embeds what the run produced, except for
cells tagged `skip-execution` because they need assets that were never part of the repository.
The `00-machine-learning` lesson lives in `<module>/notebooks/` but reads `titanic/` and writes
`models/` and `result/` from the module directory, so it runs with `--cwd module`. The lesson exists
on both sides and `--group ml` follows `--language`: `--language zh-CN --cwd module` executes the
Chinese master, omitting `--language` executes the English mirror under `english/`. After
`scripts/build_english_course.py --force` clears the mirror's outputs, refresh it in this order:
build, execute, embed.
