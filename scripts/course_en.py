#!/usr/bin/env python3
"""中文母本 -> 英文镜像的译文表（`scripts/build_chinese_course.py` 的数据文件）。

课程方向：仓库根的中文课件是母本，`english/` 的视觉与 NLP 镜像由本表的译文派生。
键是中文母本里的精确原文（Markdown 取单元首行、代码取去掉缩进后的整行）；
母本一改而本表没跟上，构建直接报错，不会静默留下过期英文；本表里没用上的条目同样报错。

- `BOOT_BLOCK`：中文课程引导单元 -> 英文课程引导单元（整元替换）。
- `FONT_BLOCK_LINES`：中文课件注入的字体三行；英文侧删除，命中一次即算使用。
- `MD_EN` / `MD_EN_BY_FILE`：含中文的 Markdown 单元 -> 英文原文（整元译文）。
- `LINE_EN` / `LINE_EN_BY_FILE`：母本与英文行不一致的代码行 -> 英文行（保留缩进）。
  同一中文行在不同课程里译法不同时（如训练日志行），文件级表优先。
- `BLOCKS_EN_BY_FILE`：行数不同的结构性单元（数据集/类别名语言不同），整元精确替换。

用 `uv run python scripts/build_chinese_course.py --check` 校验；不加参数则同步英文镜像。
"""

BOOT_BLOCK = {
    "from pathlib import Path\nimport os\nimport sys\n\n# 不依赖当前工作目录，向上找到中文课程根目录。\nstart = Path.cwd().resolve()\nCOURSE = next((p for p in [start, *start.parents]\n               if (p / \"CHINESE_COURSE_ROOT\").is_file()), None)\nif COURSE is None:\n    raise RuntimeError(\"请在项目根目录（中文课程）中启动 Jupyter。\")\nENGLISH = COURSE / \"english\"\n# 中文专用模块在仓库根 common/，与英文课程共享的数据与检测模块在 english/common。\nsys.path.insert(0, str(ENGLISH / \"common\"))\nsys.path.insert(0, str(COURSE / \"common\"))\n# 模型权重缓存与英文课程共用一份，避免同一份权重重复下载。\nos.environ.setdefault(\"HF_HOME\", str(ENGLISH / \"data\" / \"huggingface\"))\nos.environ.setdefault(\"TORCH_HOME\", str(ENGLISH / \"data\" / \"torch-cache\"))": "from pathlib import Path\nimport os\nimport sys\n\n# Find the English course root without relying on a specific working directory.\nstart = Path.cwd().resolve()\nCOURSE = next((p for p in [start, *start.parents]\n               if (p / \"COURSE_ROOT\").is_file()), None)\nif COURSE is None and (start / \"english\" / \"COURSE_ROOT\").is_file():\n    COURSE = start / \"english\"\nif COURSE is None:\n    raise RuntimeError(\"Start Jupyter inside the project or the english directory.\")\nsys.path.insert(0, str(COURSE / \"common\"))\nos.environ.setdefault(\"HF_HOME\", str(COURSE / \"data\" / \"huggingface\"))\nos.environ.setdefault(\"TORCH_HOME\", str(COURSE / \"data\" / \"torch-cache\"))",
}

FONT_BLOCK_LINES = [
    "from course_zh import setup_chinese_fonts",
    "setup_chinese_fonts(plt)",
    "print(\"图表中文字体：\", setup_chinese_fonts(plt))",
]

