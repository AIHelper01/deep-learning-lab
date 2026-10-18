# 中文情感分析

中文课程 · [English (default)](../english/03-sentiment-analysis/README.md) · [中文总览](../README.zh-CN.md)

学习顺序：NLP 基础 → 词向量 → LSTM 情感分类。选择一套框架完成全部实验，再对照另一套实现。

- [PyTorch 路线](pytorch/README.md)：延续图像分类的框架知识。
- [Paddle 路线](paddle/README.md)：PaddleNLP 与 VisualDL 实践。

两条路线独立配置环境，原始评论数据共用 data/；产物分别写入 outputs/pytorch/ 与 outputs/paddle/。不要同时运行两套数据下载和解压流程，以免互相影响。

assets/vocab-reference.json 为迁入词表，仅作参考；Paddle 实验重新生成的词表放入 outputs/paddle/。两套 NLP 概述 Notebook 原样保留，避免此次目录整理改变课程内容。

旧说明、混合依赖及锁文件保存在 archive/environment/，不用于新环境安装。BERT/ERNIE 示例与 LSTM 训练属于不同实验。历史 Paddle pir 报错未在本次复现，当前不能标记为已修复。
