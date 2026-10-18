# 深度学习实验室（中文课程）

[English (default)](README.md) · 中文

项目默认使用英文课程；此入口保留中文教学、中文数据和原有框架实现。分类与 NLP 保留语言独立的环境和数据；当前 YOLO26 检测共用正式 v1 数据与检测环境，训练产物按语言分开。

英文课程可通过 `./start-notebooks.ps1` 启动。中文课程先按环境说明准备虚拟环境，再运行 `./start-notebooks.ps1 -Language zh-CN -Module vision`。中文目标检测采用 YOLO26n，与英文共享检测环境与正式 v1 数据，旧 PaddleYOLO 内容保留为历史对照。

围绕图像分类、目标检测与中文情感分析的 Notebook 教学项目。

| 模块 | 入口 | 内容 |
|---|---|---|
| 01 图像分类 | [课程说明](01-image-classification/README.md) | MNIST → CIFAR-10 → ResNet → 自定义数据 |
| 02 目标检测 | [课程说明](02-object-detection/README.md) | CV 与 CNN 基础 → YOLO → 剪刀石头布检测 |
| 03 情感分析 | [课程说明](03-sentiment-analysis/README.md) | NLP → 词向量 → LSTM，Paddle/PyTorch 两条路线 |

首次学习从 [MNIST 规范版](01-image-classification/notebooks/01-lenet-mnist.ipynb) 开始。完成基础训练流程后，可以分别进入目标检测或情感分析。

- [学习路线](docs/learning-path.zh-CN.md)
- [环境准备](docs/environment-setup.zh-CN.md)
- [数据获取与放置路径](docs/datasets.zh-CN.md)
- [目录整理记录](docs/migration/reorganization.md)

每个运行环境独立安装依赖，以 Notebook 所在目录作为工作目录。数据放在各模块 data/，训练产物放在 outputs/，讲解图片放在 assets/。

当前状态：完成目录及路径整理和静态检查；未安装新环境、下载资源或执行训练。Notebook 历史输出原样保留，不能视为本次运行结果。


## 数据集格式与查看专题

[VOC / COCO / YOLO 转换与小土堆 Labs 查看](04-dataset-formats/README.zh-CN.md)独立于模型训练课程。
