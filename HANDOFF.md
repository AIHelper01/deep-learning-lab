# Project handoff

Updated: 2026-10-18 (Asia/Shanghai). The session changes are committed on main and pushed to origin.

## Current user direction

The project is English-first with Chinese compatibility. The user supplied the official `Rock-Paper-Scissors.v1i.yolo26.zip` and selected **YOLO26n** for both language lessons. The user explicitly stopped the earlier flattened VOC package workflow. Dataset conversion and Xiaotudui Labs viewer instructions must be a **separate parallel topic**, not part of model-training notebooks.

## Delivered structure

- `README.md` and root docs are English defaults, with `README.zh-CN.md` and `docs/*.zh-CN.md` counterparts.
- Root `start-notebooks.ps1` defaults to English vision. Current Chinese detection routes through the shared English detection uv environment; other Chinese routes retain their existing module environments.
- English detection notebook: `english/02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb`.
- New Chinese detection notebook: `02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb`.
- Both use Ultralytics YOLO26n, official v1 data, and separate outputs. Chinese YOLO theory/practice lessons are updated; previous lessons are preserved in `02-object-detection/archive/lessons/`. The old PaddleYOLO notebook remains historical.
- `04-dataset-formats/` is the parallel English/Chinese format topic. Its scripts convert bounding-box YOLO/VOC/COCO datasets and check all six directions. VOC import requires the tutorial's explicit zero-based continuous-coordinate convention; this is not an arbitrary legacy VOC importer.
- Dataset catalogs and six module data READMEs describe content, source, preparation, labels/splits, paths, transformations, and attribution.

## Official dataset verification

Reference: [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1).

- Input ZIP: `C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip`.
- SHA-256: `2cf65dffbaa92483bbf99e7903f7c23c934ccf57d1cb097a66b7d38eadac0e59`.
- Embedded workspace/project/version metadata and CC BY 4.0 notices match the requested source.
- Source splits retained: training 3,939 images / 4,610 boxes; validation 338 / 400; test 186 / 204.
- Original names are numeric; labeled crop review confirms 0=paper, 1=rock, 2=scissors. IDs are preserved while names become English.
- No invalid boxes or cross-split exact duplicate image bytes found. Near-duplicate/video/participant leakage in upstream splits is not ruled out.
- Active data: `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`; `provenance.json` records the import. Both languages share this data read-only; model outputs are separate.
- `fetch_rps.py` imports official YOLO exports and refuses overwrite/merge. `fetch_rps_legacy.py` is historical mirror reproduction only.
- Data-check evidence: `english/reports/rps-v1-data-checks.json` and `rps-v1-class-id-review.png`.

The superseded desktop `Rock-Paper-Scissors.zip` was VOC with 6,455 images and no project/version metadata. Its conversion finished before the stop message; **no training was started on it**. Its ignored output remains in `english/02-object-detection/data/rock-paper-scissors-ishcs/`, and is not read by the current course. Do not relabel it as v1 or delete local data without purpose. Historical Xuban results are retained in the archived English notebook and `detection-legacy-executed.json`.

## Environment and checks

The detection environment was actually installed using Python **3.12.12**, PyTorch **2.14.1+cpu**, Ultralytics **8.4.177**. Python 3.12.15 was unavailable locally; detection `.python-version` was updated while the original dependency lockfile was preserved. The launcher explicitly selects the lockfile's PyPI index to avoid rewriting it for a machine-specific mirror. `uv sync --locked --default-index https://pypi.org/simple --dry-run` passes for this module. Other module pins were preserved. No CUDA device was available.

Passed:

- `pwsh -NoProfile -File tests/check-launcher.ps1`: all language/module routes, shared Chinese detection environment, defaults, and invocation outside the repository.
- Detection interpreter + `tests/check-rps-import.py`: source rejection, explicit class mapping, ID/source preservation, split paths, overwrite guard, and invalid-box rejection.
- `04-dataset-formats/scripts/check_roundtrip.py`: all six format directions on fixtures, including empty images, full-image boxes, nested paths, and guards.
- Real test-split conversion: all 186 images / 204 boxes match after YOLO→VOC→YOLO and YOLO→COCO→YOLO; hashes, labels, splits and coordinates checked within 0.001 pixel tolerance. Evidence: `04-dataset-formats/reports/validation.json`.
- Final documentation check passed: 23 documents, 140 local links/anchors; both current detection notebooks completed without saved errors.
- Final static check passed: 75 English source files, 14 notebooks including the historical detection archive, zero problems. Saved-output check passed for 13 English course notebooks plus the new Chinese detection notebook, 14 total. Jupyter checkpoint copies are excluded from validation and execution discovery.

