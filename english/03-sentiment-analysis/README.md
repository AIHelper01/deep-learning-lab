# English sentiment analysis

Choose [PyTorch](pytorch/README.md) or [Paddle](paddle/README.md) and complete all three
lessons in that route. Compare frameworks only after understanding the experiment.

Both routes use English IMDb movie reviews, the same deterministic data splits, the same
English tokenizer, and `negative=0`, `positive=1`. Framework outputs and weights are separate.
Chinese segmentation, Chinese word vectors, and the original vocabulary are not used.

Raw/prepared reviews live under data/. Experiment artifacts live under outputs/pytorch/
and outputs/paddle/. Do not run dataset preparation concurrently from both kernels.

The optional pretrained-model lesson uses the PyTorch environment and an English SST-2
checkpoint. It is a separate inference demonstration, not a substitute for training LSTM.

[Dataset provenance](../docs/datasets.md) · [Environment setup](../docs/environment-setup.md)

