# Deep Learning Lab — English Training Edition

An independent English-language course covering image classification, object detection,
and sentiment analysis. Start here; the original course outside this directory is unchanged.

| Module | Learning path | Dataset and output language |
|---|---|---|
| [Image classification](01-image-classification/README.md) | LeNet MNIST → LeNet CIFAR-10 → ResNet18 → custom image folders | Digit images / object images; English class names |
| [Object detection](02-object-detection/README.md) | CNN foundations → bounding boxes → YOLO26 | Rock, paper, scissors detection; English labels |
| [Sentiment analysis](03-sentiment-analysis/README.md) | NLP overview → word embeddings → bidirectional LSTM | English IMDb reviews; negative / positive |

There are 12 counterpart notebooks plus one optional pretrained-English-sentiment notebook.
They are adapted teaching editions rather than sentence-by-sentence translations.
The compact MNIST counterpart is retained in `archive/` for comparison.

## Start a class

1. Follow [environment setup](docs/environment-setup.md).
2. Begin with [LeNet MNIST](01-image-classification/notebooks/01-lenet-mnist.ipynb).
3. Run the notebook from top to bottom. Paths are located automatically from this course root.
4. Read the [dataset preparation guide](docs/datasets.md) before downloading or distributing data.
5. Read [validation status](reports/README.md) before treating an experiment as classroom-ready.

All authored explanations, code comments, class labels, charts, and messages are English.
No Chinese screenshots or historical outputs are copied. The English course has independent
data, vocabularies, caches, model checkpoints, and logs. Third-party system errors may still
follow the operating system's language; use an English OS/kernel locale for a fully English UI.

See the [adaptation map](docs/adaptation-map.md) for every original case and its English counterpart.

The notebooks retain locally executed outputs, including charts and predictions.
Use the uv launcher in [environment setup](docs/environment-setup.md) with Python 3.12.15,
PyTorch 2.14.1, or PaddlePaddle 3.3.1. Classification and NLP use default classroom
training parameters. The YOLO26 notebook now trains on the real Rock Paper Scissors export
built by `scripts/fetch_rps.py`, and its saved outputs come from a one-epoch pipeline check
because a full ten-epoch classroom run costs about thirty-five CPU minutes. See
[execution reports](reports/README.md) for the measured results and scope. GPU execution has
not been validated.