MD_EN = {
    "# LeNet：手写数字识别": "# LeNet: handwritten digit classification\n\n**Learning outcomes:** prepare a reproducible dataset, inspect tensor shapes,\ntrain a classifier, select a checkpoint using validation data, and evaluate on\na separate test set. All class names and plots in this edition are in English.\n\nRun cells from top to bottom. The first dataset/model download requires internet.\nCPU mode works; set `COURSE_SMOKE=1` before starting the kernel for a short pipeline check.\nA smoke-test score is not a measure of model quality.",
    "## 1. 准备训练集、验证集和测试集": "## 1. Prepare training, validation, and test data\n\nKeep the official test split untouched until final evaluation. Create validation\ndata only from the training split. The fixed seed controls the split. A classroom\nrun uses a subset to keep runtime manageable; increase limits for a fuller experiment.",
    "## 2. 定义模型": "## 2. Define the model\n\nA convolution learns local features with shared weights. Pooling reduces spatial\nsize; the final linear layer returns one logit per class. Cross-entropy expects\nlogits, so softmax is used only when displaying prediction probabilities.",
    "## 3. 训练并挑选检查点": "## 3. Train and select a checkpoint\n\nTraining enables gradients and updates parameters. Evaluation disables gradients\nand switches dropout/batch normalization to evaluation behavior. Save the checkpoint\nwith the highest validation accuracy; never choose it using test accuracy.",
    "## 4. 评估已保存的检查点": "## 4. Evaluate the saved checkpoint",
    "## 5. 观察错误样本并对单张图片做预测": "## 5. Inspect errors and predict one image",
    "## 练习与讨论": "## Exercises and discussion\n\n1. Predict each tensor shape before running the model.\n2. Compare learning rates while keeping the split fixed.\n3. Explain why validation and test results can differ.\n4. Inspect misclassified examples before increasing model size.\n5. For a new image, apply exactly the evaluation preprocessing and class mapping.\n\nThe model weights, class names, seed, and metrics are stored under this experiment's\noutput directory. Results depend on the subset, hardware, and training duration.",
    "# LeNet：CIFAR-10 图像分类": "# LeNet: CIFAR-10 image classification\n\n**Learning outcomes:** prepare a reproducible dataset, inspect tensor shapes,\ntrain a classifier, select a checkpoint using validation data, and evaluate on\na separate test set. All class names and plots in this edition are in English.\n\nRun cells from top to bottom. The first dataset/model download requires internet.\nCPU mode works; set `COURSE_SMOKE=1` before starting the kernel for a short pipeline check.\nA smoke-test score is not a measure of model quality.",
    "# ResNet18：在 CIFAR-10 上做迁移学习": "# ResNet18: transfer learning on CIFAR-10\n\n**Learning outcomes:** prepare a reproducible dataset, inspect tensor shapes,\ntrain a classifier, select a checkpoint using validation data, and evaluate on\na separate test set. All class names and plots in this edition are in English.\n\nRun cells from top to bottom. The first dataset/model download requires internet.\nCPU mode works; set `COURSE_SMOKE=1` before starting the kernel for a short pipeline check.\nA smoke-test score is not a measure of model quality.",
    "### 用 ResNet18 做迁移学习": "### Transfer learning with ResNet18\n\nResidual connections add an identity shortcut to learned transformations.\nThis lesson freezes the pretrained backbone and trains a new ten-class head.\nBatch-normalization statistics also stay fixed. Use ImageNet normalization;\ninput images are resized to 224 by 224. A smoke run uses random weights and\ncannot demonstrate transfer-learning performance.",
    "# 用 ImageFolder 做自定义手写数字分类": "# Custom digit classification with ImageFolder\n\n**Learning outcomes:** prepare a reproducible dataset, inspect tensor shapes,\ntrain a classifier, select a checkpoint using validation data, and evaluate on\na separate test set. All class names and plots in this edition are in English.\n\nRun cells from top to bottom. The first dataset/model download requires internet.\nCPU mode works; set `COURSE_SMOKE=1` before starting the kernel for a short pipeline check.\nA smoke-test score is not a measure of model quality.",
    "## 1. 构造属于自己的文件夹数据集": "## 1. Build your own folder dataset\n\nThe original custom-data lesson requires an unavailable LEDNUM collection.\nHere we preserve the custom digit-classification workflow by exporting MNIST\nto `train/zero`, `train/one`, ... folders. This is handwritten-digit data, not\nLED-display data; it demonstrates dataset indexing, not LED-domain accuracy.\nReal custom images can replace these files if the same split and class layout\nis retained. Split by writer/source when multiple images share an origin.",
    "# 自然语言处理：中文入门": "# Natural Language Processing: an English-language introduction\n\n**Learning outcomes:** distinguish NLP tasks, explain tokenization and ambiguity,\nand define a binary sentiment-classification experiment.\n\n| Task | English example | Output |\n|---|---|---|\n| Sentiment analysis | \"The film was surprisingly good.\" | positive |\n| Named-entity recognition | \"Alex visited London.\" | person, location |\n| Semantic similarity | \"A lovely film\" / \"An excellent movie\" | similarity score |\n| Question answering | \"Who directed the film?\" | an answer span |\n| Text generation | \"Write a short review.\" | generated text |",
    "## 语言为什么难": "## Why language is difficult\n\n\"Not bad\" is not the same as \"bad\". \"Great, another delay\" may be sarcastic.\n\"The bank is closed\" needs context. Word order, negation, domain, and document\nlength all affect meaning. Positive and negative are dataset labels, not a\ncomplete description of every real review; mixed and neutral cases still exist.\n\nEnglish words are separated by spaces much of the time, but contractions,\npunctuation, and names still need a tokenization policy. This course preserves\napostrophes and negation using a small regular-expression tokenizer. Production\ntransformer models use their own subword tokenizer instead.",
    "## 本课程的实验": "## Our experiment\n\nWe use the [Stanford IMDb movie-review dataset](https://ai.stanford.edu/~amaas/data/sentiment/).\nLabels are `negative=0` and `positive=1`. A validation split is drawn from the\nofficial training data; the official test split is reserved for final evaluation.\nThe preparation code filters reviews containing CJK characters and removes exact\nduplicate text across splits, so prepared counts can differ from published counts.\n\nVocabulary construction and Word2Vec fitting use training text only. Validation\nand test words outside that vocabulary map to an unknown token. A pretrained\nsentiment model is an optional separate comparison, not the LSTM being trained.\n\n**Discuss:** How would you label a mixed review? Why should a negation word remain\nin the input? Why is accuracy on a tiny classroom subset not a benchmark result?",
    "# 词向量：从中文词到向量": "# Word embeddings: from English words to vectors\n\n**Learning outcomes:** compare one-hot vectors and dense embeddings, train Skip-gram\nvectors using training reviews only, and compute word/sentence similarity.\n\nOne-hot vectors identify words but do not express similarity. Word2Vec learns from\nnearby words: CBOW predicts a center word from context; Skip-gram predicts context\nfrom a center word. Similar context can make antonyms close, so cosine similarity\nis not a sentiment classifier. Small training subsets give unstable neighbors.",
    "## 1. 用训练集评论训练 Word2Vec": "## 1. Train Word2Vec on training reviews",
    "## 2. 把向量装进框架的嵌入层": "## 2. Load vectors into the framework's embedding layer\n\nThe row index is the token ID. We copy the learned vectors and freeze them for this\ndemonstration. In a downstream classifier you can choose to fine-tune them.",
    "## 3. 探索词与句子的相似度": "## 3. Explore word and sentence similarity",
    "## 4. 可视化一个投影": "## 4. Visualize a projection\n\nThis two-dimensional PCA projection is a lossy view of the embedding space.\nNearby points on the chart do not prove semantic equivalence.",
    "# 用双向 LSTM 做中文电影评论情感分类": "# English movie-review sentiment classification with a bidirectional LSTM\n\n**Learning outcomes:** build a vocabulary from training data, encode and pad reviews,\ntrain an order-sensitive model, select a validation checkpoint, and predict English labels.\n\nThis lesson uses IMDb movie reviews instead of Chinese hotel reviews. It uses an\nEnglish tokenizer rather than Chinese word segmentation. Both framework editions\nshare the same prepared data and label mapping, but have separate environments and outputs.",
    "## 1. 构建不泄漏测试信息的词表": "## 1. Build a vocabulary without test leakage\n\n`<pad>` is ID 0; `<unk>` is ID 1. Truncate very long reviews for the classroom\nexperiment and track true lengths. The vocabulary is fitted on training text only.\nDo not remove \"not\" or other negation words as stopwords.",
    "## 2. 定义模型与训练步骤": "## 2. Define the model and training step\n\nEmbedding maps IDs to vectors. A bidirectional LSTM summarizes the review in both\ndirections. Concatenated final states feed a two-class linear layer. Sequence lengths\nare passed to the recurrent computation so padding does not contaminate final states.\nGradient clipping limits unusually large updates.",
    "## 3. 训练并按验证准确率挑选检查点": "## 3. Train and select by validation accuracy",
    "## 4. 重新加载并在留出测试集上评估": "## 4. Reload and evaluate on held-out test reviews",
    "## 5. 预测新的中文评论": "## 5. Predict new English reviews",
    "# 可选：一个已经微调好的中文情感模型": "# Optional: an already fine-tuned English sentiment model\n\nUse the PyTorch environment. This checkpoint was fine-tuned on SST-2; it is not an\nuntrained classification head attached to a base language model. Its scores cannot\nbe substituted for the IMDb LSTM experiment. The first run downloads model files.",
    "## 讨论": "## Discuss\n\nWhat happens to a review longer than the model limit? How do movie-review and SST-2\nexamples differ? Why can a high confidence score still be wrong?\n\n[Model card and provenance](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).",
}

