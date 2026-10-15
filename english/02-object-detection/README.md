# Object detection with YOLO26

1. [Computer vision overview](lessons/01-cv-overview.md)
2. [CNN foundations](lessons/02-cnn-basics.md)
3. [Detection and YOLO26](lessons/03-yolo-theory.md)
4. [Practical experiment checklist](lessons/04-yolo-practice.md)
5. [Rock Paper Scissors notebook](notebooks/01-yolo26-rock-paper-scissors.ipynb)

Use Ultralytics YOLO26n (`yolo26n.pt`). The original PaddleYOLO course remains outside
english/. The new notebook covers training, held-out evaluation, and English predictions.

Classroom training is ten epochs at 320 pixels because one epoch measured about 205 seconds on
this CPU, against more than twenty minutes at 640 pixels. Set `$env:COURSE_EPOCHS='1'` before
starting the kernel for a short end-to-end check, and unset it for the full run. On a GPU,
raise `EPOCHS` and `IMGSZ` in the training cell.

Before the real experiment, build the bounding-box export:

```powershell
02-object-detection\.venv\Scripts\python.exe scripts\fetch_rps.py
```

Run it from the `english` directory. The [dataset guide](../docs/datasets.md) lists the
upstream Roboflow source and the credential-free CC BY 4.0 mirror the script uses, and
records how the held-out `test/` split is derived. No private Roboflow credentials are
embedded. Validation stops with an English explanation when labels or data are missing.

The COCO8 smoke check only verifies the software workflow; it does not replace hand-gesture
data or prove gesture-detection accuracy. [Official YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/).

