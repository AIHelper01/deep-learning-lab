# IMDb English sentiment data

**Source:** [Stanford Large Movie Review Dataset](https://ai.stanford.edu/~amaas/data/sentiment/) · [Archive](https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz).

English movie reviews support positive/negative sentiment classification, Word2Vec, and LSTM lessons. Both PyTorch and Paddle share the same prepared records: `0=negative`, `1=positive`. The source unlabeled portion is not used.

Run an embeddings or LSTM notebook to download and prepare data. `common/course_data.py` removes HTML, exact text duplicates, CJK-containing text, and empty English token sequences; validation comes from source training data with seed 42. Vocabulary is fitted on training text only. Classroom runs use balanced subsets; consult notebook limits and provenance for actual counts.

Local files are `data/imdb/train.jsonl`, `validation.jsonl`, `test.jsonl`, the downloaded archive, and `provenance.json` under this module. Keep the archive README and cite Maas et al. (2011). Chinese ChnSentiCorp data and vocabularies are separate.

See the [dataset catalog](../../../docs/datasets.md#imdb) and [preparation details](../../docs/datasets.md#english-sentiment-analysis). Pretrained DistilBERT is a separate model resource; it does not replace the IMDb training data. Data files are excluded from Git.