MD_EN_BY_FILE = {
    "03-sentiment-analysis/pytorch/notebooks/02-word-embeddings.ipynb": {
        "## 练习": "## Exercises\n\nCompare CBOW (`sg=0`) and Skip-gram (`sg=1`). Increase training data before interpreting\nneighbors. Test an unknown word and explain why it has no trained vector. Compare\nsentence averaging with an order-sensitive LSTM in the next lesson.",
    },
    "03-sentiment-analysis/pytorch/notebooks/03-lstm-sentiment.ipynb": {
        "## 练习": "## Exercises\n\nCompare a unidirectional and bidirectional model. Change the maximum length and\nmeasure truncation frequency. Inspect negation and mixed reviews. Keep all tuning\non the validation set. To reproduce predictions later, restore the vocabulary,\nmaximum length, architecture, class mapping, and weights together.\n\nFor an already fine-tuned English transformer, use the optional pretrained-model\nlesson in the PyTorch route. Its SST-2 training task differs from this IMDb experiment;\nits published scores are not this course's results.",
    },
    "03-sentiment-analysis/paddle/notebooks/02-word-embeddings.ipynb": {
        "## 练习": "## Exercises\n\nCompare CBOW (`sg=0`) and Skip-gram (`sg=1`). Increase training data before interpreting\nneighbors. Test an unknown word and explain why it has no trained vector. Compare\nsentence averaging with an order-sensitive LSTM in the next lesson.",
    },
    "03-sentiment-analysis/paddle/notebooks/03-lstm-sentiment.ipynb": {
        "## 练习": "## Exercises\n\nCompare a unidirectional and bidirectional model. Change the maximum length and\nmeasure truncation frequency. Inspect negation and mixed reviews. Keep all tuning\non the validation set. To reproduce predictions later, restore the vocabulary,\nmaximum length, architecture, class mapping, and weights together.\n\nFor an already fine-tuned English transformer, use the optional pretrained-model\nlesson in the PyTorch route. Its SST-2 training task differs from this IMDb experiment;\nits published scores are not this course's results.",
    },
}

