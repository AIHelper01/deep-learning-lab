# 图像分类数据（中文课程）

| 数据 | 内容与用途 | 来源地址 | 模块内路径 |
|---|---|---|---|
| MNIST | 灰度手写数字 0–9，用于 LeNet 入门 | [数据集介绍](https://huggingface.co/datasets/ylecun/mnist)、[torchvision 接口](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html) | `data/MNIST/` |
| CIFAR-10 | 十类彩色物体图片，用于 LeNet 与 ResNet 对比 | [大学数据集页面](https://www.cs.toronto.edu/~kriz/cifar.html)、[Python 下载包](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz) | `data/CIFAR10/` |
| LEDNUM | 历史 LED 数字扩展，需要原教学数据 | 未提供可核实的公开下载或许可 | `data/LEDNUM/` |

MNIST 与 CIFAR-10 通过 Notebook 的 torchvision 下载流程准备；保留原训练/测试划分和作者署名。LEDNUM 需要 `train_data/`、`test_data/`、`train.txt`、`test.txt`，历史 `/workspace` 复制命令不是下载地址。

如需无需额外外部数据的自定义图片目录实验，可用英文课程由 MNIST 生成的扩展，位置是 `english/01-image-classification/data/custom-digits-balanced/`，不应与中文 LEDNUM 混为同一数据。

详细规模、获取方式、许可注意事项见[中文数据集介绍](../../docs/datasets.zh-CN.md)；[默认英文说明](../../docs/datasets.md)。`data/` 下除 README 外均不入库。
