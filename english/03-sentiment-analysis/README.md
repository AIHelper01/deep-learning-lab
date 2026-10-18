# English sentiment analysis

Learning order: NLP basics -> word embeddings -> LSTM sentiment classification -> optional pretrained
model. Choose [PyTorch](pytorch/README.md) or [Paddle](paddle/README.md) and complete all three
lessons in that route. Compare frameworks only after understanding the experiment.

Both routes use English IMDb movie reviews, the same deterministic data splits, the same
English tokenizer, and `negative=0`, `positive=1`. Framework outputs and weights are separate.
Chinese segmentation, Chinese word vectors, and the original vocabulary are not used.

## Data and tokenizer: real English data, not a translation

Raw/prepared reviews live under data/. Experiment artifacts live under outputs/pytorch/
and outputs/paddle/. Do not run dataset preparation concurrently from both kernels.

The optional pretrained-model lesson uses the PyTorch environment and an English SST-2
checkpoint. It is a separate inference demonstration, not a substitute for training LSTM.

## Relationship to the Chinese course

These notebooks are the masters of the Chinese lessons in `03-sentiment-analysis/`;
`scripts/build_chinese_course.py` mirrors them cell by cell. The Chinese route is not a
translation of IMDb: it trains on ChnSentiCorp Chinese reviews segmented with jieba through
`common/sentiment_cn.py`, which keeps this course's loader interface, and its optional
pretrained lesson uses a Chinese checkpoint fine-tuned on JD shopping reviews. The name
difference is deliberate and recorded as an alias in `scripts/check_parity.py`.

Superseded Chinese notebooks are archived under each route's
`archive/legacy-notebooks/` (reference only, never executed).

## Run

Open one route and run its notebooks top to bottom, or execute a whole lesson from the command line and
keep its real output:

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group pytorch
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group paddle
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 03-sentiment-analysis
```

[Dataset provenance](../docs/datasets.md) · [Environment setup](../docs/environment-setup.md)

