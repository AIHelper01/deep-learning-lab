# 深度学习-情感分析

本模块是「AI 原理速通」系列中深度学习方向的自然语言处理（NLP）入门项目，围绕**中文情感分析**任务，从 NLP 基础理论出发，逐步深入到词向量技术与 LSTM 实战，帮助你系统掌握文本分类的完整流程。

---

## 📌 项目简介

情感分析（Sentiment Classification）是 NLP 领域最经典的任务之一，目标是让机器自动判断一段文本的情感倾向（如正面、负面）。

本项目同时提供 **PaddlePaddle（飞桨）** 和 **PyTorch** 两个版本：
- **PaddlePaddle 版**：基于 `PaddleNLP` + `VisualDL`，使用 `ERNIE 3.0` 预训练模型
- **PyTorch 版**：基于 `torch` + `transformers`，使用 `BERT` 预训练模型，适合更习惯 PyTorch 生态的读者

两个版本的教学逻辑完全一致，均通过「理论 → 基础 → 实战」三步走，带你完成中文情感分类的完整流程。

---

## 📁 文件结构

```
2.3深度学习-情感分析/
├── 01_自然语言处理综述.ipynb                    # Paddle 版：NLP 概述
├── 11_自然语言处理综述-PyTorch版.ipynb          # PyTorch 版：NLP 概述
├── 02_词向量：迈向NLP领域的第1步台阶.ipynb       # Paddle 版：词向量原理与 PaddleNLP 实践
├── 12_词向量：迈向NLP领域的第1步台阶-PyTorch版.ipynb # PyTorch 版：gensim + torch.nn.Embedding 实践
├── 03_基于LSTM的情感分类实践.ipynb              # Paddle 版：LSTM 完整实战
├── 13_基于LSTM的情感分类实践-PyTorch版.ipynb    # PyTorch 版：Bi-LSTM + transformers 实战
├── requirements.txt                              # Python 依赖包列表（同时包含 Paddle 版与 PyTorch 版依赖）
└── vocab.json                                    # 基于 ChnSentiCorp 构建的中文词表
```

---

## 🗂️ 内容详解

### 01_自然语言处理综述.ipynb
- **NLP 的常见任务**：词级任务（切词、NER）、句子级任务（情感分析、文本相似度）、篇章级任务（阅读理解、对话系统）、自然语言生成（机器翻译、写作）
- **NLP 面临的挑战**：
  - **语言学角度**：同义词、情感倾向、歧义性、长文本处理、语言惯性表达
  - **计算角度**：自然语言是离散信号，如何将其有效编码为计算机可计算的向量表示

### 02_词向量：迈向NLP领域的第1步台阶.ipynb
- **词向量（Word Embedding）概述**：将离散词语映射为连续向量，使计算机能够计算语义
- **One-Hot Encoding**：最基础的文本编码方式及其局限性
- **word2vec 算法**：
  - **CBOW**：通过上下文预测中心词
  - **Skip-gram**：通过中心词预测上下文
- **PaddleNLP 词向量实践**：
  - 加载 `w2v.baidu_encyclopedia.target.word-word.dim300` 等预训练词向量
  - 检索词向量、计算词语余弦相似度
  - 使用 **JiebaTokenizer** 分词，计算句向量与句子间相似度
  - 使用 **VisualDL** 进行词向量可视化

### 03_基于LSTM的情感分类实践.ipynb
- **情感分析任务定义**：三分类（正向 / 负向 / 其他），以及更细粒度的 Aspect-Level 情感分析
- **核心挑战**：
  - 变长句子的规整化（截断 + Padding）
  - 词序敏感的语义建模
- **两种实现方式**：
  1. **预训练模型快速体验**：使用 **ERNIE 3.0 Medium** 预训练模型直接进行情感分类预测
  2. **手动训练 LSTM 模型**：从零开始完成数据处理的完整流程
- **手动训练详细流程**：
  - **数据准备**：下载并加载 **ChnSentiCorp** 酒店评论数据集（训练集 9601 条 / 验证集 1201 条 / 测试集 1201 条）
  - **数据处理**：结巴分词 → 构建词表（`vocab.json`）→ 文本转 ID → 组装 mini-batch（Padding + Stack）
  - **网络定义**：基于 `paddle.nn.LSTM` 构建 LSTMEncoder，使用 `paddlenlp.seq2vec` 进行文本向量表示
  - **模型训练**：定义损失函数、优化器，完成多轮迭代训练
  - **模型评估**：在验证集上评估模型效果
  - **模型预测**：对单条样本进行情感倾向预测

