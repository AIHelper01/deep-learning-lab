# 图像分类

中文课程 · [English (default)](../english/01-image-classification/README.md) · [中文总览](../README.zh-CN.md)

采用 PyTorch，依次学习数据预处理、训练评估、模型保存与预测。

1. [LeNet-MNIST 主课程](notebooks/01-lenet-mnist.ipynb)：先阅读分步正文，再阅读完整训练系统附录。
2. [LeNet-CIFAR10](notebooks/02-lenet-cifar10.ipynb)：彩色图像分类。
3. [ResNet-CIFAR10](notebooks/03-resnet-cifar10.ipynb)：预训练网络与迁移学习。
4. [自定义数据扩展](notebooks/extensions/04-lenet-custom-data.ipynb)：保留原进阶版全部内容，包含 MNIST 与 LEDNUM。

[Copy1 对照版](archive/01-lenet-mnist-copy1.ipynb) 保留供比较，不作为必修入口。

## 数据与输出

- data/MNIST/raw/：已保留原始解压数据。
- data/CIFAR10/：首次运行下载；data/LEDNUM/：需要自行准备。
- assets/lenet/ 与 assets/resnet/：示例图片。
- outputs/：模型、checkpoint、曲线和日志。
- scripts/create_txt.py：LEDNUM 索引辅助脚本，在 scripts 目录运行。

以具体 Notebook 所在目录作为工作目录，包含 extensions 与 archive 中的 Notebook。路径已按各自位置调整。

[环境准备](../docs/environment-setup.zh-CN.md)。旧依赖和锁文件保留在 archive/environment/；新依赖尚未安装验证。教程中的 /workspace 数据复制命令仍是旧环境示例，Windows 下应按实际数据来源准备，不能直接照抄。训练逻辑与历史输出保留。
