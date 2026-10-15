# 深度学习实验室

围绕图像分类、目标检测与中文情感分析的 Notebook 教学项目。

| 模块 | 入口 | 内容 |
|---|---|---|
| 01 图像分类 | [课程说明](01-image-classification/README.md) | MNIST → CIFAR-10 → ResNet → 自定义数据 |
| 02 目标检测 | [课程说明](02-object-detection/README.md) | CV 与 CNN 基础 → YOLO → 剪刀石头布检测 |
| 03 情感分析 | [课程说明](03-sentiment-analysis/README.md) | NLP → 词向量 → LSTM，Paddle/PyTorch 两条路线 |

首次学习从 [MNIST 规范版](01-image-classification/notebooks/01-lenet-mnist.ipynb) 开始。完成基础训练流程后，可以分别进入目标检测或情感分析。

- [学习路线](docs/learning-path.md)
- [环境准备](docs/environment-setup.md)
- [数据获取与放置路径](docs/datasets.md)
- [目录整理记录](docs/migration/reorganization.md)

每个运行环境独立安装依赖，以 Notebook 所在目录作为工作目录。数据放在各模块 data/，训练产物放在 outputs/，讲解图片放在 assets/。

当前状态：完成目录及路径整理和静态检查；未安装新环境、下载资源或执行训练。Notebook 历史输出原样保留，不能视为本次运行结果。

## 英文版教学课程

[english/README.md](english/README.md) 是独立的英文教学版：13 个 Notebook 均已在本机 CPU 上逐格执行并保留真实输出，环境由 uv 管理，数据、词表、缓存与训练产物和中文课程完全隔离。其中 YOLO26 检测已改用 scripts/fetch_rps.py 抓取的剪刀石头布真实数据集，但保存的输出是 1 个 epoch 的管线验证；10 epoch 课堂完整训练约需 35 分钟 CPU 时间，尚未执行。执行证据见 [english/reports/README.md](english/reports/README.md)，改动映射见 [english/docs/adaptation-map.md](english/docs/adaptation-map.md)。

上一段的当前状态只描述中文课程；英文版的验证结论以 english/reports/ 为准。
