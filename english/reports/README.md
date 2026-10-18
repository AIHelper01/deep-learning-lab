# Execution evidence

Every number here comes from a real Jupyter kernel run with outputs saved into the notebook, and every number is
labelled with its run mode. Two environments produced the evidence:

- **Current:** the single classroom environment outside the repository, `~/env_dl_uv` (Python 3.12.12 on an Apple
  Silicon Mac: MPS for PyTorch and Ultralytics, CPU for Paddle), which produced all Chinese lessons plus the English
  and Chinese detection runs on 2026-10-18.
- **Earlier:** four per-module uv environments on a Windows machine, which produced the English image-classification
  and NLP evidence (their reports record `E:\...` executables).

MPS is verified on that machine; CUDA is unverified everywhere. `data/` and `outputs/` are excluded from Git, so the
datasets must be staged in the DataSet folder and then copied in before a run (see the module `data/README.md` files,
which give both the `cp` command and the download command, and the [dataset guide](../docs/datasets.md)).

## Vehicle counting, traffic flow (2026-10-18, MPS)

Both language courses ran the full lesson on the official
[vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)
export with the classroom defaults (YOLO26n, 5 epochs at `imgsz=320`, `seed=42`), then evaluated the 196-image test
split and counted vehicles in images and in a tracked video.

| Course | Notebook | Seconds | Code cells | Outputs | Figures |
|---|---|---:|---:|---:|---:|
| English | `notebooks/02-yolo26-vehicle-counting.ipynb` | 940.21 | 13 | 19 | 7 |
| Chinese | `../../02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb` | 940.47 | 13 | 19 | 7 |

English run, measured on MPS: validation mAP50 per epoch 0.4933, 0.5645, 0.6207, 0.6368, 0.6407 (cumulative
182/361/539/717/896 s); test precision 0.7308, recall 0.6444, mAP50 0.6983, mAP50-95 0.4071. Zero-shot counting
error 4.33 vehicles per image over six test images, and 3.75 over the four images also used for the fine-tuned
comparison; fine-tuned counting error 4.00 over those same four images. Line-crossing tracking on the generated
clip: 4 forward, 2 backward, 6 unique vehicles out of 10 tracks, 40.0 vehicles per minute against 6 ground-truth
crossings - a deviation of exactly 0, although one spawned `car` was reported as a `bus`. The Chinese run reaches
the same conclusions on the same data; its own numbers are in
[the Chinese narrative report](../../02-object-detection/lessons/05-vehicle-counting-run-report.md).

- Narrative report with every quoted output and figure: [English course](../02-object-detection/lessons/05-vehicle-counting-run-report.md),
  [Chinese course](../../02-object-detection/lessons/05-vehicle-counting-run-report.md).
- [English execution](detection-executed.json), [Chinese execution](detection-zh-CN-executed.json).
- Run folders (`runs/vehicle-counting-v4-yolo26n-*`) hold weights, curves, confusion matrices and `metrics.json`.
- Five epochs at 320 pixels did not converge: validation mAP50 was still rising. These are the numbers of *this*
  classroom run, not the ceiling of the dataset. Raising `imgsz` and `epochs` is the first lever.

## Rock-paper-scissors detection

Both courses ran the delivered lesson with its classroom defaults - YOLO26n, **ten epochs** at `imgsz=320`,
`batch=8`, `seed=42` - on Apple silicon MPS inside `~/env_dl_uv`, over all 3,939 training images.

| Course | Seconds | test mAP50 | test mAP50-95 |
|---|---:|---:|---:|
| English | 1161.8 | **0.9410** | **0.7467** |
| Chinese | 1163.89 | **0.9410** | **0.7467** |

