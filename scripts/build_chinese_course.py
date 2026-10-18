#!/usr/bin/env python3
"""从英文母本生成中文镜像 notebook（中文 Markdown + 中文用户可见输出）。

设计要点：
- 英文课程（english/）是唯一母本；中文课程按同名同结构镜像生成，保证中英一一对应。
- Markdown 以“英文原文精确匹配”为键；英文母本一旦改动而译文表未同步，构建直接报错，
  不会静默留下过期中文。
- 代码单元只改“用户可见文案”和数据入口（course_data -> sentiment_cn），训练逻辑保持
  与英文一致，因此两门课的成绩口径可以互相印证。
- 中文图表字体由 common/course_zh.py 探测，避免中文标签显示成方框。

用法（仓库根目录）：
    ~/env_dl_uv/.venv/bin/python scripts/build_chinese_course.py            # 生成全部
    ~/env_dl_uv/.venv/bin/python scripts/build_chinese_course.py --check     # 只校验
"""
from pathlib import Path
import argparse
import ast
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGLISH = ROOT / "english"

ZH_BOOT = '''from pathlib import Path
import os
import sys

# 不依赖当前工作目录，向上找到中文课程根目录。
start = Path.cwd().resolve()
COURSE = next((p for p in [start, *start.parents]
               if (p / "CHINESE_COURSE_ROOT").is_file()), None)
if COURSE is None:
    raise RuntimeError("请在项目根目录（中文课程）中启动 Jupyter。")
ENGLISH = COURSE / "english"
# 中文专用模块在仓库根 common/，与英文课程共享的数据与检测模块在 english/common。
sys.path.insert(0, str(ENGLISH / "common"))
sys.path.insert(0, str(COURSE / "common"))
# 模型权重缓存与英文课程共用一份，避免同一份权重重复下载。
os.environ.setdefault("HF_HOME", str(ENGLISH / "data" / "huggingface"))
os.environ.setdefault("TORCH_HOME", str(ENGLISH / "data" / "torch-cache"))'''

FONT_IMPORT = "from course_zh import setup_chinese_fonts"

VISION_TITLE = """# LeNet：手写数字识别

**学习目标：**准备可复现的数据集、查看张量形状、训练分类器、用验证集挑选检查点，
并在独立的测试集上评估。本版本的所有类别名与图表均为中文。

请从上到下依次运行单元。第一次下载数据集/模型需要联网。
纯 CPU 也能运行；启动内核前设置 `COURSE_SMOKE=1` 可以做一次短流程检查。
冒烟测试的分数用来说明流程是否跑通，不代表模型质量。
"""

CIFAR_TITLE = VISION_TITLE.replace("手写数字识别", "CIFAR-10 图像分类")
RESNET_TITLE = """# ResNet18：在 CIFAR-10 上做迁移学习

**学习目标：**准备可复现的数据集、查看张量形状、训练分类器、用验证集挑选检查点，
并在独立的测试集上评估。本版本的所有类别名与图表均为中文。

请从上到下依次运行单元。第一次下载数据集/模型需要联网。
纯 CPU 也能运行；启动内核前设置 `COURSE_SMOKE=1` 可以做一次短流程检查。
冒烟测试的分数用来说明流程是否跑通，不代表模型质量。
"""
CUSTOM_TITLE = """# 用 ImageFolder 做自定义手写数字分类

**学习目标：**准备可复现的数据集、查看张量形状、训练分类器、用验证集挑选检查点，
并在独立的测试集上评估。本版本的所有类别名与图表均为中文。

请从上到下依次运行单元。第一次下载数据集/模型需要联网。
纯 CPU 也能运行；启动内核前设置 `COURSE_SMOKE=1` 可以做一次短流程检查。
冒烟测试的分数用来说明流程是否跑通，不代表模型质量。
"""