LINE_EN = {
    "print(f\"计算设备：{DEVICE}；实验：{EXPERIMENT}；冒烟测试：{SMOKE}\")": "print(f\"Device: {DEVICE}; experiment: {EXPERIMENT}; smoke test: {SMOKE}\")",
    "CLASS_NAMES = [\"零\", \"一\", \"二\", \"三\", \"四\", \"五\", \"六\", \"七\", \"八\", \"九\"]": "CLASS_NAMES = [\"zero\", \"one\", \"two\", \"three\", \"four\", \"five\", \"six\", \"seven\", \"eight\", \"nine\"]",
    "print(\"批次形状：\", tuple(images.shape), \"标签形状：\", tuple(labels.shape))": "print(\"Batch shape:\", tuple(images.shape), \"Label shape:\", tuple(labels.shape))",
    "print(\"数据集划分规模：\", len(train_set), len(val_set), len(test_set))": "print(\"Split sizes:\", len(train_set), len(val_set), len(test_set))",
    "fig.suptitle(\"训练样本示例\")": "fig.suptitle(\"Training examples\")",
    "print(\"模型输出形状：\", tuple(model(torch.zeros(2, CHANNELS, IMAGE_SIZE, IMAGE_SIZE, device=DEVICE)).shape))": "print(\"Logit shape:\", tuple(model(torch.zeros(2, CHANNELS, IMAGE_SIZE, IMAGE_SIZE, device=DEVICE)).shape))",
    "f\"验证损失 {val_loss:.4f} | 验证准确率 {val_accuracy:.3f}\")": "f\"validation loss {val_loss:.4f} | validation accuracy {val_accuracy:.3f}\")",
    "print(f\"留出测试集准确率：{test_accuracy:.3f}\")": "print(f\"Held-out test accuracy: {test_accuracy:.3f}\")",
    "axes[0].plot(values[:, 0], label=\"训练集\")": "axes[0].plot(values[:, 0], label=\"Training\")",
    "axes[0].plot(values[:, 1], label=\"验证集\")": "axes[0].plot(values[:, 1], label=\"Validation\")",
    "axes[0].set(title=\"交叉熵损失\", xlabel=\"轮次\", ylabel=\"损失\")": "axes[0].set(title=\"Cross-entropy loss\", xlabel=\"Epoch\", ylabel=\"Loss\")",
    "axes[1].plot(values[:, 2], label=\"训练集\")": "axes[1].plot(values[:, 2], label=\"Training\")",
    "axes[1].plot(values[:, 3], label=\"验证集\")": "axes[1].plot(values[:, 3], label=\"Validation\")",
    "axes[1].set(title=\"分类准确率\", xlabel=\"轮次\", ylabel=\"准确率\")": "axes[1].set(title=\"Classification accuracy\", xlabel=\"Epoch\", ylabel=\"Accuracy\")",
    "xlabel=\"预测类别\", ylabel=\"真实类别\", title=\"测试集混淆矩阵\")": "xlabel=\"Predicted class\", ylabel=\"True class\", title=\"Test confusion matrix\")",
    "print(f\"错分样本：真实={CLASS_NAMES[true]}，预测={CLASS_NAMES[predicted]}\")": "print(f\"Misclassified example: true={CLASS_NAMES[true]}, predicted={CLASS_NAMES[predicted]}\")",
    "print(f\"预测结果：{CLASS_NAMES[prediction]} | 置信度：{probabilities[prediction]:.3f} | \"": "print(f\"Prediction: {CLASS_NAMES[prediction]} | confidence: {probabilities[prediction]:.3f} | \"",
    "f\"真实标签：{CLASS_NAMES[int(true_label)]}\")": "f\"true label: {CLASS_NAMES[int(true_label)]}\")",
    "CLASS_NAMES = [\"飞机\", \"汽车\", \"鸟\", \"猫\", \"鹿\", \"狗\", \"青蛙\", \"马\", \"船\", \"卡车\"]": "CLASS_NAMES = [\"airplane\", \"automobile\", \"bird\", \"cat\", \"deer\", \"dog\", \"frog\", \"horse\", \"ship\", \"truck\"]",
    "print(\"可训练参数量：\", sum(p.numel() for p in model.parameters() if p.requires_grad))": "print(\"Trainable parameters:\", sum(p.numel() for p in model.parameters() if p.requires_grad))",
    "from sentiment_cn import tokenize": "from course_data import tokenize",
    "examples = [\"我很喜欢这段表演，但结局令人失望。\",": "examples = [\"I loved the acting, but the ending was disappointing.\",",
    "\"这部电影一点也不差。\", \"真棒，又是一个能猜到的结局。\"]": "\"The movie isn't bad at all.\", \"Great, another predictable ending.\"]",
    "print(\"原文：\", text)": "print(\"Text:\", text)",
    "print(\"分词：\", tokenize(text))": "print(\"Tokens:\", tokenize(text))",
    "from sentiment_cn import load_reviews, tokenize, build_vocab, encode, LABELS": "from course_data import load_reviews, tokenize, build_vocab, encode, LABELS",
    "print(\"数据集划分规模：\", len(train_rows), len(validation_rows), len(test_rows))": "print(\"Split sizes:\", len(train_rows), len(validation_rows), len(test_rows))",
    "print(\"标签：\", LABELS)": "print(\"Labels:\", LABELS)",
    "print(\"词表规模：\", len(words), \"向量形状：\", vectors.shape)": "print(\"Vocabulary size:\", len(words), \"Vector shape:\", vectors.shape)",
    "word2vec.save(str(OUTPUT / \"chinese_word2vec.model\"))": "word2vec.save(str(OUTPUT / \"english_word2vec.model\"))",
    "example_word = \"酒店\" if \"酒店\" in word_to_id else words[0]": "example_word = \"movie\" if \"movie\" in word_to_id else words[0]",
    "print(f\"词向量“{example_word}”：形状={vector.shape}\")": "print(f\"Embedding for '{example_word}': shape={vector.shape}\")",
    "print(\"最相近的词：\", word2vec.wv.most_similar(example_word, topn=min(5, len(words)-1)))": "print(\"Nearest words:\", word2vec.wv.most_similar(example_word, topn=min(5, len(words)-1)))",
    "first = \"这部电影很好看，演技也十分出色。\"": "first = \"The movie was enjoyable and the acting was excellent.\"",
    "second = \"我喜欢这部片子，也喜欢里面的表演。\"": "second = \"I liked the film and its performances.\"",
    "print(\"句子相似度：\", cosine(sentence_vector(first), sentence_vector(second)))": "print(\"Sentence similarity:\", cosine(sentence_vector(first), sentence_vector(second)))",
    "print(\"可以对比“很好”和“不太好”：取平均向量会丢掉语序信息。\")": "print(\"Try comparing 'good' and 'not good'; average vectors can lose word order.\")",
    "axis.set(title=\"中文词向量：PCA 投影\", xlabel=\"第一主成分\",": "axis.set(title=\"English word vectors: PCA projection\", xlabel=\"Principal component 1\",",
    "ylabel=\"第二主成分\")": "ylabel=\"Principal component 2\")",
    "ids, length = encode(\"演技没什么说服力，但我倒是喜欢配乐。\", vocab, MAX_LENGTH)": "ids, length = encode(\"The acting wasn't convincing, but I liked the music.\", vocab, MAX_LENGTH)",
    "print(\"词表规模：\", len(vocab), \"真实长度：\", length)": "print(\"Vocabulary size:\", len(vocab), \"True length:\", length)",
    "print(\"前若干个 token ID：\", ids[:12])": "print(\"First token IDs:\", ids[:12])",
    "print(\"中文标签映射：\", dict(enumerate(LABELS)))": "print(\"English label mapping:\", dict(enumerate(LABELS)))",
    "print(f\"测试集准确率：{test_accuracy:.3f}；测试集损失：{test_loss:.4f}\")": "print(f\"Test accuracy: {test_accuracy:.3f}; test loss: {test_loss:.4f}\")",
    "axis.plot(values[:, 2], label=\"训练集\")": "axis.plot(values[:, 2], label=\"Training\")",
    "axis.plot(values[:, 3], label=\"验证集\")": "axis.plot(values[:, 3], label=\"Validation\")",
    "axis.set(title=\"中文情感分类准确率\", xlabel=\"轮次\", ylabel=\"准确率\")": "axis.set(title=\"English sentiment classification\", xlabel=\"Epoch\", ylabel=\"Accuracy\")",
    "reviews = [\"这部电影非常精彩，表演也可圈可点。\",": "reviews = [\"The movie was wonderful and the acting was excellent.\",",
    "\"剧情很无聊，结局让人失望。\",": "\"The plot was boring and the ending was disappointing.\",",
    "\"本以为会讨厌它，结果竟然还不错。\"]": "\"I expected to hate it, but it was not bad at all.\"]",
    "print(\"预测是会出错的，尤其是在课堂这种短时训练之后。\")": "print(\"Predictions can be wrong, especially after a short classroom run.\")",
}

