# Rock Paper Scissors v1 detection data

Source: [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1), CC BY 4.0.

Both English and Chinese YOLO26n lessons use `data/rock-paper-scissors-ishcs-v1/` in this module. The official YOLO26 export has 3,939/338/186 training/validation/test images and 4,610/400/204 boxes. Visually verified class order: **0=paper, 1=rock, 2=scissors**.

From the repository root:

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

Only import once; existing destinations are rejected. Original annotations and splits remain unchanged. `provenance.json` records source metadata, archive SHA-256, names and measured counts. Keep the exported attribution READMEs. Historic mirror/VOC data are excluded from default training.

See the [dataset catalog](../../../docs/datasets.md#rock-paper-scissors), [preparation guide](../../docs/datasets.md#rock-paper-scissors-detection), and separate [conversion/viewer topic](../../../04-dataset-formats/README.md). Data files stay out of Git.
