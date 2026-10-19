# PyTorch English NLP route

1. [NLP overview](notebooks/01-nlp-overview.ipynb)
2. [Word embeddings](notebooks/02-word-embeddings.ipynb)
3. [LSTM sentiment classification](notebooks/03-lstm-sentiment.ipynb)

Use this directory's requirements.txt in an independent environment (on macOS/Linux the
verified single environment `~/env_dl_uv` runs both routes). The two routes share English
IMDb data but keep outputs separate. See [setup](../../docs/environment-setup.md).

The Chinese route in `03-sentiment-analysis/pytorch/` pairs cell by cell with these notebooks. The
Chinese side is the master by repository rule, while this module's generator still keys on the English
text (see the Migration status section of `AGENTS.md`). The Chinese route trains on ChnSentiCorp
Chinese reviews segmented with jieba. Superseded Chinese notebooks stay in
`archive/legacy-notebooks/` for reference.

The optional [pretrained English transformer](../pytorch/notebooks/04-pretrained-english-sentiment.ipynb)
uses the PyTorch environment, including when following the Paddle route.
