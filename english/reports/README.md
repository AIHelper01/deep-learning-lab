# Execution evidence

## Current official RPS v1 runs (2026-10-18)

Both English and Chinese YOLO26n notebooks completed actual one-epoch CPU training
on all 3,939 source training images, followed by the independent 186-image test split.
Both reached **test mAP50 0.7266 and mAP50-95 0.4535** with seed 42.
English execution took **683.77 seconds** end to end; Chinese took **634.85 seconds**.
The measured training epoch times were 585.296 and 590.004 seconds respectively.
This is `COURSE_EPOCHS=1`, not COCO8 smoke mode and not the default ten-epoch lesson.
GPU was unavailable and has not been verified.

- [Run summary and checkpoint paths](rps-v1-run-summary.json).
- [English execution](detection-executed.json) and [Chinese execution](detection-zh-CN-executed.json).
- [Source verification](rps-v1-data-checks.json), [class review](rps-v1-class-id-review.png),
  [runtime environment](rps-v1-environment.json), and [installed packages](uv-detection-v1-environment.txt).
- Each notebook retains four figures: epoch metrics, test confusion matrix, test predictions,
  and a single-image prediction. A one-epoch plot contains one point per series, not an
  established learning trend; individual images can still have missed detections.
- [Format conversion validation](../../04-dataset-formats/reports/validation.json): 186 images,
  204 boxes, exact image-byte preservation and box round trips within 0.001 pixel tolerance.

The previous mirror execution report is `detection-legacy-executed.json` and its original
notebook is in `02-object-detection/archive/`. Historical 0.904/0.524 metrics below must
not be attributed to official v1. Current Chinese detection is YOLO26n; the old external
PaddleYOLO materials remain for historical comparison.

# Local notebook execution

## Historical uv run (2026-10-15)

The English notebooks are executed through real Jupyter kernels on this Windows PC.
Outputs are saved directly into each `.ipynb`, including logs, metrics, predictions,
and embedded PNG charts. Open the notebooks to inspect the actual results.

- Python 3.12.15, managed by uv 0.13.1.
- PyTorch 2.14.1 and torchvision 0.29.1.
- PaddlePaddle 3.3.1.
- Ultralytics 8.4.177 with YOLO26.
- Four separate module environments, each with its own `uv.lock`.

Image classification and NLP use the default classroom parameters, not smoke mode.
This means 3 epochs for classification and 5 for LSTM, using the documented course
subsets rather than the entire source datasets. ResNet uses pretrained ImageNet weights.
The optional DistilBERT notebook uses the downloaded English sentiment model.
Detection runs the same way on the real Rock Paper Scissors export: ten epochs at 320 pixels,
2127 CPU seconds, test mAP50 0.904, and mAP50-95 0.524. The rerun reproduced the same metrics,
which is the expected result under `seed=42` and `deterministic=True`. Set `COURSE_EPOCHS=1` to
repeat the same path as a short check.
These are CPU teaching runs, not GPU benchmarks or accuracy guarantees.

## Evidence

- `*-executed.json`: per-notebook status, elapsed time, output counts, and environment.
- `saved-output-checks.json`: every nonempty code cell executed, no saved errors,
  and embedded image counts.
- `uv-*-environment.txt`: actual installed packages for all four environments.
- `static-checks.json`: notebook syntax/schema, English-language scan, and local links.
- `original-course-integrity.json`: hash comparison of all 93 original course files.

Launch Jupyter using `english/start-notebooks.ps1` from the project root; see
[environment setup](../docs/environment-setup.md). The execution script is
`english/scripts/execute_and_save.py`; run it with the corresponding module's uv
Python and `--group vision`, `pytorch`, `paddle`, or `detection`. Use `--resume` to
skip previously successful notebooks in that group's report. The authoring scripts
refuse to overwrite notebooks containing saved execution.

## Leftover downloads

`01-image-classification/data/cifar10` still holds unreferenced CIFAR-10 download fragments
from an earlier fetch implementation: `cifar-10-python.tar.gz`, `cifar-10-python.tar.part`, and
`download-parts/` (41 files, 59.9 MB in total). The delivered loader only reads the checksummed
`train-00000-of-00001.parquet` and `test-00000-of-00001.parquet` files with their provenance
records, so deleting the fragments is safe.

```powershell
Remove-Item -LiteralPath english\01-image-classification\data\cifar10\cifar-10-python.tar.gz -Force
Remove-Item -LiteralPath english\01-image-classification\data\cifar10\cifar-10-python.tar.part -Force
Remove-Item -LiteralPath english\01-image-classification\data\cifar10\download-parts -Recurse -Force
```

The Rock Paper Scissors export under `02-object-detection/data` is complete and in use, and
`02-object-detection/data/rps-mirror` is the mirror cache that `scripts\fetch_rps.py` keeps so
re-runs only fetch missing files. Both stay out of Git through the existing `**/data/**` rule.

`02-object-detection\outputs\runs` keeps one delivered run, `rps-yolo26n-5` with its
`evaluation-8` folder, and the notebook renders the training curves, the normalized confusion
matrix, and a validation prediction crop from those folders. Ultralytics progress-bar redraws
are suppressed, so the saved notebook holds 13 output records rather than two thousand. Every
other folder there is superseded: the timing probes, the stopped and one-epoch attempts, and the
historical COCO8 smoke runs with their evaluation folders. None of it is tracked by Git. Delete
the superseded folders with:

```powershell
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\coco8-smoke -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\coco8-smoke-2 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\coco8-smoke-3 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\coco8-smoke-4 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation-2 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation-3 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation-4 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation-5 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation-6 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\evaluation-7 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\progress-probe -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\rps-yolo26n -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\rps-yolo26n-2 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\rps-yolo26n-3 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\rps-yolo26n-4 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\timing-probe -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\timing-probe-320 -Recurse -Force
```

## Earlier smoke checks

The `*-smoke.json`, `logs/`, and `windows-*-environment.txt` files are historical
small-sample checks using Python 3.12.11, PyTorch 2.8.0+cpu, and Paddle 3.2.2.
They are retained for troubleshooting and are superseded by the current uv execution
reports. The historical random-weight ResNet smoke score is not a transfer-learning result.
