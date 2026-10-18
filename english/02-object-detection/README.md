# Object detection with YOLO26

[Chinese course](../../02-object-detection/README.md) · [Project](../README.md)

Both languages use **Ultralytics YOLO26n (`yolo26n.pt`)** on the official
[melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1)
YOLO26 export: 3,939 training / 338 validation / 186 test images. Visually verified id order:
**0=paper, 1=rock, 2=scissors**.

1. [Computer vision overview](lessons/01-cv-overview.md)
2. [CNN foundations](lessons/02-cnn-basics.md)
3. [Detection and YOLO26](lessons/03-yolo-theory.md)
4. [Practical experiment checklist](lessons/04-yolo-practice.md)
5. [Rock Paper Scissors notebook](notebooks/01-yolo26-rock-paper-scissors.ipynb)
6. [Vehicle counting notebook](notebooks/02-yolo26-vehicle-counting.ipynb)
7. [Vehicle counting run report](lessons/05-vehicle-counting-run-report.md) (every real output and figure)

## Run

The classroom machine uses the single environment outside the repository, `~/env_dl_uv` (Jupyter kernel
`env_dl_uv`), for both languages. Import the official archives once from the repository root; importers refuse to
overwrite an existing destination, and the verified export needs no second import (see
[data/README.md](data/README.md) for the cp and download methods of each dataset):

```bash
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
~/env_dl_uv/.venv/bin/python english/scripts/import_vehicle_counting.py --from-staging
```

Windows: `uv sync --locked --project english/02-object-detection`, then
`.\start-notebooks.ps1 -Module detection` and
`.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors`.

Data is read-only and shared: `data/rock-paper-scissors-ishcs-v1/` and `data/vehicle-counting-tksu5-v4/`. Each
language keeps its own runs: English in this module's `outputs/`, Chinese in
`../../02-object-detection/outputs/`. The importer preserves splits and annotations and records source, ZIP SHA-256,
class mapping and counts in `provenance.json`.

Classroom defaults are ten epochs at 320 pixels for the gesture experiment and five epochs at 320 pixels for vehicle
counting (its dataset is an order of magnitude larger). Set `COURSE_EPOCHS=1` for one real full-dataset epoch with
held-out evaluation; `COURSE_SMOKE=1` instead uses COCO8 and is neither a gesture nor a counting experiment. Record
the actual run mode alongside every metric. The saved runs come from an Apple Silicon Mac on MPS; NVIDIA CUDA
has not been validated. Ultralytics turns on warn-only determinism with `seed=42`, but the MPS autograd kernel
`index_put_with_accumulate_mps` has no deterministic implementation, so a rerun matches the recorded metrics in
aggregate rather than bit for bit.

Every code cell in both notebooks is followed by an *Expected output* cell: text is quoted verbatim and figures are
exported to `assets/` and linked with relative paths, so the recorded results stay readable after
*Kernel -> Clear All Outputs*, and a rerun should reproduce them. Refresh them from the repository root with
`~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 02-object-detection`.

## Vehicle counting notebook

[Vehicle counting notebook](notebooks/02-yolo26-vehicle-counting.ipynb) works on the
[vehicle-counting v4 dataset](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)
(CC BY 4.0, five vehicle classes) and goes from detection counting to traffic flow with tracking plus line crossings.
It reuses the locked detection dependency set (plus the `lapx` tracking dependency), stores data in
`data/vehicle-counting-tksu5-v4/`, and keeps its runs in this module's `outputs/`. The full executed evidence -
per-cell expected outputs, per-epoch validation metrics, test-split metrics and the tracking result - is written up in
the [vehicle counting run report](lessons/05-vehicle-counting-run-report.md). See
[dataset provenance](../docs/datasets.md#vehicle-counting-traffic-flow) for import, splits, and the three normalized
segmentation label lines. The mirrored Chinese notebook is
[here](../../02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb).

The default traffic clip is synthesized offline from real vehicle crops in the dataset, so every crossing has a known
answer; set `TRAFFIC_VIDEO=/path/to/your.mp4` to count a real video instead. The counting and line-crossing
implementation lives in [common/traffic_counting.py](../common/traffic_counting.py).

## Separate dataset topic and archived lessons

[VOC / COCO / YOLO conversion and Xiaotudui Labs inspection](dataset-formats/README.md) form a separate
topic; training reads YOLO directly. Sources, licences, hashes and splits live in the
[dataset guide](../docs/datasets.md), executed numbers in [reports/](../reports/README.md).

The historical mirror-trained [notebook](archive/01-yolo26-rps-legacy-executed.ipynb) is retained for comparison; its
metrics do not describe the current dataset. The superseded Chinese PaddleYOLO/YOLO11 lesson stays in place at
`../../../02-object-detection/notebooks/01-yolo11-rock-paper-scissors.ipynb` as read-only history (never executed, no
English twin), and its old lecture notes are archived under `archive/lessons/`; see
[archive/README.md](archive/README.md).
