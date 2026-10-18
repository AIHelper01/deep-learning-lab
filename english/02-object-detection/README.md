# Object detection with YOLO26

Use **Ultralytics YOLO26n (`yolo26n.pt`)** in both English and Chinese lessons. The dataset is the official [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) YOLO26 export, with 3,939 training / 338 validation / 186 test images. Visually verified ID order: **0=paper, 1=rock, 2=scissors**.

1. [Computer vision overview](lessons/01-cv-overview.md)
2. [CNN foundations](lessons/02-cnn-basics.md)
3. [Detection and YOLO26](lessons/03-yolo-theory.md)
4. [Practical experiment checklist](lessons/04-yolo-practice.md)
5. [Rock Paper Scissors notebook](notebooks/01-yolo26-rock-paper-scissors.ipynb)

From the repository root, prepare the detection environment and import the provided archive once:

```powershell
uv sync --locked --default-index https://pypi.org/simple --project .\english\02-object-detection
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
.\start-notebooks.ps1 -Module detection
```

Existing destinations are rejected; no import is needed if the verified export already exists. Data is in `data/rock-paper-scissors-ishcs-v1/`. The importer preserves splits/annotations and records source, ZIP SHA-256, mapping, and counts. English outputs go in this module's outputs; Chinese outputs go in the root Chinese module. [Chinese lesson](../../02-object-detection/README.md) shares the locked detection environment and read-only dataset.

Classroom defaults are ten epochs at 320 pixels. Set `$env:COURSE_EPOCHS='1'` for one real full-dataset epoch with held-out evaluation. `COURSE_SMOKE=1` instead uses COCO8 and is not a gesture experiment. Record the actual run mode alongside metrics. GPU performance has not been validated.

[VOC / COCO / YOLO conversion and Xiaotudui Labs inspection](../../04-dataset-formats/README.md) form a separate topic. Training reads YOLO directly. See [dataset provenance](../docs/datasets.md#rock-paper-scissors-detection) and [execution evidence](../reports/README.md).

The historical mirror-trained [notebook](archive/01-yolo26-rps-legacy-executed.ipynb) is retained for comparison; its metrics do not describe the current dataset. Historical Chinese PaddleYOLO materials are preserved in the Chinese module.
