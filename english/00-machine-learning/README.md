# Machine learning (Titanic survival)

English course · derived mirror of the Chinese master [`00-machine-learning/`](../../00-machine-learning/README.md) · [English overview](../README.md)

An introductory classical machine-learning lesson. One notebook walks through a complete project on the
same `~/env_dl_uv` kernel the other lessons use: data preparation, EDA, preprocessing and feature
engineering, six classical classifiers plus XGBoost/LightGBM, GridSearchCV tuning, pickle/joblib/ONNX
model export, and a reusable Pipeline workflow.

- Lesson: [`notebooks/01_Titanic-Case.ipynb`](notebooks/01_Titanic-Case.ipynb). Every code cell is followed
  by an "Expected output" block quoting a real run, with figures in `assets/`.
- Data (not in Git): `titanic/LabeledData.csv` (891 training rows) and `titanic/UnlabeledData.csv`
  (418 test rows), the Kaggle [Titanic](https://www.kaggle.com/c/titanic/data) competition files. These are
  byte-identical to the Chinese master's copies (same SHA-256):
  `LabeledData.csv` `4a437fde05fe5264e1701a7387ac6fb75393772ba38bb2c9c566405af5af4bd7`,
  `UnlabeledData.csv` `42c12d055fa9edbcb63a735f6501754dcc3192b95834d2f0b25ca847069e9688`.
- Run (from the repository root; the notebook reads `titanic/` and writes `models/` and `result/`
  relative to the **module** directory, hence `--cwd module`):

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group ml --cwd module
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 00-machine-learning
```

- Generated at run time and kept out of Git: `models/*.pkl` / `models/*.onnx`, `result/Submission.csv`,
  `Submission_SVM_Pipeline.csv`, `tmp.csv`.
- `assets/reference-*.png` are screenshots of the interactive gradient-descent and
  classification-threshold teaching tools the prose refers to; see `assets/README.md`.

## Editing

Do not hand-edit this mirror. Edit the Chinese master
[`00-machine-learning/notebooks/01_Titanic-Case.ipynb`](../../00-machine-learning/notebooks/01_Titanic-Case.ipynb),
then regenerate this side:

```bash
~/env_dl_uv/.venv/bin/python scripts/build_english_course.py --force   # Chinese master -> English mirror
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group ml --cwd module
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 00-machine-learning
```

`scripts/titanic_en.py` holds the English translation tables and is keyed on exact Chinese source text, so a
master edit that is not mirrored there fails the build instead of leaving stale English prose.
