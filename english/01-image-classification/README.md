# Image classification

[Chinese course](../../01-image-classification/README.md) · [Project](../README.md)

1. [LeNet on MNIST](notebooks/01-lenet-mnist.ipynb)
2. [LeNet on CIFAR-10](notebooks/02-lenet-cifar10.ipynb)
3. [ResNet18 on CIFAR-10](notebooks/03-resnet-cifar10.ipynb)
4. [Custom image folders](notebooks/extensions/04-lenet-custom-data.ipynb)

[Compact MNIST comparison](archive/01-lenet-mnist-copy1.ipynb) is optional.
Superseded Chinese notebooks are archived in [archive/legacy-notebooks/](archive/legacy-notebooks/README.md).
The comparison notebook is archived but is executed in the course environment and carries its own
`**Expected output:**` blocks. Unlike the lessons above, it runs from the notebook's own directory
(`--cwd notebook`), and its blocks are refreshed with `--include-archive`. The legacy lessons stay out of
default course runs and output verification; `--include-legacy` re-executes them with the same
`--cwd notebook` convention and quotes each run back into its notebook, except for the cells tagged
`skip-execution` because their assets (an old server-side checkpoint, the LEDNUM images) never entered the
repository. See that README for the per-notebook status.

Each main experiment covers data inspection, model definition, training, checkpoint
selection, evaluation, and inference. The custom-folder experiment also writes CSV indexes.
Outputs are separated by experiment name. Use validation data for model selection; hold
test data back for final evaluation. The default short runs prioritize teaching flow.

## Relationship to the Chinese course

The repository rule is that the Chinese lessons are the masters and this side is the derived mirror
(see `AGENTS.md`): the tables in
`scripts/build_chinese_course.py` (data file `scripts/course_en.py`) key on the Chinese text and
derive these notebooks from the Chinese lessons. Both sides match cell by cell and differ only in narration, console text, plot
labels and class names. Before editing a lesson, read the Migration status section of `AGENTS.md` and
do not regenerate either side from the wrong direction.

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
uv run python english/scripts/execute_and_save.py --group vision
uv run python scripts/embed_expected_outputs.py --module 01-image-classification
```

The archived comparison notebook is refreshed separately:

```bash
uv run python english/scripts/execute_and_save.py --group vision --cwd notebook --notebook 01-lenet-mnist-copy1
uv run python scripts/embed_expected_outputs.py --module 01-image-classification --include-archive --notebook 01-lenet-mnist-copy1
```

[Environment setup](../docs/environment-setup.md) · [Data and provenance](../docs/datasets.md)
