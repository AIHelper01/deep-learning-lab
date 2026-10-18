# Adaptation map

Each source path below is relative to the original project root. The English counterpart
has the same module-relative path unless stated otherwise. This map records the original adaptation. The current Chinese detection lesson has since
been updated to YOLO26n as well; its older PaddleYOLO notebook stays in the same `notebooks/` folder as read-only
history, next to the current lesson.

| Source case | English counterpart | Changes |
|---|---|---|
| `01-image-classification/notebooks/01-lenet-mnist.ipynb` | Same path inside english/ | English teaching flow, digit names, plots, separate validation data |
| `01-image-classification/notebooks/02-lenet-cifar10.ipynb` | Same path | English CIFAR-10 names, portable paths, validation checkpoint |
| `01-image-classification/notebooks/03-resnet-cifar10.ipynb` | Same path | ResNet18 transfer learning, documented normalization and frozen backbone |
| `01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb` | Same path | MNIST exported to English ImageFolder classes replaces unavailable LEDNUM; domain change explicitly documented |
| `01-image-classification/archive/01-lenet-mnist-copy1.ipynb` | Same path | Compact English comparison edition, separate experiment output |
| `02-object-detection/notebooks/01-yolo11-rock-paper-scissors.ipynb` | `02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb` | Ultralytics YOLO26n; validated English detection labels; the original PaddleYOLO lesson is preserved in place in the same folder, read-only and never executed |
| `03-sentiment-analysis/pytorch/notebooks/01-nlp-overview.ipynb` | Same path | English tasks, examples, tokenization and evaluation concepts |
| `03-sentiment-analysis/pytorch/notebooks/02-word-embeddings.ipynb` | Same path | English IMDb training text → Word2Vec → PyTorch Embedding → PCA |
| `03-sentiment-analysis/pytorch/notebooks/03-lstm-sentiment.ipynb` | Same path | IMDb replaces Chinese reviews; English regex tokenizer; packed sequences; negative/positive labels |
| `03-sentiment-analysis/paddle/notebooks/01-nlp-overview.ipynb` | Same path | English tasks and examples |
| `03-sentiment-analysis/paddle/notebooks/02-word-embeddings.ipynb` | Same path | English Word2Vec → Paddle Embedding; no Chinese pretrained vectors |
| `03-sentiment-analysis/paddle/notebooks/03-lstm-sentiment.ipynb` | Same path | Same English dataset as PyTorch; Paddle LSTM with true sequence lengths |

The optional `03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb`
uses an SST-2-fine-tuned English DistilBERT model. It replaces the learning purpose of the
Chinese pretrained-model demonstrations. The Paddle route links to this optional lesson
and requires the PyTorch environment for it; no Chinese ERNIE model is loaded.

## Deliberate differences

- The English Paddle route uses core Paddle 3.3.1 rather than the original PaddleNLP 2.x
  dependency stack. Both language editions remain independent.
- Word-vector visualization uses an English-labeled PCA chart rather than requiring
  VisualDL/TensorBoard services for the introductory experiment.
- Custom digit data is not presented as LED-display data. It preserves the indexing,
  split, loading, training, and prediction learning objectives.
- Detection lecture notes are newly written English teaching notes, not translations
  of every historical log or shell transcript.
- Notebook outputs are saved from real local execution under uv and Python 3.12. Logs,
  figures, and predictions are visible on opening the files. No accuracy result is
  fabricated or copied from the original course.


## Shared current detection lesson

Both languages now use YOLO26n and the official melikeavan RPS v1 YOLO26 export. The Chinese lesson is `02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb` at the repository root; it shares the English detection environment and verified dataset but writes separate outputs. Format conversion and Xiaotudui Labs inspection are a [separate topic](../02-object-detection/dataset-formats/README.md).
