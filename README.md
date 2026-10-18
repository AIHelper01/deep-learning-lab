# Deep Learning Lab

English-first deep learning lessons, with a separate Chinese course for Chinese explanations and datasets.

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

English requires uv (or `python -m uv`); first setup may download Python and dependencies. Chinese modules require a separately prepared `.venv`; see [Chinese setup](docs/environment-setup.zh-CN.md). Chinese YOLO26 detection shares the locked English detection environment; historical PaddleYOLO materials remain available for comparison.

## Course

| Module | Default English course | Chinese counterpart |
|---|---|---|
| Image classification | [LeNet, MNIST, CIFAR-10, ResNet18, custom folders](english/01-image-classification/README.md) | [图像分类](01-image-classification/README.md) |
| Object detection | [CNN, YOLO26, rock-paper-scissors detection](english/02-object-detection/README.md) | [CV、CNN 与 YOLO26](02-object-detection/README.md) |
| Sentiment analysis | [IMDb, embeddings, LSTM, optional DistilBERT](english/03-sentiment-analysis/README.md) | [中文评论、词向量与 LSTM](03-sentiment-analysis/README.md) |

Follow the [learning path](docs/learning-path.md), [environment setup](docs/environment-setup.md), and [dataset guide](docs/datasets.md).

## Language compatibility

English is the default documentation and launcher language. English lessons remain in `english/`; the Chinese modules retain their existing root-level paths so existing notebooks, environments, and local data continue to work. Choose a course by language; changing language does not translate a notebook or switch its dataset in place.

Classification/NLP keep language-specific environments, data processing, vocabularies, and caches. Current detection shares its locked environment and verified dataset; model outputs remain separate by language. Sentiment datasets differ by language, while current detection shares YOLO26n and the official RPS v1 export; see the [adaptation map](english/docs/adaptation-map.md). Chinese runtime validation is incomplete and its saved historical outputs are not evidence of a new successful run.

## Validation and maintenance

The English course includes 13 notebooks with saved execution outputs. Current YOLO26n detection uses the official melikeavan RPS v1 export: a real one-epoch CPU run reached test mAP50 0.7266 and mAP50-95 0.4535. This is a full-data execution check; the lesson default remains ten epochs. Historical mirror scores describe a different dataset. GPU is unverified. See [execution evidence and limits](english/reports/README.md).

- `english/common/`: shared data preparation.
- `english/scripts/`: authoring, execution, and validation tools.
- `english/reports/`: saved validation evidence.
- `docs/migration/`: historical reorganization records; paths describe that migration.
- Module `data/` and `outputs/`: local datasets and experiment artifacts, excluded from Git.

Edit delivered notebooks in place to preserve their saved outputs. English authoring scripts are maintenance tools, not the course startup command.

## Dataset formats and inspection

[YOLO / VOC / COCO conversion and Xiaotudui Labs](04-dataset-formats/README.md) is a separate topic alongside model lessons.
