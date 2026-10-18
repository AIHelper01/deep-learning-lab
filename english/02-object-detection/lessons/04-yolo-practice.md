# YOLO26 in practice: rock-paper-scissors

Prepare the detection environment and the official v1 export from the repository root as described in the
[module guide](../README.md), then open the [YOLO26 notebook](../notebooks/01-yolo26-rock-paper-scissors.ipynb). This
practice uses Ultralytics; it is independent of the historical external PaddleYOLO workflow.

## Steps

1. Confirm the source is melikeavan / rock-paper-scissors-ishcs v1 with the original 3,939 training, 338 validation and
   186 test images, and confirm the class order against the dataset's `provenance.json`.
2. Run the paths-and-environment cell, which uses the same detection environment as the Chinese edition. Both languages
   read the shared read-only export; each writes its own outputs.
3. Run the data validation cell. Missing labels, a wrong source, illegal coordinates and byte-identical images that
   appear in two splits all raise an error - fix the data instead of switching the checks off.
4. Load `yolo26n.pt` and use the epochs/imgsz/batch settings in the training cell. The classroom defaults are 320 pixels
   for ten epochs; for a quick full-data pass set `COURSE_EPOCHS=1`, which still uses every training image.
5. Read the real training curves and the best checkpoint. Compute mAP50 and mAP50-95 on the independent test split, then
   look at the confusion matrix and the boxed predictions.
6. Record the failure cases, the confidence threshold, the device, the elapsed time and the framework versions, and keep
   metrics from different epoch counts or data sources apart.

`COURSE_SMOKE=1` switches to COCO8, which can prove the pipeline works but cannot prove hand-gesture accuracy. The
pretrained weights need network access on first download. On Windows the notebook uses `workers=0` to avoid
multiprocessing problems.

Changing the confidence threshold trades precision against recall; a larger image size can help small objects at more
compute cost; more epochs can overfit; and a detector trained on clean single-hand photos can struggle with several
hands, occlusion and new backgrounds.

VOC, COCO and YOLO conversion and the [Xiaotudui Labs](https://xiaotudui.com/labs) notes live in a
[separate topic](../dataset-formats/README.md); they are not a prerequisite conversion step for this experiment.

**Discussion:** how would you build a fair test set for a new instructor, camera and room?

The historical leaf-disease practice is kept in the Chinese course
[archive](../../../02-object-detection/archive/lessons/04-yolo-practice.md); its old paths, data and model differ
from this experiment.
