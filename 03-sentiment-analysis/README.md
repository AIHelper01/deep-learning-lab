# 中文情感分析

中文课程 · [English (default)](../english/03-sentiment-analysis/README.md) · [中文总览](../README.zh-CN.md)

学习顺序：NLP 基础 → 词向量 → LSTM 情感分类 →（可选）预训练模型对照。
先在一套框架里走完实验，再对照另一套实现。

- [PyTorch 路线](pytorch/README.md)：延续图像分类课的框架知识，另含可选的预训练模型课。
- [Paddle 路线](paddle/README.md)：同一实验的 PaddlePaddle 实现。

## 数据与分词：本课是真中文，不是翻译

- 数据集：ChnSentiCorp 中文酒店/影视评论，标签 `负面=0`、`正面=1`。
- 分词：jieba 词级切分，**不使用停用词表**（“不”“没”被删掉情感就会反过来）。
- 划分：官方 `train.tsv` 按标签各留 20% 作验证集；最终评估使用带标签的官方 `dev.tsv`。
  发行包里的 `test.tsv` 只有 `qid` 与文本、没有标签，本仓库不对无标签数据算准确率。
- 预处理与英文课程共用同一套接口：`../common/sentiment_cn.py` 提供
  `load_reviews / tokenize / build_vocab / encode / LABELS`，与
  `../english/common/course_data.py` 一一对应，因此两侧 notebook 的单元结构能够逐格对齐。

## 与英文课程的关系

`pytorch/notebooks/` 与 `paddle/notebooks/` 由 `../scripts/build_chinese_course.py` 从英文母本镜像生成：
单元数量与训练逻辑一致，中文讲解 + 中文控制台输出 + 中文图表；数据与分词按上面说明使用中文语料。
可选预训练课两侧各自如实命名：中文侧 `04-pretrained-chinese-sentiment.ipynb` 用京东评论二分类检查点，
英文侧 `04-pretrained-english-sentiment.ipynb` 用 SST-2 检查点，配对关系登记在 `scripts/check_parity.py` 的别名表。

两条路线共用 `data/`，产物分别写入 `outputs/pytorch/` 与 `outputs/paddle/`；不要在两个内核里同时跑数据准备。

历史版本保留在 [archive/legacy-notebooks/](pytorch/archive/legacy-notebooks/README.md)
（[Paddle 侧](paddle/archive/legacy-notebooks/README.md)，只读参考，不参与执行与校验）。
旧说明、混合依赖及锁文件在 `archive/environment/`，不用于新环境安装。

## 运行

```bash
~/env_dl_uv/.venv/bin/python ../english/scripts/execute_and_save.py --group pytorch --language zh-CN
~/env_dl_uv/.venv/bin/python ../english/scripts/execute_and_save.py --group paddle  --language zh-CN
~/env_dl_uv/.venv/bin/python ../scripts/embed_expected_outputs.py --module 03-sentiment-analysis
```

依赖 `paddlenlp` / `visualdl` 的只是归档里的历史 notebook；现行中文 Paddle 课只用到
`paddlepaddle` + `gensim`，在 `~/env_dl_uv` 中可直接运行。
