# Detection dataset formats: YOLO, VOC, and COCO

English (default) · [中文专题](README.zh-CN.md) · [Project](../README.md)

This topic is independent of model training. Use one dataset to learn how annotations represent the same boxes, convert them without changing class meaning or splits, and visually inspect the result.

## Example dataset and setup

Reference: [Rock-Paper-Scissors versions](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset), specifically [v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1), licensed CC BY 4.0. The supplied `Rock-Paper-Scissors.v1i.yolo26.zip` embeds the matching workspace, project, and version. It contains 3,939 training, 338 validation, and 186 test images, with auto-orientation and 640×640 stretch preprocessing and no export augmentation.

Labeled crops were visually reviewed: original ID **0=paper, 1=rock, 2=scissors**. The original numeric names are mapped at their existing IDs; annotation IDs are not reordered. Keep the exported README attribution. The older flattened 6,455-image VOC archive is not this version and is excluded from the current course.

From the repository root, use the detection environment described in [setup](../docs/environment-setup.md):

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

The prepared source is `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`. The importer refuses to overwrite or merge an existing destination; an already prepared, validated export does not need importing again. Source ZIP SHA-256 is recorded in `provenance.json`.

## The same box in three formats

For a 640×640 image, a box with left=160, top=128, right=480, bottom=512 is:

| Format | Representation | Example |
|---|---|---|
| YOLO detection TXT | Zero-based class ID; normalized center x/y and width/height | `0 0.5 0.5 0.5 0.6` |
| VOC XML | Class name and pixel corners xmin/ymin/xmax/ymax | `paper`, `160, 128, 480, 512` under this topic's continuous-coordinate convention |
| COCO JSON | Category/image IDs and pixel x/y/width/height | `category_id=1`, `bbox=[160,128,320,384]`, `area=122880` |

For image width W and height H:

```text
YOLO -> corners:
xmin = (xc - w/2) * W       xmax = (xc + w/2) * W
ymin = (yc - h/2) * H       ymax = (yc + h/2) * H
corners -> COCO: [xmin, ymin, xmax-xmin, ymax-ymin]
corners -> YOLO: [(xmin+xmax)/(2W), (ymin+ymax)/(2H), (xmax-xmin)/W, (ymax-ymin)/H]
```

COCO category IDs need not be consecutive or start at zero. This exporter deliberately uses 1,2,3 and records names in `classes.json`; its reader maps category IDs by name. YOLO IDs remain 0,1,2. Never infer one format's category IDs from another without the mapping.

Traditional VOC tools often use 1-based inclusive pixel corners. This tutorial's exporter explicitly tags its XML as `zero-based-continuous-xyxy`, preserves floating-point corners, and avoids an off-by-one shift. Its reader accepts that declared convention only. An arbitrary legacy VOC dataset requires an explicit coordinate-convention adapter; integer rounding or adding/subtracting one blindly can change boxes. The same nominal box may differ by one pixel when rendered in another convention.

## Convert a real held-out split

The converter uses Pillow and PyYAML already present in the detection environment. All commands below run from the repository root. Start with the test split so you can inspect all 186 images without converting the training data unnecessarily.

```powershell
$py = '.\english\02-object-detection\.venv\Scripts\python.exe'
$source = '.\english\02-object-detection\data\rock-paper-scissors-ishcs-v1'
& $py .\04-dataset-formats\scripts\convert.py --source $source --input-format yolo --output-format voc --split test --destination .\04-dataset-formats\data\rps-voc-test
& $py .\04-dataset-formats\scripts\convert.py --source $source --input-format yolo --output-format coco --split test --destination .\04-dataset-formats\data\rps-coco-test
& $py .\04-dataset-formats\scripts\convert.py --source .\04-dataset-formats\data\rps-voc-test --input-format voc --output-format yolo --split test --destination .\04-dataset-formats\data\rps-yolo-from-voc
& $py .\04-dataset-formats\scripts\convert.py --source .\04-dataset-formats\data\rps-coco-test --input-format coco --output-format yolo --split test --destination .\04-dataset-formats\data\rps-yolo-from-coco
```

