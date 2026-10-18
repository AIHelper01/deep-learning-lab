# ChnSentiCorp 中文情感数据

**来源**：[PaddleNLP 数据集实现与字段定义](https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/datasets/chnsenticorp.py) · [下载压缩包](https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip)。

中文评论二分类，用于词向量、文本预处理与 LSTM 教学。课程解释标签为 `0=负面`、`1=正面`。Paddle 与 PyTorch 路线共用 `data/ChnSentiCorp.zip` 和 `data/ChnSentiCorp/`，由 Notebook 下载解压，不要同时运行两套解压步骤。

数据是带表头 TSV：训练为 `label,text`，验证为 `qid,label,text`，该发行包测试为 `qid,text`，没有真实标签。实际数量应按下载文件统计；核对解压层级和 Notebook 路径。无标签测试预测不能计算准确率，应选用带标签的评估划分。

保留源包声明，加载器的软件许可不等于评论数据许可。详细说明见[中文数据集介绍](../../docs/datasets.zh-CN.md)。[英文课程](../../english/docs/datasets.md#english-sentiment-analysis)改用 IMDb，词表与缓存独立。数据文件不提交到 Git。

## 从 DataSet 拉取（cp 方式）

```bash
# 已解压目录（Notebook 直接读取 data/ChnSentiCorp/）
cp -r /workspace/DataSet/nlp/ChnSentiCorp/ChnSentiCorp data/
# 或原始压缩包（Notebook 首次运行时自行解压）
cp /workspace/DataSet/nlp/ChnSentiCorp/ChnSentiCorp.zip data/
```

## 下载方式

`curl -LO https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip`，解压到 `data/`；核对解压层级应为 `data/ChnSentiCorp/{train,dev,test}.tsv`（扁平一层，不要多包一层目录）。校验记录见 `/workspace/DataSet/nlp/DOWNLOAD.md`。
