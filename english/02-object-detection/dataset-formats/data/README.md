# Conversion workspace (generated, never committed)

This folder holds only the outputs that `english/scripts/dataset_formats.py` writes:
`rps-voc-test/`, `rps-coco-test/`, `rps-yolo-from-voc/`, `rps-yolo-from-coco/`. They are regenerable teaching
artifacts, so nothing here is committed. Topic guide: [English](../README.md) ·
[Chinese topic guide](../../../../02-object-detection/dataset-formats/README.md); the Chinese copy of this note sits next to it.

## Input data is not stored here

Both conversion and the round-trip check read the YOLO export that lives in the detection module:
`english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`. Stage and import it once from the repository root.

**cp method** — copy the archive you already have into the DataSet staging folder, then import:

```bash
mkdir -p /workspace/DataSet/yolo
cp "/path/to/Rock-Paper-Scissors.v1i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

**Download method** — Roboflow needs a signed-in account, so `curl` cannot fetch it. Open
[Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) ->
*Download Dataset* -> format **YOLO26**, save the ZIP under `/workspace/DataSet/yolo/`, then continue with the cp
step above.

Full provenance, counts, class ids and the alternative `--export-dir` route live in the detection data guide:
[English](../../data/README.md) · [Chinese](../../../02-object-detection/data/README.md).
