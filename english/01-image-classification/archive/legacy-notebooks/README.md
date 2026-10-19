# Legacy Chinese notebooks (read-only archive)

These are the repository's early Chinese notebooks for the vision classification module. They are
archived because:

- their cell structure does not line up with the rebuilt course notebooks, so they cannot be aligned
  cell by cell;
- their directory convention differs from the course notebooks: they resolve `../data`, `../outputs`
  and `../../assets` from their own directory, while course notebooks run from the course root;
- some cells depend on assets from the old training server that never entered the repository (below).

The notebooks themselves sit on the Chinese side only; the English course never had these early
versions, which is why this directory holds just this README. The current Chinese course lives in
`../../../../01-image-classification/notebooks/` and pairs one file per file with the English lessons
here (enforced by `scripts/check_parity.py`); the Migration status section of
`../../../../AGENTS.md` records which side currently keys the other.

## Re-running them in the locked environment (opt-in)

This directory takes part in neither default course execution nor the
`english/scripts/verify_saved_outputs.py` audit. To reproduce one, opt in with `--include-legacy`
plus `--cwd notebook`, from the repository root:

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN \
    --cwd notebook --include-legacy --notebook legacy-notebooks/02-lenet-cifar10.ipynb
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification \
    --include-archive --include-legacy --notebook legacy-notebooks/02-lenet-cifar10.ipynb
```

Embedding runs straight after execution and appends one `course-expected-output` markdown cell per
code cell: text is quoted verbatim, figures are exported into this directory's `assets/` (stem plus
counter) and linked by relative path, so the recorded run stays visible after
*Kernel -> Clear All Outputs*.

## Per-notebook status (2026-10-19, `~/env_dl_uv`: Python 3.12.12 + PyTorch 2.14.1, Apple Silicon MPS)

| Notebook | Status | Details |
| --- | --- | --- |
| `01-lenet-mnist.ipynb` | executed, outputs embedded | full MNIST, 3 epochs, 66.73 s, best test 98.32%, single-image prediction 5 |
| `02-lenet-cifar10.ipynb` | executed, outputs embedded | CIFAR-10, 3 epochs, 32.81 s, test 57.23%, single-image prediction aeroplane 0.789 |
| `03-resnet-cifar10.ipynb` | executed, outputs embedded | ResNet18 (ImageNet pretrained) + CIFAR-10 at 224x224, 3 epochs, 3897.96 s, test 93.68% (the "flashy" variant retrains 3 epochs, best validation 91.91%); the closing cell that loads the old server checkpoint is skipped |
| `extensions/04-lenet-custom-data.ipynb` | sections 1-2 executed, outputs embedded | full MNIST, 3 epochs, 58.62 s, test 97.66% ("flashy" variant best validation 97.07%), single-image prediction 5; section 3 "train your own data" is skipped because LEDNUM is missing |

Both skips are genuinely missing assets, not a misconfigured environment:

- `03-resnet-cifar10.ipynb` ends its "flashy version" by loading
  `models/resnet18_cifar10/best_model/..._acc_93.05.pth`, a checkpoint trained on the old server that
  never entered this repository and is not in the asset folders either;
- section 3 of `extensions/04-lenet-custom-data.ipynb` needs the LED digit images under
  `../../data/LEDNUM/`; on the old machine only `DOWNLOAD.md` survived, and there is no verifiable
  public download (see `docs/datasets.zh-CN.md`). The current lesson
  `../../../../01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb` teaches the same
  custom `Dataset` plus `train.txt` index technique on the downloadable `data/custom-digits-balanced`
  export instead.

Once the missing assets are in place, rerun the commands above to clear the skips; skipped cells carry
the `skip-execution` tag, so the runner leaves them untouched.

Use `git log --follow <path>` to inspect their history.
