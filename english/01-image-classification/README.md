# Image classification

1. [LeNet on MNIST](notebooks/01-lenet-mnist.ipynb)
2. [LeNet on CIFAR-10](notebooks/02-lenet-cifar10.ipynb)
3. [ResNet18 on CIFAR-10](notebooks/03-resnet-cifar10.ipynb)
4. [Custom image folders](notebooks/extensions/04-lenet-custom-data.ipynb)

[Compact MNIST comparison](archive/01-lenet-mnist-copy1.ipynb) is optional.
Superseded Chinese notebooks are archived in [archive/legacy-notebooks/](archive/legacy-notebooks/README.md).

Each main experiment covers data inspection, model definition, training, checkpoint
selection, evaluation, and inference. The custom-folder experiment also writes CSV indexes.
Outputs are separated by experiment name. Use validation data for model selection; hold
test data back for final evaluation. The default short runs prioritize teaching flow.

## Relationship to the Chinese course

These four notebooks are the masters of the Chinese lessons in `01-image-classification/`:
`scripts/build_chinese_course.py` mirrors them cell by cell, translating only narration,
console text, plot labels and class names. Change the master, then regenerate the mirror.

The custom-folder lesson exports MNIST into `train/zero`, `train/one`, ... folders; the
original LEDNUM collection has no verified public download, so the lesson teaches folder
indexing and does not claim LED-domain accuracy. Folder names stay ASCII; the Chinese
mirror maps them to Chinese display labels.

## Data and outputs

- `data/MNIST/raw/`: original MNIST (also downloaded automatically on first run).
- `data/cifar10/`: CIFAR-10, downloaded on first run, or copied from the DataSet staging area as
  described in `data/README.md`.
- `data/custom-digits-balanced/`: the `train/<class>` folders the custom-folder lesson exports from
  MNIST; the script creates them.
- `assets/`: figures referenced by the `**Expected output:**` blocks inside the notebooks.
- `outputs/<experiment>/`: weights, curves, confusion matrices and `metrics.json`.

Data and experiment products stay out of Git.

## Run

Open a notebook and run it top to bottom, or execute a whole lesson and keep its real output:

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification
```

[Environment setup](../docs/environment-setup.md) · [Data and provenance](../docs/datasets.md)

