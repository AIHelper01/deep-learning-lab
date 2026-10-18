# Dataset preparation and provenance

[Dataset introductions and source catalog](../../docs/datasets.md) · [Chinese guide](../../docs/datasets.zh-CN.md)

Paths in this page are relative to `english/`, unless a command explicitly starts from the repository root.

## Image classification

MNIST contains handwritten digit images. Labels are displayed as zero through nine.
CIFAR-10 contains images in ten object categories, displayed as airplane, automobile,
bird, cat, deer, dog, frog, horse, ship, and truck.

MNIST uses torchvision's downloader. CIFAR-10 reuses a complete local torchvision dataset
when available, otherwise it uses the [university-published Parquet mirror](https://huggingface.co/datasets/uoft-cs/cifar10).
The mirror revision and SHA-256 values are fixed in common/vision_data.py, and both split
counts and class IDs are checked. The mirror preserves the official 50,000/10,000 split.
The custom-folder lesson exports
MNIST images to English-named folders and writes CSV indexes; it does not require LEDNUM.
The course keeps data in `01-image-classification/data/` and outputs separately.
MNIST is 28 x 28 grayscale with 60,000/10,000 source training/test images; CIFAR-10
is 32 x 32 RGB with 50,000/10,000. These are source sizes, not classroom subset sizes.
The English CIFAR directory is lowercase `cifar10/`; MNIST uses `MNIST/`.

Sources: [MNIST loader](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html),
[CIFAR-10 dataset](https://www.cs.toronto.edu/~kriz/cifar.html).

## English sentiment analysis

Source: [Stanford Large Movie Review Dataset](https://ai.stanford.edu/~amaas/data/sentiment/),
Maas et al. (2011), *Learning Word Vectors for Sentiment Analysis*.

The source contains 25,000 labeled training and 25,000 labeled test reviews.
Both frameworks read the same prepared IMDb JSONL files under
`03-sentiment-analysis/data/imdb/`, with `0=negative` and `1=positive` labels. The preparation helper:

1. Downloads the official archive, retaining its source URL and SHA-256.
2. Reads only labeled review files and removes HTML tags.
3. Excludes text containing CJK characters or no English tokens.
4. Removes exact duplicate text across splits.
5. Creates validation data from official training reviews with seed 42.
6. Preserves the official test source for final evaluation.

Counts after filtering are recorded in `data/imdb/provenance.json`. This is a documented
course variant, so results are not directly comparable to unmodified IMDb benchmark scores.
No automated language detector can prove that every word in a review is English; IMDb is
an English-language review corpus, with the explicit checks above. Training tokens are
restricted to English alphabetic words and internal apostrophes.

The default classroom run uses balanced subsets. Set the limits in the notebook to `None`
to use all prepared reviews. Fit vocabulary and Word2Vec only on training data. Keep
negation words. Do not reuse the original Chinese vocabulary or Chinese weights.

## Rock Paper Scissors detection

Both English and Chinese YOLO26n lessons use [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1).
The supplied official `Rock-Paper-Scissors.v1i.yolo26.zip` matches that project and version.
Source metadata and license come from its `data.yaml` and READMEs. Its original splits are
3,939 training / 338 validation / 186 test images, with 4,610 / 400 / 204 boxes.
Labeled crop inspection confirms numeric class order: 0=paper, 1=rock, 2=scissors.

From the repository root, after preparing the detection environment:

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

The importer extracts safely into a temporary directory, checks official v1 metadata,
assigns verified names without changing IDs, validates all annotations and exact split
duplicates, and writes a fresh isolated `02-object-detection/data/rock-paper-scissors-ishcs-v1/`
under `english/`. It refuses overwriting existing data. Keep the export's original
READMEs and CC BY 4.0 attribution. The supplied archive SHA-256 is
`2cf65dffbaa92483bbf99e7903f7c23c934ccf57d1cb097a66b7d38eadac0e59`.

```text
rock-paper-scissors-ishcs-v1/
  data.yaml
  provenance.json
  README.dataset.txt
  README.roboflow.txt
  train/images/ and train/labels/
  valid/images/ and valid/labels/
  test/images/ and test/labels/
```

Both languages share this read-only dataset and detection environment, with separate
output directories. The course validator requires the matching official source;
it does not silently accept the previous mirror or flattened VOC package. Near-duplicate
or video leakage in the upstream split is still a limitation; exact duplicate checks do
not detect it. No boxes or splits were modified in the official v1 export.

The historical mirror-trained notebook is in `02-object-detection/archive/` and its
execution report is `reports/detection-legacy-executed.json`. `scripts/fetch_rps_legacy.py`
is an explicitly historical helper. Their mAP values are not results on the current data.

Conversion is a separate [YOLO / VOC / COCO topic](../02-object-detection/dataset-formats/README.md),
with runnable conversions and Xiaotudui Labs viewer steps. Training consumes YOLO directly.

`COURSE_SMOKE=1` deliberately switches to [COCO8](https://docs.ultralytics.com/datasets/detect/coco8/)
in `02-object-detection/data/coco8/`: eight images, four training and four validation.
This is a software check, not hand-gesture evaluation.

## Vehicle Counting (Traffic Flow)

The vehicle-counting lesson in both languages uses
[vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4),
an official YOLO26 export (CC BY 4.0) with 6,565 square 640x640 images in 5 classes.
Source splits are kept: 4,708 train / 1,661 valid / 196 test images and 52,668 / 18,810 / 2,120
boxes. Class IDs keep their original order with lower-cased names (the source listed `Truck`
capitalized): 0=truck, 1=bicycle, 2=bus, 3=car, 4=motorcycle. English and Chinese read the
same import and write their own `outputs/`; both share the locked detection dependency set, which
pins `lapx` so ByteTrack has the `lap` module.

Roboflow exports belong to an account: use the browser download, or call the export REST
endpoint with a personal API key. Both commands are in
`02-object-detection/data/README.md`; keep the key outside the repository. Datasets live
outside the repository in a DataSet staging folder (classroom mirror
`/workspace/DataSet/yolo/`); the importer copies the ZIP, verifies it, and records
provenance. From the repository root:

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\import_vehicle_counting.py --from-staging
```

On macOS/Linux the classroom machine uses the single `~/env_dl_uv` interpreter and stages the archive
first (`--staging <dir>` moves the DataSet folder):

```bash
cp "/path/to/vehicle counting.v4i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/import_vehicle_counting.py --from-staging
```

or point at any archive with `--archive /path/to/vehicle counting.v4i.yolo26.zip`, or at an
already unpacked export with `--export-dir`. The importer verifies embedded workspace/project
version metadata (`vehicle-counting-rtvul` / `vehicle-counting-tksu5` / 4), the exact class
set, split independence, cross-split duplicates, and box geometry, then writes
`02-object-detection/data/vehicle-counting-tksu5-v4/` with `provenance.json`; the classroom
archive SHA-256 is `3945432ed7ce76c9af3b83db7f0ee68ad898b0996bd7577f88a3b6ee6f0cea20`.
Existing destinations are refused. Three label lines in the source package were segmentation
polygons; the importer rewrites each to its enclosing detection box and records the count.

The lesson's default traffic clip is synthesized offline by
`scripts/build_traffic_demo_video.py` from real annotated vehicle crops, so every spawned
vehicle crosses the counting line exactly once and the counter has a ground truth;
`TRAFFIC_VIDEO=<path.mp4>` switches the same pipeline to a real road video.

## Optional pretrained English model

[DistilBERT fine-tuned on SST-2](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)
provides English positive/negative inference. It has a trained classification head.
Its task and data differ from the LSTM IMDb experiment; model-card metrics are not local results.

## Offline teaching

Run downloads and notebook checks before class, then copy the entire english/ course
with the needed data and weights to an ASCII-named path. Keep separate environment setup
instructions per operating system; virtual environments are not portable. Retain upstream
dataset attribution and terms. Prepared caches are local assets, not committed source files.

