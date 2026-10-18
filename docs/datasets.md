# Dataset guide

English (default) · [中文说明](datasets.zh-CN.md) · [Preparation details](../english/docs/datasets.md)

This guide describes what each dataset teaches, where it comes from, and how the course uses it. All local paths below are relative to the repository root. Source pages were reviewed on 2026-10-18; provider counts and download options may change. Source dataset sizes are distinct from the smaller classroom subsets configured in notebooks.

| Dataset | Task | Used by |
|---|---|---|
| [MNIST](#mnist) | Handwritten digit classification | LeNet and custom-folder lessons |
| [CIFAR-10](#cifar-10) | Object image classification | LeNet and ResNet18 |
| [Rock Paper Scissors](#rock-paper-scissors) | Hand-gesture object detection | YOLO lessons |
| [Vehicle counting](#vehicle-counting-traffic-flow) | Vehicle detection and traffic flow | Vehicle-counting notebook, both languages |
| [IMDb](#imdb) | English sentiment classification | English Word2Vec and LSTM |
| [ChnSentiCorp](#chnsenticorp) | Chinese sentiment classification | Chinese NLP routes |
| [COCO8](#coco8) | Tiny object-detection pipeline check | English detection smoke mode |
| [Custom digits and LEDNUM](#custom-digits-and-lednum) | Custom image loading | Extension lessons |

## MNIST

- **Introduction:** grayscale handwritten digits, 28 × 28 pixels; ten labels, 0–9. The standard split has 60,000 training and 10,000 test images. It teaches the complete preprocessing, training, evaluation, and checkpoint workflow.
- **Source:** [MNIST dataset card](https://huggingface.co/datasets/ylecun/mnist); [torchvision downloader documentation](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html).
- **Get it:** run the MNIST notebook; `torchvision.datasets.MNIST(download=True)` downloads the format the lessons expect. The linked Parquet dataset card is for browsing; it is not a drop-in replacement for torchvision's raw files.
- **Local location:** English `english/01-image-classification/data/MNIST/`; Chinese `01-image-classification/data/MNIST/`.
- **Course handling:** validation comes from training data. Keep the official test set for final evaluation. English custom-folder data is derived from MNIST, not an additional independent dataset.
- **Attribution:** retain the dataset authors' attribution and the terms supplied with the downloaded distribution.

## CIFAR-10

- **Introduction:** small color object images, 32 × 32 pixels; ten classes: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck. The official split contains 50,000 training and 10,000 test images. Used to compare LeNet with ResNet18 transfer learning.
- **Source:** [University of Toronto dataset page](https://www.cs.toronto.edu/~kriz/cifar.html); [Python archive](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz); [university-published Parquet mirror](https://huggingface.co/datasets/uoft-cs/cifar10).
- **Get it:** Chinese notebooks use torchvision's downloader. The English loader first reuses a valid local torchvision copy; otherwise it fetches a pinned Parquet mirror revision and verifies SHA-256, class IDs, and split counts.
- **Local location:** English `english/01-image-classification/data/cifar10/`; Chinese `01-image-classification/data/CIFAR10/`. Letter case is intentional.
- **Course handling:** notebook subsets are teaching settings, not the full benchmark. The English loader records provenance in `train-provenance.json` and `test-provenance.json`.
- **Attribution:** cite Krizhevsky's 2009 report linked on the source page; retain the downloaded distribution's terms.

## Rock Paper Scissors

- **Task and model:** hand-gesture bounding-box detection using Ultralytics **YOLO26n**, in both English and Chinese lessons.
- **Source:** [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1), [version listing](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset). The supplied official YOLO26 archive embeds matching project/version metadata and CC BY 4.0 notices.
- **Content:** 4,463 images, with original splits of **3,939 training / 338 validation / 186 test** and **4,610 / 400 / 204 bounding boxes**. Auto-oriented images are stretched to 640x640; no export augmentation is listed. This is distinct from model-time training augmentation.
- **Classes:** source names are numeric. Labeled crop review confirms **0=paper, 1=rock, 2=scissors**. The importer assigns those English names at the same IDs; it preserves labels and source splits.
- **Get it:** download the v1 YOLO26 export from the browser, or request the same export from the Roboflow REST API with a personal API key; both routes are documented in `english/02-object-detection/data/README.md`. Datasets are staged outside the repository in a DataSet folder (classroom mirror `/workspace/DataSet/yolo/`), then imported from there:

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```
```bash
# macOS/Linux, repository root, single classroom interpreter
cp "/path/to/Rock-Paper-Scissors.v1i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

- **Local location:** `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`; both language lessons share this verified dataset and locked detection environment. Outputs remain separate by language. Do not import again if this validated destination already exists.
- **Integrity:** the importer refuses existing destinations and validates source identity, class IDs, normalized boxes, and cross-split exact duplicates. It records ZIP SHA-256 and counts in `provenance.json`. The original supplied ZIP hash is `2cf65dffbaa92483bbf99e7903f7c23c934ccf57d1cb097a66b7d38eadac0e59`. No invalid boxes or cross-split exact duplicates were found in this export; this does not rule out near-duplicate/video leakage in the upstream split.
- **Attribution:** retain the exported READMEs, credit melikeavan, and link the selected version and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Record modifications such as English class names.

The historical Xuban mirror and the superseded flattened 6,455-image VOC package are excluded from the default course. Previous mirror metrics are historical, not results on this v1 dataset. The archived notebook and `fetch_rps_legacy.py` exist for historical reproduction only.

Dataset conversion and inspection are a separate [YOLO / VOC / COCO topic](../english/02-object-detection/dataset-formats/README.md), including [Xiaotudui Labs](https://xiaotudui.com/labs) viewer instructions. The training lesson consumes YOLO directly and requires no format conversion.

## Vehicle Counting (Traffic Flow)

- **Task and model:** vehicle bounding-box detection plus traffic-flow counting (detection, zero-shot comparison, fine-tuned counting, tracking with line-crossing) using Ultralytics **YOLO26n**. Both languages run the lesson on the same import: English
  [vehicle-counting notebook](../english/02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb) and Chinese
  [vehicle-counting notebook](../02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb).
- **Source:** [vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4), official YOLO26 export (`vehicle counting.v4i.yolo26.zip`) embedding matching workspace/project/version metadata and CC BY 4.0 notices.
- **Content:** 6,565 square 640x640 images in 5 classes, source splits kept: **4,708 train / 1,661 valid / 196 test** images and **52,668 / 18,810 / 2,120** boxes.
- **Classes:** original ID order with lower-cased names (the source listed `Truck` capitalized): **0=truck, 1=bicycle, 2=bus, 3=car, 4=motorcycle**.
- **Get it:** the v4 YOLO26 export needs a Roboflow account: use the browser download, or the export REST endpoint with a personal API key (`english/02-object-detection/data/README.md` lists both commands). Datasets are staged outside the repository in a DataSet folder (classroom mirror `/workspace/DataSet/yolo/`); the importer copies, verifies, and records provenance. From the repository root:

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\import_vehicle_counting.py --from-staging
```
```bash
# macOS/Linux, repository root, single classroom interpreter (add --staging <dir> for another DataSet folder)
cp "/path/to/vehicle counting.v4i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/import_vehicle_counting.py --from-staging
```

- **Local location:** `english/02-object-detection/data/vehicle-counting-tksu5-v4/` alongside the shared gesture dataset; each language writes its own
  `outputs/` (English `english/02-object-detection/outputs/`, Chinese `02-object-detection/outputs/`). Tracking needs the `lapx` package (provides the `lap` module), already pinned in the locked detection environment.
- **Integrity:** the importer verifies embedded Roboflow identity, class set, split independence, cross-split duplicates, and box geometry. Three label lines in the source package were segmentation polygons; they are rewritten to their enclosing detection boxes and the count (3) is recorded with the archive SHA-256 `3945432ed7ce76c9af3b83db7f0ee68ad898b0996bd7577f88a3b6ee6f0cea20` in `provenance.json`. Existing destinations are refused.
- **Attribution:** credit vehicle-counting-rtvul on Roboflow Universe, link the version page and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), and note the lower-cased names plus the three normalized segmentation lines.

## IMDb

- **Introduction:** English movie reviews for positive/negative sentiment classification. The source supplies 25,000 labeled training and 25,000 labeled test reviews, plus an unlabeled portion that this course does not use.
- **Source:** [Stanford Large Movie Review Dataset](https://ai.stanford.edu/~amaas/data/sentiment/); [official archive](https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz).
- **Get it:** run an English embeddings or LSTM notebook. `english/common/course_data.py` downloads the archive and prepares shared JSONL files for PyTorch and Paddle.
- **Local location:** `english/03-sentiment-analysis/data/imdb/` with `train.jsonl`, `validation.jsonl`, `test.jsonl`, and `provenance.json`.
- **Course handling:** removes HTML, exact duplicate texts, texts containing CJK characters, and texts without English tokens; validation is drawn from source training reviews with seed 42. Labels are `0=negative`, `1=positive`. Balanced classroom subsets and filtering change counts; use provenance and notebook settings for actual run sizes. Fit vocabulary and Word2Vec on training data only.
- **Attribution:** cite Maas et al. (2011), linked on the source page, and retain the archive's README and applicable terms. Course results are not unmodified IMDb benchmark results.

## ChnSentiCorp

- **Introduction:** Chinese review sentiment data used by the Chinese NLP lessons; binary labels are interpreted in the lessons as `0=negative`, `1=positive`.
- **Source:** [PaddleNLP dataset implementation](https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/datasets/chnsenticorp.py); [course download archive](https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip).
- **Get it:** `common/sentiment_cn.py` downloads and extracts the archive on first use. Both framework routes share `03-sentiment-analysis/data/ChnSentiCorp/` and the adjacent `ChnSentiCorp.zip`; do not run their extraction steps concurrently. If the copy already sits in the local dataset library, skip the download: `cp -R /workspace/DataSet/nlp/ChnSentiCorp 03-sentiment-analysis/data/`. Both routes produce identical results.
- **Course splits:** the same module writes reproducible JSONL splits to `03-sentiment-analysis/data/chnsentiment/{train,validation,test}.jsonl` and records row counts, dropped rows, removed duplicates and source SHA-256 values in `provenance.json` beside them. Validation is 20% per label drawn from the official `train.tsv`; the **labelled official `dev.tsv` is the final evaluation split**, because the shipped `test.tsv` carries no labels. Tokenization uses jieba word segmentation with no stopword list, so negation words survive.
- **Format and splits:** TSV files, with headers; the PaddleNLP distribution reads training as `label, text`, development as `qid, label, text`, and test as `qid, text` with no gold label. Inspect the extracted directory nesting and notebook paths. Do not treat unlabeled test predictions as measured accuracy; use labeled development data or a documented labeled evaluation split. Record actual row counts rather than borrowing counts from differently packaged mirrors.
- **Attribution:** retain the source archive's notices. The loader's software license does not establish a separate license for the review texts.

## COCO8

- **Introduction:** an eight-image detection fixture (four training, four validation) in the COCO label space, intended for fast pipeline checks.
- **Source:** [Ultralytics COCO8 guide](https://docs.ultralytics.com/datasets/detect/coco8/); [download archive](https://ultralytics.com/assets/coco8.zip).
- **Get it / location:** set `COURSE_SMOKE=1` before starting the English detection kernel. The helper downloads to `english/02-object-detection/data/coco8/`.
- **Course handling:** this is a software check, not hand-gesture training or evidence of generalization. Return to default mode for the real RPS experiment. Retain the source distribution's notices and review the provider's licensing links before redistribution.

## Custom digits and LEDNUM

- **English custom digits:** generated locally from MNIST by the extension notebook; no separate download. ImageFolder data and CSV indexes go under `english/01-image-classification/data/custom-digits-balanced/` (the smoke variant adds `-smoke`). Labels are English digit names. Preserve source split separation, and read ImageFolder's `class_to_idx` rather than assuming folder ordering equals numeric digit order. MNIST attribution still applies.
- **Chinese custom folders:** the Chinese lesson now follows the English MNIST-derived layout (`01-image-classification/data/custom-digits-balanced/`, with a `-smoke` variant), keeping ASCII folder names and mapping them to Chinese display labels, so it no longer depends on LEDNUM.
- **LEDNUM (historical):** the superseded Chinese extension expected LED-display digits under `01-image-classification/data/LEDNUM/` (`train_data/`, `test_data/`, `train.txt`, `test.txt`). The repository does not supply an authoritative public download, verified counts, or a license for this collection. Those notebooks are archived in `01-image-classification/archive/legacy-notebooks/`; the current course does not need the data. The old `/workspace` copy command is an environment example, not a download address.

## Pretrained models and offline use

Pretrained model downloads are separate from course datasets. ResNet18 uses ImageNet weights; YOLO downloads detector weights; optional [DistilBERT fine-tuned on SST-2](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) performs English binary sentiment inference. SST-2 is not the IMDb training set, and the course does not download it as an additional training corpus. Model-card metrics are not local evaluation results.

English caches are `english/data/torch-cache/`, `english/data/huggingface/`, and detection weights in `english/02-object-detection/outputs/weights/`. Download data and weights before class; copy required caches and provenance for offline use, but recreate environments per platform. Keep source attribution, versions, checksums where available, actual split counts, class mappings, and transformation notes. Dataset files and model products remain excluded from Git.
