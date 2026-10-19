# 数据集介绍与准备

中文（母本） · [English mirror](datasets.md) · [英文课程操作细节](../english/docs/datasets.md)

本页按“数据内容、课程用途、来源地址、获取方法、存放路径、处理与署名”介绍数据集。路径均相对于仓库根目录。来源页面核对日期为 2026-10-18，页面数量和下载选项可能变化；原始数据规模与 Notebook 实际使用的课堂子集规模需要区分。

| 数据集 | 任务 | 课程用途 |
|---|---|---|
| MNIST | 手写数字十分类 | LeNet 入门、自定义图片目录 |
| CIFAR-10 | 彩色物体十分类 | LeNet 与 ResNet18 对比 |
| 石头剪刀布 | 手势目标检测 | YOLO 训练、边界框与推理 |
| 车辆计数（vehicle counting） | 车辆检测与车流量统计 | 中英文车流量统计 Notebook |
| IMDb | 英文情感二分类 | 英文词向量与 LSTM |
| ChnSentiCorp | 中文情感二分类 | 中文 NLP 双框架路线 |
| COCO8 | 小规模目标检测 | 英文检测流程快速检查 |
| MNIST 派生数据 / LEDNUM | 自定义数字图片 | 数据读取扩展实验 |

## MNIST：手写数字识别

