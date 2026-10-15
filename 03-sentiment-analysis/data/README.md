# 情感分析数据

| 数据 | 获取地址 | 落地路径 |
|---|---|---|
| ChnSentiCorp 中文情感语料 | <https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip>，Notebook 自动下载并解压 | `data/ChnSentiCorp.zip` 与 `data/ChnSentiCorp/` |

Paddle 与 PyTorch 两条路线共用同一份 ChnSentiCorp。英文版改用 IMDb 英文评论，见 [english/docs/datasets.md](../../english/docs/datasets.md)。数据体积大，`.gitignore` 已排除 `data/` 下除本文件外的全部内容。
