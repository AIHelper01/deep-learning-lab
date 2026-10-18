# 图像分类

中文课程 · [English (default)](../english/01-image-classification/README.md) · [中文总览](../README.zh-CN.md)

采用 PyTorch，依次学习数据准备与复现、张量形状、训练与检查点选择、评估与单图预测。
讲解、控制台输出与图表标签均为中文。

1. [LeNet 与 MNIST](notebooks/01-lenet-mnist.ipynb)：手写数字分类完整闭环。
2. [LeNet 与 CIFAR-10](notebooks/02-lenet-cifar10.ipynb)：三通道彩色图像分类。
3. [ResNet18 与 CIFAR-10](notebooks/03-resnet-cifar10.ipynb)：冻结主干的迁移学习。
4. [自定义文件夹数据](notebooks/extensions/04-lenet-custom-data.ipynb)：`ImageFolder` 数据集组织方式。

历史版本保留在 [archive/legacy-notebooks/](archive/legacy-notebooks/README.md)（只读参考，不参与执行与校验），
[Copy1 对照版](archive/01-lenet-mnist-copy1.ipynb) 保留供比较，不作为必修入口。

## 与英文课程的关系

这四本 notebook 由 `../scripts/build_chinese_course.py` 从英文母本
`../english/01-image-classification/notebooks/` 镜像生成：单元数量、实验配置、随机种子、
训练逻辑完全一致，只有讲解语言、控制台文案、图表标签和类别名（`零…九`、`飞机…卡车`）是中文。
改内容请改英文母本再重新生成，不要直接编辑中文镜像。中文图表字体由 `../common/course_zh.py` 探测并设置。

## 数据与输出

- `data/MNIST/raw/`：MNIST 原始数据（首次运行也会自动下载）。
- `data/cifar10/`：CIFAR-10，首次运行自动下载，也可按 `data/README.md` 从 `/workspace/DataSet` 复制。
- `data/custom-digits-balanced/`：自定义数据课从 MNIST 导出的 `train/<类别>` 文件夹，脚本自动生成。
  早期版本要求的 LEDNUM 已无公开可用下载，本课用同样的目录结构演示自定义数据集，**不宣称 LED 场景精度**。
- `assets/`：notebook 内嵌「预期输出」引用的图片。
- `outputs/<实验名>/`：权重、曲线、混淆矩阵与 `metrics.json`。

## 运行

```bash
# 在本模块 notebook 内直接运行；或用命令行整本执行并保留真实输出
~/env_dl_uv/.venv/bin/python ../english/scripts/execute_and_save.py --group vision --language zh-CN
~/env_dl_uv/.venv/bin/python ../scripts/embed_expected_outputs.py --module 01-image-classification
```

环境见[环境准备](../docs/environment-setup.zh-CN.md)，数据见[数据获取](../docs/datasets.zh-CN.md)。
旧依赖与锁文件保留在 `archive/environment/`，不用于当前环境。