LINE_EN_BY_FILE = {
    "01-image-classification/notebooks/01-lenet-mnist.ipynb": {
        "print(f\"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | \"": "print(f\"Epoch {epoch + 1}/{EPOCHS} | train loss {train_loss:.4f} | \"",
    },
    "01-image-classification/notebooks/02-lenet-cifar10.ipynb": {
        "print(f\"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | \"": "print(f\"Epoch {epoch + 1}/{EPOCHS} | train loss {train_loss:.4f} | \"",
    },
    "01-image-classification/notebooks/03-resnet-cifar10.ipynb": {
        "print(f\"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | \"": "print(f\"Epoch {epoch + 1}/{EPOCHS} | train loss {train_loss:.4f} | \"",
    },
    "01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb": {
        "print(f\"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | \"": "print(f\"Epoch {epoch + 1}/{EPOCHS} | train loss {train_loss:.4f} | \"",
    },
    "03-sentiment-analysis/pytorch/notebooks/03-lstm-sentiment.ipynb": {
        "print(f\"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | \"": "print(f\"Epoch {epoch + 1}/{EPOCHS} | training loss {train_loss:.4f} | \"",
    },
    "03-sentiment-analysis/paddle/notebooks/03-lstm-sentiment.ipynb": {
        "print(f\"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | \"": "print(f\"Epoch {epoch + 1}/{EPOCHS} | training loss {train_loss:.4f} | \"",
    },
}

