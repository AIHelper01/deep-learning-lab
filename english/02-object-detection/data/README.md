# Detection datasets

This module imports every dataset through a verified importer instead of a blind copy, so `provenance.json` records
source metadata, archive SHA-256, class names, and measured counts next to the data. Each dataset below lists the
**cp method** (stage an archive you already have in the DataSet folder, then import) and the **download method**
(where to get that archive). Data files stay out of Git; import once, because existing destinations are rejected.

[Dataset catalog](../../../docs/datasets.md#rock-paper-scissors) ·
[preparation guide](../../docs/datasets.md#rock-paper-scissors-detection) ·
separate [VOC / COCO / YOLO conversion and viewer topic](../dataset-formats/README.md).

## Rock Paper Scissors v1

Source: [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1),
CC BY 4.0. Both the English and the Chinese YOLO26n lesson read
`english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`; each language writes its own `outputs/`.

The official YOLO26 export has 3,939 / 338 / 186 training/validation/test images and 4,610 / 400 / 204 boxes.
Visually verified class order: **0=paper, 1=rock, 2=scissors** (English names only; ids, annotations and splits are
unchanged). Historic mirror and flat-VOC packages are excluded from default training.

### From DataSet staging (cp method)

```bash
# from the repository root; one archive per dataset in the staging folder
mkdir -p /workspace/DataSet/yolo
cp "/path/to/Rock-Paper-Scissors.v1i.yolo26.zip" /workspace/DataSet/yolo/
uv run python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

Windows PowerShell, after `uv sync` in the repository root:

```powershell
uv run python .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

An already unpacked official export can be copied anywhere and passed with `--export-dir <folder>`. A plain
`cp -R <unpacked export> english/02-object-detection/data/rock-paper-scissors-ishcs-v1/` also runs, but it skips the
`provenance.json` written by the importer, so prefer the importer.

### Download method

**In the browser.** Open
[dataset 1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) -> *Download Dataset* ->
format **YOLO26** -> *Download for computer vision*, then save the ZIP as
`/workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip` and continue with the cp step above.

**With an API key.** Exports belong to an account, so the web button needs a session, but the export REST endpoint
accepts a personal API key and the same ZIP then arrives over plain `curl`. Copy the key from Roboflow account
settings, keep it outside the repository, and never commit it:

```bash
umask 077 && printf '%s' 'YOUR_ROBOFLOW_API_KEY' > ~/.config/roboflow_api_key && chmod 600 ~/.config/roboflow_api_key

LINK=$(curl -sS -G "https://api.roboflow.com/melikeavan/rock-paper-scissors-ishcs/1/yolo26" \
  --data-urlencode "api_key=$(cat ~/.config/roboflow_api_key)" \
  --data-urlencode "nocache=true" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["export"]["link"])')
curl -sSL "$LINK" -o "/workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip"
```

The JSON reply carries `progress` (0-1) and `export.size` in MB; repeat the first request until `progress` reaches
`1`, then follow the link. The `roboflow` SDK call `project.version(1).export("yolo26")` hits the same endpoint.

## Vehicle counting v4 (traffic-flow lesson)

Source: [vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4),
CC BY 4.0. Both languages read `english/02-object-detection/data/vehicle-counting-tksu5-v4/` and run their own
notebook: English `english/02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb`, Chinese
`02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb`, each writing to its own `outputs/`.

The official YOLO26 export holds 6,565 images in 5 classes with the source splits kept: 4,708 / 1,661 / 196
images and 52,668 / 18,810 / 2,120 boxes. Class ids keep their original order with lower-cased names:
**0=truck, 1=bicycle, 2=bus, 3=car, 4=motorcycle** (the source listed `Truck` capitalized). Three label lines in the
source package were segmentation polygons; the importer rewrites them to their enclosing detection boxes and records
the count in `provenance.json`.

### From DataSet staging (cp method)

```bash
# from the repository root
mkdir -p /workspace/DataSet/yolo
cp "/path/to/vehicle counting.v4i.yolo26.zip" /workspace/DataSet/yolo/
uv run python english/scripts/import_vehicle_counting.py --from-staging
# or point at one archive explicitly
uv run python english/scripts/import_vehicle_counting.py --archive "/workspace/DataSet/yolo/vehicle counting.v4i.yolo26.zip"
```

Use `--staging <folder>` when the DataSet folder lives elsewhere. Windows PowerShell equivalent after
`uv sync` in the repository root:

```powershell
uv run python .\english\scripts\import_vehicle_counting.py --from-staging
```

The importer checks the embedded Roboflow project and version metadata, the counts, the names, and the archive
SHA-256, then writes `data/vehicle-counting-tksu5-v4/` plus `provenance.json`.

### Download method

**In the browser.** Open
[dataset 4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4) ->
*Download Dataset* -> format **YOLO26** -> *Download for computer vision*, then save the ZIP as
`/workspace/DataSet/yolo/vehicle counting.v4i.yolo26.zip`. The importer rejects archives whose embedded metadata
does not describe dataset 4.

**With an API key.** The export REST endpoint accepts a personal API key, so no browser session is needed. Store the
key as described in the Rock Paper Scissors section above and keep it out of the repository:

```bash
LINK=$(curl -sS -G "https://api.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/4/yolo26" \
  --data-urlencode "api_key=$(cat ~/.config/roboflow_api_key)" \
  --data-urlencode "nocache=true" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["export"]["link"])')
curl -sSL "$LINK" -o "/workspace/DataSet/yolo/vehicle counting.v4i.yolo26.zip"
```

Poll the first request until `progress` reaches `1` before following the link; the finished export reports
`export.size` 525.0 MB.

## COCO8 (smoke mode only)

`COURSE_SMOKE=1` uses Ultralytics' [COCO8](https://docs.ultralytics.com/datasets/detect/coco8/) sample so the
pipeline can be checked in seconds. Ultralytics downloads it into the module's data folder on first use; no staging
step is needed and never report its scores as lesson results.
