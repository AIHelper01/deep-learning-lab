# Deep Learning Lab — English Training Edition

The English mirror of the course, derived unit by unit from the Chinese masters. It covers
image classification, object detection, and sentiment analysis. Start from the
[project entry point](../README.md); the [Chinese course](../README.zh-CN.md) is the master
and keeps the original notebook and data paths.

| Module | Learning path | Dataset and output language |
|---|---|---|
| [Image classification](01-image-classification/README.md) | LeNet MNIST → LeNet CIFAR-10 → ResNet18 → custom image folders | Digit images / object images; English class names |
| [Object detection](02-object-detection/README.md) | CNN foundations → bounding boxes → YOLO26 | Rock, paper, scissors detection; English labels |
| [Sentiment analysis](03-sentiment-analysis/README.md) | NLP overview → word embeddings → bidirectional LSTM | English IMDb reviews; negative / positive |

There are 12 counterpart notebooks plus one optional pretrained-English-sentiment notebook.
They are adapted teaching editions rather than sentence-by-sentence translations.
The compact MNIST counterpart is retained in `archive/` for comparison.

## Start a class

1. From the repository root, run `.\start-notebooks.ps1` for English image classification,
   or follow [environment setup](docs/environment-setup.md) for other modules.
2. Begin with [LeNet MNIST](01-image-classification/notebooks/01-lenet-mnist.ipynb).
3. Run the notebook from top to bottom. Paths are located automatically from this course root.
4. Read the [dataset preparation guide](docs/datasets.md) before downloading or distributing data.
5. Read [validation status](reports/README.md) before treating an experiment as classroom-ready.

All authored explanations, code comments, class labels, charts, and messages are English.
No Chinese screenshots or historical outputs are copied. Classification/NLP have independent
data, vocabularies, and caches. Current English/Chinese detection deliberately shares
its official v1 dataset and locked environment; checkpoints and logs stay separate by language. Third-party system errors may still
follow the operating system's language; use an English OS/kernel locale for a fully English UI.

See the [adaptation map](docs/adaptation-map.md) for every original case and its English counterpart.

The notebooks retain locally executed outputs, including charts and predictions.
Use the uv launcher in [environment setup](docs/environment-setup.md). Current detection
runs on Python 3.12.12, PyTorch 2.14.1, and Ultralytics 8.4.177; other lessons retain
their recorded environments. Classification and NLP saved outputs use their documented
classroom parameters. Detection now uses the official melikeavan RPS v1 YOLO26 export:
3,939 training, 338 validation, and 186 test images. The delivered English lesson ran the
default ten epochs on Apple Silicon MPS in 1161.8 seconds and reached test mAP50 0.9410
and mAP50-95 0.7467. Previous mirror-trained outputs are archived.
See [execution reports](reports/README.md) for the scope and current Chinese run.
CUDA execution has not been validated; on Apple silicon the lessons select MPS. Dataset
conversion and Xiaotudui Labs inspection
are a [separate topic](02-object-detection/dataset-formats/README.md).