Xiaotudui Labs' YOLO/VOC/COCO viewer pages were inspected in-browser. Guides document actual image/annotation selectors, start/reset/zoom controls, and COCO image-ID search. The YOLO page mentions classes.txt but exposed no independent class-upload control. **Website file imports were not performed**, so do not claim visual validation inside the website; format correctness was checked locally.

## Completed execution

Both current YOLO26 notebooks **completed successfully**: one actual full-dataset epoch,
320 pixels, batch 8, CPU, then independent test evaluation/prediction. This is
`COURSE_EPOCHS=1`, not smoke mode and not the default ten-epoch lesson result.

| Language | End-to-end seconds | Test mAP50 | Test mAP50-95 |
|---|---:|---:|---:|
| English | 683.77 | 0.7266251003 | 0.4535422539 |
| Chinese | 634.85 | 0.7266251003 | 0.4535422539 |

Each notebook retains four embedded figures and completed execution metadata.
The one-epoch plot has only one point per series; this does not establish a training trend.
The single-image sample can still have missed detections. Checkpoints, exact source,
class order, split sizes, scope and report paths are in `english/reports/rps-v1-run-summary.json`.
English and Chinese training were independent runs; shared seed/settings reproduced the metrics.

Execution commands from the root (detection interpreter):

```powershell
$env:COURSE_EPOCHS='1'
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\execute_and_save.py --group detection
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\execute_and_save.py --group detection --language zh-CN
```

Reports are `english/reports/detection-executed.json` and `detection-zh-CN-executed.json`; raw metrics/checkpoints are under each language's detection outputs. Both execution processes finished. No training is left running from this task. Repeat runs create new run directories; do not overwrite historical artifacts. Resume checks now distinguish requested run mode, so a one-epoch report cannot satisfy a default ten-epoch run.

## Full English course run with default classroom parameters

On 2026-10-18 all four English groups were executed end-to-end in a real environment with default classroom parameters (COURSE_SMOKE=0, no COURSE_EPOCHS) on a CPU-only i7-11700 (8c/16t, 32 GB). All 13 English notebooks passed; every notebook file retains its saved outputs and completion metadata, and per-run rows are in english/reports/vision-executed.json, detection-executed.json, pytorch-executed.json, and paddle-executed.json.

- Vision, PyTorch NLP, and Paddle NLP environments were rebuilt with uv sync --locked --default-index https://pypi.org/simple --python 3.12.12 because CPython 3.12.15 has no local install and no uv download on this machine. .python-version files and all lockfiles are unchanged; runtime is Python 3.12.12 with torch 2.14.1, ultralytics 8.4.177, and paddlepaddle 3.3.1, satisfying the notebook kernel asserts.
- Saved headline metrics: LeNet-MNIST test accuracy 0.894; LeNet-CIFAR10 0.383; ResNet-CIFAR10 0.817; PyTorch LSTM sentiment test accuracy 0.736; Paddle LSTM sentiment test accuracy 0.817; YOLO26n ten real epochs on the official v1 dataset (320 px, batch 8) reached test mAP50 0.9494 and mAP50-95 0.7670, trained in 4,126 s (run directory english/02-object-detection/outputs/runs/rps-ishcs-v1-yolo26n-2).
- These default-parameter results supersede the one-epoch pipeline-check metrics in the table above for classroom presentation; the one-epoch report remains historical evidence and its run directory is unchanged.
- Post-run checks passed from the repository root: python english/scripts/verify_saved_outputs.py (zero problems), python english/scripts/check_course.py (75 source files, 14 notebooks, zero problems), and git diff --check.

## Other limitations and git state

Chinese classification/NLP runtime validation remains incomplete; a historical Chinese Paddle LSTM error is not fixed. Other English Paddle notebooks were already modified when this detection task began; preserve those changes and do not reset them. Do not broadly regenerate notebooks.

`docs/migration/` and original integrity reports describe past snapshots. Changed documentation means those reports do not validate the current tree. Historical cleanup suggestions were not executed.

Commits before this session ended at `4c39b08`. The full default-parameter English course run and all session documentation changes were committed on `main` and pushed to `origin` in the closing commit of the 2026-10-18 session. Inspect `git log` and `git status --short` before continuing.

中文交接：当前正式包已核实，YOLO26n 与数据在中英文课程统一；旧 VOC 包已停用且未训练。格式转换与小土堆查看说明在独立 04 专题。两版 Notebook 已分别完成全部正式数据一轮 CPU 实跑，测试 mAP50=0.7266、mAP50-95=0.4535，不能沿用旧镜像指标，也不能当成默认十轮结果。本次改动已提交到 main 并推送到 origin。