---

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| **PaddlePaddle 版** | |
| [PaddlePaddle](https://www.paddlepaddle.org.cn/) | 百度开源深度学习框架（建议 `2.6.x`） |
| [PaddleNLP](https://github.com/PaddlePaddle/PaddleNLP) | 飞桨自然语言处理库（**请务必使用 `2.x`，`3.x` 不兼容本项目**） |
| VisualDL | 飞桨可视化工具，用于词向量降维可视化 |
| **PyTorch 版** | |
| [PyTorch](https://pytorch.org/) | 开源深度学习框架 |
| [transformers](https://huggingface.co/docs/transformers) | Hugging Face 预训练模型库，提供 BERT 等中文模型 |
| [gensim](https://radimrehurek.com/gensim/) | 主题建模与文档相似度计算库，用于训练/加载 word2vec |
| TensorBoard | PyTorch 生态可视化工具 |
| **通用工具** | |
| jieba | 中文分词工具 |
| NumPy / Pandas | 数据处理能力 |

---

## 🚀 快速开始

### PaddlePaddle 版

**第一步：根据硬件环境安装 PaddlePaddle**

```bash
# NVIDIA GPU（Linux/Windows）
pip install paddlepaddle-gpu==2.6.2

# Mac（仅支持 CPU，包括 Intel / Apple Silicon）
pip install paddlepaddle==2.6.2
```

**第二步：安装剩余依赖并启动 Jupyter**

```bash
pip install -r requirements.txt
jupyter notebook
```

按顺序运行：
1. `01_自然语言处理综述.ipynb`
2. `02_词向量：迈向NLP领域的第1步台阶.ipynb`
3. `03_基于LSTM的情感分类实践.ipynb`

> ⚠️ **版本重要提示**：本项目基于 PaddleNLP 2.x 传统 API 编写（`paddlenlp.embeddings`、`paddlenlp.data` 等）。PaddleNLP 3.x 是大模型套件，已移除这些 API，会导致词向量和 LSTM 实战 Notebook 无法运行。请务必使用 `paddlenlp>=2.6,<3.0`。

### PyTorch 版

**第一步：根据硬件环境安装 PyTorch**

```bash
# 请访问 PyTorch 官网获取对应 CUDA 版本的安装命令
# https://pytorch.org/get-started/locally/

# Mac（Apple Silicon / CPU）示例
pip install torch
```

**第二步：安装剩余依赖并启动 Jupyter**

```bash
pip install -r requirements.txt
jupyter notebook
```

按顺序运行：
1. `11_自然语言处理综述-PyTorch版.ipynb`
2. `12_词向量：迈向NLP领域的第1步台阶-PyTorch版.ipynb`
3. `13_基于LSTM的情感分类实践-PyTorch版.ipynb`

> 💡 **建议**：如果你同时使用 NVIDIA GPU 和 Mac，推荐优先使用 **PyTorch 版**，跨平台兼容性更好。

---

## 📊 数据集说明

本项目使用的是开源中文情感分类数据集 **ChnSentiCorp**，主要来源于酒店评论，标注为：
- `1`：正面评价
- `0`：负面评价

数据集会在首次运行 `03` 系列的实战 Notebook 时自动下载并解压到 `DataSet/ChnSentiCorp/` 目录下。Paddle 版和 PyTorch 版均使用同一套数据集。

---

## 💡 学习要点

- 理解自然语言从**离散符号**到**连续向量**的转换本质
- 掌握 **word2vec**（CBOW / Skip-gram）的核心思想
- 熟悉中文 NLP 的完整数据处理流程：**分词 → 建表 → 编码 → Padding → Batch**
- 理解 **RNN / LSTM** 如何解决序列数据的时序依赖问题
- 了解预训练模型（如 **ERNIE** / **BERT**）在下游任务中的强大能力

---

## 📖 相关前置知识

建议先学习以下模块，再进入本项目：
- `2.1深度学习-图像分类/`：掌握深度学习基础与 PaddlePaddle 框架使用
- `2.2深度学习-目标检测/`：了解更复杂的深度学习模型结构

---

> 本项目为教学演示用途，代码与注释均经过精心编排，适合 NLP 初学者系统学习中文情感分析的完整技术链路。