Same data, same seed, same defaults, so the two languages agree; the single-image test prediction is `paper` at
0.874 confidence in both. Rows live in [detection-executed.json](detection-executed.json) and
[detection-zh-CN-executed.json](detection-zh-CN-executed.json).
- [Run summary and checkpoints](rps-v1-run-summary.json), [source verification](rps-v1-data-checks.json),
  [class review](rps-v1-class-id-review.png), [runtime environment](rps-v1-environment.json),
  [installed packages](uv-detection-v1-environment.txt).
- Each notebook keeps four figures: epoch metrics, test confusion matrix, test predictions, single-image prediction.
- MPS reaches the Ultralytics determinism switch, whose `index_put_with_accumulate_mps` kernel has no deterministic
  implementation. The two languages matched to four decimals here; a rerun matches in aggregate, not bit-for-bit.
- [Format conversion validation](dataset-formats-validation.json): 186 images, 204 boxes, exact
  image-byte preservation, box round trips within 0.001 pixel tolerance.
- The earlier mirror execution is `detection-legacy-executed.json` and its notebook is in
  `02-object-detection/archive/`. Its 0.904/0.524 metrics belong to a different dataset package and must never be
  attributed to official v1.

## Image classification and NLP (classroom defaults, not smoke mode)

Three epochs for classification, five for LSTM, documented course subsets, ResNet18 with pretrained ImageNet weights,
and the optional pretrained sentiment checkpoint per language.

| Notebook | English seconds | Chinese seconds |
|---|---:|---:|
| vision 01 LeNet + MNIST | 18.69 | 4.88 |
| vision 02 LeNet + CIFAR-10 | 46.57 | 7.20 |
| vision 03 ResNet18 + CIFAR-10 | 748.30 | 564.99 |
| vision 04 custom folders | 74.85 | 5.81 |
| vision archive `01-lenet-mnist-copy1` | 79.51 | 36.23 |
| pytorch 01 NLP overview | 15.46 | 1.39 |
| pytorch 02 word embeddings | 206.74 | 6.39 |
| pytorch 03 LSTM sentiment | 744.07 | 63.04 |
| pytorch 04 pretrained sentiment | 53.48 (SST-2) | 8.53 (JD Chinese) |
| paddle 01 NLP overview | 16.95 | 1.44 |
| paddle 02 word embeddings | 84.84 | 6.90 |
| paddle 03 LSTM sentiment | 121.36 | 24.77 |

The Chinese NLP lessons are not a translation of IMDb: they train on ChnSentiCorp with jieba segmentation, so the
runs are shorter and the accuracies are not comparable across languages. English LSTM reached test accuracy 0.736;
the Chinese LSTM reached 0.838 on its own split.

- [vision](vision-executed.json) · [vision zh-CN](vision-zh-CN-executed.json) ·
  [pytorch](pytorch-executed.json) · [pytorch zh-CN](pytorch-zh-CN-executed.json) ·
  [paddle](paddle-executed.json) · [paddle zh-CN](paddle-zh-CN-executed.json).

## Evidence and limits

- `*-executed.json`: per-notebook status, elapsed time, output counts, run mode and interpreter. Reports accumulate;
  `--notebook` runs no longer drop the other rows.
- `saved-output-checks.json`: 28 delivered notebooks on both sides, every non-empty code cell executed, no saved
  errors, embedded image counts.
- `docs-asset-checks.json`: repository-wide local link reachability, zero remote images, `assets/<name>-<index>`
  naming, bilingual `docs/` pairing. `legacy_external_links` counts links inside archived PaddleYOLO courseware,
  which is read-only history.
- `uv-*-environment.txt`: installed packages per environment. `static-checks.json`: notebook schema, English-language
  scan, local links. `original-course-integrity.json`: hash comparison of all 93 original course files.
- `COURSE_SMOKE=1` (COCO8, random ResNet weights) and `COURSE_EPOCHS=<n>` change what a score means; never mix them
  with the default-parameter results above.
- Detection runs use Apple silicon MPS and the other lessons run in the same `~/env_dl_uv` interpreter on one
  machine. These are teaching runs, not benchmarks or accuracy guarantees.