Use `--split all` to convert available train/valid/test directories. VOC↔COCO uses the same CLI with corresponding input/output formats. The supported input contract is the layout shown below, with `classes.json` for tutorial VOC/COCO datasets; this is not an importer for every possible external directory structure.

```text
yolo/                          voc/                       coco/
  data.yaml                      classes.json               classes.json
  classes.txt                    classes.txt                classes.txt
  test/images/*.jpg              test/JPEGImages/*.jpg      test/images/*.jpg
  test/labels/*.txt               test/Annotations/*.xml     annotations/instances_test.json
```

Every output includes `conversion.json` with image/box counts and class order. The converter preserves image bytes, empty images, split membership, and all supported box annotations. It refuses existing destinations, malformed/out-of-image boxes, missing labels, unknown categories, masks/crowd annotations, and unsupported VOC conventions. It does not silently resplit, clip, resize, augment, or overwrite training data. Segmentation, keypoints, rotated boxes, difficult/crowd semantics, and arbitrary annotation extensions require a separate workflow.

## Inspect with Xiaotudui Labs

Open [Xiaotudui Labs](https://xiaotudui.com/labs). Its three viewer pages were inspected on 2026-10-18. The UI is Chinese; the labels below match the observed controls. This guide verifies the interface and provides a review workflow; it does not claim files were loaded into the website during this check.

| Viewer | Select image | Select annotation |
|---|---|---|
| [YOLO viewer](https://xiaotudui.com/labs/yolo-dataset-viewer) | An image from `test/images/` | Same-stem TXT from `test/labels/` |
| [VOC viewer](https://xiaotudui.com/labs/voc-dataset-viewer) | An image from `test/JPEGImages/` | Same-stem XML from `test/Annotations/` |
| [COCO viewer](https://xiaotudui.com/labs/coco-dataset-viewer) | An image from `test/images/` | `annotations/instances_test.json` containing that image's entry |

1. Choose the relevant viewer from the Labs page. Use the public RPS sample images for this exercise.
2. Select the file using `上传图片文件` and the annotation using `上传YOLO标注文件`, `上传VOC标注文件`, or `上传COCO标注文件`.
3. Click `开始标注` to draw boxes. Use the zoom slider and `重置视图` when necessary. The COCO page also exposes `搜索ID`; use the image ID recorded in its JSON, not an annotation ID.
4. The YOLO instructions mention `classes.txt`, one name per line. The observed interface exposed image and annotation selectors but no separate class-file control; retain `classes.txt` and verify IDs manually if names are not displayed. Do not claim the viewer reads `data.yaml` automatically.
5. Compare the same image across all three viewers: box count, corner locations, semantic category, and full-image alignment must agree. An empty annotation should remain an empty image. If boxes shift or collapse, check image width/height, class mapping, coordinate normalization, and VOC origin/inclusivity.

## Validation and teaching checklist

Run the [round-trip check](scripts/check_roundtrip.py) using the detection interpreter. It exercises all six format directions on a fixture, tests failure handling, and can compare the real converted test datasets with their YOLO source. Check image hashes, split membership, class names, box counts, and pixel coordinates within serialization tolerance. `reports/validation.json` stores measured checks when the real-data validation command is run; no model metric is produced by conversion.

Sources: [Ultralytics YOLO detection format](https://docs.ultralytics.com/datasets/detect/), [COCO format](https://cocodataset.org/#format-data), [Pascal VOC](http://host.robots.ox.ac.uk/pascal/VOC/), and the viewer pages linked above.

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\04-dataset-formats\scripts\check_roundtrip.py
.\english\02-object-detection\.venv\Scripts\python.exe .\04-dataset-formats\scripts\check_roundtrip.py --source .\english\02-object-detection\data\rock-paper-scissors-ishcs-v1
```

The second command creates the example output folders above and refuses existing destinations. For a repeat run, choose a new empty `--output-root`; do not delete or overwrite source data.
