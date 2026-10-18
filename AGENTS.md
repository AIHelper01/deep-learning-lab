# Agent instructions

## Project direction

Deep Learning Lab is an English-first notebook teaching repository with a mirrored Chinese course. Read [README.md](README.md) and [HANDOFF.md](HANDOFF.md) before editing.

- All directory and file names are ASCII/English on both sides; only prose inside Chinese files is Chinese.
- English lessons are the masters and live in `english/`. Root-level `01-image-classification/`, `02-object-detection/`, and `03-sentiment-analysis/` are the Chinese lessons, matched one file per file (`scripts/check_parity.py` enforces this and reports exceptions with a documented reason).
- For the vision and NLP lessons the Chinese notebooks are generated mirrors of the English masters by `scripts/build_chinese_course.py`: identical cell structure and training logic, Chinese narration, Chinese console output, Chinese plot labels, and Chinese class/label names. Edit the English master, then regenerate; never hand-edit a mirrored Chinese notebook. Translation tables key on exact English text, so a master edit fails the build instead of leaving stale Chinese prose.
- The Chinese NLP route is genuinely Chinese data, not a translation of IMDb: it uses ChnSentiCorp hotel reviews with jieba segmentation through `common/sentiment_cn.py`, which keeps the same `load_reviews / tokenize / build_vocab / encode / LABELS` interface as `english/common/course_data.py`.
- Detection keeps hand-authored notebooks on both sides (Chinese lesson built first, English mirror by `english/scripts/build_vehicle_notebook.py`); `scripts/localize_chinese_detection.py` keeps the Chinese console text Chinese.
- Early Chinese notebooks that predate the rebuild live in each module's `archive/legacy-notebooks/`. They stay for history, are excluded from auditing, and are never executed. Keep history; move with `git mv` instead of deleting.

## Editing conventions

- Inspect `git status --short` first and preserve existing modified/untracked work.
- Prefer small changes using existing helpers and standard libraries. Avoid dependencies for documentation or simple launcher routing.
- Use relative links in repository documents. Commands must identify their working directory; PowerShell scripts should resolve paths from their script location.
- Synchronize English and Chinese entry-point guides when setup, language routing, or dataset contracts change.
- Never batch-replace text with a pattern that has a single-character alternative (for example `|\.`). Prove the edit is invertible first, print per-file hit counts, and require a round-trip assertion before writing.

## Launching and environments

From the repository root:

```powershell
.\start-notebooks.ps1                              # English vision
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Language zh-CN -Module vision
.\start-notebooks.ps1 -DryRun                       # No setup or server
```

The root launcher defaults to `en` / `vision`. English delegates to `english/start-notebooks.ps1`, which runs `uv sync --locked` and JupyterLab. Four English projects have independent lockfiles: vision, detection, PyTorch NLP, and Paddle NLP. Use the selected module's interpreter for runtime validation.

The Chinese tree locates its root through the `CHINESE_COURSE_ROOT` marker file at the repository root, and its `sys.path` combines the repository `common/` (Chinese helpers) with `english/common/` (shared loaders); model caches are shared with the English course. In the Chinese mirrored BOOT cell, `COURSE` is the repository root, so `DATA`/`OUTPUT` land inside the Chinese module tree.

On macOS/Linux, the single verified environment is `~/env_dl_uv` (uv-managed, Python 3.12, Jupyter kernel `env_dl_uv`). Execute notebooks with `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group <vision|pytorch|paddle|detection> [--language zh-CN]`; the runner injects the tagged runtime cell, keeps per-cell saved outputs, and writes reports under `english/reports/`.

## Notebooks and evidence

- Preserve saved outputs and execution metadata. Authoring scripts `build_course.py` and `build_detection.py` are maintenance tools that can rewrite files; do not run them as routine setup.
- English shared data preparation is in `english/common/`; training and teaching code primarily lives in notebooks.
- Distinguish static checks, saved-output verification, smoke execution, classroom training, and GPU validation. Historical reports do not prove a new run.
- `COURSE_SMOKE=1` changes experiment scope: detection uses COCO8, and ResNet uses random weights. Do not present smoke accuracy as the default experiment's result.
- Do not remove historical Chinese errors to imply a fix; verify the underlying runtime before claiming success.
- Device selection is always CUDA, then Apple Silicon MPS, then CPU, in that order; see [device selection](docs/environment-setup.md#device-selection). Keep `torch.device(...)` in PyTorch lessons, a plain `"cuda"/"mps"/"cpu"` string where Ultralytics consumes it, and pass the same value to `pipeline(..., device=DEVICE)`. Paddle keeps `gpu`/`cpu` only: the pinned `paddlepaddle==3.3.1` has no MPS backend. Reports must state the device that actually ran.

## Dataset documentation

The catalog is [docs/datasets.md](docs/datasets.md), with [Chinese counterpart](docs/datasets.zh-CN.md). Detailed English preparation is in [english/docs/datasets.md](english/docs/datasets.md). Keep the six module `data/README.md` files consistent.

Describe content/task, source links, download method, paths, splits/labels, transformations, and attribution/terms. Distinguish source totals from classroom subsets. Verify external facts when updating them; explicitly identify unknown counts or licenses.

The requested RPS source is [melikeavan / rock-paper-scissors-ishcs](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs). The supplied official YOLO26 v1 ZIP was verified by embedded metadata, counts, and SHA-256. Visually verified mapping is 0=paper, 1=rock, 2=scissors. `fetch_rps.py` imports official YOLO exports into `rock-paper-scissors-ishcs-v1` and rejects other sources; the prior mirror helper is `fetch_rps_legacy.py`. Keep old mirror metrics historical and never merge the superseded flattened VOC archive. Preserve annotation IDs.

Data, environments, caches, and trained artifacts stay out of Git. Retain provenance and attribution with local exports. A loader's software license does not establish a dataset license. The documented PaddleNLP ChnSentiCorp test distribution has no gold labels; do not compute accuracy against missing labels. LEDNUM has no verified public download in this repository.

## Verification and handoff

Run checks relevant to the change, from the repository root:

```powershell
pwsh -NoProfile -File tests/check-launcher.ps1
python english/scripts/check_course.py
python english/scripts/verify_saved_outputs.py
python scripts/check_parity.py      # Chinese/English pairing + output language
git diff --check
```

`english/scripts/check_course.py` rejects any CJK character inside `english/`, including notebook Markdown, so Chinese-only helpers and scripts must live outside that tree.

Launcher tests inspect routing without starting Jupyter. Python checks inspect sources and saved outputs without training/downloads; they rewrite their corresponding report JSON files. Use a module interpreter when dependencies are needed. Check local Markdown links/anchors after documentation edits. For documentation and launcher work, notebook diffs should remain empty unless intended.

Update `HANDOFF.md` with actual completed changes, checks, limitations, and commit status before handing off. Do not mark proposed work as complete.

## Dataset formats topic

`english/02-object-detection/dataset-formats/` and `02-object-detection/dataset-formats/` form one parallel teaching topic inside the detection module: the English guide is the source of truth, the Chinese guide mirrors it. It carries runnable YOLO/VOC/COCO box conversion and Xiaotudui Labs viewer instructions. Keep conversion outside training notebooks. The tutorial VOC reader deliberately requires its declared zero-based continuous coordinate convention; do not imply arbitrary legacy VOC compatibility. Run `english/scripts/check_dataset_formats.py` with the detection interpreter for all six directions and guard checks; it writes `english/reports/dataset-formats-validation.json`. Local generated conversion data stays ignored by Git.
