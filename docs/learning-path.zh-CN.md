中文（母本） · [English mirror](learning-path.md)

# 学习路线（中文课程）

## 主线

1. [MNIST](../01-image-classification/notebooks/01-lenet-mnist.ipynb)：数据观察、网络维度、训练评估、保存与重新加载预测。
2. [CIFAR-10](../01-image-classification/notebooks/02-lenet-cifar10.ipynb)：彩色图像与更复杂任务。
3. [ResNet](../01-image-classification/notebooks/03-resnet-cifar10.ipynb)：预训练网络和分类头适配。

完成后，按兴趣进入[目标检测](../02-object-detection/README.md)或[情感分析](../03-sentiment-analysis/README.md)，两者不互为前置。

## 扩展与对照

LEDNUM 实验属于扩展，需要外部数据。MNIST Copy1 属于历史对照。情感分析选一套框架贯穿学习，另一套用于比较。CV 总览中的 ViT、Diffusion 等内容作为拓展阅读。

## 实验完成标准

能够说明输入与输出、复现数据处理和训练过程、记录评估指标，并解释失败样本。涉及模型保存的实验还应验证重新加载后的预测。比较不同模型前先对齐数据划分、预处理、训练轮数和预训练设置。

后续优先级：先验证 MNIST 完整流程，再逐模块验证环境与数据，最后评估是否提取重复训练工具。当前没有执行这些训练验证。

## 平行数据专题

[YOLO / VOC / COCO 转换与小土堆 Labs 查看](../02-object-detection/dataset-formats/README.md)独立于模型训练主线，可单独学习。