BLOCKS_EN_BY_FILE = {
    "01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb": {
        "DIGIT_CN = {\"zero\": \"零\", \"one\": \"一\", \"two\": \"二\", \"three\": \"三\", \"four\": \"四\",\n            \"five\": \"五\", \"six\": \"六\", \"seven\": \"七\", \"eight\": \"八\", \"nine\": \"九\"}\n# 文件夹名保持英文，ImageFolder 按字母序编号；下面的中文类别名按同一顺序对齐。\nCLASS_NAMES = [\"zero\", \"one\", \"two\", \"three\", \"four\", \"five\", \"six\", \"seven\", \"eight\", \"nine\"]\nCHANNELS, IMAGE_SIZE = 1, 28\nsource_train = datasets.MNIST(DATA, train=True, download=True)\nsource_test = datasets.MNIST(DATA, train=False, download=True)\nfolder = DATA / (\"custom-digits-balanced-smoke\" if SMOKE else \"custom-digits-balanced\")\nimport csv\n# Stable source indices keep exported train and validation images disjoint.\nfor split, source, start_index, end_index, per_class in [\n    (\"train\", source_train, 0, 50000, 6 if SMOKE else 200),\n    (\"validation\", source_train, 50000, 60000, 3 if SMOKE else 50),\n    (\"test\", source_test, 0, 10000, 3 if SMOKE else 50)]:\n    for name in CLASS_NAMES:\n        (folder / split / name).mkdir(parents=True, exist_ok=True)\n    rows = []\n    # Select every class explicitly, including in a tiny smoke run.\n    selected = []\n    for category in range(len(CLASS_NAMES)):\n        candidates = [i for i in range(start_index, end_index)\n                      if int(source.targets[i]) == category]\n        selected.extend(candidates[:per_class])\n    for index in selected:\n        image, label = source[index]\n        target = folder / split / CLASS_NAMES[label] / f\"digit_{index:05d}.png\"\n        if not target.exists():\n            image.save(target)\n        rows.append([target.relative_to(folder).as_posix(), CLASS_NAMES[label]])\n    with (folder / f\"{split}.csv\").open(\"w\", newline=\"\", encoding=\"utf-8\") as handle:\n        writer = csv.writer(handle)\n        writer.writerow([\"image_path\", \"label\"])\n        writer.writerows(rows)\n\ntransform = transforms.Compose([transforms.Grayscale(), transforms.ToTensor(),\n                                transforms.Normalize((0.1307,), (0.3081,))])\ntrain_set = datasets.ImageFolder(folder / \"train\", transform=transform)\nval_set = datasets.ImageFolder(folder / \"validation\", transform=transform)\ntest_set = datasets.ImageFolder(folder / \"test\", transform=transform)\n# ImageFolder 按文件夹名的字母顺序编号，不要假设按数字顺序排列。\nFOLDER_CLASSES = train_set.classes\nassert train_set.class_to_idx == val_set.class_to_idx == test_set.class_to_idx\nCLASS_NAMES = [DIGIT_CN[name] for name in FOLDER_CLASSES]\nprint(\"文件夹与类别编号映射：\", {DIGIT_CN[name]: index for name, index in train_set.class_to_idx.items()})": "CLASS_NAMES = [\"zero\", \"one\", \"two\", \"three\", \"four\", \"five\", \"six\", \"seven\", \"eight\", \"nine\"]\nCHANNELS, IMAGE_SIZE = 1, 28\nsource_train = datasets.MNIST(DATA, train=True, download=True)\nsource_test = datasets.MNIST(DATA, train=False, download=True)\nfolder = DATA / (\"custom-digits-balanced-smoke\" if SMOKE else \"custom-digits-balanced\")\nimport csv\n# Stable source indices keep exported train and validation images disjoint.\nfor split, source, start_index, end_index, per_class in [\n    (\"train\", source_train, 0, 50000, 6 if SMOKE else 200),\n    (\"validation\", source_train, 50000, 60000, 3 if SMOKE else 50),\n    (\"test\", source_test, 0, 10000, 3 if SMOKE else 50)]:\n    for name in CLASS_NAMES:\n        (folder / split / name).mkdir(parents=True, exist_ok=True)\n    rows = []\n    # Select every class explicitly, including in a tiny smoke run.\n    selected = []\n    for category in range(len(CLASS_NAMES)):\n        candidates = [i for i in range(start_index, end_index)\n                      if int(source.targets[i]) == category]\n        selected.extend(candidates[:per_class])\n    for index in selected:\n        image, label = source[index]\n        target = folder / split / CLASS_NAMES[label] / f\"digit_{index:05d}.png\"\n        if not target.exists():\n            image.save(target)\n        rows.append([target.relative_to(folder).as_posix(), CLASS_NAMES[label]])\n    with (folder / f\"{split}.csv\").open(\"w\", newline=\"\", encoding=\"utf-8\") as handle:\n        writer = csv.writer(handle)\n        writer.writerow([\"image_path\", \"label\"])\n        writer.writerows(rows)\n\ntransform = transforms.Compose([transforms.Grayscale(), transforms.ToTensor(),\n                                transforms.Normalize((0.1307,), (0.3081,))])\ntrain_set = datasets.ImageFolder(folder / \"train\", transform=transform)\nval_set = datasets.ImageFolder(folder / \"validation\", transform=transform)\ntest_set = datasets.ImageFolder(folder / \"test\", transform=transform)\n# ImageFolder sorts folder names alphabetically; do not assume numeric order.\nCLASS_NAMES = train_set.classes\nassert train_set.class_to_idx == val_set.class_to_idx == test_set.class_to_idx\nprint(\"Folder label mapping:\", train_set.class_to_idx)",
    },
    "03-sentiment-analysis/pytorch/notebooks/04-pretrained-chinese-sentiment.ipynb": {
        "from transformers import pipeline\nimport torch\nmodel_id = \"uer/roberta-base-finetuned-jd-binary-chinese\"\nDEVICE = (\"cuda\" if torch.cuda.is_available()\n          else \"mps\" if torch.backends.mps.is_available()\n          else \"cpu\")\nclassifier = pipeline(\"sentiment-analysis\", model=model_id, device=DEVICE)\nLABEL_CN = {\"negative\": \"负面\", \"positive\": \"正面\", \"0\": \"负面\", \"1\": \"正面\",\n            \"LABEL_0\": \"负面\", \"LABEL_1\": \"正面\",\n            \"positive (stars 4 and 5)\": \"正面\", \"negative (stars 1, 2 and 3)\": \"负面\"}\nreviews = [\"房间干净，位置方便，前台服务也很热情。\",\n           \"隔音很差，房间又小，下次不会再来住了。\"]\nfor text, result in zip(reviews, classifier(reviews, truncation=True, max_length=512)):\n    label = LABEL_CN.get(result[\"label\"].lower(), result[\"label\"])\n    print(f\"{label}（{result['score']:.3f}）：{text}\")": "from transformers import pipeline\nimport torch\nmodel_id = \"distilbert/distilbert-base-uncased-finetuned-sst-2-english\"\nDEVICE = (\"cuda\" if torch.cuda.is_available()\n          else \"mps\" if torch.backends.mps.is_available()\n          else \"cpu\")\nclassifier = pipeline(\"sentiment-analysis\", model=model_id, device=DEVICE)\nreviews = [\"The movie was engaging and beautifully acted.\",\n           \"The story was dull and the ending made no sense.\"]\nfor text, result in zip(reviews, classifier(reviews, truncation=True, max_length=512)):\n    print(f\"{result['label'].lower()} ({result['score']:.3f}): {text}\")",
    },
}
