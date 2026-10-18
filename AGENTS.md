# Agent instructions

## Project direction

Deep Learning Lab is an English-first notebook teaching repository with a separate Chinese course. Read [README.md](README.md) and [HANDOFF.md](HANDOFF.md) before editing.

- Default documentation, English notebook explanations, labels, and launcher messages are English. Maintain Chinese entry points in `README.zh-CN.md`, `docs/*.zh-CN.md`, and the Chinese modules.
- English lessons remain in `english/`. Root-level `01-image-classification/`, `02-object-detection/`, and `03-sentiment-analysis/` are Chinese lessons. Keep paths stable unless a physical migration is requested.
- Language selection chooses an independent course; it does not translate notebooks or swap datasets in place. Preserve language-specific classification/NLP environments, data processing, vocabularies, and outputs. Current detection deliberately shares its locked environment and official v1 dataset, while outputs stay separate.

## Editing conventions

- Inspect `git status --short` first and preserve existing modified/untracked work.
- Prefer small changes using existing helpers and standard libraries. Avoid dependencies for documentation or simple launcher routing.
- Use relative links in repository documents. Commands must identify their working directory; PowerShell scripts should resolve paths from their script location.
- Synchronize English and Chinese entry-point guides when setup, language routing, or dataset contracts change.

## Launching and environments

From the repository root:

```powershell
.\start-notebooks.ps1                              # English vision
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Language zh-CN -Module vision
.\start-notebooks.ps1 -DryRun                       # No setup or server
```

The root launcher defaults to `en` / `vision`. English delegates to `english/start-notebooks.ps1`, which runs `uv sync --locked` and JupyterLab. Four English projects have independent lockfiles: vision, detection, PyTorch NLP, and Paddle NLP. Use the selected module's interpreter for runtime validation.

Chinese launching uses a pre-existing module `.venv/Scripts/python.exe`. Relative notebook paths depend on the working directory; extensions and archives need their own notebook directory. Current Chinese YOLO26 detection shares the English detection uv environment and official v1 dataset, with separate Chinese outputs; historical PaddleYOLO lessons remain for reference.

## Notebooks and evidence

- Preserve saved outputs and execution metadata. Authoring scripts `build_course.py` and `build_detection.py` are maintenance tools that can rewrite files; do not run them as routine setup.
- English shared data preparation is in `english/common/`; training and teaching code primarily lives in notebooks.
- Distinguish static checks, saved-output verification, smoke execution, classroom training, and GPU validation. Historical reports do not prove a new run.
- `COURSE_SMOKE=1` changes experiment scope: detection uses COCO8, and ResNet uses random weights. Do not present smoke accuracy as the default experiment's result.
- Do not remove historical Chinese errors to imply a fix; verify the underlying runtime before claiming success.

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
git diff --check
```

Launcher tests inspect routing without starting Jupyter. Python checks inspect sources and saved outputs without training/downloads; they rewrite their corresponding report JSON files. Use a module interpreter when dependencies are needed. Check local Markdown links/anchors after documentation edits. For documentation and launcher work, notebook diffs should remain empty unless intended.

Update `HANDOFF.md` with actual completed changes, checks, limitations, and commit status before handing off. Do not mark proposed work as complete.

## Dataset formats topic

`04-dataset-formats/` is a parallel teaching topic with English/Chinese guides, runnable YOLO/VOC/COCO box conversion, and Xiaotudui Labs viewer instructions. Keep conversion outside training notebooks. The tutorial VOC reader deliberately requires its declared zero-based continuous coordinate convention; do not imply arbitrary legacy VOC compatibility. Run `scripts/check_roundtrip.py` with the detection interpreter for all six directions and guard checks. Local generated conversion data stays ignored by Git.