MD_ZH = {
"""# LeNet: handwritten digit classification""": VISION_TITLE,
"""# LeNet: CIFAR-10 image classification""": CIFAR_TITLE,
"""# ResNet18: transfer learning on CIFAR-10""": RESNET_TITLE,
"""# Custom digit classification with ImageFolder""": CUSTOM_TITLE,
"""## 1. Prepare training, validation, and test data""":
"""## 1. 准备训练集、验证集和测试集

官方测试集在最终评估之前保持不动，验证数据只从训练集中划分出来，划分由固定随机种子决定。
课堂运行只取一个子集以控制耗时；想做更充分的实验可以放大这些上限。
""",
"""## 1. Build your own folder dataset""":
"""## 1. 构造属于自己的文件夹数据集

原来的自定义数据课程依赖一份已无法获取的 LEDNUM 数据集。这里保留“自定义手写数字分类”
的完整流程：把 MNIST 导出成 `train/zero`、`train/one` …… 这样的文件夹。
它是手写数字数据，**不是** LED 数码管数据，因此演示的是数据集索引方式，而不是 LED 场景的精度。
只要保持同样的划分方式和类别目录结构，可以用真实采集的图片替换这些文件；
若多张图片来自同一作者或同一来源，请按作者/来源划分，避免验证集泄漏。
""",
"""## 2. Define the model""":
"""## 2. 定义模型

卷积用共享权重学习局部特征，池化缩小空间尺寸，最后的线性层为每个类别输出一个 logit。
交叉熵损失接收的是 logit，因此 softmax 只在展示预测概率时使用。
""",
"""### Transfer learning with ResNet18""":
"""### 用 ResNet18 做迁移学习

残差连接在学到的变换之外提供了一条恒等捷径。本节课冻结预训练主干，只训练新的十类输出头，
批归一化的统计量同样保持固定。请使用 ImageNet 的归一化参数，输入图像会被缩放到 224×224。
冒烟模式使用随机初始化权重，无法体现迁移学习的效果。
""",
"""## 3. Train and select a checkpoint""":
"""## 3. 训练并挑选检查点

训练时开启梯度并更新参数；评估时关闭梯度，并让 dropout/批归一化切换到评估行为。
保存验证准确率最高的检查点，绝不能用测试准确率来挑选。
""",
"""## 4. Evaluate the saved checkpoint""": "## 4. 评估已保存的检查点\n",
"""## 5. Inspect errors and predict one image""": "## 5. 观察错误样本并对单张图片做预测\n",
"""## Exercises and discussion""":
"""## 练习与讨论

1. 运行模型之前，先预测每个张量的形状。
2. 在保持划分不变的前提下比较不同学习率。
3. 解释验证结果和测试结果为什么会不一致。
4. 先观察被分错的样本，再考虑加大模型。
5. 对新图片做预测时，使用与评估完全一致的预处理和类别映射。

模型权重、类别名、随机种子和指标都保存在本实验的输出目录下。
结果会随子集规模、硬件和训练时长而变化。
""",
}

# 标题相同的单元（例如两处 "## Exercises"）用课程内路径 + 标题覆盖。
MD_ZH_BY_FILE = {
"03-sentiment-analysis/pytorch/notebooks/02-word-embeddings.ipynb": {
"## Exercises":
"""## 练习

对比 CBOW（`sg=0`）与 Skip-gram（`sg=1`）；先增加训练数据，再解读相近词。
试一个训练集里没出现过的词，解释它为什么没有训练出来的向量。
下一节课会把“句子向量取平均”和对语序敏感的 LSTM 做对比。
""",
"## 5. Predict new English reviews": "## 5. 预测新的中文评论\n",
},
"03-sentiment-analysis/paddle/notebooks/02-word-embeddings.ipynb": {
"## Exercises":
"""## 练习

对比 CBOW（`sg=0`）与 Skip-gram（`sg=1`）；先增加训练数据，再解读相近词。
试一个训练集里没出现过的词，解释它为什么没有训练出来的向量。
下一节课会把“句子向量取平均”和对语序敏感的 LSTM 做对比。
""",
"## 5. Predict new English reviews": "## 5. 预测新的中文评论\n",
},
}
for _side in ("pytorch", "paddle"):
    MD_ZH_BY_FILE[f"03-sentiment-analysis/{_side}/notebooks/03-lstm-sentiment.ipynb"] = {
"## Exercises":
"""## 练习

对比单向与双向模型；改变最大长度并统计被截断的比例；观察含否定词和褒贬混合的评论。
所有调参都只能在验证集上进行。若以后要复现预测结果，必须同时恢复词表、最大长度、
网络结构、类别映射和权重。

想直接用已经微调好的中文预训练情感模型，请看 PyTorch 路线里的可选课程。
它的训练任务与本实验使用的酒店评论不同，官方公布的分数不能当成本课程的成绩。
""",
"## 5. Predict new English reviews": "## 5. 预测新的中文评论\n",
}

