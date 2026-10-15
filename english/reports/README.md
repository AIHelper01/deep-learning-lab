# Local notebook execution

## Current uv run (2026-10-15)

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
Detection trains on the real Rock Paper Scissors export, but its saved notebook outputs come
from `COURSE_EPOCHS=1`, a one-epoch pipeline check, rather than the ten-epoch classroom run.
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

`01-image-classification/data/cifar10` still holds unreferenced CIFAR-10 download
fragments from an earlier fetch implementation: `cifar-10-python.tar.gz`,
`cifar-10-python.tar.part`, and `download-parts/` (41 files, 59.9 MB in total).
The delivered loader only reads the checksummed `train-00000-of-00001.parquet` and
`test-00000-of-00001.parquet` files with their provenance records, so deleting the
fragments is safe. Automated cleanup is blocked by the agent sandbox policy; remove
them from a terminal with:

```powershell
Remove-Item -LiteralPath english\01-image-classification\data\cifar10\cifar-10-python.tar.gz -Force
Remove-Item -LiteralPath english\01-image-classification\data\cifar10\cifar-10-python.tar.part -Force
Remove-Item -LiteralPath english\01-image-classification\data\cifar10\download-parts -Recurse -Force
```

The Rock Paper Scissors export under `02-object-detection/data` is complete and in use, and
`02-object-detection/data/rps-mirror` is the mirror cache that `scripts\fetch_rps.py` keeps so
re-runs only fetch missing files. Both stay out of Git through the existing `**/data/**` rule.
Three folders under `02-object-detection\outputs\runs` are leftovers from measuring the
classroom image size: `timing-probe` (a stopped 640-pixel run), `timing-probe-320`, and
`rps-yolo26n` (the ten-epoch run stopped on request). The delivered run is `rps-yolo26n-2`
plus the `evaluation` run. Delete the leftovers with:

```powershell
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\timing-probe -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\timing-probe-320 -Recurse -Force
Remove-Item -LiteralPath english\02-object-detection\outputs\runs\rps-yolo26n -Recurse -Force
```

## Earlier smoke checks

The `*-smoke.json`, `logs/`, and `windows-*-environment.txt` files are historical
small-sample checks using Python 3.12.11, PyTorch 2.8.0+cpu, and Paddle 3.2.2.
They are retained for troubleshooting and are superseded by the current uv execution
reports. The historical random-weight ResNet smoke score is not a transfer-learning result.
