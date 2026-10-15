# Dataset preparation and provenance

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

Sources: [MNIST loader](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html),
[CIFAR-10 dataset](https://www.cs.toronto.edu/~kriz/cifar.html).

## English sentiment analysis

Source: [Stanford Large Movie Review Dataset](https://ai.stanford.edu/~amaas/data/sentiment/),
Maas et al. (2011), *Learning Word Vectors for Sentiment Analysis*.

Both frameworks read the same prepared IMDb JSONL files. The preparation helper:

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

Use the [Roboflow Rock Paper Scissors object-detection dataset](https://universe.roboflow.com/roboflow-58fyf/rock-paper-scissors-sxsw).
Export a chosen version in a YOLO bounding-box format compatible with Ultralytics.
An account may be required by the provider. Retain the export's license and attribution
files, and record its version before distributing a classroom bundle.

Unpack the export under `02-object-detection/data/rock-paper-scissors/`:

```text
rock-paper-scissors/
├── data.yaml
├── train/images/ and train/labels/
├── valid/images/ and valid/labels/
└── test/images/ and test/labels/
```

### Download addresses

- Upstream provider, account and API key may be required:
  <https://universe.roboflow.com/roboflow-58fyf/rock-paper-scissors-sxsw>
- Credential-free YOLO mirror on Hugging Face Hub:
  <https://huggingface.co/datasets/Xuban/rock-paper-scissors-roboflow> (CC BY 4.0, mirrored
  from <https://universe.roboflow.com/rock-paper-scissors-2/rock-paper-scissors-bwev7>).
  Measured on 2026-10-15: `images/train` 1,485 files and `images/val` 100 files, 43.8 MB in
  total, with `labels/train` and `labels/val` matching the images one to one. In the 903
  mirrored label files checked here, only class IDs 0, 1, and 2 occur, in normalized
  `class_id x_center y_center width height` form.

`scripts/fetch_rps.py` turns the mirror into the layout above and is the supported way to
prepare this dataset:

```powershell
02-object-detection\.venv\Scripts\python.exe scripts\fetch_rps.py
```

The script caches the mirror in `data/rps-mirror`, so a re-run only fetches what is missing,
then builds `data/rock-paper-scissors` and validates it with `prepare_rps`. Three differences
between the mirror and the course contract are handled there and recorded in
`data/rock-paper-scissors/provenance.json`:

- The mirror layout is `images/train` plus `labels/train`, so the script rewrites
  `data.yaml` and copies each split into `<split>/images` and `<split>/labels`.
- The mirror has no test split. Its 100 validation images are ordered by the SHA-256 of the
  filename, and the first half becomes `valid/` while the second half becomes `test/`, so the
  reported test numbers are a real held-out set rather than the training distribution.
- One mirrored annotation reaches normalized coordinate 1.48, outside the image. The course
  validator rejects it, so the script clips box edges to the image bounds and keeps the
  visible extent. One of the 2,133 annotation rows is affected.

Only per-file downloads work on the mirror
(`https://huggingface.co/datasets/Xuban/rock-paper-scissors-roboflow/resolve/main/<path>`):
the usual `/archive/main.zip` endpoint returns HTTP 404, so there is no single-zip download.
Retain the CC BY 4.0 attribution in any classroom bundle. The resulting splits are 1,485
training images with 1,973 boxes, 50 validation images with 80 boxes, and 50 test images with
80 boxes. The delivered notebook run uses the classroom ten-epoch setting on this export and
reached test mAP50 0.904 and mAP50-95 0.524 in about 35 CPU minutes; `COURSE_EPOCHS=1` repeats
the same path as a short check with a much lower score.

The course checks the three English class names, preserves their ID order, checks label
coordinates, and detects exact image duplicates across splits. A labeled classification
dataset without bounding boxes cannot replace this export. Exported images may contain
incidental scene text; inspect representative samples before teaching.

`COURSE_SMOKE=1` uses COCO8 only for a YOLO26 software check. It is never reported as a
completed hand-gesture experiment. COCO8 uses English object labels.

## Optional pretrained English model

[DistilBERT fine-tuned on SST-2](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)
provides English positive/negative inference. It has a trained classification head.
Its task and data differ from the LSTM IMDb experiment; model-card metrics are not local results.

## Offline teaching

Run downloads and notebook checks before class, then copy the entire english/ course
with the needed data and weights to an ASCII-named path. Keep separate environment setup
instructions per operating system; virtual environments are not portable. Retain upstream
dataset attribution and terms. Prepared caches are local assets, not committed source files.