MD_ZH.update({
"# Natural Language Processing: an English-language introduction":
"""# 自然语言处理：中文入门

**学习目标：**区分常见的 NLP 任务，解释分词与语言歧义，定义一个二分类情感分析实验。

| 任务 | 中文例子 | 输出 |
|---|---|---|
| 情感分析 | “这部电影意外地好看。” | 正面 |
| 命名实体识别 | “小王去了上海。” | 人名、地名 |
| 语义相似度 | “好看的片子” / “出色的电影” | 相似度分数 |
| 问答 | “导演是谁？” | 一段答案文本 |
| 文本生成 | “写一条短评。” | 生成的文本 |
""",
"## Why language is difficult":
"""## 语言为什么难

“不差”不等于“差”；“又是晚点，真棒”可能是反话；“银行关门了”需要上下文才能确定是河岸还是银行。
语序、否定词、领域和文本长度都会改变含义。正面/负面只是数据集给出的标签，
不能完整描述真实评论，褒贬混合和中立的表达依然存在。

中文不像英文那样天然用空格分词，因此中文课程使用 jieba 做词级切分，
并且不使用停用词表——“不”“没”这类否定词一旦删掉，情感就会反过来。
真实的工业系统更多使用预训练模型自带的子词切分器，本节先用最直白的方式建立直觉。
""",
"## Our experiment":
"""## 本课程的实验

我们使用 [ChnSentiCorp 中文酒店评论数据集](https://github.com/pengchuanzhang/Senta)。
标签是 `负面=0`、`正面=1`。官方 `train.tsv` 按比例划出训练集与验证集；本发行包里的
`test.tsv` 只有 `qid` 和文本、没有标签（排行榜用的隐藏测试集），所以最终评估使用带标签的
官方 `dev.tsv`。预处理会剔除不含中文的记录并跨划分去掉完全重复的文本，
因此处理后的条数与论文公布的条数不同，口径写在 `provenance.json` 里。

词表构建和 Word2Vec 训练只用训练集文本；验证集和测试集中没见过的词映射到未知符号。
预训练情感模型是一份独立的可选对照，不是本节要训练的 LSTM。

**讨论：**褒贬混合的评论你会怎么打标签？为什么否定词必须留在输入里？
为什么课堂子集上的准确率不能当作基准成绩？
""",
"# Word embeddings: from English words to vectors":
"""# 词向量：从中文词到向量

**学习目标：**对比 one-hot 向量与稠密向量，只用训练集评论训练 Skip-gram 向量，
并计算词与句子的相似度。

one-hot 向量只能区分词，无法表达相似度。Word2Vec 从上下文学习：CBOW 用上下文预测中心词，
Skip-gram 用中心词预测上下文。上下文相近会让反义词也靠得很近，
所以余弦相似度不是情感分类器；训练子集太小时，相近词也会很不稳定。
""",
"## 1. Train Word2Vec on training reviews": "## 1. 用训练集评论训练 Word2Vec\n",
"## 2. Load vectors into the framework's embedding layer":
"""## 2. 把向量装进框架的嵌入层

矩阵的行号就是 token ID。这里复制训练好的向量并冻结它们，只做演示；
下游分类器里你可以选择继续微调这些向量。
""",
"## 3. Explore word and sentence similarity": "## 3. 探索词与句子的相似度\n",
"## 4. Visualize a projection":
"""## 4. 可视化一个投影

这是把词向量降到二维的 PCA 投影，是一种有损视图。
图上看近不代表语义等价。
""",
"# English movie-review sentiment classification with a bidirectional LSTM":
"""# 用双向 LSTM 做中文电影评论情感分类

**学习目标：**从训练数据构建词表，对评论做编码与补齐，训练对语序敏感的模型，
用验证集挑选检查点，并输出中文标签。

本课使用 ChnSentiCorp 中文酒店/影视评论，分词使用 jieba，而不是英文空格切分。
PyTorch 与 PaddlePaddle 两条路线共用同一份预处理数据和标签映射，但使用各自的环境与输出目录。
""",
"## 1. Build a vocabulary without test leakage":
"""## 1. 构建不泄漏测试信息的词表

`<pad>` 固定为 ID 0，`<unk>` 固定为 ID 1。课堂实验会截断过长的评论，同时记录真实长度。
词表只在训练文本上拟合。“不”“没有”等否定词不要当停用词删掉。
""",
"## 2. Define the model and training step":
"""## 2. 定义模型与训练步骤

嵌入层把 ID 映射成向量；双向 LSTM 从两个方向总结整条评论；
把两个方向的最终状态拼接后送入二分类线性层。
计算循环网络时要传入真实长度，这样补齐用的 padding 不会污染最终状态。
梯度裁剪用于限制异常大的更新。
""",
"## 3. Train and select by validation accuracy": "## 3. 训练并按验证准确率挑选检查点\n",
"## 4. Reload and evaluate on held-out test reviews": "## 4. 重新加载并在留出测试集上评估\n",
"## 5. Predict new English reviews": "## 5. 预测新的中文评论\n",
"# Optional: an already fine-tuned English sentiment model":
"""# 可选：一个已经微调好的中文情感模型

请使用 PyTorch 环境。这个检查点是在**京东商品评论**二分类任务上微调得到的，
不是在语言模型上临时接一个未训练的Classification Head；它的公开分数来自京东任务，
不能替代本课在酒店/影视评论上的 LSTM 实验——领域不同，指标不能互相顶替。
首次运行会下载模型文件。
""",
"## Discuss":
"""## 讨论

评论长度超过模型上限时会发生什么？京东商品评论与本课的酒店/影视评论有什么差别？
为什么置信度很高也可能预测错？

[模型主页与来源说明](https://huggingface.co/uer/roberta-base-finetuned-jd-binary-chinese)。
""",
})

