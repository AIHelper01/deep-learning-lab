# Archived upstream environment

The original sentiment module shipped one dependency set that mixed both frameworks, plus the Chinese
`vocab.json` built from ChnSentiCorp. Those files are preserved byte-for-byte in the Chinese course at
`../../../../03-sentiment-analysis/archive/environment/` and are deliberately **not** duplicated here.

They are not used by this course. The PyTorch and Paddle notebooks each run on their own locked uv project
(`../../pytorch/` and `../../paddle/`); see [environment setup](../../../docs/environment-setup.md).
The archived notes still record the upstream constraint `paddlenlp>=2.6,<3.0`: PaddleNLP 3.x removed
`paddlenlp.embeddings` and `paddlenlp.data`, which is why the archived lesson cannot run on the current
Paddle 3 stack.