- **数据内容与用途**：28×28 灰度手写数字，标签 0–9；标准训练集 60,000 张、测试集 10,000 张。适合掌握预处理、网络输入输出、训练评估与模型保存。
- **来源地址**：[数据集介绍](https://huggingface.co/datasets/ylecun/mnist)、[torchvision 下载接口](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html)。
- **获取方式**：运行课程中的 `torchvision.datasets.MNIST(download=True)`。介绍页的 Parquet 文件不能直接替代 torchvision 需要的原始数据格式。
- **存放路径**：英文 `english/01-image-classification/data/MNIST/`；中文 `01-image-classification/data/MNIST/`。
- **处理与使用**：验证集从训练数据划分，官方测试集用于最终评估；英文自定义目录实验由 MNIST 派生，不是新的独立采集数据集。保留原作者署名与所下载发行包的使用条款。

## CIFAR-10：彩色物体分类

- **数据内容与用途**：32×32 RGB 图片，包含飞机、汽车、鸟、猫、鹿、狗、青蛙、马、船、卡车十类。标准训练集 50,000 张、测试集 10,000 张，用于 LeNet 和 ResNet18 迁移学习。
- **来源地址**：[多伦多大学数据集介绍](https://www.cs.toronto.edu/~kriz/cifar.html)、[Python 数据包](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz)、[大学发布的 Parquet 镜像](https://huggingface.co/datasets/uoft-cs/cifar10)。
- **获取方式**：中文版由 torchvision 下载；英文加载器先复用完整的本地 torchvision 数据，否则下载固定版本的 Parquet 镜像，并检查 SHA-256、类别编号与划分数量。
- **存放路径**：英文 `english/01-image-classification/data/cifar10/`；中文 `01-image-classification/data/CIFAR10/`，注意大小写区别。
- **处理与使用**：课堂可能只取子集，不能当成完整基准实验；英文加载器写入 `train-provenance.json` 和 `test-provenance.json`。按来源页要求引用 Krizhevsky 2009 年技术报告，并保留发行包条款。

## 石头剪刀布：YOLO26 目标检测

- **模型与任务**：中英文课程统一采用 Ultralytics **YOLO26n**，检测手势位置与类别。
- **来源**：[melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1)、[版本列表](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset)。新提供的 `Rock-Paper-Scissors.v1i.yolo26.zip` 含匹配的项目、版本、CC BY 4.0 声明。
- **数据规模**：共 4,463 张，保留原训练 3,939 张、验证 338 张、测试 186 张，对应 4,610 / 400 / 204 个框。导出预处理为自动纠正方向、拉伸到 640×640；未做导出数据增强，模型训练时增强另计。
- **类别映射**：原名称为数字，已查看标注裁剪图确认 **0=paper（布）、1=rock（石头）、2=scissors（剪刀）**。只修改名称，不重排标注编号。
- **获取方式**：在 Roboflow 网页下载 v1 的 YOLO26 导出，或用个人 API key 调用导出 REST 接口取同一个包（两种方式的具体命令见 `02-object-detection/data/README.md`）。下载后先放入仓库外的 DataSet 暂存区（课堂镜像 `/workspace/DataSet/yolo/`），再从暂存区导入：

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```
```bash
# macOS/Linux，仓库根目录，统一课堂环境
cp "/path/to/Rock-Paper-Scissors.v1i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

- **存放位置**：`english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`。中英文共用这份已验证数据与检测锁定环境，各自产物分开保存。已存在合格数据时不必重复导入，脚本拒绝覆盖或合并目录。
- **完整性与处理**：保留原始划分、图片和标注，只为类别赋英文名称；核对包内来源、坐标和跨集合完全重复图片。压缩包 SHA-256 为 `2cf65dffbaa92483bbf99e7903f7c23c934ccf57d1cb097a66b7d38eadac0e59`，来源、类别和计数写入 `provenance.json`。本包未发现非法框或跨集合完全重复图片，但原划分仍可能存在视频近邻帧或参与者泄漏。
- **署名**：保留导出 README，署名 melikeavan，链接版本页与 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，说明类别名称修改。

早先 Xuban 镜像和 6,455 张扁平 VOC 包不再作为默认数据。旧镜像指标仅作历史记录；旧 Notebook 已归档，`fetch_rps_legacy.py` 仅供历史复现。

格式转换与查看放在独立的 [VOC / COCO / YOLO 数据集专题](../02-object-detection/dataset-formats/README.md)，包含[小土堆 Labs](https://xiaotudui.com/labs) 使用说明。训练直接使用正式 YOLO 导出，不需要转换。

## 车辆计数：车流量统计（YOLO26）

- **模型与任务**：Ultralytics **YOLO26n** 车辆检测 + 车流量统计：零样本对照、微调、图片计数、跟踪过线计数，中英文共用同一份导入数据：中文[车流量统计 Notebook](../02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb)、英文 [vehicle-counting notebook](../english/02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb)。
- **来源**：[vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)，正式 YOLO26 导出（`vehicle counting.v4i.yolo26.zip`），包内含匹配的 workspace/project/version 元数据与 CC BY 4.0 声明。
- **数据规模**：共 6,565 张 640×640 图片、5 类，保留原划分：训练 4,708 / 验证 1,661 / 测试 196 张，对应 52,668 / 18,810 / 2,120 个框。
- **类别映射**：编号保持原顺序，名称统一小写（原包 `Truck` 首字母大写）：**0=truck、1=bicycle、2=bus、3=car、4=motorcycle**。
- **获取方式**：v4 的 YOLO26 导出需要 Roboflow 账号，可在网页下载，或用个人 API key 调用导出 REST 接口（命令见 `02-object-detection/data/README.md`）。下载后放入仓库外的 DataSet 暂存区（课堂镜像 `/workspace/DataSet/yolo/`），在仓库根目录导入：

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\import_vehicle_counting.py --from-staging
```
```bash
# macOS/Linux, repository root, single classroom interpreter (add --staging <dir> for another DataSet folder)
cp "/path/to/vehicle counting.v4i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/import_vehicle_counting.py --from-staging
```

- **存放位置**：`english/02-object-detection/data/vehicle-counting-tksu5-v4/`（与手势数据同目录约定，只读共用），中英文产物分别写入各自模块 `outputs/`。跟踪依赖 `lapx`（提供 `lap` 模块），已在检测锁定环境中。
- **完整性与处理**：导入器核对包内来源、类别集合、划分独立性与跨集合完全重复图片；源包有 3 行标注是分割多边形，导入时改写为其外接检测框并计数记录。压缩包 SHA-256 `3945432ed7ce76c9af3b83db7f0ee68ad898b0996bd7577f88a3b6ee6f0cea20`，来源、类别与计数写入 `provenance.json`；已存在目标目录时拒绝覆盖。
- **署名**：署名 vehicle-counting-rtvul，链接版本页与 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，说明名称小写化与 3 行分割标注归一化。

## IMDb：英文电影评论情感分析

- **数据内容与用途**：英文影评正负情感二分类；来源提供训练 25,000 条、测试 25,000 条带标签评论，另有本课程未使用的无标签部分。用于英文 Word2Vec、Embedding 与 LSTM。
- **来源地址**：[Stanford 数据集介绍](https://ai.stanford.edu/~amaas/data/sentiment/)、[官方压缩包](https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz)。
- **获取方式与路径**：运行英文词向量或 LSTM Notebook，由 `english/common/course_data.py` 下载到 `english/03-sentiment-analysis/data/imdb/`，生成 `train.jsonl`、`validation.jsonl`、`test.jsonl` 与 `provenance.json`，两套框架共用。
- **处理与使用**：清除 HTML、跨划分完全重复文本、含中日韩汉字区字符或无英文词元的文本；按 seed 42 从原训练数据划出验证集。标签为 `0=负面`、`1=正面`。实际过滤数量见 provenance，课堂平衡子集数量见 Notebook；词表和 Word2Vec 只用训练集拟合。
- **署名**：引用来源页的 Maas 等人 2011 年论文，保留压缩包 README 与相关条款。经筛选后的课堂结果不等同于未修改 IMDb 基准成绩。

## ChnSentiCorp：中文评论情感分析

- **数据内容与用途**：中文评论二分类，用于中文 NLP 教程，课程解释的标签为 `0=负面`、`1=正面`。
- **来源地址**：[PaddleNLP 数据集实现与字段定义](https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/datasets/chnsenticorp.py)、[课程下载包](https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip)。
- **获取方式与路径**：中文 Notebook 自动下载解压，共用 `03-sentiment-analysis/data/ChnSentiCorp.zip` 与 `03-sentiment-analysis/data/ChnSentiCorp/`；不要同时运行两套框架的解压步骤。
- **格式与划分**：带表头的 TSV；PaddleNLP 发行包训练字段为 `label,text`，验证字段为 `qid,label,text`，测试字段为 `qid,text`，测试无真实标签。解压后核对嵌套层级及 Notebook 路径，按实际文件统计数量，不直接套用其他镜像的数据规模。无标签测试预测不能用于计算准确率，应使用带标签验证集或明确记录的带标签评估划分。
- **课程处理与划分口径**：`common/sentiment_cn.py` 读取源 TSV，剔除不含中文的记录、跨划分去掉完全重复的文本，写出可复现的 JSONL 划分到 `03-sentiment-analysis/data/chnsentiment/{train,validation,test}.jsonl`，并把条数、剔除数量、去重数量与源文件 SHA-256 写入同目录 `provenance.json`。验证集按标签各取官方 `train.tsv` 的 20%；**最终评估使用带标签的官方 `dev.tsv`**，因为发行包的 `test.tsv` 没有标签。分词使用 jieba 词级切分且不使用停用词表。
- **复制到本机**：源数据已在 `/workspace/DataSet/nlp/ChnSentiCorp/` 时可直接复制，避免重复下载：
  `cp -R /workspace/DataSet/nlp/ChnSentiCorp 03-sentiment-analysis/data/`；
  没有本地副本时由脚本从上面的下载包自动获取。两种方式的产物与口径完全一致。
- **使用条款**：保留源数据包声明；加载器代码的软件许可证不能直接视为评论文本的数据许可证。

## COCO8：检测流程快速检查

- **数据内容与用途**：8 张 COCO 标签体系图片，训练 4 张、验证 4 张，适合快速检查下载、训练、推理流程。
- **来源地址**：[Ultralytics 数据集说明](https://docs.ultralytics.com/datasets/detect/coco8/)、[下载包](https://ultralytics.com/assets/coco8.zip)。
- **获取方式与路径**：英文检测内核启动前设置 `COURSE_SMOKE=1`，辅助函数下载到 `english/02-object-detection/data/coco8/`。
- **使用边界与条款**：这是流程检查，不是手势训练，也不能用于证明泛化能力。正式实验恢复默认模式。保留源发行包声明，分发前查看提供方许可说明。

## 自定义数字目录与 LEDNUM

- **英文 MNIST 派生目录**：由扩展 Notebook 自动生成，无需额外下载。数据与 CSV 索引位于 `english/01-image-classification/data/custom-digits-balanced/`，快速检查版目录后缀为 `-smoke`；类别文件夹使用英文数字名。保留原始训练/测试隔离，读取 ImageFolder 的 `class_to_idx`，不要假设字母排序等于数字顺序。仍需保留 MNIST 署名。
- **中文自定义目录**：中文课程已改用与英文一致的 MNIST 派生目录（`01-image-classification/data/custom-digits-balanced/`，快速检查版后缀 `-smoke`），文件夹名保持英文，展示层再映射为中文类别名，因此不再需要 LEDNUM。
- **LEDNUM（历史）**：旧中文进阶课使用 LED 数字图片，预期位于归档笔记中的 `01-image-classification/data/LEDNUM/`（`train_data/`、`test_data/`、`train.txt`、`test.txt`）。仓库未提供可核实的公开下载、数量或许可；历史 notebook 保留在 `01-image-classification/archive/legacy-notebooks/`，现行课程不再依赖它。教程中的 `/workspace` 复制命令不是下载地址。

## 预训练模型与离线使用

ResNet18 的 ImageNet 权重、YOLO 权重和可选 [SST-2 微调 DistilBERT](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) 属于模型资源。SST-2 与 IMDb 不同，课程不会额外下载 SST-2 进行训练；模型卡指标不能作为本地测量结果。

英文缓存包括 `english/data/torch-cache/`、`english/data/huggingface/` 和 `english/02-object-detection/outputs/weights/`。上课前下载数据与权重，离线分发时保留来源、版本、可用校验和、真实划分数量、类别映射和处理记录；虚拟环境按平台重新建立。数据集和训练产物继续不提交到 Git。