# 代码单元只替换“用户可见文案”。每条都必须命中，否则构建失败（防止母本改动后中文失效）。
GLOBAL_CODE = [
('print(f"Device: {DEVICE}; experiment: {EXPERIMENT}; smoke test: {SMOKE}")',
 'print(f"计算设备：{DEVICE}；实验：{EXPERIMENT}；冒烟测试：{SMOKE}")'),
('print("Batch shape:", tuple(images.shape), "Label shape:", tuple(labels.shape))',
 'print("批次形状：", tuple(images.shape), "标签形状：", tuple(labels.shape))'),
('print("Split sizes:", len(train_set), len(val_set), len(test_set))',
 'print("数据集划分规模：", len(train_set), len(val_set), len(test_set))'),
('print("Split sizes:", len(train_rows), len(validation_rows), len(test_rows))',
 'print("数据集划分规模：", len(train_rows), len(validation_rows), len(test_rows))'),
('print("Labels:", LABELS)', 'print("标签：", LABELS)'),
('fig.suptitle("Training examples")', 'fig.suptitle("训练样本示例")'),
('print("Logit shape:", tuple(', 'print("模型输出形状：", tuple('),
('print("Trainable parameters:", sum(', 'print("可训练参数量：", sum('),
('f"Epoch {epoch + 1}/{EPOCHS} | train loss {train_loss:.4f} | "',
 'f"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | "'),
('f"Epoch {epoch + 1}/{EPOCHS} | training loss {train_loss:.4f} | "',
 'f"第 {epoch + 1}/{EPOCHS} 轮 | 训练损失 {train_loss:.4f} | "'),
('f"validation loss {val_loss:.4f} | validation accuracy {val_accuracy:.3f}")',
 'f"验证损失 {val_loss:.4f} | 验证准确率 {val_accuracy:.3f}")'),
('print(f"Held-out test accuracy: {test_accuracy:.3f}")',
 'print(f"留出测试集准确率：{test_accuracy:.3f}")'),
('print(f"Test accuracy: {test_accuracy:.3f}; test loss: {test_loss:.4f}")',
 'print(f"测试集准确率：{test_accuracy:.3f}；测试集损失：{test_loss:.4f}")'),
('label="Training")', 'label="训练集")'),
('label="Validation")', 'label="验证集")'),
('title="Cross-entropy loss", xlabel="Epoch", ylabel="Loss")',
 'title="交叉熵损失", xlabel="轮次", ylabel="损失")'),
('title="Classification accuracy", xlabel="Epoch", ylabel="Accuracy")',
 'title="分类准确率", xlabel="轮次", ylabel="准确率")'),
('axis.set(title="English sentiment classification", xlabel="Epoch", ylabel="Accuracy")',
 'axis.set(title="中文情感分类准确率", xlabel="轮次", ylabel="准确率")'),
('xlabel="Predicted class", ylabel="True class", title="Test confusion matrix")',
 'xlabel="预测类别", ylabel="真实类别", title="测试集混淆矩阵")'),
('print(f"Misclassified example: true={CLASS_NAMES[true]}, predicted={CLASS_NAMES[predicted]}")',
 'print(f"错分样本：真实={CLASS_NAMES[true]}，预测={CLASS_NAMES[predicted]}")'),
('f"Prediction: {CLASS_NAMES[prediction]} | confidence: {probabilities[prediction]:.3f} | "',
 'f"预测结果：{CLASS_NAMES[prediction]} | 置信度：{probabilities[prediction]:.3f} | "'),
('f"true label: {CLASS_NAMES[int(true_label)]}")',
 'f"真实标签：{CLASS_NAMES[int(true_label)]}")'),
('CLASS_NAMES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]',
 'CLASS_NAMES = ["飞机", "汽车", "鸟", "猫", "鹿", "狗", "青蛙", "马", "船", "卡车"]'),
('print("Vocabulary size:", len(vocab), "True length:", length)',
 'print("词表规模：", len(vocab), "真实长度：", length)'),
('print("Vocabulary size:", len(words), "Vector shape:", vectors.shape)',
 'print("词表规模：", len(words), "向量形状：", vectors.shape)'),
('print("First token IDs:", ids[:12])', 'print("前若干个 token ID：", ids[:12])'),
('print("English label mapping:", dict(enumerate(LABELS)))',
 'print("中文标签映射：", dict(enumerate(LABELS)))'),
('encode("The acting wasn\'t convincing, but I liked the music.", vocab, MAX_LENGTH)',
 'encode("演技没什么说服力，但我倒是喜欢配乐。", vocab, MAX_LENGTH)'),
('OUTPUT / "english_word2vec.model"', 'OUTPUT / "chinese_word2vec.model"'),
('example_word = "movie" if "movie" in word_to_id else words[0]',
 'example_word = "酒店" if "酒店" in word_to_id else words[0]'),
('print(f"Embedding for \'{example_word}\': shape={vector.shape}")',
 'print(f"词向量“{example_word}”：形状={vector.shape}")'),
('print("Nearest words:", word2vec.wv.most_similar(', 'print("最相近的词：", word2vec.wv.most_similar('),
('first = "The movie was enjoyable and the acting was excellent."',
 'first = "这部电影很好看，演技也十分出色。"'),
('second = "I liked the film and its performances."',
 'second = "我喜欢这部片子，也喜欢里面的表演。"'),
('print("Sentence similarity:", cosine(', 'print("句子相似度：", cosine('),
('print("Try comparing \'good\' and \'not good\'; average vectors can lose word order.")',
 'print("可以对比“很好”和“不太好”：取平均向量会丢掉语序信息。")'),
('axis.set(title="English word vectors: PCA projection", xlabel="Principal component 1",',
 'axis.set(title="中文词向量：PCA 投影", xlabel="第一主成分",'),
('ylabel="Principal component 2")', 'ylabel="第二主成分")'),
('print("Predictions can be wrong, especially after a short classroom run.")',
 'print("预测是会出错的，尤其是在课堂这种短时训练之后。")'),
('from course_data import', 'from sentiment_cn import'),
# 英文示例句 -> 中文示例句
('examples = ["I loved the acting, but the ending was disappointing.",\n            "The movie isn\'t bad at all.", "Great, another predictable ending."]',
 'examples = ["我很喜欢这段表演，但结局令人失望。",\n            "这部电影一点也不差。", "真棒，又是一个能猜到的结局。"]'),
('    print("Text:", text)\n    print("Tokens:", tokenize(text))',
 '    print("原文：", text)\n    print("分词：", tokenize(text))'),
('reviews = ["The movie was wonderful and the acting was excellent.",\n           "The plot was boring and the ending was disappointing.",\n           "I expected to hate it, but it was not bad at all."]',
 'reviews = ["这部电影非常精彩，表演也可圈可点。",\n           "剧情很无聊，结局让人失望。",\n           "本以为会讨厌它，结果竟然还不错。"]'),
]

