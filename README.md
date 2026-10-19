# Deep Learning Lab

English-first deep learning lessons, with a mirrored Chinese course: the same lessons cell by cell, in Chinese prose, with Chinese output, and Chinese datasets where the language matters.

**English (default)** · [中文课程与说明](README.zh-CN.md)

## Start here

From the repository root in PowerShell:

```powershell
.\start-notebooks.ps1
```

The default is **English image classification**. The launcher uses the module's locked uv environment and opens JupyterLab. Start with [LeNet on MNIST](english/01-image-classification/notebooks/01-lenet-mnist.ipynb).

```powershell
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Module paddle
.\start-notebooks.ps1 -Module detection
.\start-notebooks.ps1 -Language zh-CN -Module vision
```

English requires uv (or `python -m uv`); first setup may download Python and dependencies. On macOS/Linux the whole course - English and Chinese, all four modules - runs from one verified uv environment outside the repository, `~/env_dl_uv`, whose Jupyter kernel is also called `env_dl_uv`; see [setup](docs/environment-setup.md).

Execute a lesson and keep its real output with:

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision            # English
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py                              # quote results back into the notebooks
```

## Course

| Module | Default English course | Chinese counterpart |
|---|---|---|
| Image classification | [LeNet, MNIST, CIFAR-10, ResNet18, custom folders](english/01-image-classification/README.md) | [图像分类](01-image-classification/README.md) |
| Object detection | [CNN, YOLO26, rock-paper-scissors detection, vehicle counting](english/02-object-detection/README.md) | [CV、CNN、YOLO26 检测与车流量统计](02-object-detection/README.md) |
| Sentiment analysis | [IMDb, embeddings, LSTM, optional DistilBERT](english/03-sentiment-analysis/README.md) | [中文评论、词向量与 LSTM](03-sentiment-analysis/README.md) |

Follow the [learning path](docs/learning-path.md), [environment setup](docs/environment-setup.md), and [dataset guide](docs/datasets.md).

## Language compatibility

English is the default documentation and launcher language. English lessons remain in `english/`; the Chinese modules retain their existing root-level paths so existing notebooks, environments, and local data continue to work. Choose a course by language; changing language does not translate a notebook or switch its dataset in place.

Classification/NLP keep language-specific data processing, vocabularies and caches, and sentiment datasets differ by language, while detection shares YOLO26n and the official RPS v1 export; see the [adaptation map](english/docs/adaptation-map.md). Both languages now run in the same interpreter, and every delivered Chinese notebook was re-executed in it on 2026-10-18; the archived `archive/legacy-notebooks/` lessons stay out of default runs and are re-executed only through the explicit `--include-legacy` opt-in. Model outputs always stay separate by language.

## Validation and maintenance

Every current lesson notebook (13 per language) carries outputs from a real kernel run, quoted back into the
notebook as `**Expected output:**` / `**预期输出：**` blocks and `assets/*.png` figures. YOLO26n detection runs on
the official exports: rock-paper-scissors v1 reached test mAP50 0.9410 / mAP50-95 0.7467 in the English ten-epoch
lesson run, and the vehicle-counting lesson reached test mAP50 0.6983 / mAP50-95 0.4071 with real tracking and
line-crossing counts that matched the video ground truth exactly. Classroom runs use Apple Silicon MPS in the
single `~/env_dl_uv` environment; CUDA has not been validated. Historical mirror scores describe a different
dataset. See [execution evidence and limits](english/reports/README.md).

- `scripts/check_docs_assets.py`: local link reachability, heading anchors, zero remote images, `assets/<name>-<index>` naming, and bilingual `docs/` pairing across the whole repository.
- `english/scripts/verify_saved_outputs.py`: every delivered notebook on both sides executed, no saved errors.
- `english/common/`: shared data preparation.
- `english/scripts/`: authoring, execution, and validation tools.
- `english/reports/`: saved validation evidence.
- `docs/migration/`: historical reorganization records; paths describe that migration.
- Module `data/` and `outputs/`: local datasets and experiment artifacts, excluded from Git.

Edit delivered notebooks in place to preserve their saved outputs. English authoring scripts are maintenance tools, not the course startup command.

## How the two languages stay aligned

- `english/` holds the masters. `scripts/build_chinese_course.py` mirrors the vision and NLP lessons into the Chinese tree: identical cells and training logic, Chinese narration, prints, plot labels and class names. Translation tables key on exact English text, so an untranslated master edit fails the build.
- The Chinese NLP lessons are not a translation of IMDb: they train on ChnSentiCorp Chinese reviews with jieba segmentation via `common/sentiment_cn.py`, which keeps the English module's loader interface.
- `CHINESE_COURSE_ROOT` marks the Chinese course root; `scripts/check_parity.py` checks ASCII paths, one-to-one file pairing, cell counts per notebook, and the language of user-visible output, and records every exception with a reason.
- `scripts/embed_expected_outputs.py` writes each executed run back into its notebook as `**Expected output:**` / `**预期输出：**` blocks plus `assets/<notebook>-N.png` figures, so a cleared notebook still shows real results.
- Pre-rebuild Chinese notebooks stay in the `archive/legacy-notebooks/` folder of the vision and NLP modules, while the
  original Chinese detection notebook stays in `02-object-detection/notebooks/` next to the current lesson (reference
  only; never executed, and registered in `HISTORY_IN_NOTEBOOKS` so it is excluded from pairing and validation).

## Data: stage once, then copy or import per module

Datasets live outside Git. The classroom mirror is a DataSet staging folder - `/workspace/DataSet` on the class
machine, with one subfolder per family (`yolo/`, `cvdata/`, `nlp/`, ...) - and each module keeps its real data under
its own `data/` directory. Every module `data/README.md` documents both routes for each dataset: the **cp method**
(copy the staged archive or unpacked folder into the module, or hand it to the module's importer) and the **download
method** (source page, format to select, and where to save the archive).

| Staging location | Module destination |
|---|---|
| `/workspace/DataSet/cvdata/MNIST`, `.../CIFAR10` | `01-image-classification/data/`, `english/01-image-classification/data/` |
| `/workspace/DataSet/yolo/*.zip` | imported into `english/02-object-detection/data/` (shared, read-only) |
| `/workspace/DataSet/nlp/imdb`, `.../ChnSentiCorp` | `03-sentiment-analysis/data/`, `english/03-sentiment-analysis/data/` |

Full catalogue, licences, hashes and classroom subsets: [dataset guide](docs/datasets.md) ·
[中文数据说明](docs/datasets.zh-CN.md).

## Dataset formats and inspection

[YOLO / VOC / COCO conversion and Xiaotudui Labs](english/02-object-detection/dataset-formats/README.md) is a separate topic alongside model lessons.
