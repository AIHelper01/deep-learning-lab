# PyTorch 情感分析路线

1. [自然语言处理综述](notebooks/01-nlp-overview.ipynb)
2. [词向量](notebooks/02-word-embeddings.ipynb)
3. [LSTM 情感分类](notebooks/03-lstm-sentiment.ipynb)
4. [可选：已微调的中文情感模型](notebooks/04-pretrained-chinese-sentiment.ipynb)：京东评论二分类检查点，跨领域对照；走 Paddle 路线时用 PyTorch 环境运行这一本。

在 notebook 里以 `notebooks/` 为工作目录顺序运行即可：数据在 `../../data/`，产物写入
`../../outputs/pytorch/`。数据是 ChnSentiCorp 中文评论，分词用 jieba（详见[模块说明](../README.md)）。
首次运行会下载数据集；可选预训练课会下载中文检查点。

命令行整本执行并保留真实输出：

```bash
uv run python ../../../english/scripts/execute_and_save.py --group pytorch --language zh-CN
uv run python ../../../scripts/embed_expected_outputs.py --module 03-sentiment-analysis
```

本路线与 `../../english/03-sentiment-analysis/pytorch/notebooks/` 逐单元对应，训练逻辑一致；两侧以哪一侧充当翻译来源，见 `../../AGENTS.md` 的 Migration status。
[环境准备](../../docs/environment-setup.zh-CN.md) · [数据获取](../../docs/datasets.zh-CN.md)
历史版本在 [archive/legacy-notebooks/](archive/legacy-notebooks/README.md)，只读参考。