# 个别单元需要结构性改写（数据集语言不同、目录名必须保持英文）。
FILE_CODE = {
"01-image-classification/notebooks/01-lenet-mnist.ipynb": [
('CLASS_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]',
 'CLASS_NAMES = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]'),
],
# 自定义数据课：磁盘目录名必须是英文（也便于跨平台），只在展示层映射成中文。
"01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb": [
('CLASS_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]',
 'DIGIT_CN = {"zero": "零", "one": "一", "two": "二", "three": "三", "four": "四",\n            "five": "五", "six": "六", "seven": "七", "eight": "八", "nine": "九"}\n'
 '# 文件夹名保持英文，ImageFolder 按字母序编号；下面的中文类别名按同一顺序对齐。\n'
 'CLASS_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]'),
('# ImageFolder sorts folder names alphabetically; do not assume numeric order.\nCLASS_NAMES = train_set.classes\nassert train_set.class_to_idx == val_set.class_to_idx == test_set.class_to_idx\nprint("Folder label mapping:", train_set.class_to_idx)',
 '# ImageFolder 按文件夹名的字母顺序编号，不要假设按数字顺序排列。\n'
 'FOLDER_CLASSES = train_set.classes\n'
 'assert train_set.class_to_idx == val_set.class_to_idx == test_set.class_to_idx\n'
 'CLASS_NAMES = [DIGIT_CN[name] for name in FOLDER_CLASSES]\n'
 'print("文件夹与类别编号映射：", {DIGIT_CN[name]: index for name, index in train_set.class_to_idx.items()})'),
],
"03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb": [
('model_id = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"',
 'model_id = "uer/roberta-base-finetuned-jd-binary-chinese"'),
('reviews = ["The movie was engaging and beautifully acted.",\n           "The story was dull and the ending made no sense."]',
 'LABEL_CN = {"negative": "负面", "positive": "正面", "0": "负面", "1": "正面",\n            "LABEL_0": "负面", "LABEL_1": "正面",\n            "positive (stars 4 and 5)": "正面", "negative (stars 1, 2 and 3)": "负面"}\n'
 'reviews = ["房间干净，位置方便，前台服务也很热情。",\n           "隔音很差，房间又小，下次不会再来住了。"]'),
('    print(f"{result[\'label\'].lower()} ({result[\'score\']:.3f}): {text}")',
 '    label = LABEL_CN.get(result["label"].lower(), result["label"])\n'
 '    print(f"{label}（{result[\'score\']:.3f}）：{text}")'),
],
}

