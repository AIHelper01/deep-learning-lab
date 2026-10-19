# Environment setup

English (default) · [中文课程环境](environment-setup.zh-CN.md)

The default English course has four independent uv projects with committed lockfiles. See the [full English environment guide](../english/docs/environment-setup.md) for versions, alternate platforms, and smoke mode.

From the repository root in PowerShell:

```powershell
.\start-notebooks.ps1                         # English / vision
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Module paddle
.\start-notebooks.ps1 -Module detection
```

The launcher runs `uv sync --locked` and opens JupyterLab in the selected English module. It falls back to `python -m uv` when uv is not on PATH. First setup requires network access if dependencies are not cached. Select the module's Python kernel.

To inspect the selection without installing packages or starting Jupyter:

```powershell
.\start-notebooks.ps1 -DryRun
.\start-notebooks.ps1 -Language zh-CN -Module pytorch -DryRun
```

Chinese notebooks need no separate environment on macOS/Linux: the single [`env_dl_uv`](#one-kernel-for-the-whole-course-macoslinux) kernel below runs both languages. On Windows, recreate the pinned module environment first (see the [Chinese setup guide](environment-setup.zh-CN.md)), then launch:

```powershell
.\start-notebooks.ps1 -Language zh-CN -Module vision
```

Chinese sessions start from the notebook directory because their relative data paths require it. For extensions or archived notebooks, start Jupyter from that notebook's directory as described in the Chinese guide. Chinese YOLO26 detection uses the same pinned dependencies and the official RPS v1 dataset as the English lesson; on the classroom machine both languages run in the one `env_dl_uv` interpreter. Launch it on Windows with `.\start-notebooks.ps1 -Language zh-CN -Module detection`; outputs remain in the Chinese module. Other Chinese dependencies retain their original validation limitations.

The existing `english/start-notebooks.ps1` remains available and now also defaults to image classification.

The [dataset-format topic](../english/02-object-detection/dataset-formats/README.md) reuses this detection environment for its conversion scripts; training does not require conversion.

## One kernel for the whole course (macOS/Linux)

`~/env_dl_uv` is a single uv project outside the repository that merges the four module
lockfiles into one interpreter, so a local machine only needs one Jupyter kernel named
`env_dl_uv`. It covers image classification, object detection (including the
vehicle-counting notebook), the dataset-format topic, and the PyTorch NLP track:

```bash
cd ~/env_dl_uv
uv sync
.venv/bin/python -m ipykernel install --user --name env_dl_uv --display-name env_dl_uv
uv run --no-sync jupyter lab /path/to/deep-learning-lab
```

Then pick **env_dl_uv** in JupyterLab (Notebook → Change Kernel). The same interpreter also
registers an equivalent `python3` kernel, which is what the command-line runner uses. English
notebooks resolve `english/COURSE_ROOT` and Chinese notebooks resolve `CHINESE_COURSE_ROOT` at
the repository root, so opening the course from either directory works.

`paddlenlp` and `visualdl` are deliberately not installed there: they pin `protobuf 3.20.x`
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
| Execute a notebook and keep real outputs | `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision\|pytorch\|paddle\|detection [--language zh-CN] [--notebook <name>] [--cwd root\|notebook] [--include-legacy]` |
| Quote executed results back into the notebook (`Expected output` + `assets` figures) | `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py [--module <module>] [--notebook <name>] [--include-archive] [--include-legacy]` |
| Regenerate the Chinese mirrors from the English masters | `~/env_dl_uv/.venv/bin/python scripts/build_chinese_course.py` |
| Keep the Chinese detection lesson's console text Chinese | `~/env_dl_uv/.venv/bin/python scripts/localize_chinese_detection.py` |
| Chinese/English pairing and output-language audit | `~/env_dl_uv/.venv/bin/python scripts/check_parity.py` |
| English course static checks (no CJK inside `english/`) | `~/env_dl_uv/.venv/bin/python english/scripts/check_course.py` |
| Repository-wide link, image-localisation and `assets` naming checks | `~/env_dl_uv/.venv/bin/python scripts/check_docs_assets.py` |
| Saved outputs still match their code | `~/env_dl_uv/.venv/bin/python english/scripts/verify_saved_outputs.py` |

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
