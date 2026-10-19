# English sentiment analysis

[Chinese course](../../03-sentiment-analysis/README.md) · [Project](../README.md)

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

The Chinese lessons in `03-sentiment-analysis/` pair one file per file with these notebooks. The
repository rule makes the Chinese side the master, while this module's generator
(`scripts/build_chinese_course.py`) still keys on the English text - see the Migration status section
of `AGENTS.md`. The Chinese route is not a
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
uv run python english/scripts/execute_and_save.py --group pytorch
uv run python english/scripts/execute_and_save.py --group paddle
uv run python scripts/embed_expected_outputs.py --module 03-sentiment-analysis
```

[Dataset provenance](../docs/datasets.md) · [Environment setup](../docs/environment-setup.md)