# 中文课程树里需要生成同名文件；英文侧独有的文件不生成。
TARGETS = [
"01-image-classification/notebooks/01-lenet-mnist.ipynb",
"01-image-classification/notebooks/02-lenet-cifar10.ipynb",
"01-image-classification/notebooks/03-resnet-cifar10.ipynb",
"01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb",
"03-sentiment-analysis/pytorch/notebooks/01-nlp-overview.ipynb",
"03-sentiment-analysis/pytorch/notebooks/02-word-embeddings.ipynb",
"03-sentiment-analysis/pytorch/notebooks/03-lstm-sentiment.ipynb",
"03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb",
"03-sentiment-analysis/paddle/notebooks/01-nlp-overview.ipynb",
"03-sentiment-analysis/paddle/notebooks/02-word-embeddings.ipynb",
"03-sentiment-analysis/paddle/notebooks/03-lstm-sentiment.ipynb",
]

# 中文课的可选预训练课使用中文检查点，文件名如实描述，配对关系记录在 check_parity 的别名表里。
ZH_NAME_OVERRIDES = {
"03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb":
    "03-sentiment-analysis/pytorch/notebooks/04-pretrained-chinese-sentiment.ipynb",
}

FONT_LINES = [FONT_IMPORT,
              "setup_chinese_fonts(plt)",
              'print("图表中文字体：", setup_chinese_fonts(plt))']


def translate_markdown(key, source):
    stripped = source.strip()
    heading = stripped.splitlines()[0].strip() if stripped else ""
    override = MD_ZH_BY_FILE.get(key, {})
    if heading in override:
        return override[heading]
    if stripped in MD_ZH:          # 兼容以整段原文为键的写法
        return MD_ZH[stripped]
    if heading in MD_ZH:
        return MD_ZH[heading]
    raise KeyError(f"{key}: 缺少中文译文 -> {heading[:70]}")


GLOBAL_USED = set()
FILE_USED = {}


def build_notebook(key, problems):
    source_path = ENGLISH / key
    notebook = json.loads(source_path.read_text(encoding="utf-8"))
    # 运行信息单元与「预期输出」单元由各自语言的执行/内嵌脚本生成，不参与镜像翻译。
    generated = {"course-runtime-info", "course-expected-output"}
    cells = [cell for cell in notebook["cells"]
             if not generated & set(cell.get("metadata", {}).get("tags", []))]
    first_boot = True
    font_done = False
    result = []
    for cell in cells:
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            result.append({"cell_type": "markdown", "metadata": cell.get("metadata", {}),
                           "source": translate_markdown(key, source)})
            continue
        if first_boot:
            result.append({"cell_type": "code", "execution_count": None, "outputs": [],
                           "metadata": cell.get("metadata", {}), "source": ZH_BOOT})
            first_boot = False
            continue
        for index, (old, new) in enumerate(GLOBAL_CODE):
            if old in source:
                source = source.replace(old, new)
                GLOBAL_USED.add(index)
        for index, (old, new) in enumerate(FILE_CODE.get(key, [])):
            if old not in source:
                continue
            source = source.replace(old, new)
            FILE_USED.setdefault(key, set()).add(index)
        if not font_done and "import matplotlib.pyplot as plt" in source:
            lines = source.splitlines()
            position = lines.index("import matplotlib.pyplot as plt")
            source = "\n".join(lines[:position + 1] + FONT_LINES + lines[position + 1:])
            font_done = True
        try:
            ast.parse(source)
        except SyntaxError as exc:
            problems.append(f"{key}: 生成的代码单元语法错误：{exc}")
        result.append({"cell_type": "code", "execution_count": None, "outputs": [],
                       "metadata": cell.get("metadata", {}), "source": source})
    for index, (old, _) in enumerate(FILE_CODE.get(key, [])):
        if index not in FILE_USED.get(key, set()):
            problems.append(f"{key}: 文件级替换未命中：{old[:60]}")
    notebook["cells"] = result
    notebook["metadata"]["language"] = "zh-CN"
    notebook["metadata"]["translated_from"] = f"english/{key}"
    return notebook


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只校验译文覆盖，不写文件")
    parser.add_argument("--force", action="store_true",
                        help="覆盖已带实跑输出的中文镜像（覆盖后必须重新执行并内嵌输出）")
    parser.add_argument("--only", action="append",
                        help="只处理文件名包含该子串的母本，可重复；与 --force 搭配重建单本镜像")
    args = parser.parse_args()
    problems, written = [], []
    global_usage = set()
    keys = [key for key in TARGETS
            if not args.only or any(needle in key for needle in args.only)]
    if not keys:
        problems.append(f"--only 没有匹配到任何母本：{args.only}")
    for key in keys:
        try:
            notebook = build_notebook(key, problems)
        except FileNotFoundError:
            problems.append(f"缺少英文母本：english/{key}")
            continue
        target = ROOT / ZH_NAME_OVERRIDES.get(key, key)
        if not args.check and target.exists() and not args.force:
            saved = json.loads(target.read_text(encoding="utf-8"))
            executed = any(cell.get("outputs") or cell.get("execution_count")
                           for cell in saved.get("cells", []) if cell.get("cell_type") == "code")
            if executed:
                problems.append(f"{key}: 中文镜像已保存实跑输出，拒绝覆盖。"
                                "确需重建请加 --force，然后重新执行并内嵌输出")
                continue
        written.append(key)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
                              encoding="utf-8")
    # 只处理子集时不审计“全局替换未命中”，否则每次都会误报。
    for index in range(len(GLOBAL_CODE)) if not args.only else sorted(GLOBAL_USED):
        if index not in GLOBAL_USED:
            problems.append(f"全局替换一次都没命中（母本可能已改动）：{GLOBAL_CODE[index][0][:70]}")
    if problems:
        print("\n".join(dict.fromkeys(problems)))
    for key in written:
        print("生成" if not args.check else "校验", key)
    if problems:
        print(f"发现 {len(set(problems))} 个问题")
        return 1
    print(f"中文镜像{'生成' if not args.check else '校验'}完成：{len(written)} 本")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
